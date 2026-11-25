"""Resumable querying loop. Each answer is appended to a JSONL file together
with the scenario, the identity variant and the model (Lab III, step 4)."""
from __future__ import annotations

import json
import pathlib
import time

from .parsing import parse
from .prompts import build_messages


def load_jsonl(path: pathlib.Path) -> list[dict]:
    if not path.exists():
        return []
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def run(client, prompts: list[dict], out_path: pathlib.Path, repetitions: int = 1,
        progress_every: int = 50, paraphrase: int = 0) -> None:
    """paraphrase: 0 = original task instruction, k = k-th alternative wording."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    done = {(r["pid"], r["rep"]) for r in load_jsonl(out_path)}
    todo = [(p, rep) for p in prompts for rep in range(repetitions) if (p["pid"], rep) not in done]
    print(f"[{client.name}] {len(done)} done, {len(todo)} to go -> {out_path}", flush=True)
    t0 = time.time()
    with open(out_path, "a", encoding="utf-8") as f:
        for i, (p, rep) in enumerate(todo, 1):
            t = time.time()
            try:
                raw = client.chat(build_messages(p["task"], p["scenario"], paraphrase))
                err = None
            except Exception as e:  # network / runtime error: store and continue
                raw, err = None, repr(e)
            value, status = parse(p["task"], raw)
            if err:
                status = "error"
            rec = {**p, "model": client.name, "rep": rep, "raw": raw, "value": value,
                   "status": status, "latency_s": round(time.time() - t, 3)}
            if err:
                rec["error"] = err
            if paraphrase:
                rec["paraphrase"] = paraphrase
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            f.flush()
            if i % progress_every == 0:
                rate = (time.time() - t0) / i
                print(f"  {i}/{len(todo)}  {rate:.2f}s/prompt  eta {rate * (len(todo) - i) / 60:.1f} min",
                      flush=True)
    print(f"[{client.name}] finished in {(time.time() - t0) / 60:.1f} min", flush=True)
