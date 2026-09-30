"""Evaluate one PrepBench run with the shared table evaluator, then refresh its summary."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT.parent))
from evaluation import Evaluator
from runners.results import read, save, summarize
from simulator.case_ids import normalize_case_id


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', required=True)
    parser.add_argument('--run-dir', required=True, type=Path)
    args = parser.parse_args(argv)
    case = ROOT / normalize_case_id(args.case)
    run = args.run_dir.resolve()
    generation = read(run / 'detail/generation.json')
    if not generation or generation.get('benchmark') != 'PrepBench' or generation.get('task') != case.name:
        parser.error('--run-dir must contain a PrepBench generation record for the specified case')
    if generation.get('status') != 'completed':
        parser.error('Generation must be completed before evaluation')
    payload = {'status': 'running', 'passed': None,
               'started_at': datetime.now(timezone.utc).isoformat(), 'finished_at': None,
               'elapsed_seconds': None, 'timing_scope': 'table_evaluator', 'error_types': []}
    save(run / 'detail/evaluation.json', payload)
    summarize(run)
    started = time.monotonic()
    try:
        report = Evaluator(case / 'evaluation/gt', run / 'workspace/outputs',
                           case / 'evaluation/config.json').run()
        payload['report'] = report
        payload['error_types'] = sorted({e['error_type'] for e in report['errors']})
        # GT/config/internal failures do not establish that the candidate is wrong.
        invalid_evaluation = any(e.get('side') in {'gt', 'config', 'evaluator'} for e in report['errors'])
        payload['status'] = 'error' if invalid_evaluation else 'completed'
        payload['passed'] = None if invalid_evaluation else report['passed']
    except Exception as exc:
        payload.update(status='error', error_types=['EVALUATOR_ERROR'], message=str(exc))
    finally:
        payload['elapsed_seconds'] = time.monotonic() - started
        payload['finished_at'] = datetime.now(timezone.utc).isoformat()
        save(run / 'detail/evaluation.json', payload)
        summarize(run)
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0 if payload['passed'] is True else 1


if __name__ == '__main__':
    raise SystemExit(main())
