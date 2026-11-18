"""Steps 5 and 9: analysis of E1 (decisions), E3 (link representations <->
decisions) and of the COMPAS pilot; writes CSV tables and figures.

    python scripts/05_analyze.py
"""
from __future__ import annotations

import json
import pathlib
import sys

import numpy as np
import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from legalbias import compas, metrics, stats  # noqa: E402
from legalbias import identities as ids  # noqa: E402
from legalbias.runner import load_jsonl  # noqa: E402

CS = ROOT / "results" / "case_study"
CP = ROOT / "results" / "compas"
MODEL_LABEL = {"ollama/llama3.1:latest": "Llama-3.1-8B-Instruct (Q4)",
               "hf/Qwen2.5-1.5B-Instruct": "Qwen2.5-1.5B-Instruct"}
E2_REP = "standardized"   # primary representation pipeline (see chapter 1.6)


def load_runs(folder: pathlib.Path) -> pd.DataFrame:
    frames = [pd.DataFrame(load_jsonl(p)) for p in sorted(folder.glob("*.jsonl"))
              if not p.stem.endswith("_pilot")]
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()


def status_table(df: pd.DataFrame) -> pd.DataFrame:
    t = df.groupby(["model", "task"])["status"].value_counts().unstack(fill_value=0)
    t["n"] = t.sum(axis=1)
    t["valid_rate"] = (t.get("ok", 0) + t.get("ok_lenient", 0)) / t["n"]
    t["median_latency_s"] = df.groupby(["model", "task"])["latency_s"].median()
    return t.reset_index()


# --------------------------------------------------------------------- E1
def analyze_case_study() -> dict:
    df = load_runs(CS / "e1_raw")
    out = {}
    status_table(df).to_csv(CS / "e1_status.csv", index=False)
    e1 = metrics.e1_table(df, versus="ref")
    e1.to_csv(CS / "e1_vs_reference.csv", index=False)
    metrics.e1_table(df, versus="control").to_csv(CS / "e1_vs_control.csv", index=False)
    metrics.h1b_table(df).to_csv(CS / "e1_h1b.csv", index=False)
    mc = metrics.manipulation_check(df)
    mc.to_csv(CS / "e1_manipulation_check.csv", index=False)
    # determinism check: pilot answers vs. full-run answers for the same prompts
    det = []
    for p in sorted((CS / "e1_raw").glob("*_pilot.jsonl")):
        pilot = pd.DataFrame(load_jsonl(p)).set_index("pid")["value"]
        full = df[df["model"] == pd.DataFrame(load_jsonl(p))["model"].iloc[0]].set_index("pid")["value"]
        common = pilot.index.intersection(full.index)
        det.append({"model": p.stem, "n": len(common),
                    "identical": float((pilot[common] == full[common]).mean())})
    pd.DataFrame(det).to_csv(CS / "e1_determinism.csv", index=False)
    out["df"], out["e1"], out["mc"] = df, e1, mc
    return out


# --------------------------------------------------------------------- E3
def analyze_e3(e1: pd.DataFrame) -> pd.DataFrame:
    e2 = pd.read_csv(CS / "e2_seat_Qwen2.5-1.5B-Instruct.csv")
    e2 = e2[e2["rep"] == E2_REP]
    dbar = e2.groupby(["vid", "concept"])["d"].mean().unstack()
    q = e1[e1["model"] == "hf/Qwen2.5-1.5B-Instruct"]
    pts = []
    for r in q.itertuples():
        pts.append({"task": r.task, "vid": r.vid, "mode": r.mode, "nMSD": r.nMSD,
                    "MSD": r.MSD, "d_task": dbar.loc[r.vid, r.task],
                    "d_valence": dbar.loc[r.vid, "VAL"]})
    pts = pd.DataFrame(pts)
    pts.to_csv(CS / "e3_points.csv", index=False)
    res = {
        "task_aligned": stats.spearman_perm(pts["d_task"], pts["nMSD"]),
        "valence_baseline": stats.spearman_perm(pts["d_valence"], pts["nMSD"]),
    }
    for k in ("REC", "PRE", "CRED"):
        sub = pts[pts.task == k]
        res[f"within_{k}"] = stats.spearman_perm(sub["d_task"], sub["nMSD"], n_perm=5000)
    with open(CS / "e3_summary.json", "w", encoding="utf-8") as f:
        json.dump(res, f, indent=2)
    return pts


# ------------------------------------------------------------------ COMPAS
def analyze_compas() -> pd.DataFrame | None:
    df = load_runs(CP / "e1_raw")
    if df.empty:
        return None
    df["recid"] = df["meta"].apply(lambda m: m["two_year_recid"])
    df["decile"] = df["meta"].apply(lambda m: m["decile_score"])
    status_table(df).to_csv(CP / "compas_status.csv", index=False)
    rows = []
    for model, g in df.groupby("model"):
        ok = g[g["status"].isin(metrics.OK_STATUSES)]
        ctrl = ok[ok["mode"] == "control"]
        base = ctrl.drop_duplicates("sid")
        row = {"model": model, "n_records": int(base["sid"].nunique()),
               "AUC_llm_control": compas.auc(ctrl["value"], ctrl["recid"]),
               "ACC_llm_control_thr5": float(((ctrl["value"] >= 5) == (ctrl["recid"] == 1)).mean()),
               "AUC_compas_decile": compas.auc(base["decile"], base["recid"]),
               "ACC_compas_decile_thr5": float(((base["decile"] >= 5) == (base["recid"] == 1)).mean())}
        # error-rate balance (separation): FPR / FNR per variant at threshold 5
        for vid_suffix in ("het_exp", "gay_exp|les_exp", "bi_exp", "het_imp", "gay_imp|les_imp", "ctrl"):
            sub = ok[ok["vid"].str.contains(vid_suffix)]
            pred = sub["value"] >= 5
            neg, pos = sub["recid"] == 0, sub["recid"] == 1
            key = vid_suffix.split("|")[0].replace("gay", "lgb")
            row[f"FPR_{key}"] = float(pred[neg].mean())
            row[f"FNR_{key}"] = float((~pred[pos]).mean())
            row[f"AUC_{key}"] = compas.auc(sub["value"], sub["recid"])
        rows.append(row)
    summary = pd.DataFrame(rows)
    summary.to_csv(CP / "compas_summary.csv", index=False)
    # counterfactual metrics on real records (gender of the record)
    e1 = metrics.e1_table(df.drop(columns=["recid", "decile"]), versus="ref")
    e1.to_csv(CP / "compas_e1_vs_reference.csv", index=False)
    return summary


if __name__ == "__main__":
    res = analyze_case_study()
    e1 = res["e1"]
    pd.set_option("display.width", 220)
    cols = ["model", "task", "vid", "n_pairs", "CFR", "CFR_worse", "CFR_better", "MSD",
            "MSD_lo", "MSD_hi", "p_wilcoxon", "p_wilcoxon_holm", "r_rb"]
    print(e1[cols].round(3).to_string())
    pre = e1[e1.task == "PRE"][["model", "vid", "custodial_v", "custodial_ref", "RD", "DIR",
                                "p_mcnemar", "p_mcnemar_holm"]]
    print(pre.round(3).to_string())
    print(pd.read_csv(CS / "e1_h1b.csv").round(3).to_string())
    print(res["mc"].round(3).to_string())
    print(pd.read_csv(CS / "e1_determinism.csv").to_string())
    if (CS / "e2_seat_Qwen2.5-1.5B-Instruct.csv").exists():
        pts = analyze_e3(e1)
        print(pts.round(3).to_string())
        print(open(CS / "e3_summary.json").read())
    s = analyze_compas()
    if s is not None:
        print(s.round(3).T.to_string())
