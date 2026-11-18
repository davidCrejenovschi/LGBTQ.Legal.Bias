# 3. Lucrări similare și pregătirea validării pe date reale

Capitolul descrie abordările din literatură cu care se compară lucrarea, arată prin ce se aseamănă și prin ce se deosebesc de abordarea propusă și identifică metricile pentru care se așteaptă rezultate similare sau mai bune. Ultima secțiune descrie seturile de date reale pregătite pentru validare.

## 3.1 Asocieri măsurate în reprezentările modelelor

**WEAT** (Caliskan et al. [4]) a arătat că vectorii de cuvinte GloVe, învățați din texte de pe internet, reproduc asocierile măsurate la oameni prin testul de asociere implicită (IAT): florile sunt mai apropiate de cuvinte plăcute decât insectele, iar numele masculine sunt mai apropiate de carieră decât cele feminine. Testul compară două mulțimi de cuvinte-țintă cu două mulțimi de atribute prin diferența de similaritate cosinus și raportează o mărime a efectului de tip Cohen, cu un test de permutare. **SEAT** (May et al. [5]) aplică același test pe codificatoare de propoziții, introducând cuvintele în propoziții „neutre” precum „This is a [WORD].”. Pe modele precum ELMo și BERT, rezultatele au fost mai puțin consecvente decât pentru vectorii de cuvinte, iar autorii avertizează că lipsa unui efect nu dovedește lipsa prejudecății. **CEAT** (Guo și Caliskan [17]) tratează efectele măsurate în contexte diferite ca o distribuție și le combină printr-o meta-analiză cu efecte aleatoare. Ethayarajh [18] a arătat că reprezentările contextuale sunt puternic anizotrope (ocupă un con îngust al spațiului), mai ales în straturile superioare ale GPT-2. Ca urmare, cosinusul dintre două propoziții oarecare este mare și comparațiile directe devin înșelătoare.

**Asemănări.** E2 folosește aceeași statistică (formulele 10–12), aceleași propoziții neutre ca SEAT și testul de permutare al lui Caliskan et al., deci rezultatele pot fi comparate direct cu literatura.

**Diferențe.** (1) Atributele nu sunt generice (plăcut–neplăcut), ci concepte juridice alese pentru fiecare sarcină din E1, ceea ce face posibilă legătura cu deciziile (E3). (2) Analiza se face pe modele decoder de tip instruct, pe fiecare strat, nu doar pe ultimul. (3) Studiul de caz a arătat că, la aceste modele, problema descrisă de Ethayarajh are o cauză concretă, primul token cu „activări masive” [29], [30]. Abordarea propusă îl exclude și standardizează dimensiunile. (4) Propozițiile pentru LGBTQ+ și cele pentru referința heterosexuală formează perechi, ceea ce permite o variantă pe perechi a testului, mai sensibilă decât varianta cu eșantioane independente.

## 3.2 Benchmark-uri pentru prejudecăți și prejudecăți față de persoanele LGBTQ+

**CrowS-Pairs** (Nangia et al. [6]) conține 1.508 perechi de propoziții care diferă printr-un singur grup social, pe nouă tipuri de prejudecăți, dintre care 84 privesc orientarea sexuală. Metrica este procentul de perechi în care modelul consideră mai probabilă propoziția stereotipă (50% înseamnă lipsa preferinței). **BBQ** (Parrish et al. [7]) are 58.492 de întrebări pe nouă dimensiuni sociale, inclusiv orientarea sexuală, puse în contexte ambigue și dezambiguizate, și măsoară cât de des răspunsul modelului urmează stereotipul. **WinoQueer** (Felkner et al. [1]) a fost construit pornind de la un sondaj cu 295 de persoane LGBTQ+. Măsoară, ca și CrowS-Pairs, preferința modelului pentru propoziții anti-LGBTQ+ și arată că toate modelele testate au astfel de prejudecăți, care pot fi reduse prin reantrenare pe texte scrise de membri ai comunității. Nozza et al. [8] au analizat completările generate de modele pentru propoziții despre persoane LGBTQIA+ și au găsit o proporție semnificativă de completări dăunătoare.

**Asemănări.** Ca în CrowS-Pairs și WinoQueer, unitatea de analiză este o pereche de texte care diferă doar prin grupul social. Termenii de identitate sunt preluați din WinoQueer.

**Diferențe.** Aceste benchmark-uri măsoară probabilitatea unor propoziții sau răspunsuri la întrebări de cultură generală, nu decizii cu consecințe asupra unei persoane. Abordarea propusă măsoară prejudecata direct în unitatea deciziei (puncte pe scala de risc, proporția de arestări preventive), în trei sarcini juridice. În plus, orientarea este semnalată și implicit, prin partener, situație pe care benchmark-urile de mai sus nu o acoperă sistematic.

## 3.3 Decizii cu miză luate de modelele de limbaj

**Tamkin et al. [9]** au generat 70 de scenarii de decizie (de exemplu aprobarea unui credit sau a unei închirieri) în care au variat vârsta, genul și rasa persoanei, declarate explicit sau sugerate prin nume. Au măsurat diferența dintre probabilitățile răspunsului „da” față de un profil de referință și au găsit atât discriminare pozitivă, cât și negativă, care poate fi redusă prin instrucțiuni în prompt. **Hofmann et al. [2]** au folosit metoda „matched guise”: același conținut, scris în engleza afro-americană sau în engleza standard. Au arătat că 12 modele asociază vorbitorii de engleză afro-americană cu stereotipuri negative, chiar dacă stereotipurile exprimate pe față sunt pozitive. În deciziile juridice simulate, acești vorbitori au fost mai des condamnați și mai des condamnați la moarte. Modelele mai mari și antrenarea cu feedback uman au redus prejudecățile exprimate pe față, dar nu și pe cele ascunse.

**Asemănări.** E1 preia de la Tamkin et al. construcția scenariilor din șabloane și comparația cu un profil de referință, iar de la Hofmann et al. ideea că un grup poate fi sugerat, nu doar numit, și decizii juridice ca variabilă măsurată.

**Diferențe.** Niciuna dintre cele două lucrări nu variază orientarea sexuală. Tamkin et al. nu folosesc decizii penale. Hofmann et al. folosesc sarcini juridice simplificate (achitare sau condamnare), în timp ce sarcinile propuse aici urmează procedura penală română (scala măsurilor preventive) și includ credibilitatea martorului, în care persoana nu este acuzată. Abordarea propusă adaugă și analiza reprezentărilor interne pe aceleași modele.

## 3.4 Corectitudinea sistemelor automate în domeniul juridic

Analiza ProPublica a sistemului **COMPAS** (Angwin et al. [22]) a arătat că persoanele de culoare care nu au recidivat erau clasificate ca risc ridicat de aproape două ori mai des decât persoanele albe. Chouldechova [23] a demonstrat că, atunci când ratele de recidivă diferă între grupuri, un instrument calibrat nu poate avea în același timp rate egale de fals pozitive și fals negative. **Dressel și Farid [13]** au arătat că persoane fără pregătire juridică, recrutate online, care primeau doar un profil scurt (sex, vârstă, faptă, antecedente), prezic recidiva aproape la fel de bine ca COMPAS: aproximativ 62–67% acuratețe pentru oameni, față de 65,2% pentru COMPAS. Un clasificator liniar cu doar două variabile (vârsta și numărul de condamnări anterioare) obține aceeași acuratețe. **FairLex** (Chalkidis et al. [3]) evaluează corectitudinea modelelor pe patru seturi de hotărâri judecătorești (CEDO, Curtea Supremă a SUA, Tribunalul Federal Elvețian, instanțele penale din China), în cinci limbi, după gen, vârstă, regiune, limbă și domeniu juridic. Concluzia este că nicio metodă de reantrenare nu reduce constant diferențele dintre grupuri. **LegalBench** (Guha et al. [14]) are 162 de sarcini de raționament juridic, dar măsoară competența, nu corectitudinea. **Regulamentul european privind inteligența artificială** [15] clasifică drept „de risc ridicat” atât sistemele folosite pentru a evalua riscul ca o persoană să comită sau să repete o infracțiune, cât și pe cele care asistă autoritățile judiciare (Anexa III, punctele 6 și 8).

**Asemănări.** Sarcina REC este echivalentul generativ al instrumentelor de tip COMPAS. Pe setul COMPAS se folosesc aceleași profile ca la Dressel și Farid și aceleași metrici de eroare (FPR, FNR) ca la ProPublica și Chouldechova.

**Diferențe.** FairLex nu include orientarea sexuală, iar studiile despre COMPAS analizează rasa și genul. Atributul analizat aici nu apare în datele reale, ci este introdus contrafactual, deci efectul lui poate fi izolat fără variabile ascunse care să-l confunde. În plus, modelele evaluate sunt modele de limbaj generale, nu clasificatoare antrenate pe date penale.

## 3.5 Evaluarea contrafactuală și metricile de corectitudine

**Kusner et al. [10]** au definit corectitudinea contrafactuală: o decizie este corectă față de un individ dacă ar fi aceeași într-o lume în care doar atributul protejat al individului ar fi fost altul. **Garg et al. [11]** au transformat definiția într-o metrică aplicabilă textului, counterfactual token fairness, înlocuind termenii de identitate și măsurând cât se schimbă predicția unui clasificator de toxicitate. Au propus și metode de corectare (de exemplu, counterfactual logit pairing). **Feldman et al. [12]** au formalizat impactul disparat prin raportul ratelor deciziilor favorabile și regula celor patru cincimi (prag de 0,8). Studiul lui Gallegos et al. [19] clasifică metricile de prejudecată pentru LLM-uri în metrici bazate pe reprezentări, pe probabilități și pe textul generat.

**Asemănări.** CFR (formula 3) este echivalentul pentru decizii ordinale al metricii lui Garg et al. DIR (formula 6) este metrica lui Feldman et al., cu același prag de 0,8.

**Diferențe.** Garg et al. lucrează cu probabilitățile unui clasificator. Aici, decizia este extrasă din textul generat, iar refuzurile sunt tratate ca un rezultat separat (formula 7), situație care nu există în cazul clasificatoarelor.

## 3.6 Legătura dintre metricile intrinseci și cele extrinseci

**Goldfarb-Tarrant et al. [16]** au comparat WEAT cu prejudecata măsurată în aplicații (rezolvarea coreferințelor și detectarea discursului instigator la ură), în mai multe limbi, și nu au găsit o corelație consistentă între ele. Aceasta este principala lucrare cu care se compară E3. Dacă și în context juridic corelația este slabă, rezultatul lor se confirmă. Dacă conceptele aliniate pe sarcini produc o corelație mai bună decât testul generic, abordarea propusă oferă o cale de a face metricile intrinseci mai utile pentru auditarea aplicațiilor.

## 3.7 Comparație de ansamblu

Table: Comparația abordării propuse cu lucrările din literatură.

| Lucrarea | Atribut | Domeniu | Nivel | Semnalare | Metrici principale | Diferența față de abordarea propusă |
|---|---|---|---|---|---|---|
| Caliskan et al. [4] | gen, rasă, vârstă etc. | general | reprezentări (cuvinte) | – | WEAT d, permutare | fără orientare sexuală, fără decizii |
| May et al. [5] | gen, rasă | general | reprezentări (propoziții) | – | SEAT d, permutare | codificatoare vechi, atribute generice |
| Nangia et al. [6]; Parrish et al. [7] | 9 dimensiuni, inclusiv orientarea | general | probabilitate / QA | explicită | % stereotip, scor de bias | fără decizii cu miză |
| Felkner et al. [1] | LGBTQ+ | general | probabilitate | explicită | % preferință anti-LGBTQ+ | fără context juridic |
| Tamkin et al. [9] | vârstă, gen, rasă | decizii (credit, locuință etc.) | decizie | explicită și prin nume | scor de discriminare (logit) | fără orientare, fără drept penal |
| Hofmann et al. [2] | dialect (rasă) | angajare, drept penal | decizie și asocieri | implicită | rate de condamnare | alt atribut, fără analiza straturilor |
| Chalkidis et al. [3] | gen, vârstă, regiune, limbă | hotărâri judecătorești | performanță pe grupuri | din date | F1 pe grupuri, diferențe | fără orientare, clasificatoare antrenate |
| Dressel și Farid [13] | rasă | recidivă (COMPAS) | decizie | din date | acuratețe, FPR, FNR | oameni și COMPAS, nu LLM-uri |
| Goldfarb-Tarrant et al. [16] | gen, rasă | coreferință, discurs instigator | intrinsec vs. extrinsec | – | corelație | fără context juridic, atribute generice |
| **Abordarea propusă** | **orientare sexuală** | **drept penal (RO)** | **decizie + reprezentări + legătura lor** | **explicită și implicită** | **CFR, MSD, RD, DIR, refuz, SEAT pe straturi, ρ** | – |

## 3.8 Unde se așteaptă rezultate similare sau mai bune

Tabelul 15 rezumă, pentru fiecare metrică, rezultatul de referință din literatură, ce se așteaptă în experimentul complet și ce arată deja studiul de caz din capitolul 2.

[[include:generated/expectations.md]]

## 3.9 Pregătirea validării pe date reale

Validarea pe date reale folosește seturi publice, folosite și în articolele citate, astfel încât rezultatele să poată fi puse alături de cele din literatură (Tabelul 16).

Table: Seturile de date reale pregătite pentru validare.

| Set de date | Folosit în | Ce conține | Cum este folosit aici | Stare |
|---|---|---|---|---|
| COMPAS, ProPublica (compas-scores-two-years.csv) | [13], [22], [23] | 6.167 de dosare (după filtrare), recidiva reală în 2 ani, scorul COMPAS | profiluri de tip Dressel și Farid cu cele 6 variante de identitate; AUC, acuratețe, FPR/FNR pe variantă; comparație cu COMPAS | descărcat, încărcat și testat; pilot pe 60 de dosare (secțiunea 2.8) |
| CrowS-Pairs, subsetul pentru orientarea sexuală | [6] | 84 de perechi de propoziții | scorul de preferință pentru stereotip al fiecărui model, pentru a-l plasa față de rezultatele publicate | planificat |
| BBQ, categoria sexual_orientation | [7] | întrebări în context ambiguu și dezambiguizat | scorul de bias din BBQ, comparat cu prejudecata din deciziile juridice ale acelorași modele | planificat |
| WinoQueer | [1] | perechi de propoziții anti-LGBTQ+ / heterosexuale | termenii de identitate (deja folosiți) și scorul WinoQueer pe modelele open-weights | termeni preluați; scor planificat |

Setul COMPAS este singurul care are o valoare reală de referință pentru decizie, așa că a fost pregătit primul. Pașii parcurși sunt: descărcarea fișierului din repository-ul public ProPublica (script `scripts/download_assets.py`), aplicarea acelorași filtre ca în analiza originală, extragerea unui eșantion echilibrat (jumătate persoane care au recidivat), construirea profilurilor și a celor 6 variante de identitate pe dosar (script `scripts/04_compas_prompts.py`, verificat prin teste unitare) și rularea modelelor (secțiunea 2.8). Celelalte trei seturi vor fi folosite pentru a verifica dacă un model cu prejudecăți mari pe benchmark-urile generale are și diferențe mari în deciziile juridice. Este o întrebare de tip extrinsec–extrinsec, complementară lui E3.

\newpage
