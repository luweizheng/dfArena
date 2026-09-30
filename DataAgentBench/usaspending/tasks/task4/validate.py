# Canonical agency names from this dataset's agencies table. This is used only
# to distinguish bold agency answers from unrelated bold headings.
_AGENCY_NAMES = frozenset({
    'agency for international development',
    'consumer financial protection bureau',
    'council of the inspectors general on integrity and efficiency',
    'court services and offender supervision agency',
    'department of agriculture',
    'department of commerce',
    'department of defense',
    'department of education',
    'department of energy',
    'department of health and human services',
    'department of homeland security',
    'department of housing and urban development',
    'department of justice',
    'department of labor',
    'department of state',
    'department of the interior',
    'department of the treasury',
    'department of transportation',
    'department of veterans affairs',
    'district of columbia courts',
    'environmental protection agency',
    'equal employment opportunity commission',
    'export-import bank of the united states',
    'federal communications commission',
    'federal election commission',
    'federal mediation and conciliation service',
    'federal trade commission',
    'general services administration',
    'international trade commission',
    'millennium challenge corporation',
    'national aeronautics and space administration',
    'national archives and records administration',
    'national endowment for the humanities',
    'national gallery of art',
    'national labor relations board',
    'national science foundation',
    'national transportation safety board',
    'nuclear regulatory commission',
    'office of personnel management',
    'peace corps',
    'railroad retirement board',
    'securities and exchange commission',
    'small business administration',
    'social security administration',
    'u.s. agency for global media',
    'u.s. international development finance corporation',
    'united states trade and development agency',
})


def validate(llm_output: str):
    """Prefer declared answers; recognize only agency names as bold answers."""
    import re
    from pathlib import Path
    gt = Path(__file__).parent.joinpath("ground_truth.csv").read_text().strip().lower()
    text = llm_output.lower()
    # Ignore inline Markdown when parsing answer labels and their values.
    plain = text.replace("*", "").replace("`", "")
    patterns = [
        r"\banswer\s*(?:is|:)\s*[\"' ]*([a-z][a-z0-9 _'-]*?)(?:[\"'.\r\n;,!?]|$)",
        r"\bhighest[^.]*?is[: ]\s*[\"' ]*([a-z][a-z0-9 _'-]*?)(?:[\"'.\r\n;,!?]|$)",
        r"\bagency\s*(?:is|:)\s*[\"' ]*([a-z][a-z0-9 _'-]*?)(?:[\"'.\r\n;,!?]|$)",
    ]
    declared = []
    for pattern in patterns:
        for match in re.finditer(pattern, plain):
            declared.append((match.start(), match.group(1).strip().rstrip(".")))
    if declared:
        declared.sort()
        last = declared[-1][1]
        if gt in last:
            return True, f"matched declared answer {gt!r}"
        return False, f"expected {gt!r}, declared {last!r}"

    bold_agencies = [
        match.group(1).strip().rstrip(".:;!,?")
        for match in re.finditer(r"\*\*([^*\r\n]+)\*\*", text)
        if match.group(1).strip().rstrip(".:;!,?") in _AGENCY_NAMES
    ]
    if bold_agencies:
        last = bold_agencies[-1]
        if last == gt:
            return True, f"matched bold agency answer {gt!r}"
        return False, f"expected {gt!r}, declared {last!r}"
    if gt in text:
        return True, f"matched (fallback) {gt!r}"
    return False, f"expected {gt!r}"
