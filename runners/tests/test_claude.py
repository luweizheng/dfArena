import argparse
import json
from pathlib import Path
import tempfile
import unittest
from runners.agents import get_agent

class ClaudeTests(unittest.TestCase):
    def test_isolation_and_mcp(self):
        agent=get_agent('claude')
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); source=root/'source.json'
            source.write_text(json.dumps({'model':'test-model','env':{'ANTHROPIC_BASE_URL':'https://example.invalid','ANTHROPIC_AUTH_TOKEN':'test-secret','UNRELATED':'ignored'},'hooks':{'ignored':True},'mcpServers':{'private':{}}}))
            args=argparse.Namespace(claude_config=source,model=None)
            target=root/'isolated';target.mkdir()
            flags,cmd=agent.prepare(args,target,agent.settings(args))
            config=json.loads((target/'settings.json').read_text())
            self.assertNotIn('hooks',config)
            self.assertNotIn('UNRELATED',config['env'])
            self.assertNotIn('test-secret',' '.join(flags+cmd))
            self.assertEqual((target/'settings.json').stat().st_mode & 0o777,0o600)
            agent.configure_local_mcp(target,'clarification',['python','service.py'],{'URL':'local'})
            server=json.loads((target/'mcp.json').read_text())['mcpServers']
            self.assertEqual(list(server),['clarification'])
            self.assertEqual(server['clarification']['args'],['service.py'])
            with self.assertRaises(ValueError):agent.configure_local_mcp(target,'clarification',['x'],{})

    def test_usage_and_errors(self):
        agent=get_agent('claude')
        event={'type':'result','usage':{'input_tokens':10,'output_tokens':5,'cache_read_input_tokens':20,'cache_creation_input_tokens':3},'is_error':False}
        result=agent.metrics([event],True,'test')
        self.assertEqual(result['token_usage']['total_tokens'],38)
        self.assertEqual(result['token_usage_status'],'complete')
        event['is_error']=True;event['subtype']='error_max_turns'
        self.assertEqual(agent.metrics([event],True,'test')['agent_errors'],['error_max_turns'])
        self.assertEqual(agent.metrics([],True,'test')['agent_errors'],['MissingResultEvent'])
        self.assertIsNone(agent.metrics([],False,'test')['token_usage'])

    def test_zero_output_usage_with_generated_content_is_partial(self):
        agent = get_agent('claude')
        events = [
            {'type': 'assistant', 'message': {'content': [{'type': 'text', 'text': 'Done'}]}},
            {'type': 'result', 'usage': {'input_tokens': 10, 'output_tokens': 0,
             'cache_read_input_tokens': 0, 'cache_creation_input_tokens': 0}},
        ]
        result = agent.metrics(events, True, 'test')
        self.assertEqual(result['token_usage_status'], 'partial')
        self.assertEqual(result['token_usage_native']['output_tokens'], 0)
        self.assertEqual(result['agent_errors'], [])
