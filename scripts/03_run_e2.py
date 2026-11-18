"""Steps 6-8: experiment E2 - associations in the representation space.

For every layer l, every LGBTQ+ identity v (vs. its heterosexual reference)
and every concept pair (task-aligned + generic valence baseline):
SEAT effect size d_l and one-sided permutation p-value, with and without
centering (anisotropy correction).

    python scripts/03_run_e2.py --model Qwen/Qwen2.5-1.5B-Instruct
"""
from __future__ import annotations

import argparse
import pathlib
import sys
import time

import numpy as np
import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from legalbias import identities as ids  # noqa: E402
from legalbias import seat  # noqa: E402
from legalbias.representations import HiddenStateExtractor, all_sentences, load_sets  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--model", default="Qwen/Qwen2.5-1.5B-Instruct")
ap.add_argument("--outdir", default="results/case_study")
ap.add_argument("--n-perm", type=int, default=10_000)
a = ap.parse_args()
outdir = ROOT / a.outdir
outdir.mkdir(parents=True, exist_ok=True)
tag = a.model.split("/")[-1]

sets = load_sets()
groups = all_sentences(sets)
names, sentences = [], []
for k, v in groups.items():
    names += [k] * len(v)
    sentences += v
names = np.array(names)
print(f"{len(sentences)} sentences in {len(groups)} sets")

_extractor = None


def extractor():
    global _extractor
    if _extractor is None:
        _extractor = HiddenStateExtractor(a.model)
    return _extractor


def hidden(skip_first: bool) -> np.ndarray:
    cache = outdir / f"hidden_{tag}{'' if skip_first else '_withfirst'}.npz"
    if cache.exists():
        saved = np.load(cache)
        # reuse the cache only if it was computed for exactly the same sentences
        if "sentences" in saved and list(saved["sentences"]) == sentences:
            return saved["H"]
        print(f"cache {cache.name} is stale (sentence sets changed) - recomputing")
    t = time.time()
    H_ = extractor().encode(sentences, skip_first=skip_first)
    np.savez_compressed(cache, H=H_, sentences=np.array(sentences))
    print(f"hidden states {H_.shape} (skip_first={skip_first}) in {time.time() - t:.1f}s")
    return H_


H = hidden(skip_first=True)
H_first = hidden(skip_first=False)   # only to document the anisotropy problem
n_layers = H.shape[0] - 1

concepts = {t: (f"A:{t}:neg", f"A:{t}:pos") for t in ("REC", "PRE", "CRED")}
concepts["VAL"] = ("A:VAL:neg", "A:VAL:pos")

rows, aniso = [], []
for layer in range(1, n_layers + 1):
    raw = H[layer]
    reps = {"raw": raw, "centered": seat.center(raw), "standardized": seat.standardize(raw)}
    aniso.append({"layer": layer, **{f"anisotropy_{k}": seat.anisotropy(M) for k, M in reps.items()},
                  "anisotropy_with_first_token": seat.anisotropy(H_first[layer]),
                  "max_dim_over_median": float(np.abs(raw).max() / np.median(np.abs(raw)))})
    for rep_name, M in reps.items():
        for vid in ids.LGBTQ_IDS:
            X = M[names == f"T:{vid}"]
            Y = M[names == f"T:{ids.ref(vid)}"]
            for concept, (neg, pos) in concepts.items():
                A, B = M[names == neg], M[names == pos]
                dz, p_paired = seat.paired_effect(X, Y, A, B)
                rows.append({
                    "model": tag, "layer": layer, "rep": rep_name, "vid": vid,
                    "concept": concept, "d": seat.effect_size(X, Y, A, B),
                    "p": seat.permutation_p(X, Y, A, B, n_perm=a.n_perm, seed=layer),
                    "dz": dz, "p_paired": p_paired,
                })
    if layer % 7 == 0:
        print(f"  layer {layer}/{n_layers} done", flush=True)

df = pd.DataFrame(rows)
df.to_csv(outdir / f"e2_seat_{tag}.csv", index=False)
pd.DataFrame(aniso).to_csv(outdir / f"e2_anisotropy_{tag}.csv", index=False)
for rep_name in reps:
    summary = (df[df.rep == rep_name].groupby(["vid", "concept"])
               .agg(d_mean=("d", "mean"), dz_mean=("dz", "mean"),
                    share_sig=("p", lambda p: float(np.mean(p < 0.05)))).round(3))
    print(f"--- {rep_name}\n{summary.unstack('concept').to_string()}")
