"""Validate the PrepBench-compatible, per-file evaluation contract."""
import json
import re
from decimal import Decimal, InvalidOperation
from pathlib import Path


class ConfigError(ValueError):
    pass


TYPES = {'number', 'integer', 'text_exact', 'text_norm', 'boolean', 'date', 'datetime', 'time'}
DEFAULT_TIME_FORMATS = ['%H:%M', '%H:%M:%S', '%H:%M:%S.%f']
DEFAULT_DATE_FORMATS = ['%Y-%m-%d']
DEFAULT_DATETIME_FORMATS = [
    '%Y-%m-%d %H:%M', '%Y-%m-%dT%H:%M',
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
    if kind in {'integer', 'text_exact'}:
        allowed.add('aliases')
    if kind == 'number':
        allowed |= {'abs_tol', 'rel_tol'}
    if kind in {'date', 'datetime', 'time'}:
        allowed.add('formats')
    if kind == 'datetime':
        allowed.add('assume_timezone')
    if 'assume_timezone' in rule and rule['assume_timezone'] != 'UTC':
        raise ConfigError('assume_timezone supports only explicit UTC')
    if set(rule) - allowed:
        raise ConfigError(f'Unsupported column options: {sorted(set(rule) - allowed)}')
    if 'null_values' in rule and (not isinstance(rule['null_values'], list) or
                                 not all(isinstance(x, str) for x in rule['null_values'])):
        raise ConfigError('null_values must be an explicit list of strings')
    if 'aliases' in rule:
        aliases = rule['aliases']
        if not isinstance(aliases, dict) or not aliases:
            raise ConfigError('aliases must be a nonempty string-to-string object')
        for label, target in aliases.items():
            if (not isinstance(label, str) or not label.strip()
                    or label in rule.get('null_values', [''])
                    or not isinstance(target, str) or not target.strip()
                    or target in rule.get('null_values', [''])):
                raise ConfigError('Aliases require nonempty, non-null string labels and targets')
            if kind == 'integer':
                if not re.fullmatch(r'[+-]?[0-9]+', target):
                    raise ConfigError('Integer aliases require integer-string targets')
                try:
                    Decimal(label.strip())
                except InvalidOperation:
                    pass
                else:
                    raise ConfigError('Integer aliases cannot remap numeric representations')
            elif target in aliases:
                raise ConfigError('Text aliases must point directly to canonical text, without chains or cycles')
    if 'formats' in rule and (not isinstance(rule['formats'], list) or not rule['formats'] or
                             not all(isinstance(x, str) and x for x in rule['formats'])):
        raise ConfigError('formats must be a nonempty list of strptime formats')
    if kind in {'date', 'datetime', 'time'} and (not legacy or kind == 'time'):
        rule.setdefault('formats', list(DEFAULT_TIME_FORMATS if kind == 'time' else DEFAULT_DATE_FORMATS if kind == 'date' else DEFAULT_DATETIME_FORMATS))
        for fmt in rule['formats']:
            directives = re.findall(r'%(.)', fmt)
            if any(d not in 'YymdbBjaAwUWGVuHIMSfp%' for d in directives) or fmt.endswith('%'):
                raise ConfigError('Unsupported date/time directive (including timezones)')
            if kind == 'time' and any(d not in 'HIMSfp%' for d in directives):
                raise ConfigError('time formats cannot contain date components')
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
        if not isinstance(spec, dict) or set(spec) - {'columns', 'key', 'ignore_order', 'order_by', 'order_mode', 'alternative_gt', 'csv_quoting'}:
            raise ConfigError(f'Invalid file options for {name}')
        quoting = spec.get('csv_quoting', 'standard')
        if quoting not in ('standard', 'standard_or_backslash'):
            raise ConfigError(f'{name}: unsupported csv_quoting')
        alternatives = spec.get('alternative_gt', {})
        if not isinstance(alternatives, dict):
            raise ConfigError(f'{name}: alternative_gt must map labels to relative CSV paths')
        for label, relative in alternatives.items():
            if (not isinstance(label, str) or not re.fullmatch(r'[A-Za-z0-9_-]+', label)
                    or label == 'primary' or not isinstance(relative, str)
                    or not relative or '\\' in relative or ':' in relative
                    or relative.startswith('/') or not relative.lower().endswith('.csv')
                    or any(p in {'', '.', '..'} for p in relative.split('/'))):
                raise ConfigError(f'{name}: invalid alternative_gt label or relative CSV path')
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
        mode = spec.get('order_mode', 'fields')
        if mode not in ('fields', 'gt_position'):
            raise ConfigError(f'{name}: unknown order_mode')
        if mode == 'gt_position' and (ignore or order or alternatives):
            raise ConfigError(f'{name}: gt_position requires ignore_order=false and no order_by or alternative_gt')
        if not isinstance(order, list) or (not ignore and not order and mode == 'fields'):
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
        if quoting != 'standard':
            result[name]['csv_quoting'] = quoting
        if mode == 'gt_position':
            result[name]['order_mode'] = mode
        if alternatives:
            result[name]['alternative_gt'] = dict(alternatives)
    return {'files': result}
