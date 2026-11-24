"""Validation on a public benchmark: CrowS-Pairs, sexual-orientation subset.

    python scripts/download_assets.py --crows
    python scripts/08_crows_pairs.py --model Qwen/Qwen2.5-1.5B-Instruct

Outputs results/crows_pairs/<model>_scores.csv and <model>_summary.json.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys

import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from legalbias import crows_pairs as cp  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--model", default="Qwen/Qwen2.5-1.5B-Instruct")
ap.add_argument("--outdir", default="results/crows_pairs")
a = ap.parse_args()

pairs = cp.load()
print(f"CrowS-Pairs sexual-orientation pairs: {len(pairs)} "
      f"({pairs['stereo_antistereo'].value_counts().to_dict()})")
scorer = cp.LogLikelihoodScorer(a.model)
rows = []
for r in pairs.itertuples():
    ll_more, n_more = scorer.score(r.sent_more)
    ll_less, n_less = scorer.score(r.sent_less)
    rows.append({"sent_more": r.sent_more, "sent_less": r.sent_less,
                 "stereo_antistereo": r.stereo_antistereo, "ll_more": ll_more, "n_more": n_more,
                 "ll_less": ll_less, "n_less": n_less})
scores = pd.DataFrame(rows)
summary = {"model": a.model, **cp.summarize(scores)}
out = ROOT / a.outdir
out.mkdir(parents=True, exist_ok=True)
tag = a.model.split("/")[-1]
scores.to_csv(out / f"{tag}_scores.csv", index=False)
(out / f"{tag}_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
print(json.dumps(summary, indent=2))
