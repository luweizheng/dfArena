"""Allocate a run, generate with Codex, evaluate tables, and retain both stage reports."""
import argparse
from pathlib import Path
import re
import subprocess
import sys
import tomllib

from generate import BACKENDS, ROOT, next_run
from simulator.case_ids import normalize_case_id
from simulator.case_views import load_internal_case_view
from runners.results import read, save, summarize
from runners.agents import add_agent_options, add_model_options, settings, label_for, forwarded_options


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--case', required=True)
    p.add_argument('--mode', choices=['direct', 'interact', 'clarified'], default='interact')
    p.add_argument('--backend', choices=BACKENDS, default='pandas')
    p.add_argument('--image', default='dfarena-agent-sandbox:latest')
    p.add_argument('--simulator-env', type=Path, default=ROOT/'.env')
    p.add_argument('--timeout', type=int, default=1800)
    p.add_argument('--dry-run', action='store_true', help='Prepare only; no generation or evaluation')
    add_agent_options(p)
    add_model_options(p)
    a = p.parse_args(argv)
    if a.timeout <= 0:
        p.error('--timeout must be positive')
    case = ROOT/normalize_case_id(a.case)
    load_internal_case_view(case, require_reference_solution=True)
    info = settings(a)
    model = info['model']
    label = label_for(a, info)
    run = next_run(case, a.mode, label, a.backend)
    print(f'RUN={run}', flush=True)
    command = [sys.executable, str(ROOT/'generate.py'), '--case', case.name,
               '--mode', a.mode, '--backend', a.backend, '--agent-model', label,
               '--image', a.image,
               '--simulator-env', str(a.simulator_env.expanduser().resolve()),
               '--timeout', str(a.timeout), '--run-dir', str(run), *forwarded_options(a)]
    if a.model:
        command += ['--model', a.model]
    if a.dry_run:
        command.append('--dry-run')
    g = subprocess.run(command)
    generation = read(run/'detail/generation.json')
    if generation is None:
        generation = {'benchmark':'PrepBench', 'dataset':'PrepBench', 'task':case.name,
            'mode':a.mode, 'backend':a.backend, 'run_id':run.name, 'status':'runner_error',
            'agent':{**info,'label':label},
            'error_type':'MissingGenerationReport'}
        save(run/'detail/generation.json', generation)
    if g.returncode == 0 and generation['status'] == 'completed':
        subprocess.run([sys.executable, str(ROOT/'evaluate.py'), '--case', case.name, '--run-dir', str(run)])
        if not (run/'detail/evaluation.json').exists():
            save(run/'detail/evaluation.json', {'status':'error','passed':None,
                'error_types':['MissingEvaluationReport']})
    elif a.dry_run and g.returncode == 0:
        summarize(run)
        print(f'RESULT={run/"result.json"}', flush=True)
        return 0
    else:
        save(run/'detail/evaluation.json', {'status':'skipped','passed':None,
            'started_at':None,'finished_at':None,'elapsed_seconds':None,'error_types':[],
            'message':'Generation did not complete successfully'})
    result = summarize(run)
    print(f'RESULT={run/"result.json"}', flush=True)
    return 0 if result['evaluation'].get('passed') is True else 1


if __name__ == '__main__':
    raise SystemExit(main())
