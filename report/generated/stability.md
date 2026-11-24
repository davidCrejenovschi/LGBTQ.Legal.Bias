Table: Stabilitatea deciziilor: aceleași 720 de prompturi rulate de două ori. Rata de schimbare fără nicio modificare a promptului este zgomotul de fond al CFR.

| Model | Sarcina | Prompturi | Acord exact | Schimbări fără modificare | Diferența medie | Diferența maximă | CFR (prima rulare, variante LGBTQ+) |
|---|---|---|---|---|---|---|---|
| Llama-3.1-8B | CRED | 240 | 99,6% | 0,4% | 0,008 | 2 | 5%–55% |
| Llama-3.1-8B | PRE | 240 | 96,2% | 3,8% | 0,054 | 2 | 0%–30% |
| Llama-3.1-8B | REC | 240 | 99,6% | 0,4% | 0,004 | 1 | 0%–30% |

Table: Replicarea efectelor E1 pentru Llama-3.1-8B în a doua rulare (prima / a doua). Un efect este replicat doar dacă are același semn și p Holm < 0,05 în ambele rulări.

| Sarcina | Varianta | MSD | p Holm | Replicat |
|---|---|---|---|---|
| REC | gay (expl.) | −0,50 / −0,50 | 0,463 / 0,463 | nu |
| REC | bărbat bisexual (expl.) | −0,30 / −0,30 | 1,000 / 1,000 | nu |
| REC | bărbat cu soț (impl.) | −0,30 / −0,30 | 1,000 / 1,000 | nu |
| REC | lesbiană (expl.) | −0,30 / −0,25 | 1,000 / 1,000 | nu |
| REC | femeie bisexuală (expl.) | −0,10 / −0,05 | 1,000 / 1,000 | nu |
| REC | femeie cu soție (impl.) | 0,00 / 0,00 | 1,000 / 1,000 | nu |
| PRE | gay (expl.) | −0,45 / −0,45 | 0,610 / 0,644 | nu |
| PRE | bărbat bisexual (expl.) | −0,50 / −0,40 | 0,463 / 0,819 | nu |
| PRE | bărbat cu soț (impl.) | −0,25 / −0,25 | 1,000 / 1,000 | nu |
| PRE | lesbiană (expl.) | −0,05 / −0,05 | 1,000 / 1,000 | nu |
| PRE | femeie bisexuală (expl.) | 0,00 / 0,00 | 1,000 / 1,000 | nu |
| PRE | femeie cu soție (impl.) | −0,05 / −0,10 | 1,000 / 1,000 | nu |
| CRED | gay (expl.) | −0,65 / −0,65 | 0,042 / 0,042 | da |
| CRED | bărbat bisexual (expl.) | −0,55 / −0,45 | 0,104 / 0,140 | nu |
| CRED | bărbat cu soț (impl.) | −0,15 / −0,15 | 1,000 / 1,000 | nu |
| CRED | lesbiană (expl.) | −0,65 / −0,65 | 0,042 / 0,042 | da |
| CRED | femeie bisexuală (expl.) | −0,60 / −0,60 | 0,065 / 0,065 | nu |
| CRED | femeie cu soție (impl.) | −0,05 / −0,05 | 1,000 / 1,000 | nu |
