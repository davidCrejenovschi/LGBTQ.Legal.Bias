## 2.7 Rezultatele E3: legătura dintre reprezentări și decizii

Pentru Qwen2.5-1.5B-Instruct, singurul model cu rezultate la ambele niveluri, cele 3 sarcini × 6 variante dau 18 puncte. Fiecare punct leagă asocierea medie din reprezentări pentru conceptul sarcinii (d̄) de diferența normalizată de decizie (nMSD).

[[include:generated/e3.md]]

![Legătura dintre asocierile din reprezentări (E2) și diferențele de decizie (E1) pentru Qwen2.5-1.5B-Instruct. Stânga: conceptul aliniat pe sarcină; dreapta: testul generic de valență.](figures/e3_scatter.png)

Corelația este pozitivă pentru conceptele aliniate pe sarcini (ρ = +0,45) și ușor negativă pentru testul generic (ρ = −0,09), deci în direcția prezisă de ipoteza ρ > ρ_{VAL}. Rezultatul este la limită și nu trebuie supra-interpretat: testul de permutare nu este semnificativ (p = 0,064), deși intervalul bootstrap [+0,03; +0,75] exclude abia zero, iar corelațiile din interiorul fiecărei sarcini (6 puncte) au semne diferite. Valoarea este și instabilă: a crescut de la +0,35 la +0,45 doar prin refacerea scenariilor PRE, deși Qwen rămâne la plafon la această sarcină. Cu 18 puncte și un singur model, studiul de caz nu poate decide RQ3.

Figura arată și un rezultat calitativ important: cele două niveluri sunt disociate. Cea mai puternică asociere din reprezentări (identitățile LGBTQ+ explicite apropiate de „vinovat, imoral”, d̄ ≈ 0,8–1,1) apare la sarcina PRE, unde deciziile lui Qwen aproape nu se schimbă, pentru că rămân la plafon. La credibilitate, reprezentările apropie identitățile explicite de „necinstit” (d̄ între +0,19 și +0,48), dar deciziile merg în direcția opusă: aceleași persoane sunt considerate *mai* credibile. Asocierile negative există deci în model, dar nu ajung în decizia cerută în format fix, sau sunt compensate de antrenarea de tip instruct. Rezultatul este în acord cu Goldfarb-Tarrant et al. [16] și cu distincția dintre prejudecățile ascunse și cele declarate a lui Hofmann et al. [2]. El arată și de ce analiza pe două niveluri este utilă: un audit doar al deciziilor ar fi găsit un model „favorabil” persoanelor LGBTQ+, iar un audit doar al reprezentărilor, un model cu prejudecăți puternice. Niciuna dintre concluzii nu este completă singură.

[[include:sections/compas_results.md]]

## 2.9 Interpretare și discuție

**Ce arată studiul de caz despre metodologie.** Întregul lanț, de la șabloane la teste statistice, a funcționat fără intervenție manuală. Toate cele 1.440 de răspunsuri din E1 au putut fi extrase automat, niciun model nu a refuzat vreo sarcină, invarianța contrafactuală a fost verificată automat pentru fiecare scenariu, iar ambele modele au trecut verificarea de manipulare. Astfel, diferențele dintre identități pot fi interpretate ca efecte ale orientării menționate, nu ca zgomot sau ca diferențe între texte.

**Ce arată studiul de caz despre modele (rezultate preliminare).**

- Nu există dovezi că persoanele LGBTQ+ ar fi tratate mai defavorabil în decizii (H1a nu este susținută pe acest set). Efectele observate merg mai ales în sens opus. Când orientarea este numită explicit, ambele modele consideră martorii LGBTQ+ mai credibili, iar Llama acordă și un risc de recidivă mai mic. Efectul este semnificativ după corecție pentru Llama, la „gay” și „lesbiană”.
- La credibilitate, când orientarea este doar sugerată prin partener, efectul favorabil dispare aproape complet la ambele modele. Faptul că semnalarea explicită și cea implicită dau rezultate diferite este cea mai consecventă observație a studiului de caz. Direcția diferenței nu este însă mereu aceeași: la Qwen, pentru riscul de recidivă, varianta implicită este cea tratată mai favorabil. Observația este compatibilă cu mecanismul descris de Hofmann et al. [2] și susține includerea ambelor tipuri de semnalare (beneficiul B1).
- În reprezentările interne ale Qwen există o asociere puternică între etichetele LGBTQ+ și vinovăție sau imoralitate, pe care testul generic din literatură nu o detectează.
- Asocierile din reprezentări nu se transmit direct în decizii (E3 neconcludent, cu disocieri clare).
- Pe 60 de dosare reale COMPAS, ambele modele prezic recidiva cel puțin la fel de bine ca scorul COMPAS, iar efectele de identitate păstrează direcția observată pe scenariile sintetice. La Llama, supracorecția pentru bărbații numiți explicit gay sau bisexuali este semnificativă după corecția Holm.

**Interpretare.** Tratamentul mai favorabil nu este un rezultat „bun” din perspectivă juridică. Încalcă aceeași condiție de corectitudine contrafactuală [10] ca discriminarea negativă, pentru că decizia depinde de un atribut irelevant. Faptul că el apare doar la menționarea explicită sugerează o corecție învățată de model pentru grupurile numite direct, nu o evaluare neutră. Asocierile negative din reprezentări rămân prezente și ar putea apărea în situații mai puțin controlate decât un răspuns de un singur număr, de exemplu în motivarea scrisă a unei decizii. Aceste interpretări trebuie verificate în experimentul complet, cu mai multe modele și cu motivări în text liber.

**Interpretarea experților.** Studiul de caz nu include încă o evaluare a scenariilor de către un specialist în drept penal. Grila descrisă în secțiunea 1.5 este pregătită și va fi aplicată înainte de rularea completă. Rezultatele de mai sus trebuie deci citite ca dovezi empirice preliminare, nu ca interpretare validată juridic.

**Limitări specifice studiului de caz.** Eșantionul este mic (20 de scenarii pe sarcină), deci doar efectele mari pot fi detectate. Sunt evaluate doar două modele open-weights, iar cel folosit pentru E2 și E3 este mic (1,5 miliarde de parametri). Sarcina PRE are încă puțină variație: Llama folosește mai ales valoarea 3, iar Qwen rămâne la plafon. Prompturile sunt în engleză, dar folosesc o scală din dreptul român. Rezultatele E2 depind de alegerea cuvintelor-atribut și a cadrelor: lista vinovat–nevinovat conține și termeni morali, așa că efectul ei amestecă vinovăția juridică cu judecata morală. Cuvântul „heterosexual” apare rar în texte reale, deci comparația explicită pune față în față două etichete marcate. La Qwen, varianta heterosexuală explicită diferă ea însăși de control (secțiunea 2.5), iar o parte din diferența dintre grupuri poate veni din această marcare. Pe datele COMPAS, eșantionul are doar 13 femei, așa că rezultatele pentru lesbiene și femei bisexuale au o putere statistică foarte mică.

## 2.10 Ajustări pentru experimentul complet

- **Sarcina PRE** a fost reconstruită și calibrată pe variantele de control (secțiunea 2.4), dar criteriile sunt îndeplinite doar parțial. Urmează scenarii cu o distribuție mai echilibrată pentru Llama și o soluție separată pentru Qwen, de exemplu un model mai mare, deoarece modelul de 1,5 miliarde de parametri nu coboară sub măsura 4.
- **Dimensiunea eșantionului.** Efectele observate pentru variantele explicite (|d_{z}| între 0,32 și 0,97 la Llama) pot fi detectate cu 100 de scenarii pe sarcină chiar și după corecția Holm (pragul minim este 0,39). Efectele implicite sunt însă mai mici (|d_{z}| între 0,22 și 0,46 la cele două modele). Pentru a detecta d_{z} = 0,25 după corecție ar fi nevoie de aproximativ 250 de scenarii pe sarcină. Șabloanele vor fi extinse la 10–15 pe sarcină, iar numărul de scenarii va fi stabilit între 100 și 250, în funcție de costul API-urilor.
- **Atributele din E2** vor fi separate în concepte strict juridice (guilty, culpable, convicted) și concepte morale (immoral, wicked), pentru a vedea care dintre ele produce asocierea. Numărul de cadre va crește de la 10 la cel puțin 30.
- **Modelele.** E2 va fi rulat pe cele trei modele open-weights de 7–9 miliarde de parametri, cuantizate pe 4 biți pe GPU (PyTorch cu CUDA), iar E1 pe cele trei modele comerciale.
- **Motivarea în text liber.** Pe un subset de scenarii, modelele vor fi rugate să-și motiveze decizia, pentru a verifica dacă orientarea sexuală este menționată sau folosită ca argument.
- **Determinismul.** Fiecare prompt va fi rulat de două ori, iar răspunsurile diferite vor fi raportate separat.

\newpage
