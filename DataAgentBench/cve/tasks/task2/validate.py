"""Accept either locally verified tied vendor for CVE task 2.

See DataAgentBench/curation/POSTRUN_REVIEW_20260926.md for the decision
and the unresolved limits of the source data.
"""

ACCEPTED_VENDORS = frozenset({"fortinet", "ivanti"})


def validate(llm_output: str):
    """Require one vendor name, allowing surrounding whitespace and case changes."""
    if not isinstance(llm_output, str):
        return False, "Expected a single vendor name as a string"
    vendor = llm_output.strip().lower()
    if vendor in ACCEPTED_VENDORS:
        return True, f"matched accepted vendor {vendor!r}"
    return False, "Expected one vendor name: 'fortinet' or 'ivanti'"
