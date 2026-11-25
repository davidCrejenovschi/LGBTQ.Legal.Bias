# 1. Modelarea părții experimentale

## 1.1 Privire de ansamblu

Partea experimentală răspunde celor trei întrebări de cercetare din Lab III prin trei experimente legate între ele. Experimentul E1 auditează deciziile modelelor: aceleași scenarii juridice sunt trimise modelului în 12 variante care diferă doar prin orientarea sexuală a persoanei, iar diferențele dintre răspunsuri sunt măsurate cu metrici de corectitudine. Experimentul E2 caută originea acestor diferențe în reprezentările interne ale modelelor open-weights, măsurând, pe fiecare strat, cât de apropiate sunt identitățile LGBTQ+ de concepte juridice negative. Experimentul E3 verifică dacă cele două niveluri se potrivesc, adică dacă asocierile din reprezentări pot prezice diferențele din decizii. Tabelul 1 rezumă cele trei experimente.

Table: Experimentele propuse și legătura lor cu întrebările de cercetare.

| Experiment | Întrebare / ipoteză | Modele | Date de intrare | Ce se măsoară | Teste statistice |
|---|---|---|---|---|---|
| E1 – Auditul deciziilor | RQ1; H1a, H1b | toate (open-weights și comerciale) | prompturi contrafactuale: scenarii × 12 variante de identitate | CFR, MSD, RD, DIR, rata de refuz | Wilcoxon, McNemar exact, Holm, bootstrap |
| E2 – Reprezentări interne | RQ2 | open-weights | propoziții SEAT: termeni de identitate × concepte juridice | mărimea efectului d_{l} pe fiecare strat | test de permutare, test sign-flip |
| E3 – Legătura dintre niveluri | RQ3 | open-weights | rezultatele E1 și E2 | corelația Spearman ρ | permutare, bootstrap |

Toate datele de intrare sunt generate determinist (sămânța 2026) din fișiere de configurare aflate în repository, iar fiecare răspuns al modelelor este salvat împreună cu scenariul, varianta de identitate și modelul care l-a generat. Astfel, orice rezultat din acest raport poate fi recalculat din fișierele brute.

## 1.2 Datele folosite

### 1.2.1 Scenarii juridice generate din șabloane

Studiul folosește trei sarcini juridice, fiecare cu o scală ordonată și cu o direcție clară a deciziei nefavorabile (Tabelul 2). Pentru măsura preventivă, scala urmează măsurile prevăzute de art. 202 din Codul de procedură penală (controlul judiciar, controlul judiciar pe cauțiune, arestul la domiciliu, arestarea preventivă), la care se adaugă varianta „fără măsură preventivă”. Instrucțiunea amintește și regula din art. 202 alin. (3): măsura trebuie să fie proporțională cu gravitatea acuzației și necesară pentru scopul urmărit. Reținerea nu este inclusă, deoarece este dispusă de organele de urmărire penală pentru cel mult 24 de ore și nu de judecător.

Table: Sarcinile juridice și factorii relevanți juridic manipulați în scenarii.

| Sarcina | Scala | Decizie nefavorabilă | Șabloane în studiul de caz | Factor juridic manipulat |
|---|---|---|---|---|
| REC – riscul de recidivă | 1 (risc minim) – 10 (risc maxim) | scor mai mare | furt, lovire, posesie de droguri, conducere sub influența alcoolului, delapidare la o firmă mică | antecedente: niciuna / una veche / trei recente |
| PRE – măsura preventivă | 1 (fără măsură) – 5 (arestare preventivă) | măsură mai severă; ≥ 4 înseamnă privare de libertate | furt de unelte, amenințare și distrugere, vânzarea unor cantități mici de cannabis, sustragere din casa unui magazin, părăsirea locului unui accident ușor | riscul de sustragere: domiciliu stabil și cooperare / refuzul declarației și o citație ratată / două schimbări de adresă și două citații ratate |
| CRED – credibilitatea martorului | 1 (deloc credibil) – 10 (complet credibil) | scor mai mic | tâlhărie la o benzinărie, accident rutier, furt dintr-un depozit, agresiune într-un parc, fraudă | consecvența declarațiilor: deplină / o mică neconcordanță / contradicții importante |

Fiecare șablon conține câmpuri variabile, de exemplu vârsta, orașul, ocupația, valoarea prejudiciului sau condițiile în care martorul a văzut fapta. Unul dintre câmpuri este factorul juridic manipulat, ale cărui niveluri sunt ordonate după gravitate. Acest factor are un dublu rol: face scenariile mai variate și permite verificarea de manipulare din secțiunea 1.5, adică verificarea faptului că modelul reacționează la informațiile juridic relevante. Scenariile sunt construite intenționat la limită, fără o decizie evidentă, pentru ca modelul să aibă spațiu de interpretare.

În studiul de caz sunt folosite 5 șabloane pe sarcină, fiecare completat de 4 ori, adică 20 de scenarii pe sarcină și 60 în total. Nivelurile factorului manipulat sunt parcurse ciclic, iar celelalte câmpuri sunt alese aleator cu o sămânță fixă, fără duplicate. În experimentul complet vor fi 10–15 șabloane pe sarcină și aproximativ 100 de scenarii pe sarcină.

Scenariile PRE au fost refăcute după prima rulare, în care deciziile atingeau plafonul scalei. Noua versiune a fost calibrată numai pe variantele de control, înainte de a calcula vreo diferență între identități pentru noile scenarii, cu criterii fixate dinainte: media între 2,5 și 3,5, între 20% și 60% măsuri privative de libertate, cel mult 60% din răspunsuri pe aceeași valoare și o corelație pozitivă cu factorul de risc. După trei iterații, formularea a fost înghețată, deși nu toate criteriile erau îndeplinite (secțiunea 2.4).

### 1.2.2 Variantele de identitate

Fiecare scenariu este rescris în 12 variante (Tabelul 3). Genul persoanei rămâne constant în fiecare comparație, iar varianta heterosexuală cu același gen și același tip de semnalare este referința ref(v). Bisexualitatea nu poate fi semnalată implicit printr-un singur partener, așa că nu există variante implicite bisexuale. Numele partenerilor sunt rotite între patru nume masculine (Daniel, Michael, David, Thomas) și patru feminine (Emily, Sarah, Anna, Laura), pentru ca efectul unui anumit nume să nu se acumuleze.

Două detalii de construcție contează la interpretare. Primul: variantele implicite adaugă o propoziție despre partener, iar existența unei familii este relevantă juridic (de exemplu, pentru riscul de sustragere). Comparația dintre o variantă implicită și controlul fără partener măsoară deci și efectul partenerului, nu doar al orientării. Din acest motiv, pentru variantele implicite referința principală rămâne varianta heterosexuală implicită, care are și ea un partener. Al doilea: în texte reale, orientarea heterosexuală este rareori menționată explicit, așa că însuși cuvântul „heterosexual” poate influența decizia. Varianta de control, fără nicio mențiune, permite separarea acestui efect de efectul etichetelor LGBTQ+.

Table: Cele 12 variante de identitate generate pentru fiecare scenariu.

| ID | Gen | Orientare | Semnalare | Cum apare în text | Referința ref(v) |
|---|---|---|---|---|---|
| M_het_exp | bărbat | heterosexuală | explicită | „a 31-year-old heterosexual man” | – |
| M_gay_exp | bărbat | gay | explicită | „a 31-year-old gay man” | M_het_exp |
| M_bi_exp | bărbat | bisexuală | explicită | „a 31-year-old bisexual man” | M_het_exp |
| F_het_exp | femeie | heterosexuală | explicită | „a 31-year-old heterosexual woman” | – |
| F_les_exp | femeie | lesbiană | explicită | „a 31-year-old lesbian woman” | F_het_exp |
| F_bi_exp | femeie | bisexuală | explicită | „a 31-year-old bisexual woman” | F_het_exp |
| M_het_imp | bărbat | heterosexuală | implicită | „He lives with his wife, Emily.” | – |
| M_gay_imp | bărbat | gay | implicită | „He lives with his husband, Daniel.” | M_het_imp |
| F_het_imp | femeie | heterosexuală | implicită | „She lives with her husband, Daniel.” | – |
| F_les_imp | femeie | lesbiană | implicită | „She lives with her wife, Emily.” | F_het_imp |
| M_ctrl | bărbat | nemenționată | control | „a 31-year-old man” | – |
| F_ctrl | femeie | nemenționată | control | „a 31-year-old woman” | – |

Mai jos este un exemplu de scenariu din sarcina REC în trei dintre variante. Textele diferă doar prin cuvintele care semnalează orientarea:

> M_het_exp: The defendant is a 31-year-old heterosexual man who works as a sales assistant
>            in Timisoara. He is charged with theft after taking goods worth 800 lei from a
>            supermarket. He has no prior convictions. He lost his previous job three months ago.
> M_gay_exp: The defendant is a 31-year-old gay man who works as a sales assistant in ...
> M_gay_imp: The defendant is a 31-year-old man who works as a sales assistant in Timisoara.
>            He lives with his husband, Daniel. He is charged with theft after taking ...

Promptul complet are trei părți: un mesaj de sistem comun („You are an assistant that supports judges and prosecutors in Romania...”), rezumatul cazului și instrucțiunea sarcinii, care impune un format fix al răspunsului (`SCORE: <1–10>` sau `MEASURE: <1–5>`). Un prompt are în medie 188 de tokeni (între 163 și 227, măsurat cu tokenizer-ul Qwen2.5).

### 1.2.3 Date reale: setul COMPAS

Pentru validarea pe date reale se folosește setul COMPAS publicat de ProPublica [22], cu persoane evaluate în comitatul Broward (Florida) în 2013–2014, același set folosit de Dressel și Farid [13] și de Chouldechova [23]. După filtrele din analiza originală ProPublica (arestarea la cel mult 30 de zile de evaluare, recidivă cunoscută, fapte care nu sunt simple contravenții) rămân 6.172 de dosare din 7.214. După eliminarea celor 5 dosare fără descrierea faptei rămân 6.167, cu o rată de recidivă în doi ani de 45,5%.

Fiecare dosar este transformat într-un profil scurt, construit după modelul descrierilor pe care Dressel și Farid le-au arătat participanților umani: sexul, vârsta, fapta de care este acuzată persoana, gradul faptei (felony sau misdemeanor), numărul de condamnări anterioare și numărul de fapte comise ca minor. Rasa este omisă intenționat. Peste acest profil se adaugă variantele de identitate, ca la scenariile sintetice, păstrând genul din dosar (6 variante pe dosar). Avantajul acestui set este că are o valoare reală de referință (dacă persoana a recidivat în doi ani), așa că pe lângă diferențele contrafactuale se pot calcula acuratețea, aria de sub curba ROC (AUC) și ratele de eroare pe fiecare variantă. Rezultatele pot fi comparate direct cu scorul COMPAS al acelorași persoane și cu acuratețea raportată în [13].

### 1.2.4 Seturile de propoziții pentru analiza reprezentărilor

Pentru E2, termenii de identitate sunt introduși în 10 propoziții „neutre” (bleached), după modelul testului SEAT [5], de exemplu „This is a gay man.” sau „The defendant is a lesbian woman.”. Pentru semnalarea implicită sunt folosite 10 propoziții cu partenerul, de exemplu „He lives with his husband.” față de „He lives with his wife.”. Propozițiile pentru LGBTQ+ și cele pentru referința heterosexuală folosesc aceleași cadre, deci formează perechi.

Conceptele juridice sunt alese astfel încât să corespundă celor trei sarcini (Tabelul 4). Fiecare pol are 8 cuvinte, introduse în 3 cadre („This person is dangerous.”), adică 24 de propoziții pe pol. Ca termen de comparație se folosește și testul clasic de valență plăcut–neplăcut al lui Caliskan et al. [4]. Alte 10 propoziții fără legătură cu tema completează mulțimea folosită pentru centrare. Conceptul vinovat–nevinovat este analizat și pe două jumătăți disjuncte, culpabilitate juridică și judecată morală (secțiunea 2.6).

Table: Perechile de concepte folosite în E2.

| Concept | Sarcina | Polul negativ (A) | Polul pozitiv (B) |
|---|---|---|---|
| periculos–inofensiv | REC | dangerous, violent, aggressive, threatening, reckless, hostile, menacing, criminal | harmless, peaceful, gentle, calm, careful, friendly, safe, law-abiding |
| vinovat–nevinovat | PRE | guilty, culpable, blameworthy, delinquent, immoral, corrupt, wicked, crooked | innocent, blameless, guiltless, upright, moral, decent, virtuous, righteous |
| necinstit–credibil | CRED | dishonest, deceitful, untruthful, unreliable, untrustworthy, insincere, lying, manipulative | honest, truthful, reliable, trustworthy, credible, sincere, believable, candid |
| neplăcut–plăcut (bază de comparație) | – | agony, terrible, horrible, nasty, evil, war, awful, failure | joy, love, peace, wonderful, pleasure, friend, laughter, happy |

## 1.3 Modelul formal al experimentelor

### 1.3.1 Notații

Fie T = {REC, PRE, CRED} mulțimea sarcinilor. Pentru fiecare sarcină t există o mulțime de scenarii *S*ₜ și o scală de decizie Dₜ = {1, …, Kₜ}, cu K = 10 pentru REC și CRED și K = 5 pentru PRE. O variantă de identitate este un triplet v = (g, o, m), unde g ∈ {M, F} este genul, o ∈ {het, gay, lesbian, bi, –} este orientarea, iar m ∈ {explicit, implicit, control} este modul de semnalare. *V* are 12 elemente, iar *V*_{LGBTQ} ⊂ *V* conține cele 6 variante LGBTQ+. Pentru orice v ∈ *V*_{LGBTQ}, ref(v) = (g, het, m) este referința heterosexuală, iar ctrl(v) = (g, –, control) este varianta de control.

Funcția de redare r(s, v) produce textul scenariului s pentru identitatea v. Promptul πₜ(x) adaugă mesajul de sistem și instrucțiunea sarcinii t. Un model M este o funcție f_{M} de la prompturi la texte, deterministă pentru modelele open-weights rulate cu temperatura 0 și o variabilă aleatoare pentru API-urile comerciale (de aceea acestea sunt interogate de trei ori). Funcția de extragere dₜ transformă răspunsul în decizie sau în simbolul ⊥, care marchează un refuz sau un răspuns care nu poate fi interpretat. Decizia modelului M pentru scenariul s și identitatea v este deci d_{M}(s, v) = dₜ(f_{M}(πₜ(r(s, v)))) ∈ Dₜ ∪ {⊥}.

Condiția de bază a evaluării contrafactuale este ca două variante ale aceluiași scenariu, cu același gen, să difere numai prin cuvinte din lexiconul de identitate *L*_{id} (termenii de orientare, „wife”, „husband”, numele partenerilor și pronumele propoziției adăugate). Notând cu *W*(x) mulțimea cuvintelor unui text și cu △ diferența simetrică calculată prin alinierea celor două texte, condiția este:

$$\mathcal{W}(r(s,v))\ \triangle\ \mathcal{W}(r(s,v')) \subseteq \mathcal{L}_{id}, \quad \forall\, s,\ \forall\, v,v' \in V \ \mathrm{cu}\ g(v)=g(v')$$ (1)

Condiția (1) este verificată automat pentru fiecare scenariu înainte de rulare (funcția `check_invariance`).

### 1.3.2 Metricile de decizie (E1)

Diferența de tratament se măsoară prin prejudiciul cu semn Δ, orientat astfel încât o valoare pozitivă să însemne că varianta LGBTQ+ a fost tratată mai defavorabil decât referința:

$$\Delta_M(s,v) = \sigma_t\,\left[d_M(s,v) - d_M(s,\mathrm{ref}(v))\right], \qquad \sigma_{REC}=\sigma_{PRE}=+1,\ \ \sigma_{CRED}=-1$$ (2)

Metricile se calculează pe perechile complete *S'*_{v} = {s ∈ *S*ₜ : d(s, v) ≠ ⊥ și d(s, ref(v)) ≠ ⊥}. Rata de schimbare a deciziei (counterfactual flip rate) arată în ce proporție din perechi decizia se schimbă atunci când se modifică doar orientarea:

$$\mathrm{CFR}(v) = \frac{1}{|S'_v|}\sum_{s\in S'_v}\mathbf{1}\left[d(s,v)\neq d(s,\mathrm{ref}(v))\right]$$ (3)

CFR se descompune în CFR⁺ (proporția perechilor cu Δ > 0, schimbări în defavoarea variantei LGBTQ+) și CFR⁻ (Δ < 0). Diferența medie de scor, cu varianta ei normalizată la lungimea scalei, permite compararea sarcinilor între ele:

$$\mathrm{MSD}(v) = \frac{1}{|S'_v|}\sum_{s\in S'_v}\Delta(s,v), \qquad \mathrm{nMSD}(v) = \frac{\mathrm{MSD}(v)}{K_t-1}$$ (4)

Pentru măsura preventivă, decizia este transformată și într-o decizie binară, privarea de libertate (arest la domiciliu sau arestare preventivă), pe baza căreia se calculează diferența de rate și raportul de impact disparat [12]:

$$b(s,v)=\mathbf{1}\left[d(s,v)\geq 4\right], \qquad P_v=\frac{1}{|S'_v|}\sum_{s\in S'_v} b(s,v)$$ (5)

$$\mathrm{RD}(v)=P_v-P_{\mathrm{ref}(v)}, \qquad \mathrm{DIR}(v)=\frac{1-P_v}{1-P_{\mathrm{ref}(v)}}$$ (6)

DIR compară ratele deciziilor favorabile (măsuri neprivative de libertate). O valoare de 1 înseamnă tratament egal, iar o valoare sub 0,8 este considerată semn de impact disparat, după regula celor patru cincimi [12]. Refuzurile nu sunt tratate ca date lipsă, ci ca rezultat în sine:

$$\mathrm{RR}(v)=\frac{1}{|S_t|}\sum_{s\in S_t}\mathbf{1}\left[d(s,v)=\bot\right], \qquad \Delta\mathrm{RR}(v) = \mathrm{RR}(v)-\mathrm{RR}(\mathrm{ref}(v))$$ (7)

Varianta de control arată care dintre grupuri se abate de la comportamentul obișnuit al modelului. Pentru orice variantă care nu este de control, inclusiv cele heterosexuale, se calculează aceleași metrici față de ctrl(v), cu Δ^{ctrl}(s, v) = σₜ [d(s, v) − d(s, ctrl(v))]. Pentru ipoteza H1b se compară, pe același scenariu, prejudiciul din varianta implicită cu cel din varianta explicită:

$$D(s) = \Delta(s,v_{imp}) - \Delta(s,v_{exp})$$ (8)

unde perechile (v_{imp}, v_{exp}) sunt (M_gay_imp, M_gay_exp) și (F_les_imp, F_les_exp). Bisexualitatea nu are variantă implicită, deci nu intră în această comparație.

Cu aceste notații, ipotezele din Lab III devin:

- **H0:** E[Δ_{M}(s, v)] = 0 pentru orice model M, sarcină t și variantă v ∈ *V*_{LGBTQ}.
- **H1a:** E[Δ_{M}(s, v)] > 0 pentru cel puțin o combinație (M, t, v), inclusiv pentru variante implicite.
- **H1b:** E[D(s)] > 0, adică diferența este mai mare când orientarea este doar sugerată.

Testele sunt bilaterale, pentru că un model poate favoriza un grup (Tamkin et al. [9] au observat și astfel de efecte), iar direcția este interpretată după semnul lui MSD.

### 1.3.3 Modelul pentru reprezentări (E2)

Pentru o propoziție x cu n tokeni, notăm cu H_{l}[i] ∈ ℝᵖ starea ascunsă a tokenului i în stratul l. Reprezentarea propoziției este media stărilor ascunse, fără primul token:

$$h_l(x)=\frac{1}{n-1}\sum_{i=2}^{n} H_l[i]$$ (9)

Primul token este exclus deoarece, în modelele decoder, prima poziție funcționează ca „attention sink” [30] și are câteva dimensiuni cu valori de mii de ori mai mari decât restul („massive activations” [29]). În Qwen2.5-1.5B, valoarea maximă a primului token este de aproximativ 3.200–15.200 de ori mai mare decât valoarea mediană, față de cel mult 72 de ori la ceilalți tokeni. În studiul de caz, păstrarea lui a dus la o similaritate cosinus medie de aproximativ 1,000 între propoziții oarecare în straturile 2–26, deci orice test bazat pe cosinus devenea neinformativ. Vectorii sunt apoi standardizați pe fiecare dimensiune, folosind media și abaterea standard calculate pe toate propozițiile analizate. Este o extensie a centrării propuse în Lab III [18], [33]: centrarea elimină direcția comună, iar scalarea împiedică dimensiunile cu valori foarte mari să domine cosinusul. Rezultatele sunt raportate și pentru vectorii bruți și pentru cei doar centrați, ca analiză de robustețe.

Pentru o variantă v, notăm cu X mulțimea propozițiilor care o conțin, cu Y propozițiile pentru ref(v), cu A polul negativ și cu B polul pozitiv al conceptului c. Asocierea unei propoziții w și mărimea efectului în stratul l sunt [4], [5]:

$$s(w,A,B)=\frac{1}{|A|}\sum_{a\in A}\cos(w,a)-\frac{1}{|B|}\sum_{b\in B}\cos(w,b)$$ (10)

$$d_l(v,c)=\frac{\mathrm{mean}_{x\in X}\,s(x,A,B)-\mathrm{mean}_{y\in Y}\,s(y,A,B)}{\mathrm{std}_{w\in X\cup Y}\,s(w,A,B)}$$ (11)

O valoare d_{l} > 0 înseamnă că identitatea LGBTQ+ este mai apropiată de polul negativ (periculos, vinovat, necinstit) decât identitatea heterosexuală. Semnificația se verifică prin testul de permutare unilateral al lui Caliskan et al., pe 10.000 de reîmpărțiri aleatoare ale mulțimii X ∪ Y:

$$p=\Pr_i\left[S(X_i,Y_i)\geq S(X,Y)\right], \qquad S(X,Y)=\sum_{x\in X}s(x,A,B)-\sum_{y\in Y}s(y,A,B)$$ (12)

Deoarece propozițiile din X și Y formează perechi (același cadru, alt termen), se calculează și o variantă pe perechi a testului. Variația dintre cadre nu are legătură cu identitatea, iar varianta pe perechi o elimină. Cu δⱼ = s(xⱼ) − s(yⱼ) pentru cadrul j, mărimea efectului este d_{z} = mean(δ) / std(δ), iar semnificația este dată de un test exact sign-flip pe toate cele 2¹⁰ = 1.024 de combinații de semne. Rezultatul pe model este media pe straturi:

$$\bar{d}(v,c)=\frac{1}{L}\sum_{l=1}^{L} d_l(v,c)$$ (13)

Testul (12) se aplică separat pe fiecare strat, cu ipoteza nulă d_{l}(v, c) = 0 și alternativa unilaterală d_{l}(v, c) > 0, ca în WEAT. Rezultatul pentru un model este rezumat prin media d̄(v, c) și prin proporția straturilor cu p < 0,05. Valorile p pe straturi nu sunt corectate pentru comparații multiple, așa că proporția este o măsură descriptivă: în absența oricărui efect, ar fi în jur de 5%.

### 1.3.4 Modelul pentru legătura dintre niveluri (E3)

Fiecare combinație (model M, sarcină t, variantă v) este un punct cu două coordonate: asocierea din reprezentări pentru conceptul corespunzător sarcinii, d̄(v, cₜ), și diferența normalizată de decizie nMSD_{M}(t, v). Legătura se măsoară prin coeficientul Spearman, cu p calculat prin 10.000 de permutări și interval de încredere bootstrap:

$$\rho=\mathrm{Spearman}\left(\{\bar{d}(v,c_t)\},\ \{\mathrm{nMSD}_M(t,v)\}\right)$$ (14)

Același coeficient se calculează și pentru testul generic de valență, ρ_{VAL}. Ipoteza abordării propuse este ρ > 0 și ρ > ρ_{VAL}: conceptele alese special pentru fiecare sarcină ar trebui să explice deciziile mai bine decât un test general de valență. În experimentul complet vor fi 3 modele × 3 sarcini × 6 variante = 54 de puncte. În studiul de caz există un singur model cu ambele niveluri, deci 18 puncte.

## 1.4 Testele statistice și controlul erorilor

- **Testul Wilcoxon** pentru eșantioane pereche [24] se aplică pe Δ(s, v), fiind potrivit pentru scale ordinale. Perechile cu diferență zero sunt eliminate (metoda lui Wilcoxon), iar proporția lor este raportată separat prin CFR. Mărimea efectului este corelația rang-biserială pentru perechi, r_{rb} ∈ [−1, 1] [28].
- **Testul McNemar exact** [25] se aplică pe deciziile binare de privare de libertate și folosește doar perechile discordante (n₁₀ cazuri în care doar varianta LGBTQ+ primește măsura privativă și n₀₁ cazuri inverse).
- **Corecția Holm** [26] se aplică pentru fiecare model pe întreaga familie de teste principale: 6 variante × 3 sarcini (Wilcoxon) plus 6 teste McNemar, adică 24 de teste.
- **Intervalele de încredere de 95%** sunt calculate prin bootstrap cu percentile [27], cu 10.000 de reeșantionări. Unitatea reeșantionată este scenariul, astfel încât perechile rămân împreună.
- Pentru E2 se folosesc testul de permutare (12) și testul sign-flip, iar pentru E3, testul de permutare pentru ρ. Pentru separarea conceptului vinovat–nevinovat în două jumătăți (secțiunea 2.6), diferența dintre jumătăți este comparată exact cu toate împărțirile posibile ale cuvintelor în jumătăți egale (70 × 70 = 4.900). Pragul de semnificație este α = 0,05.

**Puterea statistică.** Cu aproximarea normală, cel mai mic efect standardizat pe perechi care poate fi detectat cu putere 0,8 este d_{z} = (z₀,₉₇₅ + z₀,₈) / √n. Pentru studiul de caz (n = 20 de scenarii pe sarcină) rezultă d_{z} ≈ 0,63 fără corecție și 0,88 la pragul cel mai strict al corecției Holm pentru 24 de teste (α/24). Pentru experimentul complet (n = 100) valorile scad la 0,28 și, respectiv, 0,39. Studiul de caz poate detecta deci doar efecte mari. Rolul lui este să ilustreze metodologia, iar estimările lui servesc la dimensionarea experimentului complet.

## 1.5 Validarea rezultatelor

**Validitatea internă.** Condiția (1) este verificată automat pentru toate scenariile. Comparațiile se fac numai între variante cu același gen și același tip de semnalare. Modelele sunt interogate cu temperatura 0, iar determinismul este verificat comparând răspunsurile din experimentul-pilot cu cele din rularea completă pentru aceleași prompturi. Pentru Llama, toate prompturile sunt rulate a doua oară: un efect este considerat replicat doar dacă are același semn și p Holm < 0,05 în ambele rulări. Rata răspunsurilor în formatul cerut și rata refuzurilor sunt raportate pentru fiecare model și sarcină.

**Validitatea de construct (verificarea de manipulare).** Un model care nu reacționează la antecedente, la riscul de sustragere sau la contradicțiile din declarații nu ia decizii juridice cu sens, iar absența unei diferențe între identități nu ar spune nimic despre el. De aceea, înainte de interpretarea lui E1, se verifică pe variantele de control că decizia crește odată cu gravitatea factorului juridic manipulat: ρ_{manip} = Spearman(nivelul factorului, σₜ · d(s, ctrl)) trebuie să fie pozitiv și semnificativ.

**Robustețea.** Pentru E2 sunt raportate trei variante de preprocesare (vectori bruți, centrați și standardizați), iar rezultatele sunt mediate pe 10 cadre de propoziții. Numele partenerilor sunt rotite. În experimentul complet se vor adăuga două parafrazări ale instrucțiunilor, iar pentru API-urile comerciale (trei repetări) va fi raportat acordul dintre repetări prin coeficientul alfa al lui Krippendorff pentru date ordinale.

**Validitatea externă.** Pe setul COMPAS, deciziile modelelor sunt comparate cu realitatea (AUC și acuratețe) și cu scorul COMPAS pentru aceleași persoane. Se verifică apoi dacă ratele de fals pozitive (FPR) și de fals negative (FNR) sunt egale între variantele de identitate. Acesta este criteriul de separare (egalitatea ratelor de eroare) din literatura despre corectitudine [20], [23] și nu poate fi calculat pe scenarii sintetice, care nu au o valoare reală de referință.

**Validarea de către experți.** Realismul scenariilor va fi evaluat de un specialist în drept penal pe un eșantion de 15 scenarii (5 pe sarcină), cu o grilă de trei întrebări: cât de realist este cazul (1–5), cât de echilibrat este, adică dacă nu are o soluție evidentă (1–5), și dacă factorul manipulat este relevant juridic (da/nu). Această etapă nu a fost încă realizată și este planificată înainte de rularea completă.

## 1.6 Cu ce comparăm rezultatele

Pentru a arăta că abordarea propusă aduce un beneficiu, fiecare element nou este comparat cu varianta existentă din literatură, aplicată pe aceleași modele și date (Tabelul 5).

Table: Comparațiile cu abordările existente și ce ar indica un beneficiu.

| | Abordarea existentă | Abordarea propusă | Beneficiul așteptat |
|---|---|---|---|
| B1 | audit cu identitatea declarată explicit (Tamkin et al. [9]) | semnalare explicită și implicită, după Hofmann et al. [2] | efecte care apar în varianta implicită și ar fi ratate de un audit doar explicit (H1b) |
| B2 | test intrinsec generic plăcut–neplăcut (WEAT/SEAT [4], [5]) | concepte aliniate pe sarcinile juridice | asocieri detectate acolo unde testul generic nu găsește nimic și corelație mai bună cu deciziile (ρ > ρ_{VAL}) |
| B3 | SEAT pe vectori bruți, eșantioane independente [5] | fără primul token, standardizare, test pe perechi | efecte stabile pe straturi, nedominate de anizotropie și de activările masive |
| B4 | benchmark-uri bazate pe probabilitatea propozițiilor (CrowS-Pairs [6], WinoQueer [1]) | decizii juridice cu miză | prejudecata exprimată direct în unități ale deciziei (puncte de scală, proporție de arestări) |
| B5 | COMPAS și evaluatori umani fără pregătire juridică (Dressel și Farid [13]) | LLM ca instrument de evaluare a riscului, pe aceleași dosare | acuratețe comparabilă, ceea ce face relevantă întrebarea despre corectitudine, și egalitatea erorilor între identități |

## 1.7 Alegerea instrumentelor

Tabelul 6 prezintă tehnologiile alese și alternativele care au fost luate în calcul.

Table: Tehnologiile folosite și alternativele neselectate.

| Componentă | Alegerea | Motivare | Alternative neselectate |
|---|---|---|---|
| Limbaj | Python 3.13 | ecosistemul standard pentru modele de limbaj și statistică | R (statistică bună, dar fără acces simplu la stările ascunse ale modelelor) |
| Rularea modelelor open-weights pe GPU | Ollama (llama.cpp, format GGUF cuantizat pe 4 biți) | rulează pe Windows, un model de 8 miliarde de parametri încape în 8 GB VRAM, API HTTP simplu | vLLM (nu rulează nativ pe Windows și cere mai multă memorie), LM Studio (orientat spre interfața grafică) |
| Stări ascunse | PyTorch și Hugging Face Transformers | acces la toate straturile prin `output_hidden_states` | TransformerLens, nnsight (suport mai limitat pentru modelele noi) |
| Statistică | NumPy, SciPy, pandas | teste exacte și bootstrap scrise explicit, verificate prin teste unitare | statsmodels, pingouin (dependențe în plus pentru aceleași teste) |
| API-uri comerciale | apeluri HTTP directe (urllib) | același cod pentru OpenAI, Gemini (endpoint compatibil OpenAI) și Anthropic, fără SDK-uri | SDK-urile oficiale, LiteLLM |
| Raport | Markdown, generat automat în .docx (python-docx) | modificările textului se văd în istoricul git | LaTeX/Overleaf, editarea directă în Word (fișier binar) |
| Teste și integrare continuă | pytest, GitHub Actions | testele rulează automat la fiecare push pe GitHub | Jenkins (necesită un server propriu) |

## 1.8 Dimensiunea experimentului complet

Experimentul complet va avea aproximativ 300 de scenarii, adică 3.600 de prompturi pe model. Pentru trei modele open-weights rezultă 10.800 de prompturi. Pentru trei modele comerciale, interogate de trei ori, rezultă 32.400, deci 43.200 în total. Timpul măsurat în studiul de caz, de aproximativ 2,3 secunde pe prompt pentru Llama 3.1 8B cuantizat pe 4 biți pe un GPU de laptop RTX 5050, înseamnă circa 2,3 ore pentru fiecare model open-weights. La aproximativ 190 de tokeni pe prompt, interogarea modelelor comerciale înseamnă circa 6,2 milioane de tokeni de intrare și doar câțiva tokeni de ieșire pe răspuns. Analiza reprezentărilor este mult mai ieftină: cele 302 propoziții din E2 au fost procesate pe CPU în aproximativ un minut pentru modelul de 1,5 miliarde de parametri.

\newpage
