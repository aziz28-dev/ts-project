# Prompt 2 — Vulgarisation des résultats pour un décideur (cahier §5, tâche 2)

**But.** Faire expliquer nos résultats réels à un décideur non statisticien. On vérifie ensuite, point par point, si le LLM déforme, simplifie trop ou invente quelque chose. La réponse est à mettre en annexe du rapport.

**Mode d'emploi.**
1. Ouvrir une **nouvelle** conversation, sans historique.
2. Coller le texte ci-dessous.
3. Enregistrer la réponse **intégrale** dans `llm/responses/02_vulgarisation_<modele>_<date>.md`, avec le nom du modèle et la date.

Toutes les valeurs viennent des tables `tab16` à `tab35` et du journal (`docs/journal.md`).

---

Voici les résultats d'une étude statistique sur l'action Exxon Mobil (XOM) et l'ETF de l'énergie XLE, en données journalières de 2016 à 2024. Rédige une explication d'une page, claire et sans jargon, pour un directeur financier qui n'est pas statisticien. Il veut savoir ce qu'il peut et ne peut pas en tirer.

**1. Prévision du rendement moyen**
- Le modèle retenu est la marche aléatoire, ARIMA(0,1,0) sur le log-prix : la meilleure prévision du rendement de demain est zéro. Le critère BIC choisit ce modèle.
- Le critère AIC propose un ARIMA(3,1,2). Ses racines AR (module 1,047) et MA (module 1,075) se compensent presque, et ses résidus standardisés restent autocorrélés (Ljung-Box p = 0,013). Il est donc écarté.
- Un SARIMA hebdomadaire (s = 5) a été testé et écarté : son coefficient saisonnier n'est pas significatif avec des erreurs-types robustes (p = 0,12).
- Validation sur 5 périodes successives (walk-forward), avec l'erreur quadratique moyenne des rendements journaliers en % (RMSE) :

  | Modèle | RMSE |
  | --- | --- |
  | Marche aléatoire | 1,8450 |
  | LSTM | 1,8472 |
  | GRU | 1,8482 |
  | ARIMA(3,1,2) | 1,8501 |
  | Hybride ARIMA + LSTM | 1,8527 |

  Aucun réseau de neurones ne bat la marche aléatoire. Leurs prévisions sont quasi constantes : écart-type de 0,06 % contre 1,3 % pour les rendements réels.

**2. Lien entre XOM et XLE**
- Les chocs des deux rendements ont une corrélation de 0,915 le même jour.
- Test de Granger de XLE vers XOM : p = 0,009 avec le test classique, mais p = 0,20 avec des erreurs-types robustes à l'hétéroscédasticité (HC3).
- Fonction de réponse impulsionnelle : un choc d'un écart-type sur XLE fait varier XOM de +1,63 % le jour même, de −0,08 % le lendemain, puis l'effet est nul.
- Décomposition de la variance (FEVD) : la part de XLE dans la variance de prévision de XOM vaut 83,7 % si XLE est placé en premier dans l'ordre de Cholesky, et 0,3 % si XOM est placé en premier.
- Cointégration des log-prix : Engle-Granger p = 0,037 ; Johansen, statistique de trace 14,73 pour des valeurs critiques de 13,43 à 10 % et 15,49 à 5 %. La relation n'est significative dans aucune des deux sous-périodes 2016-2019 et 2021-2024.
- Modèle à correction d'erreur (VECM) : la vitesse d'ajustement n'est significative ni pour XOM (p = 0,93) ni pour XLE (p = 0,16). La demi-vie d'un écart à l'équilibre est de 62,6 jours de bourse.

**3. Volatilité (risque)**
- Le modèle retenu est un GJR-GARCH(1,1) avec loi de Student : ω = 0,0094, α = 0,043, γ = 0,042 (p = 0,004), β = 0,935, ν = 7,47 degrés de liberté.
- La loi de Student améliore la log-vraisemblance d'environ 37 points par rapport à la loi normale.
- Persistance (α + β + γ/2) : 0,9993 sur 2016-2024 (demi-vie de 1 015 jours), mais 0,893 sur 2016-2019 et 0,996 sur 2021-2024.
- Pics de volatilité annualisée estimée : 107 % le 2020-03-19, 47 % le 2022-03-16 et 52 % le 2022-06-24.
- Après le modèle, l'effet ARCH résiduel passe de 441 à 14 (p = 0,016).

Contraintes pour ta réponse :
- n'utilise aucun chiffre qui ne figure pas ci-dessus ;
- signale clairement ce que ces résultats ne permettent **pas** de conclure.
