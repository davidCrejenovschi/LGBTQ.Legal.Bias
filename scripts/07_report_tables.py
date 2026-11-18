"""Generate the Markdown tables used in the report (report/generated/*.md)
directly from the result files, so the numbers in the document always match
the computed ones."""
from __future__ import annotations

import ast
import re
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
    if abs(x) < 0.5 * 10 ** -nd:
        x = 0.0
    s = f"{x:+.{nd}f}" if sign and x != 0 else f"{x:.{nd}f}"
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
    parts = []
    for r in det.itertuples():
        name = "Llama-3.1-8B" if "llama" in r.model else "Qwen2.5-1.5B"
        same = int(round(r.identical * r.n))
        parts.append(f"{name} – {same} din {int(r.n)} răspunsuri identice ({f(100 * r.identical, 1)}%)")
    (OUT / "determinism.md").write_text("; ".join(parts) + ".", encoding="utf-8")
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


NB = " "   # non-breaking space: keeps "0% / 15%" and "[a; b]" on one line


def ci(lo, hi) -> str:
    return f"[{f(lo, 2, True)};{NB}{f(hi, 2, True)}]"


def e1_main():
    e = pd.read_csv(CS / "e1_vs_reference.csv")
    out = []
    for model in MODEL:
        rows = []
        for task in TASKS:
            for vid in VID_ORDER:
                r = e[(e.model == model) & (e.task == task) & (e.vid == vid)]
                if r.empty:
                    continue
                r = r.iloc[0]
                rows.append([task, VID[vid], pct(r.CFR),
                             f"{pct(r.CFR_worse)}{NB}/{NB}{pct(r.CFR_better)}",
                             f"{f(r.MSD, 2, True)} {ci(r.MSD_lo, r.MSD_hi)}",
                             f(r.r_rb, 2, True), pv(r.p_wilcoxon), pv(r.p_wilcoxon_holm)])
        n = int(e[e.model == model].n_pairs.min())
        out.append(table(
            f"Rezultatele E1 pentru {MODEL[model]}: fiecare variantă LGBTQ+ comparată cu referința "
            f"heterosexuală (același gen, același tip de semnalare), n = {n} perechi de scenarii. "
            "CFR⁺ / CFR⁻: proporția perechilor în care decizia se schimbă în defavoarea / în favoarea "
            "variantei LGBTQ+; MSD > 0 înseamnă tratament mai defavorabil.",
            ["Sarcina", "Varianta", "CFR", "CFR⁺ / CFR⁻", "MSD [IÎ 95%]", "r_{rb}", "p Wilcoxon",
             "p Holm"], rows))
    write("e1_main.md", "\n".join(out))


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
                         f(r.RD, 2, True), f(r.DIR, 2), f"{int(r.n10)}{NB}/{NB}{int(r.n01)}",
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
                     f"{f(r.mean_D, 2, True)} {ci(r.D_lo, r.D_hi)}",
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
    rows = [[lab[k], str(v["n"]), f(v["rho"], 2, True), ci(v['ci'][0], v['ci'][1]),
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
    rows.append(["COMPAS (decile ≥ 5)",
                 f"{f(first.AUC_compas_decile, 2)} [{f(first.AUC_compas_lo, 2)}; {f(first.AUC_compas_hi, 2)}]",
                 pct(first.ACC_compas_decile_thr5), "–"])
    for r in s.itertuples():
        rows.append([f"{MODEL[r.model]} (control, scor ≥ 5)",
                     f"{f(r.AUC_llm_control, 2)} [{f(r.AUC_llm_lo, 2)}; {f(r.AUC_llm_hi, 2)}]",
                     pct(r.ACC_llm_control_thr5),
                     ci(r.AUC_diff_lo, r.AUC_diff_hi)])
    out = table(
        f"Pilotul pe date reale: predicția recidivei în 2 ani pe aceleași {int(first.n_records)} "
        f"de dosare COMPAS (eșantion echilibrat, {int(first.n_male)} de bărbați). Între paranteze: "
        f"intervale de încredere bootstrap de 95%.",
        ["Predictor", "AUC [IÎ 95%]", "Acuratețe", "Diferența de AUC față de COMPAS [IÎ 95%]"], rows)
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
                     f"{f(r.MSD, 2, True)} {ci(r.MSD_lo, r.MSD_hi)}",
                     pv(r.p_wilcoxon)])
    out += "\n" + table(
        "Diferențele contrafactuale pe dosarele reale (scorul de risc 1–10, comparat cu referința "
        "heterosexuală de același gen).",
        ["Model", "Varianta", "n", "CFR", "MSD [IÎ 95%]", "p Wilcoxon"], rows)
    write("compas.md", out)


def expectations():
    """Table for section 3.8: literature reference, expectation, case-study evidence."""
    e = pd.read_csv(CS / "e1_vs_reference.csv")
    h = pd.read_csv(CS / "e1_h1b.csv")
    d2 = pd.read_csv(CS / "e2_seat_Qwen2.5-1.5B-Instruct.csv")
    d2 = d2[(d2.rep == "standardized") & d2.vid.str.endswith("_exp")]
    agg = d2.groupby(["vid", "concept"]).agg(d=("d", "mean"), sig=("p", lambda p: (p < 0.05).mean()))
    e3s = json.loads((CS / "e3_summary.json").read_text())

    def rng(series, nd=2):
        return f"{f(series.min(), nd, True)} … {f(series.max(), nd, True)}"

    def model_summary(model):
        sub = e[e.model == model]
        expl = sub[sub["mode"] == "explicit"]
        impl = sub[sub["mode"] == "implicit"]
        out = []
        for t in ("CRED", "REC"):
            ex, im = expl[expl.task == t], impl[impl.task == t]
            out.append(f"{t} {rng(ex.MSD)} (expl.), {rng(im.MSD)} (impl.)")
        return "; ".join(out)

    def dir_summary(model):
        d = e[(e.model == model) & (e.task == "PRE")].DIR
        if d.isna().all():
            return f"{MODEL[model]}: nedefinit (privare de libertate în 100% din cazuri)"
        if d.min() == d.max():
            return f"{MODEL[model]}: {f(d.min(), 2)} pentru toate variantele"
        return f"{MODEL[model]}: {f(d.min(), 2)}–{f(d.max(), 2)}"
    cmp_path = CP / "compas_summary.csv"
    if cmp_path.exists():
        cs = pd.read_csv(cmp_path)
        auc_txt = "; ".join(f"{MODEL[r.model]}: AUC {f(r.AUC_llm_control, 2)}, acuratețe {pct(r.ACC_llm_control_thr5)}"
                            for r in cs.itertuples())
        auc_txt += f"; COMPAS pe aceleași dosare: AUC {f(cs.iloc[0].AUC_compas_decile, 2)}, acuratețe {pct(cs.iloc[0].ACC_compas_decile_thr5)}"
        fpr = []
        for r in cs.itertuples():
            vals = [getattr(r, f"FPR_{k}") for k in ("het_exp", "lgb_exp", "bi_exp", "het_imp", "lgb_imp", "ctrl")]
            fnr = [getattr(r, f"FNR_{k}") for k in ("het_exp", "lgb_exp", "bi_exp", "het_imp", "lgb_imp", "ctrl")]
            fpr.append(f"{MODEL[r.model]}: FPR {pct(min(vals))}–{pct(max(vals))}, FNR {pct(min(fnr))}–{pct(max(fnr))}")
        fpr_txt = "; ".join(fpr)
    else:
        auc_txt = fpr_txt = "în curs"
    hl = h[(h.model == "ollama/llama3.1:latest")]
    rows = [
        ["Diferența de decizie (CFR, MSD)", "Tamkin et al. [9]; Hofmann et al. [2]",
         "diferențe sistematice în decizii pentru vârstă, gen, rasă și dialect",
         "similar: diferențe nenule și pentru orientarea sexuală",
         "MSD pe variante LGBTQ+. Llama: " + model_summary("ollama/llama3.1:latest") + ". Qwen: " +
         model_summary("hf/Qwen2.5-1.5B-Instruct") + f". PRE: între {f(e[e.task == 'PRE'].MSD.min(), 2, True)} și {f(e[e.task == 'PRE'].MSD.max(), 2, True)} (plafon)"],
        ["Explicit vs. implicit (H1b)", "Hofmann et al. [2]",
         "stereotipuri declarate pozitive, asocieri ascunse negative; RLHF corectează doar ce este declarat",
         "similar: efect favorabil sau nul la semnalarea explicită, mai defavorabil la cea implicită",
         "Llama, CRED: D = " + ", ".join(f(x, 2, True) for x in hl[hl.task == "CRED"].mean_D) +
         " (p " + ", ".join(pv(x) for x in hl[hl.task == "CRED"].p_wilcoxon) + "); favorabil explicit, aproape nul implicit"],
        ["Impact disparat (DIR, prag 0,8)", "Feldman et al. [12]",
         "regula celor patru cincimi", "DIR ≥ 0,8 pentru majoritatea combinațiilor",
         "PRE – " + "; ".join(dir_summary(m) for m in MODEL)],
        ["Asocieri generice (plăcut–neplăcut)", "Caliskan et al. [4]; May et al. [5]",
         "efecte mari pentru vectori de cuvinte, inconsecvente pentru codificatoare de propoziții",
         "similar: efecte slabe sau inconsecvente",
         f"Qwen, variante explicite: d̄ {rng(agg.xs('VAL', level='concept').d)}, "
         f"cel mult {pct(agg.xs('VAL', level='concept').sig.max())} din straturi semnificative"],
        ["Asocieri cu concepte juridice", "– (contribuție nouă)", "–",
         "mai bun (mai sensibil) decât testul generic",
         f"Qwen, vinovat–nevinovat: d̄ {rng(agg.xs('PRE', level='concept').d)}, "
         f"{pct(agg.xs('PRE', level='concept').sig.min())}–{pct(agg.xs('PRE', level='concept').sig.max())} din straturi semnificative"],
        ["Legătura intrinsec–extrinsec", "Goldfarb-Tarrant et al. [16]",
         "nicio corelație consistentă", "similar sau mai bun: ρ (concept aliniat) > ρ (generic)",
         f"Qwen: ρ = {f(e3s['task_aligned']['rho'], 2, True)} (p {pv(e3s['task_aligned']['p_perm'])}) "
         f"față de ρ_{{VAL}} = {f(e3s['valence_baseline']['rho'], 2, True)} (p {pv(e3s['valence_baseline']['p_perm'])})"],
        ["Predicția recidivei (AUC, acuratețe)", "Dressel și Farid [13]",
         "COMPAS 65,2%; oameni fără pregătire 62–67%", "similar: 60–70%", auc_txt],
        ["Egalitatea erorilor (FPR, FNR)", "Angwin et al. [22]; Chouldechova [23]",
         "FPR aproape dublă pentru inculpații de culoare la COMPAS",
         "diferențe mici între variantele de orientare", fpr_txt],
    ]
    write("expectations.md", table(
        "Metricile la care se așteaptă rezultate similare sau mai bune decât în literatură și "
        "ce arată studiul de caz.",
        ["Metrică", "Referința", "Rezultatul din literatură", "Așteptarea (experimentul complet)",
         "Studiul de caz"], rows))


def git_log():
    fmt = "%h|%ad|%s"
    log = subprocess.run(["git", "log", f"--pretty=format:{fmt}", "--date=format:%Y-%m-%d %H:%M"],
                         cwd=ROOT, capture_output=True, text=True, encoding="utf-8").stdout
    rows = []
    for line in log.splitlines():
        h, d, msg = line.split("|", 2)
        n = subprocess.run(["git", "show", "--shortstat", "--format=", h], cwd=ROOT, capture_output=True,
                           text=True, encoding="utf-8").stdout.strip()
        files = re.search(r"(\d+) files? changed", n)
        ins = re.search(r"(\d+) insertions?", n)
        dels = re.search(r"(\d+) deletions?", n)
        stat = (f"{files.group(1) if files else 0} fișiere, +{ins.group(1) if ins else 0} / "
                f"−{dels.group(1) if dels else 0} linii")
        rows.append([f"`{h}`", d, msg, stat])
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
    if (CS / "e3_summary.json").exists():
        expectations()
    git_log()
