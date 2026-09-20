#!/usr/bin/env python3
"""Retain the validator stage result and refresh the combined run summary."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import time
import uuid

from results import save, summarize


def now():
    return datetime.now(timezone.utc).isoformat()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--dataset', type=Path, required=True)
    p.add_argument('--task', required=True)
    p.add_argument('--run-dir', type=Path, required=True)
    p.add_argument('--image', default='dfarena-agent-sandbox:latest')
    p.add_argument('--timeout', type=int, default=120)
    a = p.parse_args()
    if a.timeout <= 0:
        p.error('--timeout must be positive')
    ds, run = a.dataset.resolve(), a.run_dir.resolve()
    (run/'logs').mkdir(parents=True, exist_ok=True)
    payload = {'status': 'running', 'passed': None, 'answer': None, 'started_at': now(),
               'finished_at': None, 'elapsed_seconds': None, 'error_types': [],
               'timing_scope': 'evaluation_docker_call', 'message': ''}
    save(run/'detail/evaluation.json', payload)
    summarize(run)
    started = time.monotonic()
    container = 'dfarena-dab-eval-' + uuid.uuid4().hex[:12]
    code = '''import json,sys
sys.path.insert(0,"/workspace/answer")
import validate
ans=json.load(open("/workspace/solution/answer.json"))["answer"]
ok,msg=validate.validate(ans)
print(json.dumps({"passed":bool(ok),"message":str(msg),"answer":ans}))
'''
    cmd = ['docker', 'run', '--rm', '--name', container,
           '-v', f'{ds/"data"}:/workspace/data:ro',
           '-v', f'{ds/"context"}:/workspace/context:ro',
           '-v', f'{run/"solution"}:/workspace/solution:ro',
           '-v', f'{ds/"tasks"/a.task/"answer"}:/workspace/answer:ro',
           '-w', '/workspace/solution', a.image, 'python', '-c', code]
    try:
        log_path = run/'logs/evaluation.log'
        with log_path.open('w', encoding='utf-8') as log:
            cp = subprocess.run(cmd, text=True, stdout=log, stderr=subprocess.STDOUT, timeout=a.timeout)
        payload['returncode'] = cp.returncode
        if cp.returncode:
            raise RuntimeError('Validator process failed; see evaluation.log')
        parsed = None
        for line in reversed(log_path.read_text(encoding='utf-8', errors='replace').splitlines()):
            try:
                item = json.loads(line)
                if isinstance(item, dict) and type(item.get('passed')) is bool:
                    parsed = item
                    break
            except ValueError:
                continue
        if parsed is None:
            raise RuntimeError('Validator did not return a valid result')
        payload.update({k: parsed.get(k) for k in ('passed', 'answer', 'message')})
        payload['status'] = 'completed'
        payload['error_types'] = [] if payload['passed'] else ['ANSWER_MISMATCH']
    except subprocess.TimeoutExpired:
        payload.update(status='timeout', message='Evaluation timed out', error_types=['EVALUATION_TIMEOUT'])
    except Exception as exc:
        payload.update(status='error', message=str(exc), error_types=['EVALUATION_ERROR'])
    finally:
        payload['elapsed_seconds'] = time.monotonic() - started
        payload['finished_at'] = now()
        try:
            subprocess.run(['docker', 'rm', '-f', container], capture_output=True, timeout=30)
        except (OSError, subprocess.TimeoutExpired):
            payload['cleanup_error'] = True
        save(run/'detail/evaluation.json', payload)
        summarize(run)
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0 if payload['passed'] is True else 1


if __name__ == '__main__':
    raise SystemExit(main())
