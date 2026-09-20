import argparse
import json
import os
from pathlib import Path
import tempfile
import sqlite3
import unittest
from unittest.mock import patch

from runners.agents import settings, prepare_agent, label_for, archive_sessions, add_agent_options, forwarded_options, get_agent
from runners.results import opencode_metrics, token_usage, save, summarize


def finish(part_id, tokens=None, **extra):
    return {'type':'step_finish','sessionID':'s1','part':{'id':part_id,'tokens':tokens or
        {'input':10,'output':20,'reasoning':3,'total':100,'cache':{'read':60,'write':7}},'cost':0.01,**extra}}


class OpenCodeTests(unittest.TestCase):
    def test_codex_adapter_preserves_isolation_and_command(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root/'source'; source.mkdir()
            target = root/'target'; target.mkdir()
            (source/'config.toml').write_text('model="configured"\nmodel_reasoning_effort="medium"\n[mcp_servers.private]\ncommand="private"\n')
            (source/'auth.json').write_text('{"token":"test-only"}')
            (source/'sessions').mkdir()
            (source/'sessions/old.jsonl').write_text('old session')
            parser = argparse.ArgumentParser()
            add_agent_options(parser)
            args = parser.parse_args(['--codex-config-dir', str(source)])
            args.model = 'override'; args.agent_model = None
            info = settings(args)
            flags, command = prepare_agent(args, target, info)
            self.assertEqual(info['model'], 'override')
            self.assertEqual(command[-3:], ['--model', 'override', '-'])
            self.assertNotIn('mcp_servers', (target/'config.toml').read_text())
            self.assertFalse((target/'sessions').exists())
            self.assertNotIn('test-only', ' '.join(flags+command))
            self.assertEqual(forwarded_options(args), ['--agent', 'codex', '--codex-config-dir', str(source.resolve())])
            sessions = target/'sessions'; sessions.mkdir()
            (sessions/'new.jsonl').write_text('new session')
            run = root/'run'
            self.assertEqual(archive_sessions('codex', target, run), 'detail/codex_sessions')
            self.assertEqual((run/'detail/codex_sessions/new.jsonl').read_text(), 'new session')
            self.assertFalse((run/'detail/codex_sessions/auth.json').exists())
            with (source/'config.toml').open('a') as config:
                config.write('\n[model_providers.custom]\nenv_key="DFARENA_TEST_API_KEY"\n')
            text = (source/'config.toml').read_text()
            (source/'config.toml').write_text('model_provider="custom"\n'+text)
            with patch.dict(os.environ, {'DFARENA_TEST_API_KEY': 'private-test-value'}):
                flags, command = prepare_agent(args, target, info)
                self.assertEqual(flags[-2:], ['-e', 'DFARENA_TEST_API_KEY'])
                self.assertNotIn('private-test-value', ' '.join(flags+command))
            with patch.dict(os.environ, {}, clear=True):
                with self.assertRaisesRegex(ValueError, 'Missing Codex provider'):
                    prepare_agent(args, target, info)

    def test_unknown_agent_rejected(self):
        with self.assertRaisesRegex(ValueError, 'Unsupported coding agent'):
            get_agent('unknown')

    def test_session_archive_includes_wal_but_not_auth(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            config = root/'config'
            data = config/'data'
            data.mkdir(parents=True)
            (data/'auth.json').write_text('{"secret":"credential"}')
            with sqlite3.connect(data/'opencode.db') as db:
                db.execute('PRAGMA journal_mode=WAL')
                db.execute('CREATE TABLE session (id TEXT)')
                db.execute("INSERT INTO session VALUES ('test-session')")
                db.commit()
                run = root/'run'
                self.assertEqual(archive_sessions('opencode', config, run), 'detail/opencode_sessions')
                dest = run/'detail/opencode_sessions'
                self.assertEqual([p.name for p in dest.iterdir()], ['opencode.db'])
                with sqlite3.connect(dest/'opencode.db') as saved:
                    self.assertEqual(saved.execute('SELECT id FROM session').fetchone()[0], 'test-session')

    def test_native_usage_and_dedup(self):
        a=finish('one');b=finish('two')
        r=opencode_metrics([a,a,b],True)
        self.assertEqual(r['token_usage_steps'],2)
        self.assertEqual(r['token_usage']['input_tokens'],154)
        self.assertEqual(r['token_usage']['total_tokens'],200)
        self.assertEqual(r['token_usage']['cached_input_tokens'],120)
        self.assertEqual(r['token_usage']['reasoning_tokens'],6)
        self.assertEqual(r['reported_cost'],0.02)
        self.assertEqual(r['token_usage_status'],'complete')
        self.assertEqual(r['session_ids'],['s1'])

    def test_missing_partial_and_error_events(self):
        self.assertIsNone(opencode_metrics([],True)['token_usage'])
        r=opencode_metrics([finish('one',{'input':1,'output':2})],True)
        self.assertIsNone(r['token_usage']['total_tokens'])
        self.assertIsNone(r['token_usage']['cached_input_tokens'])
        r=opencode_metrics([finish('one'),{'type':'step_finish','part':{}}],True)
        self.assertEqual(r['token_usage_status'],'partial')
        r=opencode_metrics([finish('one'),{'type':'error','error':{'name':'APIError','message':'secret'}}],True)
        self.assertEqual(r['agent_errors'],['APIError'])
        self.assertNotIn('secret',json.dumps(r))
        self.assertEqual(r['token_usage_status'],'partial')
        self.assertEqual(opencode_metrics([finish('one')],False)['token_usage_status'],'partial')

    def test_file_parser_and_summary(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);log=root/'opencode.jsonl'
            log.write_text('not-json\n'+json.dumps(finish('one'))+'\n')
            stats=token_usage(log,True,agent='opencode')
            save(root/'detail/generation.json',{'status':'completed',**stats})
            result=summarize(root)
            self.assertEqual(result['generation']['token_usage_steps'],1)
            self.assertEqual(result['generation']['token_usage_basis'],'opencode_inclusive_cache_and_reasoning')

    def test_config_allowlist_credentials_and_command(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);config=root/'source.json';target=root/'target';target.mkdir()
            config.write_text(json.dumps({'model':'test/model','mcp':{'secret':{}},'plugin':['bad-plugin'],
                'instructions':['private.md'],'provider':{'test':{'npm':'@ai-sdk/openai-compatible',
                'options':{'apiKey':'{env:TEST_AGENT_KEY}'},'models':{'model':{'variants':{'high':{'reasoningEffort':'high'}}}}},
                'other':{'options':{'apiKey':'other-secret'}}}}))
            auth=root/'auth.json';auth.write_text(json.dumps({'test':{'key':'test-key'},'other':{'key':'other-key'}}))
            args=argparse.Namespace(agent='opencode',model=None,variant='high',opencode_config=config,
                opencode_auth=auth,agent_model=None)
            info=settings(args)
            with patch.dict(os.environ,{'TEST_AGENT_KEY':'private-key'}):
                flags,cmd=prepare_agent(args,target,info)
            out=json.loads((target/'opencode.json').read_text())
            self.assertEqual(list(out['provider']),['test'])
            self.assertEqual(out['provider']['test']['options']['apiKey'],'private-key')
            for k in ('mcp','plugin','instructions'):
                self.assertNotIn(k,out)
            self.assertEqual(list(json.loads((target/'auth.json').read_text())),['test'])
            self.assertNotIn('private-key',' '.join(flags+cmd))
            self.assertIn('--auto',cmd)
            self.assertIn('--pure',cmd)
            self.assertNotIn('--session',cmd)
            self.assertEqual(info['reasoning_effort'],'high')
            self.assertEqual(label_for(args,info),'opencode_model')

    def test_requires_explicit_model_when_config_has_no_default(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'config.json';p.write_text('{}')
            args=argparse.Namespace(agent='opencode',model=None,variant=None,opencode_config=p)
            with self.assertRaisesRegex(ValueError,'provider/model'):
                settings(args)


if __name__=='__main__':
    unittest.main()
