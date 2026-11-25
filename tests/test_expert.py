import json
import pathlib

import pandas as pd
import pytest

from legalbias import expert

ROOT = pathlib.Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def items():
    return expert.select_for_review()


def test_fifteen_control_scenarios_five_per_task(items):
    assert len(items) == 15
    assert pd.Series([i["task"] for i in items]).value_counts().to_dict() == {"REC": 5, "PRE": 5, "CRED": 5}
    assert all(i["vid"] in ("M_ctrl", "F_ctrl") for i in items)
    assert len({i["pid"] for i in items}) == 15
    assert expert.select_for_review() == items                      # deterministic


def test_no_orientation_is_shown_to_the_expert(items):
    words = ("gay", "lesbian", "bisexual", "heterosexual", "husband", "wife")
    for i in items:
        assert not any(w in i["scenario"].lower().split() for w in words)


def test_selection_covers_templates_and_factor_levels(items):
    for task in ("REC", "PRE", "CRED"):
        sel = [i for i in items if i["task"] == task]
        assert len({i["template_id"] for i in sel}) == 5
        assert {i["manip_level"] for i in sel} == {0, 1, 2}
    cred = [i["template_id"][:6] for i in items if i["task"] == "CRED"]
    assert any(t <= "CRED05" for t in cred) and any(t >= "CRED06" for t in cred)


def test_factor_text_appears_in_the_scenario(items):
    for i in items:
        assert i["factor"] in i["scenario"]


def test_selected_prompts_exist_in_the_case_study(items):
    pids = {json.loads(line)["pid"] for line in
            open(ROOT / "data" / "case_study" / "prompts.jsonl", encoding="utf-8")}
    assert {i["pid"] for i in items} <= pids


def test_summarize_ratings_and_comparison():
    ratings = pd.DataFrame({
        "item": [1, 2, 3], "pid": ["a", "b", "c"], "task": ["REC", "REC", "CRED"],
        "realism_1_5": [4, 5, 3], "balance_1_5": [3, 4, ""],
        "factor_relevant_da_nu": ["da", "Nu", "DA"],
        "expert_decision_optional": [6, "", 7], "comments": ["", "", ""],
    })
    per_task, _ = expert.summarize_ratings(ratings)
    rec = per_task.set_index("task").loc["REC"]
    assert rec["realism_mean"] == 4.5 and rec["balance_mean"] == 3.5
    assert rec["factor_relevant_share"] == 0.5 and rec["n_decisions"] == 1
    answers = pd.DataFrame({"pid": ["a", "c", "c"], "model": ["m1", "m1", "m2"],
                            "value": [4, 7, 9], "status": ["ok", "ok", "ok"]})
    _, comp = expert.summarize_ratings(ratings, answers)
    comp = comp.set_index(["model", "task"])
    assert comp.loc[("m1", "REC"), "mean_abs_diff"] == 2
    assert comp.loc[("m1", "CRED"), "mean_abs_diff"] == 0
    assert comp.loc[("m2", "CRED"), "mean_abs_diff"] == 2


def test_ratings_template_has_one_row_per_item(items):
    t = expert.ratings_template(items)
    assert list(t.columns) == expert.RATING_COLUMNS and len(t) == 15
