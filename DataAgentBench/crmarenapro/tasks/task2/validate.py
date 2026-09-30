"""Temporary multi-policy acceptance for the unresolved CRM task 2 case.

See DataAgentBench/curation/POSTRUN_REVIEW_20260926.md for the review decision.
"""
import re


ACCEPTED_ARTICLE_IDS = frozenset({
    "ka0Wt000000Eq0MIAS",  # Volume-Based Discounts
    "ka0Wt000000Ens5IAC",  # Mandatory Bundles for Quotes
})
# Capture whole ID-like tokens, including malformed ones, rather than accepting
# a valid ID embedded in a longer token. Matching remains case-sensitive below.
ARTICLE_TOKEN = re.compile(r"(?<!\w)ka0\w*(?!\w)", re.IGNORECASE)


def validate(llm_output: str):
    """Accept either permitted article or both, but no other article ID."""
    if not isinstance(llm_output, str):
        return False, "Expected an answer string containing knowledge article IDs"

    found_ids = set(ARTICLE_TOKEN.findall(llm_output.strip()))
    if not found_ids:
        return False, "No accepted knowledge article ID found in LLM output"
    unexpected = found_ids - ACCEPTED_ARTICLE_IDS
    if unexpected:
        return False, f"Unexpected or malformed knowledge article IDs: {sorted(unexpected)}"
    return True, f"Found accepted knowledge article IDs: {sorted(found_ids)}"
