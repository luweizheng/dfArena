"""Durable stage records and a rebuildable run summary."""
import json
from pathlib import Path

from runners.agents import get_agent
from runners.agents.codex import token_metrics  # compatibility export
from runners.agents.opencode import opencode_metrics  # compatibility export


def save(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + '.tmp')
    temp.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    temp.replace(path)


def read(path):
    return json.loads(path.read_text()) if path.exists() else None


def summarize(run):
    run = Path(run)
    gen = read(run / 'detail/generation.json')
    evaluation = read(run / 'detail/evaluation.json')
    result = {'schema_version': 1}
    if gen:
        for key in ('benchmark', 'dataset', 'task', 'mode', 'run_id', 'backend', 'agent'):
            result[key] = gen.get(key)
        result['generation'] = {key: gen.get(key) for key in
            ('status', 'returncode', 'started_at', 'finished_at', 'elapsed_seconds',
             'timing_scope', 'token_usage', 'token_usage_status')}
        for key in ('elapsed_seconds_excluding_simulator', 'timing_scope_excluding_simulator',
                    'token_usage_source','token_usage_basis','token_usage_steps','token_usage_native','reported_cost','agent_errors'):
            if key in gen:
                result['generation'][key] = gen[key]
        result['artifacts'] = gen.get('artifacts', {})
        if 'interaction' in gen:
            result['interaction'] = gen['interaction']
    else:
        result['generation'] = {'status': 'not_generated'}
    result['evaluation'] = ({key: evaluation.get(key) for key in
        ('status', 'passed', 'answer', 'started_at', 'finished_at', 'elapsed_seconds', 'timing_scope', 'error_types')}
        if evaluation else {'status': 'not_evaluated', 'passed': None,
                           'elapsed_seconds': None, 'error_types': []})
    result['reports'] = {'generation': 'detail/generation.json' if gen else None,
                         'evaluation': 'detail/evaluation.json' if evaluation else None}
    save(run / 'result.json', result)
    return result


def token_usage(path, completed, agent='codex'):
    events = []
    if path.exists():
        for line in path.read_text().splitlines():
            try:
                event = json.loads(line)
                if isinstance(event, dict):
                    events.append(event)
            except ValueError:
                pass
    return get_agent(agent).metrics(events, completed, source=f'logs/{path.name}')
