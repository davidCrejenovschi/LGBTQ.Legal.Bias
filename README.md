# Bias Against Sexual Minorities in LLMs Applied to Legal Tasks

Counterfactual evaluation of sexual-orientation bias in large language models on three
legal tasks (recidivism risk, pretrial measure, witness credibility), plus an analysis of
the models' hidden representations (WEAT/SEAT per layer) and of the link between the two.

Research project, Lab 5–8 (applied part). The report is `docs/IV.docx`, generated from the
Markdown sources in `report/`.

## Layout

| Path | Content |
|---|---|
| `src/legalbias/` | library: identities, scenario generator, prompts, parsing, model clients, metrics, statistics, SEAT, hidden states, COMPAS |
| `data/templates/` | scenario templates (JSON) for REC / PRE / CRED and the SEAT sentence sets |
| `data/case_study/prompts.jsonl` | 720 counterfactual prompts of the case study (60 scenarios × 12 variants) |
| `data/compas/prompts.jsonl` | 360 prompts built from 60 real COMPAS records × 6 variants |
| `scripts/` | numbered pipeline steps (see below) |
| `results/` | raw model answers (JSONL) and analysis tables (CSV/JSON) |
| `report/` | report chapters (Markdown), generated tables, figures, `build_report.py` |
| `tests/` | unit tests (pytest), run by GitHub Actions on every push |
| `docs/` | the Lab 5–8 report `IV.docx`, previous labs `I.docx`–`III.docx` (topic, literature analysis, outline and plan) and the assignment `Lab5_8.pdf` |

## Reproducing the case study

```bash
pip install -r requirements.txt
python scripts/download_assets.py                      # Qwen2.5-1.5B-Instruct + COMPAS csv
ollama pull llama3.1                                   # Llama-3.1-8B-Instruct, Q4 (GPU)

python scripts/01_generate_prompts.py                  # templates -> 720 prompts (+ invariance check)
python scripts/02_run_e1.py --model ollama:llama3.1:latest --pilot 9   # pilot: answer format
python scripts/02_run_e1.py --model ollama:llama3.1:latest             # E1
python scripts/02_run_e1.py --model hf:Qwen/Qwen2.5-1.5B-Instruct      # E1 (CPU)
python scripts/03_run_e2.py                            # E2: hidden states + SEAT per layer
python scripts/03b_massive_activations.py              # first-token massive activations (why it is excluded)
python scripts/04_compas_prompts.py --n 60             # real data: COMPAS -> prompts
python scripts/02_run_e1.py --model ollama:llama3.1:latest --prompts data/compas/prompts.jsonl --outdir results/compas/e1_raw
python scripts/02_run_e1.py --model hf:Qwen/Qwen2.5-1.5B-Instruct --prompts data/compas/prompts.jsonl --outdir results/compas/e1_raw
python scripts/05_analyze.py                           # E1 tables, H1b, manipulation check, E3, COMPAS
python scripts/06_figures.py                           # figures
python scripts/07_report_tables.py                     # tables for the report
python report/build_report.py                          # -> docs/IV.docx
python -m pytest -q                                    # unit tests
```

Commercial models (full study): `--model openai:<model>`, `--model anthropic:<model>`
with `OPENAI_API_KEY` / `ANTHROPIC_API_KEY` set, and `--reps 3`.
