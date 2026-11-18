Table: Pilotul pe date reale: predicția recidivei în 2 ani pe aceleași 60 de dosare COMPAS (eșantion echilibrat, 47 de bărbați). Între paranteze: intervale de încredere bootstrap de 95%.

| Predictor | AUC [IÎ 95%] | Acuratețe | Diferența de AUC față de COMPAS [IÎ 95%] |
|---|---|---|---|
| COMPAS (decile ≥ 5) | 0,68 [0,52; 0,81] | 65% | – |
| Qwen2.5-1.5B (control, scor ≥ 5) | 0,71 [0,57; 0,84] | 68% | [−0,10; +0,16] |
| Llama-3.1-8B (control, scor ≥ 5) | 0,76 [0,63; 0,88] | 70% | [−0,05; +0,22] |

Table: Ratele de eroare pe variante de identitate pe datele COMPAS (prag: scor ≥ 5). Criteriul de separare cere FPR și FNR egale între variante.

| Model | Varianta | AUC | FPR | FNR |
|---|---|---|---|---|
| Qwen2.5-1.5B | heterosexual (expl.) | 0,713 | 23% | 33% |
| Qwen2.5-1.5B | gay / lesbiană (expl.) | 0,722 | 33% | 30% |
| Qwen2.5-1.5B | bisexual (expl.) | 0,700 | 30% | 33% |
| Qwen2.5-1.5B | partener de sex opus (impl.) | 0,714 | 23% | 33% |
| Qwen2.5-1.5B | partener de același sex (impl.) | 0,711 | 17% | 33% |
| Qwen2.5-1.5B | control | 0,708 | 30% | 33% |
| Llama-3.1-8B | heterosexual (expl.) | 0,768 | 30% | 27% |
| Llama-3.1-8B | gay / lesbiană (expl.) | 0,765 | 27% | 27% |
| Llama-3.1-8B | bisexual (expl.) | 0,765 | 30% | 27% |
| Llama-3.1-8B | partener de sex opus (impl.) | 0,768 | 30% | 27% |
| Llama-3.1-8B | partener de același sex (impl.) | 0,759 | 30% | 30% |
| Llama-3.1-8B | control | 0,760 | 33% | 27% |

Table: Diferențele contrafactuale pe dosarele reale (scorul de risc 1–10, comparat cu referința heterosexuală de același gen).

| Model | Varianta | n | CFR | MSD [IÎ 95%] | p Wilcoxon |
|---|---|---|---|---|---|
| Qwen2.5-1.5B | gay (expl.) | 47 | 15% | +0,23 [+0,09; +0,40] | 0,015 |
| Qwen2.5-1.5B | bărbat bisexual (expl.) | 47 | 6% | 0,00 [−0,11; +0,09] | 1,000 |
| Qwen2.5-1.5B | lesbiană (expl.) | 13 | 15% | +0,31 [0,00; +0,85] | 0,500 |
| Qwen2.5-1.5B | femeie bisexuală (expl.) | 13 | 8% | +0,23 [0,00; +0,69] | 1,000 |
| Qwen2.5-1.5B | bărbat cu soț (impl.) | 47 | 11% | −0,13 [−0,26; −0,02] | 0,034 |
| Qwen2.5-1.5B | femeie cu soție (impl.) | 13 | 31% | −0,69 [−1,31; −0,15] | 0,125 |
| Llama-3.1-8B | gay (expl.) | 47 | 26% | −0,32 [−0,49; −0,15] | 0,001 |
| Llama-3.1-8B | bărbat bisexual (expl.) | 47 | 15% | −0,15 [−0,26; −0,06] | 0,008 |
| Llama-3.1-8B | lesbiană (expl.) | 13 | 23% | −0,38 [−0,85; 0,00] | 0,250 |
| Llama-3.1-8B | femeie bisexuală (expl.) | 13 | 0% | 0,00 [0,00; 0,00] | 1,000 |
| Llama-3.1-8B | bărbat cu soț (impl.) | 47 | 9% | −0,11 [−0,23; −0,02] | 0,059 |
| Llama-3.1-8B | femeie cu soție (impl.) | 13 | 0% | 0,00 [0,00; 0,00] | 1,000 |
