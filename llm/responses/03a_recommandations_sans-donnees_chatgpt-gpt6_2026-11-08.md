# Réponse au prompt 3 — Essai sans données (à refaire après la phase 6)

- **Modèle :** ChatGPT, agent GPT-6 (nom donné par l'étudiant)
- **Date :** 2026-11-08
- **Prompt :** `llm/prompts/03_recommandations.md`, envoyé **avec les champs « [À REMPLIR] » encore vides**, c'est-à-dire avant la phase 6. Le LLM n'avait aucune prévision ni aucun intervalle.
- **Statut :** essai conservé à titre documentaire. La version qui fera foi sera `03_recommandations_<modele>_<date>.md`, envoyée avec les résultats de la phase 6.
- **Réponse :** intégrale, copiée sans retouche ci-dessous.

---

Analyse et recommandations d'investissement simulées – Exxon Mobil (XOM)
Statut : exercice académique – simulation uniquement

Les données nécessaires à l'analyse ne sont pas encore renseignées. Les prévisions, les intervalles de confiance, la volatilité et les résultats des tests statistiques sont remplacés par des champs à compléter.

Il serait incorrect de formuler une recommandation d'achat ou de vente sans connaître ces résultats. Voici néanmoins la grille d'analyse et les recommandations conditionnelles à appliquer.
1. Interprétation des prévisions
Le modèle ARIMA(0,1,0) + GJR-GARCH-t combine deux approches :
- ARIMA(0,1,0) : sert de référence pour prévoir l'évolution du prix à partir de la dernière observation, sans supposer une tendance systématique.
- GJR-GARCH-t : estime la volatilité future en tenant compte de l'évolution passée des variations de prix et de la possibilité que les mauvaises nouvelles aient un effet différent des bonnes nouvelles.
Les prévisions à 1, 5 et 10 jours donnent une indication de l'évolution possible du cours, tandis que les intervalles à 95 % permettent d'apprécier l'incertitude associée.

Il faut toutefois rappeler qu'un intervalle à 95 % n'est pas une garantie que le prix restera dans cette fourchette.
2. Recommandations d'investissement simulées
Scénario 1 – Achat à court terme
Condition : si la prévision à 1 jour indique une évolution favorable et que l'incertitude reste relativement limitée.

Une position acheteuse pourrait être envisagée dans le cadre de cette simulation, avec un horizon très court.

Limites et risques :
- Le modèle ne garantit pas que le mouvement prévu se réalisera.
- Les coûts de transaction peuvent réduire, voire annuler, un éventuel gain.
- L'horizon d'un jour est particulièrement sensible aux événements imprévus.
- L'intervalle à 95 % rappelle que plusieurs évolutions restent possibles.
- Un changement brutal des conditions du marché peut rendre la prévision rapidement obsolète.
Scénario 2 – Position à moyen terme
Condition : si les prévisions à 5 jours confirment une évolution favorable et que la volatilité prévue reste maîtrisée.

Une position acheteuse pourrait être étudiée dans cette simulation, sous réserve de la cohérence des résultats statistiques.

Limites et risques :
- L'incertitude augmente généralement avec l'horizon de prévision.
- Les erreurs de prévision peuvent s'accumuler.
- Les frais de transaction et les éventuels coûts de détention doivent être pris en compte.
- Le modèle peut mal réagir à un changement de régime économique ou financier.
Scénario 3 – Prudence à horizon de 10 jours
Condition : si les intervalles de prévision à 10 jours sont particulièrement larges ou si la volatilité prévue est élevée.

Dans ce cas, conserver une position neutre dans la simulation ou attendre de nouvelles observations serait plus prudent qu'une décision d'achat fondée uniquement sur la prévision ponctuelle.

Limites et risques :
- Une prévision à 10 jours comporte davantage d'incertitude.
- Les intervalles à 95 % ne couvrent pas nécessairement les événements extrêmes.
- Les changements de politique monétaire, les tensions géopolitiques et les chocs pétroliers peuvent modifier les conditions du marché.
- Le modèle repose sur des relations statistiques historiques qui peuvent ne plus être représentatives.
3. Évaluation de la qualité des prévisions
Les indicateurs RMSE, MAE et le test de Diebold-Mariano permettent d'évaluer la qualité des prévisions.
Indicateur	Interprétation
RMSE	Mesure l'importance des erreurs, en pénalisant davantage les grandes erreurs.
MAE	Mesure l'erreur absolue moyenne en dollars.
Diebold-Mariano	Permet de comparer statistiquement les performances prédictives de deux modèles.

La comparaison avec la marche aléatoire est particulièrement importante : si le modèle ARIMA-GARCH ne fait pas significativement mieux que cette référence, il n'existe pas de justification statistique suffisante pour lui accorder un avantage prédictif.
4. Ce que les modèles ne peuvent pas prévoir
Même avec de bonnes performances historiques, ARIMA et GJR-GARCH ne peuvent pas prévoir de manière fiable :
- Les décisions inattendues de l'OPEP et de l'OPEP+.
- Les guerres et les crises géopolitiques.
- Les catastrophes naturelles et les incidents majeurs dans les installations pétrolières.
- Les annonces financières inattendues d'Exxon Mobil.
- Les changements réglementaires et fiscaux.
- Les mouvements imprévus des taux d'intérêt et des marchés financiers.
- Les changements structurels de l'offre et de la demande de pétrole.
Ces événements peuvent provoquer des variations importantes que les données historiques ne permettent pas nécessairement d'anticiper.
5. Conclusion générale
Dans cet exercice, les modèles ARIMA(0,1,0) et GJR-GARCH-t doivent être considérés comme des outils d'aide à l'analyse statistique et non comme des systèmes autonomes de décision d'investissement.

La décision simulée doit tenir compte simultanément de la direction des prévisions, de leur incertitude, de la volatilité anticipée et de la comparaison avec la marche aléatoire.

Une prévision favorable ne constitue pas, à elle seule, un signal d'achat. De même, une prévision défavorable ne constitue pas automatiquement un signal de vente.
