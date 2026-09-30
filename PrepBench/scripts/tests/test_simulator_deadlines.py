import json
from pathlib import Path
import sys
import unittest
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from simulator.user_simulator import OpenAICompatibleClient, UserSimulator


class SimulatorDeadlineTests(unittest.TestCase):
    def client(self):
        client = OpenAICompatibleClient(api_key='test', model_name='test',
                                      base_url='http://unused/v1', timeout=120)
        client.session = Mock()
        return client

    def test_retries_stop_at_shared_deadline(self):
        client = self.client()
        client.session.post.return_value = Mock(status_code=429, headers={'Retry-After': '30'})
        with patch('simulator.user_simulator.time.monotonic', side_effect=[0, 1, 1, 5]),             patch('simulator.user_simulator.time.sleep') as sleep:
            with self.assertRaises(TimeoutError):
                client.generate([], temperature=0, max_tokens=50, deadline=5)
        self.assertEqual(client.session.post.call_count, 1)
        self.assertEqual(sum(client.session.post.call_args.kwargs['timeout']), 5)
        sleep.assert_called_once_with(4)

    def test_expired_deadline_never_calls_provider(self):
        client = self.client()
        with patch('simulator.user_simulator.time.monotonic', return_value=10):
            with self.assertRaises(TimeoutError):
                client.generate([], temperature=0, max_tokens=50, deadline=9)
        client.session.post.assert_not_called()

    def test_json_repair_reuses_original_deadline(self):
        simulator = UserSimulator.__new__(UserSimulator)
        simulator._build_prompt = Mock(return_value='test prompt')
        simulator._generate = Mock(side_effect=['invalid', json.dumps({'answers': [{
            'sub_question': 'q', 'classification': 'fallback', 'answer': 'a', 'ref': None
        }]})])
        with patch('simulator.user_simulator.time.monotonic', return_value=10):
            result = simulator.answer(query_full_text='', amb_kb_json={}, solution_text='',
                                      question='q', expected_sub_questions=['q'])
        self.assertIsNone(result.parse_error)
        self.assertEqual(simulator._generate.call_count, 2)
        self.assertEqual([call.kwargs['deadline'] for call in simulator._generate.call_args_list], [150, 150])


if __name__ == '__main__':
    unittest.main()
