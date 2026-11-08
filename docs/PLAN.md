# Plan — Mini-projet Séries Temporelles TEK-UP 2026

Nov 8, 2026 · @Aziz

## 1. Synthèse du cahier des charges

Le projet demande une démarche de modélisation argumentée sur une série multidimensionnelle réelle : chaque choix doit être justifié par un test ou un diagnostic. Le barème le dit clairement : un SARIMA bien diagnostiqué vaut mieux qu'un LSTM mal validé.

**Alerte date limite.** Le cahier des charges fixe la remise au 12 octobre 2026 à 23h55, date déjà passée. Vérifie avec M. Dhouibi la nouvelle date avant de planifier (report possible ou coquille dans le document).

| Bloc | Contenu | Points | Sections |
| --- | --- | --- | --- |
| A — Fondamentaux | Données, EDA, ARIMA/SARIMA, VAR, diagnostics, prévision et évaluation | 10 | 1, 2, 3.1, 3.2, 6 |
| B — Avancé | GARCH diagnostiqué, LSTM/GRU avec validation walk-forward, comparaison | 4 | 3.3, 4.1 |
| C — IA générative | Hypothèses, vulgarisation, recommandations + limites, comparaison humain/LLM | 4 | 5 |
| D — Approfondissement | Cointégration/VECM, hybride, Prophet/N-BEATS, extensions section 7 | 2 | 3.2, 4.2, 4.3, 7 |

**Contraintes non négociables :**

- Split chronologique 90 % train / 10 % test, jamais aléatoire.
- Horizon de prévision h = 5 à 10 pas, avec intervalles quand le modèle le permet.
- Métriques MSE, RMSE, MAE, MAPE dans **un seul tableau** + test de Diebold-Mariano.
- Socle classique (section 3) codé en **R ET en Python** ; l'avancé dans un seul langage, identifié comme tel.
- Un modèle sans diagnostic de résidus n'est pas noté.
- Notebook exécutable de bout en bout sur machine vierge, seed fixée, versions documentées.
- Rapport de 15 à 25 pages hors annexes, Word ou PDF.
- Envoi en .zip (code + rapport + notebook) à ahmed.dhouibi@tek-up.de ; groupe de 5 maximum ; soutenance possible pour tout projet.

**En Derja :** el prof ma yhemmouch 9addech men modèle 3malt, yhemmou kol choix 3lech 3maltou w b anahou test. Kol modèle lezmou diagnostic mte3 résidus, sinon ma yetna9atch.

## 2. Choix de thématique recommandé

Recommandation : **Option A — Finance**, avec une action pétrolière et son indice sectoriel : **XOM (ExxonMobil) + XLE (ETF Energy Select Sector)**, en journalier, du 2016-01-01 au 2025-12-31 (10 ans, \~2 500 observations). Le baril de Brent (`BZ=F`) peut servir de 3e variable ou de variable exogène.

**Pourquoi ce choix :**

- **GARCH a un vrai sens** : les rendements financiers ont presque toujours des effets ARCH (bloc B, 4 points). Sur l'environnement, c'est souvent artificiel.
- **Cointégration plausible** : une action et l'ETF de son secteur sont l'exemple même du cahier des charges (bloc D).
- **Données triviales à récupérer** : `yfinance` (Python) et `quantmod` (R), même source dans les deux langages.
- **Événements connus à relier à la volatilité** : krach pétrolier 2016, COVID et prix négatif du WTI (avril 2020), guerre en Ukraine (2022).
- **Date de fin figée** = reproductibilité : le notebook donne les mêmes résultats à chaque exécution.

**Points d'honnêteté à assumer dans le rapport :**

- Pas de saisonnalité en finance journalière : SARIMA sera **testé puis écarté** avec justification (STL, ACF aux lags 5 et 21). C'est un résultat, pas un échec.
- Les prix sont proches d'une marche aléatoire : la baseline naïve (ŷₜ₊ₕ = yₜ) sera difficile à battre. Le dire est valorisé (critère « honnêteté scientifique »).
- La cointégration n'est pas garantie. Si Johansen la rejette, on le rapporte et on reste sur un VAR en différences.

**Alternative si tu préfères l'Option B** : consommation électrique journalière France (RTE éCO2mix) + température moyenne (Copernicus/NOAA), 2019–2025. Avantage : vraie saisonnalité (SARIMA pertinent, s = 7). Inconvénient : GARCH moins naturel et données plus longues à assembler. Le reste du plan s'applique en remplaçant rendements par écarts à la tendance.

Phrase de justification pour l'introduction (exigée par la section 1) : « Nous retenons le couple XOM/XLE car une action et son indice sectoriel partagent un facteur commun, ce qui permet d'étudier cointégration et volatilité conditionnelle sur des épisodes de crise identifiables. »

## 3. Table de traçabilité des exigences

Chaque exigence du cahier des charges a une implémentation et une preuve vérifiable. Mets le statut à jour au fil de l'avancement ; avant l'envoi, toutes les lignes doivent être « Fait ».

| § | Exigence | Implémentation prévue | Preuve / livrable | Statut |
| --- | --- | --- | --- | --- |
| 1 | Thématique justifiée en une phrase | Finance XOM/XLE | Intro du rapport | À faire |
| 1.1 | ≥ 5 ans journaliers, ≥ 1 indicateur technique | 2016–2025 ; log-rendement, volatilité réalisée 21 j, MM 50 j | `01_data`, tableau des variables | À faire |
| 1.3 | Objet série temporelle natif, fréquence déclarée | `DatetimeIndex` jours ouvrés (Python), `xts` (R) | Code + `df.info()` | À faire |
| 1.3 | Split chronologique 90/10 | Coupure à la date du 90e centile | Graphique train/test | À faire |
| 1.3 | Source, période, ajustements documentés | Note sur Adjusted Close (dividendes, splits) | Section Données | À faire |
| 2 | Visualisation, ACF/PACF brute et différenciée interprétées | Graphes + texte d'interprétation | Figures EDA | À faire |
| 2 | Décomposition commentée | STL sur log-prix | Figure STL + commentaire | À faire |
| 2 | Valeurs aberrantes détectées et traitées | IQR glissant sur rendements, indicatrice | Tableau des outliers | À faire |
| 2 | ADF + KPSS, ordre d conclu | Sur niveaux et différences | Tableau des tests | À faire |
| 3.1 | Ordres par ACF/PACF vs auto.arima/pmdarima | Deux approches comparées | Tableau AIC/BIC | À faire |
| 3.1 | Ljung-Box, normalité, ARCH-LM sur résidus | Pour chaque modèle | Tableau diagnostics | À faire |
| 3.2 | VAR (ordre par AIC/BIC) + Granger | VAR sur rendements XOM/XLE | Sorties + interprétation | À faire |
| 3.2 | Johansen / Engle-Granger, VECM si cointégration | Sur log-prix | Terme α interprété | À faire |
| 3.3 | GARCH(1,1) + ordres supérieurs, résidus standardisés | `arch` / `rugarch`, loi t de Student | Graphe volatilité + événements | À faire |
| 4.1 | LSTM + GRU, hyperparamètres justifiés, walk-forward | Keras, fenêtres glissantes | Courbes de perte, scores par fold | À faire |
| 5 | 4 tâches LLM documentées, erreurs du LLM signalées | Prompts + réponses intégrales | Annexe LLM | À faire |
| 6 | h = 5–10, IC, tableau unique MSE/RMSE/MAE/MAPE, Diebold-Mariano | Prévision multi-origines sur le test | Tableau récapitulatif + matrice DM | À faire |
| 8.1 | Socle classique en R ET Python, code commenté « pourquoi » | `.Rmd` + `.ipynb` | Deux notebooks | À faire |
| 8.3 | Notebook reproductible de bout en bout | Seed, versions, pas de chemin local | Exécution sur env. vierge | À faire |
| 8.4 | Discussion critique (modèles + IA générative) | Section dédiée | Rapport | À faire |

## 4. Architecture du dépôt et environnement

Un dépôt unique, un notebook Python principal qui exécute tout, un RMarkdown pour le socle classique en R, et un module `src/` pour ne pas dupliquer le code entre notebooks.

```
ts-project/
├── CLAUDE.md                 # règles pour Claude Code (section 6)
├── README.md                 # installation + ordre d'exécution
├── requirements.txt          # versions Python figées
├── install_packages.R        # packages R + versions
├── config.yaml               # tickers, dates, split, horizon, seed
├── data/
│   ├── raw/                  # CSV téléchargés (cache, versionnés)
│   └── processed/            # séries préparées, train/test
├── src/
│   ├── data.py               # téléchargement, nettoyage, features
│   ├── eda.py                # graphes, tests ADF/KPSS, outliers
│   ├── classical.py          # ARIMA, VAR, VECM, GARCH + diagnostics
│   ├── deep.py               # LSTM, GRU, hybride, walk-forward
│   ├── evaluation.py         # métriques, Diebold-Mariano, tableau unique
│   └── utils.py              # seed, chemins, sauvegarde figures
├── notebooks/
│   ├── main_python.ipynb     # étude complète de bout en bout
│   └── classical_R.Rmd       # socle section 3 en R
├── llm/
│   ├── prompts/              # prompts exacts (.md)
│   └── responses/            # réponses intégrales + date + modèle
├── outputs/
│   ├── figures/              # PNG numérotés fig01_..., fig02_...
│   └── tables/               # CSV des tableaux du rapport
└── report/
    └── rapport.docx / .pdf
```

**Environnement Python (Python 3.11) :** pandas, numpy, matplotlib, seaborn, yfinance, statsmodels, pmdarima, arch, scipy, scikit-learn, tensorflow (ou pytorch), prophet, pyyaml, jupyter.

**Environnement R (R ≥ 4.3) :** quantmod, xts, forecast, tseries, urca, vars, rugarch, FinTS, lmtest, ggplot2, rmarkdown.

**Règles de reproductibilité :**

1. Une seule seed (42) fixée pour `random`, `numpy`, `tensorflow` (et `set.seed(42)` en R).
2. Les données téléchargées sont sauvegardées en CSV dans `data/raw/` : si Yahoo change ou bloque, le notebook relit le cache.
3. Chemins relatifs uniquement (`pathlib`, `here::here()`), aucun `C:\Users\...`.
4. Première cellule du notebook : versions des packages affichées (`pip freeze` filtré, `sessionInfo()`).
5. Test final : créer un environnement neuf, `pip install -r requirements.txt`, puis « Restart & Run All » sans erreur.

**Piège pmdarima :** il casse souvent avec numpy ≥ 2. Fige `numpy<2` ou remplace par `statsforecast.AutoARIMA` en le signalant dans le rapport.

## 5. Phases détaillées

Neuf phases dans l'ordre du rapport. Chaque phase se termine par une sortie vérifiable (figure, tableau, test) : ne passe pas à la suivante tant qu'elle n'existe pas.

### Phase 1 — Données et préparation (§1)

1. Télécharger XOM et XLE (et `BZ=F` si 3e variable) avec `yfinance` (`auto_adjust=False` pour garder `Adj Close` explicitement) et `quantmod::getSymbols` en R. Sauvegarder en CSV dans `data/raw/`.
2. Aligner les deux séries par jointure interne sur les dates de bourse ; compter et documenter les valeurs manquantes.
3. Construire les variables dérivées :
   - log-prix : lₜ = ln(Pₜ) ;
   - log-rendement en % : rₜ = 100 × ln(Pₜ / Pₜ₋₁) ;
   - volatilité réalisée 21 jours annualisée : σₜ = √252 × écart-type glissant de rₜ ;
   - moyenne mobile 50 jours sur le prix.
4. Index : dates de bourse (`DatetimeIndex`, `xts`). Le calendrier est irrégulier (week-ends, fériés) : ne pas remplir par ffill, cela créerait des rendements nuls artificiels qui biaisent GARCH. Les modèles reçoivent un index positionnel, les dates servent aux graphes. À écrire dans le rapport.
5. Split chronologique 90/10 sur les dates : environ 2 260 jours de train et 250 de test. Toute normalisation est ajustée sur le train uniquement.
6. Documenter : source Yahoo Finance, dates exactes, `Adj Close` ajusté des dividendes et splits.

**Sortie :** tableau des variables (nom, définition, unité), graphe prix + coupure train/test.

### Phase 2 — Analyse exploratoire (§2)

1. Graphes : prix des deux actifs (axes séparés ou base 100), rendements, volatilité réalisée. Repérer les ruptures (2020, 2022).
2. Statistiques descriptives des rendements : moyenne, variance, skewness, kurtosis, Jarque-Bera. Elles servent aussi au prompt LLM de la phase 5.
3. ACF/PACF sur le log-prix (décroissance lente = non stationnarité), puis sur les rendements (quasi bruit blanc), puis sur rₜ² (autocorrélation forte = effets ARCH). **Écrire l'interprétation de chaque graphe.**
4. Décomposition STL sur le log-prix (période testée 5 et 252) : commenter tendance, saisonnalité (attendue négligeable) et résidu.
5. Outliers : IQR sur fenêtre glissante de 63 jours appliqué aux rendements. Traitement recommandé : **conservation** (les chocs sont réels et c'est ce que GARCH modélise) + variable indicatrice pour les jours extrêmes. Justifier.
6. Stationnarité : ADF et KPSS sur log-prix puis sur rendements, en précisant la spécification (constante, tendance) et le nombre de retards.

| ADF (H₀ : racine unitaire) | KPSS (H₀ : stationnaire) | Conclusion |
| --- | --- | --- |
| Rejetée | Non rejetée | Stationnaire |
| Non rejetée | Rejetée | Non stationnaire : différencier |
| Rejetée | Rejetée | Contradictoire : stationnaire en différence ou rupture, discuter |
| Non rejetée | Non rejetée | Données peu informatives, discuter |

Résultat attendu : log-prix I(1), rendements I(0), donc d = 1. À confirmer par tes propres sorties.

**En Derja :** ADF w KPSS 3aksin ba3dhhom : ADF yebda yfaredh elli el série mouch stationnaire, KPSS yfaredh elli hiya stationnaire. Ki ettnin ytaf9ou, conclusion mte3ek sa7i7a.

### Phase 3 — Modélisation classique (§3), en Python ET en R

**3.1 ARIMA / SARIMA sur le log-prix XOM (train)**

1. Identification manuelle (Box-Jenkins) : ACF/PACF des différences, proposer 2–3 candidats (ex. ARIMA(0,1,0), (1,1,0), (0,1,1), (1,1,1)).
2. Recherche automatique : `pmdarima.auto_arima` (Python) et `forecast::auto.arima` (R), `stepwise=False` si le temps le permet.
3. Tableau comparatif : ordre, AIC, BIC, significativité des coefficients. Comparer les choix manuel vs automatique et expliquer l'écart.
4. SARIMA : tester une saisonnalité s = 5 et conclure qu'elle n'apporte rien (AIC, coefficients non significatifs). Rapporter ce résultat.
5. Diagnostics de résidus pour chaque modèle retenu :
   - Ljung-Box aux lags 10 et 20, degrés de liberté corrigés de p + q ;
   - Jarque-Bera, adapté aux grands échantillons (Shapiro-Wilk rejette presque toujours sur \~2 000 points) ;
   - ARCH-LM (lags 5 et 10) : un rejet est attendu et motive la phase 3.3.
6. En R : `checkresiduals`, `Box.test(fitdf=)`, `tseries::jarque.bera.test`, `FinTS::ArchTest`.

**3.2 VAR et cointégration**

1. VAR sur les **rendements** XOM et XLE (stationnaires). Ordre par `select_order` / `VARselect` (AIC vs BIC, max 10). Commenter si les deux critères divergent.
2. Diagnostics VAR : stabilité (racines dans le cercle unité), Portmanteau multivarié, normalité.
3. Granger dans les deux sens. Interprétation prudente : « X aide à prévoir Y », pas « X cause Y ». Une faible prédictibilité croisée est cohérente avec l'efficience des marchés.
4. Cointégration sur les **log-prix** : Engle-Granger (`coint`) puis Johansen (`coint_johansen` / `urca::ca.jo`), statistiques trace et valeur propre maximale.
5. Si r = 1 : VECM (`statsmodels VECM` / `cajorls`). Interpréter β (relation de long terme) et α (vitesse d'ajustement). Demi-vie = ln(0,5) / ln(1 + α).
6. Si pas de cointégration : le rapporter, garder le VAR en différences, et noter que XOM pèse lourd dans XLE, ce qui rend le lien en partie mécanique.

**En Derja :** la cointégration ya3ni zouz séries kol wa7da tetmacha random, ama el far9 binethom yo93ed stable. Ki yetba3dou, α yhezzhom yarj3ou, w 9addech bel fissa yarj3ou heka el vitesse de correction.

**3.3 GARCH sur les rendements XOM**

1. ARCH-LM sur les résidus du meilleur ARIMA (ou directement sur rₜ centrés).
2. GARCH(1,1) avec loi normale puis loi de Student (`arch_model(dist='t')`, `rugarch` avec `std`). Comparer à GARCH(1,2), (2,1) et, en bonus, GJR-GARCH pour l'effet de levier.
3. Vérifier ω > 0, α, β ≥ 0, persistance α + β < 1 ; demi-vie d'un choc = ln(0,5) / ln(α + β).
4. Résidus standardisés zₜ : Ljung-Box sur zₜ et zₜ², ARCH-LM. Ils doivent être homoscédastiques.
5. Graphe de la volatilité conditionnelle annoté : 2016, mars–avril 2020, février–mars 2022.

**Piège à retenir :** GARCH ne prévoit pas le sens du prix, seulement l'amplitude des variations.

## 6. Travailler avec Claude Code

Donne à Claude Code le cahier des charges, ce plan et un `CLAUDE.md` à la racine du dépôt, puis avance **une phase par session**, en vérifiant les sorties avant de passer à la suivante.

**Mise en place :**

1. Crée le dossier `ts-project/`, copie `Mini_Projet_Series_Temporelles 2026.md` dans `docs/` et exporte ce plan en Markdown dans `docs/PLAN.md`.
2. Crée `CLAUDE.md` avec le contenu ci-dessous.
3. Lance Claude Code dans le dossier et commence par le prompt de la phase 0.

**Contenu de `CLAUDE.md` :**

```markdown
# Projet : Mini-projet Séries Temporelles TEK-UP 2026

Références : docs/Mini_Projet_Series_Temporelles 2026.md (cahier des charges)
et docs/PLAN.md (plan validé). Le cahier des charges fait foi.

## Données
- XOM + XLE (Adj Close), Yahoo Finance, 2016-01-01 → 2025-12-31, journalier.
- Paramètres centralisés dans config.yaml (tickers, dates, split 0.9, horizon 10, seed 42).
- Cache CSV dans data/raw/ ; relire le cache si le téléchargement échoue.

## Règles méthodologiques (non négociables)
- Split chronologique 90/10, jamais de shuffle, jamais de k-fold classique.
- Scalers et transformations ajustés sur le train uniquement (pas de fuite).
- Chaque modèle : diagnostic de résidus complet (Ljung-Box, Jarque-Bera, ARCH-LM).
- Baseline marche aléatoire systématique.
- Métriques sur le prix en dollars ; jamais de MAPE sur les rendements.
- Ne jamais inventer un résultat : toute valeur citée vient d'une exécution réelle.

## Code
- Python 3.11, versions figées dans requirements.txt ; R dans install_packages.R.
- Logique dans src/*.py, notebooks = appels + interprétations.
- Commentaires en français : une ligne par bloc qui explique POURQUOI (pas ce que fait le code).
- Figures dans outputs/figures/figNN_nom.png, tableaux dans outputs/tables/*.csv.
- Seed 42 partout. Chemins relatifs uniquement.
- Socle classique (ARIMA, VAR, VECM, GARCH) aussi en R dans notebooks/classical_R.Rmd.

## Manière de travailler
- Une phase à la fois ; exécuter le code et montrer les sorties réelles.
- À la fin de chaque phase : résumer résultats, décisions et justifications
  dans docs/journal.md (sert ensuite à rédiger le rapport).
- Signaler tout résultat inattendu au lieu de le contourner.
```

**Prompts par phase** (à copier dans Claude Code, un par session) :

| Phase | Prompt |
| --- | --- |
| 0 — Setup | « Lis CLAUDE.md, docs/PLAN.md et le cahier des charges. Crée l'arborescence, config.yaml, requirements.txt, install\_packages.R, src/utils.py (seed, chemins) et un README. Vérifie que l'installation fonctionne. » |
| 1 — Données | « Implémente la phase 1 du plan dans src/data.py et la première partie de main\_python.ipynb. Montre l'aperçu des données, les manquants, le tableau des variables et le graphe train/test. » |
| 2 — EDA | « Implémente la phase 2. Pour chaque graphe ACF/PACF, STL et test ADF/KPSS, ajoute une cellule Markdown d'interprétation basée sur les valeurs obtenues. Conclus sur d. » |
| 3a — ARIMA | « Implémente 3.1 : candidats manuels vs auto\_arima, tableau AIC/BIC, test SARIMA s=5, diagnostics complets. Explique chaque décision. » |
| 3b — VAR/VECM | « Implémente 3.2 : VAR sur rendements, Granger, Engle-Granger et Johansen sur log-prix, VECM si cointégration avec demi-vie. » |
| 3c — GARCH | « Implémente 3.3 : ARCH-LM, GARCH(1,1) normal vs Student, ordres supérieurs, résidus standardisés, graphe de volatilité annoté. » |
| 3d — R | « Reproduis les phases 1 à 3 dans notebooks/classical\_R.Rmd avec quantmod, forecast, vars, urca, rugarch. Compare les résultats R et Python et explique les écarts. » |
| 4 — Deep | « Implémente la phase 4 dans src/deep.py : LSTM et GRU, walk-forward 5 folds, grille réduite, 3 seeds, courbes de perte. Puis l'hybride ARIMA + LSTM. » |
| 6 — Évaluation | « Implémente la phase 6 dans src/evaluation.py : rolling origin h=1..10, baseline, tableau unique, Diebold-Mariano avec correction HLN, évaluation de la variance GARCH. » |
| 7 — Extensions | « Ajoute la corrélation glissante 60 j annotée et un VARX avec le Brent. » |
| 9 — Contrôle | « Crée un environnement neuf, réinstalle tout et exécute les deux notebooks de bout en bout. Liste toute erreur ou dépendance manquante. » |

La phase 5 (LLM) se fait **hors Claude Code**, dans une conversation séparée, avec tes vrais résultats : c'est ta comparaison critique qui est notée.

**Après chaque phase, demande-lui :** « Explique-moi ce code comme si j'étais en soutenance : pourquoi ce choix, quelle alternative, quel risque. » Tu dois pouvoir défendre tout le code.

## 7. Planning, checklist et soutenance

Compte environ trois semaines à temps partiel, en sécurisant d'abord le bloc A (10 points) avant les bonus. À recaler sur la date confirmée par l'enseignant.

| Semaine | Phases | Objectif de fin de semaine |
| --- | --- | --- |
| S1 | 0, 1, 2, 3.1 | Données propres, EDA interprétée, ARIMA diagnostiqué en Python |
| S2 | 3.2, 3.3, 3d (R), 4 | VAR/VECM, GARCH, version R, LSTM/GRU validés |
| S3 | 6, 5, 7, 8, 9 | Tableau unique + DM, annexe LLM, rapport, archive envoyée |

**Checklist avant envoi :**

- [ ] Chaque modèle a son diagnostic de résidus interprété
- [ ] ADF et KPSS rapportés avec H₀, statistique, p-value, décision
- [ ] Un seul tableau de métriques avec la baseline et tous les modèles
- [ ] Diebold-Mariano calculé sur les erreurs multi-origines
- [ ] Socle classique présent en R et en Python
- [ ] Partie avancée identifiée comme « Python uniquement »
- [ ] Prompts et réponses LLM intégrales en annexe, erreurs du LLM signalées
- [ ] Interprétation personnelle datée, rédigée avant le LLM
- [ ] Limites et échecs rapportés (SARIMA écarté, baseline difficile à battre, cointégration)
- [ ] Notebooks exécutés de bout en bout sur un environnement neuf
- [ ] Rapport entre 15 et 25 pages hors annexes
- [ ] Date limite confirmée avec M. Dhouibi

**Questions probables en soutenance :**

1. Pourquoi ADF **et** KPSS ? Parce que leurs H₀ sont opposées : la conclusion est solide quand les deux concordent.
2. Pourquoi le VAR sur les rendements et la cointégration sur les log-prix ? Le VAR exige la stationnarité ; la cointégration n'a de sens qu'entre séries I(1).
3. Que signifie α dans le VECM ? La fraction de l'écart à l'équilibre corrigée à chaque période ; on en déduit la demi-vie.
4. Que signifie α + β proche de 1 dans un GARCH ? Une volatilité très persistante : un choc met longtemps à se dissiper.
5. Pourquoi pas de k-fold ? Il mélange futur et passé, ce qui crée une fuite d'information.
6. Pourquoi votre LSTM ne bat-il pas la marche aléatoire ? Les prix boursiers sont proches d'une marche aléatoire (efficience) ; c'est un résultat attendu et honnête.
7. Que teste Diebold-Mariano ? H₀ : deux modèles ont la même précision attendue ; il évite de conclure sur un écart de RMSE dû au hasard.
8. Granger = causalité ? Non : c'est une prédictibilité incrémentale, sans mécanisme causal.
9. Où le LLM s'est-il trompé ? Avoir 2–3 exemples précis tirés de ton annexe.
10. Explique cette ligne de code. Le jury peut pointer n'importe quel bloc : relis tout le code produit par Claude Code avant l'envoi.

**En Derja :** el soutenance mouch 3la el résultats, 3la ennek tfahem chnowa 3malt w 3lech. Ken Claude Code ktebelek ligne ma fhemtech'ha, ma tab3athch el projet 9bal ma tfahemha.

### Phase 4 — Modélisation avancée (§4), en Python uniquement

1. **Cible :** prévoir les log-rendements XOM sur h = 10 jours (sortie directe à 10 valeurs), puis reconstruire le prix. Un LSTM entraîné sur des prix extrapole mal hors de la plage vue au train.
2. **Features :** rendements XOM et XLE, volatilité 21 j, éventuellement rendement du Brent. `StandardScaler` ajusté sur le train seulement.
3. **Fenêtres glissantes :** taille 20 (un mois de bourse) puis 60 testée ; tenseurs de forme (échantillons, fenêtre, features).
4. **Architectures :** LSTM et GRU, 1 à 2 couches de 32–64 unités, dropout 0,2, Adam (lr = 1e-3), perte MSE, early stopping (patience 10) sur une validation formée des derniers 10 % du train, **dans l'ordre chronologique**.
5. **Walk-forward :** `TimeSeriesSplit(n_splits=5)` en fenêtre croissante sur le train. Rapporter RMSE moyen ± écart-type par fold. Petite grille (fenêtre × unités × dropout) choisie sur ces folds, jamais sur le test.
6. **Robustesse :** répéter l'entraînement final avec 3 seeds et rapporter la dispersion.
7. **Sorties :** courbes de perte train/val, tableau des hyperparamètres avec leur justification, scores par fold.
8. **Hybride (bonus, bloc D) :** ARIMA pour la partie linéaire, puis LSTM sur les résidus ARIMA ; prévision = ARIMA + LSTM(résidus).
9. **Prophet (bonus, bloc D) :** facile à ajouter comme modèle de comparaison. Attendre des résultats médiocres sur un prix boursier et l'expliquer.

**En Derja :** jamais k-fold 3adi 3la série temporelle. El walk-forward ya3ni dima tetrainé 3la el madhi w tetesti 3la elli ba3dou, kif fi el 7a9i9a.

### Phase 5 — IA générative et LLM (§5, 4 points)

1. **Avant tout prompt**, rédige ta propre interprétation experte des résultats (une page, datée). C'est la référence de la comparaison humain/LLM.
2. **Prompt 1 — hypothèses :** donner moyenne, variance, skewness, kurtosis, résultats ADF/KPSS et ARCH-LM ; demander quels modèles tester et pourquoi.
3. **Prompt 2 — vulgarisation :** donner les résultats réels des modèles ; demander une explication pour un décideur non statisticien (annexe).
4. **Prompt 3 — recommandations simulées :** donner les prévisions et intervalles ; exiger que le LLM formule lui-même les limites et risques ; compléter ensuite de façon critique.
5. **Comparaison :** tableau convergences / divergences / erreurs du LLM.
6. **Grille de détection d'hallucinations :**
   - p-values ou statistiques citées qui ne figurent pas dans tes sorties ;
   - Granger présenté comme une causalité réelle ;
   - GARCH présenté comme prédisant la direction du prix ;
   - confiance excessive, oubli des coûts de transaction et du risque de modèle ;
   - lien causal inventé entre un événement et la série.
7. Archiver chaque prompt et chaque réponse intégrale dans `llm/` avec le nom du modèle et la date.

**Transparence :** indique aussi dans le rapport que le code a été développé avec l'aide de Claude Code. En soutenance, tu dois pouvoir expliquer chaque ligne.

### Phase 6 — Prévision et évaluation (§6)

1. **Prévision illustrative :** depuis la fin du train, prévision h = 10 pour chaque modèle, avec intervalles à 95 % (ARIMA, VAR, VECM, ARIMA-GARCH). Un graphe par modèle ou un graphe superposé.
2. **Prévision multi-origines (rolling origin) sur tout le test :** à chaque date du test, prévoir h = 1 à 10 en n'utilisant que le passé ; ré-estimer les modèles classiques tous les 20 jours pour limiter le temps de calcul. On obtient \~240 erreurs par horizon, indispensables au test de Diebold-Mariano (10 erreurs seules ne suffisent pas).
3. **Baseline obligatoire :** marche aléatoire (ŷ = dernier prix observé). Tout modèle est jugé par rapport à elle.
4. **Tableau unique :** MSE, RMSE, MAE, MAPE calculées sur le **prix en dollars** pour h = 1, 5 et 10. Jamais de MAPE sur les rendements (division par des valeurs proches de zéro).
5. **GARCH dans le tableau :** ligne ARIMA-GARCH (même moyenne que l'ARIMA, intervalles différents) + évaluation séparée de la variance prévue face à r²ₜ₊₁ (perte QLIKE ou MSE).
6. **Diebold-Mariano :** à implémenter soi-même (absent de statsmodels), perte quadratique, variance HAC avec h − 1 retards, correction de Harvey-Leybourne-Newbold ; en R, `forecast::dm.test`. Matrice des p-values contre la baseline.
7. **Choix final :** tableau performance × interprétabilité × coût de calcul, puis conclusion explicite.

### Phase 7 — Extensions (§7, bloc D)

Par ordre de rentabilité :

1. Corrélation glissante sur 60 jours entre rendements XOM et XLE, annotée avec les crises (facile, très visuel).
2. Brent comme variable exogène : VARX ou ARIMAX.
3. DCC-GARCH (`rmgarch` en R) pour une corrélation dynamique modélisée.
4. FinBERT sur un corpus d'actualités : coûteux, à garder pour la fin s'il reste du temps.

### Phase 8 — Rapport (§8.2, 15–25 pages)

| Partie | Pages |
| --- | --- |
| Introduction, thématique, question de modélisation | 1–2 |
| Données et préparation | 2 |
| Analyse exploratoire | 3–4 |
| ARIMA/SARIMA, VAR, cointégration, GARCH | 5–6 |
| LSTM/GRU, hybride | 3 |
| Prévision et évaluation (tableau unique + DM) | 2–3 |
| Apport des LLM | 2 |
| Discussion critique et conclusion | 2 |
| Annexes : prompts, réponses LLM, tableaux détaillés | hors quota |

Chaque figure est numérotée, citée dans le texte et suivie d'une interprétation. Chaque test donne H₀, statistique, p-value et décision.

### Phase 9 — Vérification et envoi (§8.3, §10)

1. Environnement neuf, installation, « Restart & Run All » sur les deux notebooks sans erreur.
2. Relecture de la table de traçabilité : toutes les lignes en « Fait ».
3. Archive `NomPrenom_TS_2026.zip` : code, notebooks, rapport, `requirements.txt`, `README.md`, données en cache.
4. Envoi à ahmed.dhouibi@tek-up.de avant la date confirmée.
