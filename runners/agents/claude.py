"""Isolated Claude Code adapter using an Anthropic-compatible provider."""
import json
import shutil
from pathlib import Path
from .base import AgentAdapter


class ClaudeAgent(AgentAdapter):
    name = 'claude'

    def add_options(self, parser):
        parser.add_argument('--claude-config', type=Path, default=Path(__file__).resolve().parents[1]/'configs/claude/settings.json')

    def forwarded_options(self, args):
        return ['--claude-config', str(args.claude_config.expanduser().resolve())]

    def settings(self, args):
        config = json.loads(args.claude_config.expanduser().read_text())
        model = args.model or config.get('model')
        if not isinstance(model, str) or not model:
            raise ValueError('Claude Code requires --model or a model in its settings')
        return {'name': self.name, 'model': model, 'reasoning_effort': config.get('effortLevel')}

    def prepare(self, args, target, info):
        original = json.loads(args.claude_config.expanduser().read_text())
        # Deliberately do not import hooks, skills, MCP, history or host permissions.
        env = {k: v for k, v in original.get('env', {}).items()
               if k in {'ANTHROPIC_BASE_URL', 'ANTHROPIC_API_KEY', 'ANTHROPIC_AUTH_TOKEN'}}
        config = {'env': env, 'model': info['model']}
        if info.get('reasoning_effort'):
            config['effortLevel'] = info['reasoning_effort']
        path = target/'settings.json'
        path.write_text(json.dumps(config)); path.chmod(0o600)
        mcp = target/'mcp.json'; mcp.write_text('{"mcpServers":{}}'); mcp.chmod(0o600)
        home = target/'home'; home.mkdir(mode=0o700)
        flags = ['-e', 'IS_SANDBOX=1', '-e', 'CLAUDE_CONFIG_DIR=/runner/claude-home',
                 '-v', f'{home}:/runner/claude-home:rw',
                 '-v', f'{path}:/runner/claude-settings.json:ro',
                 '-v', f'{mcp}:/runner/claude-mcp.json:ro']
        command = ['claude', '-p', '--verbose', '--output-format', 'stream-json',
                   '--settings', '/runner/claude-settings.json', '--setting-sources', '',
                   '--strict-mcp-config', '--mcp-config', '/runner/claude-mcp.json',
                   '--dangerously-skip-permissions', '--model', info['model']]
        return flags, command

    def configure_local_mcp(self, config_dir, name, command, environment, *,
                            startup_timeout_seconds=30, tool_timeout_seconds=180):
        if not command or min(startup_timeout_seconds, tool_timeout_seconds) <= 0:
            raise ValueError('MCP requires a command and positive timeouts')
        path = config_dir/'mcp.json'; config = json.loads(path.read_text())
        if name in config['mcpServers']:
            raise ValueError(f'MCP server already configured: {name}')
        config['mcpServers'][name] = {'type': 'stdio', 'command': command[0], 'args': command[1:], 'env': environment}
        path.write_text(json.dumps(config))
        settings = config_dir/'settings.json'; value = json.loads(settings.read_text())
        value['env'].update(MCP_TIMEOUT=str(startup_timeout_seconds*1000), MCP_TOOL_TIMEOUT=str(tool_timeout_seconds*1000))
        settings.write_text(json.dumps(value))

    def archive_sessions(self, config_dir, run):
        source = config_dir/'home/projects'
        if not source.exists():
            return None
        dest = run/'detail/claude_sessions'
        shutil.copytree(source, dest)
        return dest.relative_to(run).as_posix()

    def metrics(self, events, completed, source):
        results = [e for e in events if e.get('type') == 'result']
        last = results[-1] if results else {}
        raw = last.get('usage') or {}
        keys = ['input_tokens', 'output_tokens', 'cache_read_input_tokens', 'cache_creation_input_tokens']
        valid = all(type(raw.get(k)) is int and raw[k] >= 0 for k in keys)
        usage = None
        if valid:
            inputs = raw['input_tokens']+raw['cache_read_input_tokens']+raw['cache_creation_input_tokens']
            usage = {'input_tokens': inputs, 'output_tokens': raw['output_tokens'],
                     'total_tokens': inputs+raw['output_tokens'], 'cached_input_tokens': raw['cache_read_input_tokens'],
                     'cache_write_tokens': raw['cache_creation_input_tokens'], 'reasoning_tokens': None}
        # Some gateways emit generated content but report zero output usage.
        # Keep native counters for audit, without certifying them as complete.
        generated_content = any(
            e.get('type') == 'assistant' and e.get('message', {}).get('content')
            for e in events
        )
        suspicious_usage = generated_content and raw.get('output_tokens') == 0
        errors = [last.get('subtype', 'ClaudeError')] if last.get('is_error') else []
        if completed and not results:
            errors.append('MissingResultEvent')
        return {'token_usage': usage, 'token_usage_status': 'complete' if valid and completed and not errors and not suspicious_usage else 'partial' if raw else 'unavailable',
                'token_usage_basis': 'claude_inclusive_cache', 'token_usage_native': raw or None,
                'token_usage_source': source+':result.usage', 'reported_cost': last.get('total_cost_usd'),
                'agent_errors': errors, 'session_ids': [last['session_id']] if last.get('session_id') else []}
