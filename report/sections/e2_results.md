## 2.6 Rezultatele E2: asocierile din reprezentările interne

**Corectarea anizotropiei.** Prima rulare a lui E2, cu media stărilor ascunse pe toți tokenii, a produs efecte aproape nule și identice pe straturile 2–25. Cauza este vizibilă în figura de mai jos: cosinusul mediu dintre propoziții fără legătură între ele era practic 1 în aceste straturi. Toate propozițiile erau reprezentate de aproape același vector, dominat de primul token. Primul token are câteva dimensiuni cu valori uriașe [29], [30]: valoarea absolută maximă dintr-un vector este de 34 până la 150 de ori mai mare decât valoarea mediană, chiar și după eliminarea lui din medie. Excluderea primului token reduce cosinusul mediu la 0,64–0,95, iar standardizarea pe dimensiuni îl aduce la aproximativ 0. Toate rezultatele de mai jos folosesc vectori fără primul token, standardizați.

![Cosinusul mediu între propoziții oarecare, pe straturile Qwen2.5-1.5B-Instruct, pentru cele trei moduri de a construi reprezentarea propoziției.](figures/e2_anisotropy.png)

[[include:generated/e2_main.md]]

![Mărimea efectului SEAT pe fiecare strat, pentru cele 6 variante LGBTQ+ (rândul de sus: bărbați, rândul de jos: femei). Punctele marchează straturile cu p < 0,05.](figures/e2_seat_layers.png)

Rezultatele se împart în trei situații:

- **Conceptul vinovat–nevinovat.** Pentru toate cele patru variante explicite (gay, lesbiană, bărbat și femeie bisexuală), efectul este pozitiv pe aproape toate straturile, cu d̄ între +0,81 și +1,09. Este semnificativ în 54–79% din straturi. Termenii de identitate LGBTQ+ sunt deci reprezentați mai aproape de „guilty, immoral, corrupt” decât termenul „heterosexual”. Lista de atribute conține și cuvinte cu sens moral (immoral, wicked, virtuous), iar asocierea lor cu orientarea sexuală corespunde stigmatului istoric descris în Lab I [21].
- **Conceptele periculos–inofensiv și necinstit–credibil.** Efectele sunt tot pozitive, dar mai mici (d̄ între +0,19 și +0,74) și semnificative pe mai puține straturi (0–50%). Ele apar mai ales în straturile din mijloc (10–22), unde modelele de acest tip tind să reprezinte sensul propozițiilor.
- **Testul generic plăcut–neplăcut.** Testul folosit în literatură ca bază de comparație [4], [5] nu găsește aproape nimic: d̄ între −0,24 și +0,11, cu cel mult un strat semnificativ din 28. Un audit care ar folosi doar testul generic ar concluziona că modelul nu asociază identitățile LGBTQ+ cu nimic negativ. Conceptele alese special pentru sarcinile juridice arată însă o asociere puternică. Aceasta este prima dovadă empirică pentru beneficiul B2 din secțiunea 1.6.

Semnalarea implicită produce efecte mai slabe. Pentru „He lives with his husband.” apare un efect pozitiv mic la periculos–inofensiv (d̄ = +0,49, 4 straturi semnificative), iar pentru „She lives with her wife.” efectele sunt practic nule. Modelul reține asocierile mai ales pentru eticheta de identitate, nu pentru situația descrisă.

[[include:generated/e2_robust.md]]

**Robustețea.** Semnul și ordinea efectelor (vinovat–nevinovat > celelalte concepte juridice > valența generică) se păstrează la toate cele trei variante de preprocesare. Pe vectorii bruți și pe cei doar centrați, efectul la vinovat–nevinovat este chiar ceva mai mare. Varianta pe perechi (d_{z}) dă valori mult mai mari, pentru că elimină variația dintre cadre. Pentru că cele 10 cadre sunt foarte asemănătoare între ele, testul sign-flip devine însă foarte permisiv: găsește semnificație și pentru diferențe consecvente, dar foarte mici, inclusiv la testul generic. De aceea, rezultatul principal rămâne SEAT-ul clasic, iar varianta pe perechi este raportată ca analiză suplimentară. În experimentul complet, numărul și diversitatea cadrelor vor fi mărite.
