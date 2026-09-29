#!/usr/bin/env python3
"""Generate in an isolated Docker/agent session; retain an independent stage report."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import uuid

from results import save, summarize, token_usage
from runners.agents import add_agent_options, add_model_options, settings, label_for, prepare_agent, archive_sessions, agent_log_paths

ROOT = Path(__file__).resolve().parents[2]
BACKENDS = {
    'pandas': 'Use pandas as the main dataframe backend for loading, transformation, and computation.',
    'polars': 'Use Polars as the main dataframe backend for loading, transformation, and computation. Do not use pandas for the main workflow. Pandas may be used only for an explicit final interoperability boundary when required.',
    'ibis': 'Use Ibis with DuckDB as the main dataframe backend for loading, filtering, joins, aggregation, sorting, and date handling. Keep relational computation lazy until final materialization where practical. Do not use pandas for the main workflow. A small final boundary conversion is allowed only when required for answer serialization.'
}


def build_prompt(dataset, task, backend_instruction, *, complete_requirements=False):
    prompt = f'''Solve this DataAgentBench task. Read only /workspace/data, /workspace/context, and /workspace/task.json. Put code and intermediate files under /workspace/work. Do not modify /workspace/data. Do not read hidden answers, validators, reference solutions, or other runs. Use this backend: {backend_instruction} Generate /workspace/work/solution.py, execute it, repair failures, and write /workspace/work/answer.json with exactly {{"answer": "<concise final answer>"}}. Do not hard-code the answer.

Context: {task.get("context", "")}
Question: {task.get("query", "")}'''
    delivery = {
        'version': 1,
        'mode': 'complete_requirements' if complete_requirements else 'file_references',
        'hints_enabled': True if complete_requirements else None,
        'inline_sources': [],
    }
    if complete_requirements:
        prompt += (
            '\n\nHints are enabled for this run. The data description and hints below, '
            'including any task-specific clarifications, are equally binding parts of '
            'the task requirements. Read and follow both when solving the task. '
            'Both documents are included in full below.\n'
        )
        for name, title in [('description.md', 'Data description'), ('hints.md', 'Hints and task-specific clarifications')]:
            relative = f'context/{name}'
            raw = (dataset / relative).read_bytes()
            body = raw.decode('utf-8-sig').replace('\r\n', '\n').replace('\r', '\n')
            if not body.strip():
                raise ValueError(f'Complete requirements need a nonempty {relative}')
            prompt += f'\n## {title} ({relative})\n\n{body}\n'
            delivery['inline_sources'].append({
                'path': relative, 'sha256': hashlib.sha256(raw).hexdigest(),
                'bytes': len(raw), 'text_characters': len(body),
            })
    delivery['prompt_sha256'] = hashlib.sha256(prompt.encode('utf-8')).hexdigest()
    return prompt, delivery


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--dataset', type=Path, required=True)
    p.add_argument('--task', required=True)
    p.add_argument('--backend', choices=BACKENDS, default='pandas')
    p.add_argument('--image', default='dfarena-agent-sandbox:latest')
    p.add_argument('--run-dir', type=Path, required=True)
    p.add_argument('--timeout', type=int, default=600)
    p.add_argument('--complete-requirements', action='store_true',
                   help='Enable hints and include full description and hints as equally binding task requirements.')
    add_agent_options(p)
    add_model_options(p)
    a = p.parse_args()
    info = settings(a)
    label = label_for(a, info)
    if a.timeout <= 0:
        p.error('--timeout must be positive')
    ds, run = a.dataset.resolve(), a.run_dir.resolve()
    agent_logs = agent_log_paths(run)
    # Refuse reuse: stale answers/evaluations must not masquerade as a new run.
    if any((run / name).exists() for name in ('detail/generation.json', 'detail/evaluation.json', 'work', 'solution')):
        p.error('Use a fresh run directory; generation artifacts already exist')
    task = json.loads((ds/'tasks'/a.task/'task.json').read_text(encoding='utf-8'))
    try:
        prompt, delivery = build_prompt(ds, task, BACKENDS[a.backend],
                                        complete_requirements=a.complete_requirements)
    except (OSError, UnicodeError, ValueError) as exc:
        p.error(f'Cannot prepare task requirements: {exc}')
    for folder in ('solution', 'detail', 'work', 'logs'):
        (run/folder).mkdir(parents=True, exist_ok=True)
    (run/'detail/prompt.txt').write_bytes(prompt.encode('utf-8'))
    save(run/'detail/input_delivery.json', delivery)
    result = {'benchmark': 'DataAgentBench', 'dataset': ds.name, 'task': a.task,
              'mode': 'direct', 'run_id': run.name, 'backend': a.backend,
              'agent': {**info, 'label': label},
              'input_delivery': delivery,
              'status': 'running', 'returncode': None, 'started_at': None, 'finished_at': None,
              'elapsed_seconds': None, 'timing_scope': a.agent + '_process',
              'artifacts': {'solution': 'solution/solution.py', 'answer': 'solution/answer.json',
                            'agent_log': str(agent_logs['events'].relative_to(run))},
              **token_usage(agent_logs['events'], False, agent=a.agent)}
    save(run/'detail/generation.json', result)
    summarize(run)
    container = 'dfarena-dab-' + uuid.uuid4().hex[:12]
    try:
        with tempfile.TemporaryDirectory(prefix='dfarena-dab-') as tmp:
            cfg = Path(tmp)/a.agent; cfg.mkdir()
            metrics = Path(tmp)/'metrics'; metrics.mkdir()
            agent_flags, agent_command = prepare_agent(a, cfg, info)
            save(run/'detail/generation.json', result)
            cmd = ['docker', 'run', '--rm', '-i', '--name', container,
                   '-v', f'{ds/"data"}:/workspace/data:ro',
                   '-v', f'{ds/"context"}:/workspace/context:ro',
                   '-v', f'{ds/"tasks"/a.task/"task.json"}:/workspace/task.json:ro',
                   '-v', f'{run/"work"}:/workspace/work:rw',
                   *agent_flags,
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
