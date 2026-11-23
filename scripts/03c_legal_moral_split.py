"""Split the guilty-innocent concept of E2 into legal culpability and moral judgement.

The two halves are disjoint subsets of the original 8 + 8 attribute words, so the sentence
pool, the standardization and the main E2 results stay exactly the same. Requires the
hidden-state cache written by scripts/03_run_e2.py.

    python scripts/03c_legal_moral_split.py
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
from legalbias import seat  # noqa: E402
from legalbias.representations import all_sentences, attribute_sentences, load_sets  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--model", default="Qwen2.5-1.5B-Instruct")
ap.add_argument("--outdir", default="results/case_study")
ap.add_argument("--n-perm", type=int, default=10_000)
a = ap.parse_args()
outdir = ROOT / a.outdir

sets = load_sets()
names, sentences = [], []
for key, group in all_sentences(sets).items():
    names += [key] * len(group)
    sentences += group
names, sent_arr = np.array(names), np.array(sentences)

saved = np.load(outdir / f"hidden_{a.model}.npz")
if "sentences" not in saved or list(saved["sentences"]) != sentences:
    sys.exit("Hidden-state cache does not match the sentence sets: run scripts/03_run_e2.py first.")
H = saved["H"]

frames = sets["attribute_frames"]
masks = {}
for part, spec in sets["pre_split"].items():
    masks[part] = (
        (names == "A:PRE:neg") & np.isin(sent_arr, attribute_sentences(spec["negative"], frames)),
        (names == "A:PRE:pos") & np.isin(sent_arr, attribute_sentences(spec["positive"], frames)),
    )
    assert masks[part][0].sum() == masks[part][1].sum() == 12

rows = []
for layer in range(1, H.shape[0]):
    M = seat.standardize(H[layer])
    for vid in ids.LGBTQ_IDS:
        X, Y = M[names == f"T:{vid}"], M[names == f"T:{ids.ref(vid)}"]
        for part, (neg, pos) in masks.items():
            rows.append({"model": a.model, "layer": layer, "vid": vid, "part": part,
                         "d": seat.effect_size(X, Y, M[neg], M[pos]),
                         "p": seat.permutation_p(X, Y, M[neg], M[pos], n_perm=a.n_perm, seed=layer)})

df = pd.DataFrame(rows)
df.to_csv(outdir / f"e2_legal_moral_{a.model}.csv", index=False)
summary = df.groupby(["vid", "part"]).agg(d_mean=("d", "mean"),
                                          share_sig=("p", lambda p: float(np.mean(p < 0.05))))
print(summary.unstack("part").round(3).to_string())
