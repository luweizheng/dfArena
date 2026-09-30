import re


def _normalize_title(s: str) -> str:
    s = s.lower()
    s = re.sub(r"\([^)]*\)", "", s)
    s = re.sub(r"[^a-z0-9\s]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def validate(llm_output: str):
    """Check every ground-truth title appears in the LLM output after
    normalization (strip parenthesized tags, lowercase, collapse whitespace)."""
    ground_truth_books = [
        "The Sludge",
        "Something That Feels Like Truth (Switchgrass Books)",
        "Kennebago Moments",
        "Hollywood Confessions: Hollywood Headlines Book #3 (Hollywood Headlines Mysteries)",
        "Forged in Blood (Freehold)",
        "Local Honey",
        "Exits, Desires, & Slow Fires",
        "Fire Cracker",
        "Reunion: The Children of Lauderdale Park",
        "Childe Harold of Dysna",
        "The Prophet: With Original 1923 Illustrations by the Author",
        "Knowing When To Die: Uncollected Stories",
        "Liza of Lambeth",
        "Child Of The King A Journey of Hope Book 1: Earthly Story With A Heavenly Message",
        "The Melancholy Strumpet Master",
    ]
    llm_norm = _normalize_title(llm_output)
    for book in ground_truth_books:
        if _normalize_title(book) not in llm_norm:
            return False, f"Missing book title in LLM output: {book}"
    return True, "All book titles found in LLM output."
