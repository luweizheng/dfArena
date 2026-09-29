import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

SCRIPTS=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(SCRIPTS))
from results import save, summarize, token_usage
from generate import build_prompt
WRAPPER=SCRIPTS.parents[1]/'runners/timed_process.py'


class ResultsTests(unittest.TestCase):
    def test_stage_preservation_and_rebuild(self):
        with tempfile.TemporaryDirectory() as tmp:
            run=Path(tmp)
            gen={'benchmark':'DataAgentBench','status':'completed','elapsed_seconds':12,'agent':{'model':'test'}}
            save(run/'detail/generation.json',gen)
            self.assertIsNone(summarize(run)['evaluation']['passed'])
            before=(run/'detail/generation.json').read_bytes()
            save(run/'detail/evaluation.json',{'status':'completed','passed':True,'elapsed_seconds':1})
            result=summarize(run)
            self.assertTrue(result['evaluation']['passed'])
            self.assertEqual((run/'detail/generation.json').read_bytes(),before)
            (run/'result.json').unlink()
            self.assertEqual(summarize(run),result)

    def test_tokens_missing_and_cached_subset(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'log'
            self.assertIsNone(token_usage(path,False)['token_usage'])
            path.write_text(json.dumps({'type':'turn.completed','usage':{'input_tokens':100,'cached_input_tokens':80,'output_tokens':20}})+'\n')
            r=token_usage(path,True)
            self.assertEqual(r['token_usage']['total_tokens'],120)
            self.assertEqual(r['token_usage_status'],'complete')
            self.assertEqual(token_usage(path,False)['token_usage_status'],'partial')

    def test_wrapper_success_failure_and_timeout(self):
        for script,status,timeout in [('print(input())','completed',3),('raise SystemExit(7)','failed',3),
                                      ('import time; time.sleep(5)','timeout',0.05)]:
            with self.subTest(status=status),tempfile.TemporaryDirectory() as tmp:
                report=Path(tmp)/'report.json'
                cp=subprocess.run([sys.executable,str(WRAPPER),'--report',str(report),'--timeout',str(timeout),
                                   '--',sys.executable,'-c',script],input='hello\n',text=True,capture_output=True)
                r=json.loads(report.read_text())
                self.assertEqual(r['status'],status)
                self.assertGreater(r['elapsed_seconds'],0)
                self.assertTrue(r['started_at'])
                self.assertTrue(r['finished_at'])
                if status=='completed':
                    self.assertEqual(cp.stdout,'hello\n')
                    self.assertEqual(cp.returncode,0)
                if status=='failed':
                    self.assertEqual(r['returncode'],7)
                if status=='timeout':
                    self.assertEqual(cp.returncode,124)
                    self.assertLess(r['elapsed_seconds'],3)


class PromptDeliveryTests(unittest.TestCase):
    def make_input(self, root):
        (root / 'context').mkdir()
        (root / 'context/description.md').write_text('字段说明：Date 是交易日期。\n', encoding='utf-8')
        (root / 'context/hints.md').write_text('规则：所有指数采用共同截止日期。\n', encoding='utf-8')
        return {'context': 'Hints are available only when enabled.', 'query': 'Find the top five.'}

    def test_complete_text_and_auditable_hashes_without_hidden_answers(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            task = self.make_input(root)
            (root / 'answer').mkdir()
            (root / 'answer/secret.txt').write_text('HIDDEN_GOLD_SENTINEL', encoding='utf-8')
            prompt, delivery = build_prompt(root, task, 'Use pandas.', complete_requirements=True)
            self.assertIn(task['query'], prompt)
            self.assertIn('Hints are enabled for this run.', prompt)
            self.assertIn('equally binding', prompt)
            self.assertNotIn('HIDDEN_GOLD_SENTINEL', prompt)
            self.assertTrue(delivery['hints_enabled'])
            self.assertEqual(len(delivery['inline_sources']), 2)
            for item in delivery['inline_sources']:
                source = root / item['path']
                self.assertIn(source.read_text(encoding='utf-8'), prompt)
                self.assertEqual(item['sha256'], hashlib.sha256(source.read_bytes()).hexdigest())
            self.assertEqual(delivery['prompt_sha256'], hashlib.sha256(prompt.encode('utf-8')).hexdigest())

    def test_incomplete_or_invalid_documents_fail(self):
        for name in ['description.md', 'hints.md']:
            for content, error in [(None, FileNotFoundError), (b' \n', ValueError), (b'\xff', UnicodeError)]:
                with self.subTest(name=name, content=content), tempfile.TemporaryDirectory() as tmp:
                    root = Path(tmp)
                    task = self.make_input(root)
                    source = root / 'context' / name
                    if content is None:
                        source.unlink()
                    else:
                        source.write_bytes(content)
                    with self.assertRaises(error):
                        build_prompt(root, task, 'Use pandas.', complete_requirements=True)

    def test_file_reference_mode_is_not_marked_complete(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            task = self.make_input(root)
            prompt, delivery = build_prompt(root, task, 'Use pandas.')
            self.assertNotIn('所有指数', prompt)
            self.assertEqual(delivery['mode'], 'file_references')
            self.assertIsNone(delivery['hints_enabled'])
            self.assertEqual(delivery['inline_sources'], [])

    def test_actual_subprocess_input_matches_saved_prompt(self):
        import generate
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            task = self.make_input(root)
            task_dir = root / 'tasks/task1'
            task_dir.mkdir(parents=True)
            (task_dir / 'task.json').write_text(json.dumps(task), encoding='utf-8')
            run = root / 'run'
            sent = []

            def fake_process(command, **kwargs):
                if command[:2] == ['docker', 'run']:
                    self.assertEqual(kwargs['encoding'], 'utf-8')
                    sent.append(kwargs['input'])
                    metrics_mount = next(x for x in command if x.endswith(':/runner/metrics:rw'))
                    metrics = Path(metrics_mount[:-len(':/runner/metrics:rw')])
                    (metrics / 'codex.json').write_text(json.dumps({'status': 'completed', 'returncode': 0}), encoding='utf-8')
                    (run / 'work/solution.py').write_text('print("test fixture")', encoding='utf-8')
                    (run / 'work/answer.json').write_text('{"answer":"test fixture"}', encoding='utf-8')
                return subprocess.CompletedProcess(command, 0)

            argv = ['generate.py', '--dataset', str(root), '--task', 'task1', '--run-dir', str(run),
                    '--complete-requirements', '--agent', 'codex']
            with patch.object(sys, 'argv', argv), \
                 patch.object(generate, 'settings', return_value={'model': 'test'}), \
                 patch.object(generate, 'label_for', return_value='test'), \
                 patch.object(generate, 'prepare_agent', return_value=([], ['fake-agent'])), \
                 patch.object(generate, 'archive_sessions', return_value=None), \
                 patch.object(generate.subprocess, 'run', side_effect=fake_process), \
                 patch('builtins.print'):
                self.assertEqual(generate.main(), 0)
            self.assertEqual(len(sent), 1)
            self.assertEqual(sent[0].encode('utf-8'), (run / 'detail/prompt.txt').read_bytes())
            for name in ['description.md', 'hints.md']:
                self.assertIn((root / 'context' / name).read_text(encoding='utf-8'), sent[0])
            delivery = json.loads((run / 'detail/input_delivery.json').read_text(encoding='utf-8'))
            self.assertTrue(delivery['hints_enabled'])
            self.assertEqual(delivery['prompt_sha256'], hashlib.sha256(sent[0].encode('utf-8')).hexdigest())


if __name__=='__main__':
    unittest.main()
