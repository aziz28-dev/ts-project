# Interprétation personnelle des résultats

**Auteurs :** Aziz Bellaaj, Mohamed Yassine Khiari
**Date de rédaction (avant tout prompt LLM) :** 2026-11-08

> Cette page est rédigée par l'étudiant, **avant** d'interroger le LLM. Elle sert de référence pour la comparaison humain / LLM (cahier §5). Environ une page. Pour chaque point, suivre la méthode : hypothèse nulle → statistique et p-value → décision → sens concret → conséquence.

## 1. Stationnarité et ordre de différenciation

H₀ de l'ADF : racine unitaire (série non stationnaire). H₀ du KPSS : série stationnaire. Les deux hypothèses sont opposées, donc on conclut quand les deux tests concordent.

Log-prix : l'ADF ne rejette pas H₀ (p = 0,76) et le KPSS rejette H₀ (p < 0,01). Les deux tests concordent : le log-prix n'est pas stationnaire.

Rendements : l'ADF rejette H₀ (p < 0,001) et le KPSS ne rejette pas H₀ (p > 0,10). Les deux tests concordent : les rendements sont stationnaires.

Le log-prix devient stationnaire après 1 différenciation, donc d = 1. On modélise donc les rendements et non les prix.

## 2. Dynamique de la moyenne (ARIMA, SARIMA)

Je retiens l'ARIMA(0,1,0) car le BIC, qui pénalise davantage la complexité, le choisit, et car l'ARIMA(3,1,2) proposé par l'AIC n'est pas meilleur : ses résidus restent autocorrélés (p = 0,013).

Le coefficient saisonnier a p = 0,12 > 0,05 : on ne rejette pas H₀, donc on écarte le SARIMA.

ARCH-LM sur les résidus de la marche aléatoire : 441, p ≈ 0 < 0,05 : on rejette H₀. La variance n'est pas constante : les grosses variations arrivent en grappes, par exemple en 2020. Il faut donc ajouter un modèle GARCH.

## 3. Lien entre XOM et XLE (VAR, Granger, IRF/FEVD, cointégration)

Granger de XLE vers XOM : avec le test robuste, p = 0,20 > 0,05 : on ne rejette pas H₀. Le passé de XLE n'améliore pas la prévision de XOM.

IRF : XOM réagit le jour même à un choc sur XLE (+1,63 %). Il n'y a pas d'effet retardé, ce qui est cohérent avec Granger.

FEVD : la part de XLE vaut 84 % ou 0,3 % selon l'ordre. On ne peut pas dire que XLE entraîne XOM, car le résultat dépend de l'ordre des variables. On ne peut donc pas dire qui entraîne qui.

La cointégration est fragile : elle n'est retenue qu'à 10 % et disparaît dans les sous-périodes.

## 4. Volatilité (GARCH)

H₀ : γ = 0. Avec p = 0,004, on rejette H₀. Une baisse augmente la volatilité de α + γ = 0,085, contre α = 0,043 pour une hausse. Un investisseur doit donc s'attendre à plus de risque après une baisse. Le GARCH prévoit l'amplitude des variations, pas leur sens.

La persistance de 0,999 est gonflée par la rupture de 2020. Le GARCH confond un changement de niveau de la volatilité avec une forte persistance. Sur 2016–2019, elle n'est que de 0,893.

## 5. Deep learning (LSTM, GRU, hybride)

Le meilleur modèle est la marche aléatoire (RMSE 1,8450). Le LSTM (1,8472) ne bat pas la marche aléatoire. Ce n'est pas un échec, car les rendements sont un bruit blanc en moyenne : il n'y a rien à prévoir.

## 6. Ce que ces résultats ne permettent pas de conclure

On ne peut pas dire que XLE « cause » XOM. Le GARCH prévoit le risque, pas le sens du prix. Les résultats peuvent changer si le marché change de régime, comme en 2020.
