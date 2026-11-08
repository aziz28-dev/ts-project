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
