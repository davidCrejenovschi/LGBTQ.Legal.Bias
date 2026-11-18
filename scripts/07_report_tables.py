"""Generate the Markdown tables used in the report (report/generated/*.md)
directly from the result files, so the numbers in the document always match
the computed ones."""
from __future__ import annotations

import ast
import json
import pathlib
import subprocess

import numpy as np
import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parents[1]
CS = ROOT / "results" / "case_study"
CP = ROOT / "results" / "compas"
OUT = ROOT / "report" / "generated"
OUT.mkdir(parents=True, exist_ok=True)

MODEL = {"ollama/llama3.1:latest": "Llama-3.1-8B", "hf/Qwen2.5-1.5B-Instruct": "Qwen2.5-1.5B"}
VID = {"M_gay_exp": "gay (expl.)", "M_bi_exp": "bărbat bisexual (expl.)",
       "F_les_exp": "lesbiană (expl.)", "F_bi_exp": "femeie bisexuală (expl.)",
       "M_gay_imp": "bărbat cu soț (impl.)", "F_les_imp": "femeie cu soție (impl.)",
       "M_het_exp": "bărbat heterosexual (expl.)", "F_het_exp": "femeie heterosexuală (expl.)",
       "M_het_imp": "bărbat cu soție (impl.)", "F_het_imp": "femeie cu soț (impl.)"}
VID_ORDER = ["M_gay_exp", "M_bi_exp", "M_gay_imp", "F_les_exp", "F_bi_exp", "F_les_imp"]
TASKS = ["REC", "PRE", "CRED"]


def f(x, nd=2, sign=False) -> str:
    if x is None or (isinstance(x, float) and np.isnan(x)):
        return "–"
    s = f"{x:+.{nd}f}" if sign else f"{x:.{nd}f}"
    return s.replace("-", "−").replace(".", ",")


def pct(x) -> str:
    return "–" if x is None or np.isnan(x) else f"{100 * x:.0f}%"


def pv(p) -> str:
    if p is None or np.isnan(p):
        return "–"
    return "< 0,001" if p < 0.001 else f(p, 3)


def table(caption: str, header: list[str], rows: list[list[str]]) -> str:
    lines = [f"Table: {caption}", "", "| " + " | ".join(header) + " |",
             "|" + "---|" * len(header)]
    lines += ["| " + " | ".join(r) + " |" for r in rows]
    return "\n".join(lines) + "\n"


def write(name: str, text: str) -> None:
    (OUT / name).write_text(text, encoding="utf-8")
    print("wrote", name)


def status():
    s = pd.read_csv(CS / "e1_status.csv")
    rows = []
    for r in s.itertuples():
        ok = getattr(r, "ok", 0) + getattr(r, "ok_lenient", 0)
        rows.append([MODEL[r.model], r.task, str(r.n), f"{ok} ({pct(ok / r.n)})",
                     str(getattr(r, "refusal", 0)), str(getattr(r, "unparseable", 0)),
                     f(r.median_latency_s, 2) + " s"])
    det = pd.read_csv(CS / "e1_determinism.csv")
    write("status.md", table(
        "Calitatea răspunsurilor în studiul de caz (720 de prompturi pe model).",
        ["Model", "Sarcina", "Prompturi", "Format corect", "Refuzuri", "Neinterpretabile",
         "Latența mediană"], rows))
    return det


def manip():
    m = pd.read_csv(CS / "e1_manipulation_check.csv")
    rows = []
    for r in m.itertuples():
        means = ast.literal_eval(r.mean_by_level)
        rows.append([MODEL[r.model], r.task,
                     " / ".join(f(means[k], 2) for k in sorted(means)),
                     f(r.rho, 2, sign=True), pv(r.p)])
    write("manip.md", table(
        "Verificarea de manipulare: decizia medie pe nivelurile factorului juridic (variantele de "
        "control, 40 de răspunsuri pe sarcină și model) și corelația Spearman cu gravitatea factorului.",
        ["Model", "Sarcina", "Decizia medie pe niveluri (0 / 1 / 2)", "ρ_{manip}", "p"], rows))


def e1_main():
    e = pd.read_csv(CS / "e1_vs_reference.csv")
    rows = []
    for model in MODEL:
        for task in TASKS:
            for vid in VID_ORDER:
                r = e[(e.model == model) & (e.task == task) & (e.vid == vid)]
                if r.empty:
                    continue
                r = r.iloc[0]
                rows.append([MODEL[model], task, VID[vid], str(int(r.n_pairs)), pct(r.CFR),
                             f"{pct(r.CFR_worse)} / {pct(r.CFR_better)}",
                             f"{f(r.MSD, 2, True)} [{f(r.MSD_lo, 2, True)}; {f(r.MSD_hi, 2, True)}]",
                             f(r.r_rb, 2, True), pv(r.p_wilcoxon), pv(r.p_wilcoxon_holm)])
    write("e1_main.md", table(
        "Rezultatele E1: fiecare variantă LGBTQ+ comparată cu referința heterosexuală (același gen, "
        "același tip de semnalare). CFR⁺/CFR⁻: proporția perechilor în care decizia se schimbă în "
        "defavoarea / în favoarea variantei LGBTQ+; MSD > 0 înseamnă tratament mai defavorabil.",
        ["Model", "Sarcina", "Varianta", "n", "CFR", "CFR⁺ / CFR⁻", "MSD [IÎ 95%]", "r_{rb}",
         "p Wilcoxon", "p Holm"], rows))


def e1_pre():
    e = pd.read_csv(CS / "e1_vs_reference.csv")
    e = e[e.task == "PRE"]
    rows = []
    for model in MODEL:
        for vid in VID_ORDER:
            r = e[(e.model == model) & (e.vid == vid)]
            if r.empty:
                continue
            r = r.iloc[0]
            rows.append([MODEL[model], VID[vid], pct(r.custodial_v), pct(r.custodial_ref),
                         f(r.RD, 2, True), f(r.DIR, 2), f"{int(r.n10)} / {int(r.n01)}",
                         pv(r.p_mcnemar), pv(r.p_mcnemar_holm)])
    write("e1_pre.md", table(
        "Măsura preventivă ca decizie binară (privare de libertate: arest la domiciliu sau arestare "
        "preventivă). n₁₀ / n₀₁: perechi în care doar varianta LGBTQ+ / doar referința primește "
        "măsura privativă.",
        ["Model", "Varianta", "P_{v}", "P_{ref}", "RD", "DIR", "n₁₀ / n₀₁", "p McNemar", "p Holm"], rows))


def e1_control():
    e = pd.read_csv(CS / "e1_vs_control.csv")
    order = ["M_het_exp", "M_gay_exp", "M_bi_exp", "M_het_imp", "M_gay_imp",
             "F_het_exp", "F_les_exp", "F_bi_exp", "F_het_imp", "F_les_imp"]
    header = ["Varianta"] + [f"{MODEL[m]} {t}" for m in MODEL for t in TASKS]
    rows = []
    for vid in order:
        row = [VID[vid]]
        for m in MODEL:
            for t in TASKS:
                r = e[(e.model == m) & (e.task == t) & (e.vid == vid)]
                if r.empty:
                    row.append("–")
                    continue
                r = r.iloc[0]
                star = "*" if r.p_wilcoxon < 0.05 else ""
                row.append(f(r.MSD, 2, True) + star)
        rows.append(row)
    write("e1_control.md", table(
        "Abaterea fiecărei variante față de varianta de control cu același gen (MSD față de "
        "control; > 0 = mai defavorabil decât persoana fără orientare menționată; * p < 0,05 "
        "Wilcoxon, necorectat).", header, rows))


def h1b():
    h = pd.read_csv(CS / "e1_h1b.csv")
    rows = []
    for r in h.itertuples():
        rows.append([MODEL[r.model], r.task, "bărbat gay" if r.implicit.startswith("M") else "femeie lesbiană",
                     f(r.MSD_explicit, 2, True), f(r.MSD_implicit, 2, True),
                     f"{f(r.mean_D, 2, True)} [{f(r.D_lo, 2, True)}; {f(r.D_hi, 2, True)}]",
                     pv(r.p_wilcoxon)])
    write("h1b.md", table(
        "Testarea ipotezei H1b: prejudiciul mediu în varianta explicită și în cea implicită și "
        "diferența lor pe același scenariu, D = Δ_{impl} − Δ_{expl} (> 0 susține H1b).",
        ["Model", "Sarcina", "Identitatea", "MSD explicit", "MSD implicit", "D mediu [IÎ 95%]",
         "p Wilcoxon"], rows))


def e2():
    d = pd.read_csv(CS / "e2_seat_Qwen2.5-1.5B-Instruct.csv")
    st = d[d.rep == "standardized"]
    rows = []
    for vid in VID_ORDER:
        row = [VID[vid]]
        for c in ["REC", "PRE", "CRED", "VAL"]:
            s = st[(st.vid == vid) & (st.concept == c)]
            row.append(f"{f(s.d.mean(), 2, True)} ({pct((s.p < 0.05).mean())})")
        rows.append(row)
    write("e2_main.md", table(
        "Rezultatele E2 pe Qwen2.5-1.5B-Instruct (vectori standardizați): mărimea medie a efectului "
        "pe cele 28 de straturi, d̄, și, în paranteză, proporția straturilor cu p < 0,05 "
        "(test de permutare unilateral).",
        ["Varianta", "periculos–inofensiv (REC)", "vinovat–nevinovat (PRE)",
         "necinstit–credibil (CRED)", "neplăcut–plăcut (bază)"], rows))
    rows = []
    expl = ["M_gay_exp", "M_bi_exp", "F_les_exp", "F_bi_exp"]
    for rep, lab in (("raw", "vectori bruți (fără primul token)"), ("centered", "centrați"),
                     ("standardized", "standardizați")):
        s = d[(d.rep == rep) & d.vid.isin(expl)]
        row = [lab]
        for c in ["REC", "PRE", "CRED", "VAL"]:
            sc = s[s.concept == c]
            row.append(f"{f(sc.d.mean(), 2, True)} / {f(sc.dz.mean(), 2, True)}")
        rows.append(row)
    write("e2_robust.md", table(
        "Robustețea E2 la preprocesare: media efectelor pentru cele 4 variante explicite, ca "
        "d (SEAT clasic) / d_{z} (varianta pe perechi).",
        ["Preprocesare", "periculos–inofensiv", "vinovat–nevinovat", "necinstit–credibil",
         "neplăcut–plăcut (bază)"], rows))


def e3():
    s = json.loads((CS / "e3_summary.json").read_text())
    lab = {"task_aligned": "concept aliniat pe sarcină, toate sarcinile",
           "valence_baseline": "valență generică (bază), toate sarcinile",
           "within_REC": "aliniat, doar REC", "within_PRE": "aliniat, doar PRE",
           "within_CRED": "aliniat, doar CRED"}
    rows = [[lab[k], str(v["n"]), f(v["rho"], 2, True), f"[{f(v['ci'][0], 2, True)}; {f(v['ci'][1], 2, True)}]",
             pv(v["p_perm"])] for k, v in s.items()]
    write("e3.md", table(
        "Rezultatele E3: corelația Spearman dintre asocierea din reprezentări (d̄) și diferența "
        "normalizată de decizie (nMSD) pentru Qwen2.5-1.5B-Instruct.",
        ["Asocierea folosită", "Puncte", "ρ", "IÎ 95% (bootstrap)", "p (permutare)"], rows))


def compas_tables():
    if not (CP / "compas_summary.csv").exists():
        return
    s = pd.read_csv(CP / "compas_summary.csv")
    rows = []
    first = s.iloc[0]
    rows.append(["COMPAS (decile ≥ 5)", f(first.AUC_compas_decile, 3), pct(first.ACC_compas_decile_thr5)])
    for r in s.itertuples():
        rows.append([f"{MODEL[r.model]} (control, scor ≥ 5)", f(r.AUC_llm_control, 3),
                     pct(r.ACC_llm_control_thr5)])
    out = table(
        f"Pilotul pe date reale: capacitatea de a prezice recidiva în 2 ani pe aceleași "
        f"{int(first.n_records)} dosare COMPAS (eșantion echilibrat).",
        ["Predictor", "AUC", "Acuratețe"], rows)
    rows = []
    keys = [("het_exp", "heterosexual (expl.)"), ("lgb_exp", "gay / lesbiană (expl.)"),
            ("bi_exp", "bisexual (expl.)"), ("het_imp", "partener de sex opus (impl.)"),
            ("lgb_imp", "partener de același sex (impl.)"), ("ctrl", "control")]
    for r in s.itertuples():
        for k, lab in keys:
            rows.append([MODEL[r.model], lab, f(getattr(r, f"AUC_{k}"), 3),
                         pct(getattr(r, f"FPR_{k}")), pct(getattr(r, f"FNR_{k}"))])
    out += "\n" + table(
        "Ratele de eroare pe variante de identitate pe datele COMPAS (prag: scor ≥ 5). Criteriul de "
        "separare cere FPR și FNR egale între variante.",
        ["Model", "Varianta", "AUC", "FPR", "FNR"], rows)
    e = pd.read_csv(CP / "compas_e1_vs_reference.csv")
    rows = []
    for r in e.itertuples():
        rows.append([MODEL[r.model], VID[r.vid], str(int(r.n_pairs)), pct(r.CFR),
                     f"{f(r.MSD, 2, True)} [{f(r.MSD_lo, 2, True)}; {f(r.MSD_hi, 2, True)}]",
                     pv(r.p_wilcoxon)])
    out += "\n" + table(
        "Diferențele contrafactuale pe dosarele reale (scorul de risc 1–10, comparat cu referința "
        "heterosexuală de același gen).",
        ["Model", "Varianta", "n", "CFR", "MSD [IÎ 95%]", "p Wilcoxon"], rows)
    write("compas.md", out)


def git_log():
    fmt = "%h|%ad|%s"
    log = subprocess.run(["git", "log", f"--pretty=format:{fmt}", "--date=format:%Y-%m-%d %H:%M"],
                         cwd=ROOT, capture_output=True, text=True, encoding="utf-8").stdout
    rows = []
    for line in log.splitlines():
        h, d, msg = line.split("|", 2)
        n = subprocess.run(["git", "show", "--stat", "--format=", h], cwd=ROOT, capture_output=True,
                           text=True, encoding="utf-8").stdout.strip().splitlines()
        rows.append([f"`{h}`", d, msg, n[-1].strip() if n else ""])
    write("git_log.md", table("Istoricul commit-urilor (cel mai recent primul).",
                              ["Commit", "Data", "Descriere", "Modificări"], rows))


if __name__ == "__main__":
    status()
    manip()
    e1_main()
    e1_pre()
    e1_control()
    h1b()
    e2()
    if (CS / "e3_summary.json").exists():
        e3()
    compas_tables()
    git_log()
