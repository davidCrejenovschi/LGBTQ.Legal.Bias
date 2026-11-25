# 4. Repository-ul de cod și istoricul modificărilor

Codul, datele de intrare, răspunsurile brute ale modelelor, tabelele de rezultate și sursele acestui document sunt păstrate într-un repository git. Textul raportului este scris în fișiere Markdown (`report/*.md`), din care documentul .docx este generat automat (`python report/build_report.py`). Astfel, fiecare modificare a textului apare în istoric ca diferență de text, nu doar ca fișier binar modificat. Tabelele cu rezultate din capitolul 2 sunt generate direct din fișierele CSV (`scripts/07_report_tables.py`), deci nu pot apărea diferențe între cifrele din raport și cele calculate.

Table: Structura repository-ului.

| Director / fișier | Conținut |
|---|---|
| `docs/` | acest raport (`IV.docx`, generat), rapoartele Lab I–III și cerința Lab 5–8 |
| `src/legalbias/` | biblioteca proiectului: variante de identitate, generatorul de scenarii, prompturi, extragerea deciziei, clienți pentru modele, metrici, teste statistice, SEAT, stări ascunse, COMPAS |
| `data/templates/` | șabloanele scenariilor (JSON) pentru REC, PRE și CRED și seturile de propoziții pentru E2 |
| `data/case_study/`, `data/compas/` | prompturile generate pentru studiul de caz (720) și pentru pilotul pe date reale (360) |
| `scripts/01_…07_` | pașii metodologiei, numerotați în ordinea rulării |
| `results/` | răspunsurile brute (JSONL, câte un rând pentru fiecare prompt) și tabelele de analiză (CSV, JSON) |
| `report/` | capitolele raportului (Markdown), tabelele și figurile generate, scriptul care produce .docx |
| `tests/` | 59 de teste unitare (pytest) |
| `.github/workflows/tests.yml` | integrare continuă: testele rulează automat pe GitHub la fiecare `push` |

Rularea completă a studiului de caz, de la șabloane la document, se face cu următoarele comenzi:

> python scripts/download_assets.py            # Qwen2.5-1.5B-Instruct + COMPAS + CrowS-Pairs
> python scripts/01_generate_prompts.py        # 720 de prompturi + verificarea invarianței
> python scripts/02b_calibrate_control.py --task PRE --model ollama:llama3.1:latest   # calibrare pe control
> python scripts/02_run_e1.py --model ollama:llama3.1:latest
> python scripts/02_run_e1.py --model hf:Qwen/Qwen2.5-1.5B-Instruct
> python scripts/03_run_e2.py                  # stări ascunse + SEAT pe straturi
> python scripts/03b_massive_activations.py    # activările masive ale primului token
> python scripts/03c_legal_moral_split.py      # vinovăție juridică vs. judecată morală
> python scripts/03d_legal_moral_permutation.py   # testul exact al diferenței juridic–moral
> python scripts/04_compas_prompts.py --n 60   # date reale
> python scripts/02_run_e1.py --model ollama:llama3.1:latest --prompts data/compas/prompts.jsonl --outdir results/compas/e1_raw
> python scripts/02_run_e1.py --model hf:Qwen/Qwen2.5-1.5B-Instruct --prompts data/compas/prompts.jsonl --outdir results/compas/e1_raw
> python scripts/05_analyze.py                 # E1, H1b, verificarea de manipulare, E3, COMPAS
> python scripts/05b_stability.py              # stabilitatea deciziilor între două rulări
> python scripts/05c_paraphrase.py             # robustețea la formularea instrucțiunii (CRED)
> python scripts/08_crows_pairs.py             # CrowS-Pairs (orientare sexuală) pe Qwen
> python scripts/06_figures.py
> python scripts/07_report_tables.py
> python report/build_report.py                # docs/IV.docx
> python -m pytest -q

**Testele automate** acoperă: generarea deterministă a scenariilor și invarianța contrafactuală (inclusiv un test care verifică faptul că o modificare în afara cuvintelor de identitate este detectată), extragerea deciziei și detectarea refuzurilor, metricile (direcția semnului pentru fiecare sarcină, ratele de privare de libertate, RD, DIR, eliminarea perechilor incomplete), testele statistice (corecția Holm, McNemar exact, rang-biserial și Wilcoxon pe valori calculate de mână, bootstrap, puterea minimă detectabilă, Spearman), testele SEAT (semnul efectului, testul de permutare, varianta pe perechi, centrarea și standardizarea) conversia dosarelor COMPAS în scenarii, compararea a două rulări (stabilitate și replicare) scorarea CrowS-Pairs, parafrazările instrucțiunii și testul exact pentru împărțirea cuvintelor în jumătăți.

**Istoricul modificărilor.** Tabelul de mai jos este generat din `git log` la momentul producerii documentului.

[[include:generated/git_log.md]]
