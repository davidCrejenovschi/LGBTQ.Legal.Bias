"""Generalization of the credibility results to new scenario templates.

The credibility task was extended from 5 to 10 templates after the first results had been
seen. So that the extension is not judged only by the pooled result, the 20 scenarios built
from the 5 new templates (CRED06-CRED10) are also analysed on their own, as an
out-of-sample check of the effect found on the original templates (CRED01-CRED05).

Rule fixed before the new runs: the credibility effect for gay and lesbian witnesses
generalizes to new scenarios if, for Llama-3.1-8B on the new templates, both have MSD < 0 and
a Holm-adjusted p < 0.05 (Holm over the 6 CRED tests of the subset). Qwen is reported
descriptively.

    python scripts/05d_new_templates.py
Output: results/case_study/new_templates/generalization.csv and manipulation.csv
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
SUBSETS = {
    "original": [f"CRED0{i}" for i in range(1, 6)],
    "new": [f"CRED0{i}" for i in range(6, 10)] + ["CRED10"],
}
FOCUS = ("M_gay_exp", "F_les_exp")
LLAMA = "ollama/llama3.1:latest"

df = pd.concat([pd.DataFrame(load_jsonl(p)) for p in sorted((CS / "e1_raw").glob("*.jsonl"))
                if not p.stem.endswith("_pilot")], ignore_index=True)
df = df[df["task"] == "CRED"]
df["template_short"] = df["template_id"].str.split("_").str[0]

rows, manip = [], []
for name, prefixes in SUBSETS.items():
    sub = df[df["template_short"].isin(prefixes)]
    if sub.empty:
        continue
    e1 = metrics.e1_table(sub)                       # Holm over the 6 CRED tests, per model
    e1.insert(0, "templates", name)
    rows.append(e1)
    m = metrics.manipulation_check(sub)
    m.insert(0, "templates", name)
    manip.append(m)

res = pd.concat(rows, ignore_index=True)
man = pd.concat(manip, ignore_index=True)
out = CS / "new_templates"
out.mkdir(parents=True, exist_ok=True)
res.to_csv(out / "generalization.csv", index=False)
man.to_csv(out / "manipulation.csv", index=False)

pd.set_option("display.width", 200)
print(res[["templates", "model", "vid", "n_pairs", "CFR", "MSD", "MSD_lo", "MSD_hi", "p_wilcoxon",
           "p_wilcoxon_holm"]].round(3).to_string(index=False))
print(man[["templates", "model", "n", "rho", "p", "mean_by_level"]].round(3).to_string(index=False))
focus = res[(res["templates"] == "new") & (res["model"] == LLAMA) & res["vid"].isin(FOCUS)]
if len(focus) == len(FOCUS):
    verdict = bool(((focus["MSD"] < 0) & (focus["p_wilcoxon_holm"] < 0.05)).all())
    print(f"\nGeneralizes to new templates (Llama, gay and lesbian, MSD < 0 and Holm p < 0.05): {verdict}")
else:
    print("\nNew templates not run yet for Llama.")
