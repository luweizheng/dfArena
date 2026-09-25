import contextlib
from datetime import datetime
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import generate


class MetricsTests(unittest.TestCase):
    def test_usage_aggregation_and_cache(self):
        events = [{'type':'turn.completed','usage':{'input_tokens':100,'cached_input_tokens':80,'output_tokens':20}},
                  {'type':'turn.completed','usage':{'input_tokens':30,'cached_input_tokens':10,'output_tokens':5}}]
        r=generate.token_metrics(events,True)
        self.assertEqual(r['token_usage'],{'input_tokens':130,'output_tokens':25,'cached_input_tokens':90,'total_tokens':155})
        self.assertEqual(r['token_usage_status'],'complete')
        self.assertEqual(generate.token_metrics(events,False)['token_usage_status'],'partial')

    def test_missing_usage_not_zero(self):
        r=generate.token_metrics([],False)
        self.assertIsNone(r['token_usage'])
        self.assertEqual(r['token_usage_status'],'unavailable')
        events=[{'type':'turn.completed','usage':{'input_tokens':1,'output_tokens':2}},
                {'type':'turn.completed','usage':None}]
        r=generate.token_metrics(events,True)
        self.assertEqual(r['token_usage_status'],'partial')
        self.assertIsNone(r['token_usage']['cached_input_tokens'])

    def test_success_timeout_and_prelaunch_failure(self):
        for agent, outcome in [(a, o) for a in ['codex','opencode'] for o in ['success','timeout','setup_failure']]:
            with self.subTest(agent=agent,outcome=outcome), tempfile.TemporaryDirectory() as tmp:
                root=Path(tmp); run=root/'run'; run.mkdir()
                config=root/'config'; config.mkdir()
                (config/'config.toml').write_text('model="test-model"\nmodel_reasoning_effort="medium"\n')
                opencode_config=root/'opencode.json'
                opencode_config.write_text(json.dumps({'model':'test/model','provider':{}}))
                def fake_run(cmd, **kwargs):
                    if cmd[:2]==['docker','run']:
                        kwargs['stdout'].write('{"type":"thread.started","thread_id":"test-session"}\n')
                        mount=next(x for x in cmd if x.endswith(':/runner/metrics:rw'))
                        metrics=Path(mount.rsplit(':',2)[0])
                        (metrics/(agent+'.json')).write_text(json.dumps({
                            'started_at':'2026-09-19T00:00:00+00:00',
                            'finished_at':'2026-09-19T00:00:01+00:00',
                            'elapsed_seconds':1.0,'returncode':-15 if outcome=='timeout' else 0,
                            'status':'timeout' if outcome=='timeout' else 'completed',
                            'timing_scope':agent+'_process'}))
                        if outcome=='timeout':
                            return subprocess.CompletedProcess(cmd,124)
                        event={'type':'turn.completed','usage':{'input_tokens':100,'cached_input_tokens':50,'output_tokens':20}} if agent=='codex' else {'type':'step_finish','part':{'tokens':{'input':100,'output':20,'reasoning':0,'cache':{'read':0,'write':0},'total':120}}}
                        kwargs['stdout'].write(json.dumps(event)+'\n')
                        (run/'workspace/outputs/output_01.csv').write_text('x\n1\n')
                        (run/'workspace/solution.py').write_text('# test solution')
                    return subprocess.CompletedProcess(cmd,0)
                args=['generate.py','--case','001','--mode','clarified','--codex-config-dir',str(config),'--agent',agent,'--opencode-config',str(opencode_config),'--opencode-auth',str(root/'missing-auth.json')]
                original=generate.prepare_agent
                def config_copy(*args):
                    if outcome=='setup_failure':
                        raise OSError('test setup failure')
                    return original(*args)
                with patch.object(sys,'argv',args), patch.object(generate,'next_run',return_value=run), \
                     patch.object(generate.subprocess,'run',side_effect=fake_run), \
                     patch.object(generate,'prepare_agent',side_effect=config_copy), \
                     contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                    code=generate.main()
                result=json.loads((run/'detail/generation.json').read_text())
                self.assertEqual(code,0 if outcome=='success' else 1)
                self.assertEqual(result['artifacts']['agent_log'], 'logs/agent_events.jsonl')
                if outcome != 'setup_failure':
                    self.assertTrue((run/'logs/agent_events.jsonl').is_file())
                    self.assertTrue((run/'logs/agent_stderr.log').is_file())
                    self.assertIn('logs/agent_events.jsonl:', result['token_usage_source'])
                if outcome=='setup_failure':
                    self.assertIsNone(result['started_at'])
                    self.assertIsNone(result['elapsed_seconds'])
                else:
                    self.assertLessEqual(datetime.fromisoformat(result['started_at']),datetime.fromisoformat(result['finished_at']))
                    self.assertEqual(result['elapsed_seconds'],1.0)
                    self.assertEqual(result['timing_scope'],agent+'_process')
                self.assertEqual(result['agent']['reasoning_effort'],'medium' if agent=='codex' else None)
                self.assertFalse((run/'run.json').exists())
                self.assertIsNone(json.loads((run/'result.json').read_text())['evaluation']['passed'])
                self.assertEqual(result['token_usage_status'],'complete' if outcome=='success' else 'unavailable')
                self.assertEqual(result['status'],{'success':'completed','timeout':'timeout','setup_failure':'runner_error'}[outcome])


if __name__=='__main__':
    unittest.main()
