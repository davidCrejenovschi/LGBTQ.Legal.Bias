"""Step 3-4: query a model with the counterfactual prompts (experiment E1).

Examples:
    python scripts/02_run_e1.py --model ollama:llama3.1:latest
    python scripts/02_run_e1.py --model hf:Qwen/Qwen2.5-1.5B-Instruct
    python scripts/02_run_e1.py --model ollama:llama3.1:latest --pilot 10   # pilot experiment
    python scripts/02_run_e1.py --model anthropic:<model> --reps 3         # commercial APIs
"""
from __future__ import annotations

import argparse
import collections
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from legalbias.models import make_client  # noqa: E402
from legalbias.runner import load_jsonl, run  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--model", required=True)
ap.add_argument("--prompts", default="data/case_study/prompts.jsonl")
ap.add_argument("--outdir", default="results/case_study/e1_raw")
ap.add_argument("--reps", type=int, default=1)
ap.add_argument("--pilot", type=int, default=0,
                help="only N scenarios (all 12 variants each), written to *_pilot.jsonl")
ap.add_argument("--threads", type=int, default=0)
a = ap.parse_args()

prompts = load_jsonl(ROOT / a.prompts)
safe = re.sub(r"[^A-Za-z0-9._-]+", "_", a.model)
suffix = ""
if a.pilot:
    sids = []
    for task in ("REC", "PRE", "CRED"):
        task_sids = sorted({p["sid"] for p in prompts if p["task"] == task})
        sids += task_sids[:: max(1, len(task_sids) // max(1, a.pilot // 3))][: max(1, a.pilot // 3)]
    prompts = [p for p in prompts if p["sid"] in set(sids)]
    suffix = "_pilot"
out = ROOT / a.outdir / f"{safe}{suffix}.jsonl"

kw = {"threads": a.threads} if a.model.startswith("hf:") and a.threads else {}
client = make_client(a.model, **kw)
run(client, prompts, out, repetitions=a.reps)

recs = load_jsonl(out)
print("status counts:", dict(collections.Counter(r["status"] for r in recs)))
bad = [r for r in recs if r["status"] not in ("ok",)][:5]
for r in bad:
    print("  non-ok example:", r["vid"], json.dumps(r["raw"])[:160])
