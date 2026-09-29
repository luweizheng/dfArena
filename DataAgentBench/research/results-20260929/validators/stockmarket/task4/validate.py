import re
from common_scaffold.validate.levenshtein import levenshtein

def validate(llm_output: str):
    """
    Validate that:
    - Each GT name appears in LLM output (case-insensitive, exact or <=5 edits)
    - Use dynamic window length around GT name length for matching

    Returns:
        (True, "OK") if all pass
        (False, reason) if not
    """
    gt_names = [
        "MFA Financial, Inc",
        "Argo Group International Holdings, Ltd",
        "HDFC Bank Limited Common Stock",
        "Albany International Corporation Common Stock",
        "DTE Energy Company"
    ]

    llm_output_clean = re.sub(r'\s+', ' ', llm_output).strip().lower()

    _SUFFIX_RE = re.compile(
        r"\b(common\s+stock|preferred\s+stock|corporation|corp|company|co|"
        r"incorporated|inc|ltd|limited|plc|holdings|group|trust|the)\b\.?",
        re.I,
    )
    def _strip(s):
        s = _SUFFIX_RE.sub(" ", s)
        s = re.sub(r"[,\.]", " ", s)
        return re.sub(r"\s+", " ", s).strip()

    llm_stripped = _strip(llm_output_clean)

    for gt_name in gt_names:
        gt_name_clean = gt_name.lower()
        gt_len = len(gt_name_clean)

        # First: exact match
        if gt_name_clean in llm_output_clean:
            continue
        # Suffix-stripped exact match (e.g. "HDFC Bank Limited" matches
        # "HDFC Bank Limited Common Stock")
        gt_stripped = _strip(gt_name_clean)
        if gt_stripped and gt_stripped in llm_stripped:
            continue

        # Else: fuzzy match within a window
        min_distance = float('inf')
        best_match = ""
        window_range = 10  # allow ±10 chars around GT length

        for i in range(len(llm_output_clean) - gt_len + 1):
            for extra in range(-window_range, window_range + 1):
                start = i
                end = i + gt_len + extra
                if end > len(llm_output_clean) or end <= start:
                    continue
                candidate = llm_output_clean[start:end]

                # Remove digits to avoid interference
                candidate = re.sub(r'\b\d+([.,]\d+)?\b', '', candidate)
                candidate = re.sub(r'\s+', ' ', candidate).strip()
                if not candidate:
                    continue

                dist = levenshtein(gt_name_clean, candidate)
                if dist < min_distance:
                    min_distance = dist
                    best_match = candidate
                    if min_distance == 0:
                        break
            if min_distance == 0:
                break

        if min_distance <= 5:
            pass
        else:
            reason = (
                f"Name not found within 5 edits: '{gt_name}', "
                f"closest: '{best_match}' (distance={min_distance})"
            )
            return False, reason

    return True, "All names matched (exact or ≤5 edits)."