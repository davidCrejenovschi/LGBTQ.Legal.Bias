import pytest

from legalbias.parsing import parse


@pytest.mark.parametrize("task,text,expected", [
    ("REC", "SCORE: 7", (7, "ok")),
    ("REC", "**SCORE:** 3", (3, "ok")),
    ("REC", "score = 10", (10, "ok")),
    ("REC", "SCORE: 11", (None, "unparseable")),
    ("PRE", "MEASURE: 4", (4, "ok")),
    ("PRE", "MEASURE: 6", (None, "unparseable")),
    ("CRED", "8", (8, "ok_lenient")),
    ("REC", "I cannot provide a risk assessment based on this information.", (None, "refusal")),
    ("PRE", "The appropriate measure depends on many factors 2 3", (None, "unparseable")),
    ("REC", None, (None, "unparseable")),
])
def test_parse(task, text, expected):
    assert parse(task, text) == expected
