"""legalbias - counterfactual audit of sexual-orientation bias in LLM legal decisions.

Modules
-------
identities      the 12 identity variants and the reference mapping ref(v)
scenarios       scenario templates, slot filling, counterfactual rendering
prompts         task instructions with a fixed answer format
parsing         extraction of the decision from the raw answer, refusal detection
models          clients: Ollama, Hugging Face (local), OpenAI-compatible, Anthropic
runner          resumable querying loop, JSONL storage
metrics         CFR, RD, DIR, mean signed harm, refusal gap
stats           Wilcoxon, McNemar (exact), Holm, bootstrap CI, rank-biserial
seat            WEAT/SEAT effect size, exact/permutation test, centering
representations hidden-state extraction (mean pooling, all layers)
compas          real recidivism records (ProPublica COMPAS) -> scenarios
analysis        E1/E2/E3 aggregation
"""

__version__ = "0.1.0"
