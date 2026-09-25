"""Run with python -m evaluation --gt-dir ... --cand-dir ... --config ..."""
import argparse
import json
from pathlib import Path

from .evaluator import Evaluator


def main():
    parser = argparse.ArgumentParser(description='Compare candidate CSV tables with frozen GT/config.')
    parser.add_argument('--gt-dir', required=True, type=Path)
    parser.add_argument('--cand-dir', required=True, type=Path)
    parser.add_argument('--config', required=True, type=Path)
    parser.add_argument('--report', type=Path, help='Save JSON report outside GT/candidate directories')
    args = parser.parse_args()
    if args.report:
        target = args.report.resolve()
        if any(target.is_relative_to(p.resolve()) for p in (args.gt_dir, args.cand_dir)) or target == args.config.resolve():
            parser.error('--report must not overwrite config or files under GT/candidate directories')
    result = Evaluator(args.gt_dir, args.cand_dir, args.config).run()
    output = json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False) + '\n'
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(output, encoding='utf-8')
    print(output, end='')
    return 0 if result['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
