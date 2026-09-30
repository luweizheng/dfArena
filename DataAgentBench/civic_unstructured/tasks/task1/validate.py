import re
import json

# Ground truth = canonical (entity-resolved) project names.
GROUND_TRUTH = [
    "Annual Street Maintenance",
    "Civic Center Water Treatment Facility Phase 2",
    "Marie Canyon Green Streets",
    "Michael Landon Center Roof Replacement Project",
    "PCH Median Improvements Project",
    "PCH Signal Synchronization System Improvements Project",
    "PCH at Trancas Canyon Road Right Turn Lane",
    "Permanent Skate Park",
    "Westward Beach Road Repair Project",
]

# Entity resolution, listed explicitly here (NOT loaded from the ground-truth
# dataset): canonical project name -> every surface-name variant that refers to
# the same project. The answer is entity-resolved against this map, so naming a
# project by ANY of its variants counts as naming the canonical project.
ER = {
    "Annual Street Maintenance": [
        "Annual Street Maintenance",
        "2021 Annual Street Maintenance",
        "2022 Annual Street Maintenance",
    ],
    "Civic Center Water Treatment Facility Phase 2": [
        "Civic Center Water Treatment Facility Phase 2",
    ],
    "Marie Canyon Green Streets": [
        "Marie Canyon Green Streets",
    ],
    "Michael Landon Center Roof Replacement Project": [
        "Michael Landon Center Roof Replacement Project",
        "Malibu Bluffs Park Roof Replacement Project",
    ],
    "PCH Median Improvements Project": [
        "PCH Median Improvements Project",
    ],
    "PCH Signal Synchronization System Improvements Project": [
        "PCH Signal Synchronization System Improvements Project",
    ],
    "PCH at Trancas Canyon Road Right Turn Lane": [
        "PCH at Trancas Canyon Road Right Turn Lane",
    ],
    "Permanent Skate Park": [
        "Permanent Skate Park",
    ],
    "Westward Beach Road Repair Project": [
        "Westward Beach Road Repair Project",
        "Westward Beach Road Improvements Project",
    ],
}


def _norm(s):
    """Lowercase, underscores→spaces, strip non-alphanumeric, collapse whitespace."""
    s = s.lower().replace('_', ' ')
    s = re.sub(r'[^a-z0-9\s]', ' ', s)
    return re.sub(r'\s+', ' ', s).strip()


# Parse a concise final list, not arbitrary mentions anywhere in the answer.
# Unsupported prose is reported explicitly instead of silently discarded.
_HEADINGS = {
    'project', 'projects', 'project name', 'project names', 'name', 'no',
    'number', 'rank', 'funding', 'total funding', 'accumulated funding',
    'accumulated total funding', 'total funding usd', 'funding usd',
    'amount', 'amount usd', 'status', 'type', 'project type', 'latest status',
    'capital', 'design', 'usd', 'qualifying projects', 'eligible projects',
    'the following projects qualify', 'the following projects meet the criteria',
    'these projects meet all the criteria', 'all listed projects meet the criteria',
    'there are no other qualifying projects', 'no other projects qualify',
}
_INTRO = re.compile(
    r'^(?:(?:the\s+)?(?:qualifying|eligible|selected)\s+projects'
    r'(?:\s+are)?|(?:the\s+)?projects\s+(?:are|that\s+qualify\s+are)'
    r'|the\s+following\s+projects\s+(?:qualify|meet\s+the\s+criteria)'
    r'|(?:final\s+)?answer)\s*[:\-]?\s*', re.I)
_EXCLUDED = re.compile(
    r'^(?:excluded(?:\s+projects)?|(?:non[- ]qualifying|ineligible)'
    r'\s+projects|projects\s+(?:excluded|not\s+included))\s*:\s*', re.I)
_NEGATIVE = re.compile(
    r'^(?P<names>.+?)\s+(?:(?:does|do)\s+not\s+(?:qualify|meet\s+(?:the\s+)?criteria)'
    r'|(?:is|are)\s+(?:excluded|ineligible|not\s+(?:included|eligible|qualifying)))'
    r'(?:\s+(?:because|since|as)\s+.+)?[.!]?$', re.I)
_POSITIVE = re.compile(
    r'\s+(?:(?:is|are)\s+(?:eligible|included)|qualif(?:y|ies)'
    r'|meets?\s+(?:all\s+)?(?:the\s+)?criteria)[.!]?$', re.I)
_MONEY = re.compile(
    r'^(?:(?:total|accumulated)\s+)?(?:funding|amount)?\s*[:=]?\s*'
    r'(?:(?:USD\s*)?\$?\s*\d+(?:\.\d+)?\s*'
    r'(?:(?:million|thousand|billion|[kmb])\s*)?(?:USD|dollars)?)[.!]?$', re.I)
_ASSERTION_IN_NAMES = re.compile(
    r'\b(?:qualif(?:y|ies)|does|do|is|are|include|included|exclude|excluded|selected)\b', re.I)


def _is_annotation(s):
    s = s.strip(' \t():\u2014\u2013-')
    return not s or _norm(s) in _HEADINGS or bool(_MONEY.fullmatch(s))


def _replace_names(text):
    # Longest aliases first, with word boundaries: "Permanent Skate Park
    # Extension" must not be accepted as just "Permanent Skate Park".
    variants = [(alias, canonical) for canonical, aliases in ER.items() for alias in aliases]
    for alias, canonical in sorted(variants, key=lambda x: len(x[0]), reverse=True):
        pattern = r'(?<!\w)' + r'[\W_]+'.join(map(re.escape, _norm(alias).split())) + r'(?!\w)'
        token = f'@P{GROUND_TRUTH.index(canonical)}@'
        text = re.sub(pattern, lambda _: token, text, flags=re.I)
    return text


def _parse_names(text):
    selected, unknown = set(), []
    text = _replace_names(text)
    # Commas in amounts are not list separators.
    text = re.sub(r'(?<=\d),(?=\d{3}(?:\D|$))', '', text)
    text = re.sub(r'\(([^()]*)\)',
                  lambda m: '' if _is_annotation(m.group(1)) else m.group(0), text)
    for item in re.split(r'[,;|]|\s+(?:and|&)\s+', text, flags=re.I):
        item = item.strip()
        item = re.sub(r'^\s*(?:[-+\u2022]\s+|\d+[.)]\s+)', '', item)
        if _is_annotation(item):
            continue
        tokens = re.findall(r'@P(\d+)@', item)
        remainder = re.sub(r'@P\d+@', '', item).strip(' \t.:\u2014\u2013-')
        if tokens and _is_annotation(remainder):
            selected.update(GROUND_TRUTH[int(i)] for i in tokens)
        else:
            # Keep unknown identities, including text attached to a known name.
            display = re.sub(r'@P(\d+)@', lambda m: GROUND_TRUTH[int(m.group(1))], item)
            unknown.append(display)
    return selected, unknown


def validate(llm_output: str):
    if not isinstance(llm_output, str) or not llm_output.strip():
        return False, 'Missing project list.'
    text = llm_output.strip()
    if text.startswith('```'):
        text = re.sub(r'^```(?:json|text|markdown)?\s*\n?', '', text, flags=re.I)
        text = re.sub(r'\s*```$', '', text)
    if text.startswith('['):
        try:
            values = json.loads(text)
        except (ValueError, TypeError):
            return False, 'Could not parse the JSON project list.'
        if not isinstance(values, list) or not all(isinstance(v, str) for v in values):
            return False, 'Expected a list of project-name strings.'
        text = '\n'.join(values)
    text = text.replace('_', ' ')
    text = re.sub(r'\*\*|__|`', '', text)
    selected, excluded, unknown = set(), set(), []
    exclusion_section = False
    # Decimal points remain intact. Contrast clauses get separate polarity.
    clauses = re.split(r'\n+|;|\.(?=\s|$)|\s*\b(?:but|however|whereas)\b\s*', text, flags=re.I)
    for clause in clauses:
        clause = clause.strip().strip('*').strip().rstrip(',').strip()
        clause = re.sub(r'^\s*(?:[-+\u2022]\s+|\d+[.)]\s+)', '', clause)
        if not clause or re.fullmatch(r'[|:\s-]+', clause):
            continue
        negative = _EXCLUDED.match(clause)
        if negative:
            body = clause[negative.end():]
            if not body:
                exclusion_section = True
                continue
            if _ASSERTION_IN_NAMES.search(body):
                unknown.append('Unrecognized exclusion clause: ' + clause)
                continue
            names, errors = _parse_names(body)
            excluded.update(names)
            # Named extras in an explicit exclusion are not selected.
            continue
        intro = _INTRO.match(clause)
        if intro:
            exclusion_section = False
            clause = clause[intro.end():]
            if not clause:
                continue
        negative = _NEGATIVE.fullmatch(clause)
        if negative:
            subject = negative.group('names')
            if _ASSERTION_IN_NAMES.search(subject):
                unknown.append('Unrecognized mixed assertion: ' + clause)
                continue
            names, errors = _parse_names(subject)
            excluded.update(names)
            continue
        if exclusion_section:
            if _ASSERTION_IN_NAMES.search(clause):
                unknown.append('Unrecognized assertion in exclusion section: ' + clause)
                continue
            names, errors = _parse_names(clause)
            excluded.update(names)
            continue
        if _norm(clause) in _HEADINGS:
            continue
        clause = _POSITIVE.sub('', clause)
        names, errors = _parse_names(clause)
        selected.update(names)
        unknown.extend(errors)
    missing = sorted(set(GROUND_TRUTH) - selected)
    conflicting = sorted(selected & excluded)
    reasons = []
    if missing:
        reasons.append(f'Missing project(s): {missing}')
    if unknown:
        reasons.append(f'Extra project(s) or unrecognized answer text: {sorted(set(unknown))}')
    if conflicting:
        reasons.append(f'Conflicting inclusion/exclusion for project(s): {conflicting}')
    if reasons:
        return False, '; '.join(reasons)
    return True, 'The selected project set exactly matches the expected set (aliases resolved).'


