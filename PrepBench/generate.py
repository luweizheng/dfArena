"""Run local PrepBench assets in an isolated, fresh Codex Docker session."""
import argparse
import re
import hashlib
import json
import os
from pathlib import Path
import secrets
import shutil
import socket
import subprocess
import sys
import tempfile
import time
import tomllib
import uuid

import requests
from simulator.case_ids import normalize_case_id
from simulator.case_views import load_internal_case_view

ROOT = Path(__file__).resolve().parent
BACKENDS = {'pandas': 'pandas', 'polars': 'Polars', 'ibis': 'Ibis with DuckDB as the backend'}


sys.path.insert(0, str(ROOT.parent))
from runners.results import save, summarize, token_metrics, token_usage
from runners.agents import add_agent_options, add_model_options, settings, label_for, prepare_agent, archive_sessions, agent_log_paths


def prepare(case, run, mode, backend):
    work = run / 'workspace'
    work.mkdir(parents=True)
    source = case / ('query_full.md' if mode == 'clarified' else 'query.md')
    (work / 'outputs').mkdir()
    (run / 'logs').mkdir()
    (run / 'detail').mkdir()
    files = [source, *sorted(p for p in (case / 'inputs').rglob('*') if p.is_file())]
    save(run / 'assets.json', {str(p.relative_to(case)): hashlib.sha256(p.read_bytes()).hexdigest() for p in files})
    prompt = f'Read /workspace/query.md and inspect the input files under /workspace/inputs.\nImplement the requested data processing task using {BACKENDS[backend]}. '
    if backend != 'pandas':
        prompt += 'Do not use pandas for the data transformation logic. '
    prompt += 'You may use Python standard-library utilities for file handling.\n'
    if mode == 'interact':
        prompt += '''This is an interactive requirement-clarification task. Inspect the input data yourself. When a business requirement is unclear, ask the simulated user through the HTTP service. Use the returned answers to guide your implementation. Each question should concern one decision. You may send multiple questions in one request. Follow the returned budget and done flag; reuse the same session.
Call POST $DFARENA_SIMULATOR_URL/session/ask with Content-Type: application/json. Body: {"session_id": "the value of DFARENA_SESSION_ID", "questions": ["your question"]}. You may create a JSON file using Python json.dumps and submit it with curl --fail-with-body -sS --max-time 180 -H 'Content-Type: application/json' --data-binary @request.json "$DFARENA_SIMULATOR_URL/session/ask". Responses contain answers (answer, classification, ref), budget, done, and next_round. Read the actual answers and use them. Do not create new simulator sessions.
'''
    prompt += 'Write and run /workspace/work/solution.py, and save the requested output under /workspace/work/outputs/. The final program must run without contacting the simulator.\n'
    (run / 'detail/prompt.txt').write_text(prompt)
    return work, prompt


def next_run(case, mode, agent_model, backend):
    root = case / 'runs' / mode / agent_model / backend
    root.mkdir(parents=True, exist_ok=True)
    ids = [int(p.name[1:]) for p in root.iterdir()
           if p.is_dir() and re.fullmatch(r'r[0-9]+', p.name)]
    run = root / f'r{max(ids, default=0) + 1:03d}'
    run.mkdir()
    return run


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--case', required=True)
    ap.add_argument('--mode', choices=['interact', 'clarified'], default='interact')
    ap.add_argument('--backend', choices=BACKENDS, default='pandas')
    ap.add_argument('--image', default='dfarena-agent-sandbox:latest')
    ap.add_argument('--simulator-env', type=Path, default=ROOT / '.env')
    ap.add_argument('--timeout', type=int, default=1800)
    ap.add_argument('--dry-run', action='store_true', help='Prepare public workspace only; no Docker/API calls')
    ap.add_argument('--run-dir', type=Path, help='Fresh run directory allocated by run_benchmark.py')
    add_agent_options(ap)
    add_model_options(ap)
    args = ap.parse_args(argv)
    if args.timeout <= 0:
        ap.error('--timeout must be positive')
    case = ROOT / normalize_case_id(args.case)
    load_internal_case_view(case, require_reference_solution=True)
    info = settings(args)
    model = info['model']
    agent_model = label_for(args, info)
    run = args.run_dir.resolve() if args.run_dir else next_run(case, args.mode, agent_model, args.backend)
    agent_logs = agent_log_paths(run)
    run.mkdir(parents=True, exist_ok=True)
    if any(run.iterdir()):
        ap.error('Use a fresh empty run directory')
    work, prompt = prepare(case, run, args.mode, args.backend)
    summary = {'benchmark': 'PrepBench', 'dataset': 'PrepBench', 'task': case.name,
               'case': case.name, 'mode': args.mode, 'backend': args.backend, 'run_id': run.name,
               'agent': {**info, 'label': agent_model},
               'status': 'prepared' if args.dry_run else 'running', 'returncode': None,
               'started_at': None, 'finished_at': None, 'elapsed_seconds': None,
               'timing_scope': args.agent + '_process',
               'interaction': {'enabled': args.mode == 'interact', 'ask_calls': 0},
               'artifacts': {'solution': 'workspace/solution.py', 'outputs': [],
                             'agent_log': str(agent_logs['events'].relative_to(run))},
               **token_usage(agent_logs['events'], completed=False, agent=args.agent)}
    save(run / 'detail/generation.json', summary)
    summarize(run)
    print(f'RUN={run}', flush=True)
    if args.dry_run:
        return 0
    server = None
    container = 'prepbench-' + uuid.uuid4().hex[:12]
    try:
        with tempfile.TemporaryDirectory(prefix='prepbench-agent-') as tmp:
            cfg = Path(tmp) / args.agent
            cfg.mkdir()
            metrics = Path(tmp) / 'metrics'
            metrics.mkdir()
            agent_flags, agent_command = prepare_agent(args, cfg, info)
            docker_env = []
            if args.mode == 'interact':
                with socket.socket() as sock:
                    sock.bind(('127.0.0.1', 0))
                    port = sock.getsockname()[1]
                admin = secrets.token_urlsafe(32)
                env = dict(os.environ, DFARENA_CASE_ROOT=str(ROOT), DFARENA_ADMIN_TOKEN=admin,
                           DFARENA_TRACE=str(run / 'logs' / 'interaction.jsonl'), DFARENA_SIMULATOR_ENV=str(args.simulator_env.resolve()))
                with (run / 'logs' / 'server.log').open('w') as log:
                    server = subprocess.Popen([sys.executable, '-m', 'uvicorn', 'simulator_server:app', '--app-dir', str(ROOT), '--host', '0.0.0.0', '--port', str(port)], env=env, stdout=log, stderr=subprocess.STDOUT)
                url = f'http://127.0.0.1:{port}'
                for _ in range(100):
                    if server.poll() is not None:
                        raise RuntimeError('Simulator exited; see server.log')
                    try:
                        requests.get(url + '/health', timeout=1).raise_for_status()
                        break
                    except requests.RequestException:
                        time.sleep(.2)
                else:
                    raise TimeoutError('Simulator did not become healthy')
                response = requests.post(url + '/session/start', headers={'Authorization': 'Bearer ' + admin}, json={'case_id': case.name, 'run_id': run.name}, timeout=30)
                response.raise_for_status()
                session = response.json()
                save(run / 'session.json', session)
                docker_env = ['-e', f'DFARENA_SIMULATOR_URL=http://host.docker.internal:{port}', '-e', f'DFARENA_SESSION_ID={session["session_id"]}']
            cmd = ['docker', 'run', '--rm', '-i', '--name', container, '--add-host=host.docker.internal:host-gateway', *docker_env,
                   '-v', f'{case / ("query_full.md" if args.mode == "clarified" else "query.md")}:/workspace/query.md:ro',
                   '-v', f'{case / "inputs"}:/workspace/inputs:ro',
                   '-v', f'{work}:/workspace/work:rw', *agent_flags,
                   '-v', f'{ROOT.parent / "runners/timed_process.py"}:/runner/timed_process.py:ro',
                   '-v', f'{metrics}:/runner/metrics:rw', '-w', '/workspace/work', args.image,
                   'python', '/runner/timed_process.py', '--report', f'/runner/metrics/{args.agent}.json',
                   '--agent', args.agent, '--timeout', str(args.timeout), '--', *agent_command]
            save(run / 'detail/command.json', cmd)
            try:
                with (agent_logs['events']).open('w') as out, agent_logs['stderr'].open('w') as err:
                    cp = subprocess.run(cmd, input=prompt, text=True, stdout=out, stderr=err, timeout=args.timeout + 90)
                summary['docker_returncode'] = cp.returncode
            finally:
                try:
                    subprocess.run(['docker', 'rm', '-f', container], capture_output=True, timeout=30)
                except (OSError, subprocess.TimeoutExpired):
                    summary['cleanup_error'] = True
                timing_path = metrics / (args.agent + '.json')
                if timing_path.exists():
                    timing = json.loads(timing_path.read_text())
                    save(run / 'detail/agent_exec_timing.json', timing)
                    summary.update(timing)
                else:
                    summary['status'] = 'runner_error'
                    summary['error_type'] = 'MissingTimingReport'
                session_archive = archive_sessions(args.agent, cfg, run)
                if session_archive:
                    summary['artifacts']['sessions'] = session_archive
    except subprocess.TimeoutExpired:
        summary['status'] = 'runner_timeout'
    except Exception as exc:
        summary['status'] = 'runner_error'
        summary['error_type'] = type(exc).__name__
        print(f'Runner failed: {type(exc).__name__}; inspect run logs', file=sys.stderr)
    finally:
        if server is not None:
            server.terminate()
            try:
                server.wait(timeout=10)
            except subprocess.TimeoutExpired:
                server.kill(); server.wait()
        events = []
        if (agent_logs['events']).exists():
            for line in (agent_logs['events']).read_text().splitlines():
                try:
                    event = json.loads(line)
                    if isinstance(event, dict):
                        events.append(event)
                except ValueError:
                    pass
        summary.update(token_usage(agent_logs['events'], completed=summary.get('returncode') == 0, agent=args.agent))
        if args.agent == 'codex':
            summary['session_ids'] = [e['thread_id'] for e in events if e.get('type') == 'thread.started' and 'thread_id' in e]
        if summary.get('agent_errors') and summary['status'] == 'completed':
            summary['status'] = 'agent_failed'
        trace = run / 'logs' / 'interaction.jsonl'
        summary['interaction']['ask_calls'] = len(trace.read_text().splitlines()) if trace.exists() else 0
        outputs = sorted((work / 'outputs').glob('*.csv'))
        summary['artifacts']['outputs'] = [str(p.relative_to(run)) for p in outputs]
        if summary['status'] == 'completed' and (not outputs or not (work / 'solution.py').is_file()):
            summary['status'] = 'missing_output'
        save(run / 'detail/generation.json', summary)
        summarize(run)
    print(json.dumps(summary, indent=2))
    return 0 if summary['status'] == 'completed' else 1


if __name__ == '__main__':
    raise SystemExit(main())
