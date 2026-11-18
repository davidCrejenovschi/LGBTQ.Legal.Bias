"""Model clients f_M : prompt -> answer text.

All clients expose `chat(messages) -> str` and a `name`. Decoding is greedy /
temperature 0 everywhere (Lab III: open-weights models run once, commercial
APIs three times per prompt).
"""
from __future__ import annotations

import json
import os
import urllib.request


def _post(url: str, body: dict, headers: dict | None = None, timeout: int = 600) -> dict:
    req = urllib.request.Request(url, data=json.dumps(body).encode("utf-8"),
                                 headers={"Content-Type": "application/json", **(headers or {})})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())


class OllamaClient:
    """Local model served by Ollama (GGUF, 4-bit quantised, GPU)."""

    def __init__(self, model: str = "llama3.1:latest", host: str = "http://localhost:11434",
                 max_tokens: int = 24, seed: int = 0):
        self.model, self.host, self.max_tokens, self.seed = model, host, max_tokens, seed
        self.name = f"ollama/{model}"

    def chat(self, messages: list[dict]) -> str:
        r = _post(f"{self.host}/api/chat", {
            "model": self.model, "messages": messages, "stream": False,
            "options": {"temperature": 0, "seed": self.seed, "num_predict": self.max_tokens},
        })
        return r["message"]["content"]


class HFClient:
    """Local Hugging Face model (transformers), greedy decoding.
    Also gives access to hidden states (see representations.py)."""

    def __init__(self, model_id: str = "Qwen/Qwen2.5-1.5B-Instruct", max_tokens: int = 24,
                 device: str | None = None, threads: int | None = None):
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer

        if threads:
            torch.set_num_threads(threads)
        self.torch = torch
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.tok = AutoTokenizer.from_pretrained(model_id)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_id, dtype=torch.float32 if self.device == "cpu" else torch.float16
        ).to(self.device).eval()
        self.max_tokens = max_tokens
        self.name = f"hf/{model_id.split('/')[-1]}"

    def chat(self, messages: list[dict]) -> str:
        torch = self.torch
        text = self.tok.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        enc = self.tok(text, return_tensors="pt").to(self.device)
        with torch.no_grad():
            out = self.model.generate(**enc, max_new_tokens=self.max_tokens, do_sample=False,
                                      temperature=None, top_p=None, top_k=None,
                                      pad_token_id=self.tok.eos_token_id)
        return self.tok.decode(out[0, enc["input_ids"].shape[1]:], skip_special_tokens=True)


class OpenAICompatibleClient:
    """OpenAI chat-completions API (also usable for Gemini through its
    OpenAI-compatible endpoint). Not exercised in the case study (no API key)."""

    def __init__(self, model: str, base_url: str = "https://api.openai.com/v1",
                 api_key_env: str = "OPENAI_API_KEY", max_tokens: int = 24):
        self.model, self.base_url, self.max_tokens = model, base_url.rstrip("/"), max_tokens
        self.api_key = os.environ.get(api_key_env, "")
        self.name = f"api/{model}"

    def chat(self, messages: list[dict]) -> str:
        r = _post(f"{self.base_url}/chat/completions",
                  {"model": self.model, "messages": messages, "temperature": 0,
                   "max_tokens": self.max_tokens},
                  headers={"Authorization": f"Bearer {self.api_key}"})
        return r["choices"][0]["message"]["content"]


class AnthropicClient:
    """Anthropic Messages API. Not exercised in the case study (no API key)."""

    def __init__(self, model: str, api_key_env: str = "ANTHROPIC_API_KEY", max_tokens: int = 24):
        self.model, self.max_tokens = model, max_tokens
        self.api_key = os.environ.get(api_key_env, "")
        self.name = f"api/{model}"

    def chat(self, messages: list[dict]) -> str:
        system = "\n".join(m["content"] for m in messages if m["role"] == "system")
        msgs = [m for m in messages if m["role"] != "system"]
        r = _post("https://api.anthropic.com/v1/messages",
                  {"model": self.model, "system": system, "messages": msgs,
                   "temperature": 0, "max_tokens": self.max_tokens},
                  headers={"x-api-key": self.api_key, "anthropic-version": "2023-06-01"})
        return "".join(b.get("text", "") for b in r["content"])


def make_client(spec: str, **kw):
    """'ollama:llama3.1:latest' | 'hf:Qwen/Qwen2.5-1.5B-Instruct' |
    'openai:<model>' | 'anthropic:<model>'"""
    kind, _, model = spec.partition(":")
    if kind == "ollama":
        return OllamaClient(model, **kw)
    if kind == "hf":
        return HFClient(model, **kw)
    if kind == "openai":
        return OpenAICompatibleClient(model, **kw)
    if kind == "anthropic":
        return AnthropicClient(model, **kw)
    raise ValueError(f"unknown model spec {spec!r}")
