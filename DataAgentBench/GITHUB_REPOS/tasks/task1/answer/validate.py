"""Accept equivalent decimal, percentage, and fraction representations."""
import re


_NUMBER = r"[+-]?(?:\d+(?:\.\d+)?|\.\d+)"
_VALUE = re.compile(
    rf"(?<![\w.])(?P<numerator>{_NUMBER})"
    rf"(?:(?P<percent>\s*(?:%|percent\b))|\s*/\s*(?P<denominator>{_NUMBER}))?"
    r"(?!\w|\.\d)",
    re.IGNORECASE,
)


def validate(llm_output: str):
    # Preserve the original criterion: the proportion rounds to 0.33.
    # Normalize an explicit unit before comparing, so 0.33% is not read as 0.33.
    for match in _VALUE.finditer(llm_output):
        value = float(match['numerator'])
        if match['percent']:
            value /= 100
        elif match['denominator'] is not None:
            denominator = float(match['denominator'])
            if denominator == 0:
                continue
            value /= denominator
        if 0 <= value <= 1 and round(value, 2) == 0.33:
            return True, f"Found matching proportion: {value} -> ~0.33"
    return False, "No proportion in LLM output rounds to 0.33"
