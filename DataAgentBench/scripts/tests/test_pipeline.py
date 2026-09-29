import contextlib
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

SCRIPTS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS))
import run_benchmark as pipeline
from results import save


class PipelineTests(unittest.TestCase):
    def run_pipeline(self, dataset, *, complete=False, agent='codex', generation_ok=True, passed=True):
        calls = []
        generation_bytes = []

        def execute(command):
            calls.append(command)
            run = Path(command[command.index('--run-dir') + 1])
            if Path(command[1]).name == 'generate.py':
                save(run / 'detail/generation.json', {
                    'benchmark': 'DataAgentBench', 'status': 'completed' if generation_ok else 'timeout',
                    'elapsed_seconds': 12,
                })
                generation_bytes.append((run / 'detail/generation.json').read_bytes())
                return subprocess.CompletedProcess(command, 0 if generation_ok else 1)
            self.assertEqual(Path(command[1]).name, 'evaluate.py')
            save(run / 'detail/evaluation.json', {
                'status': 'completed' if passed is not None else 'error', 'passed': passed,
            })
            return subprocess.CompletedProcess(command, 0 if passed is True else 1)

        args = ['--dataset', str(dataset), '--task', 'task1', '--agent', agent,
                '--model', 'custom/test' if agent == 'opencode' else 'test',
                '--backend', 'polars', '--image', 'local-test-image',
                '--timeout', '321', '--evaluation-timeout', '45']
        if complete:
            args.append('--complete-requirements')
        with patch.object(pipeline, 'settings', return_value={'model': 'test'}), \
             patch.object(pipeline.subprocess, 'run', side_effect=execute), \
             contextlib.redirect_stdout(io.StringIO()):
            rc = pipeline.main(args)
        run = Path(calls[0][calls[0].index('--run-dir') + 1])
        self.assertEqual((run / 'detail/generation.json').read_bytes(), generation_bytes[0])
        result = json.loads((run / 'result.json').read_text(encoding='utf-8'))
        return rc, run, calls, result

    def test_controller_forwards_generation_options_and_shares_run_with_evaluation(self):
        for agent in ['codex', 'opencode']:
            for complete in [False, True]:
                with self.subTest(agent=agent, complete=complete), tempfile.TemporaryDirectory() as tmp:
                    rc, run, calls, result = self.run_pipeline(Path(tmp), agent=agent, complete=complete)
                    self.assertEqual(rc, 0)
                    self.assertTrue(result['evaluation']['passed'])
                    self.assertEqual(len(calls), 2)
                    generate, evaluate = calls
                    self.assertEqual('--complete-requirements' in generate, complete)
                    self.assertNotIn('--complete-requirements', evaluate)
                    self.assertNotIn('--backend', evaluate)
                    for command in calls:
                        self.assertEqual(command[command.index('--run-dir') + 1], str(run))
                        self.assertEqual(command[command.index('--dataset') + 1], str(Path(tmp).resolve()))
                        self.assertEqual(command[command.index('--task') + 1], 'task1')
                        self.assertEqual(command[command.index('--image') + 1], 'local-test-image')
                    self.assertEqual(generate[generate.index('--timeout') + 1], '321')
                    self.assertEqual(evaluate[evaluate.index('--timeout') + 1], '45')
                    self.assertEqual(generate[generate.index('--agent') + 1], agent)
                    self.assertEqual(generate[generate.index('--model') + 1], 'custom/test' if agent == 'opencode' else 'test')

    def test_generation_failure_skips_scoring(self):
        with tempfile.TemporaryDirectory() as tmp:
            rc, run, calls, result = self.run_pipeline(Path(tmp), complete=True, generation_ok=False)
            self.assertEqual(rc, 1)
            self.assertEqual(len(calls), 1)
            self.assertEqual(result['evaluation']['status'], 'skipped')
            self.assertIsNone(result['evaluation']['passed'])

    def test_scoring_mismatch_and_error_do_not_report_success(self):
        for passed in [False, None]:
            with self.subTest(passed=passed), tempfile.TemporaryDirectory() as tmp:
                rc, run, calls, result = self.run_pipeline(Path(tmp), passed=passed)
                self.assertEqual(rc, 1)
                self.assertEqual(len(calls), 2)
                self.assertIs(result['evaluation']['passed'], passed)

    def test_repeated_controller_calls_allocate_fresh_runs(self):
        with tempfile.TemporaryDirectory() as tmp:
            _, first, _, _ = self.run_pipeline(Path(tmp))
            before = (first / 'result.json').read_bytes()
            _, second, _, _ = self.run_pipeline(Path(tmp), complete=True)
            self.assertEqual(first.name, 'r001')
            self.assertEqual(second.name, 'r002')
            self.assertEqual(first.parent, second.parent)
            self.assertEqual((first / 'result.json').read_bytes(), before)


if __name__ == '__main__':
    unittest.main()
