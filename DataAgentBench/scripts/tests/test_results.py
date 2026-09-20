import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPTS=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(SCRIPTS))
from results import save, summarize, token_usage
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


if __name__=='__main__':
    unittest.main()
