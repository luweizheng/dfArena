#!/usr/bin/env python3
"""Generate in an isolated Docker/agent session; retain an independent stage report."""
import argparse
import json
import math
import os
from pathlib import Path
import secrets
import shutil
import socket
import subprocess
import tempfile
import time
import uuid
import requests

from results import save, summarize, token_usage
from runners.backends import BACKENDS
from runners.agents import add_agent_options, add_model_options, settings, label_for, prepare_agent, archive_sessions, agent_log_paths

ROOT = Path(__file__).resolve().parents[2]

def build_prompt(dataset, task_text, backend_instruction, *, mode='direct'):
    prompt = f'''Solve this DataAgentBench task. Read only /workspace/data, /workspace/context, and /workspace/query.md. Resolve dataset-relative paths from /workspace. Put code and intermediate files under /workspace/work. Do not modify the input files. Do not read hidden answers, validators, reference solutions, or other runs. Use this backend: {backend_instruction} Generate /workspace/work/solution.py, execute it, repair failures, and write /workspace/work/answer.json with exactly {{"answer": "<concise final answer>"}}. Do not hard-code the answer.

Question: {task_text}'''
    if mode == 'interact':
        prompt += ('\n\nThis is an interactive clarification task. If a requirement is unclear, '
                   'ask the clarification.ask MCP tool and use its answers. The tool call '
                   'is blocking; wait for the complete answer before continuing. Do not call '
                   'the clarification service from solution.py.\n')
    agent_inputs = ['data/', 'context/description.md', 'query.md']
    if mode == 'clarified':
        agent_inputs.append('context/hints.md')
    delivery = {
        'agent_inputs': agent_inputs,
        'simulator': mode == 'interact',
        'simulator_context': ['hints.md'] if mode == 'interact' else [],
    }
    if mode == 'clarified':
        prompt += (
            '\n\nHints are enabled for this run. The data description and hints below, '
            'including any task-specific clarifications, are equally binding parts of '
            'the task requirements. Read and follow both when solving the task. '
            'Both documents are included in full below.\n'
        )
        for name, title in [('description.md', 'Data description'), ('hints.md', 'Hints and task-specific clarifications')]:
            relative = name
            raw = (dataset / relative).read_bytes()
            body = raw.decode('utf-8-sig').replace('\r\n', '\n').replace('\r', '\n')
            if not body.strip():
                raise ValueError(f'Clarified mode needs a nonempty {relative}')
            prompt += f'\n## {title} ({relative})\n\n{body}\n'

    return prompt, delivery


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--dataset', type=Path, required=True)
    p.add_argument('--task', required=True)
    p.add_argument('--backend', choices=BACKENDS, default='pandas')
    p.add_argument('--image', default='dfarena-agent-sandbox:latest')
    p.add_argument('--run-dir', type=Path, required=True)
    p.add_argument('--simulator-env', type=Path, default=ROOT/'runners/configs/simulator/simulator.env')
    p.add_argument('--timeout', type=int, default=600)
    p.add_argument('--mode', choices=['direct', 'clarified', 'interact'], default='interact')
    add_agent_options(p)
    add_model_options(p)
    a = p.parse_args(argv)
    info = settings(a)
    label = label_for(a, info)
    if a.timeout <= 0:
        p.error('--timeout must be positive')
    ds, run = a.dataset.resolve(), a.run_dir.resolve()
    agent_logs = agent_log_paths(run)
    # Refuse reuse: stale answers/evaluations must not masquerade as a new run.
    if any((run / name).exists() for name in ('detail/generation.json', 'detail/evaluation.json', 'work', 'solution')):
        p.error('Use a fresh run directory; generation artifacts already exist')
    task_dir = ds/'tasks'/a.task
    task_text = (task_dir/'query.md').read_text(encoding='utf-8')
    try:
        prompt, delivery = build_prompt(ds, task_text, BACKENDS[a.backend], mode=a.mode)
    except (OSError, UnicodeError, ValueError) as exc:
        p.error(f'Cannot prepare task requirements: {exc}')
    for folder in ('solution', 'detail', 'work', 'logs'):
        (run/folder).mkdir(parents=True, exist_ok=True)
    (run/'detail/prompt.txt').write_bytes(prompt.encode('utf-8'))
    result = {'benchmark': 'DataAgentBench', 'dataset': ds.name, 'task': a.task,
              'mode': a.mode, 'run_id': run.name, 'backend': a.backend,
              'agent': {**info, 'label': label},
              'input_delivery': {'mode': a.mode, **delivery},
              'status': 'running', 'returncode': None, 'started_at': None, 'finished_at': None,
              'elapsed_seconds': None, 'timing_scope': a.agent + '_process',
              'interaction': {'enabled': a.mode == 'interact', 'ask_calls': 0,
                              'simulator_elapsed_seconds': None},
              'elapsed_seconds_excluding_simulator': None,
              'timing_scope_excluding_simulator': None,
              'artifacts': {'solution': 'solution/solution.py', 'answer': 'solution/answer.json',
                            'agent_log': str(agent_logs['events'].relative_to(run))},
              **token_usage(agent_logs['events'], False, agent=a.agent)}
    save(run/'detail/generation.json', result)
    summarize(run)
    container = 'dfarena-dab-' + uuid.uuid4().hex[:12]
    server = None
    try:
        with tempfile.TemporaryDirectory(prefix='dfarena-dab-') as tmp:
            cfg = Path(tmp)/a.agent; cfg.mkdir()
            metrics = Path(tmp)/'metrics'; metrics.mkdir()
            context = Path(tmp)/'context'; context.mkdir()
            shutil.copy2(ds/'description.md', context/'description.md')
            if a.mode == 'clarified':
                shutil.copy2(ds/'hints.md', context/'hints.md')
            agent_flags, agent_command = prepare_agent(a, cfg, info)
            docker_env = []
            if a.mode == 'interact':
                with socket.socket() as sock:
                    sock.bind(('127.0.0.1', 0)); port = sock.getsockname()[1]
                admin = secrets.token_urlsafe(32)
                env = dict(os.environ, DFARENA_DAB_ROOT=str(ds.parent), DFARENA_ADMIN_TOKEN=admin,
                           DFARENA_TRACE=str(run/'logs'/'interaction.jsonl'),
                           DFARENA_SIMULATOR_ENV=str(a.simulator_env.expanduser().resolve()))
                log = (run/'logs'/'server.log').open('w')
                server = subprocess.Popen([__import__('sys').executable, '-m', 'uvicorn', 'simulator_server:app',
                    '--app-dir', str(Path(__file__).parent), '--host', '0.0.0.0', '--port', str(port)],
                    env=env, stdout=log, stderr=subprocess.STDOUT)
                for _ in range(100):
                    if server.poll() is not None: raise RuntimeError('Simulator exited; see server.log')
                    try:
                        requests.get(f'http://127.0.0.1:{port}/health', timeout=1).raise_for_status(); break
                    except requests.RequestException: time.sleep(.2)
                else: raise TimeoutError('Simulator did not become healthy')
                response = requests.post(f'http://127.0.0.1:{port}/session/start',
                    headers={'Authorization':'Bearer '+admin},
                    json={'dataset_id': ds.name, 'task_id': a.task, 'run_id': run.name}, timeout=30)
                response.raise_for_status(); session = response.json(); save(run/'session.json', session)
                docker_env = ['--add-host=host.docker.internal:host-gateway', '-e', f'DFARENA_SESSION_ID={session["session_id"]}']
                with (cfg/'config.toml').open('a') as f:
                    f.write(f'\n[mcp_servers.clarification]\ncommand = "bash"\nargs = ["-c", "exec /usr/local/bin/python /runner/mcp_adapter.py"]\nstartup_timeout_sec = 30\ntool_timeout_sec = 180\nrequired = true\n[mcp_servers.clarification.env]\nDFARENA_CLARIFIER_URL = "http://host.docker.internal:{port}/session/ask"\nDFARENA_SESSION_ID = "{session["session_id"]}"\n')
            save(run/'detail/generation.json', result)
            cmd = ['docker', 'run', '--rm', '-i', '--name', container, *docker_env,
                   '-v', f'{ds/"data"}:/workspace/data:ro',
                   '-v', f'{context}:/workspace/context:ro',
                   '-v', f'{task_dir/"query.md"}:/workspace/query.md:ro',
                   '-v', f'{run/"work"}:/workspace/work:rw',
                   *agent_flags,
                   *(['-v', f'{Path(__file__).parent/"simulator/mcp_adapter.py"}:/runner/mcp_adapter.py:ro'] if a.mode == 'interact' else []),
                   '-v', f'{ROOT/"runners/timed_process.py"}:/runner/timed_process.py:ro',
                   '-v', f'{metrics}:/runner/metrics:rw', '-w', '/workspace/work', a.image,
                   'python', '/runner/timed_process.py', '--report', f'/runner/metrics/{a.agent}.json',
                   '--agent', a.agent, '--timeout', str(a.timeout), '--', *agent_command]
            save(run/'detail/command.json', cmd)
            try:
                with (agent_logs['events']).open('w') as out, agent_logs['stderr'].open('w') as err:
                    cp = subprocess.run(cmd, input=prompt, text=True, encoding='utf-8', stdout=out, stderr=err, timeout=a.timeout+90)
                result['docker_returncode'] = cp.returncode
            except subprocess.TimeoutExpired:
                result['status'] = 'runner_timeout'
            finally:
                subprocess.run(['docker', 'rm', '-f', container], capture_output=True, timeout=30)
                if server is not None:
                    server.terminate(); server.wait(timeout=10); server = None
                report = metrics/(a.agent+'.json')
                if report.exists():
                    timing = json.loads(report.read_text())
                    save(run/'detail/agent_exec_timing.json', timing)
                    result.update(timing)
                elif result['status'] == 'running':
                    result['status'] = 'runner_error'
                    result['error_type'] = 'MissingTimingReport'
                session_archive = archive_sessions(a.agent, cfg, run)
                if session_archive:
                    result['artifacts']['sessions'] = session_archive
    except Exception as exc:
        result['status'] = 'runner_error'
        result['error_type'] = type(exc).__name__
    finally:
        if server is not None:
            server.terminate(); server.wait(timeout=10)
        trace = run / 'logs' / 'interaction.jsonl'
        # The HTTP handler writes the trace just before its response completes;
        # allow a short flush window before collecting interaction metrics.
        if a.mode == 'interact':
            previous_size = -1
            for _ in range(40):
                size = trace.stat().st_size if trace.is_file() else 0
                if size > 0 and size == previous_size:
                    break
                previous_size = size
                time.sleep(0.05)
        if a.mode == 'interact' and trace.is_file():
            records = []
            for line in trace.read_text(encoding='utf-8').splitlines():
                try:
                    record = json.loads(line)
                except json.JSONDecodeError:
                    continue
                records.append(record)
            result['interaction']['ask_calls'] = len(records)
            durations = [r.get('elapsed_seconds') for r in records]
            timing_complete = all(isinstance(x, (int, float)) and math.isfinite(x) and x >= 0
                                  for x in durations)
            simulator_seconds = sum(durations) if timing_complete else None
            result['interaction']['simulator_elapsed_seconds'] = simulator_seconds if records else None
            elapsed = result.get('elapsed_seconds')
            if (result.get('status') == 'completed' and
                    isinstance(elapsed, (int, float)) and records and
                    simulator_seconds is not None and simulator_seconds <= elapsed):
                result['elapsed_seconds_excluding_simulator'] = elapsed - simulator_seconds
                result['timing_scope_excluding_simulator'] = a.agent + '_process_minus_simulator_wait'
        for name in ('solution.py', 'answer.json'):
            source = run/'work'/name
            if source.is_file():
                shutil.copy2(source, run/'solution'/name)
        if result['status'] == 'completed':
            try:
                answer = json.loads((run/'solution/answer.json').read_text())
                if not (run/'solution/solution.py').is_file() or not isinstance(answer, dict) or not isinstance(answer.get('answer'), str):
                    raise ValueError('Missing solution or answer string')
            except (OSError, ValueError):
                result['status'] = 'missing_output'
        result.update(token_usage(agent_logs['events'], result.get('returncode') == 0, agent=a.agent))
        if result.get('agent_errors') and result['status'] == 'completed':
            result['status'] = 'agent_failed'
        save(run/'detail/generation.json', result)
        summarize(run)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if result['status'] == 'completed' else 1


if __name__ == '__main__':
    raise SystemExit(main())
