#!/usr/bin/env python3
"""Run generation and evaluation, preserving both stage reports."""
import argparse
from pathlib import Path
import re
import subprocess
import sys

from results import save, summarize
from runners.agents import add_agent_options, settings, label_for, forwarded_options


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--dataset', type=Path, required=True)
    p.add_argument('--task', required=True)
    p.add_argument('--agent-model')
    p.add_argument('--backend', choices=['pandas','polars','ibis'], default='pandas')
    p.add_argument('--model')
    p.add_argument('--image', default='dfarena-agent-sandbox:latest')
    p.add_argument('--timeout', type=int, default=600)
    p.add_argument('--evaluation-timeout', type=int, default=120)
    add_agent_options(p)
    a = p.parse_args()
    a.agent_model = label_for(a, settings(a))
    if a.timeout <= 0 or a.evaluation_timeout <= 0:
        p.error('Timeouts must be positive')
    if not re.fullmatch(r'[A-Za-z0-9_-][A-Za-z0-9_.-]*', a.agent_model):
        p.error('--agent-model must be a directory label')
    if not re.fullmatch(r'[A-Za-z0-9_-]+', a.task):
        p.error('--task must be a task directory name')
    root = a.dataset.resolve()/'output'/a.task/a.agent_model/a.backend
    root.mkdir(parents=True, exist_ok=True)
    ids = [int(x.name[1:]) for x in root.iterdir() if x.is_dir() and re.fullmatch(r'r[0-9]+', x.name)]
    run = root/f'r{max(ids,default=0)+1:03d}'
    run.mkdir()
    print(f'RUN={run}', flush=True)
    scripts = Path(__file__).parent
    common = ['--dataset',str(a.dataset.resolve()),'--task',a.task,'--run-dir',str(run),'--image',a.image]
    command = [sys.executable,str(scripts/'generate.py'),*common,'--agent-model',a.agent_model,
               '--backend',a.backend,'--timeout',str(a.timeout),*forwarded_options(a)]
    if a.model:
        command += ['--model',a.model]
    g = subprocess.run(command)
    if g.returncode == 0:
        subprocess.run([sys.executable,str(scripts/'evaluate.py'),*common,'--timeout',str(a.evaluation_timeout)])
    else:
        save(run/'detail/evaluation.json', {'status':'skipped','passed':None,'answer':None,
            'started_at':None,'finished_at':None,'elapsed_seconds':None,'error_types':[],
            'message':'Generation did not complete successfully'})
    result = summarize(run)
    print(f'RESULT={run/"result.json"}', flush=True)
    return 0 if result['evaluation'].get('passed') is True else 1


if __name__ == '__main__':
    raise SystemExit(main())
