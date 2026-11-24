"""Stability of the decisions: compare two independent runs of the same prompts.

Run A is the primary E1 run (results/case_study/e1_raw); run B is a replication
written to results/case_study/stability/e1_raw by

    python scripts/02_run_e1.py --model ollama:llama3.1:latest --outdir results/case_study/stability/e1_raw

Outputs (results/case_study/stability/):
    stability.csv    agreement / noise flip rate per task
    replication.csv  E1 per variant in both runs; replicated = same sign and Holm p < 0.05 in both
    e1_run_b.csv     full E1 table of run B
"""
from __future__ import annotations

import pathlib
import sys

import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from legalbias import metrics  # noqa: E402
from legalbias.runner import load_jsonl  # noqa: E402

CS = ROOT / "results" / "case_study"
OUT = CS / "stability"

frames_b = [pd.DataFrame(load_jsonl(p)) for p in sorted((OUT / "e1_raw").glob("*.jsonl"))]
if not frames_b:
    sys.exit("No replication run found in results/case_study/stability/e1_raw")
run_b = pd.concat(frames_b, ignore_index=True)
models = set(run_b["model"])
run_a = pd.concat([pd.DataFrame(load_jsonl(p)) for p in sorted((CS / "e1_raw").glob("*.jsonl"))
                   if not p.stem.endswith("_pilot")], ignore_index=True)
run_a = run_a[run_a["model"].isin(models)]

stab = metrics.stability_table(run_a, run_b)
e1_a = metrics.e1_table(run_a)
e1_b = metrics.e1_table(run_b)
rep = metrics.replication_table(e1_a, e1_b)

stab.to_csv(OUT / "stability.csv", index=False)
rep.to_csv(OUT / "replication.csv", index=False)
e1_b.to_csv(OUT / "e1_run_b.csv", index=False)

pd.set_option("display.width", 200)
print(stab.round(3).to_string(index=False))
cfr = e1_a.groupby(["model", "task"])["CFR"].agg(["min", "max"]).round(2)
print("\nCFR range across LGBTQ+ variants in run A:\n" + cfr.to_string())
print("\n" + rep[["task", "vid", "MSD_a", "MSD_b", "p_wilcoxon_holm_a", "p_wilcoxon_holm_b",
                  "same_sign", "replicated"]].round(3).to_string(index=False))
