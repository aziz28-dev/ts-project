# Journal de bord

Résultats, décisions et justifications, phase par phase. Sert de base à la rédaction du rapport.

## Phase 0 — Setup (2026-11-08)

- Arborescence créée selon `docs/PLAN.md` §4.
- Paramètres centralisés dans `config.yaml` (XOM/XLE/BZ=F, 2016-01-01 → 2025-12-31, split 0.9, h = 10, seed 42).
- `numpy` figé en 1.26.4 : `pmdarima` 2.0.4 et `tensorflow` 2.16 ne supportent pas numpy 2.
- `scikit-learn` figé en 1.5.2 : `pmdarima` 2.0.4 casse avec 1.6.
- R : versions figées par un snapshot CRAN daté (Posit Package Manager, 2025-10-01).
- Git 2.56 installé (winget), dépôt initialisé sur la branche `main`, `.gitattributes` en LF. Publié sur github.com/aziz28-dev/ts-project.
- Installés via winget : Python 3.11.9, R 4.6.2, Visual C++ Redistributable (DLL exigée par TensorFlow).
- R : packages installés dans la bibliothèque personnelle (Program Files non accessible en écriture). Snapshot CRAN déplacé au 2026-10-01 : celui du 2025-10-01 n'a pas de binaires pour R 4.6, ce qui aurait imposé Rtools.
- Python : `cmdstanpy` figé en 1.2.5, car la 1.3 rejette le CmdStan embarqué par prophet 1.1.6. `keras` 3.15.1 et `yfinance` 0.2.66 figés. Environnement exact dans `requirements-lock.txt`.
- Test d'installation sur données simulées, tout OK :
  - R : 16 packages chargés ; auto.arima, Ljung-Box, ArchTest, Jarque-Bera, VAR, ca.jo, ugarchfit, dm.test ; quantmod récupère XOM.
  - Python : utils/config/seed ; pmdarima, ADF/KPSS, Ljung-Box, ARCH-LM, VAR, Engle-Granger, Johansen, GARCH-t (arch), LSTM et GRU (TF 2.16.2), Prophet ; yfinance récupère XOM avec la colonne `Adj Close`.
- **À traiter en phase 1** : bornes de fin différentes. Pour décembre 2025, quantmod (`to = "2025-12-31"`) renvoie 21 lignes, yfinance (`end = "2026-01-01"`) en renvoie 22 : le `to` de quantmod exclut la date de fin. Il faudra passer `to = "2026-01-01"` en R pour avoir exactement le même échantillon dans les deux langages.

## Phase 1 — Données et préparation (2026-11-08)

**Implémentation** : `src/data.py` (téléchargement + cache, alignement, variables dérivées, split) ; `notebooks/main_python.ipynb` §1. Sorties : `outputs/tables/tab01_manquants.csv`, `tab02_variables.csv`, `tab03_split.csv`, `outputs/figures/fig01_prix_train_test.png`, `data/processed/{panel,train,test}.csv`.

**Décisions et justifications**
- Cache **prioritaire** sur le téléchargement : Yahoo recalcule l'Adj Close rétroactivement à chaque dividende ; seul le CSV versionné (`data/raw/`, téléchargé le 2026-11-08) garantit des résultats identiques. `refresh=True` pour forcer.
- Variable de prix : `Adj Close` (Close de Yahoo déjà ajusté des splits ; Adj Close ajuste en plus les dividendes). XOM au 2016-01-04 : Close 77,46 $ contre Adj Close 49,00 $.
- Calendrier : jointure interne XOM/XLE ; Brent rattaché par jointure à gauche, **sans ffill** (éviter des rendements nuls fictifs qui biaisent GARCH). Pas de `freq="B"` sur l'index (cela réinsérerait les 94 jours fériés de bourse) ; la fréquence « jours de bourse » est déclarée dans `config.yaml`.
- Rendements en % (100 × diff log), volatilité réalisée 21 j annualisée (√252), MM 50 j : fenêtres tournées vers le passé uniquement, donc pas de fuite train → test.

**Résultats**
- XOM et XLE : 2 514 jours de bourse, du 2016-01-04 au 2025-12-31, 0 NaN, 0 doublon, calendriers identiques.
- Brent (`BZ=F`) : 2 515 cotations ; 2 jours absents du calendrier commun (2016-10-10, 2016-11-11), restés NaN ; 3 cotations hors calendrier écartées (2023-11-23, 2025-01-09, 2025-07-04). Série continue de contrats à terme : sauts possibles au changement d'échéance, à rappeler en section 7.
- Split 90/10 : train 2 262 jours (2016-01-04 → 2024-12-27), test 252 jours (2024-12-30 → 2025-12-31).
- Corrélation des rendements journaliers XOM/XLE : 0,914.
- Le test est plus calme que le train : écart-type des rendements XOM 1,48 % contre 1,78 % ; volatilité réalisée maximale XOM 47,4 % contre 108,9 % (XLE : 61,1 % contre 149,9 %). Choc visible début avril 2025. À rappeler dans les limites : les métriques du test reflètent ce régime.

**À faire plus tard**
- R (phase 3d) : `quantmod::getSymbols(to = "2026-01-01")`, car `to` exclut la date de fin. Le plus simple est de relire les CSV de `data/raw/` pour garantir le même échantillon qu'en Python.

## Phase 2 — Analyse exploratoire (2026-11-08)

**Implémentation** : `src/eda.py` ; `notebooks/main_python.ipynb` §2. Figures 2 à 8, tableaux tab04 à tab10, indicatrices `data/processed/outliers.csv`.

**Décisions et justifications**
- Tests et outils d'identification (stats, ACF/PACF, STL, ADF/KPSS) calculés sur le **train uniquement** (pas de fuite) ; graphiques descriptifs sur toute la période.
- Outliers : IQR glissant sur les 63 jours **précédents** (shift(1)), k = 3 (k = 1,5 signalerait des centaines de jours avec ces queues épaisses). Détection sur toute la période pour que l'indicatrice existe aussi sur le test. **Conservés** (chocs réels, communs aux deux actifs, objet même du GARCH) + indicatrices sauvegardées.
- KPSS : p-value bornée à [0,01 ; 0,10] par statsmodels, affichée « < 0,01 » / « > 0,10 » ; décision sur statistique vs valeur critique.
- Ajouts de rigueur, non prévus au plan : Ljung-Box robuste (rendements standardisés par la vol. passée, et hors 2020) ; effet jour de la semaine (Kruskal-Wallis, Levene) ; force STL (Wang-Smith-Hyndman) ; Zivot-Andrews (rupture structurelle).

**Résultats (train, 2 261 rendements)**
- Rendement moyen 0,032 %/jour (≈ 8 %/an), non significatif (t ≈ 0,85 XOM, 0,78 XLE). Volatilité annualisée 28,3 % (XOM), 30,5 % (XLE).
- Skewness −0,16 (XOM), −0,89 (XLE) ; excès de kurtosis 6,6 et 16,4 ; Jarque-Bera 4 142 et 25 747, p < 0,0001 : normalité rejetée → GARCH avec loi de Student.
- ACF log-prix : ACF(1) = 0,998, ACF(21) = 0,959, 40/40 retards significatifs ; PACF : un seul pic au retard 1 → marche aléatoire.
- ACF rendements : |ACF| ≤ 0,064 (XOM), 0,129 au retard 7 (XLE). Ljung-Box rejette (Q(10) p = 0,0001 XOM) **mais** le rejet disparaît sur rendements standardisés (p = 0,98) et hors 2020 (p = 0,44) : artefact d'hétéroscédasticité, bruit blanc en moyenne.
- ACF rendements² : 40/40 retards significatifs (XOM), max 0,32 ; Ljung-Box Q(10) = 1 464 → effets ARCH forts et persistants.
- STL : force de saisonnalité F_S = 0,000 / 0,032 / 0,000 (périodes 5 / 21 / 252, XOM). Pas d'effet jour de la semaine en moyenne (Kruskal-Wallis p = 0,59 XOM, 0,78 XLE) ; variance du lundi un peu plus forte pour XLE (Levene p = 0,035).
- Outliers : 15 (XOM) et 18 (XLE), dont 10 chacun en 2020, 11 jours communs ; test : 2 (XOM) et 4 (XLE), tous du 3 au 10 avril 2025. Limite : bornes trop larges après mars 2020 (baisse de −9,2 % du 2020-06-11 non signalée).
- ADF/KPSS : log-prix non stationnaires (ADF p ≥ 0,53 ; KPSS p < 0,01, constante et constante + tendance) ; rendements stationnaires (ADF p < 0,0001 ; KPSS p > 0,10). Zivot-Andrews : racine unitaire non rejetée même avec rupture (p de 0,18 à 0,48 ; ruptures estimées janvier 2020 et décembre 2021).

**Conclusion : d = 1, D = 0** pour les log-prix de XOM et de XLE (I(1)) ; rendements I(0).

**Pour la phase 3** : ARIMA(0,1,0) comme référence, constante probablement non significative ; SARIMA s = 5 à estimer puis écarter ; VAR sur rendements ; cointégration testable (deux séries I(1)) ; GARCH-t.

### Phase 2 — compléments de robustesse (2026-11-08)

Ajoutés après relecture critique, pour anticiper deux objections probables :
- **Test de moyenne robuste** (`eda.mean_test`, tab04b) : t classique 0,85 (XOM) / 0,78 (XLE) ; t HAC Newey-West (7 retards) 0,86 / 0,76, p = 0,39 / 0,45. Même conclusion : moyenne non significative.
- **Sensibilité des outliers** (`eda.outlier_sensitivity`, tab08b et tab08c) : 16 réglages (fenêtre 21/63/126/252 × k 2/2,5/3/3,5). Le nombre de jours varie de 11 à 66 selon le réglage, mais un noyau de 11 jours (XOM) et 14 (XLE), signalés par au moins 12 réglages sur 16, est entièrement retrouvé par le réglage de référence. 4 jours limites par actif. Impact limité : les outliers sont conservés, seule l'indicatrice dépend du réglage.

Sources des événements (2020-03-09, 2020-11-09, avril 2025) : trouvées et intégrées au notebook le 2026-11-08, regroupées dans `docs/sources.md`. Recoupement : le Brent de notre cache perd −24,1 % le 2020-03-09, comme la baisse de 24 % à la clôture rapportée par la presse.

## Phase 3.1 — ARIMA / SARIMA (2026-11-08)

**Implémentation** : `src/classical.py` (estimation, comparaison, robustesse des critères, racines, auto_arima, diagnostics) ; notebook §3.1. Tableaux tab11 à tab16, figures 9 et 10.

**Décisions de méthode**
- ARIMA(p,1,q) du log-prix estimé comme ARMA(p,q) sur r_t = 100 × Δ ln P_t : la constante est la dérive, tous les modèles ont les mêmes n = 2 261 observations (AIC/BIC comparables). Première tentative avec `trend="t"` sur le niveau abandonnée : dérive croissante dans le temps, mauvaise spécification.
- d = 1 imposé (§2.7) ; vérifié par `pmdarima.ndiffs` (ADF, KPSS, PP → 1) et `nsdiffs` (OCSB, CH → 0).
- Erreurs-types robustes (sandwich QMLE) à cause des effets ARCH.
- `auto_arima` exhaustif (stepwise=False, p, q ≤ 5), avec AIC puis avec BIC.

**Résultats**
- Manuel : ARIMA(0,1,0) meilleur AIC (9 037,10) et BIC (9 042,83) ; AR(1) −0,024 (p = 0,49), MA(1) −0,023 (p = 0,50), dérive 0,032 (p = 0,40) non significatifs. ARIMA(1,1,1) : coefficients AR/MA quasi opposés.
- auto_arima AIC → ARIMA(3,1,2) (AIC 9 021,27, soit −15,8 ; BIC +12,8) ; BIC → ARIMA(0,1,0). Minimum AIC isolé dans la grille.
- ARIMA(3,1,2) : racines AR (module 1,047) et MA (module 1,075) quasi identiques, cycle de 2,36 jours → quasi-annulation, modèle quasi non identifié.
- Robustesse : ΔAIC de (3,1,2) −15,8 → −7,8 hors 2020 → +9,2 sur rendements standardisés. SARIMA(1,0,0)[5] −5,7 → +1,7 → +1,9.
- SARIMA s = 5 : AIC −5,7 et LR p = 0,006 en faveur, mais coefficient non significatif en robuste (0,058, p = 0,12), ΔBIC = 0,05, gain disparu hors 2020. Seuls 82 % des couples (t, t−5) sont le même jour de semaine. **Écarté** — résultat plus nuancé que prévu par le plan, rapporté tel quel.
- Diagnostics : ARIMA(0,1,0) → LB brut rejette, LB standardisé non (p = 0,98) ; JB = 4 142 ; ARCH-LM(5) = 441 (p < 0,0001). ARIMA(3,1,2) → LB standardisé rejette (p = 0,013), JB = 3 376, ARCH-LM(5) = 383.

**Décision** : ARIMA(0,1,0) sans dérive (marche aléatoire) retenu ; ARIMA(3,1,2) conservé comme concurrent pour l'évaluation hors échantillon (§6, Diebold-Mariano). Effets ARCH et queues épaisses → §3.3 (GARCH-t).

## Phase 3.2 — VAR, Granger, cointégration, VECM (2026-11-08)

**Implémentation** : `src/classical.py` (section 3.2) ; notebook §3.2. Tableaux tab17 à tab24, figure 11.

**Résultats**
- Ordre du VAR (max 10) : AIC 9, FPE 9, HQ 7, BIC 0. Hors 2020 et sur rendements standardisés : **0 pour les quatre critères**. Le saut de l'AIC au retard 7 correspond à l'autocorrélation de XLE due à 2020 (§2.3).
- Diagnostics : tous les VAR stables. Portmanteau (Hosking ajusté, codé à la main, vérifié identique à statsmodels) sur résidus standardisés : VAR(0) p = 0,77 ; VAR(1) p = 0,038 ; VAR(7) et VAR(9) p < 0,0001 → ajouter des retards crée de la structure parasite (même signature que l'ARIMA(3,1,2)). JB et ARCH-LM rejettent partout. Corrélation des résidus 0,915 : lien contemporain.
- Coefficients du VAR(1) : +0,10 (XOM passé) et −0,13 (XLE passé) sur l'échantillon complet ; ≈ ±0,01 à 0,03 hors 2020.
- Granger : F classique significatif presque partout ; HC3 robuste → rien à 1 retard, XLE → XOM seulement à 7 et 9 retards (p = 0,034 et 0,016) ; hors 2020, aucun test robuste ne rejette à 5 %. Conclusion : pas de prédictibilité croisée robuste (cohérent avec l'efficience).
- Engle-Granger (constante) : p = 0,037 (XOM sur XLE) et 0,024 (XLE sur XOM) ; avec tendance : 0,105 et 0,072.
- Johansen (constante) : k = 0 (ordre robuste) trace 14,73 → rejet à 10 % seulement ; k = 6 et 8 → rejet à 5 %. r ≤ 1 jamais rejeté.
- Sous-périodes : 2016-2019 EG p = 0,081 ; 2021-2024 EG p = 0,232 → relation non significative dans chaque moitié.
- **Cointégration jugée faible et fragile** ; VECM estimé conditionnellement (r = 1, k = 0, constante restreinte).
- VECM : β = (1 ; −1,128), constante −0,453 ; α(XOM) = −0,0006 (p = 0,93), α(XLE) = +0,0093 (p = 0,16) ; β'α = −0,0110 → **demi-vie de 62,6 jours** (identique avec un AR(1) de l'écart, ρ = 0,989). Portmanteau standardisé p = 0,53.

**Écart au plan** : la formule de demi-vie ln(0,5)/ln(1 + α) du plan suppose qu'un seul actif s'ajuste. En bivarié, la bonne vitesse est β'α (on obtiendrait sinon plus de 1 200 jours avec α(XOM)).

**Pour la section 6** : VAR(1) et VECM comme candidats multivariés ; la marche aléatoire (= VAR(0) sans constante) reste la référence.

**Pondération de XOM dans XLE** : 24,47 % au 2026-11-05 (StockAnalysis), premier composant devant Chevron (18,78 %) ; valeur historique sur 2016-2024 non vérifiée. Voir `docs/sources.md`.

## Phase 3.3 — GARCH (2026-11-08)

**Implémentation** : `src/classical.py` (section 3.3) ; notebook §3.3. Tableaux tab25 à tab28, figures 12 à 14.

**Résultats**
- ARCH-LM sur les résidus de la marche aléatoire : 441,2 (5 retards), 491,6 (10), p < 0,0001.
- 4 structures × 3 lois, moyenne nulle. Student ≫ normale (+37,5 de log-vraisemblance, BIC −67) ; Student asymétrique et ordres supérieurs n'apportent rien. **GJR(1,1)-t** meilleur AIC et BIC (BIC −0,5 seulement face au GARCH(1,1)-t ; LR = 8,2, p ≈ 0,004). Constante : μ = 0,027 (p = 0,27), BIC +6,5 → moyenne nulle.
- GJR(1,1)-t : ω = 0,0094 (p = 0,066), α = 0,043, γ = 0,042 (p = 0,004), β = 0,935, ν = 7,47. Réaction aux baisses α + γ = 0,085, deux fois celle aux hausses.
- Persistance 0,9993 (GJR), 0,9990 (GARCH) ; variance de long terme impliquée 13,7 et 10,2 %², contre 3,18 %² observée → invraisemblable. Sous-périodes (GARCH(1,1)-t) : 2016-2019 persistance 0,893 (demi-vie 6 jours) ; 2021-2024 0,996 (172 jours). **Persistance gonflée par la rupture de 2020** (Lamoureux et Lastrapes, 1990).
- Résidus standardisés du GJR : LB z p = 0,97 ; ARCH-LM(5) 441 → 14,0 (−97 %) mais encore p = 0,016 ; LB z² p = 0,046 (10) et 0,33 (20) ; KS contre Student p = 0,46 ; excès de kurtosis 6,6 → 1,5. GARCH(1,2)-t et GARCH(1,1) normal suppriment le reste d'ARCH, mais le premier est mal identifié (β non significatifs) et le second a une moins bonne loi.
- Volatilité conditionnelle : corrélation 0,97 avec la volatilité réalisée ; pics 40,5 % (2016-02-04), 107,4 % (2020-03-19), 46,9 % (2022-03-16, invasion), 52,2 % (2022-06-24, chute du pétrole en juin 2022). Le pic de 2022 est en juin, pas en février-mars comme le supposait le plan. Après le 2020-11-09, σ passe de 36,1 % à 52,5 % le lendemain.

**Décision** : ARIMA(0,1,0) + GJR(1,1)-t ; GARCH(1,1)-t comme référence.

**Pour la section 6** : couverture des intervalles à 95 % (GJR contre variance constante) ; prévision de variance (QLIKE) ; tester une ré-estimation glissante à cause de la persistance gonflée.

## Phase 3d — Socle classique en R et comparaison avec Python (2026-11-08)

**Implémentation** : `notebooks/classical_R.Rmd` (quantmod, forecast, tseries, urca, vars, sandwich, FinTS, rugarch), rendu dans `notebooks/classical_R.html` (versionné pour être lisible sans R). Le notebook Python exporte 88 valeurs clés (`tab29_reference_python.csv`, §3.4) ; le Rmd calcule les mêmes et produit `tab30_comparaison_R_python.csv`. Pandoc 3.13 installé (winget), requis par rmarkdown.

**Choix** : même cache CSV qu'en Python (données identiques) ; quantmod sert de vérification (2 514 lignes, écart relatif max 8,8e-07 : mêmes données). Mêmes réglages imposés quand c'est possible (retards KPSS et Zivot-Andrews de Python, maxlag ADF = 27). `urca::ca.jo` exige K ≥ 2 → comparaison de Johansen et du VECM avec 1 retard en différences, calculés aussi en Python.

**Résultat** : sur 88 grandeurs, 68 identiques (< 0,1 %), 14 très proches (< 2 %), 6 écarts expliqués et vérifiés. **Aucune conclusion ne change.**
- ADF log-prix (−0,948 contre −0,971) et Engle-Granger (−4,41 contre −3,46) : urca estime sur l'échantillon raccourci par le retard maximal ; avec les retards de Python imposés, R retrouve exactement −0,9714 et −3,4565. L'EG est très sensible aux 8 premières observations (janvier 2016, écart au plus haut).
- ARIMA(3,1,2) : R s'arrête sur un maximum local (−4 511,1) ; démarré aux coefficients de Python, il retrouve −4 504,631. Conséquence : auto.arima (AIC) choisit ARIMA(5,1,0) en R (AIC 9 033,74 dans les deux langages). Confirme l'instabilité du choix de l'AIC ; le BIC donne ARIMA(0,1,0) dans les deux.
- VAR, BIC : 1 en R contre 0 en Python, car VARselect ne teste que 1 à 10.
- GARCH : paramètres à 0,3–1,6 % près, log-vraisemblance environ 0,3 de moins ; cause : variance initiale (backcast 4,48 dans arch, moyenne des r² 3,18 dans rugarch). Aux paramètres Python, rugarch donne −4 045,62, et Python avec la convention de rugarch aussi.
- Granger : p-values à 0,1–0,3 % près (ddl système 4 514 dans vars, équation seule 2 257 en Python).
