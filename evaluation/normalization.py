"""Raw CSV scalar normalization for the dfArena table evaluation protocol."""
from datetime import datetime
from decimal import Decimal, InvalidOperation, localcontext
import math
import re
from .config import DEFAULT_DATE_FORMATS, DEFAULT_DATETIME_FORMATS, DEFAULT_TIME_FORMATS

EMPTY = {'', 'none', 'nan', 'null', 'n/a', 'na'}
DATE_FORMATS = ['%Y-%m-%d', '%Y/%m/%d', '%d/%m/%Y']
DATETIME_FORMATS = ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M', '%Y/%m/%d %H:%M:%S', '%d/%m/%Y %H:%M:%S']
TRUE = {'true', '1', 'yes', 'y', 't', '是'}
FALSE = {'false', '0', 'no', 'n', 'f', '否'}


def normalize(raw, rule):
    kind, legacy = rule['type'], rule['legacy']
    # Explicit exact labels only; the configured type still validates the target.
    raw = rule.get('aliases', {}).get(raw, raw)
    s = raw.strip()
    if legacy and kind in {'text_exact', 'text_norm'}:
        if len(s) >= 2 and s[0] == s[-1] and s[0] in {'"', "'"}:
            s = s[1:-1]
    if legacy:
        tokens = {'', 'na', 'n/a', 'null'} if kind in {'date', 'datetime'} else EMPTY
        # New types have no broad legacy null-token aliasing.
        if kind in {'integer', 'time'}:
            tokens = {''}
        # Quote removal can expose whitespace; trim only for null detection.
        if s.strip().lower() in tokens:
            return None
    else:
        tokens = rule.get('null_values', [''])
        if kind in {'date', 'datetime', 'time'}:
            if s.lower() in {token.strip().lower() for token in tokens}:
                return None
        elif raw in tokens:
            return None
    if kind in {'text_exact', 'text_norm'}:
        if kind == 'text_norm':
            return re.sub(r'\s+', ' ', s.strip().lower())
        return s if legacy else raw
    if kind == 'boolean':
        if s.lower() in TRUE:
            return True
        if s.lower() in FALSE:
            return False
        raise ValueError('Unrecognized boolean')
    if kind in {'number', 'integer'}:
        if legacy and kind == 'number':
            s = re.sub(r'[,$%]\s*', '', s.lower())
            try:
                value = float(s)
            except ValueError as exc:
                raise ValueError('Invalid number') from exc
            if not math.isfinite(value):
                raise ValueError('Non-finite number')
            return value
        if not re.fullmatch(r'[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?', s):
            raise ValueError('Invalid numeric representation')
        try:
            value = Decimal(s)
        except InvalidOperation as exc:
            raise ValueError('Invalid number') from exc
        if not value.is_finite():
            raise ValueError('Non-finite number')
        if kind == 'integer' and value != value.to_integral_value():
            raise ValueError('Expected an integer')
        return value
    formats = rule.get('formats')
    if formats is None:
        if kind == 'time':
            formats = DEFAULT_TIME_FORMATS
        elif legacy:
            formats = DATE_FORMATS if kind == 'date' else DATETIME_FORMATS
        else:
            formats = DEFAULT_DATE_FORMATS if kind == 'date' else DEFAULT_DATETIME_FORMATS
    if kind == 'datetime':
        # Task formats extend ISO formats; try all to detect ambiguous values.
        formats = list(dict.fromkeys(DEFAULT_DATETIME_FORMATS + formats))
    if legacy and '/' in s:
        parts = s.split('/')
        if len(parts) == 3 and len(parts[2]) == 3 and parts[2].isdigit():
            s = '/'.join([parts[0], parts[1], '0' + parts[2]])
    parsed = set()
    if kind == 'date':
        # ISO dates are always accepted, independently of task-specific formats.
        # Only an exactly zero time suffix is representation-equivalent to a date.
        iso = re.fullmatch(r'(\d{4}-\d{2}-\d{2})(?:[ T]00:00:00(?:\.0+)?)?', s)
        if iso:
            try:
                parsed.add(datetime.strptime(iso[1], '%Y-%m-%d').date())
            except ValueError:
                pass
    for fmt in formats:
        try:
            value = datetime.strptime(s, fmt)
            if value.tzinfo is not None:
                raise ValueError('Timezone-aware dates are not supported in this protocol')
            parsed.add(value.time() if kind == 'time' else value.date() if kind == 'date' else value)
        except ValueError:
            continue
    if len(parsed) != 1:
        raise ValueError('Invalid or ambiguous date/datetime/time for configured formats')
    return parsed.pop()


def equal(a, b, rule):
    if a is None or b is None:
        return a is b
    if rule['type'] != 'number':
        return a == b
    if rule['legacy']:
        if a == b == 0:
            return True
        if a == 0 or b == 0:
            return abs(a - b) < 0.02
        return abs(a - b) / max(abs(a), abs(b)) < 0.02
    # Avoid loss of integer/decimal precision in exact comparisons.
    if a == b:
        return True
    absolute, relative = rule['abs_tol'], rule['rel_tol']
    if absolute == relative == 0:
        return False
    vals = (a, b, absolute, relative)
    precision = max(50, sum(len(v.as_tuple().digits) for v in vals) +
                    max(v.adjusted() for v in vals) - min(v.adjusted() for v in vals) + 10)
    with localcontext() as ctx:
        ctx.prec = precision
        return abs(a - b) <= max(absolute, relative * abs(a))
