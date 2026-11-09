# Mini-projet Séries Temporelles — TEK-UP 2026

**Auteurs :** Aziz Bellaaj, Mohamed Yassine Khiari

Modélisation, prévision et diagnostic de la série multidimensionnelle **XOM (ExxonMobil) + XLE (Energy Select Sector ETF)**, cours journaliers Yahoo Finance du 2016-01-01 au 2025-12-31. Le Brent (`BZ=F`) sert de variable exogène.

Modèles : ARIMA/SARIMA, VAR, cointégration/VECM, GARCH (en Python **et** en R), LSTM/GRU et hybride ARIMA+LSTM (en **Python uniquement**). L'évaluation se fait sur un tableau unique de métriques complété d'un test de Diebold-Mariano.

## Prérequis

- Python **3.11** (les versions de `requirements.txt` sont figées pour 3.11)
- R **≥ 4.3** (testé avec R 4.6.2 ; les binaires Windows du snapshot CRAN évitent Rtools)
- Windows : **Microsoft Visual C++ Redistributable** (requis par TensorFlow)
- Windows : le projet peut être placé **n'importe où**. TensorFlow installe un fichier dont le chemin, relatif à l'environnement Python, fait 161 caractères. Si le projet est dans un dossier profond, `.venv` dépasserait la limite Windows de 260 caractères et pip échouerait (`OSError: No such file or directory … tensorflow\include\…`). `install.py` le détecte et crée alors l'environnement dans un dossier court (`%USERPROFILE%\.venvs\ts-project`).
- **Pandoc** (requis par `rmarkdown` pour produire `classical_R.html` ; inclus dans RStudio, sinon `winget install JohnMacFarlane.Pandoc`)
- Connexion internet au premier lancement. Les données sont ensuite relues depuis le cache `data/raw/`.

Installation testée le 2026-11-08 sous Windows 10 :

```powershell
winget install Python.Python.3.11 RProject.R Microsoft.VCRedist.2015+.x64 Git.Git JohnMacFarlane.Pandoc
```

**Vérification sur environnement vierge (2026-11-08)** : clone neuf depuis GitHub, sorties supprimées, environnement Python neuf (`pip install -r requirements.txt`, 6 min 30 s) et bibliothèque R vide (`Rscript install_packages.R`, 50 s). Le notebook Python s'exécute sans erreur en environ 13 min, le Rmd en environ 1 min 30 s, et tous les tableaux de résultats sont identiques à ceux du dépôt.

`requirements.txt` fige les dépendances directes ; `requirements-lock.txt` contient l'environnement exact vérifié (toutes les dépendances transitives).

## Installation et exécution (recommandé)

Depuis la racine du projet, avec Python 3.11 :

```powershell
python install.py      # environnement Python (emplacement choisi automatiquement) + packages R
python run_all.py      # exécute main_python.ipynb puis rend classical_R.Rmd
```

`install.py` vérifie aussi l'installation (`pip check`, versions affichées) et écrit l'emplacement de l'environnement dans `.venv-path`, que `run_all.py` relit.

`run_all.py` utilise toujours cet environnement, même si un autre est déjà activé dans le terminal (VS Code par exemple) ; il affiche le Python du noyau Jupyter pour contrôle. Le notebook est enregistré après chaque cellule (`cellule N/83` dans la console) : on peut suivre l'exécution en ouvrant `notebooks/main_python.ipynb` dans VS Code ou Jupyter, sans le modifier pendant l'exécution (environ 13 min, dont 8 min pour la grille LSTM/GRU de la cellule 65).

## Installation manuelle

Si le chemin du projet est court (ou si les chemins longs de Windows sont activés) :

```powershell
# Python
python -m venv .venv
.venv\Scripts\Activate.ps1          # Linux/macOS : source .venv/bin/activate
pip install -r requirements.txt
python -m src.utils                 # contrôle : racine, config, seed, versions

# R
Rscript install_packages.R          # installe et affiche les versions
```

Ordre d'exécution :

1. `notebooks/main_python.ipynb` : étude complète de bout en bout (données → EDA → modèles → évaluation → extensions).
2. `notebooks/classical_R.Rmd` : socle classique (section 3) en R, et vérifications R de Diebold-Mariano et du DCC. Il relit les tableaux exportés par le notebook Python : l'exécuter en second.

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
| `rapport/` | Rapport final : `rapport.docx` et `rapport.pdf`, source `rapport.md`, reconstruction par `python rapport/build_rapport.py` (Pandoc ; PDF via Microsoft Word si installé) |

## Note de transparence

Le code a été développé avec l'assistance de Claude Code. La section 5 (LLM) a été réalisée séparément ; prompts et réponses sont archivés dans `llm/`.
