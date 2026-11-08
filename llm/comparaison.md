# Comparaison entre notre interprétation et celle du LLM

**Auteurs :** Aziz Bellaaj, Mohamed Yassine Khiari
**Date :** 2026-11-08

**Sources comparées :**
- notre interprétation, rédigée avant le LLM : `interpretation_personnelle.md` ;
- les réponses du LLM (ChatGPT, agent GPT-6) : `responses/01_hypotheses_chatgpt-gpt6_2026-11-08.md` et `responses/02_vulgarisation_chatgpt-gpt6_2026-11-08.md`.

## Prompt 1 — Hypothèses de modèles

| Thème | Notre interprétation | LLM | Verdict | Justification |
| --- | --- | --- | --- | --- |
| Modèle de la moyenne | ARIMA(0,1,0) sur le log-prix | ARIMA(0,0,0) sur les rendements | **Convergence** | Le rendement est le log-prix différencié une fois : les deux écritures désignent le même modèle. |
| Volatilité | GJR-GARCH(1,1) avec loi de Student | GARCH(1,1)-t en priorité, GJR et EGARCH à tester | **Convergence** | Nos tests confirment l'effet de levier : γ est significatif (p = 0,004). |
| Lien de long terme entre XOM et XLE | Cointégration testée (Engle-Granger, Johansen) : relation fragile | Aucun test de cointégration proposé | **Oubli du LLM** | Les deux log-prix sont I(1), et le LLM le sait. C'est précisément le cas où il faut tester la cointégration. |
| Rendement passé de XLE pour prévoir XOM | Granger robuste : p = 0,20, le passé de XLE n'améliore pas la prévision | Propose un ARMAX avec le rendement retardé de XLE | **Divergence** | Une idée raisonnable à tester, mais nos résultats la rejettent. Le LLM ne pouvait pas le savoir sans nos tests. |

## Prompt 2 — Vulgarisation

| Thème | Notre interprétation | LLM | Verdict | Justification |
| --- | --- | --- | --- | --- |
| Persistance de la volatilité | 0,999, gonflée par la rupture de 2020 ; 0,893 sur 2016–2019 | « Très persistante : le risque peut rester élevé longtemps » | **Simplification excessive** | Le LLM omet la valeur de 2016–2019 alors qu'elle figurait dans le prompt. Il prend la persistance à la lettre (erreur 7 de la grille). |
| Explication des pics de volatilité | On ne donne que des dates (2020-03-19, 2022-06-24) | « Tensions sur le marché énergétique en 2022 » | **Explication ajoutée par le LLM** | Cette cause ne figurait pas dans le prompt : le LLM l'a ajoutée lui-même (erreur 5 de la grille). Elle doit être vérifiée par une source, voir `docs/sources.md`. |
