"""Figures for the report (report/figures/*.png)."""
from __future__ import annotations

import json
import pathlib
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
CS = ROOT / "results" / "case_study"
FIG = ROOT / "report" / "figures"
FIG.mkdir(parents=True, exist_ok=True)

# reference palette (light mode): categorical slots 1-3, text and grid tokens
BLUE, ORANGE, AQUA, YELLOW = "#2a78d6", "#eb6834", "#1baf7a", "#eda100"
INK, INK2, GRID, NEUTRAL = "#0b0b0b", "#52514e", "#e4e3df", "#8a8984"
MODEL_COLOR = {"ollama/llama3.1:latest": BLUE, "hf/Qwen2.5-1.5B-Instruct": ORANGE}
MODEL_LABEL = {"ollama/llama3.1:latest": "Llama-3.1-8B-Instruct (Q4)",
               "hf/Qwen2.5-1.5B-Instruct": "Qwen2.5-1.5B-Instruct"}
TASK_LABEL = {"REC": "REC – risc de recidivă (1–10)", "PRE": "PRE – măsura preventivă (1–5)",
              "CRED": "CRED – credibilitatea martorului (1–10)"}
VID_LABEL = {"M_gay_exp": "gay (explicit)", "M_bi_exp": "bărbat bisexual (explicit)",
             "F_les_exp": "lesbiană (explicit)", "F_bi_exp": "femeie bisexuală (explicit)",
             "M_gay_imp": "bărbat cu soț (implicit)", "F_les_imp": "femeie cu soție (implicit)"}
VID_ORDER = ["M_gay_exp", "M_bi_exp", "M_gay_imp", "F_les_exp", "F_bi_exp", "F_les_imp"]

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 9, "axes.edgecolor": NEUTRAL,
    "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2,
    "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True,
    "grid.color": GRID, "grid.linewidth": 0.6, "axes.axisbelow": True,
    "legend.frameon": False, "savefig.dpi": 200, "savefig.bbox": "tight",
    "axes.titlesize": 9.5, "axes.titlecolor": INK, "axes.titleweight": "bold",
})


def fig_e1_forest():
    e1 = pd.read_csv(CS / "e1_vs_reference.csv")
    models = [m for m in MODEL_LABEL if m in set(e1["model"])]
    fig, axes = plt.subplots(1, 3, figsize=(10, 3.8), sharey=True)
    for ax, task in zip(axes, ("REC", "PRE", "CRED")):
        for k, m in enumerate(models):
            sub = e1[(e1.task == task) & (e1.model == m)].set_index("vid").reindex(VID_ORDER)
            y = np.arange(len(VID_ORDER)) + (k - 0.5) * 0.28
            ax.errorbar(sub["MSD"], y, xerr=[sub["MSD"] - sub["MSD_lo"], sub["MSD_hi"] - sub["MSD"]],
                        fmt="o", ms=5, color=MODEL_COLOR[m], ecolor=MODEL_COLOR[m], elinewidth=1.6,
                        capsize=0, label=MODEL_LABEL[m], mec="white", mew=0.8)
        ax.axvline(0, color=INK2, lw=1)
        ax.set_title(TASK_LABEL[task], loc="left")
        ax.set_xlabel("MSD (puncte pe scală; > 0 = LGBTQ+ defavorizat)")
        lim = max(0.6, np.nanmax(np.abs(e1[e1.task == task][["MSD_lo", "MSD_hi"]].to_numpy())) * 1.15)
        ax.set_xlim(-lim, lim)
        ax.grid(axis="y", visible=False)
    axes[0].set_yticks(range(len(VID_ORDER)), [VID_LABEL[v] for v in VID_ORDER])
    axes[0].invert_yaxis()
    h, lab = axes[0].get_legend_handles_labels()
    fig.legend(h, lab, loc="upper center", ncol=2, bbox_to_anchor=(0.5, 1.06))
    fig.tight_layout()
    fig.savefig(FIG / "e1_msd_forest.png")
    plt.close(fig)


def fig_manipulation():
    df = pd.concat([pd.read_json(p, lines=True) for p in (CS / "e1_raw").glob("*.jsonl")
                    if not p.stem.endswith("_pilot")])
    df = df[df["status"].isin(["ok", "ok_lenient"]) & (df["mode"] == "control")]
    xl = {"REC": ["0 antecedente", "1 veche", "3 recente"],
          "PRE": ["stabil, cooperează", "fără domiciliu", "rude în străinătate"],
          "CRED": ["consecvent", "mică neconcordanță", "contradicții"]}
    fig, axes = plt.subplots(1, 3, figsize=(10, 2.9))
    for ax, task in zip(axes, ("REC", "PRE", "CRED")):
        for m in MODEL_LABEL:
            g = df[(df.task == task) & (df.model == m)].groupby("manip_level")["value"]
            if g.ngroups == 0:
                continue
            mean, sem = g.mean(), g.sem()
            ax.errorbar(mean.index, mean, yerr=1.96 * sem, color=MODEL_COLOR[m], marker="o", ms=5,
                        lw=2, capsize=0, label=MODEL_LABEL[m], mec="white", mew=0.8)
        ax.set_xticks([0, 1, 2], xl[task])
        ax.set_title(TASK_LABEL[task], loc="left")
        ax.set_ylabel("decizia medie (control)")
    axes[0].legend(loc="upper left", fontsize=8)
    fig.tight_layout()
    fig.savefig(FIG / "e1_manipulation_check.png")
    plt.close(fig)


def fig_e2_layers():
    e2 = pd.read_csv(CS / "e2_seat_Qwen2.5-1.5B-Instruct.csv")
    e2 = e2[e2.rep == "standardized"]
    conc = [("REC", "periculos–inofensiv", BLUE, "-"), ("PRE", "vinovat–nevinovat", ORANGE, "-"),
            ("CRED", "necinstit–credibil", AQUA, "-"), ("VAL", "neplăcut–plăcut (bază)", NEUTRAL, "--")]
    fig, axes = plt.subplots(2, 3, figsize=(10, 5.2), sharex=True, sharey=True)
    for ax, vid in zip(axes.T.flat, VID_ORDER):
        sub = e2[e2.vid == vid]
        for c, lab, col, ls in conc:
            s = sub[sub.concept == c].sort_values("layer")
            ax.plot(s["layer"], s["d"], color=col, lw=2 if c != "VAL" else 1.6, ls=ls, label=lab)
            sig = s[s.p < 0.05]
            ax.plot(sig["layer"], sig["d"], "o", color=col, ms=3.5, mec="white", mew=0.5)
        ax.axhline(0, color=INK2, lw=0.9)
        ax.set_title(VID_LABEL[vid], loc="left")
    for ax in axes[-1]:
        ax.set_xlabel("stratul ℓ")
    for ax in axes[:, 0]:
        ax.set_ylabel("dℓ (> 0: mai aproape de polul negativ)")
    h, lab = axes[0, 0].get_legend_handles_labels()
    fig.legend(h, lab, loc="upper center", ncol=4, bbox_to_anchor=(0.5, 1.04))
    fig.tight_layout()
    fig.savefig(FIG / "e2_seat_layers.png")
    plt.close(fig)


def fig_e2_anisotropy():
    a = pd.read_csv(CS / "e2_anisotropy_Qwen2.5-1.5B-Instruct.csv")
    fig, ax = plt.subplots(figsize=(6.4, 2.8))
    series = [("anisotropy_with_first_token", "media pe toți tokenii (cu primul token)", ORANGE, "-"),
              ("anisotropy_raw", "fără primul token", BLUE, "-"),
              ("anisotropy_standardized", "fără primul token + standardizare", AQUA, "-")]
    for col, lab, c, ls in series:
        if col in a:
            ax.plot(a["layer"], a[col], color=c, lw=2, ls=ls, label=lab)
    ax.set_xlabel("stratul ℓ")
    ax.set_ylabel("cosinus mediu între\npropoziții oarecare")
    ax.set_ylim(-0.1, 1.05)
    ax.legend(loc="center right", fontsize=8)
    fig.tight_layout()
    fig.savefig(FIG / "e2_anisotropy.png")
    plt.close(fig)


def fig_e3():
    pts = pd.read_csv(CS / "e3_points.csv")
    summ = json.loads((CS / "e3_summary.json").read_text())
    colors = {"REC": BLUE, "PRE": ORANGE, "CRED": AQUA}
    fig, axes = plt.subplots(1, 2, figsize=(9, 3.4), sharey=True)
    for ax, (col, key, title) in zip(axes, (
            ("d_task", "task_aligned", "Concept aliniat pe sarcină"),
            ("d_valence", "valence_baseline", "Valență generică (bază de comparație)"))):
        for task, g in pts.groupby("task"):
            for mode, mk in (("explicit", "o"), ("implicit", "s")):
                gg = g[g["mode"] == mode]
                ax.scatter(gg[col], gg["nMSD"], color=colors[task], marker=mk, s=42,
                           edgecolor="white", linewidth=0.8,
                           label=f"{task}, {'explicit' if mode == 'explicit' else 'implicit'}")
        r = summ[key]
        ax.set_title(f"{title}\nρ = {r['rho']:.2f}, p = {r['p_perm']:.2f}", loc="left")
        ax.axhline(0, color=INK2, lw=0.8)
        ax.axvline(0, color=INK2, lw=0.8)
        ax.set_xlabel("d̄ (media pe straturi, E2)")
    axes[0].set_ylabel("nMSD (E1, Qwen2.5-1.5B)")
    h, lab = axes[0].get_legend_handles_labels()
    fig.legend(h, lab, loc="center right", bbox_to_anchor=(1.12, 0.5), fontsize=8)
    fig.tight_layout()
    fig.savefig(FIG / "e3_scatter.png")
    plt.close(fig)


if __name__ == "__main__":
    for f in (fig_e1_forest, fig_manipulation, fig_e2_layers, fig_e2_anisotropy, fig_e3):
        try:
            f()
            print("ok", f.__name__)
        except FileNotFoundError as e:
            print("skip", f.__name__, e)
