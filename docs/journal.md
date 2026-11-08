# Journal de bord

Résultats, décisions et justifications, phase par phase. Sert de base à la rédaction du rapport.

## Phase 0 — Setup (2026-11-08)

- Arborescence créée selon `docs/PLAN.md` §4.
- Paramètres centralisés dans `config.yaml` (XOM/XLE/BZ=F, 2016-01-01 → 2025-12-31, split 0.9, h = 10, seed 42).
- `numpy` figé en 1.26.4 : `pmdarima` 2.0.4 et `tensorflow` 2.16 ne supportent pas numpy 2.
- `scikit-learn` figé en 1.5.2 : `pmdarima` 2.0.4 casse avec 1.6.
- R : versions figées par un snapshot CRAN daté (Posit Package Manager, 2025-10-01).
- Git 2.56 installé (winget), dépôt initialisé sur la branche `main`, `.gitattributes` en LF.
- Installation Python/R : **non vérifiée**, Python et R absents de la machine au 2026-11-08.
