## TEK-UP

Cours Séries Temporelles pour Data Science & IA

## MINI-PROJET

## Modélisation, prévision et diagnostic de séries temporelles multidimensionnelles

De l'ARIMA classique aux réseaux de neurones, en passant par la cointégration, la volatilité conditionnelle et

l'IA générative

## Deux thématiques au choix — Finance ou Environnement

Ce projet peut être réalisé indifféremment sur des données financières (actions, indices, devises, cryptomonnaies) ou sur des données environnementales et énergétiques (température, CO₂, électricité, qualité de l'air). Les deux thématiques mobilisent exactement les mêmes outils méthodologiques , seul le terrain d'application change. Le barème et les attentes sont strictement identiques pour les deux choix.

| Barème total | Date de remise | Modalité |
| --- | --- | --- |
| 20 points | 12 Octobre 2026, 23h55 | Envoi par mail à ahmed.dhouibi@tek-up.de |

Chaque étudiant doit donc être en mesure d'expliquer et de défendre l'intégralité de son propre travail, y compris le code.


## 0. Introduction et objectifs pédagogiques

Ce mini-projet vous met en situation de data scientist face à un problème réel et non trivial : choisir, ajuster, diagnostiquer et comparer plusieurs familles de modèles de séries temporelles sur des données que vous aurez vous-même collectées et préparées. Il ne s'agit pas d'appliquer une recette unique, mais de construire une démarche de modélisation argumentée, où chaque choix (transformation, ordre de modèle, architecture de réseau) est justifié par un diagnostic statistique ou une observation empirique.

Le projet couvre volontairement un spectre large des modèles économétriques classiques (ARIMA, SARIMA, VAR, cointégration, GARCH) jusqu'aux réseaux de neurones récurrents et à l'usage réflexif de l'intelligence artificielle générative. Cette diversité n'est pas là pour vous noyer : le barème valorise la profondeur et la rigueur du diagnostic bien plus que le nombre de modèles empilés. Un SARIMA bien diagnostiqué et honnêtement comparé à sa baseline vaut mieux qu'un LSTM mal validé.

## Compétences visées

- Construire un pipeline complet de traitement de série temporelle, de la donnée brute à la prévision évaluée.

- Maîtriser les diagnostics statistiques qui justifient le choix d'un modèle plutôt qu'un autre (stationnarité, autocorrélation, cointégration, hétéroscédasticité conditionnelle).

- Comparer rigoureusement modèles économétriques et modèles d'apprentissage profond sur un même jeu de données, avec les mêmes métriques.

- Utiliser un LLM comme outil d'assistance à l'analyse, en gardant un regard critique sur ses productions.

- Rédiger un rapport scientifique qui articule clairement méthode, résultats et limites.

## 1. Choix de la thématique et importation des données

Vous choisissez librement l'une des deux thématiques suivantes. Ce choix est définitif et doit être justifié en une phrase dans l'introduction du rapport (pourquoi cette série, pourquoi cette thématique).

## 1.1 Option A — Données financières (Yahoo Finance)

Le site Yahoo Finance (finance.yahoo.com) donne accès à de nombreuses séries temporelles multidimensionnelles : actions, indices boursiers, devises, cryptomonnaies. Chaque actif fournit au minimum un vecteur multidimensionnel (Open, High, Low, Close, Adjusted Close, Volume).

- Choisir un actif ou un panier de 2 à 3 actifs corrélés (ex. une action et son indice sectoriel, ou deux cryptomonnaies), sur une fréquence journalière et une profondeur d'au moins 5 ans.

- Récupération possible via le package R quantmod ou tidyquant, ou en Python via yfinance.

- Construire au moins un indicateur technique dérivé (moyenne mobile, volatilité réalisée, rendement logarithmique) en plus des variables brutes.

## 1.2 Option B — Données environnementales et énergétiques

Alternative pédagogiquement équivalente à la finance, mais souvent plus intuitive à interpréter et porteuse d'enjeux différents (saisonnalité très marquée, tendances de long terme, ruptures liées à des politiques publiques). Sources publiques recommandées :


| Type de donnée | Source recommandée | Fréquence typique |
| --- | --- | --- |
| Température, précipitations | NOAA (ncdc.noaa.gov), ECMWF/Copernicus (Climate Data Store) | Journalière à mensuelle |
| CO₂ atmosphérique | NOAA Global Monitoring Lab (Mauna Loa), Our World in Data | Mensuelle |
| Consommation et production électrique | RTE éCO2mix (France), ENTSO-E Transparency Platform (Europe) | Horaire à journalière |
| Qualité de l'air (PM2.5, NO₂, ozone) | European Environment Agency (EEA), OpenAQ | Horaire à journalière |
| Indicateurs climatiques et énergétiques agrégés | Our World in Data (ourworldindata.org), Kaggle (jeux de données climat) | Variable |

- Choisir une série multidimensionnelle : par exemple, consommation électrique horaire accompagnée de la température et du jour de la semaine, ou concentration de CO₂ accompagnée d'un indicateur d'activité industrielle.

- Profondeur recommandée : au moins 3 ans de données pour capturer plusieurs cycles saisonniers complets.

## 1.3 Préparation commune aux deux options

- Transformer les données en objet série temporelle natif (ts, xts ou tsibble sous R ; DatetimeIndex sous Python avec pandas), avec un vecteur temps explicite et une fréquence correctement déclarée.

- Diviser l'échantillon de façon chronologique (jamais aléatoire) : 90 % pour l'apprentissage, 10 % pour le test.

- Documenter précisément la source, la période et toute transformation déjà appliquée par le fournisseur de données (ex. ajustements de dividendes pour la finance, corrections d'homogénéisation pour le climat).

## 2. Analyse exploratoire

- Visualiser la ou les séries : tendance, saisonnalité, ruptures visibles, comparaison des échelles si plusieurs variables.

- Produire et interpréter ACF et PACF sur la série brute puis sur la série différenciée — l'interprétation doit être écrite, pas seulement le graphique affiché.

- Réaliser une décomposition (classique additive/multiplicative, ou STL) et commenter chaque composante extraite.

- Détecter les valeurs aberrantes (boxplot glissant, IQR, ou test statistique dédié) et proposer un traitement justifié (conservation, correction, variable indicatrice).

- Tester formellement la stationnarité (ADF, KPSS — les deux, car ils ont des hypothèses nulles opposées et se complètent) et conclure explicitement sur l'ordre de différenciation nécessaire.


## 3. Modélisation classique

Cette section est le cœur économétrique du projet. Chaque modèle doit être accompagné de son diagnostic de résidus complet — un modèle sans diagnostic ne sera pas noté, quelle que soit la qualité apparente de ses prévisions.

## 3.1 ARIMA et SARIMA

- Identifier les ordres (p,d,q) et, si saisonnalité, (P,D,Q,s) à partir de l'ACF/PACF et confirmer par une recherche automatique (auto.arima en R, pmdarima en Python) — comparer les deux approches.

- Diagnostic de résidus complet : test de Ljung-Box (indépendance), test de normalité (Shapiro-Wilk ou Jarque-Bera), test ARCH (homoscédasticité conditionnelle — voir section 3.3).

## 3.2 Modèles multivariés : VAR et cointégration

Si votre série est multidimensionnelle (ce qui est attendu dans les deux options), vous devez impérativement dépasser l'analyse univariée pour modéliser les interactions entre variables.

- Estimer un modèle VAR (Vector AutoRegression) sur au moins deux variables corrélées de votre jeu de données, en sélectionnant l'ordre par critère d'information (AIC/BIC).

- Tester la causalité au sens de Granger entre les variables du VAR et interpréter le résultat.

- Tester la cointégration entre les séries non stationnaires (test de Johansen, ou test d'Engle-Granger pour deux séries) : deux séries individuellement non stationnaires peuvent partager une relation d'équilibre de long terme.

- Si cointégration détectée, estimer un modèle à correction d'erreur (VECM — Vector Error Correction Model) et interpréter le terme de correction d'erreur (vitesse de retour à l'équilibre).

## Exemple concret par thématique

Finance : une action et son indice sectoriel peuvent être cointégrés — leur écart de long terme est stable même si chaque série individuellement suit une marche aléatoire. Environnement : la consommation électrique et la température peuvent être cointégrées — leur relation

structurelle (effet chauffage/climatisation) persiste au-delà des fluctuations de court terme.

## 3.3 Modèles de volatilité conditionnelle : ARCH et GARCH

Pertinent dès que les résidus d'un modèle ARIMA/VAR échouent au test ARCH (variance non constante), ce qui est très fréquent sur les rendements financiers et pas rare sur des séries climatiques extrêmes.

- Vérifier la présence d'effets ARCH sur les résidus du meilleur modèle ARIMA/VAR obtenu précédemment (test ARCH-LM).

- Estimer un modèle GARCH(1,1) sur la série de rendements (finance) ou d'écarts à la tendance (environnement) et comparer à des ordres supérieurs si le diagnostic le justifie.

- Diagnostiquer les résidus standardisés du GARCH (les résidus doivent redevenir homoscédastiques une fois la volatilité correctement modélisée).

- Visualiser la volatilité conditionnelle estimée dans le temps et la mettre en relation avec des événements connus de votre série (crise financière, vague de chaleur, pic de consommation).

## 4. Modélisation avancée


## 4.1 Réseaux de neurones récurrents

- Implémenter et comparer au moins deux architectures : LSTM et GRU, avec une mise en forme des données adaptée (fenêtres glissantes, normalisation).

- Justifier les choix d'hyperparamètres (taille de fenêtre, nombre de couches, dropout) et documenter la procédure d'entraînement (courbes de perte train/validation).

- Évaluer la robustesse par validation croisée temporelle (time series cross-validation / walk-forward validation — jamais de k-fold classique sur une série temporelle).

## 4.2 Approches hybrides

Optionnel mais fortement valorisé : combiner un modèle économétrique et un modèle d'apprentissage profond, par exemple en modélisant la tendance/saisonnalité par ARIMA ou Prophet puis les résidus non linéaires restants par un LSTM.

## 4.3 Modèles additionnels au choix (approfondissement)

Pour les étudiants souhaitant explorer au-delà du socle obligatoire, les pistes suivantes sont valorisées comme approfondissement (voir barème) :

| Modèle | Intérêt pédagogique | Niveau de difficulté |
| --- | --- | --- |
| Prophet (Meta) | Décomposition automatique tendance/saisonnalité/jours fériés, robuste aux données manquantes | Facile à mettre en œuvre |
| N-BEATS | Architecture purement neuronale interprétable, sans ingénierie de features manuelle | Intermédiaire |
| Temporal Fusion Transformer (TFT) | Attention multi-horizon, gestion native de variables exogènes multiples | Avancé |
| Transformers pour séries temporelles (Informer, PatchTST) | État de l'art récent pour les séries longues | Avancé — à titre exploratoire |

## 5. IA générative et LLM (4 points)

Cette section évalue votre capacité à utiliser un LLM (ChatGPT, Claude, Gemini ou équivalent) comme outil d'assistance analytique, tout en gardant un regard critique — pas comme générateur automatique de rapport que vous copierez sans le comprendre.

- Générer, à partir des statistiques descriptives de votre série (moyenne, variance, skewness, kurtosis, résultats des tests de stationnarité), des hypothèses de modèles à tester par le LLM. Documenter le prompt utilisé et la réponse obtenue intégralement.

- Faire expliquer par le LLM les résultats de vos modèles de façon vulgarisée, comme si le rapport s'adressait à un décideur non-statisticien. Inclure cette explication en annexe.

- Générer des recommandations d'investissement simulées (option finance) ou des recommandations de politique/gestion (option environnement, ex. anticipation de pic de consommation) à partir de vos prévisions — en explicitant systématiquement les limites et risques de ces recommandations (le LLM doit être invité à les formuler lui-même, puis vous les complétez de façon critique).

- Comparer la cohérence entre votre propre interprétation experte (rédigée avant de solliciter le LLM) et l'explication générée par le LLM : où convergent-elles ? Où le LLM se trompe-t-il, simplifie-t-il à l'excès, ou invente-t-il une causalité non fondée ?


## Attention à l'hallucination statistique

Les LLM généralistes peuvent produire des affirmations statistiques qui semblent plausibles mais sont fausses (p- values inventées, causalités non vérifiées). Une partie de la note de cette section porte spécifiquement sur votre capacité à détecter et signaler ces erreurs dans les productions du LLM, pas seulement à les rapporter.

## 6. Prévision et évaluation

- Produire des prévisions à horizon h = 5 à 10 pas pour chaque modèle retenu, avec intervalles de confiance/prédiction quand le modèle le permet.

- Comparer aux observations réelles de l'échantillon test à l'aide des métriques MSE, RMSE, MAE et MAPE — présentées dans un tableau récapitulatif unique regroupant tous les modèles testés.

- Tester si les différences de performance entre modèles sont significatives (test de Diebold-Mariano) plutôt que de comparer seulement les valeurs brutes des métriques.

- Conclure explicitement sur le meilleur modèle selon votre cas d'usage, en tenant compte non seulement de la performance mais aussi de l'interprétabilité et du coût de calcul.

## 7. Extensions possibles (bonus)

Ces extensions ne sont pas obligatoires mais sont valorisées dans le barème (voir section Évaluation). Elles peuvent être adaptées à votre thématique :

- Introduire des variables exogènes externes à votre série principale : actualités économiques ou indices de sentiment textuel (finance), ou indicateurs météorologiques complémentaires et jours fériés (environnement).

- Appliquer une détection d'événements par embeddings de texte (modèles transformers de type BERT/FinBERT) sur un corpus d'actualités ou de rapports liés à votre série, et relier ces événements aux ruptures observées.

- Étudier la corrélation dynamique entre deux séries dans le temps (corrélation glissante, DCC-GARCH) plutôt qu'une corrélation statique unique — par exemple une action et son indice sectoriel, ou la température et la consommation électrique selon les saisons.

## 8. Livrables attendus

## 8.1 Codes complets

- Code en R ET en Python pour au moins le socle classique (section 3) — le socle avancé (section 4) et les extensions peuvent être implémentés dans un seul des deux langages, au choix, mais doivent alors être clairement identifiés comme tels.

- Code commenté : chaque bloc doit expliquer en une ligne ce qu'il fait et pourquoi ce choix a été fait à cette étape (pas une paraphrase du code, une justification).

## 8.2 Rapport détaillé (Word ou PDF)

- Introduction du problème : thématique choisie, série(s) retenue(s), question de modélisation posée.


- Étapes d'analyse, graphiques et diagnostics, présentés dans l'ordre logique du projet (sections 1 à 6).

- Tableau de comparaison détaillée des modèles (métriques, complexité, interprétabilité).

- Interprétation des résultats et apport spécifique des LLM (ce qu'ils ont permis de gagner en temps ou en clarté, ce qu'ils n'ont pas su faire).

- Longueur indicative : 15 à 25 pages hors annexes et code.

## 8.3 Notebook exécutable

RMarkdown (.Rmd) ou Jupyter (.ipynb), permettant de reproduire l'intégralité de l'étude de bout en bout sans intervention manuelle autre que l'exécution des cellules. Le notebook doit s'exécuter sans erreur sur une machine vierge disposant des packages listés en en-tête.

## 8.4 Discussion critique

- Limites des modèles utilisés (hypothèses violées, échantillon insuffisant, instabilité des estimations, etc.).

- Avantages et inconvénients de l'utilisation d'IA générative pour l'analyse de séries temporelles dans votre domaine d'application — au-delà de la comparaison ponctuelle demandée en section 5, une réflexion plus générale est attendue ici.

## 9. Barème détaillé (20 points)

Le barème est réparti en trois blocs. Le bloc "Approfondissement et extensions" récompense la profondeur méthodologique (cointégration, GARCH bien diagnostiqué, approches hybrides, extensions de la section 7) plutôt que la simple accumulation de modèles.

| Bloc | Contenu | Points |
| --- | --- | --- |
| A — Fondamentaux | Préparation des données, analyse exploratoire, ARIMA/SARIMA/VAR avec diagnostics complets, prévision et évaluation comparative (sections 1, 2, 3.1-3.2, 6) | 10 |
| B — Modélisation avancée | GARCH avec diagnostic, LSTM/GRU avec validation croisée temporelle, comparaison rigoureuse classique vs. avancé (sections 3.3, 4.1) | 4 |
| C — IA générative et LLM | Génération d'hypothèses, vulgarisation, recommandations avec limites explicites, comparaison humain/LLM (section 5) | 4 |
| D — Approfondissement et extensions | Cointégration/VECM, approches hybrides, modèles additionnels (Prophet, TFT...), extensions de la section 7 | 2 |

## 9.1 Critères transversaux de qualité (appliqués à tous les blocs)

| Critère | Ce qui est valorisé | Ce qui pénalise |
| --- | --- | --- |
| Rigueur du diagnostic | Tests statistiques correctement interprétés, hypothèses vérifiées avant application d'un modèle | Modèle appliqué sans vérification préalable, résultats de tests non interprétés |
| Reproductibilité | Notebook exécutable de bout en bout, seed fixée, versions de packages documentées | Code qui échoue à l'exécution, dépendance à des fichiers ou chemins locaux non documentés |


| Critère | Ce qui est valorisé | Ce qui pénalise |
| --- | --- | --- |
| Honnêteté scientifique | Limites et échecs de modèles rapportés explicitement, incertitude quantifiée | Résultats présentés comme définitifs sans discussion des limites |
| Esprit critique face au LLM | Erreurs et approximations du LLM identifiées et corrigées | Contenu généré par LLM recopié sans relecture critique |

## Rappel important

Un modèle sophistiqué mal diagnostiqué rapporte moins de points qu'un modèle simple parfaitement diagnostiqué et honnêtement interprété. La profondeur de la réflexion prime sur le nombre d'algorithmes utilisés.

## 10. Modalités pratiques

| Élément | Détail |
| --- | --- |
| Date limite de remise | 12 octobre 2026, 23h55 |
| Modalité d'envoi | Par mail à ahmed.dhouibi@tek-up.de (code + rapport + notebook, archive .zip recommandée) |
| Soutenance | Sélection aléatoire d'un sous-ensemble de projets pour soutenance orale ultérieure préparez-vous à défendre l'intégralité de votre propre travail |
| Travail en groupe (au max 5) | Selon les modalités communiquées en cours — à confirmer avec l'enseignant si non précisé |

## 11. Ressources indicatives

## Packages R

forecast, fpp3 / fable, tsibble, urca (cointégration), vars (VAR), rugarch / fGarch (GARCH), keras / torch (LSTM/GRU), prophet, quantmod / tidyquant (finance).

## Bibliothèques Python

statsmodels (ARIMA, VAR, VECM), arch (GARCH), pmdarima, tensorflow/keras ou pytorch (LSTM/GRU), prophet, yfinance (finance), pandas, scikit-learn (métriques, validation croisée).

## Données

Finance : finance.yahoo.com. Environnement : NOAA (ncdc.noaa.gov), Our World in Data (ourworldindata.org), RTE éCO2mix, ENTSO-E Transparency Platform, European Environment Agency, OpenAQ.

## Bon travail à toutes et à tous.
