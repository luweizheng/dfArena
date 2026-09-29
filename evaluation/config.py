"""Validate the PrepBench-compatible, per-file evaluation contract."""
import json
import re
from decimal import Decimal, InvalidOperation
from pathlib import Path


class ConfigError(ValueError):
    pass


TYPES = {'number', 'integer', 'text_exact', 'text_norm', 'boolean', 'date', 'datetime'}
DEFAULT_DATE_FORMATS = ['%Y-%m-%d']
DEFAULT_DATETIME_FORMATS = [
    '%Y-%m-%d %H:%M:%S', '%Y-%m-%dT%H:%M:%S',
    '%Y-%m-%d %H:%M:%S.%f', '%Y-%m-%dT%H:%M:%S.%f',
]


def column_rule(value):
    legacy = isinstance(value, str)
    rule = {'type': value} if legacy else value
    if not isinstance(rule, dict) or not isinstance(rule.get('type'), str) or rule['type'] not in TYPES:
        raise ConfigError(f'Unknown column rule: {value!r}')
    rule = dict(rule)
    kind = rule['type']
    allowed = {'type', 'null_values'}
    if kind == 'number':
        allowed |= {'abs_tol', 'rel_tol'}
    if kind in {'date', 'datetime'}:
        allowed.add('formats')
    if set(rule) - allowed:
        raise ConfigError(f'Unsupported column options: {sorted(set(rule) - allowed)}')
    if 'null_values' in rule and (not isinstance(rule['null_values'], list) or
                                 not all(isinstance(x, str) for x in rule['null_values'])):
        raise ConfigError('null_values must be an explicit list of strings')
    if 'formats' in rule and (not isinstance(rule['formats'], list) or not rule['formats'] or
                             not all(isinstance(x, str) and x for x in rule['formats'])):
        raise ConfigError('formats must be a nonempty list of strptime formats')
    if kind in {'date', 'datetime'} and not legacy:
        rule.setdefault('formats', list(DEFAULT_DATE_FORMATS if kind == 'date' else DEFAULT_DATETIME_FORMATS))
        for fmt in rule['formats']:
            directives = re.findall(r'%(.)', fmt)
            if any(d not in 'YymdbBjaAwUWGVuHIMSfp%' for d in directives) or fmt.endswith('%'):
                raise ConfigError('Unsupported date/time directive (including timezones)')
            if kind == 'date' and any(d in 'HIMSfp' for d in directives):
                raise ConfigError('date formats cannot contain time components')
            if re.search(r'Z|UTC|GMT|[+-]\d{2}:?\d{2}', fmt):
                raise ConfigError('Timezone literals are not supported')
    if kind == 'number' and not legacy:
        for name in ('abs_tol', 'rel_tol'):
            v = rule.get(name, 0)
            if isinstance(v, bool) or not isinstance(v, (int, float)):
                raise ConfigError(f'{name} must be a finite nonnegative JSON number')
            try:
                d = Decimal(str(v))
                if not d.is_finite() or d < 0:
                    raise ConfigError(f'{name} must be finite and nonnegative')
            except InvalidOperation as exc:
                raise ConfigError(f'Invalid {name}') from exc
            rule[name] = d
    rule['legacy'] = legacy
    return rule


def load_config(path):
    try:
        raw = json.loads(Path(path).read_text(encoding='utf-8'))
    except (OSError, ValueError) as exc:
        raise ConfigError(str(exc)) from exc
    if not isinstance(raw, dict) or set(raw) != {'files'}:
        raise ConfigError('Config must contain only a files object')
    if not isinstance(raw['files'], dict) or not raw['files']:
        raise ConfigError('files must be a nonempty object')
    result = {}
    for name, spec in raw['files'].items():
        if not name or '/' in name or '\\' in name or not name.lower().endswith('.csv'):
            raise ConfigError(f'Expected a plain CSV filename: {name!r}')
        if not isinstance(spec, dict) or set(spec) - {'columns', 'key', 'ignore_order', 'order_by'}:
            raise ConfigError(f'Invalid file options for {name}')
        cols = spec.get('columns')
        if not isinstance(cols, dict) or not cols or not all(isinstance(c, str) and c for c in cols):
            raise ConfigError(f'{name}: columns must be a nonempty object')
        cols = {c: column_rule(v) for c, v in cols.items()}
        key = spec.get('key')
        if (not isinstance(key, list) or not key or not all(isinstance(c, str) and c in cols for c in key)
                or len(set(key)) != len(key)):
            raise ConfigError(f'{name}: key must contain distinct declared columns')
        ignore = spec.get('ignore_order', True)
        if type(ignore) is not bool:
            raise ConfigError(f'{name}: ignore_order must be a boolean')
        order = spec.get('order_by', [])
        if not isinstance(order, list) or (not ignore and not order):
            raise ConfigError(f'{name}: ignore_order=false requires nonempty order_by')
        if ignore and order:
            raise ConfigError(f'{name}: order_by requires ignore_order=false')
        seen = set()
        for item in order:
            if (not isinstance(item, dict) or set(item) != {'column', 'direction', 'nulls'} or
                    not isinstance(item['column'], str) or item['column'] not in cols or
                    item['column'] in seen or item['direction'] not in ('asc', 'desc') or
                    item['nulls'] not in ('first', 'last')):
                raise ConfigError(f'{name}: order_by requires distinct declared columns, direction asc/desc, nulls first/last')
            seen.add(item['column'])
        result[name] = {'columns': cols, 'key': key, 'ignore_order': ignore, 'order_by': order}
    return {'files': result}
