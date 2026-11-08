# Prompt 1 — Hypothèses de modèles à partir des statistiques descriptives (cahier §5, tâche 1)

**But.** Voir quels modèles le LLM propose à partir des **seules** statistiques descriptives et des tests de stationnarité, **sans lui donner nos conclusions**. On compare ensuite ses propositions avec ce que nos analyses ont réellement montré (sections 2 et 3).

**Mode d'emploi.**
1. Ouvrir une **nouvelle** conversation, sans historique.
2. Coller le texte ci-dessous tel quel.
3. Enregistrer la réponse **intégrale** dans `llm/responses/01_hypotheses_<modele>_<date>.md`, en notant le nom exact du modèle et la date.

Toutes les valeurs viennent de `outputs/tables/tab04`, `tab05`, `tab09` et `tab16` (train : 2016-01-04 → 2024-12-27).

---

Je travaille sur une série temporelle financière journalière : le rendement logarithmique en pourcentage, r_t = 100 × Δln(P_t), de l'action Exxon Mobil (XOM, cours ajusté Yahoo Finance). J'ai aussi le rendement de l'ETF sectoriel de l'énergie XLE, dont XOM est le premier composant. L'échantillon d'apprentissage va du 2016-01-04 au 2024-12-27 (2 261 rendements).

Statistiques descriptives des rendements (en %) :

| | XOM | XLE |
| --- | --- | --- |
| Moyenne | 0,0319 | 0,0315 |
| Variance | 3,185 | 3,692 |
| Écart-type | 1,785 | 1,922 |
| Skewness | −0,163 | −0,890 |
| Excès de kurtosis | 6,62 | 16,44 |
| Min / max | −13,04 / +11,94 | −22,49 / +14,87 |
| Jarque-Bera | 4 142 (p < 0,001) | 25 747 (p < 0,001) |

Test de la moyenne de XOM (t de Student HAC, Newey-West, 7 retards) : t = 0,86, p = 0,39.

Tests de stationnarité :

| Série | Spécification | ADF (retards), p-value | KPSS (retards), p-value |
| --- | --- | --- | --- |
| Log-prix XOM | constante | −0,971 (18), p = 0,76 | 3,563 (29), p < 0,01 |
| Log-prix XOM | constante + tendance | −1,600 (18), p = 0,79 | 1,397 (29), p < 0,01 |
| Rendement XOM | constante | −10,557 (17), p < 0,001 | 0,144 (8), p > 0,10 |
| Log-prix XLE | constante | −1,503 (7), p = 0,53 | 3,586 (29), p < 0,01 |
| Rendement XLE | constante | −16,064 (6), p < 0,001 | 0,084 (9), p > 0,10 |

Autocorrélation et hétéroscédasticité des rendements de XOM :
- Ljung-Box Q(10) sur les rendements : 34,9 (p = 0,0001).
- Ljung-Box Q(10) sur les rendements divisés par la volatilité des 21 jours précédents : p = 0,98.
- Ljung-Box Q(10) sur les rendements, année 2020 exclue : p = 0,44.
- ACF des rendements au carré : 40 retards sur 40 hors de la bande à 95 %.
- ARCH-LM(5) : 441,2 (p < 0,001).

Questions :
1. Quels modèles me recommandes-tu de tester, et pourquoi ? Justifie chaque proposition par les statistiques ci-dessus.
2. Quel ordre de différenciation d retiens-tu ? Quels ordres p et q faut-il essayer en premier ?
3. Quelle loi d'innovation choisir, et pourquoi ?
4. Quels diagnostics faudra-t-il faire sur les résidus ?
5. Qu'est-ce qui pourrait te faire changer d'avis ?
