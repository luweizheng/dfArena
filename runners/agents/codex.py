"""Codex CLI, isolated TOML configuration, rollout archive and usage parsing."""
import json
import os
from pathlib import Path
import shutil
import tomllib

from .base import AgentAdapter


def isolated_codex(source, target):
    config = tomllib.loads((source/'config.toml').read_text())
    lines = []
    for key in ('model', 'model_provider', 'model_reasoning_effort', 'disable_response_storage'):
        if key in config:
            lines.append(key+' = '+json.dumps(config[key]))
    for name, fields in config.get('model_providers', {}).items():
        lines.append('\n[model_providers.'+json.dumps(name)+']')
        for key, value in fields.items():
            if not isinstance(value, (str, bool, int, float)):
                raise ValueError('Unsupported provider setting')
            lines.append(key+' = '+json.dumps(value))
    (target/'config.toml').write_text('\n'.join(lines)+'\n')
    (target/'config.toml').chmod(0o600)
    if (source/'auth.json').exists():
        shutil.copy2(source/'auth.json', target/'auth.json')
    return config


def token_metrics(events, completed, source='logs/agent_events.jsonl:turn.completed.usage'):
    events = [e for e in events if isinstance(e, dict) and e.get('type') == 'turn.completed']
    usages = [e['usage'] for e in events if isinstance(e.get('usage'), dict) and
              all(type(e['usage'].get(k)) is int and e['usage'][k] >= 0
                  for k in ('input_tokens', 'output_tokens'))]
    total = None
    if usages:
        total = {k: sum(u[k] for u in usages) for k in ('input_tokens', 'output_tokens')}
        cached = [u.get('cached_input_tokens') for u in usages]
        total['cached_input_tokens'] = sum(cached) if all(type(v) is int and v >= 0 for v in cached) else None
        total['total_tokens'] = total['input_tokens'] + total['output_tokens']
    return {'token_usage': total, 'token_usage_status': 'unavailable' if not usages else
            'complete' if completed and len(usages) == len(events) else 'partial',
            'token_usage_source': source,
            'token_usage_turns': len(usages)}


class CodexAgent(AgentAdapter):
    name = "codex"

    def add_options(self, parser):
        parser.add_argument('--codex-config-dir', type=Path, default=Path(__file__).resolve().parents[1]/'configs/codex')

    def forwarded_options(self, args):
        return ['--codex-config-dir', str(args.codex_config_dir.expanduser().resolve())]

    def settings(self, args):
        if args.variant:
            raise ValueError('--variant is only supported with --agent opencode')
        config = tomllib.loads((args.codex_config_dir.expanduser() / 'config.toml').read_text())
        return {'name': 'codex', 'model': args.model or config.get('model'), 'reasoning_effort': config.get('model_reasoning_effort')}

    def prepare(self, args, target, info):
        config = isolated_codex(args.codex_config_dir.expanduser(), target)
        flags = ['-v', f'{target}:/root/.codex:rw']
        provider = config.get('model_providers', {}).get(config.get('model_provider'), {})
        env_key = provider.get('env_key')
        if env_key:
            if env_key not in os.environ:
                raise ValueError(f'Missing Codex provider environment variable: {env_key}')
            # Docker inherits the value from its environment; command.json contains only the name.
            flags += ['-e', env_key]
        command = ['codex', 'exec', '--json', '--dangerously-bypass-approvals-and-sandbox', '--skip-git-repo-check']
        if info['model']:
            command += ['--model', info['model']]
        return flags, command + ['-']

    def configure_local_mcp(self, config_dir, name, command, environment, *,
                            startup_timeout_seconds=30, tool_timeout_seconds=180):
        if not command or startup_timeout_seconds <= 0 or tool_timeout_seconds <= 0:
            raise ValueError('MCP requires a command and positive timeouts')
        path = config_dir / 'config.toml'
        existing = path.read_text()
        if name in tomllib.loads(existing).get('mcp_servers', {}):
            raise ValueError(f'MCP server already configured: {name}')
        # JSON strings with literal Unicode are valid TOML basic strings too.
        quote = lambda value: json.dumps(value, ensure_ascii=False)
        section = 'mcp_servers.' + quote(name)
        lines = [f'\n[{section}]', 'command = ' + quote(command[0]),
                 'args = ' + quote(command[1:]),
                 f'startup_timeout_sec = {startup_timeout_seconds}',
                 f'tool_timeout_sec = {tool_timeout_seconds}', 'required = true',
                 f'[{section}.env]']
        lines.extend(quote(k) + ' = ' + quote(v) for k, v in environment.items())
        path.write_text(existing + '\n'.join(lines) + '\n')

    def archive_sessions(self, config_dir, run):
        source = config_dir/'sessions'
        if not source.exists():
            return None
        destination = run/'detail/codex_sessions'
        shutil.copytree(source, destination)
        return str(destination.relative_to(run))

    def metrics(self, events, completed, source):
        return token_metrics(events, completed, source=source+':turn.completed.usage')
