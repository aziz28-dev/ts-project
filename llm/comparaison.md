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
| Corrélation de 0,915 | Corrélation des **chocs** (résidus du VAR) le même jour | « Les **rendements** ont une corrélation de 0,915 » | **Imprécision** | Le LLM change le sens du chiffre fourni : il s'agit des chocs, pas des rendements bruts. La valeur est proche, mais ce n'est pas la même grandeur. |
| FEVD | 84 % ou 0,3 % selon l'ordre de Cholesky : on ne peut pas dire qui entraîne qui | Non mentionnée | **Oubli du LLM** | Le résultat le plus piégeux du prompt est passé sous silence. Le décideur ne saura pas que la part de XLE n'est pas identifiable. |
| Test de Granger | Prédictibilité incrémentale, non robuste (HC3, p = 0,20) | « Le test suggère initialement une **influence** de XLE sur XOM » | **Vocabulaire causal** | Granger mesure une prédictibilité, pas une influence (erreur 2 de la grille). L'erreur reste légère, car le LLM écrit ensuite qu'il n'y a pas de « relation de causalité solide ». |

## Prompt 3 — Essai sans données (03a)

Le prompt a été envoyé par erreur avant la phase 6, avec les champs de données encore vides. L'essai est conservé, car il révèle le comportement du LLM quand il n'a aucun chiffre.

| Thème | Notre interprétation | LLM | Verdict | Justification |
| --- | --- | --- | --- | --- |
| Données absentes | — | « Il serait incorrect de formuler une recommandation sans connaître ces résultats » | **Bon comportement** | Le LLM n'invente aucun chiffre et signale que les données manquent. |
| Achat si la prévision est « favorable » | La marche aléatoire prévoit le même prix chaque jour (rendement prévu nul) | Scénarios 1 et 2 : acheter si la prévision à 1 ou 5 jours indique une évolution favorable | **Erreur de raisonnement** | Avec ARIMA(0,1,0), la prévision ponctuelle ne peut jamais être « favorable » : ces scénarios ne peuvent pas se produire. Le LLM décrit le modèle correctement, mais n'en tire pas la conséquence. |
| « Direction des prévisions » | Le GARCH prévoit l'amplitude, pas le sens (§3.3) | La décision doit tenir compte de « la direction des prévisions » et de la volatilité | **Erreur 3 de la grille** | Aucun des deux modèles ne fournit de direction. Seule l'amplitude du risque est prévisible. |

## Bilan

| Verdict | Nombre |
| --- | --- |
| Convergences | 2 |
| Divergence | 1 |
| Oublis du LLM | 2 |
| Simplification, imprécision ou ajout non fondé | 3 |
| Vocabulaire causal | 1 |

Sur les **faits principaux**, le LLM converge avec notre interprétation : marche aléatoire pour la moyenne, GARCH avec loi de Student et effet de levier pour la variance, aucun avantage des réseaux de neurones. Il n'invente aucune p-value. Ses erreurs sont plus subtiles :
- il **oublie** les résultats qui nuancent, comme la cointégration ou la dépendance de la FEVD à l'ordre ;
- il **simplifie** la persistance de la volatilité ;
- il **ajoute** des explications qu'on ne lui a pas fournies.

Un décideur qui lirait sa réponse seule aurait une image trop simple de la volatilité et du lien entre XOM et XLE.
