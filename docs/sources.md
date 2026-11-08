# Sources des faits externes cités

Chaque fait qui ne vient pas de nos propres calculs est listé ici avec sa source, consultée le 2026-11-08. Les rendements cités viennent de nos données (`data/raw/`, Yahoo Finance), recoupées avec la presse quand c'est possible.

## Événements associés aux rendements extrêmes et aux pics de volatilité (§2.1, §2.5, §3.3)

| Date | Événement | Nos données (rendement simple du jour) | Sources |
| --- | --- | --- | --- |
| 2020-03-09 | Échec des négociations OPEP+ ; l'Arabie saoudite lance une guerre des prix contre la Russie, en pleine propagation du COVID-19. Le Brent connaît sa plus forte baisse en une séance depuis janvier 1991 (première guerre du Golfe). | Brent −24,1 % ; XLE −20,1 % ; XOM −12,2 %. La presse rapporte un Brent en baisse de 24 % à la clôture, ce qui recoupe exactement notre série `BZ=F`. | [KVIA / CNN Business, 2020-03-09](https://kvia.com/news/business-technology/2020/03/09/oil-crashes-by-most-since-1991-as-saudi-arabia-launches-price-war/) ; [Offshore Engineer, « Oil Suffers Rout After Saudi Arabia Fires First Shot of Price War »](https://www.oedigital.com/amp/news/476377-oil-suffers-rout-after-saudi-arabia-fires-first-shot-of-price-war) |
| 2020-11-09 | Pfizer et BioNTech annoncent que leur vaccin contre le COVID-19 est efficace à plus de 90 % (résultats préliminaires de phase 3) ; forte hausse des valeurs énergétiques et du pétrole. | XLE +14,3 % ; XOM +12,7 % ; Brent +7,5 %. Les ordres de grandeur rapportés par la presse diffèrent un peu selon la mesure retenue (cours intrajournalier ou de clôture). | [PBS NewsHour, 2020-11-09](https://www.pbs.org/newshour/world/global-markets-rocket-higher-amid-vaccine-news-and-u-s-election) ; [Boston Globe, 2020-11-09](https://www.bostonglobe.com/2020/11/09/business/stocks-pounded-by-pandemic-rally-vaccine-test-results) |
| Juin 2022 | Forte baisse des valeurs énergétiques : le secteur de l'énergie du S&P 500 perd environ 16,8 % en juin 2022, à cause de la chute des cours du pétrole et des craintes de récession. | Pic de volatilité conditionnelle de XOM (GJR) : 52,2 % le 2022-06-24, le plus haut de 2022 (§3.3.4). | [S&P Global Market Intelligence, juillet 2022](https://www.spglobal.com/market-intelligence/en/news-insights/articles/2022/7/energy-stocks-plummet-in-june-as-recession-fears-drag-oil-prices-71046468) |
| 2025-04-02 → 2025-04-10 | Annonce des droits de douane « réciproques » américains (« Liberation Day », 2 avril après la clôture), chute des marchés les 3 et 4 avril, suspension de 90 jours pour la plupart des pays annoncée le 9 avril (forte hausse), nouvelle baisse le 10 avril. | XLE : −7,9 % (3 avril), −9,2 % (4 avril), +7,7 % (9 avril), −6,5 % (10 avril). XOM : −5,3 %, −7,2 %, +5,0 %, −5,6 %. | [Wikipedia, « 2025 stock market crash »](https://en.wikipedia.org/wiki/2025_stock_market_crash) ; [Washington Times, 2025-04-09](https://www.washingtontimes.com/news/2025/apr/9/trump-pauses-reciprocal-tariffs-14-hours-retains-10-baseline/) |

## Composition de l'ETF XLE (§3.2.4)

- **ExxonMobil représente 24,47 % de XLE**, ce qui en fait le premier composant devant Chevron (18,78 %), d'après le tableau des principales positions mis à jour le 2026-11-05 : [StockAnalysis, XLE holdings](https://stockanalysis.com/etf/xle/holdings/).
- D'autres relevés de 2026 donnent entre 22 % et 23 %. **La pondération varie dans le temps**, et sa valeur historique sur la période étudiée (2016–2024) n'a pas été vérifiée. Pour le rapport, on écrit donc « environ un quart de l'ETF en 2026 », sans l'attribuer à toute la période.
- Source officielle à privilégier pour une valeur datée : la page des positions de l'émetteur, State Street (SPDR).

## Note sur la fiabilité

Wikipedia sert ici de chronologie de synthèse ; les dates qu'elle donne pour avril 2025 (2, 3–4, 9 et 10 avril) sont cohérentes avec les jours extrêmes que notre propre détection a signalés de façon indépendante (§2.5).
