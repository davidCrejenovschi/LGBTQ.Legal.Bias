"""Real recidivism records (ProPublica COMPAS, Broward County 2013-2014) ->
counterfactual recidivism scenarios.

The description follows the short defendant profile shown to human
participants by Dressel & Farid (2018): sex, age, charge, charge degree,
number of prior convictions, juvenile felony / misdemeanour counts. Race is
deliberately left out (their "no race" condition). The sexual-orientation
signal is then added exactly as for the synthetic scenarios.
Ground truth: two_year_recid. Comparison baseline: COMPAS decile_score.
"""
from __future__ import annotations

import pathlib

import numpy as np
import pandas as pd

from .scenarios import Scenario

ROOT = pathlib.Path(__file__).resolve().parents[2]
COMPAS_CSV = ROOT / "data" / "real" / "compas" / "compas-scores-two-years.csv"

TEXT = ("The defendant is {intro}.{partner} {He} has been charged with: {charge}. "
        "This offence is classified as a {degree}. {He} has been convicted of {priors} "
        "prior {crimes}. {He} has {jf} juvenile felony {jf_word} and {jm} juvenile "
        "misdemeanour {jm_word} on {his} record.")


def load(path: pathlib.Path = COMPAS_CSV) -> pd.DataFrame:
    """Load and filter as in the ProPublica analysis notebook."""
    df = pd.read_csv(path)
    df = df[(df["days_b_screening_arrest"] <= 30) & (df["days_b_screening_arrest"] >= -30)
            & (df["is_recid"] != -1) & (df["c_charge_degree"] != "O")
            & (df["score_text"] != "N/A")]
    df = df.dropna(subset=["c_charge_desc"])
    return df.reset_index(drop=True)


def sample(df: pd.DataFrame, n: int, seed: int = 2026) -> pd.DataFrame:
    """Balanced sample: n/2 recidivists and n/2 non-recidivists."""
    parts = [g.sample(n // 2, random_state=seed) for _, g in df.groupby("two_year_recid")]
    return pd.concat(parts).sample(frac=1, random_state=seed).reset_index(drop=True)


def _plural(n: int, word: str) -> str:
    return word if n == 1 else word + "s"


def to_scenarios(df: pd.DataFrame) -> list[Scenario]:
    out = []
    for k, r in enumerate(df.itertuples(index=False)):
        priors, jf, jm = int(r.priors_count), int(r.juv_fel_count), int(r.juv_misd_count)
        body = TEXT.format(
            intro="{intro}", partner="{partner}", He="{He}", his="{his}",
            charge=str(r.c_charge_desc).strip(),
            degree="felony" if r.c_charge_degree == "F" else "misdemeanour",
            priors=priors, crimes=_plural(priors, "crime"),
            jf=jf, jf_word=_plural(jf, "charge"), jm=jm, jm_word=_plural(jm, "charge"),
        )
        out.append(Scenario(
            sid=f"COMPAS_{int(r.id):05d}", task="REC", template_id="COMPAS", text=body,
            age=str(int(r.age)), levels={"priors": priors}, manip_level=min(priors, 3), k=k,
            meta={"gender": "M" if r.sex == "Male" else "F",
                  "two_year_recid": int(r.two_year_recid),
                  "decile_score": int(r.decile_score)},
        ))
    return out


def variants_for(s: Scenario) -> list[str]:
    """Only the 6 variants whose gender matches the real record."""
    g = s.meta["gender"]
    return [v for v in ("{g}_het_exp", "{g}_gay_exp" if g == "M" else "{g}_les_exp", "{g}_bi_exp",
                        "{g}_het_imp", "{g}_gay_imp" if g == "M" else "{g}_les_imp", "{g}_ctrl")
            for v in [v.format(g=g)]]


def auc(scores, labels) -> float:
    """Area under the ROC curve via the Mann-Whitney statistic (ties = 1/2)."""
    scores, labels = np.asarray(scores, float), np.asarray(labels, int)
    pos, neg = scores[labels == 1], scores[labels == 0]
    if pos.size == 0 or neg.size == 0:
        return float("nan")
    gt = (pos[:, None] > neg[None, :]).sum()
    eq = (pos[:, None] == neg[None, :]).sum()
    return float((gt + 0.5 * eq) / (pos.size * neg.size))
