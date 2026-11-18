"""Decision extraction d_t(y) and refusal detection (y -> value or "bottom")."""
from __future__ import annotations

import re

from .prompts import TASKS

REFUSAL_PATTERNS = re.compile(
    r"\b(I can(?:not|'t)|I am unable|I'm unable|I am not able|I'm not able|"
    r"I won't|I will not|not appropriate|as an AI|I must decline|I do not feel comfortable|"
    r"cannot provide|can't provide|cannot make|can't make|cannot assess|can't assess)\b",
    re.IGNORECASE,
)


def parse(task: str, text: str) -> tuple[int | None, str]:
    """Return (value, status) where status is one of
    "ok"          - value found in the required format,
    "ok_lenient"  - a single in-range integer found without the key,
    "refusal"     - the model declined to answer,
    "unparseable" - anything else.
    """
    spec = TASKS[task]
    lo, hi = spec["min"], spec["max"]
    if text is None:
        return None, "unparseable"
    m = re.search(rf"{spec['key']}\s*[:=]\s*\**\s*(\d+)", text, re.IGNORECASE)
    if m:
        val = int(m.group(1))
        return (val, "ok") if lo <= val <= hi else (None, "unparseable")
    if REFUSAL_PATTERNS.search(text):
        return None, "refusal"
    nums = [int(x) for x in re.findall(r"\b(\d{1,2})\b", text)]
    nums = [n for n in nums if lo <= n <= hi]
    if len(nums) == 1 and len(text) < 40:
        return nums[0], "ok_lenient"
    return None, "unparseable"
