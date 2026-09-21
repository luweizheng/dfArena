"""Agent registry and shared entry points used by both benchmarks.

Add an AgentAdapter implementation and register it in AGENTS to add an agent.
Provider-specific behavior belongs in that adapter, not in this module.
"""
from pathlib import Path
import re

from .base import AgentAdapter
from .codex import CodexAgent
from .opencode import OpenCodeAgent

AGENTS: dict[str, AgentAdapter] = {
    adapter.name: adapter for adapter in (CodexAgent(), OpenCodeAgent())
}


def get_agent(name: str) -> AgentAdapter:
    try:
        return AGENTS[name]
    except KeyError:
        raise ValueError(f'Unsupported coding agent: {name}') from None


def add_agent_options(parser):
    parser.add_argument('--agent', choices=list(AGENTS), default='codex')
    for adapter in AGENTS.values():
        adapter.add_options(parser)


def add_model_options(parser):
    """Register model selection and optional output-label arguments."""
    parser.add_argument('--model', help='Actual model override; otherwise use agent configuration')
    parser.add_argument('--agent-model', help='Optional output directory label; does not select the agent or model')


def validate_label(label):
    if not re.fullmatch(r'[A-Za-z0-9_-][A-Za-z0-9_.-]*', label):
        raise ValueError('--agent-model must be a directory label')


def settings(args):
    return get_agent(args.agent).settings(args)


def label_for(args, info):
    model = get_agent(args.agent).model_label(info['model'] or 'default')
    label = args.agent_model or (args.agent+'_'+model)
    label = re.sub(r'[^A-Za-z0-9_.-]+', '-', label).strip('.-')
    if not label:
        raise ValueError('Agent-model label must contain a valid directory name')
    return label


def prepare_agent(args, target, info):
    return get_agent(args.agent).prepare(args, target, info)


def archive_sessions(agent, config_dir, run):
    return get_agent(agent).archive_sessions(config_dir, run)


def forwarded_options(args):
    return ['--agent', args.agent, *get_agent(args.agent).forwarded_options(args)]


def agent_log_paths(run_dir):
    """Shared log locations for new runs; native event schemas remain unchanged."""
    logs = Path(run_dir) / 'logs'
    return {'events': logs / 'agent_events.jsonl', 'stderr': logs / 'agent_stderr.log'}
