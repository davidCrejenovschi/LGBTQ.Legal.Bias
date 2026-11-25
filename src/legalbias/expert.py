"""Expert review of the scenarios by a criminal-law practitioner (validation, section 1.5).

The expert sees only CONTROL variants (no mention of sexual orientation): the review is
about how the cases are built, not about bias. For every scenario the expert rates
    1. realism (1-5), 2. balance, i.e. how borderline the case is (1-5),
    3. whether the manipulated factor is legally relevant (da/nu),
    4. optionally, the decision the expert would take, on the scale given to the models.
The selected prompts exist in the case study, so the expert's decisions can be compared
with the models' decisions on exactly the same text.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from . import identities as ids
from . import scenarios as sc
from .prompts import instruction

TASK_ORDER = ("REC", "PRE", "CRED")
TASK_NAME_RO = {"REC": "riscul de recidivă", "PRE": "măsura preventivă",
                "CRED": "credibilitatea martorului"}
RATING_COLUMNS = ["item", "pid", "task", "realism_1_5", "balance_1_5", "factor_relevant_da_nu",
                  "expert_decision_optional", "comments"]


def _fill_pronouns(text: str, gender: str) -> str:
    p = ids.pronouns(gender)
    for key in sc.PRONOUN_KEYS:
        text = text.replace("{" + key + "}", p[key])
    return text


def select_for_review(per_task: int = 5, per_template: int = 4, seed: int = 2026) -> list[dict]:
    """Deterministic selection: per task, `per_task` templates spread evenly over the template
    list, one scenario each; the levels of the manipulated factor are cycled (0, 1, 2, 0, ...)
    and the control gender alternates (man, woman, ...). Uses the same generation settings as
    the case study, so every selected prompt also exists in data/case_study/prompts.jsonl."""
    items: list[dict] = []
    for task in TASK_ORDER:
        spec = sc.load_templates(task)
        levels = spec["shared_slots"][spec["manip_slot"]]
        scen = sc.generate_scenarios(task, per_template, seed=seed)
        tids = [t["id"] for t in spec["templates"]]
        idx = sorted(set(np.linspace(0, len(tids) - 1, per_task).round().astype(int)))
        for j, i in enumerate(idx):
            level = j % len(levels)
            cands = [s for s in scen if s.template_id == tids[i] and s.manip_level == level]
            if not cands:
                cands = [s for s in scen if s.template_id == tids[i]]
            s = cands[0]
            vid = "M_ctrl" if len(items) % 2 == 0 else "F_ctrl"
            gender = ids.BY_ID[vid].gender
            items.append({
                "item": len(items) + 1, "pid": f"{s.sid}__{vid}", "sid": s.sid, "task": task,
                "template_id": s.template_id, "vid": vid, "manip_level": s.manip_level,
                "factor": _fill_pronouns(levels[s.manip_level]["text"], gender),
                "scenario": sc.render(s, vid), "question": instruction(task),
            })
    return items


def ratings_template(items: list[dict]) -> pd.DataFrame:
    df = pd.DataFrame([{"item": it["item"], "pid": it["pid"], "task": it["task"]} for it in items])
    for col in RATING_COLUMNS[3:]:
        df[col] = ""
    return df[RATING_COLUMNS]


def _yes(value) -> float:
    if pd.isna(value) or str(value).strip() == "":
        return np.nan
    return 1.0 if str(value).strip().lower() in {"da", "yes", "y", "1", "true"} else 0.0


def summarize_ratings(ratings: pd.DataFrame, answers: pd.DataFrame | None = None):
    """Returns (per_task, comparison). per_task: number of rated scenarios, mean realism,
    mean balance and share of factors judged relevant. comparison (if model answers are
    given): mean absolute difference between the expert's decision and each model's decision
    on the same prompt."""
    r = ratings.copy()
    for col in ("realism_1_5", "balance_1_5", "expert_decision_optional"):
        r[col] = pd.to_numeric(r[col], errors="coerce")
    r["factor_relevant"] = r["factor_relevant_da_nu"].map(_yes)
    per_task = r.groupby("task").agg(
        n=("pid", "count"), realism_mean=("realism_1_5", "mean"),
        balance_mean=("balance_1_5", "mean"), factor_relevant_share=("factor_relevant", "mean"),
        n_decisions=("expert_decision_optional", "count")).reset_index()
    comparison = None
    if answers is not None:
        a = answers[answers["status"].isin(("ok", "ok_lenient"))][["pid", "model", "value"]]
        m = r.dropna(subset=["expert_decision_optional"]).merge(a, on="pid")
        if not m.empty:
            m["abs_diff"] = (m["expert_decision_optional"] - m["value"]).abs()
            comparison = m.groupby(["model", "task"]).agg(
                n=("pid", "count"), mean_abs_diff=("abs_diff", "mean"),
                expert_mean=("expert_decision_optional", "mean"),
                model_mean=("value", "mean")).reset_index()
    return per_task, comparison
