# 2. Studiu de caz pe date inițiale

## 2.1 Scopul și configurația

Studiul de caz rulează întreaga metodologie din capitolul 1 pe un set mic de date, cu trei scopuri: să verifice că fiecare pas funcționează de la un capăt la altul, să ilustreze pe exemple concrete ce poate măsura abordarea propusă și să ofere estimări pentru dimensionarea experimentului complet. Nu are ca scop testarea definitivă a ipotezelor. Cu 20 de scenarii pe sarcină, doar efectele mari pot fi detectate (secțiunea 1.4).

Table: Configurația studiului de caz.

| Element | Valoare |
|---|---|
| Scenarii | 3 sarcini × 5 șabloane × 4 completări = 60 de scenarii |
| Prompturi | 60 de scenarii × 12 variante de identitate = 720 pe model |
| Modele | Llama-3.1-8B-Instruct [32], cuantizat pe 4 biți (Q4, Ollama, GPU) – E1; Qwen2.5-1.5B-Instruct [31] (Hugging Face Transformers, CPU, float32) – E1, E2, E3 |
| Decodare | temperatura 0 (greedy), cel mult 24 de tokeni generați, o singură rulare |
| Date reale | 60 de dosare COMPAS (30 cu recidivă, 30 fără) × 6 variante = 360 de prompturi pe model |
| E2 | 302 propoziții, stări ascunse din toate cele 28 de straturi ale Qwen2.5-1.5B-Instruct |
| Hardware | laptop cu GPU NVIDIA RTX 5050 (8 GB), 24 GB RAM, Windows 11 |

Modelele comerciale (GPT, Gemini, Claude) nu au fost incluse în studiul de caz. Clienții pentru API-urile lor sunt implementați (`src/legalbias/models.py`) și vor fi folosiți în experimentul complet. Al doilea model open-weights este mai mic decât cele planificate (1,5 miliarde de parametri, nu 7–9), pentru că trebuie rulat pe CPU ca să-i putem extrage stările ascunse. Versiunea de PyTorch instalată rulează doar pe CPU. Llama-3.1-8B-Instruct corespunde modelelor planificate, dar este servit prin Ollama, care nu oferă acces la stările ascunse, așa că pentru el a fost rulat doar E1.

## 2.2 Implementarea

Codul este organizat ca o bibliotecă Python (`src/legalbias`) și o serie de scripturi numerotate în ordinea pașilor din metodologie (tabelul de mai jos).

Table: Modulele bibliotecii și rolul lor.

| Modul | Rol | Pas din metodologie |
|---|---|---|
| `identities.py` | cele 12 variante de identitate, ref(v), ctrl(v), lexiconul de identitate | 2 |
| `scenarios.py` | încărcarea șabloanelor, generarea scenariilor, redarea r(s, v), verificarea invarianței (1) | 1, 2 |
| `prompts.py`, `parsing.py` | instrucțiunile cu format fix, extragerea deciziei și detectarea refuzurilor | 3, 4 |
| `models.py`, `runner.py` | clienți pentru Ollama, Hugging Face, OpenAI/Gemini, Anthropic; interogare cu reluare după întrerupere | 4 |
| `metrics.py`, `stats.py` | formulele (2)–(8), Wilcoxon, McNemar exact, Holm, bootstrap, Spearman cu permutări | 5, 9 |
| `representations.py`, `seat.py` | extragerea stărilor ascunse (9), formulele (10)–(13), anizotropia | 6, 7, 8 |
| `compas.py` | filtrarea setului COMPAS, eșantionarea, conversia dosarelor în scenarii, AUC | validare |

Fiecare răspuns este salvat ca un rând JSON care conține scenariul, varianta, modelul, textul brut, decizia extrasă, starea (corect, refuz, neinterpretabil) și timpul de răspuns. Dacă rularea este întreruptă, ea continuă de unde a rămas. Răspunsurile brute sunt păstrate în repository (`results/*/e1_raw/*.jsonl`), astfel încât toate tabelele de mai jos pot fi recalculate fără a interoga din nou modelele.

## 2.3 Experimentul-pilot și calitatea răspunsurilor

Înainte de rularea completă, 9 scenarii (3 pe sarcină, adică 108 prompturi) au fost trimise ambelor modele, pentru a verifica dacă răspunsurile respectă formatul cerut (pasul 3 din metodologie). Ambele modele au răspuns corect la toate cele 108 prompturi, așa că instrucțiunile au fost păstrate neschimbate. Tabelul de mai jos arată calitatea răspunsurilor în rularea completă.

[[include:generated/status.md]]

Niciun model nu a refuzat vreo sarcină. Toate răspunsurile au putut fi extrase automat, deci metricile din E1 sunt calculate pe toate cele 20 de perechi de scenarii din fiecare comparație. Determinismul a fost verificat comparând răspunsurile din pilot cu cele din rularea completă pentru aceleași prompturi: [[include:generated/determinism.md]] Diferențele rare la Llama provin din calculele în virgulă mobilă pe GPU, care nu sunt perfect reproductibile nici la temperatura 0. Pentru experimentul complet, fiecare prompt va fi rulat de două ori și vor fi raportate răspunsurile care diferă.

## 2.4 Verificarea de manipulare

Înainte de a interpreta diferențele dintre identități, trebuie verificat că modelele iau decizii juridice cu sens, adică reacționează la factorii relevanți juridic (secțiunea 1.5).

[[include:generated/manip.md]]

![Decizia medie pe nivelurile factorului juridic manipulat, pe variantele de control (bare: interval de încredere de 95%).](figures/e1_manipulation_check.png)

Ambele modele trec verificarea pentru toate sarcinile, cu corelații între 0,69 și 0,92. Scorul de risc crește odată cu antecedentele, măsura preventivă devine mai severă când riscul de sustragere crește, iar credibilitatea scade când declarațiile martorului se contrazic. Rezultatul confirmă că scenariile au fost construite corect: modelele „citesc” faptele juridice, deci o eventuală lipsă a efectului de identitate nu se datorează unor răspunsuri aleatoare.

Verificarea a scos la iveală și o problemă de construcție. La sarcina PRE, ambele modele aleg aproape mereu arestarea preventivă (5) imediat ce apare un factor de risc. Media este 5,0 la nivelurile 1 și 2, deci deciziile ating plafonul scalei. Cât timp o decizie este deja la maxim, o eventuală prejudecată nu o mai poate face mai severă, iar sensibilitatea lui E1 pentru această sarcină este redusă. Corectarea este descrisă în secțiunea 2.10.

[[include:sections/e1_results.md]]

[[include:sections/e2_results.md]]

[[include:sections/e3_compas_discussion.md]]
