"""Prepare the real-data validation: COMPAS records -> counterfactual prompts.

    python scripts/download_assets.py --compas
    python scripts/04_compas_prompts.py --n 60
    python scripts/02_run_e1.py --model ollama:llama3.1:latest \
        --prompts data/compas/prompts.jsonl --outdir results/compas/e1_raw
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from legalbias import compas  # noqa: E402
from legalbias import scenarios as sc  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--n", type=int, default=60)
ap.add_argument("--seed", type=int, default=2026)
ap.add_argument("--out", default="data/compas/prompts.jsonl")
a = ap.parse_args()

df = compas.load()
print(f"COMPAS after ProPublica filters: {len(df)} records "
      f"(recidivism rate {df['two_year_recid'].mean():.3f})")
sub = compas.sample(df, a.n, a.seed)
scen = compas.to_scenarios(sub)
problems = [p for s in scen for p in sc.check_invariance(s)]
if problems:
    sys.exit("invariance violations: " + "; ".join(problems[:5]))
rows = []
for s in scen:
    rows += sc.expand([s], compas.variants_for(s))
out = ROOT / a.out
out.parent.mkdir(parents=True, exist_ok=True)
with open(out, "w", encoding="utf-8") as f:
    for r in rows:
        f.write(json.dumps(r, ensure_ascii=False) + "\n")
print(f"{len(scen)} records x 6 variants = {len(rows)} prompts -> {out}")
print("example:", rows[1]["scenario"])
