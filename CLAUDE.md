# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Projet

Mini-projet Séries Temporelles TEK-UP 2026 (Data Science & IA) : modélisation, prévision et diagnostic d'une série multidimensionnelle, de l'ARIMA au LSTM/GRU, avec cointégration, GARCH et usage critique d'un LLM. Rédaction et commentaires en **français**.

Documents de référence (dans `docs/`) :
- `docs/cahier_des_charges.md` : cahier des charges, **fait foi** en cas de conflit.
- `docs/PLAN.md` : plan validé (phases 0 à 9, table de traçabilité des exigences, prompts par phase, checklist d'envoi).

État actuel : phase 0 terminée, installation vérifiée (Python 3.11.9 dans `.venv`, R 4.6.2). Prochaine étape : phase 1 (données).

Environnement local (Windows) :
- Python du projet : `.venv\Scripts\python.exe`. Le `python3.exe` du PATH est le raccourci Microsoft Store, ne pas l'utiliser.
- Rscript : `C:\Program Files\R\R-4.6.2\bin\Rscript.exe` (pas dans le PATH) ; packages dans la bibliothèque personnelle `R_LIBS_USER`.
- Un script lancé hors de la racine a besoin de `PYTHONPATH` pointant sur la racine pour importer `src`.
- quantmod : `to` exclut la date de fin, contrairement à `config.yaml`. Utiliser `to = end + 1 jour` pour aligner l'échantillon R sur Python.

## Données

- Option A Finance : XOM + XLE (`Adj Close`), Yahoo Finance, 2016-01-01 → 2025-12-31, journalier. Brent (`BZ=F`) en 3e variable ou variable exogène.
- Paramètres centralisés dans `config.yaml` : tickers, dates, split 0.9, horizon 10, seed 42.
- `yfinance` avec `auto_adjust=False`. Cache CSV dans `data/raw/` : relire le cache si le téléchargement échoue.
- Calendrier boursier irrégulier : **ne pas faire de ffill** (cela crée des rendements nuls artificiels qui biaisent GARCH). Les modèles reçoivent un index positionnel ; les dates servent aux graphes.
- Outliers des rendements : **conservés** (chocs réels, modélisés par GARCH), signalés par une variable indicatrice. Ne jamais supprimer ou corriger une observation sans le justifier dans `docs/journal.md`.

## Architecture prévue

```
config.yaml, requirements.txt (Python 3.11), install_packages.R (R ≥ 4.3), README.md
src/        data.py, eda.py, classical.py (ARIMA/VAR/VECM/GARCH + diagnostics),
            deep.py (LSTM/GRU/hybride, walk-forward), evaluation.py (métriques, Diebold-Mariano), utils.py (seed, chemins)
notebooks/  main_python.ipynb (étude complète de bout en bout), classical_R.Rmd (socle §3 en R)
llm/        prompts/ et responses/ (intégrales, avec modèle + date)
outputs/    figures/figNN_nom.png, tables/*.csv
docs/       cahier_des_charges.md, PLAN.md, journal.md (résultats et décisions par phase, sert à rédiger le rapport)
```

La logique va dans `src/*.py` ; les notebooks se limitent aux appels et aux interprétations en Markdown. Le socle classique (§3 : ARIMA, VAR, VECM, GARCH) doit exister **en R ET en Python**. La partie avancée (§4) est en Python uniquement et doit être identifiée comme telle.

Commandes prévues, une fois la phase 0 faite :
- `pip install -r requirements.txt` / `Rscript install_packages.R`
- `jupyter nbconvert --to notebook --execute notebooks/main_python.ipynb` : contrôle d'exécution de bout en bout
- `Rscript -e "rmarkdown::render('notebooks/classical_R.Rmd')"`

## Règles méthodologiques (non négociables)

- Split chronologique 90/10, jamais de shuffle, jamais de k-fold classique (walk-forward / `TimeSeriesSplit`).
- Scalers et transformations ajustés sur le train uniquement. Hyperparamètres choisis sur les folds du train, jamais sur le test.
- Chaque modèle a un diagnostic de résidus complet : Ljung-Box (ddl corrigés de p+q), Jarque-Bera (Shapiro-Wilk rejette presque toujours sur environ 2 000 points), ARCH-LM. Un modèle sans diagnostic n'est pas noté.
- ADF **et** KPSS (hypothèses nulles opposées), avec la spécification et les retards indiqués.
- SARIMA testé (s = 5) puis écarté si non pertinent, avec justification chiffrée.
- VAR sur les rendements (stationnaires) ; cointégration (Engle-Granger, Johansen) et VECM sur les log-prix.
- Granger = prédictibilité incrémentale, jamais « causalité ». GARCH prévoit l'amplitude des variations, pas leur sens.
- GARCH : comparer loi normale et loi de Student ; vérifier α + β < 1 ; tester les résidus standardisés (Ljung-Box sur z et z², ARCH-LM). La variance prévue est évaluée à part (QLIKE ou MSE face à r²).
- LSTM/GRU : prédire les **log-rendements** (sortie directe h = 10) puis reconstruire le prix, jamais entraîner sur les prix bruts. Early stopping sur une validation chronologique, 3 seeds, courbes de perte sauvegardées.
- Baseline marche aléatoire systématique. Prévision rolling origin h = 1..10 sur tout le test (ré-estimation des modèles classiques tous les 20 jours).
- Métriques MSE/RMSE/MAE/MAPE sur le **prix en dollars**, jamais de MAPE sur les rendements, dans **un seul tableau** récapitulatif.
- Diebold-Mariano implémenté à la main (variance HAC avec h−1 retards, correction HLN) ; `forecast::dm.test` en R.
- Chaque test est rapporté avec H₀, statistique, p-value et décision. Chaque figure est numérotée et suivie d'une interprétation écrite.
- **Ne jamais inventer un résultat** : toute valeur citée vient d'une exécution réelle. Les échecs (SARIMA écarté, baseline non battue, absence de cointégration) sont rapportés, pas contournés.

## Code

- Seed 42 partout (`random`, `numpy`, `tensorflow`, `set.seed(42)`). Chemins relatifs uniquement (`pathlib`, `here::here()`).
- La première cellule de chaque notebook affiche les versions des packages.
- Commentaires en français : une ligne par bloc qui explique **pourquoi** ce choix, pas ce que fait le code.
- Piège : `pmdarima` casse avec numpy ≥ 2. Figer `numpy<2` ou utiliser `statsforecast.AutoARIMA` et le signaler dans le rapport.
- Dépôt git initialisé en phase 0 ; un commit à la fin de chaque phase.

## Manière de travailler

- Une phase du plan par session ; exécuter le code et montrer les sorties réelles avant de passer à la suivante.
- À la fin de chaque phase, consigner résultats, décisions et justifications dans `docs/journal.md`, et mettre à jour le statut de la table de traçabilité.
- Signaler tout résultat inattendu au lieu de le contourner.
- L'étudiant doit pouvoir défendre chaque ligne en soutenance : expliquer les choix (pourquoi, alternative, risque) quand on le demande.
- La phase 5 (LLM) se fait hors Claude Code.
