import re


def _norm(s: str) -> str:
    s = s.lower()
    s = s.replace("&", " and ")
    s = re.sub(r"[^a-z0-9\s]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def validate(llm_output: str):
    """All ground-truth categories present, normalizing '&' ↔ 'and' and punctuation."""
    categories = ["Restaurants", "Food", "American (New)", "Shopping", "Breakfast & Brunch"]
    llm_norm = _norm(llm_output)
    for cat in categories:
        if _norm(cat) not in llm_norm:
            return False, f"Missing category: {cat}"
    return True, "All categories are present."
