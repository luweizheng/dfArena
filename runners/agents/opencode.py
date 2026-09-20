"""OpenCode CLI, provider configuration, SQLite archive and native usage parsing."""
import copy
import json
import os
from pathlib import Path
import re
import sqlite3

from .base import AgentAdapter


def _expand(value):
    if isinstance(value, dict):
        return {k:_expand(v) for k,v in value.items()}
    if isinstance(value, list):
        return [_expand(v) for v in value]
    if isinstance(value, str):
        if '{file:' in value:
            raise ValueError('File substitutions in OpenCode provider config are not supported; use env substitutions')
        def substitute(match):
            name = match.group(1)
            if name not in os.environ:
                raise ValueError(f'Missing OpenCode provider environment variable: {name}')
            return os.environ[name]
        return re.sub(r'\{env:([^}]+)\}', substitute, value)
    return value


def opencode_metrics(events, completed, source='opencode:step_finish.part.tokens'):
    """OpenCode 1.18.29 separates cache from input, and reasoning from output.

    Normalize to inclusive input/output totals and preserve native counters.
    Missing sub-counters remain unknown, never silently become zero.
    """
    finishes = []
    seen = set()
    errors = []
    sessions = set()
    for event in events:
        if not isinstance(event, dict):
            continue
        if event.get('sessionID'):
            sessions.add(event['sessionID'])
        if event.get('type') == 'error':
            # Do not copy provider response bodies or possible secrets to summaries.
            error = event.get('error', {})
            errors.append(error.get('name', 'OpenCodeError') if isinstance(error, dict) else 'OpenCodeError')
        if event.get('type') != 'step_finish':
            continue
        part = event.get('part', {})
        if not isinstance(part, dict):
            part = {}
        identity = (event.get('sessionID'), part.get('id'))
        if part.get('id') and identity in seen:
            continue
        seen.add(identity)
        finishes.append(part)
    good = [p for p in finishes if isinstance(p.get('tokens'), dict) and
            all(type(p['tokens'].get(k)) is int and p['tokens'][k] >= 0 for k in ('input','output'))]
    def total(values):
        return sum(values) if values and all(type(v) is int and v >= 0 for v in values) else None
    usage = None
    if good:
        usage = {name:total([p['tokens'].get(key) for p in good]) for name,key in
                 [('input_tokens','input'),('output_tokens','output'),('reasoning_tokens','reasoning'),('total_tokens','total')]}
        for name,key in [('cached_input_tokens','read'),('cache_write_tokens','write')]:
            usage[name] = total([p['tokens'].get('cache',{}).get(key) if isinstance(p['tokens'].get('cache'),dict) else None for p in good])
    native = usage
    if native:
        def add(*values):
            return sum(values) if all(v is not None for v in values) else None
        input_total = add(native['input_tokens'], native['cached_input_tokens'], native['cache_write_tokens'])
        output_total = add(native['output_tokens'], native['reasoning_tokens'])
        usage = {'input_tokens':input_total, 'output_tokens':output_total,
                 'total_tokens':add(input_total, output_total),
                 'cached_input_tokens':native['cached_input_tokens'],
                 'cache_write_tokens':native['cache_write_tokens'],
                 'reasoning_tokens':native['reasoning_tokens']}
    costs = [p.get('cost') for p in finishes]
    import math
    cost = sum(costs) if costs and all(type(v) in (int,float) and math.isfinite(v) and v >= 0 for v in costs) else None
    return {'token_usage':usage,'token_usage_status':'unavailable' if not good else
            'complete' if completed and not errors and len(good)==len(finishes) and usage['total_tokens'] is not None else 'partial',
            'token_usage_basis':'opencode_inclusive_cache_and_reasoning', 'token_usage_native':native, 'token_usage_source':source,
            'token_usage_steps':len(good),'reported_cost':cost,
            'agent_errors':errors,'session_ids':sorted(sessions)}


class OpenCodeAgent(AgentAdapter):
    name = "opencode"

    def add_options(self, parser):
        parser.add_argument('--opencode-config', type=Path, default=Path(__file__).resolve().parents[1]/'configs/opencode/opencode.json')
        parser.add_argument('--opencode-auth', type=Path, default=Path(__file__).resolve().parents[1]/'configs/opencode/auth.json')
        parser.add_argument('--variant', help='OpenCode model variant; not a Codex reasoning override')

    def forwarded_options(self, args):
        options = ['--opencode-config', str(args.opencode_config.expanduser().resolve()),
                   '--opencode-auth', str(args.opencode_auth.expanduser().resolve())]
        if args.variant:
            options += ['--variant', args.variant]
        return options

    def model_label(self, model):
        return model.split('/', 1)[-1]

    def settings(self, args):
        config = json.loads(args.opencode_config.expanduser().read_text())
        model = args.model or config.get('model')
        if not isinstance(model, str) or '/' not in model:
            raise ValueError('OpenCode requires --model provider/model or a model in its JSON config')
        provider, model_id = model.split('/', 1)
        if not provider or not model_id:
            raise ValueError('OpenCode model must be provider/model')
        model_spec = config.get('provider', {}).get(provider, {}).get('models', {}).get(model_id, {})
        effort = model_spec.get('options', {}).get('reasoningEffort')
        if args.variant:
            effort = model_spec.get('variants', {}).get(args.variant, {}).get('reasoningEffort')
        return {'name': 'opencode', 'model': model, 'variant': args.variant, 'reasoning_effort': effort}

    def prepare(self, args, target, info):
        original = json.loads(args.opencode_config.expanduser().read_text())
        provider = info['model'].split('/', 1)[0]
        selected = copy.deepcopy(original.get('provider', {}).get(provider))
        config = {'model': info['model'], 'share': 'disabled', 'autoupdate': False, 'permission': 'allow', 'enabled_providers': [provider]}
        if selected is not None:
            config['provider'] = {provider: _expand(selected)}
        config_path = target / 'opencode.json'
        config_path.write_text(json.dumps(config))
        config_path.chmod(0o600)
        data = target / 'data'
        data.mkdir()
        flags = ['-v', f'{config_path}:/runner/opencode.json:ro', '-e', 'OPENCODE_CONFIG=/runner/opencode.json', '-v', f'{data}:/root/.local/share/opencode:rw']
        auth_path = args.opencode_auth.expanduser()
        if auth_path.exists():
            auth = json.loads(auth_path.read_text())
            local_auth = target / 'auth.json'
            local_auth.write_text(json.dumps({provider: auth[provider]} if provider in auth else {}))
            local_auth.chmod(0o600)
            flags += ['-v', f'{local_auth}:/root/.local/share/opencode/auth.json:rw']
        command = ['opencode', 'run', '--pure', '--auto', '--format', 'json', '--agent', 'build', '--model', info['model']]
        if args.variant:
            command += ['--variant', args.variant]
        return (flags, command)

    def archive_sessions(self, config_dir, run):
        source = config_dir/'data/opencode.db'
        if not source.is_file():
            return None
        destination = run/'detail/opencode_sessions'
        destination.mkdir(parents=True)
        # Backup includes committed WAL pages without copying credentials or live WAL files.
        with sqlite3.connect(source.resolve().as_uri()+'?mode=ro', uri=True) as original:
            with sqlite3.connect(destination/'opencode.db') as archived:
                original.backup(archived)
        return str(destination.relative_to(run))

    def metrics(self, events, completed, source):
        return opencode_metrics(events, completed, source=source+':step_finish.part.tokens')
