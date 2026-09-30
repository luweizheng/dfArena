"""
Levenshtein edit distance — shared utility for fuzzy validation.

Used by validators that need approximate string matching (e.g., matching
ETF names, repo names, histology codes with minor formatting differences).
"""


def levenshtein(s1: str, s2: str) -> int:
    """
    Compute Levenshtein edit distance between two strings.

    Uses iterative dynamic programming (O(n*m) time, O(m) space).
    """
    if len(s1) < len(s2):
        return levenshtein(s2, s1)

    if len(s2) == 0:
        return len(s1)

    previous_row = list(range(len(s2) + 1))
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]
