# Réponse au prompt 3 — Recommandations d'investissement simulées

- **Modèle :** ChatGPT, agent GPT-6 (nom donné par l'étudiant)
- **Date :** 2026-11-08
- **Prompt :** `llm/prompts/03_recommandations.md`, version remplie avec les résultats de la phase 6, envoyée dans une nouvelle conversation
- **Réponse :** intégrale, copiée sans retouche ci-dessous

---

Analyse et recommandations d'investissement simulées – Exxon Mobil (XOM)
Exercice académique – Novembre 2026
 Aucun conseil financier réel

1. Synthèse de l'analyse
Les résultats statistiques conduisent à une conclusion importante : le prix de l'action Exxon Mobil est difficile à prévoir à court terme, et les modèles étudiés ne démontrent pas de capacité significative à anticiper son évolution mieux qu'une simple marche aléatoire.

Le modèle retenu, ARIMA(0,1,0) associé à un GJR-GARCH(1,1) avec loi de Student, prévoit un prix constant de 117,97 $ aux trois horizons étudiés.

Cela ne signifie pas que le cours restera effectivement à ce niveau. Cela signifie que le modèle ne dispose pas d'informations statistiques suffisamment solides pour prévoir une hausse ou une baisse moyenne.

En revanche, le modèle GJR-GARCH-t apporte une information complémentaire sur le risque : il estime l'ampleur potentielle des fluctuations du cours et adapte les intervalles de prévision à l'évolution de la volatilité.
2. Recommandations d'investissement simulées
Recommandation 1 – Conserver l'action (HOLD)
Recommandation privilégiée
Justification :

La marche aléatoire constitue une référence difficile à dépasser. Aucun modèle testé n'a démontré une supériorité statistiquement significative sur cette référence.

Par conséquent, les résultats ne fournissent pas de justification statistique solide pour vendre immédiatement l'action ou renforcer une position dans l'espoir d'une hausse à court terme.

Pour un investisseur qui détient déjà XOM, une stratégie de conservation peut donc être retenue dans cette simulation.

Limites et risques :
- Risque de modèle : la marche aléatoire suppose implicitement que les variations futures ne peuvent pas être anticipées à partir des informations historiques exploitées.
- Incertitude : l'intervalle à 95 % à 10 jours s'étend de 109,87 $ à 126,37 $, ce qui représente une dispersion importante autour de la prévision centrale.
- Changement de régime : une évolution brutale du marché pétrolier ou de l'environnement économique pourrait rendre les paramètres historiques moins représentatifs.
- Coûts de transaction : conserver une position évite de multiplier les achats et les ventes, mais ne supprime pas les coûts de détention éventuels.
Recommandation 2 – Éviter les achats spéculatifs à très court terme (BUY : prudence)
Justification :

Le modèle ne prévoit aucune progression du prix à 1, 5 ou 10 jours.

De plus, les résultats du test de Diebold-Mariano montrent qu'aucun modèle étudié ne surpasse significativement la marche aléatoire.

Il serait donc difficile de justifier un achat spéculatif à court terme sur la seule base de ces prévisions.

Un achat pourrait éventuellement être envisagé dans une stratégie de détention plus longue, mais il nécessiterait d'autres éléments d'analyse, notamment fondamentaux.

Limites et risques :
- Les prévisions ne garantissent pas que le cours restera proche de 117,97 $.
- Les intervalles à 95 % ne couvrent pas tous les scénarios possibles : des mouvements plus importants restent envisageables.
- Les frais de transaction peuvent réduire la rentabilité d'une stratégie d'achats et de ventes fréquents.
- Le modèle ne tient pas compte des changements soudains de comportement des investisseurs.
Recommandation 3 – Utiliser le GJR-GARCH-t pour gérer le risque
Intérêt statistique démontré
Justification :

Le GJR-GARCH-t présente de meilleurs résultats pour la modélisation de la volatilité que le modèle à variance constante.

Deux observations soutiennent ce choix :
- Sa couverture empirique des intervalles à 95 % est de 94,8 %, avec une valeur p de 0,885 au test de couverture.
- Sa perte QLIKE est de 1,732, contre 1,844 pour le modèle à variance constante.
Cela indique que le GJR-GARCH-t constitue un outil intéressant pour évaluer le risque associé à l'action.

Il faut néanmoins rester prudent : le test de Diebold-Mariano donne une valeur p de 0,075 pour la comparaison des prévisions de variance. L'amélioration observée n'est donc pas statistiquement significative au seuil habituel de 5 %.

Limites et risques :
- Le modèle estime la volatilité, mais ne prédit pas avec certitude la direction du cours.
- Les intervalles reposent sur des hypothèses statistiques qui peuvent devenir moins adaptées lors de crises.
- La loi de Student permet de mieux représenter certaines fluctuations extrêmes, mais ne garantit pas la prise en compte de tous les événements exceptionnels.
- Une mauvaise estimation de la volatilité peut conduire à une évaluation insuffisante du risque réel.
Recommandation 4 – Ne pas utiliser les modèles complexes comme argument principal d'achat ou de vente
Justification :

Les modèles LSTM, GRU et hybride ARIMA-LSTM n'ont pas apporté d'amélioration significative par rapport à la marche aléatoire.

À 10 jours, ils présentent même des performances statistiquement moins bonnes :
Modèle	Résultat du test DM
LSTM	p = 0,011
GRU	p inférieur à 0,001
Hybride ARIMA-LSTM	p = 0,008

Ces résultats montrent qu'une architecture plus complexe ne garantit pas une meilleure prévision financière.

Il serait donc préférable de privilégier un modèle simple et interprétable plutôt que de choisir automatiquement le modèle le plus sophistiqué.

Limites et risques :
- Les performances observées en 2025 ne garantissent pas les performances futures.
- Les modèles complexes peuvent être sensibles aux données utilisées pour leur apprentissage.
- Un changement de régime économique peut dégrader leurs performances.
- Les coûts de transaction et les contraintes d'exécution ne sont pas intégrés dans les erreurs statistiques présentées.

3. Ce que les modèles ne peuvent pas prévoir
Il est essentiel de distinguer la prévision statistique de la réalité économique et financière.

Les modèles étudiés ne permettent pas de prévoir avec certitude :
Élément	Pourquoi ?
Les décisions de l'OPEP	Elles dépendent de décisions économiques et politiques.
Les conflits géopolitiques	Leur apparition et leurs conséquences sont difficiles à anticiper statistiquement.
Les variations futures du prix du pétrole	Elles dépendent de l'offre, de la demande et des événements internationaux.
Les résultats financiers d'Exxon Mobil	Les modèles de prix étudiés n'intègrent pas directement les futurs résultats de l'entreprise.
Les annonces de dividendes	Elles dépendent des décisions de l'entreprise.
Les décisions des banques centrales	Elles peuvent modifier les conditions financières et les comportements des investisseurs.
Les crises financières	Leur déclenchement et leur ampleur ne sont pas prévisibles avec fiabilité par ces modèles.
Les réactions des investisseurs	Les comportements collectifs peuvent évoluer rapidement.

En particulier, un intervalle de confiance à 95 % ne signifie pas qu'il existe une garantie de 95 % que le prix futur restera dans cet intervalle. Il s'agit d'une mesure statistique conditionnelle aux hypothèses du modèle et à sa méthode de construction.
4. Tableau récapitulatif des décisions simulées
Stratégie	Recommandation	Justification
Investisseur détenant déjà XOM	HOLD	Absence de signal statistique significatif de vente ou d'achat.
Nouvel investisseur à court terme	Prudence	Absence d'avantage prédictif démontré.
Gestion du risque	Utiliser GJR-GARCH-t	Meilleure couverture empirique et meilleure perte QLIKE observées.
Choix du modèle	Privilégier la marche aléatoire	Simplicité et performances compétitives.
Modèles Deep Learning	Ne pas les privilégier	Performances inférieures à 10 jours.

5. Conclusion générale
L'étude de l'action Exxon Mobil montre que la prévision des prix financiers demeure un exercice particulièrement incertain, même avec des modèles statistiques et des architectures d'intelligence artificielle avancées.

La marche aléatoire constitue ici une référence pertinente, puisqu'aucun des modèles concurrents ne démontre une amélioration statistiquement significative de la prévision du prix.

Le GJR-GARCH-t présente néanmoins un intérêt complémentaire pour la mesure de la volatilité et l'évaluation des risques.

La recommandation simulée finale est donc de conserver une position existante sur XOM, d'éviter les décisions spéculatives fondées uniquement sur les prévisions à court terme et d'utiliser le GJR-GARCH-t comme outil complémentaire de gestion du risque.

Cette recommandation reste conditionnelle : elle ne repose ni sur une valorisation fondamentale de l'entreprise, ni sur une analyse de ses dividendes, de sa situation financière ou des perspectives du secteur énergétique.

Enseignement principal de l'étude : en finance, un modèle performant pour mesurer le risque n'est pas nécessairement performant pour prévoir le prix. Et un modèle complexe n'est pas automatiquement meilleur qu'un modèle simple.
