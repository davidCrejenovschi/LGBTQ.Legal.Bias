"""Hidden-state extraction and the E2 sentence sets."""
from __future__ import annotations

import json
import pathlib

import numpy as np

from . import identities as ids

ROOT = pathlib.Path(__file__).resolve().parents[2]
SEAT_FILE = ROOT / "data" / "templates" / "seat_sets.json"


def load_sets(path: pathlib.Path = SEAT_FILE) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def target_sentences(vid: str, sets: dict) -> list[str]:
    """Sentences that mention identity vid (explicitly or through the partner)."""
    v = ids.BY_ID[vid]
    if v.mode == "explicit":
        term = sets["explicit_terms"][vid]
        return [f.replace("{T}", term) for f in sets["explicit_frames"]]
    if v.mode == "implicit":
        p = ids.pronouns(v.gender)
        out = []
        for f in sets["implicit_frames"]:
            s = f.replace("{S}", ids.spouse(v))
            for k in ("He", "His", "his"):
                s = s.replace("{" + k + "}", p[k])
            out.append(s)
        return out
    raise ValueError("control variants have no target sentences")


def attribute_sentences(words: list[str], frames: list[str]) -> list[str]:
    return [f.replace("{w}", w) for w in words for f in frames]


def all_sentences(sets: dict) -> dict[str, list[str]]:
    """Every sentence set used in E2, keyed by a short name."""
    out: dict[str, list[str]] = {}
    for v in ids.IDENTITIES:
        if v.mode != "control":
            out[f"T:{v.vid}"] = target_sentences(v.vid, sets)
    for task, c in sets["concepts"].items():
        out[f"A:{task}:neg"] = attribute_sentences(c["negative"], sets["attribute_frames"])
        out[f"A:{task}:pos"] = attribute_sentences(c["positive"], sets["attribute_frames"])
    b = sets["baseline"]
    out["A:VAL:neg"] = attribute_sentences(b["negative"], b["frames"])
    out["A:VAL:pos"] = attribute_sentences(b["positive"], b["frames"])
    out["N:neutral"] = list(sets["neutral_reference"])
    return out


class HiddenStateExtractor:
    """Mean-pooled hidden states of every layer for a list of sentences."""

    def __init__(self, model_id: str = "Qwen/Qwen2.5-1.5B-Instruct", device: str | None = None):
        import torch
        from transformers import AutoModel, AutoTokenizer

        self.torch = torch
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.tok = AutoTokenizer.from_pretrained(model_id)
        if self.tok.pad_token is None:
            self.tok.pad_token = self.tok.eos_token
        self.tok.padding_side = "right"
        self.model = AutoModel.from_pretrained(model_id, dtype=torch.float32).to(self.device).eval()
        self.model_id = model_id

    def encode(self, sentences: list[str], batch_size: int = 32) -> np.ndarray:
        """Returns array [n_layers + 1, n_sentences, hidden_dim] (index 0 = embeddings)."""
        torch = self.torch
        chunks = []
        for i in range(0, len(sentences), batch_size):
            enc = self.tok(sentences[i:i + batch_size], return_tensors="pt", padding=True).to(self.device)
            with torch.no_grad():
                out = self.model(**enc, output_hidden_states=True)
            mask = enc["attention_mask"].unsqueeze(-1).float()            # [b, t, 1]
            hs = torch.stack(out.hidden_states)                              # [L+1, b, t, d]
            pooled = (hs * mask.unsqueeze(0)).sum(2) / mask.sum(1).unsqueeze(0)
            chunks.append(pooled.cpu().numpy())
        return np.concatenate(chunks, axis=1)
