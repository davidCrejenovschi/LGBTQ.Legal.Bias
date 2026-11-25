"""Formal test of the legal vs. moral split of the guilt concept (E2).

For every LGBTQ+ identity: delta = mean over layers of d(legal half) - d(moral half),
compared with all 70 x 70 = 4,900 ways of splitting the 8 + 8 attribute words into two
equal halves (exact permutation test, two-sided), Holm correction over the 6 identities.
The test was defined after the descriptive split of section 2.6 had been seen (post hoc).

    python scripts/03d_legal_moral_permutation.py
Output: results/case_study/e2_legal_moral_test_<model>.csv
"""
from __future__ import annotations

import argparse
import pathlib
import sys

import numpy as np
import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from legalbias import identities as ids  # noqa: E402
from legalbias import seat, stats  # noqa: E402
from legalbias.representations import all_sentences, load_sets  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--model", default="Qwen2.5-1.5B-Instruct")
ap.add_argument("--outdir", default="results/case_study")
a = ap.parse_args()
outdir = ROOT / a.outdir

sets = load_sets()
names, sentences = [], []
for key, group in all_sentences(sets).items():
    names += [key] * len(group)
    sentences += group
names = np.array(names)
saved = np.load(outdir / f"hidden_{a.model}.npz")
if "sentences" not in saved or list(saved["sentences"]) != sentences:
    sys.exit("Hidden-state cache does not match the sentence sets: run scripts/03_run_e2.py first.")
H = saved["H"]

concept = sets["concepts"]["PRE"]
frames = len(sets["attribute_frames"])
legal = sets["pre_split"]["legal"]
obs_neg = [concept["negative"].index(w) for w in legal["negative"]]
obs_pos = [concept["positive"].index(w) for w in legal["positive"]]
word_of = np.repeat(np.arange(len(concept["negative"])), frames)   # sentences are word-major

rows = []
for vid in ids.LGBTQ_IDS:
    cneg, cpos = [], []
    for layer in range(1, H.shape[0]):
        M = seat.standardize(H[layer])
        T = np.vstack([M[names == f"T:{vid}"], M[names == f"T:{ids.ref(vid)}"]])
        cneg.append(seat.word_associations(T, M[names == "A:PRE:neg"], word_of, len(concept["negative"])))
        cpos.append(seat.word_associations(T, M[names == "A:PRE:pos"], word_of, len(concept["positive"])))
    nx = int((names == f"T:{vid}").sum())
    r = seat.split_difference_test(np.stack(cneg), np.stack(cpos), nx, obs_neg, obs_pos)
    rows.append({"model": a.model, "vid": vid, "d_legal": r["d_first"], "d_moral": r["d_second"],
                 "delta_legal_minus_moral": r["delta"], "p": r["p"], "n_splits": r["n_splits"]})

df = pd.DataFrame(rows)
df["p_holm"] = stats.holm(df["p"].to_numpy())
df.to_csv(outdir / f"e2_legal_moral_test_{a.model}.csv", index=False)
print(df.round(3).to_string(index=False))
