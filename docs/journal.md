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
