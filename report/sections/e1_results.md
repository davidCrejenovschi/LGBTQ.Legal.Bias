## 2.5 Rezultatele E1: diferențele de decizie

Tabelele de mai jos prezintă, pentru fiecare model, sarcină și variantă LGBTQ+, metricile din formulele (3)–(4) față de referința heterosexuală. Figura care urmează le rezumă grafic.

[[include:generated/e1_main.md]]

![Diferența medie de scor (MSD) față de referința heterosexuală, cu intervale de încredere bootstrap de 95%. Valorile negative înseamnă că varianta LGBTQ+ a fost tratată mai favorabil.](figures/e1_msd_forest.png)

**Llama-3.1-8B-Instruct.** Cel mai clar rezultat al studiului de caz este că Llama tratează *mai favorabil* persoanele numite explicit gay, lesbiene sau bisexuale. La credibilitatea martorului, scorul crește cu 0,55–0,65 puncte. Decizia se schimbă în 45–55% din perechi, toate schimbările fiind în favoarea variantei LGBTQ+ (CFR⁺ = 0%). Pentru „gay” și „lesbiană”, efectul rămâne semnificativ și după corecția Holm pentru 24 de teste (p = 0,042). La riscul de recidivă, direcția este aceeași (scoruri mai mici cu 0,1–0,5 puncte), dar efectele nu trec de corecția Holm. Când orientarea este doar sugerată prin partener, efectul aproape dispare: MSD între −0,30 și 0 la toate sarcinile, fără niciun rezultat semnificativ. La măsura preventivă, cele 12 variante au primit exact aceeași decizie pentru fiecare scenariu, iar rata privării de libertate este de 65% pentru toate variantele (tabelul de mai jos).

[[include:sections/e1_qwen.md]]

[[include:generated/e1_pre.md]]

**Cine se abate de la comportamentul obișnuit.** Tabelul următor compară fiecare variantă, inclusiv cele heterosexuale, cu varianta de control, în care orientarea nu este menționată. La Llama, pentru credibilitate, variantele heterosexuale nu diferă de control (MSD între −0,10 și +0,10), în timp ce variantele LGBTQ+ explicite se abat toate cu 0,50–0,65 puncte. Abaterea vine deci de la grupul LGBTQ+, nu de la referință. La riscul de recidivă, simpla menționare a orientării scade scorul și pentru heterosexuali (−0,2 la bărbați, −0,5 la femei), dar efectul este mai mare pentru variantele LGBTQ+ (până la −0,8). La Qwen, pentru credibilitate, ambele grupuri se abat de la control, dar în direcții opuse. Martorii numiți explicit heterosexuali sunt considerați *mai puțin* credibili decât cei fără orientare menționată (+0,35), iar cei numiți explicit LGBTQ+ mai credibili (−0,15 până la −0,35). Diferența dintre grupuri apare deci din ambele părți.

[[include:generated/e1_control.md]]

**Ipoteza H1b.** Lab III a prezis că diferența în defavoarea persoanelor LGBTQ+ va fi mai mare în varianta implicită. Tabelul următor arată că, la Llama, D este pozitiv și semnificativ pentru credibilitate (+0,50 și +0,60, p < 0,01). Explicația este însă alta decât cea prezisă. Varianta implicită nu este tratată mai rău decât referința. În schimb, avantajul pe care modelul îl acordă persoanelor numite explicit LGBTQ+ dispare când orientarea este doar sugerată. Formal, inegalitatea E[D] > 0 este îndeplinită, dar H1a (un dezavantaj față de referință) nu este susținută de datele studiului de caz. Qwen are același tipar la credibilitate (D = +0,50 și +0,40, p ≈ 0,06). La riscul de recidivă apare tiparul opus (D = −0,40 pentru bărbați, p = 0,038), pentru că varianta implicită primește un scor *mai mic* decât cea explicită.

[[include:generated/h1b.md]]

Acest tipar seamănă cu ce au găsit Hofmann et al. [2] pentru dialect: modelele aliniate prin feedback uman corectează, chiar cu exces, atitudinea față de un grup atunci când grupul este numit explicit, dar nu și atunci când apartenența la grup este doar sugerată. Studiul de caz nu poate spune dacă supracorecția explicită este dezirabilă. Din punct de vedere juridic, ea este tot o încălcare a corectitudinii contrafactuale: un martor nu ar trebui să fie considerat mai credibil pentru că este gay.
