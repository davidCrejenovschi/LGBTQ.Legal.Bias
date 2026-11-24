Table: CrowS-Pairs, subsetul pentru orientarea sexuală, pe Qwen2.5-1.5B-Instruct: proporția perechilor în care modelul preferă propoziția mai stereotipă (50% = nicio preferință; adaptare pentru modele decoder, prin log-probabilitatea întregii propoziții).

| Perechi | n | Preferă stereotipul | IÎ 95% (bootstrap) | p binomial (vs. 50%) |
|---|---|---|---|---|
| toate perechile | 84 | 82% | [74%; 89%] | < 0,001 |
| tip „stereo” | 72 | 85% | – | – |
| tip „antistereo” | 12 | 67% | – | – |
| toate, normalizat pe token | 84 | 77% | – | – |
