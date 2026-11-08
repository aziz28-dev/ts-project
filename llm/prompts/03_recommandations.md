# Prompt 3 — Recommandations d'investissement simulées (cahier §5, tâche 3)

**Statut : à compléter après la phase 6.** Ce prompt a besoin des prévisions sur le test (h = 1 à 10) et de leurs intervalles de confiance, en dollars. Ces valeurs seront produites par la phase 6 (évaluation multi-origines). Ne pas l'envoyer au LLM avant.

**Mode d'emploi, une fois les valeurs remplies.**
1. Ouvrir une **nouvelle** conversation.
2. Coller le texte ci-dessous.
3. Enregistrer la réponse intégrale dans `llm/responses/03_recommandations_<modele>_<date>.md`.

---

Tu es analyste. À partir des prévisions ci-dessous sur l'action Exxon Mobil (XOM), formule des recommandations d'investissement **simulées** (exercice académique, pas un conseil réel).

[À REMPLIR après la phase 6 :
- dernier prix observé ;
- prévision à 1, 5 et 10 jours avec intervalles à 95 % (ARIMA(0,1,0) + GJR-GARCH-t) ;
- volatilité prévue ;
- tableau des erreurs RMSE et MAE en dollars sur le test, et résultat du test de Diebold-Mariano contre la marche aléatoire.]

Exigences :
1. Pour chaque recommandation, **formule toi-même** les limites et les risques : risque de modèle, coûts de transaction, horizon, incertitude des intervalles, changement de régime.
2. N'utilise aucun chiffre absent de ce message.
3. Indique ce que ces modèles **ne peuvent pas** prévoir.
