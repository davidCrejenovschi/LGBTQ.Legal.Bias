"""Robustness of the credibility effects to the wording of the task instruction.

Wording 0 is the original instruction (main run); wordings 1 and 2 come from
prompts.PARAPHRASES and are run with

    python scripts/02_run_e1.py --model ollama:llama3.1:latest --task CRED --paraphrase 1 \
        --outdir results/case_study/paraphrase_1/e1_raw
    (same with --paraphrase 2 and paraphrase_2)

All wordings are analysed in the same way: CRED only, Holm correction over the 6 CRED tests.
Rule fixed before the runs: the effect for gay and lesbian witnesses is called robust only if,
for every wording, MSD < 0 (more favourable) and the Holm-adjusted p < 0.05.

Output: results/case_study/paraphrase/robustness.csv and manipulation.csv
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
MODEL = "ollama/llama3.1:latest"
FOCUS = ("M_gay_exp", "F_les_exp")


def load(folder: pathlib.Path) -> pd.DataFrame:
    frames = [pd.DataFrame(load_jsonl(p)) for p in sorted(folder.glob("*.jsonl"))
              if not p.stem.endswith("_pilot")]
    df = pd.concat(frames, ignore_index=True)
    return df[(df["model"] == MODEL) & (df["task"] == "CRED")]


runs = {0: load(CS / "e1_raw")}
for k in (1, 2):
    folder = CS / f"paraphrase_{k}" / "e1_raw"
    if folder.exists():
        runs[k] = load(folder)

# compare the same scenarios under every wording: the paraphrase runs cover the original
# 20 CRED scenarios, while the main run was later extended with new templates
if len(runs) > 1:
    common = set.intersection(*(set(df["pid"]) for k, df in runs.items() if k > 0))
    runs[0] = runs[0][runs[0]["pid"].isin(common)]

rows, manip = [], []
for k, df in runs.items():
    e1 = metrics.e1_table(df)                     # Holm over the 6 CRED tests of this wording
    e1.insert(0, "wording", k)
    rows.append(e1)
    m = metrics.manipulation_check(df)
    m.insert(0, "wording", k)
    m["mean_control"] = df[df["mode"] == "control"]["value"].mean()
    m["valid_rate"] = df["status"].isin(metrics.OK_STATUSES).mean()
    manip.append(m)

res = pd.concat(rows, ignore_index=True)
man = pd.concat(manip, ignore_index=True)
out = CS / "paraphrase"
out.mkdir(parents=True, exist_ok=True)
res.to_csv(out / "robustness.csv", index=False)
man.to_csv(out / "manipulation.csv", index=False)

focus = res[res["vid"].isin(FOCUS)]
robust = bool(((focus["MSD"] < 0) & (focus["p_wilcoxon_holm"] < 0.05)).all()) and len(runs) == 3
pd.set_option("display.width", 200)
print(res[["wording", "vid", "n_pairs", "CFR", "MSD", "MSD_lo", "MSD_hi", "p_wilcoxon",
           "p_wilcoxon_holm"]].round(3).to_string(index=False))
print(man[["wording", "n", "rho", "p", "mean_by_level", "mean_control", "valid_rate"]].round(3)
      .to_string(index=False))
print(f"\nRobust (gay and lesbian, all {len(runs)} wordings, MSD < 0 and Holm p < 0.05): {robust}")
