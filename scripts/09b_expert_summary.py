"""Summarize the expert's ratings once they come back.

Copy the answers from the form into data/expert_review/ratings.csv (same columns as
ratings_template.csv), then run
    python scripts/09b_expert_summary.py
Output: results/expert_review/per_task.csv and, if the expert gave decisions,
results/expert_review/comparison_with_models.csv
"""
from __future__ import annotations

import pathlib
import sys

import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from legalbias import expert  # noqa: E402
from legalbias.runner import load_jsonl  # noqa: E402

ratings_path = ROOT / "data" / "expert_review" / "ratings.csv"
if not ratings_path.exists():
    sys.exit(f"No ratings yet: fill in {ratings_path.relative_to(ROOT)} first.")
ratings = pd.read_csv(ratings_path)
answers = pd.concat([pd.DataFrame(load_jsonl(p)) for p in
                     sorted((ROOT / "results" / "case_study" / "e1_raw").glob("*.jsonl"))
                     if not p.stem.endswith("_pilot")], ignore_index=True)
per_task, comparison = expert.summarize_ratings(ratings, answers)
out = ROOT / "results" / "expert_review"
out.mkdir(parents=True, exist_ok=True)
per_task.to_csv(out / "per_task.csv", index=False)
print(per_task.round(2).to_string(index=False))
if comparison is not None:
    comparison.to_csv(out / "comparison_with_models.csv", index=False)
    print(comparison.round(2).to_string(index=False))
