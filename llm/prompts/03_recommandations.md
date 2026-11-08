# Prompt 3 — Recommandations d'investissement simulées (cahier §5, tâche 3)

**But.** Faire formuler au LLM des recommandations simulées à partir de nos prévisions réelles. Il doit formuler lui-même les limites et les risques. On complète ensuite ces limites de façon critique dans `llm/comparaison.md`.

**Statut.** Prompt rempli avec les résultats de la phase 6. Une première version avait été envoyée sans données : `responses/03a_…`.

**Mode d'emploi.**
1. Ouvrir une **nouvelle** conversation.
2. Coller le texte situé sous la ligne `---`.
3. Enregistrer la réponse intégrale dans `llm/responses/03_recommandations_<modele>_<date>.md`.

**Sources des valeurs.**
- Prévision depuis le 2025-12-31 : `src/evaluation.py`, fonction `forecast_from_last` (GJR-GARCH-t ré-estimé sur tout l'échantillon, 20 000 trajectoires simulées).
- Évaluation sur le test : tableaux tab36 à tab39 (§6 du notebook).

---

Tu es analyste. À partir des résultats ci-dessous sur l'action Exxon Mobil (XOM), formule des recommandations d'investissement **simulées** : c'est un exercice académique, pas un conseil réel.

**1. Modèle et prévision depuis le dernier jour observé**

Le modèle retenu est une marche aléatoire pour le prix, ARIMA(0,1,0) sur le log-prix, combinée à un GJR-GARCH(1,1) avec loi de Student pour la volatilité. Il est estimé sur les données journalières du 2016-01-04 au 2025-12-31.

Dernier prix observé, le 2025-12-31 : **117,97 $**.

| Horizon | Prévision du prix | Intervalle à 95 % | Volatilité prévue (annualisée) |
| --- | --- | --- | --- |
| 1 jour | 117,97 $ | [115,29 ; 120,65] $ | 17,8 % |
| 5 jours | 117,97 $ | [112,17 ; 123,96] $ | 18,1 % |
| 10 jours | 117,97 $ | [109,87 ; 126,37] $ | 18,4 % |

**2. Évaluation sur l'année 2025 (période de test non utilisée pour estimer les modèles)**

Les prévisions ont été faites depuis chacun des 252 jours de 2025. Les modèles classiques ont été ré-estimés tous les 20 jours. Sur cette période, XOM est passée de 100,69 $ à 117,97 $.

Erreurs de prévision du prix, en dollars :

| Modèle | RMSE h = 1 | MAE h = 1 | RMSE h = 5 | MAE h = 5 | RMSE h = 10 | MAE h = 10 |
| --- | --- | --- | --- | --- | --- | --- |
| Marche aléatoire | 1,560 | 1,170 | 3,617 | 2,762 | 4,650 | 3,487 |
| VAR(1) XOM-XLE | 1,561 | 1,166 | 3,616 | 2,741 | 4,628 | 3,465 |
| VECM XOM-XLE | 1,560 | 1,170 | 3,618 | 2,763 | 4,652 | 3,489 |
| ARIMA(3,1,2) | 1,569 | 1,175 | 3,620 | 2,764 | 4,657 | 3,495 |
| LSTM | 1,558 | 1,171 | 3,672 | 2,810 | 4,867 | 3,668 |
| GRU | 1,558 | 1,170 | 3,630 | 2,771 | 4,770 | 3,590 |
| Hybride ARIMA + LSTM | 1,569 | 1,175 | 3,670 | 2,807 | 4,866 | 3,666 |

Test de Diebold-Mariano contre la marche aléatoire (perte quadratique, correction de Harvey-Leybourne-Newbold) :
- aucun modèle n'est significativement meilleur que la marche aléatoire, à aucun horizon de 1 à 10 jours ;
- le VAR(1) à 10 jours a p = 0,69 ;
- sont significativement moins bons à 10 jours : ARIMA(3,1,2) (p < 0,001), LSTM (p = 0,011), GRU (p < 0,001) et hybride (p = 0,008).

Intervalles à 95 % à 1 jour sur 2025 :
- modèles à variance constante : le prix réalisé est dans l'intervalle 98,0 % du temps (test binomial de couverture à 95 % : p = 0,028), largeur moyenne 7,46 $ ;
- GJR-GARCH-t : 94,8 % du temps (p = 0,885), largeur moyenne 6,27 $.

Prévision de la variance à 1 jour (perte QLIKE, plus faible = meilleure) : GJR-GARCH-t 1,732 ; variance constante 1,844. Diebold-Mariano : p = 0,075.

**Exigences pour ta réponse**
1. Pour chaque recommandation, **formule toi-même** les limites et les risques : risque de modèle, coûts de transaction, horizon, incertitude des intervalles, changement de régime.
2. N'utilise aucun chiffre absent de ce message.
3. Indique ce que ces modèles **ne peuvent pas** prévoir.
