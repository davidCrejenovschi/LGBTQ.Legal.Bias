"""Download the external assets used by the experiments.

* Qwen/Qwen2.5-1.5B-Instruct (Hugging Face, Apache-2.0) -> local HF cache.
  Used for E1 (decisions) and E2 (hidden states) on CPU.
* COMPAS two-year recidivism data (ProPublica, 2016) -> data/real/compas/.
  Used to build recidivism scenarios from real defendant records
  (same data as Dressel & Farid, 2018).

Usage:
    python scripts/download_assets.py [--qwen] [--compas]
"""
from __future__ import annotations

import argparse
import pathlib
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
COMPAS_URL = (
    "https://raw.githubusercontent.com/propublica/compas-analysis/"
    "master/compas-scores-two-years.csv"
)
QWEN_ID = "Qwen/Qwen2.5-1.5B-Instruct"


def download_compas() -> pathlib.Path:
    out = ROOT / "data" / "real" / "compas" / "compas-scores-two-years.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    if out.exists():
        print(f"COMPAS already present: {out}")
        return out
    print(f"Downloading {COMPAS_URL}")
    urllib.request.urlretrieve(COMPAS_URL, out)
    print(f"Saved {out} ({out.stat().st_size / 1e6:.2f} MB)")
    return out


def download_qwen() -> str:
    from huggingface_hub import snapshot_download

    path = snapshot_download(
        QWEN_ID,
        allow_patterns=["*.json", "*.safetensors", "*.txt", "merges.txt", "vocab.json"],
    )
    print(f"{QWEN_ID} -> {path}")
    return path


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--qwen", action="store_true")
    ap.add_argument("--compas", action="store_true")
    a = ap.parse_args()
    if not (a.qwen or a.compas):
        a.qwen = a.compas = True
    if a.compas:
        download_compas()
    if a.qwen:
        download_qwen()
