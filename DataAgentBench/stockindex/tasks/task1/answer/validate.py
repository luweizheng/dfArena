def validate(llm_output: str):
    """Check the target ticker is present in the first 200 chars of the output
    (so it's stated as THE answer, not just mentioned in a comparison list)."""
    gt = "399001.SZ"
    head = llm_output[:200].lower()
    if gt.lower() not in head:
        return False, f"Target '{gt}' not stated as primary answer (not in first 200 chars)."
    return True, f"Target '{gt}' present as primary answer."
