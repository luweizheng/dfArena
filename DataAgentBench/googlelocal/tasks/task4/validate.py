import re

ground_truth = [
    ("Encino Dermatology & Laser", 19),
    ("The Boochyard @ Local Roots", 17),
    ("Aurora Massage", 14),
]


def _norm(s: str) -> str:
    s = s.lower()
    s = s.replace("&", " and ").replace("@", " at ")
    s = re.sub(r"[^a-z0-9\s]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def validate(llm_output: str):
    """Each (name, expected_num) pair: name present (normalized); the expected
    number appears within ±150 chars of the name's position."""
    llm = llm_output
    llm_n = _norm(llm)
    for name, expected in ground_truth:
        name_n = _norm(name)
        idx = llm_n.find(name_n)
        if idx == -1:
            return False, f"Missing business name: {name}"
        # anchor on the most distinctive token (longest alphabetic word)
        tokens = [t for t in re.findall(r"[A-Za-z]{4,}", name) if t.lower() not in
                  {"the", "and", "inc", "ltd", "llc", "corp"}]
        anchor = max(tokens, key=len) if tokens else name.split()[0]
        m = re.search(re.escape(anchor), llm, re.I)
        pos = m.start() if m else 0
        lo = max(0, pos - 150)
        hi = min(len(llm), pos + len(name) + 150)
        window = llm[lo:hi]
        nums = re.findall(r"\d+", window)
        if not any(int(n) == expected for n in nums if n.isdigit()):
            return False, f"Number {expected} not found near {name}"
    return True, "All names and numbers matched."
