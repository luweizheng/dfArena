import re

def validate(llm_output: str):
    """
    Validate LLM output for histology average expression task.

    Validation strategy:
    - For each ground truth histology code:
        - Check if it's present in LLM output.
        - Ignore Markdown emphasis and read complete numeric values starting
          within 10 characters after the code, without crossing another code.
        - Accept if any value matches the ground truth (rounded to 4 decimals).

    Returns:
        (True, "OK") if all matched
        (False, reason) if any mismatch
    """

    ground_truth = [
        ("9382/3", 2.713571305193452),
        ("9400/3", 2.6014163319762287),
        ("9401/3", 2.558390345072906),
        ("9450/3", 2.6967184429497295),
        ("9451/3", 2.5826348457075095),
    ]

    llm_output = re.sub(r"\*\*|__|`", "", llm_output)

    for hist_code, true_score in ground_truth:
        idx = llm_output.find(hist_code)
        if idx == -1:
            reason = f"Missing histology type: {hist_code}"
            return False, reason

        # Limit where a value may start, but never truncate the numeric token.
        start = idx + len(hist_code)
        window = re.split(r"\b\d{4}/\d\b", llm_output[start:], maxsplit=1)[0]
        number = r"(?<![\w.+-])[+-]?(?:\d+(?:\.\d+)?|\.\d+)(?:[eE][+-]?\d+)?(?![\w%]|\.\d)"
        matches = [m.group() for m in re.finditer(number, window) if m.start() < 10]
        gt_rounded = round(true_score, 4)

        for m in matches:
            try:
                val = float(m)
                if round(val, 4) == gt_rounded:
                    break
            except ValueError:
                continue
        else:
            reason = f"No matching score found near {hist_code} (expected ~{gt_rounded})"
            return False, reason

    return True, "All histology codes and scores matched successfully."
