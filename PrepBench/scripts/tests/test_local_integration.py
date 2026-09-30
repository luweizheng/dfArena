import os
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'scripts'))
from simulator.case_views import load_internal_case_view
from generate import prepare, next_run


class LocalIntegration(unittest.TestCase):
    def test_six_local_assets(self):
        for i in range(1, 7):
            view = load_internal_case_view(ROOT / f'case_{i:03d}', require_reference_solution=True)
            self.assertIn('def solve', view.reference_solution_text)
            self.assertTrue(view.input_files)
            self.assertEqual(view.query_full_text, (view.case_dir / 'query_full.md').read_text())

    def test_public_workspace(self):
        for mode in ['interact', 'clarified']:
            with tempfile.TemporaryDirectory() as tmp:
                work, prompt = prepare(ROOT / 'case_006', Path(tmp), mode, 'ibis')
                self.assertEqual({p.name for p in work.iterdir()}, {'outputs'})
                self.assertTrue((Path(tmp) / 'assets.json').exists())
                self.assertIn('/workspace/work/outputs/', prompt)
                self.assertEqual('clarification.ask' in prompt, mode == 'interact')

    def test_run_numbering(self):
        with tempfile.TemporaryDirectory() as tmp:
            case = Path(tmp)
            first = next_run(case, 'interact', 'codex_test', 'polars')
            second = next_run(case, 'interact', 'codex_test', 'polars')
            separate = next_run(case, 'clarified', 'codex_test', 'polars')
            self.assertEqual(first.relative_to(case).as_posix(), 'runs/interact/codex_test/polars/r001')
            self.assertEqual(second.name, 'r002')
            self.assertEqual(separate.name, 'r001')

    def test_http_routes_with_fake_model(self):
        from fastapi.testclient import TestClient
        from simulator.user_simulator import UserSimulatorResult, UserSimulatorAnswerItem
        with tempfile.TemporaryDirectory() as tmp, patch.dict(os.environ, {
            'DFARENA_ADMIN_TOKEN': 'test-admin',
            'DFARENA_TRACE': str(Path(tmp) / 'trace.jsonl'),
            'DFARENA_CASE_ROOT': str(ROOT),
            'PREPBENCH_SIMULATOR_MODEL': 'test-model',
            'PREPBENCH_SIMULATOR_API_KEY': 'test-key',
        }):
            import simulator_server as server
            client = TestClient(server.app)
            self.assertEqual(client.post('/session/start', json={'case_id':'006','run_id':'test'}).status_code,403)
            response=client.post('/session/start', headers={'Authorization':'Bearer test-admin'},json={'case_id':'006','run_id':'test'})
            self.assertEqual(response.status_code,200)
            sid=response.json()['session_id']
            fake=UserSimulatorResult(answers=[UserSimulatorAnswerItem('month?', 'hit', 'lib', '2019-03-19', '5_O1_march_month_start_date_representation')],raw_response='',messages=[])
            with patch.object(server, 'trace', Path(tmp)/'trace.jsonl'),                 patch.object(server.api.user_simulator, 'answer', return_value=fake):
                reply=client.post('/session/ask',json={'session_id':sid,'questions':['month?']})
            record=json.loads((Path(tmp)/'trace.jsonl').read_text())
            self.assertGreaterEqual(record['elapsed_seconds'], 0)
            self.assertEqual(record['time'],record['started_at'])
            self.assertGreaterEqual(record['finished_at'],record['started_at'])
            with patch.object(server, 'trace', Path(tmp)/'trace.jsonl'),                 patch.object(server.api.user_simulator, 'answer', side_effect=TimeoutError('test')):
                failed=client.post('/session/ask',json={'session_id':sid,'questions':['month?']})
            self.assertEqual(failed.status_code,502)
            records=[json.loads(line) for line in (Path(tmp)/'trace.jsonl').read_text().splitlines()]
            self.assertEqual(records[-1]['error_type'],'TimeoutError')
            self.assertGreaterEqual(records[-1]['elapsed_seconds'],0)
            self.assertEqual(server.api._sessions[sid].used_rounds,1)
            self.assertEqual(reply.status_code,200)
            self.assertEqual(reply.json()['answers'][0]['answer'],'2019-03-19')
            self.assertEqual(reply.json()['answers'][0]['question'],'month?')
            self.assertNotIn('budget', reply.json())
            self.assertNotIn('classification', reply.json()['answers'][0])

if __name__ == '__main__':
    unittest.main()
