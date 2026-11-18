"""Step 1-2: templates -> scenarios -> 12 counterfactual variants -> prompts.

Case study (date initiale): 5 templates x 4 fillings = 20 scenarios per task,
60 scenarios x 12 variants = 720 prompts per model.
Full study: --per-template 7..8  (~100 scenarios per task, 3,600 prompts).
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from legalbias import scenarios as sc  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--per-template", type=int, default=4)
ap.add_argument("--seed", type=int, default=2026)
ap.add_argument("--out", default="data/case_study/prompts.jsonl")
a = ap.parse_args()

all_rows, problems = [], []
for task in ("REC", "PRE", "CRED"):
    scen = sc.generate_scenarios(task, a.per_template, seed=a.seed)
    for s in scen:
        problems += sc.check_invariance(s)
    rows = sc.expand(scen)
    all_rows += rows
    print(f"{task}: {len(scen)} scenarios -> {len(rows)} prompts")

if problems:
    print("INVARIANCE VIOLATIONS:")
    print("\n".join(problems[:20]))
    sys.exit(1)
print("Invariance check: OK (variants differ only in identity-marking words)")

out = ROOT / a.out
out.parent.mkdir(parents=True, exist_ok=True)
with open(out, "w", encoding="utf-8") as f:
    for r in all_rows:
        f.write(json.dumps(r, ensure_ascii=False) + "\n")
print(f"{len(all_rows)} prompts -> {out}")
