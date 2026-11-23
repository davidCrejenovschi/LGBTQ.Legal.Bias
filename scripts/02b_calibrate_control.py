"""Calibrate a task's scenarios on the CONTROL variants only.

Scenario wording may be tuned until the decisions have room to vary, but this must
not depend on the identity effects. The script therefore queries only the variants
with no mention of orientation and checks criteria fixed in advance:

    * mean decision between 2.5 and 3.5 (PRE scale 1-5)
    * custodial decisions (>= 4) in 20-60% of the answers
    * no single scale value in more than 60% of the answers
    * decisions become more severe with the legal risk factor (Spearman rho > 0)

    python scripts/02b_calibrate_control.py --task PRE --model ollama:llama3.1:latest
"""
from __future__ import annotations

import argparse
import collections
import pathlib
import re
import sys

from scipy.stats import spearmanr

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from legalbias import scenarios as sc  # noqa: E402
from legalbias.models import make_client  # noqa: E402
from legalbias.prompts import TASKS  # noqa: E402
from legalbias.runner import load_jsonl, run  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--task", default="PRE")
ap.add_argument("--model", required=True)
ap.add_argument("--per-template", type=int, default=4)
ap.add_argument("--seed", type=int, default=2026)
ap.add_argument("--outdir", default="results/case_study/calibration")
a = ap.parse_args()

scen = sc.generate_scenarios(a.task, a.per_template, seed=a.seed)
prompts = sc.expand(scen, ["M_ctrl", "F_ctrl"])
safe = re.sub(r"[^A-Za-z0-9._-]+", "_", a.model)
out = ROOT / a.outdir / f"{a.task}_{safe}.jsonl"
out.unlink(missing_ok=True)      # a calibration run always reflects the current templates
run(make_client(a.model), prompts, out)

rows = [r for r in load_jsonl(out) if r["value"] is not None]
values = [r["value"] for r in rows]
n = len(values)
counts = collections.Counter(values)
mean = sum(values) / n
threshold = TASKS[a.task].get("custodial_threshold", 4)
custodial = sum(v >= threshold for v in values) / n
top_share = max(counts.values()) / n
rho = spearmanr([r["manip_level"] for r in rows], values).statistic
by_level = {k: round(sum(r["value"] for r in rows if r["manip_level"] == k) /
                     sum(r["manip_level"] == k for r in rows), 2)
            for k in sorted({r["manip_level"] for r in rows})}
checks = {"mean in [2.5, 3.5]": 2.5 <= mean <= 3.5,
          "custodial in [20%, 60%]": 0.2 <= custodial <= 0.6,
          "top value <= 60%": top_share <= 0.6,
          "rho > 0": rho > 0}
print(f"{a.model}: n={n}/{len(prompts)} distribution={sorted(counts.items())}")
print(f"  mean={mean:.2f} custodial={custodial:.0%} top_share={top_share:.0%} "
      f"rho={rho:.2f} mean_by_level={by_level}")
for name, ok in checks.items():
    print(f"  {'PASS' if ok else 'FAIL'}  {name}")
