# Mini-projet Séries Temporelles — TEK-UP 2026

**Auteurs :** Aziz Bellaaj, Mohamed Yassine Khiari

Modélisation, prévision et diagnostic de la série multidimensionnelle **XOM (ExxonMobil) + XLE (Energy Select Sector ETF)**, cours journaliers Yahoo Finance du 2016-01-01 au 2025-12-31. Le Brent (`BZ=F`) sert de variable exogène.

Modèles : ARIMA/SARIMA, VAR, cointégration/VECM, GARCH (en Python **et** en R), LSTM/GRU et hybride ARIMA+LSTM (en **Python uniquement**). L'évaluation se fait sur un tableau unique de métriques complété d'un test de Diebold-Mariano.

## Prérequis

- Python **3.11** (les versions de `requirements.txt` sont figées pour 3.11)
- R **≥ 4.3** (testé avec R 4.6.2 ; les binaires Windows du snapshot CRAN évitent Rtools)
- Windows : **Microsoft Visual C++ Redistributable** (requis par TensorFlow)
- **Pandoc** (requis par `rmarkdown` pour produire `classical_R.html` ; inclus dans RStudio, sinon `winget install JohnMacFarlane.Pandoc`)
- Connexion internet au premier lancement. Les données sont ensuite relues depuis le cache `data/raw/`.

Installation testée le 2026-11-08 sous Windows 10 :

```powershell
winget install Python.Python.3.11 RProject.R Microsoft.VCRedist.2015+.x64 Git.Git JohnMacFarlane.Pandoc
```

`requirements.txt` fige les dépendances directes ; `requirements-lock.txt` contient l'environnement exact vérifié (toutes les dépendances transitives).

## Installation

```powershell
# Python
python -m venv .venv
.venv\Scripts\Activate.ps1          # Linux/macOS : source .venv/bin/activate
pip install -r requirements.txt
python -m src.utils                 # contrôle : racine, config, seed, versions

# R
Rscript install_packages.R          # installe et affiche les versions
```

## Ordre d'exécution

1. `notebooks/main_python.ipynb` : étude complète de bout en bout (données → EDA → modèles → évaluation).
2. `notebooks/classical_R.Rmd` : socle classique (section 3) en R.

```powershell
jupyter nbconvert --to notebook --execute --inplace notebooks/main_python.ipynb
Rscript -e "rmarkdown::render('notebooks/classical_R.Rmd')"
```

Aucune intervention manuelle n'est nécessaire. Tous les paramètres (tickers, dates, split 90/10, horizon, seed 42) sont dans `config.yaml`.

## Arborescence

| Dossier | Contenu |
| --- | --- |
| `src/` | Logique Python (données, EDA, modèles, évaluation, utilitaires) |
| `notebooks/` | Notebooks Python et R : appels + interprétations |
| `data/raw/` | Cache CSV des téléchargements Yahoo (versionné) |
| `data/processed/` | Séries préparées, train/test (régénérées) |
| `outputs/figures/`, `outputs/tables/` | Figures `figNN_nom.png` et tableaux CSV du rapport |
| `llm/` | Prompts et réponses intégrales du LLM (section 5) |
| `docs/` | Cahier des charges, plan, journal de bord |
| `report/` | Rapport final |

## Note de transparence

Le code a été développé avec l'assistance de Claude Code. La section 5 (LLM) a été réalisée séparément ; prompts et réponses sont archivés dans `llm/`.
