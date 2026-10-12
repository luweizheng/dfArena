"""Verify native MCP configuration without importing host integrations."""
import json
from pathlib import Path
import tempfile
import tomllib
import unittest
from runners.agents import get_agent


class LocalMCPTests(unittest.TestCase):
    def test_native_configs_preserve_provider_and_roundtrip_arguments(self):
        for agent, filename, parse in [('codex', 'config.toml', tomllib.loads),
                                      ('opencode', 'opencode.json', json.loads)]:
            with self.subTest(agent=agent), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                initial = 'model="test"\n[model_providers.test]\nbase_url="https://example.invalid"\n' if agent == 'codex' else json.dumps({'model': 'test/model', 'provider': {'test': {'options': {'baseURL': 'https://example.invalid'}}}})
                p = root / filename;p.write_text(initial);p.chmod(0o600)
                name = 'clarification."测试'
                command = ['bash', '-c', 'echo "hello"\n# \\ path']
                env = {'URL': 'http://host/session/ask', 'SESSION': 'quote"\\\n测试'}
                adapter = get_agent(agent)
                adapter.configure_local_mcp(root, name, command, env,
                                            startup_timeout_seconds=13, tool_timeout_seconds=47)
                config = parse(p.read_text())
                for key,value in parse(initial).items():self.assertEqual(config[key],value)
                if agent == 'codex':
                    server=config['mcp_servers'][name]
                    self.assertEqual([server['command'],*server['args']],command)
                    self.assertEqual(server['env'],env)
                    self.assertEqual(server['startup_timeout_sec'],13)
                    self.assertEqual(server['tool_timeout_sec'],47)
                    self.assertTrue(server['required'])
                else:
                    server=config['mcp'][name]
                    self.assertEqual(server['command'],command)
                    self.assertEqual(server['environment'],env)
                    self.assertEqual(server['timeout'],47000)
                    self.assertTrue(server['enabled'])
                self.assertEqual(p.stat().st_mode & 0o777,0o600)
                before=p.read_bytes()
                with self.assertRaisesRegex(ValueError,'already configured'):
                    adapter.configure_local_mcp(root,name,command,env)
                self.assertEqual(p.read_bytes(),before)
                adapter.configure_local_mcp(root,'second',['python','adapter.py'],{})
                self.assertIn(name,parse(p.read_text())['mcp_servers' if agent=='codex' else 'mcp'])

    def test_invalid_spec_does_not_write(self):
        for agent,filename in [('codex','config.toml'),('opencode','opencode.json')]:
            with self.subTest(agent=agent),tempfile.TemporaryDirectory() as tmp:
                root=Path(tmp);p=root/filename;p.write_text('')
                for command,start,tool in [([],30,180),(['python'],0,180),(['python'],30,-1)]:
                    with self.assertRaises(ValueError):
                        get_agent(agent).configure_local_mcp(root,'test',command,{},startup_timeout_seconds=start,tool_timeout_seconds=tool)
                    self.assertEqual(p.read_text(),'')
