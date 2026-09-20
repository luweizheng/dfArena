"""Run inside the container: time the child process, not Docker startup.

The child inherits stdin/stdout/stderr. A timeout terminates its process group
before the timer is stopped. The report survives ordinary failure/timeout;
SIGKILL or a container crash may prevent a final report.
"""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import signal
import subprocess
import time


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--agent', choices=['codex', 'opencode'], default='codex')
    parser.add_argument('--report', required=True, type=Path)
    parser.add_argument('--timeout', required=True, type=float)
    parser.add_argument('command', nargs=argparse.REMAINDER)
    args = parser.parse_args()
    command = args.command[1:] if args.command[:1] == ['--'] else args.command
    if not command or args.timeout <= 0:
        parser.error('A command and a positive timeout are required')
    report = {'started_at': utc_now(), 'finished_at': None, 'elapsed_seconds': None,
              'status': 'running', 'returncode': None, 'timing_scope': args.agent + '_process'}
    started = time.monotonic()
    try:
        process = subprocess.Popen(command, start_new_session=True)
        try:
            report['returncode'] = process.wait(timeout=args.timeout)
            report['status'] = 'completed' if process.returncode == 0 else 'failed'
        except subprocess.TimeoutExpired:
            report['status'] = 'timeout'
            try:
                os.killpg(process.pid, signal.SIGTERM)
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGKILL)
                process.wait()
            except ProcessLookupError:
                process.wait()
            report['returncode'] = process.returncode
    except OSError as exc:
        report['status'] = 'launch_error'
        report['error_type'] = type(exc).__name__
    finally:
        report['elapsed_seconds'] = time.monotonic() - started
        report['finished_at'] = utc_now()
        args.report.parent.mkdir(parents=True, exist_ok=True)
        temp = args.report.with_suffix('.tmp')
        temp.write_text(json.dumps(report, indent=2) + '\n')
        temp.replace(args.report)
    if report['status'] == 'timeout':
        return 124
    return 0 if report['status'] == 'completed' else 1


if __name__ == '__main__':
    raise SystemExit(main())
