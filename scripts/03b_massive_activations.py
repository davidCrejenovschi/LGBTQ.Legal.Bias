"""Documents the 'massive activations' of the first token (Sun et al., 2024) that
motivate excluding it from mean pooling in E2.

For every SEAT sentence and layers 4 / 14 / 24: the largest absolute hidden-state
value of the first token and of the remaining tokens, divided by the median
absolute value of the sentence. Output: results/case_study/e2_massive_activations.csv
"""
from __future__ import annotations

import pathlib
import sys

import numpy as np
import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from legalbias.representations import all_sentences, load_sets  # noqa: E402

MODEL = "Qwen/Qwen2.5-1.5B-Instruct"


def main():
    import torch
    from transformers import AutoModel, AutoTokenizer

    tok = AutoTokenizer.from_pretrained(MODEL)
    model = AutoModel.from_pretrained(MODEL, dtype=torch.float32).eval()
    rows = []
    for name, sents in all_sentences(load_sets()).items():
        for s in sents:
            enc = tok(s, return_tensors="pt")
            with torch.no_grad():
                hs = model(**enc, output_hidden_states=True).hidden_states
            for layer in (4, 14, 24):
                H = hs[layer][0].abs()
                med = H.median().item()
                rows.append({"set": name, "sentence": s, "layer": layer,
                             "first_token_ratio": H[0].max().item() / med,
                             "other_tokens_ratio": H[1:].max().item() / med})
    df = pd.DataFrame(rows)
    out = ROOT / "results" / "case_study" / "e2_massive_activations.csv"
    df.to_csv(out, index=False)
    print(df.groupby("layer")[["first_token_ratio", "other_tokens_ratio"]]
          .agg(["min", "median", "max"]).round(0).to_string())
    print(f"overall: first token {np.min(df.first_token_ratio):.0f}-{np.max(df.first_token_ratio):.0f}x, "
          f"other tokens {np.min(df.other_tokens_ratio):.0f}-{np.max(df.other_tokens_ratio):.0f}x")


if __name__ == "__main__":
    main()
