# Préparation de la soutenance (phases 0 à 3.3)

Questions probables du jury et réponses courtes, appuyées sur nos propres résultats. Les numéros de section renvoient au notebook `notebooks/main_python.ipynb`.

## Données et méthode générale

**Pourquoi XOM et XLE ?**
Une action et l'ETF de son secteur partagent un facteur commun (XOM pèse environ un quart de XLE : 24,47 % en novembre 2026). Ce couple permet d'étudier la cointégration et la volatilité sur des crises identifiables : 2020 et 2022.

**Pourquoi l'Adj Close plutôt que le Close ?**
L'Adj Close réintègre les dividendes, et mesure donc le rendement réellement obtenu. Sur Yahoo, le Close est déjà ajusté des splits.

**Pourquoi lire le cache plutôt que retélécharger ?**
Yahoo recalcule l'Adj Close de tout l'historique à chaque nouveau dividende. Sans fichier figé, deux exécutions à des dates différentes donneraient des chiffres différents.

**Pourquoi ne pas remplir les jours fériés (ffill) ?**
Recopier le prix de la veille crée des rendements exactement nuls qui n'ont jamais existé. La variance serait sous-estimée et le GARCH biaisé.

**Pourquoi tester sur le train uniquement ?**
Choisir un modèle en regardant le test, c'est utiliser l'avenir pour décider : une fuite d'information. Le test ne sert qu'à l'évaluation finale (section 6).

**Le test est plus calme que le train : est-ce un problème ?**
C'est une limite, pas une erreur : la volatilité réalisée maximale de XOM vaut 47 % sur le test, contre 109 % sur le train. Le découpage chronologique 90/10 est imposé par le cahier, et choisir la période de test après coup serait un biais. On le signale, et la validation walk-forward (section 4) évalue aussi les modèles sur des périodes agitées.

## Analyse exploratoire (§2)

**Pourquoi ADF et KPSS ensemble ?**
Leurs hypothèses nulles sont opposées : racine unitaire pour l'ADF, stationnarité pour le KPSS. Quand les deux concordent, la conclusion est solide. Pour le log-prix, l'ADF ne rejette pas (p ≥ 0,53) et le KPSS rejette (p < 0,01) : I(1). Pour les rendements, c'est l'inverse : I(0). Donc **d = 1**.

**Le krach de 2020 ne fausse-t-il pas l'ADF ?**
C'est le risque identifié par Perron (1989). On l'a testé avec Zivot-Andrews, qui autorise une rupture : la racine unitaire n'est toujours pas rejetée (p de 0,18 à 0,48).

**Ljung-Box rejetait le bruit blanc pour les rendements. Pourquoi conclure qu'ils sont un bruit blanc ?**
Ljung-Box suppose une variance constante. En divisant les rendements par leur volatilité récente, le rejet disparaît (p = 0,98), et il disparaît aussi sans l'année 2020 (p = 0,44). L'autocorrélation apparente venait de la variance, pas de la moyenne.

**Rendements non autocorrélés veut-il dire indépendants ?**
Non. Les rendements sont imprévisibles en moyenne, mais leurs carrés sont fortement autocorrélés : les 40 retards sont significatifs, avec un maximum de 0,32. Leur amplitude est donc en partie prévisible, d'où le GARCH.

**Pourquoi garder les valeurs aberrantes ?**
Ce sont des chocs réels et documentés : guerre des prix du pétrole le 2020-03-09, vaccin le 2020-11-09, droits de douane en avril 2025. Ils sont communs aux deux actifs (11 jours). Les supprimer ferait disparaître ce que le GARCH doit modéliser et rétrécirait à tort les intervalles de prévision. On ajoute seulement une variable indicatrice.

**Et si vous changez le seuil de détection ?**
Le nombre de jours signalés varie de 11 à 66 selon le réglage. Mais un noyau de 11 jours (XOM) et de 14 jours (XLE), signalés par au moins 12 réglages sur 16, est entièrement retrouvé par notre réglage. Et comme les outliers sont conservés, le seuil ne change que l'indicatrice.

## ARIMA (§3.1)

**Pourquoi la marche aléatoire, alors qu'`auto_arima` choisit ARIMA(3,1,2) ?**
1. **Le BIC choisit la marche aléatoire.** Il est convergent et pénalise davantage : 7,7 points par paramètre contre 2 pour l'AIC sur 2 261 observations.
2. **Les racines d'ARIMA(3,1,2) s'annulent presque.** AR et MA ont des modules de 1,047 et 1,075 et décrivent le même cycle de 2,4 jours : le modèle est quasi non identifié.
3. **Son gain d'AIC vient de 2020.** Il s'inverse sur les rendements standardisés : +9,2.
4. **Ses résidus standardisés restent autocorrélés** (p = 0,013), contrairement à ceux de la marche aléatoire (p = 0,98).

On le garde comme concurrent pour l'évaluation hors échantillon (section 6).

**Qu'est-ce qu'une quasi-annulation des racines ?**
Quand le polynôme AR et le polynôme MA ont presque les mêmes racines, ils se simplifient dans φ(L)/θ(L). Le modèle équivaut alors à un modèle plus petit, avec des coefficients énormes et opposés (ici −1,66 et +1,65).

**L'AIC et le test du rapport de vraisemblance favorisaient le SARIMA. Pourquoi l'écarter ?**
Le test LR compare des vraisemblances gaussiennes à variance constante. Avec des effets ARCH, il rejette trop souvent. Le test de Wald robuste ne trouve pas le coefficient saisonnier significatif (p = 0,12), le BIC ne voit aucun gain, et sans 2020 le terme saisonnier dégrade l'AIC. Enfin, « s = 5 » n'est même pas une semaine fixe : à cause des jours fériés, seuls 82 % des couples (t, t−5) tombent le même jour de la semaine.

**Les résidus de la marche aléatoire ne sont pas normaux : le modèle est-il invalide ?**
Il décrit correctement la moyenne : aucune autocorrélation une fois la volatilité neutralisée. Ce qu'il ne modélise pas, c'est la variance (ARCH-LM = 441) et les queues épaisses (Jarque-Bera = 4 142). Ce sont exactement les défauts que traite un GARCH à loi de Student.

**Pourquoi des erreurs-types robustes ?**
Avec de l'hétéroscédasticité, les erreurs-types classiques sont trop petites et font paraître significatifs des coefficients qui ne le sont pas.

## VAR, Granger, cointégration (§3.2)

**Pourquoi le VAR sur les rendements et la cointégration sur les log-prix ?**
Le VAR exige des séries stationnaires : les rendements sont I(0). La cointégration n'a de sens qu'entre séries I(1), puisqu'elle cherche une combinaison stationnaire de deux séries qui ne le sont pas.

**Granger, est-ce une causalité ?**
Non. « XLE cause XOM au sens de Granger » signifie seulement que le passé de XLE améliore la prévision de XOM. Les deux réagissent à la même information sectorielle, et un décalage peut venir de différences de liquidité. Ici, il n'y a de toute façon pas de prédictibilité robuste : le test F classique rejette, mais les tests robustes sans 2020 ne rejettent plus au seuil de 5 %.

**Pourquoi le VAR(0) quand l'AIC propose 9 retards ?**
Sans 2020, ou sur rendements standardisés, les quatre critères choisissent 0 retard. Le saut de l'AIC au retard 7 venait de 2020, et le VAR(0) est le seul dont les résidus standardisés ne sont pas autocorrélés (p = 0,77).

**Y a-t-il cointégration ?**
Elle est faible et fragile :
- Engle-Granger rejette l'absence de cointégration à 5 % (p = 0,037) ;
- Johansen, avec l'ordre robuste, ne rejette qu'à 10 % (trace 14,73 contre une valeur critique de 15,49 à 5 %) ;
- elle n'est significative dans aucune des deux sous-périodes.

On estime le VECM conditionnellement, comme le demande le cahier.

**Que signifient β et α ?**
β est l'équilibre de long terme : ln XOM ≈ 1,128 × ln XLE − 0,453. α mesure la réaction de chaque actif à l'écart : α(XOM) ≈ 0 (p = 0,93) et α(XLE) = +0,009 (p = 0,16). Si l'ajustement existe, c'est XLE qui comble l'écart, mais aucun α n'est significatif.

**Pourquoi la demi-vie utilise β′α et pas α ?**
L'écart z = β′y évolue selon z_t = (1 + β′α) z_{t−1}. Quand les deux actifs s'ajustent, la vitesse de l'écart combine les deux α. La formule ln(0,5)/ln(1 + α) ne vaut que si un seul actif s'ajuste : avec α(XOM), elle donnerait plus de 1 200 jours. On trouve **62,6 jours**, et un AR(1) estimé directement sur l'écart donne la même valeur.

**Le VECM va-t-il mieux prévoir à 10 jours ?**
Probablement pas. Avec une demi-vie de 63 jours, le rappel ne corrige qu'environ 10 % d'un écart en 10 jours. La section 6 le vérifiera.

**Que montrent les IRF et la FEVD ?**
Un choc sur XLE fait bouger XOM de +1,63 % le jour même, et la réponse est nulle dès le 2ᵉ jour, avec les deux ordres de Cholesky. Il n'y a donc pas de transmission retardée, ce qui confirme le test de Granger.

**XLE explique 84 % de la variance de XOM : XLE entraîne donc XOM ?**
Non. Avec l'ordre inverse, ce chiffre tombe à 0,3 %. Les 84 % sont simplement la corrélation des chocs au carré (0,915²) : la FEVD attribue le choc commun du jour même à la variable placée en premier. On ne peut pas dire qui entraîne qui sans un SVAR ou des données intrajournalières.

## GARCH (§3.3)

**Pourquoi un GARCH ?**
Les résidus de tous les modèles précédents ont des effets ARCH massifs (ARCH-LM(5) = 441) : les gros chocs se suivent. Le GARCH modélise la variance conditionnelle σ²_t, c'est-à-dire l'amplitude attendue demain. Il ne prévoit pas le sens du prix.

**Pourquoi la loi de Student ?**
Elle gagne 37,5 points de log-vraisemblance face à la loi normale pour un seul paramètre en plus (ν ≈ 7,5). Le test de Kolmogorov-Smirnov ne rejette pas l'adéquation des résidus standardisés à cette loi (p = 0,46).

**Qu'est-ce que l'effet de levier ?**
Dans le GJR, γ = 0,042 (p = 0,004) : après une baisse, la variance réagit avec α + γ = 0,085, soit deux fois plus qu'après une hausse (α = 0,043). Les mauvaises nouvelles augmentent davantage le risque. La figure 14 le montre : un choc de −3 % donne une variance de 3,87 le lendemain, contre 3,49 pour +3 %.

**Que signifie α + β ≈ 0,999 ?**
Une volatilité presque infiniment persistante : la demi-vie d'un choc serait de 2 à 4 ans, et la variance de long terme serait quatre fois la variance observée. Ce n'est pas crédible. Par sous-période, la persistance vaut 0,893 sur 2016–2019 (demi-vie de 6 jours) et 0,996 sur 2021–2024. La valeur proche de 1 est gonflée par le changement de niveau de la volatilité en 2020 : c'est l'effet décrit par Lamoureux et Lastrapes (1990).

**Les résidus standardisés sont-ils propres ?**
Presque. Ils ne sont plus autocorrélés (p = 0,97), et l'ARCH-LM tombe de 441 à 14, soit 97 % de moins. Un léger reste est significatif à 5 % (p = 0,016), mais il disparaît à 20 retards. Le GARCH(1,2) le supprime au prix de coefficients non identifiés : on ne l'a pas retenu.

**Pourquoi la volatilité monte-t-elle le lendemain du choc, et pas le jour même ?**
σ_t est calculée avec l'information disponible la veille. Le choc du 9 novembre 2020 (+11,9 %) fait passer σ de 36 % à 52 % le 10 novembre.

**Le pic de 2022, c'est la guerre en Ukraine ?**
En partie. L'invasion produit un pic de 46,9 % le 16 mars 2022. Mais le maximum de l'année (52,2 %) date du 24 juin 2022, lors de la chute du pétrole et des craintes de récession, quand le secteur de l'énergie perd 16,8 % en un mois (S&P Global).

## R et Python (§8.1)

**Pourquoi le projet existe-t-il en deux langages ?**
Le cahier l'exige pour le socle classique (§8.1). `notebooks/classical_R.Rmd` reproduit les phases 1 à 3 avec quantmod, forecast, urca, vars et rugarch, puis compare 91 grandeurs à leur valeur Python.

**Les résultats sont-ils les mêmes ?**
Oui : 71 grandeurs identiques à moins de 0,1 %, 14 à moins de 2 %, et 6 écarts, tous expliqués. **Aucune conclusion ne change.**

**D'où viennent les écarts ?**
Uniquement de réglages par défaut différents, et à chaque fois on retrouve le résultat Python en imposant le même réglage en R :
- échantillon utilisé pour choisir les retards de l'ADF et d'Engle-Granger ;
- point de départ de l'optimiseur pour l'ARIMA(3,1,2) ;
- variance initiale du GARCH ;
- `VARselect` qui ne teste pas l'ordre 0.

**Un écart vous a-t-il appris quelque chose ?**
Oui, deux choses :
1. **L'ARIMA(3,1,2) a une vraisemblance à plusieurs sommets.** R s'arrête sur un sommet plus bas, et son `auto.arima` choisit alors ARIMA(5,1,0). Le choix de l'AIC est donc instable, alors que celui du BIC (marche aléatoire) est le même dans les deux langages.
2. **Le test d'Engle-Granger dépend fortement des 8 premières observations** (janvier 2016) : la cointégration est fragile.

## Deep learning (§4)

**Pourquoi ne pas entraîner le réseau sur les prix ?**
Les prix sont I(1) : un réseau entraîné dessus apprend à recopier la dernière valeur, ce qui donne une illusion de précision. On prédit donc les 10 rendements suivants, puis on reconstruit le prix.

**Comment avez-vous évité les fuites de données ?**
Par plusieurs précautions :
- walk-forward chronologique, avec un gap de 10 jours entre la partie d'apprentissage et l'évaluation ;
- scaler ajusté sur la partie apprentissage de chaque fold uniquement ;
- early stopping sur les 10 % finaux de cette partie ;
- hyperparamètres choisis sans jamais toucher au test.

**Pourquoi le LSTM ne bat-il pas la marche aléatoire ?**
Parce qu'il n'y a rien à apprendre dans la moyenne : les sections 2 et 3 ont montré un bruit blanc. Le réseau produit des prévisions quasi constantes (écart-type 0,06 % contre 1,3 % pour les rendements réels) : il redécouvre la marche aléatoire.

**Pourquoi 3 seeds ?**
Changer la seed fait varier la prévision autant que son amplitude. La moyenne des 3 seeds réduit ce bruit d'initialisation, et la dispersion entre seeds montre que le « signal » appris n'est pas fiable.

**Et l'hybride ?**
L'ARIMA modélise la partie linéaire et le LSTM ses résidus. Il ne bat la marche aléatoire sur aucun fold, car les résidus n'ont pas de structure non linéaire dans la moyenne. La seule structure prévisible est la variance, qui relève du GARCH.

**Pourquoi la sélection par gain et pas par RMSE ?**
La fenêtre de 60 retire des observations, donc les RMSE bruts ne portent pas sur les mêmes échantillons. Le gain face à la prévision zéro, calculé sur les mêmes points, est comparable d'une configuration à l'autre.

## Prévision et évaluation (§6)

**Pourquoi 252 origines et pas une seule prévision ?**
Une prévision unique depuis la fin du train ne donne que 10 erreurs : c'est trop peu pour un test. Avec une prévision depuis chaque jour du test, on obtient environ 250 erreurs par horizon, ce qu'il faut pour Diebold-Mariano.

**Pourquoi ré-estimer tous les 20 jours seulement ?**
Pour limiter le temps de calcul : 13 estimations au lieu de 252. Entre deux estimations, les paramètres restent fixes, mais l'état du modèle (derniers rendements, variance GARCH) est mis à jour chaque jour. Chaque prévision utilise donc toute l'information disponible.

**Quel est le meilleur modèle ?**
Ça dépend de l'usage :
- pour le **niveau** du prix, la marche aléatoire : aucun modèle ne la bat significativement (Diebold-Mariano) ;
- pour le **risque**, le GJR-GARCH-t : c'est le seul dont les intervalles à 95 % ont une couverture correcte (94,8 %), et ils sont 16 % plus étroits.

**Le VAR(1) a un RMSE plus faible à 10 jours. Pourquoi ne pas le retenir ?**
Le gain est de 0,5 % et le test de Diebold-Mariano donne p = 0,69 : la différence n'est pas significative. De plus, le Granger robuste ne trouvait aucune prédictibilité sur le train.

**Pourquoi les intervalles à variance constante sont-ils trop larges ?**
Leur variance mélange tout le passé, crise de 2020 comprise. Le test (2025) est plus calme : le prix reste dans l'intervalle 98 % du temps au lieu de 95 %. Le GARCH s'adapte au régime du moment.

**Comment avez-vous vérifié votre test de Diebold-Mariano ?**
En le recalculant en R avec `forecast::dm.test` sur exactement les mêmes erreurs : les statistiques et les p-values coïncident.

**Pourquoi la MAPE ne se calcule-t-elle pas sur les rendements ?**
Les rendements sont souvent proches de zéro : diviser par eux fait exploser l'erreur relative. On calcule toutes les métriques sur le prix en dollars.

## Extensions (§7)

**Pourquoi une corrélation glissante plutôt qu'une corrélation unique ?**
Parce que le lien change dans le temps. La corrélation XOM – XLE est passée d'environ 0,82 avant 2020 à 0,93 après, et elle monte encore pendant les crises. Une valeur unique (0,91) mélange ces régimes.

**La bande de confiance est-elle exacte ?**
Non. La transformation de Fisher suppose des rendements indépendants et de variance constante, ce qui est faux avec des effets ARCH. Elle ne donne qu'un ordre de grandeur, d'environ ±0,05 pour une corrélation de 0,9 sur 60 jours.

**Le Brent aide-t-il à prévoir XOM ?**
Non. Il **explique** les mouvements du jour : XOM monte de 0,37 % quand le Brent monte de 1 %, et le R² passe de 0,4 % à 28 %. Mais le Brent de la **veille** n'a aucun effet (p = 0,86), et le VARX ne prévoit pas mieux sur le test. Pour exploiter le Brent du jour, il faudrait le prévoir, ce qui est aussi difficile que de prévoir XOM.

**Pourquoi ne pas avoir expliqué le creux de corrélation de mars 2022 ?**
La corrélation du 1ᵉʳ mars porte sur les 60 jours précédents, alors que la seule annonce propre à XOM ce jour-là (la sortie de Sakhalin-1) a été faite après la clôture. L'attribuer à cet événement serait une causalité inventée, l'erreur que l'on reproche justement au LLM.

**Qu'apporte le DCC-GARCH par rapport à la corrélation glissante ?**
La corrélation glissante constate que le lien varie. Le DCC le modélise : la corrélation de demain dépend du choc commun d'aujourd'hui (a = 0,026) et de la corrélation d'hier (b = 0,970). Elle ne dépend pas d'une fenêtre arbitraire de 60 jours, et elle réagit dès le lendemain d'un choc.

**Comment savez-vous que la corrélation n'est pas constante ?**
Par le test d'Engle et Sheppard (H₀ : corrélation constante), qui donne p < 0,0001, même sans 2020. On n'utilise pas un rapport de vraisemblance DCC contre CCC : sous H₀, b n'est pas identifié, donc la loi du χ² ne s'applique pas.

**Pourquoi rmgarch ne donne-t-il pas exactement les mêmes paramètres ?**
À cause de l'étape 1 : les GARCH univariés de R et de Python ne partent pas de la même variance initiale, comme au §3d. Sur les mêmes résidus standardisés, les deux étapes 2 donnent le même résultat.

## Usage de l'IA

**Avez-vous utilisé une IA ?**
Oui. Le code a été développé avec Claude Code, ce qui est déclaré dans le README et sera déclaré dans le rapport. La section 5 (LLM) est réalisée séparément, avec une interprétation personnelle rédigée **avant** de solliciter le LLM, comme l'exige le cahier.

**Pouvez-vous expliquer cette ligne de code ?**
Le jury peut pointer n'importe quel bloc : relire `src/` en s'appuyant sur les commentaires « pourquoi » de chaque bloc.
