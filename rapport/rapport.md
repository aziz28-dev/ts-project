---
lang: fr-FR
title-meta: "Modélisation, prévision et diagnostic d'une série temporelle financière multidimensionnelle"
author-meta: "Aziz Bellaaj, Mohamed Yassine Khiari"
---

::: {custom-style="Cover Logo"}
![](logo_tekup.png){width=6cm}
:::

::: {custom-style="Cover Text"}
Filière Data Science et Intelligence Artificielle

Module : Séries temporelles
:::

::: {custom-style="Cover Kind"}
Rapport de mini-projet
:::

::: {custom-style="Cover Title"}
Modélisation, prévision et diagnostic d'une série temporelle financière multidimensionnelle
:::

::: {custom-style="Cover Subtitle"}
Le cas d'ExxonMobil (XOM) et de l'ETF Energy Select Sector (XLE), 2016-2025
:::

::: {custom-style="Cover Names"}
Réalisé par\
Aziz Bellaaj\
Mohamed Yassine Khiari

Encadré par\
M. Ahmed Dhouibi
:::

::: {custom-style="Cover Year"}
Année universitaire 2026-2027
:::

```{=openxml}
<w:p><w:r><w:br w:type="page"/></w:r></w:p>
```

::: {custom-style="Front Heading"}
Résumé
:::

Ce travail étudie le cours journalier de l'action ExxonMobil (XOM) et de l'ETF sectoriel de l'énergie XLE entre 2016 et 2025, soit 2 514 séances de bourse issues de Yahoo Finance, le prix du Brent servant de variable externe. Il cherche à savoir si le prix de XOM peut être prévu à un horizon de 1 à 10 jours mieux que par une marche aléatoire, et, à défaut, si son risque peut l'être.

Les tests ADF et KPSS concordent pour conclure que les log-prix sont intégrés d'ordre 1. Les rendements se comportent comme un bruit blanc en moyenne mais présentent une forte hétéroscédasticité conditionnelle. Le critère BIC retient la marche aléatoire, ARIMA(0,1,0). Le VAR ne met en évidence aucune prédictibilité croisée robuste et la cointégration entre XOM et XLE n'est acceptée qu'au seuil de 10 % par le test de Johansen. Un modèle GJR-GARCH(1,1) à loi de Student capte l'effet de levier (γ = 0,042, p = 0,004). Les réseaux LSTM et GRU, validés par une procédure walk-forward, ne font pas mieux que la marche aléatoire.

Sur l'année de test (252 origines de prévision, ré-estimation tous les 20 jours), le test de Diebold-Mariano ne désigne aucun modèle significativement meilleur que la marche aléatoire, et les réseaux sont significativement moins précis à 10 jours. Le GJR-GARCH-t est en revanche le seul modèle dont les intervalles de prévision à 95 % ont une couverture correcte (94,8 %, contre environ 98 % pour les modèles à variance constante), avec des intervalles plus étroits de 16 %. Le modèle retenu est donc l'ARIMA(0,1,0) associé à un GJR-GARCH(1,1)-t. Les extensions établissent que la corrélation entre XOM et XLE est dynamique (DCC-GARCH) et que le Brent explique les rendements du jour même sans les prévoir. Un modèle de langage (ChatGPT) a enfin été utilisé et évalué de manière critique.

Le socle de modèles classiques est implémenté en Python et en R, avec une comparaison de 91 grandeurs ; les réseaux de neurones et les extensions sont implémentés en Python uniquement, à l'exception des vérifications en R signalées dans le texte.

*Mots-clés* : séries temporelles financières, marche aléatoire, ARIMA, VAR, cointégration, VECM, GJR-GARCH, DCC-GARCH, LSTM, GRU, test de Diebold-Mariano.

::: {custom-style="Front Heading"}
Abstract
:::

This study examines the daily prices of ExxonMobil (XOM) and of the energy sector ETF XLE from 2016 to 2025 (2,514 trading days from Yahoo Finance), with the Brent crude price as an external variable. It asks whether the XOM price can be forecast 1 to 10 days ahead more accurately than by a random walk and, failing that, whether its risk can be forecast.

ADF and KPSS tests agree that log-prices are integrated of order one. Returns are white noise in the mean but strongly conditionally heteroskedastic. The BIC selects the random walk, ARIMA(0,1,0); the VAR reveals no robust cross-predictability, and cointegration between XOM and XLE is accepted only at the 10 % level by the Johansen test. A GJR-GARCH(1,1) model with Student-t innovations captures the leverage effect (γ = 0.042, p = 0.004). LSTM and GRU networks, validated with a walk-forward scheme, do not outperform the random walk.

Over the test year (252 forecast origins, models re-estimated every 20 days), the Diebold-Mariano test finds no model significantly more accurate than the random walk, and the networks are significantly less accurate at the 10-day horizon. The GJR-GARCH-t, however, is the only model whose 95 % prediction intervals achieve correct coverage (94.8 %, against about 98 % for constant-variance models) while being 16 % narrower. The selected model is therefore ARIMA(0,1,0) with GJR-GARCH(1,1)-t errors. Extensions show that the XOM-XLE correlation is time-varying (DCC-GARCH) and that Brent explains same-day returns without forecasting them. A large language model (ChatGPT) was used and critically assessed.

*Keywords*: financial time series, random walk, ARIMA, VAR, cointegration, VECM, GJR-GARCH, DCC-GARCH, LSTM, GRU, Diebold-Mariano test.

```{=openxml}
<w:p><w:r><w:br w:type="page"/></w:r></w:p>
<w:sdt><w:sdtPr><w:docPartObj><w:docPartGallery w:val="Table of Contents"/><w:docPartUnique/></w:docPartObj></w:sdtPr><w:sdtContent><w:p><w:pPr><w:pStyle w:val="TOCHeading"/></w:pPr><w:r><w:t>Table des matières</w:t></w:r></w:p><w:p><w:r><w:fldChar w:fldCharType="begin" w:dirty="true"/></w:r><w:r><w:instrText xml:space="preserve"> TOC \o "1-2" \h \z \u </w:instrText></w:r><w:r><w:fldChar w:fldCharType="separate"/></w:r><w:r><w:t>Mettre à jour la table des matières (F9).</w:t></w:r><w:r><w:fldChar w:fldCharType="end"/></w:r></w:p></w:sdtContent></w:sdt>
<w:p><w:r><w:br w:type="page"/></w:r></w:p>
```

# 1. Introduction

## 1.1 Contexte et question de recherche

La prévision des cours boursiers occupe une place particulière en économétrie financière. Selon l'hypothèse d'efficience des marchés sous sa forme faible (Fama, 1970), les prix passés ne contiennent aucune information permettant de prévoir les rendements futurs, si bien que la marche aléatoire constitue une référence difficile à battre. Cette hypothèse ne s'applique pas à la variance : depuis les travaux d'Engle (1982) et de Bollerslev (1986), il est établi que la volatilité des rendements financiers est persistante et donc en partie prévisible.

Ce projet confronte ces deux résultats à une série concrète, en mobilisant l'ensemble des outils du cours, des modèles de Box et Jenkins (1976) aux réseaux de neurones récurrents (Hochreiter et Schmidhuber, 1997 ; Cho et al., 2014). Nous avons retenu l'option finance du cahier des charges. La série principale est le cours ajusté d'ExxonMobil (XOM), première capitalisation pétrolière américaine. Elle est étudiée conjointement avec l'ETF Energy Select Sector SPDR (XLE), dont XOM est le premier composant (environ un quart de l'ETF en 2026), et avec le contrat à terme sur le Brent (BZ=F) comme variable externe. Ce couple formé d'une action et de son secteur se prête à toute la chaîne de modélisation : deux séries intégrées pour l'étude de la cointégration, des rendements à effets ARCH pour le GARCH, un lien contemporain fort pour le VAR et pour l'étude de la corrélation dynamique.

La question de recherche est la suivante : un investisseur peut-il prévoir le prix de XOM à 1, 5 et 10 jours mieux qu'en supposant que le prix de demain sera celui d'aujourd'hui ? À défaut, peut-il prévoir l'amplitude des variations, c'est-à-dire le risque ?

## 1.2 Démarche et organisation du rapport

La démarche suit l'ordre du cahier des charges. La section 2 présente les données et leur préparation, la section 3 l'analyse exploratoire, la section 4 les modèles économétriques classiques et la section 5 les réseaux de neurones. La section 6 évalue tous les modèles hors échantillon selon un protocole commun. La section 7 présente deux extensions, la section 8 l'usage critique d'un modèle de langage, et la section 9 discute les limites du travail avant de conclure.

Le tableau 1 recense les livrables. Toutes les valeurs citées dans ce rapport proviennent d'une exécution réelle du code ; la graine aléatoire est fixée à 42 et les versions des bibliothèques sont figées.

| Livrable | Contenu |
| ------------------------ | ---------------------------------------- |
| notebooks/main_python.ipynb | Étude complète, exécutable de bout en bout sans intervention |
| notebooks/classical_R.Rmd et son rendu HTML | Socle classique en R, comparaison avec Python, vérification du test de Diebold-Mariano et du DCC |
| src/*.py | Code Python : données, analyse exploratoire, modèles classiques, réseaux, évaluation, extensions |
| llm/ | Interprétation personnelle, prompts et réponses intégrales du modèle de langage, comparaison |
| docs/journal.md, docs/sources.md | Résultats et décisions par étape ; sources des faits externes |

Table: Tableau 1. Livrables du projet.

# 2. Données et préparation

## 2.1 Source et variables

Les cours journaliers sont extraits de Yahoo Finance à l'aide de la bibliothèque *yfinance*, du 1^er^ janvier 2016 au 31 décembre 2025. Nous utilisons la colonne *Adj Close*, ajustée des dividendes et des divisions d'actions. L'écart avec le cours de clôture brut est important : au 4 janvier 2016, le cours de clôture de XOM vaut 77,46 $ et son cours ajusté 49,00 $. Sans cet ajustement, chaque détachement de dividende produirait une baisse fictive du prix.

Yahoo Finance recalcule le cours ajusté à chaque nouveau dividende. Afin de garantir la reproductibilité des résultats, les données téléchargées le 8 novembre 2026 ont été figées dans un fichier de cache versionné (data/raw/), relu en priorité par les codes Python et R. Le tableau 2 définit les variables dérivées.

| Variable | Définition | Usage |
| ---------------- | -------------------------------- | ------------------------ |
| Prix ajusté $P_t$ | Adj Close | Métriques d'évaluation, en dollars |
| Log-prix | $\ln P_t$ | Stationnarité, cointégration |
| Rendement $r_t$ | $100 \times \Delta \ln P_t$, en % | Variable modélisée (ARIMA, VAR, GARCH, réseaux) |
| Volatilité réalisée | Écart-type des rendements sur 21 jours, multiplié par $\sqrt{252}$ | Indicateur de risque, entrée des réseaux |
| Moyenne mobile | 50 jours | Indicateur technique, graphiques |

Table: Tableau 2. Variables utilisées.

Toutes les fenêtres glissantes ne portent que sur le passé, de sorte qu'aucune information de l'échantillon de test ne peut se diffuser vers l'échantillon d'apprentissage.

## 2.2 Valeurs manquantes et calendrier

XOM et XLE partagent exactement le même calendrier : 2 514 séances, sans valeur manquante ni doublon. Le Brent, coté sur un autre marché, manque deux jours du calendrier commun (10 octobre et 11 novembre 2016), et trois cotations hors calendrier ont été écartées.

Nous n'avons procédé à aucune imputation. Reporter la valeur de la veille créerait des rendements nuls fictifs qui biaiseraient à la baisse l'estimation de la variance conditionnelle. Les modèles reçoivent donc un index positionnel, c'est-à-dire la suite des séances, et les dates ne servent qu'aux représentations graphiques.

## 2.3 Découpage chronologique

L'échantillon est découpé chronologiquement, sans mélange des observations (tableau 3). Toute l'identification des modèles, qu'il s'agisse des tests, du choix des ordres ou des hyperparamètres, est réalisée sur l'échantillon d'apprentissage.

| Échantillon | Séances | Période |
| ---------------- | -------- | ------------------------ |
| Apprentissage (90 %) | 2 262 | du 4 janvier 2016 au 27 décembre 2024 |
| Test (10 %) | 252 | du 30 décembre 2024 au 31 décembre 2025 |

Table: Tableau 3. Découpage de l'échantillon.

![Figure 1. Prix ajustés de XOM et de XLE et séparation entre apprentissage et test (figure 1 du notebook).](../outputs/figures/fig01_prix_train_test.png){width=16cm}

Les deux prix évoluent de concert sur toute la période : effondrement de 2020, forte hausse en 2021 et 2022, puis plateau. La figure 1 montre aussi que la période de test est plus calme que la période d'apprentissage. La volatilité réalisée de XOM y atteint au plus 47,4 %, contre 108,9 % pendant l'apprentissage. Les métriques calculées sur le test reflètent ce régime, ce dont il faudra tenir compte dans la section 6.

# 3. Analyse exploratoire

L'ensemble de cette section porte sur l'échantillon d'apprentissage.

## 3.1 Statistiques descriptives

| Rendements (%) | Moyenne | Écart-type | Volatilité annualisée | Asymétrie | Excès de kurtosis | Jarque-Bera |
| ---------------- | ---------- | ----------- | ------------- | ----------- | ------------ | ------------------- |
| XOM | 0,032 | 1,78 | 28,3 % | −0,16 | 6,6 | 4 142 (p < 0,0001) |
| XLE | 0,031 | 1,92 | 30,5 % | −0,89 | 16,4 | 25 747 (p < 0,0001) |

Table: Tableau 4. Statistiques descriptives des rendements journaliers.

La moyenne des rendements n'est pas significativement différente de zéro. Pour XOM, le test de Student avec erreurs-types robustes de Newey et West (1987), calculées avec 7 retards, donne t = 0,86 et p = 0,39 : l'hypothèse d'une espérance nulle n'est pas rejetée, et le modèle de la moyenne peut se passer de constante.

La normalité est en revanche nettement rejetée par le test de Jarque et Bera (1980), en raison de queues épaisses (excès de kurtosis de 6,6 et 16,4) et d'une asymétrie négative. Ce constat justifie deux choix ultérieurs : l'emploi d'une loi de Student pour le GARCH, et le recours au test de Jarque-Bera plutôt qu'à celui de Shapiro-Wilk, qui rejette presque systématiquement la normalité sur un échantillon de 2 000 observations.

![Figure 2. Prix, rendements journaliers et volatilité réalisée sur 21 jours, 2016-2025 (figure 2 du notebook).](../outputs/figures/fig02_series_rendements_volatilite.png){width=16cm}

Les rendements oscillent autour de zéro, mais leur amplitude varie fortement dans le temps (figure 2). Des périodes calmes alternent avec des grappes de fortes variations, au début de 2016, en mars et avril 2020, en 2022 et en avril 2025. Ce regroupement des fortes variations est caractéristique de l'hétéroscédasticité conditionnelle que modélise le GARCH.

## 3.2 Autocorrélations

Le log-prix présente une autocorrélation d'ordre 1 de 0,998 et une décroissance très lente (les 40 premiers retards sont significatifs), avec un seul pic d'autocorrélation partielle au retard 1. C'est le profil typique d'une marche aléatoire. Les autocorrélations des rendements sont au contraire très faibles (au plus 0,064 en valeur absolue pour XOM), tandis que celles des rendements au carré sont significatives aux 40 retards, avec un maximum de 0,32.

![Figure 3. Fonctions d'autocorrélation et d'autocorrélation partielle des rendements de XOM (en haut) et de XLE (en bas) sur l'apprentissage (figure 4 du notebook ; rendements au carré : figure 5).](../outputs/figures/fig04_acf_pacf_rendements.png){width=15cm}

Le test de Ljung et Box (1978), dont l'hypothèse nulle est l'absence d'autocorrélation jusqu'au retard 10, précise ce diagnostic (tableau 5).

| Rendements de XOM | Q(10) et p-value | Décision |
| -------------------------------- | -------------------- | ---------------- |
| Bruts | 34,9 ; p = 0,0001 | H₀ rejetée |
| Standardisés par la volatilité des 21 jours précédents | p = 0,98 | H₀ non rejetée |
| Hors année 2020 | p = 0,44 | H₀ non rejetée |
| Au carré | 1 464 ; p < 0,0001 | H₀ rejetée |

Table: Tableau 5. Test de Ljung-Box sur les rendements de XOM.

Le rejet observé sur les rendements bruts disparaît dès que l'on neutralise la volatilité ou que l'on exclut l'année 2020. Il s'agit donc d'un artefact de l'hétéroscédasticité et non d'une véritable dynamique de la moyenne. Les rendements se comportent comme un bruit blanc en moyenne, alors que leur variance, mesurée par les rendements au carré, est fortement prévisible.

## 3.3 Saisonnalité et valeurs aberrantes

La décomposition STL (Cleveland et al., 1990) ne révèle aucune saisonnalité : la force saisonnière vaut 0,000 pour une période de 5 jours comme pour une période de 252 jours, et 0,032 pour une période de 21 jours. Le test de Kruskal et Wallis (1952) ne rejette pas l'égalité des distributions des rendements selon le jour de la semaine (p = 0,59).

Les valeurs aberrantes sont détectées par un critère interquartile glissant calculé sur les 63 séances précédentes (k = 3). On en dénombre 15 pour XOM et 18 pour XLE, dont 10 en 2020 pour chacune des deux séries. Elles ont été conservées : il s'agit de chocs réels, communs aux deux actifs, que le GARCH a précisément vocation à modéliser. Une variable indicatrice les signale. Cette détection est robuste, puisqu'un noyau de 11 jours est retrouvé pour XOM par au moins 12 des 16 réglages testés.

## 3.4 Stationnarité

Les tests de Dickey et Fuller augmenté (ADF ; Dickey et Fuller, 1979) et de Kwiatkowski, Phillips, Schmidt et Shin (KPSS ; 1992) reposent sur des hypothèses nulles opposées : la présence d'une racine unitaire pour le premier, la stationnarité pour le second. Une conclusion n'est retenue que lorsque les deux tests concordent. Les retards de l'ADF sont choisis par le critère AIC ; les valeurs critiques à 5 % sont −2,86 (avec constante) et −3,41 (avec constante et tendance) pour l'ADF, 0,463 et 0,146 pour le KPSS.

| Série | Spécification | ADF : statistique (retards), p | KPSS : statistique (retards), p | Conclusion |
| -------------- | -------------- | ------------------- | ------------------- | -------------- |
| Log-prix XOM | constante | −0,971 (18), p = 0,76 | 3,563 (29), p < 0,01 | non stationnaire |
| Log-prix XOM | constante et tendance | −1,600 (18), p = 0,79 | 1,397 (29), p < 0,01 | non stationnaire |
| Rendements XOM | constante | −10,557 (17), p < 0,001 | 0,144 (8), p > 0,10 | stationnaire |
| Log-prix XLE | constante | −1,503 (7), p = 0,53 | 3,586 (29), p < 0,01 | non stationnaire |
| Rendements XLE | constante | −16,064 (6), p < 0,001 | 0,084 (9), p > 0,10 | stationnaire |

Table: Tableau 6. Tests de stationnarité ADF et KPSS (échantillon d'apprentissage).

Une rupture structurelle peut conduire à tort à accepter une racine unitaire. Le test de Zivot et Andrews (1992), qui autorise une rupture de date inconnue, ne rejette pas non plus l'hypothèse de racine unitaire (p compris entre 0,18 et 0,48), les ruptures étant estimées en janvier 2020 et en décembre 2021.

Les log-prix sont donc intégrés d'ordre 1 et les rendements stationnaires, ce qui conduit à retenir d = 1 et D = 0. Les modèles portent sur les rendements et non sur les prix.

# 4. Modélisation classique

Les modèles de cette section sont estimés en Python et reproduits en R (section 4.4).

## 4.1 ARIMA et SARIMA

Un modèle ARIMA(p,1,q) du log-prix est estimé sous la forme d'un ARMA(p,q) des rendements :

$$\phi(L)\, r_t = c + \theta(L)\, \varepsilon_t,$$

où $L$ est l'opérateur retard, $\phi$ et $\theta$ des polynômes de degrés p et q, et la constante $c$ représente la dérive du prix. Cette convention garantit que tous les modèles portent sur les mêmes 2 261 observations, ce qui rend leurs critères d'information comparables. Les erreurs-types sont robustes, de type sandwich (quasi-maximum de vraisemblance), afin de tenir compte des effets ARCH qui rendraient les erreurs-types usuelles trop optimistes.

| Modèle | AIC | BIC | Coefficients (p-value robuste) |
| ------------------------ | ---------- | ---------- | --------------------------- |
| ARIMA(0,1,0) | 9 037,10 | 9 042,83 | aucun |
| ARIMA(1,1,0) | 9 037,84 | 9 049,29 | AR(1) = −0,024 (p = 0,49) |
| ARIMA(0,1,1) | 9 037,87 | 9 049,32 | MA(1) = −0,023 (p = 0,50) |
| ARIMA(0,1,0) avec dérive | 9 038,38 | 9 049,83 | dérive = 0,032 (p = 0,40) |
| ARIMA(3,1,2), recherche automatique (AIC) | 9 021,27 | 9 055,6 | racines AR et MA quasi identiques |

Table: Tableau 7. Modèles ARIMA candidats (échantillon d'apprentissage).

L'identification manuelle selon la méthode de Box et Jenkins ne fait apparaître aucun pic net dans les fonctions d'autocorrélation des rendements. Les candidats de petit ordre ont tous des coefficients non significatifs, et la marche aléatoire obtient à la fois le meilleur AIC et le meilleur BIC (tableau 7).

La recherche automatique exhaustive (*pmdarima*, p et q au plus égaux à 5) retient un ARIMA(3,1,2) selon l'AIC, avec un gain de 15,8 points, mais l'ARIMA(0,1,0) selon le BIC. L'ARIMA(3,1,2) présente plusieurs signes de surajustement. Ses racines autorégressives (module 1,047) et de moyenne mobile (module 1,075) se compensent presque, ses résidus standardisés restent autocorrélés (Ljung-Box, p = 0,013), et son gain d'AIC devient une perte de 9,2 points lorsque le modèle est estimé sur des rendements standardisés. En R, l'optimiseur converge en outre vers un autre maximum local de la vraisemblance (section 4.4).

Le modèle SARIMA de période 5 améliore l'AIC de 5,7 points et le test du rapport de vraisemblance lui est favorable (p = 0,006). Son coefficient saisonnier n'est cependant pas significatif avec des erreurs-types robustes (0,058, p = 0,12), le BIC est pratiquement inchangé (+0,05) et le gain disparaît lorsque l'on exclut 2020. Compte tenu d'une force saisonnière nulle, le SARIMA a été écarté.

Les résidus de la marche aléatoire ont été soumis aux trois tests de diagnostic. Le test de Ljung-Box sur les résidus standardisés ne rejette pas l'absence d'autocorrélation (p = 0,98). Le test de Jarque-Bera rejette la normalité (4 142). Enfin, le test ARCH-LM d'Engle (1982) à 5 retards, dont l'hypothèse nulle est l'absence d'effet ARCH, la rejette nettement (441, p < 0,0001).

![Figure 4. Diagnostic des résidus de l'ARIMA(0,1,0) : série, histogramme, diagramme quantile-quantile et autocorrélations (figure 9 du notebook).](../outputs/figures/fig09_diagnostics_ARIMA010.png){width=15cm}

Nous retenons donc l'ARIMA(0,1,0) sans dérive, c'est-à-dire la marche aléatoire. Ce modèle décrit correctement la moyenne mais pas la variance, qui appelle une modélisation GARCH (section 4.3). L'ARIMA(3,1,2) est conservé comme modèle concurrent pour l'évaluation hors échantillon.

## 4.2 VAR, causalité au sens de Granger, cointégration et VECM

### Modèle VAR des rendements

Le vecteur $\mathbf{r}_t$ des rendements de XOM et de XLE est modélisé par un VAR(p) (Sims, 1980) :

$$\mathbf{r}_t = \mathbf{c} + \sum_{i=1}^{p} A_i\, \mathbf{r}_{t-i} + \mathbf{u}_t .$$

Le critère AIC retient 9 retards et le BIC aucun. Hors 2020 et sur rendements standardisés, les quatre critères d'information retiennent 0 retard, ce qui montre que l'ordre élevé choisi par l'AIC est induit par l'année 2020. Le test portmanteau multivarié de Hosking (1980), appliqué aux résidus standardisés, confirme ce choix : p = 0,77 pour le VAR(0), 0,038 pour le VAR(1), et p < 0,0001 pour le VAR(7) et le VAR(9). L'ajout de retards introduit donc une structure parasite. La corrélation entre les résidus des deux équations atteint 0,915, ce qui indique un lien essentiellement contemporain entre XOM et XLE.

### Causalité au sens de Granger

Le test de Granger (1969) a pour hypothèse nulle que le passé de XLE n'améliore pas la prévision de XOM. Le test F usuel la rejette (p = 0,009), mais il ne la rejette plus lorsque l'on utilise des erreurs-types robustes à l'hétéroscédasticité de type HC3 (MacKinnon et White, 1985), avec p = 0,20. Hors 2020, aucun test robuste ne la rejette au seuil de 5 %. Il n'existe donc pas de prédictibilité croisée robuste. Rappelons que ce test mesure une prédictibilité incrémentale et non une causalité au sens strict.

### Réponses impulsionnelles et décomposition de la variance

Un choc d'un écart-type sur XLE fait varier XOM de +1,63 % le jour même et de −0,08 % le lendemain ; l'effet est ensuite nul, quel que soit l'ordre de la décomposition de Cholesky (figure 5). La décomposition de la variance des erreurs de prévision (FEVD) attribue 83,7 % de la variance de XOM à XLE lorsque XLE est placé en premier, mais seulement 0,3 % lorsque XOM est placé en premier. La valeur de 83,7 % est exactement égale au carré de la corrélation des résidus (0,915²) : la FEVD se borne ici à attribuer la covariance contemporaine à la variable placée en premier. Sans restrictions d'identification supplémentaires, comme celles d'un VAR structurel, il n'est donc pas possible de déterminer laquelle des deux séries entraîne l'autre.

![Figure 5. Réponses impulsionnelles orthogonalisées du VAR(1) pour les deux ordres de Cholesky ; la bande représente l'intervalle de confiance à 95 % (figure 11b du notebook).](../outputs/figures/fig11b_irf.png){width=15cm}

### Cointégration des log-prix

Les log-prix de XOM et de XLE étant tous deux intégrés d'ordre 1, nous avons testé l'existence d'une relation de long terme par les méthodes d'Engle et Granger (1987) et de Johansen (1991). Le tableau 8 résume les résultats.

| Test | H₀ | Statistique | p-value ou seuil | Décision |
| ------------------------ | ---------------- | ---------- | --------------------- | -------------- |
| Engle-Granger (constante) | absence de cointégration | | p = 0,037 | rejet à 5 % |
| Engle-Granger (constante et tendance) | absence de cointégration | | p = 0,105 | non-rejet |
| Johansen, trace (r = 0) | aucune relation | 14,73 | VC à 10 % = 13,43 ; VC à 5 % = 15,49 | rejet à 10 % seulement |
| Engle-Granger, 2016-2019 et 2021-2024 | absence de cointégration | | p = 0,081 et 0,232 | non-rejet |

Table: Tableau 8. Tests de cointégration des log-prix de XOM et de XLE.

La cointégration apparaît faible et fragile. Elle n'est acceptée qu'au seuil de 10 % par le test de Johansen, dépend de la spécification retenue et disparaît dans chacune des sous-périodes. Le VECM est néanmoins estimé à titre conditionnel, avec un rang de cointégration égal à 1 et une constante dans la relation de long terme :

$$\Delta \mathbf{y}_t = \boldsymbol{\alpha}\left(\boldsymbol{\beta}' \mathbf{y}_{t-1} + \mu\right) + \mathbf{u}_t ,$$

où $\mathbf{y}_t$ est le vecteur des log-prix. On obtient β = (1 ; −1,128), soit à long terme ln XOM ≈ 1,128 ln XLE + 0,453. Les coefficients d'ajustement ont le signe attendu mais ne sont pas significatifs (α~XOM~ = −0,0006, p = 0,93 ; α~XLE~ = +0,0093, p = 0,16). La demi-vie d'un écart à l'équilibre, égale à ln(0,5)/ln(1 + β'α), est de 62,6 séances : en 10 jours, la correction ne résorbe qu'environ 10 % d'un écart.

## 4.3 Volatilité conditionnelle : modèles GARCH

Sur les résidus de la marche aléatoire, la statistique ARCH-LM à 5 retards vaut 441,2 (p < 0,0001), ce qui confirme que la variance conditionnelle n'est pas constante. Nous avons comparé quatre structures, GARCH(1,1), GJR(1,1), GARCH(1,2) et GARCH(2,1), combinées à trois lois pour les innovations (normale, Student, Student asymétrique), avec une moyenne nulle. La loi de Student (Bollerslev, 1987) améliore la log-vraisemblance d'environ 37 points par rapport à la loi normale, tandis que la loi asymétrique et les ordres supérieurs n'apportent aucun gain. Le modèle GJR(1,1) de Glosten, Jagannathan et Runkle (1993) avec innovations de Student obtient le meilleur AIC et le meilleur BIC. Il s'écrit :

$$r_t = \varepsilon_t = \sigma_t z_t, \qquad \sigma_t^2 = \omega + \left(\alpha + \gamma\, \mathbb{1}_{\{\varepsilon_{t-1} < 0\}}\right) \varepsilon_{t-1}^2 + \beta\, \sigma_{t-1}^2 ,$$

où $z_t$ suit une loi de Student standardisée à ν degrés de liberté. Le tableau 9 donne les estimations, avec les erreurs-types robustes de Bollerslev et Wooldridge (1992).

| Paramètre | Estimation | p-value | Interprétation |
| ------------ | -------- | -------- | -------------------------------- |
| ω | 0,0094 | 0,066 | constante de la variance |
| α | 0,043 | < 0,001 | réaction aux chocs |
| γ | 0,042 | 0,004 | réaction supplémentaire aux chocs négatifs (levier) |
| β | 0,935 | < 0,001 | persistance de la variance |
| ν | 7,47 | < 0,001 | degrés de liberté (queues épaisses) |

Table: Tableau 9. Estimation du GJR-GARCH(1,1) à loi de Student (échantillon d'apprentissage).

L'hypothèse nulle d'absence d'effet de levier (γ = 0) est rejetée (p = 0,004). Une baisse accroît la variance du lendemain de α + γ = 0,085, contre α = 0,043 pour une hausse de même ampleur, soit un effet environ deux fois plus fort.

La persistance, mesurée par α + β + γ/2, vaut 0,9993 sur l'apprentissage. Elle reste inférieure à 1, de sorte que la condition de stationnarité est respectée, mais de justesse. Cette valeur est gonflée par la rupture de 2020 : elle n'est que de 0,893 sur 2016-2019, soit une demi-vie de 6 jours, contre 0,996 sur 2021-2024. Lamoureux et Lastrapes (1990) ont montré qu'un GARCH tend à confondre un changement de niveau de la volatilité avec une forte persistance.

Les résidus standardisés ne présentent plus d'autocorrélation (Ljung-Box sur $z_t$, p = 0,97). La statistique ARCH-LM à 5 retards passe de 441 à 14,0, soit une baisse de 97 %, mais demeure significative (p = 0,016). Le test de Kolmogorov-Smirnov ne rejette pas l'adéquation à la loi de Student estimée (p = 0,46). Le modèle capte donc l'essentiel de l'hétéroscédasticité, sans l'éliminer entièrement.

![Figure 6. Volatilité conditionnelle annualisée estimée par le GJR-GARCH-t et événements documentés (figure 13 du notebook).](../outputs/figures/fig13_volatilite_conditionnelle.png){width=16cm}

La volatilité estimée suit de près la volatilité réalisée, avec une corrélation de 0,97 (figure 6). Ses pics coïncident avec des événements documentés : 107,4 % le 19 mars 2020 (guerre des prix au sein de l'OPEP+ et pandémie de COVID-19), 46,9 % le 16 mars 2022 (invasion de l'Ukraine) et 52,2 % le 24 juin 2022 (chute des valeurs du secteur de l'énergie). Il convient de souligner qu'un GARCH prévoit l'amplitude des variations et non leur sens.

## 4.4 Reproduction en R et comparaison avec Python

Le socle classique, de la préparation des données au GARCH, est reproduit en R dans le document classical_R.Rmd à l'aide des bibliothèques *quantmod*, *forecast*, *urca*, *vars* et *rugarch*, à partir du même cache de données. Sur les 91 grandeurs comparées, 71 sont identiques (écart inférieur à 0,1 %), 14 sont très proches (écart inférieur à 2 %) et 6 diffèrent davantage. Aucune conclusion n'en est modifiée.

Chacun de ces écarts a une cause identifiée, vérifiée en imposant le même réglage dans les deux langages : l'échantillon utilisé pour choisir les retards de l'ADF et du test d'Engle-Granger, le point de départ de l'optimiseur de l'ARIMA(3,1,2), les ordres examinés par la fonction VARselect (qui n'examine pas l'ordre 0) et la variance initiale du GARCH. Deux de ces écarts sont instructifs : la vraisemblance de l'ARIMA(3,1,2) présente plusieurs maxima, ce qui rend son choix par l'AIC instable, et le test d'Engle-Granger est sensible aux toutes premières observations, ce qui confirme la fragilité de la cointégration.

# 5. Modélisation avancée : réseaux de neurones récurrents (Python uniquement)

## 5.1 Protocole

Les réseaux prévoient directement les 10 rendements suivants de XOM, en une seule sortie, et le prix est ensuite reconstruit par

$$\hat P_{t+h} = P_t \exp\left(\frac{1}{100}\sum_{j=1}^{h} \hat r_{t+j}\right).$$

Aucun réseau n'est entraîné sur les prix bruts, qui ne sont pas stationnaires. Les entrées sont des fenêtres glissantes de 20 ou 60 jours portant sur trois variables : les rendements de XOM et de XLE et la volatilité réalisée de XOM.

La validation repose sur un découpage walk-forward en 5 blocs à fenêtre croissante sur l'apprentissage (TimeSeriesSplit), avec un intervalle de 10 jours entre la partie d'ajustement et la partie d'évaluation pour éviter le chevauchement des cibles. La validation croisée classique par k blocs est exclue. La normalisation est ajustée sur la partie d'ajustement de chaque bloc. L'arrêt précoce (patience de 10 époques) est fondé sur les 10 % finaux de cette partie, avec restauration des meilleurs poids, et chaque configuration est entraînée avec trois graines (42, 43 et 44).

La grille d'hyperparamètres croise les deux architectures, LSTM et GRU, avec deux tailles de fenêtre (20 et 60), deux nombres d'unités (32 et 64) et deux taux de dropout (0,2 et 0,4), soit 16 configurations et 80 entraînements. Le critère de sélection est le gain moyen par rapport à la prévision nulle, calculé sur les mêmes échantillons, car le RMSE brut n'est pas comparable d'une taille de fenêtre à l'autre.

## 5.2 Résultats

Les 16 configurations sont toutes moins précises que la marche aléatoire, avec un gain moyen compris entre −0,14 % et −0,43 %. Les configurations retenues sont un LSTM (fenêtre de 20 jours, 64 unités, dropout de 0,2) et un GRU (fenêtre de 20 jours, 32 unités, dropout de 0,4). Le tableau 10 compare leurs performances en validation.

| Modèle | RMSE moyen sur les 5 blocs (rendements, %) |
| ---------------------------------------- | ------------ |
| Marche aléatoire (prévision nulle) | 1,8450 |
| Moyenne de l'apprentissage | 1,8457 |
| LSTM | 1,8472 |
| GRU | 1,8482 |
| ARIMA(3,1,2) | 1,8501 |
| Hybride ARIMA(3,1,2) et LSTM | 1,8527 |

Table: Tableau 10. Performances en validation walk-forward.

![Figure 7. Courbes de perte des modèles LSTM et GRU retenus, pour les trois graines (figure 15 du notebook).](../outputs/figures/fig15_courbes_perte.png){width=15cm}

La perte de validation est plate dès la première époque (de 0,4348 à 0,4343 au mieux pour le LSTM), ce qui montre que le réseau n'apprend aucune structure généralisable (figure 7). Ses prévisions sont presque constantes, avec un écart-type de 0,058 % contre 1,297 % pour les rendements observés, et leur corrélation avec les rendements réalisés n'est que de 0,016. Le réseau retrouve ainsi, de fait, la marche aléatoire. Le changement de graine modifie la prévision d'un montant comparable à son amplitude, raison pour laquelle nous utilisons la moyenne des trois graines.

Nous avons également estimé un modèle hybride dans l'esprit de Zhang (2003) : l'ARIMA(3,1,2) modélise la partie linéaire et un LSTM ses résidus. Ce modèle ne bat la marche aléatoire sur aucun bloc et fait moins bien que l'ARIMA seul sur 3 blocs sur 5, ce qui indique que les résidus ne contiennent pas de structure non linéaire exploitable dans la moyenne.

Ce résultat confirme, avec une classe de modèles non linéaires, l'absence de structure exploitable dans la moyenne des rendements. Le modèle Prophet n'a pas été estimé, faute de saisonnalité à modéliser.

# 6. Prévision et évaluation hors échantillon

## 6.1 Protocole multi-origines

À chacune des 252 origines de l'échantillon de test, du 27 décembre 2024 au 30 décembre 2025, chaque modèle prévoit le prix de XOM aux horizons h = 1 à 10 en n'utilisant que l'information disponible à cette date. Les modèles classiques sont ré-estimés tous les 20 jours, soit 13 estimations, et leur état est mis à jour quotidiennement ; les réseaux sont entraînés une seule fois sur l'apprentissage. On dispose ainsi de 243 à 252 erreurs de prévision par horizon, nombre nécessaire au test de Diebold-Mariano. Les prévisions calculées par notre code ont été vérifiées identiques à celles de *statsmodels*.

## 6.2 Tableau récapitulatif

Le tableau 11 rassemble les métriques de précision calculées sur le prix en dollars. La MSE, carré du RMSE, figure dans le tableau complet fourni avec le code (outputs/tables/tab36_metriques_prix.csv). La MAPE n'est jamais calculée sur les rendements, dont les valeurs proches de zéro rendraient l'erreur relative instable.

| Modèle | RMSE h=1 | MAE h=1 | MAPE h=1 | RMSE h=5 | MAE h=5 | RMSE h=10 | MAE h=10 | MAPE h=10 |
| -------------------------- | -------- | -------- | --------- | -------- | -------- | --------- | -------- | --------- |
| Marche aléatoire | 1,560 | 1,170 | 1,10 % | 3,617 | 2,762 | 4,650 | 3,487 | 3,29 % |
| ARIMA(3,1,2) | 1,569 | 1,175 | 1,11 % | 3,620 | 2,764 | 4,657 | 3,495 | 3,29 % |
| VAR(1) | 1,561 | 1,166 | 1,10 % | 3,616 | 2,741 | 4,628 | 3,465 | 3,27 % |
| VECM | 1,560 | 1,170 | 1,10 % | 3,618 | 2,763 | 4,652 | 3,489 | 3,29 % |
| Marche aléatoire et GJR-GARCH-t | 1,560 | 1,170 | 1,10 % | 3,617 | 2,762 | 4,650 | 3,487 | 3,29 % |
| LSTM | 1,558 | 1,171 | 1,10 % | 3,672 | 2,810 | 4,867 | 3,668 | 3,46 % |
| GRU | 1,558 | 1,170 | 1,10 % | 3,630 | 2,771 | 4,770 | 3,590 | 3,39 % |
| Hybride ARIMA et LSTM | 1,569 | 1,175 | 1,11 % | 3,670 | 2,807 | 4,866 | 3,666 | 3,46 % |

Table: Tableau 11. Précision des prévisions du prix de XOM sur l'échantillon de test (en dollars).

![Figure 8. RMSE de chaque modèle rapporté à celui de la marche aléatoire, selon l'horizon (figure 18 du notebook).](../outputs/figures/fig18_rmse_relatif.png){width=14cm}

Aucun modèle ne fait nettement mieux que la marche aléatoire (figure 8). Le VAR(1) est le seul à faire légèrement mieux à moyen terme, avec un RMSE inférieur de 0,5 % à 10 jours. Les réseaux font jeu égal à un jour mais se dégradent avec l'horizon (RMSE supérieur de 2,6 % à 4,7 % à 10 jours) : leur légère prévision de baisse s'accumule alors que le cours de XOM a progressé de 17 % en 2025, de 100,69 $ à 117,97 $. Le modèle associant la marche aléatoire au GARCH présente exactement les mêmes erreurs que la marche aléatoire, puisque sa moyenne conditionnelle est nulle.

## 6.3 Test de Diebold-Mariano

Le test de Diebold et Mariano (1995) compare la précision de chaque modèle à celle de la marche aléatoire. Pour un horizon h, on note $d_t = e_{1,t}^2 - e_{2,t}^2$ la différence des pertes quadratiques du modèle et de la marche aléatoire. La statistique est

$$DM = \frac{\bar d}{\sqrt{\hat V(\bar d)}}, \qquad \hat V(\bar d) = \frac{1}{n}\left(\hat\gamma_0 + 2\sum_{k=1}^{h-1}\hat\gamma_k\right),$$

où les $\hat\gamma_k$ sont les autocovariances empiriques de $d_t$. Elle est corrigée selon Harvey, Leybourne et Newbold (1997) par le facteur $\sqrt{\left(n + 1 - 2h + h(h-1)/n\right)/n}$ et comparée à une loi de Student à n − 1 degrés de liberté. Une statistique positive signifie que le modèle est moins précis que la marche aléatoire. Ce test, programmé par nos soins, est reproduit exactement par la fonction dm.test du paquet R *forecast*, l'écart maximal étant de 7 × 10⁻¹⁵ sur 18 tests.

| Modèle comparé à la marche aléatoire | p (h = 1) | p (h = 5) | DM (h = 10) | p (h = 10) | Décision à h = 10 |
| -------------------------- | -------- | -------- | --------- | --------- | ---------------- |
| VAR(1) | 0,985 | 0,976 | −0,40 | 0,69 | pas de différence |
| VECM | 0,839 | 0,608 | 1,01 | 0,32 | pas de différence |
| ARIMA(3,1,2) | 0,411 | 0,384 | 4,11 | < 0,001 | moins précis |
| LSTM | 0,756 | 0,178 | 2,56 | 0,011 | moins précis |
| GRU | 0,728 | 0,686 | 4,45 | < 0,001 | moins précis |
| Hybride ARIMA et LSTM | 0,531 | 0,180 | 2,69 | 0,008 | moins précis |

Table: Tableau 12. Test de Diebold-Mariano contre la marche aléatoire (perte quadratique).

L'hypothèse nulle d'égale précision n'est rejetée en faveur d'aucun modèle, à aucun horizon compris entre 1 et 10 jours (tableau 12). Elle est rejetée en défaveur de l'ARIMA(3,1,2) et des réseaux à l'horizon de 10 jours. La marche aléatoire demeure ainsi la meilleure prévision du prix, conformément à l'efficience faible du marché, et ce sur des données que les modèles n'ont jamais vues.

## 6.4 Intervalles de prévision et prévision de la variance

La qualité des intervalles de prévision à 95 % est évaluée par leur taux de couverture, comparé au taux nominal par un test binomial (tableau 13).

| Intervalles à 95 %, h = 1 | Couverture | Test binomial (H₀ : 95 %) | Largeur moyenne | Couverture à h = 10 |
| --------------------------- | ------------- | ------------------ | ------------ | ------------ |
| Variance constante (marche aléatoire, ARIMA, VAR, VECM) | 98,0 à 98,4 % | p = 0,009 à 0,028 : rejet | 7,42 à 7,46 $ | 96,3 % |
| GJR-GARCH-t (intervalles simulés) | 94,8 % | p = 0,885 : non-rejet | 6,27 $ | 94,7 % |

Table: Tableau 13. Couverture et largeur des intervalles de prévision sur le test.

![Figure 9. Intervalles de prévision à un jour sur l'échantillon de test : variance constante et GJR-GARCH-t (figure 19 du notebook).](../outputs/figures/fig19_intervalles_test.png){width=16cm}

Les intervalles fondés sur une variance constante sont trop larges, car cette variance agrège tout le passé, y compris la crise de 2020, alors que l'année 2025 est plus calme (figure 9). Le GJR-GARCH-t atteint une couverture correcte avec des intervalles plus étroits de 16 %, parce qu'il s'adapte au régime de volatilité courant. C'est le résultat le plus utile de l'évaluation : si aucun modèle ne prévoit mieux le niveau du prix, le GARCH en prévoit mieux l'incertitude.

La variance prévue à un jour est évaluée séparément à l'aide de la perte QLIKE (Patton, 2011), $L_t = \ln \hat\sigma_t^2 + r_{t+1}^2 / \hat\sigma_t^2$, qui reste fiable lorsque le rendement au carré sert d'approximation bruitée de la variance. Le GJR-GARCH-t obtient la perte la plus faible (1,732), devant le lissage exponentiel EWMA (1,738), la volatilité réalisée sur 21 jours (1,764) et la variance constante (1,844). L'écart avec la variance constante n'est toutefois significatif qu'au seuil de 10 % (Diebold-Mariano, p = 0,075) : une seule année de test, qui ne comporte qu'une véritable période agitée (avril 2025), offre une puissance limitée. Les paramètres du GJR restent stables sur les 13 ré-estimations (γ entre 0,039 et 0,046, β entre 0,933 et 0,936).

## 6.5 Comparaison détaillée et choix du modèle

Le tableau 14 confronte les modèles selon la précision, la calibration des intervalles, l'interprétabilité et le coût de calcul.

| Modèle | RMSE h=10 ($) | Écart à la référence | Diebold-Mariano h=10 | Couverture IC 95 % h=1 | Interprétabilité | Coût de calcul |
| ------------------- | ----------- | ----------- | ------------- | ------------ | ------------------ | ------------------ |
| Marche aléatoire | 4,650 | référence | | 98,0 % | totale | nul |
| ARIMA(3,1,2) | 4,657 | +0,1 % | moins précis | 98,0 % | faible (racines compensées) | 14 s (13 estimations) |
| VAR(1) | 4,628 | −0,5 % | non significatif | 98,4 % | bonne (IRF, Granger) | moins de 1 s |
| VECM | 4,652 | +0,04 % | non significatif | 98,0 % | bonne (équilibre, demi-vie) | moins de 1 s |
| Marche aléatoire et GJR-GARCH-t | 4,650 | 0 | identique | 94,8 % | bonne (levier, persistance) | 5 s (13 estimations) |
| LSTM | 4,867 | +4,7 % | moins précis | | très faible | grille de 80 entraînements (environ 10 min) et 3 graines |
| GRU | 4,770 | +2,6 % | moins précis | | très faible | idem |
| Hybride ARIMA et LSTM | 4,866 | +4,6 % | moins précis | | très faible | ARIMA et 3 graines de LSTM |

Table: Tableau 14. Comparaison détaillée des modèles.

Le modèle finalement retenu associe un ARIMA(0,1,0) à un GJR-GARCH(1,1) à loi de Student. Pour le niveau du prix, la marche aléatoire n'est battue par aucun modèle ; elle est en outre sans coût et parfaitement interprétable. Pour le risque, qu'il s'agisse des intervalles de prévision, de la valeur à risque ou du dimensionnement des positions, le GJR-GARCH-t est le seul modèle bien calibré, tout en restant interprétable et peu coûteux. Le VAR et le VECM servent à comprendre le lien entre XOM et XLE plutôt qu'à prévoir. L'évaluation hors échantillon confirme ainsi le choix établi sur l'apprentissage à la section 4.

# 7. Extensions

## 7.1 Corrélation dynamique

La corrélation entre les rendements de XOM et de XLE, calculée sur des fenêtres glissantes de 60 jours, varie sensiblement au cours du temps : 0,82 en moyenne sur 2016-2019, 0,94 en 2020, 0,93 sur 2021-2024 et 0,88 en 2025. La hausse de niveau (+0,11) excède nettement l'incertitude d'une corrélation estimée sur 60 jours, de l'ordre de ±0,05. Après chacun des six événements documentés, la corrélation mesurée 60 jours plus tard est plus élevée, par exemple de 0,88 à 0,95 après l'annonce des droits de douane d'avril 2025. En période de crise, le choc commun domine et la diversification au sein du secteur disparaît.

Le modèle DCC-GARCH d'Engle (2002) formalise cette dynamique :

$$Q_t = (1-a-b)\,\bar Q + a\, \mathbf{z}_{t-1} \mathbf{z}_{t-1}' + b\, Q_{t-1},$$

où $\mathbf{z}_t$ est le vecteur des rendements standardisés par leurs GARCH univariés et où la matrice de corrélation conditionnelle s'obtient en normalisant $Q_t$. Estimé sur l'apprentissage par notre propre code et vérifié avec le paquet R *rmgarch*, il donne a = 0,026 (erreur-type 0,006) et b = 0,970 (0,008). La corrélation réagit donc au choc commun de la veille et persiste longtemps, la demi-vie d'un choc étant d'environ 145 jours. Le test d'Engle et Sheppard (2001), dont l'hypothèse nulle est une corrélation constante, la rejette nettement : χ²(6) = 34,3, p < 0,0001, et 32,1 hors 2020.

![Figure 10. Corrélation conditionnelle DCC-GARCH et corrélation glissante sur 60 jours ; les numéros d'événements renvoient à la figure 21 du notebook (figure 23 du notebook).](../outputs/figures/fig23_dcc_garch.png){width=16cm}

La corrélation DCC suit la corrélation glissante, avec laquelle elle est corrélée à 0,946, tout en étant plus lisse et plus réactive (figure 10). Filtrée sur 2025 avec les paramètres estimés sur l'apprentissage, elle culmine à 0,92 le 11 avril 2025. Ce résultat a une application directe : le ratio de couverture de XOM par XLE, $\beta_t = \rho_t\, \sigma_{XOM,t} / \sigma_{XLE,t}$, varie dans le temps, et le calculer avec une corrélation constante le fausserait dans un sens comme dans l'autre.

## 7.2 Le Brent comme variable exogène

Nous avons estimé un VAR(1) des rendements de XOM et de XLE augmenté du rendement du Brent, soit du jour même, soit de la veille. L'estimation est faite par moindres carrés ordinaires équation par équation, avec des erreurs-types HC3, et les résultats sont identiques à ceux de *statsmodels* (tableau 15).

| Version | Coefficient du Brent (équation de XOM) | p-value HC3 | R² de l'équation de XOM | Hors 2020 |
| ---------------- | ------------------ | ---------- | --------------- | ------------------ |
| Brent du jour même | 0,371 | < 0,001 | de 0,4 % à 27,9 % | 0,374 ; p < 0,001 |
| Brent de la veille | −0,005 | 0,86 | inchangé | −0,027 ; p = 0,24 |

Table: Tableau 15. Effet du rendement du Brent dans l'équation de XOM (VARX).

Le Brent explique les rendements de XOM le jour même, une hausse de 1 % du Brent s'accompagnant d'une hausse de 0,37 % de XOM, mais le Brent de la veille ne prévoit rien. Sur l'échantillon de test, le VARX ne fait mieux ni que le VAR(1) ni que la marche aléatoire (Diebold-Mariano, p = 0,69 à 10 jours) ; il a été évalué selon le même protocole que les modèles du tableau 11. Le lien entre XOM et le Brent reste d'ailleurs lâche, avec une corrélation de 0,53. Le 21 avril 2020, le Brent perd 24,4 % alors que XOM ne recule que de 0,5 %. XOM demeure avant tout une action, sensible au marché boursier et à la politique propre de l'entreprise, et pas seulement au prix du pétrole.

## 7.3 Extension non réalisée

Une analyse du sentiment des communiqués de l'entreprise à l'aide du modèle FinBERT a été écartée pour une raison méthodologique. Le corpus disponible sur l'ensemble de la période ne compte qu'une quarantaine d'annonces de résultats, ce qui est insuffisant pour tester de façon fiable un effet du sentiment sur les rendements. Nous avons préféré approfondir la corrélation dynamique et le rôle de la variable exogène.

# 8. Apport de l'intelligence artificielle générative

## 8.1 Protocole

Conformément au cahier des charges, nous avons d'abord rédigé notre propre interprétation des résultats, datée du 8 novembre 2026 (annexe B), avant de solliciter un modèle de langage (ChatGPT, agent GPT-6), chaque fois dans une nouvelle conversation. Trois tâches lui ont été confiées : formuler des hypothèses de modèles à partir des seules statistiques descriptives et des tests de stationnarité ; vulgariser nos résultats à l'intention d'un directeur financier non statisticien ; enfin, formuler des recommandations d'investissement simulées à partir de nos prévisions, en énonçant lui-même leurs limites. Un premier envoi de la troisième tâche a eu lieu par erreur sans les données ; nous l'avons conservé, car il est instructif.

Les prompts et les réponses intégrales figurent en annexe C. Chaque réponse a été confrontée à une grille de neuf types d'erreurs à rechercher, parmi lesquelles les p-values inventées, la causalité attribuée au test de Granger, la direction des prix attribuée au GARCH, les causes non fondées et l'excès de confiance.

## 8.2 Résultats de la comparaison

Le tableau 16 classe les observations issues de cette comparaison, détaillée en annexe D.

| Type d'observation | Nombre | Exemples |
| ------------------- | -------- | ---------------------------------------- |
| Convergences et comportements corrects | 5 | Association marche aléatoire et GARCH-t proposée d'emblée ; aucune p-value inventée ; tests correctement lus ; absence de données signalée |
| Divergence | 1 | Rendement retardé de XLE proposé comme prédicteur, alors que notre test de Granger robuste le rejette |
| Oublis | 2 | Aucun test de cointégration alors que les deux log-prix sont intégrés ; FEVD passée sous silence |
| Simplifications ou ajouts non fondés | 3 | Persistance du GARCH prise à la lettre ; cause des pics de 2022 avancée sans source ; corrélation des chocs présentée comme celle des rendements |
| Erreurs de raisonnement | 2 | Recommandation d'achat « si la prévision est favorable » avec une marche aléatoire, dont la prévision est constante ; recommandation de conservation justifiée par l'absence de signal de vente |
| GARCH présenté comme prévoyant la direction | 2 | « Direction des prévisions » ; « ne prédit pas avec certitude la direction du cours » |
| Vocabulaire causal ou statistique impropre | 2 | « Influence » pour le test de Granger ; « intervalle de confiance » pour un intervalle de prévision |

Table: Tableau 16. Synthèse de la comparaison entre notre interprétation et celle du modèle de langage.

Le modèle de langage retrouve rapidement les grandes lignes d'une stratégie de modélisation adaptée, à savoir un ARIMA associé à un GARCH à loi de Student et les diagnostics correspondants, et il reformule clairement des résultats vérifiés à l'intention d'un public non spécialiste. Il a permis de gagner du temps sur la rédaction et la structuration, et sa suggestion d'un modèle EGARCH ou GJR rejoint notre propre choix.

Il ne contrôle pas, en revanche, la cohérence entre un modèle et la décision qui en découle. Il envisage des scénarios impossibles avec une marche aléatoire et recommande de conserver l'action sans justification. Il omet les résultats qui nuancent l'analyse, comme la fragilité de la cointégration ou la dépendance de la FEVD à l'ordre des variables, et il ajoute des explications causales qui ne lui ont pas été fournies. Un décideur qui ne lirait que ses réponses retiendrait une image trop simple et trop assurée des résultats.

# 9. Discussion et conclusion

## 9.1 Limites des modèles

Plusieurs hypothèses des modèles ne sont pas vérifiées. Les résidus ne sont jamais normaux, le test de Jarque-Bera rejetant la normalité pour tous les modèles, et un effet ARCH résiduel subsiste après le GJR (ARCH-LM, p = 0,016). Les erreurs-types robustes et la loi de Student atténuent ces écarts sans les supprimer.

L'année 2020 pèse sur plusieurs résultats : le choix de l'ordre du VAR par les critères d'information, l'autocorrélation apparente des rendements, la persistance du GARCH (0,999 contre 0,893 avant 2020) et la significativité du SARIMA. Nous l'avons vérifié systématiquement par des analyses excluant 2020 ou portant sur les rendements standardisés, mais un modèle à changement de régime serait mieux adapté à cette rupture.

L'échantillon de test se limite à une année, calme et haussière (+17 %), qui ne constitue qu'une réalisation de l'histoire. Le test portant sur la variance (p = 0,075) manque de puissance, et le classement des modèles pourrait différer dans un régime de crise. Par ailleurs, les réseaux n'ont pas été ré-entraînés au cours du test, ce qui ne les désavantage guère puisqu'ils n'apprennent rien sur l'apprentissage, et leur grille d'hyperparamètres est restreinte. Les coûts de transaction ont été ignorés, ce qui ne pourrait que renforcer la conclusion. Enfin, la cointégration est fragile et sensible aux premières observations : la demi-vie de 62,6 jours n'est qu'une estimation ponctuelle à interpréter avec prudence.

## 9.2 L'IA générative appliquée aux séries temporelles

L'IA générative se révèle utile comme outil d'assistance. Elle accélère l'écriture du code, la recherche de méthodes et la reformulation, et elle propose des pistes raisonnables. En séries temporelles financières, ses faiblesses sont cependant particulièrement dangereuses. Elle raisonne par associations plausibles, du type « le pétrole monte, donc XOM montera demain », confond explication et prévision et attribue facilement des causes à de simples corrélations. Elle ne vérifie ni les hypothèses d'un test ni la cohérence d'une recommandation.

Son usage exige donc un contrôle humain systématique : une interprétation personnelle rédigée au préalable, la vérification de chaque chiffre au regard des sorties du code et une grille d'erreurs explicite. Dans ces conditions, elle fait gagner du temps sans dégrader la rigueur de l'analyse. Utilisée sans ce contrôle, elle conduirait à des recommandations d'investissement trop assurées et insuffisamment fondées.

## 9.3 Conclusion

Ce travail apporte une réponse claire à la question posée. Le prix de XOM n'est pas prévisible à un horizon de 1 à 10 jours mieux que par une marche aléatoire. Ni les modèles linéaires (ARIMA, VAR, VECM, VARX) ni les réseaux de neurones (LSTM, GRU, modèle hybride) ne la battent significativement hors échantillon, et plusieurs font significativement moins bien. Ce résultat négatif est cohérent à toutes les étapes de l'analyse, de l'étude exploratoire au test de Diebold-Mariano, et il est conforme à l'efficience faible du marché.

Le risque est en revanche prévisible. Le GJR-GARCH à loi de Student capte le regroupement des fortes variations et l'effet de levier, et il fournit les seuls intervalles de prévision correctement calibrés sur l'année 2025. Le lien entre XOM et son secteur est fort, essentiellement contemporain, et varie dans le temps, comme le montre le DCC-GARCH.

Ces conclusions illustrent un principe rappelé par le cahier des charges : un modèle simple et bien diagnostiqué vaut mieux qu'un modèle complexe insuffisamment validé. Trois prolongements paraissent naturels : des modèles à changement de régime pour la volatilité, des réseaux de neurones appliqués à la variance plutôt qu'à la moyenne, et une analyse du sentiment fondée sur un corpus de presse quotidien de grande taille.

Les sources des faits externes cités (événements de marché, composition de l'ETF XLE) sont recensées dans le fichier docs/sources.md ; chaque fait y est recoupé avec nos données lorsque c'est possible.

# Références bibliographiques

::: {custom-style="Bibliography"}
Bollerslev, T. (1986). Generalized autoregressive conditional heteroskedasticity. *Journal of Econometrics*, 31(3), 307-327.

Bollerslev, T. (1987). A conditionally heteroskedastic time series model for speculative prices and rates of return. *The Review of Economics and Statistics*, 69(3), 542-547.

Bollerslev, T. et Wooldridge, J. M. (1992). Quasi-maximum likelihood estimation and inference in dynamic models with time-varying covariances. *Econometric Reviews*, 11(2), 143-172.

Box, G. E. P. et Jenkins, G. M. (1976). *Time Series Analysis: Forecasting and Control* (édition révisée). San Francisco : Holden-Day.

Cho, K., van Merriënboer, B., Gulcehre, C., Bahdanau, D., Bougares, F., Schwenk, H. et Bengio, Y. (2014). Learning phrase representations using RNN encoder-decoder for statistical machine translation. *Proceedings of the 2014 Conference on Empirical Methods in Natural Language Processing (EMNLP)*, 1724-1734.

Cleveland, R. B., Cleveland, W. S., McRae, J. E. et Terpenning, I. (1990). STL: A seasonal-trend decomposition procedure based on loess. *Journal of Official Statistics*, 6(1), 3-73.

Dickey, D. A. et Fuller, W. A. (1979). Distribution of the estimators for autoregressive time series with a unit root. *Journal of the American Statistical Association*, 74(366), 427-431.

Diebold, F. X. et Mariano, R. S. (1995). Comparing predictive accuracy. *Journal of Business & Economic Statistics*, 13(3), 253-263.

Engle, R. F. (1982). Autoregressive conditional heteroscedasticity with estimates of the variance of United Kingdom inflation. *Econometrica*, 50(4), 987-1007.

Engle, R. F. (2002). Dynamic conditional correlation: A simple class of multivariate generalized autoregressive conditional heteroskedasticity models. *Journal of Business & Economic Statistics*, 20(3), 339-350.

Engle, R. F. et Granger, C. W. J. (1987). Co-integration and error correction: Representation, estimation, and testing. *Econometrica*, 55(2), 251-276.

Engle, R. F. et Sheppard, K. (2001). Theoretical and empirical properties of dynamic conditional correlation multivariate GARCH. *NBER Working Paper* n° 8554.

Fama, E. F. (1970). Efficient capital markets: A review of theory and empirical work. *The Journal of Finance*, 25(2), 383-417.

Glosten, L. R., Jagannathan, R. et Runkle, D. E. (1993). On the relation between the expected value and the volatility of the nominal excess return on stocks. *The Journal of Finance*, 48(5), 1779-1801.

Granger, C. W. J. (1969). Investigating causal relations by econometric models and cross-spectral methods. *Econometrica*, 37(3), 424-438.

Harvey, D., Leybourne, S. et Newbold, P. (1997). Testing the equality of prediction mean squared errors. *International Journal of Forecasting*, 13(2), 281-291.

Hochreiter, S. et Schmidhuber, J. (1997). Long short-term memory. *Neural Computation*, 9(8), 1735-1780.

Hosking, J. R. M. (1980). The multivariate portmanteau statistic. *Journal of the American Statistical Association*, 75(371), 602-608.

Jarque, C. M. et Bera, A. K. (1980). Efficient tests for normality, homoscedasticity and serial independence of regression residuals. *Economics Letters*, 6(3), 255-259.

Johansen, S. (1991). Estimation and hypothesis testing of cointegration vectors in Gaussian vector autoregressive models. *Econometrica*, 59(6), 1551-1580.

Kruskal, W. H. et Wallis, W. A. (1952). Use of ranks in one-criterion variance analysis. *Journal of the American Statistical Association*, 47(260), 583-621.

Kwiatkowski, D., Phillips, P. C. B., Schmidt, P. et Shin, Y. (1992). Testing the null hypothesis of stationarity against the alternative of a unit root. *Journal of Econometrics*, 54(1-3), 159-178.

Lamoureux, C. G. et Lastrapes, W. D. (1990). Persistence in variance, structural change, and the GARCH model. *Journal of Business & Economic Statistics*, 8(2), 225-234.

Ljung, G. M. et Box, G. E. P. (1978). On a measure of lack of fit in time series models. *Biometrika*, 65(2), 297-303.

MacKinnon, J. G. et White, H. (1985). Some heteroskedasticity-consistent covariance matrix estimators with improved finite sample properties. *Journal of Econometrics*, 29(3), 305-325.

Newey, W. K. et West, K. D. (1987). A simple, positive semi-definite, heteroskedasticity and autocorrelation consistent covariance matrix. *Econometrica*, 55(3), 703-708.

Patton, A. J. (2011). Volatility forecast comparison using imperfect volatility proxies. *Journal of Econometrics*, 160(1), 246-256.

Sims, C. A. (1980). Macroeconomics and reality. *Econometrica*, 48(1), 1-48.

Zhang, G. P. (2003). Time series forecasting using a hybrid ARIMA and neural network model. *Neurocomputing*, 50, 159-175.

Zivot, E. et Andrews, D. W. K. (1992). Further evidence on the great crash, the oil-price shock, and the unit-root hypothesis. *Journal of Business & Economic Statistics*, 10(3), 251-270.
:::

```{=openxml}
<w:p><w:r><w:br w:type="page"/></w:r></w:p>
```

# Annexes

## Annexe A. Reproduction des résultats

| Étape | Commande |
| ---------------- | ---------------------------------------- |
| Installation complète (Python 3.11 et R 4.3 ou plus récent) | `python install.py` ; l'environnement Python est placé dans un dossier court si le chemin du projet dépasse la limite de 260 caractères de Windows, puis les paquets R sont installés |
| Exécution des deux notebooks | `python run_all.py` (notebook Python en 13 min environ, puis document R en 1 min 30 s environ) |
| Environnement Python, installation manuelle | `pip install -r requirements.txt` (versions exactes dans requirements-lock.txt) |
| Environnement R, installation manuelle | `Rscript install_packages.R` (instantané CRAN daté) |
| Étude complète en Python, exécution manuelle | `jupyter nbconvert --to notebook --execute notebooks/main_python.ipynb` |
| Socle classique en R | `Rscript -e "rmarkdown::render('notebooks/classical_R.Rmd')"`, après le notebook Python dont il relit les exports |
| Rapport Word | `python rapport/build_rapport.py` |

Table: Tableau A.1. Commandes de reproduction.

Les paramètres de l'étude (symboles boursiers, dates, découpage, horizon, graine) sont centralisés dans le fichier config.yaml, et les données sont figées dans data/raw/. Les tableaux détaillés au format CSV se trouvent dans outputs/tables/, numérotés comme dans le notebook, et les figures dans outputs/figures/.
