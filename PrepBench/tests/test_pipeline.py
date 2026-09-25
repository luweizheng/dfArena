import contextlib
import io
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import evaluate as prep_evaluate
import run_benchmark as pipeline
from runners.results import save, summarize


class PipelineTests(unittest.TestCase):
    def test_both_modes_chain_evaluation_and_preserve_generation(self):
        for mode in ['clarified','interact']:
            with self.subTest(mode=mode),tempfile.TemporaryDirectory() as tmp:
                run=Path(tmp)/'run'; run.mkdir()
                config=Path(tmp)/'codex'; config.mkdir()
                (config/'config.toml').write_text('model="test"\n')
                calls=[]
                def execute(cmd):
                    calls.append(Path(cmd[1]).name)
                    if calls[-1]=='generate.py':
                        self.assertEqual(cmd[cmd.index('--mode')+1],mode)
                        shutil.copytree(ROOT/'case_001/evaluation/gt',run/'workspace/outputs')
                        gen={'benchmark':'PrepBench','task':'case_001','mode':mode,'status':'completed',
                             'elapsed_seconds':1,'timing_scope':'codex_process'}
                        save(run/'detail/generation.json',gen)
                        summarize(run)
                        return subprocess.CompletedProcess(cmd,0)
                    return subprocess.CompletedProcess(cmd,prep_evaluate.main(cmd[2:]))
                with patch.object(pipeline,'next_run',return_value=run),patch.object(pipeline.subprocess,'run',side_effect=execute),contextlib.redirect_stdout(io.StringIO()):
                    rc=pipeline.main(['--case','001','--mode',mode,'--codex-config-dir',str(config)])
                self.assertEqual(rc,0)
                self.assertEqual(calls,['generate.py','evaluate.py'])
                gen_path=run/'detail/generation.json'
                original=gen_path.read_bytes()
                summary=json.loads((run/'result.json').read_text())
                self.assertTrue(summary['evaluation']['passed'])
                self.assertEqual(summary['generation']['elapsed_seconds'],1)
                with contextlib.redirect_stdout(io.StringIO()):
                    self.assertEqual(prep_evaluate.main(['--case','001','--run-dir',str(run)]),0)
                self.assertEqual(gen_path.read_bytes(),original)

    def test_generation_failure_skips_evaluation(self):
        with tempfile.TemporaryDirectory() as tmp:
            run=Path(tmp)/'run';run.mkdir()
            config=Path(tmp)/'cfg';config.mkdir()
            (config/'config.toml').write_text('model="test"\n')
            def execute(cmd):
                save(run/'detail/generation.json',{'benchmark':'PrepBench','task':'case_001','status':'timeout'})
                return subprocess.CompletedProcess(cmd,1)
            with patch.object(pipeline,'next_run',return_value=run),patch.object(pipeline.subprocess,'run',side_effect=execute) as mock,contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(pipeline.main(['--case','001','--codex-config-dir',str(config)]),1)
            self.assertEqual(mock.call_count,1)
            summary=json.loads((run/'result.json').read_text())
            self.assertEqual(summary['evaluation']['status'],'skipped')
            self.assertIsNone(summary['evaluation']['passed'])

    def test_bad_candidate_and_config_error_distinguished(self):
        for invalid_config in [False,True]:
            with self.subTest(invalid_config=invalid_config),tempfile.TemporaryDirectory() as tmp:
                root=Path(tmp)
                case=root/'case_001'
                shutil.copytree(ROOT/'case_001/evaluation',case/'evaluation')
                run=root/'run'
                shutil.copytree(case/'evaluation/gt',run/'workspace/outputs')
                save(run/'detail/generation.json',{'benchmark':'PrepBench','task':'case_001','status':'completed'})
                if invalid_config:
                    (case/'evaluation/config.json').write_text('{}')
                else:
                    (run/'workspace/outputs/output_01.csv').unlink()
                with patch.object(prep_evaluate,'ROOT',root),contextlib.redirect_stdout(io.StringIO()):
                    self.assertEqual(prep_evaluate.main(['--case','001','--run-dir',str(run)]),1)
                report=json.loads((run/'detail/evaluation.json').read_text())
                self.assertEqual(report['status'],'error' if invalid_config else 'completed')
                self.assertEqual(report['passed'],None if invalid_config else False)
                self.assertIn('assets',report['report'])


if __name__=='__main__':
    unittest.main()
