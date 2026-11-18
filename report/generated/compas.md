Table: Pilotul pe date reale: capacitatea de a prezice recidiva în 2 ani pe aceleași 31 dosare COMPAS (eșantion echilibrat).

| Predictor | AUC | Acuratețe |
|---|---|---|
| COMPAS (decile ≥ 5) | 0,750 | 68% |
| Llama-3.1-8B (control, scor ≥ 5) | 0,735 | 65% |

Table: Ratele de eroare pe variante de identitate pe datele COMPAS (prag: scor ≥ 5). Criteriul de separare cere FPR și FNR egale între variante.

| Model | Varianta | AUC | FPR | FNR |
|---|---|---|---|---|
| Llama-3.1-8B | heterosexual (expl.) | 0,757 | 38% | 32% |
| Llama-3.1-8B | gay / lesbiană (expl.) | 0,719 | 38% | 32% |
| Llama-3.1-8B | bisexual (expl.) | 0,735 | 38% | 33% |
| Llama-3.1-8B | partener de sex opus (impl.) | 0,731 | 38% | 33% |
| Llama-3.1-8B | partener de același sex (impl.) | 0,735 | 38% | 33% |
| Llama-3.1-8B | control | 0,735 | 38% | 33% |

Table: Diferențele contrafactuale pe dosarele reale (scorul de risc 1–10, comparat cu referința heterosexuală de același gen).

| Model | Varianta | n | CFR | MSD [IÎ 95%] | p Wilcoxon |
|---|---|---|---|---|---|
| Llama-3.1-8B | gay (expl.) | 27 | 26% | −0,33 [−0,56; −0,11] | 0,014 |
| Llama-3.1-8B | bărbat bisexual (expl.) | 27 | 19% | −0,19 [−0,33; −0,04] | 0,025 |
| Llama-3.1-8B | lesbiană (expl.) | 5 | 20% | −0,20 [−0,60; 0,00] | 1,000 |
| Llama-3.1-8B | femeie bisexuală (expl.) | 4 | 0% | 0,00 [0,00; 0,00] | 1,000 |
| Llama-3.1-8B | bărbat cu soț (impl.) | 27 | 4% | −0,04 [−0,11; 0,00] | 0,317 |
| Llama-3.1-8B | femeie cu soție (impl.) | 4 | 0% | 0,00 [0,00; 0,00] | 1,000 |
