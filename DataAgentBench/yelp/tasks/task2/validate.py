import re


def validate(llm_output: str):
    """Anchor on the target numeric value; require 'PA' or 'Pennsylvania'
    within 150 chars on either side."""
    ground_truth_value = 3.699395770392749
    gt_rounded = round(ground_truth_value, 2)
    text = llm_output
    lower = text.lower()

    for m in re.finditer(r"\d+\.\d+", text):
        try:
            if round(float(m.group()), 2) != gt_rounded:
                continue
        except Exception:
            continue
        start = max(0, m.start() - 150)
        end = min(len(text), m.end() + 150)
        window = lower[start:end]
        if "pa" in re.findall(r"\b[a-z]+\b", window) or "pennsylvania" in window:
            return True, f"Found: value≈{gt_rounded} near PA/Pennsylvania"
    return False, f"No occurrence of {gt_rounded} near PA/Pennsylvania."
