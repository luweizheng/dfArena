"""Validate an empty funding-source selection without treating exclusions as selections."""
import re

GROUND_TRUTH = []
FUNDING_SOURCES = [
    'Public-Private Partnership', 'Municipal Fund', 'Municipal Bond',
    'Emergency Relief Fund', 'Private Donation', 'County Grant',
    'State Grant', 'Federal Grant',
]


def _norm(s):
    s = s.lower().replace('_', ' ')
    return re.sub(r'\s+', ' ', re.sub(r'[^a-z0-9\s]', ' ', s)).strip()


_SOURCE_BY_NAME = {_norm(s): s for s in FUNDING_SOURCES}
_EMPTY_PATTERNS = [
    r'empty',
    r'none(?: qualify)?',
    r'no(?: qualifying| eligible)?(?: funding)? sources?(?: qualify| qualifies)?',
    r'(?:there (?:are|were) )?no (?:qualifying|eligible)(?: funding)? sources?',
    r'no (?:funding )?sources? (?:meet|meets|satisfy|satisfies) (?:the |all )?(?:criteria|criterion|requirements|threshold)',
    # _norm converts percent signs and hyphens to spaces; match the full assertion.
    r'no (?:funding )?sources? (?:meet|meets|satisfy|satisfies) (?:the )?25(?: percent)? (?:completed projects? )?(?:threshold|cutoff)',
    r'none of the (?:funding )?sources? (?:qualify|meet the criteria)',
    r'(?:an? )?empty (?:set|list|result)',
    r'(?:the )?(?:set|list|result) is empty',
    r'zero (?:qualifying|eligible)(?: funding)? sources?',
    r'all (?:funding )?sources? (?:are below|fall below) (?:the )?25(?: percent)? (?:threshold|cutoff)',
]
_NEGATIVE = re.compile(
    r'^(?P<names>.+?)\s+(?:(?:does|do)\s+not\s+(?:qualify|meet\s+(?:the\s+)?(?:criteria|threshold))'
    r'|(?:is|are)\s+(?:excluded|ineligible|not\s+(?:eligible|included|qualifying)))'
    r'(?:\s+(?:because|since|as)\s+(?P<reason>.+))?$', re.I)
_PREFIX = re.compile(r'^(?:in particular|specifically|for example)\s*,\s*', re.I)
_ANSWER_PREFIX = re.compile(r'^(?:the\s+)?(?:final\s+)?(?:answer|result)\s*(?:is\s+|:\s*)', re.I)
_DATE_PREFIX = re.compile(r'^as of\s+\d{4}-\d{2}-\d{2}\s*[:,]?\s*', re.I)
_DATE_SUFFIX = re.compile(r'\s+as of\s+\d{4}-\d{2}-\d{2}\s*$', re.I)
_EXCLUDE_PREFIX = re.compile(r'^(?:excluded|ineligible|non[- ]qualifying)(?:\s+funding)?\s+sources?\s*:\s*', re.I)


def _is_empty(text):
    compact = re.sub(r'\s+', '', text)
    if compact in ('[]', '{}', '∅', 'set()'):
        return True
    normalized = _norm(text)
    return any(re.fullmatch(p, normalized) for p in _EMPTY_PATTERNS)


def _source_list(text):
    """Only an explicit list of known source names counts as an exclusion."""
    items = re.split(r',|\band\b|&', text, flags=re.I)
    selected = set()
    for item in items:
        name = _norm(item)
        if not name or name not in _SOURCE_BY_NAME:
            return None
        selected.add(_SOURCE_BY_NAME[name])
    return selected


def validate(llm_output: str):
    if not isinstance(llm_output, str) or not llm_output.strip():
        return False, 'An explicit empty result is required; blank output is not an answer.'
    text = llm_output.strip()
    if text.startswith('```'):
        text = re.sub(r'^```(?:json|text|markdown|python)?\s*\n?', '', text, flags=re.I)
        text = re.sub(r'\s*```$', '', text)
    text = re.sub(r'\*\*|`', '', text)
    empty_stated, excluded, problems = False, set(), []
    exclusion_section = False
    clauses = re.split(r'\n+|;|\.(?=\s|$)|\s*\b(?:but|however|whereas)\b\s*', text, flags=re.I)
    for clause in clauses:
        clause = clause.strip().rstrip(',').strip()
        clause = re.sub(r'^(?:[-+\u2022]\s+|\d+[.)]\s+)', '', clause)
        if not clause or re.fullmatch(r'[|:\s-]+', clause):
            continue
        # An empty one-column table is another list presentation.
        if clause.startswith('|') and clause.endswith('|') and clause.count('|') == 2:
            clause = clause.strip('|').strip()
        if _norm(clause) in ('funding source', 'funding sources', 'source', 'sources'):
            continue
        clause = _PREFIX.sub('', clause)
        clause = _DATE_PREFIX.sub('', clause)
        clause = _DATE_SUFFIX.sub('', clause)
        clause = _ANSWER_PREFIX.sub('', clause)
        if _is_empty(clause):
            empty_stated = True
            exclusion_section = False
            continue
        match = _EXCLUDE_PREFIX.match(clause)
        if match:
            body = clause[match.end():]
            if not body:
                exclusion_section = True
                continue
            names = _source_list(body)
            if names is None:
                problems.append('Could not parse excluded source list: ' + clause)
            else:
                excluded.update(names)
            continue
        match = _NEGATIVE.fullmatch(clause)
        if match:
            names = _source_list(match.group('names'))
            reason = match.group('reason') or ''
            # Do not swallow a second selection assertion inside an explanation.
            additional_assertion = re.search(r'\b(?:qualif(?:y|ies)|eligible|include|selected|but|however)\b', reason, re.I)
            additional_source = any(n in _norm(reason) for n in _SOURCE_BY_NAME)
            if names is None or additional_assertion or additional_source:
                problems.append('Could not unambiguously parse exclusion: ' + clause)
            else:
                excluded.update(names)
            continue
        if exclusion_section:
            names = _source_list(clause)
            if names is not None:
                excluded.update(names)
                continue
        problems.append('Non-empty selection or unrecognized answer text: ' + clause)
    if problems:
        return False, '; '.join(problems)
    if empty_stated or excluded == set(FUNDING_SOURCES):
        return True, 'Correctly reports an empty selection; explicit exclusions are not selected sources.'
    return False, 'The answer does not establish that no funding sources qualify.'
