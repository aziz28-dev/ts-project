# Section 5 — IA générative et LLM (4 points)

Ce dossier documente l'usage critique d'un LLM, comme le demande le cahier des charges (§5).

## Ordre à respecter

| Étape | Fichier | Qui | Statut |
| --- | --- | --- | --- |
| 0. Interprétation personnelle, datée, écrite **avant** tout prompt | `interpretation_personnelle.md` | Étudiant | Fait (2026-11-08) |
| 1. Hypothèses de modèles | `prompts/01_hypotheses.md` → `responses/` | Étudiant (LLM externe) | Prompt prêt |
| 2. Vulgarisation pour un décideur | `prompts/02_vulgarisation.md` → `responses/` | Étudiant (LLM externe) | Prompt prêt |
| 3. Recommandations simulées | `prompts/03_recommandations.md` → `responses/` | Étudiant (LLM externe) | Après la phase 6 |
| 4. Comparaison humain / LLM et erreurs du LLM | `comparaison.md` | Étudiant | À faire après les réponses |

## Règles

- **Nouvelle conversation** pour chaque prompt, sans historique, pour que le LLM ne voie pas nos conclusions.
- **Réponse intégrale** copiée sans retouche, avec le nom exact du modèle (par exemple « ChatGPT, GPT-x ») et la date.
- **Nommage** des réponses : `responses/NN_tache_<modele>_<AAAA-MM-JJ>.md`.
- **Transparence** : le code du projet a été développé avec l'aide de Claude Code. Le LLM de cette section est utilisé à part, comme outil d'analyse dont on évalue la fiabilité.

## Grille de détection des erreurs du LLM

À appliquer à chaque réponse, en citant le passage concerné.

| # | Erreur à chercher | Bonne référence dans le projet |
| --- | --- | --- |
| 1 | p-value ou statistique citée qui ne figure pas dans nos sorties | tables `outputs/tables/` |
| 2 | Granger présenté comme une causalité | §3.2 : prédictibilité incrémentale, et non robuste ici (HC3 p = 0,20) |
| 3 | GARCH présenté comme prévoyant le **sens** du prix | §3.3 : il prévoit l'amplitude, pas la direction |
| 4 | FEVD lue comme « XLE entraîne XOM » | §3.2.6 : 83,7 % ou 0,3 % selon l'ordre de Cholesky |
| 5 | Lien causal inventé entre un événement et la série | `docs/sources.md` |
| 6 | Confiance excessive : oubli du risque de modèle et des coûts de transaction | §4 et §6 : aucun modèle ne bat la marche aléatoire |
| 7 | Persistance GARCH prise à la lettre (« un choc dure 4 ans ») | §3.3 : persistance gonflée par 2020 (0,893 sur 2016-2019) |
| 8 | Conseil d'utiliser un LSTM sur les prix bruts, ou un k-fold classique | §4 : rendements et walk-forward |
| 9 | Confusion des hypothèses nulles de l'ADF et du KPSS | §2.6 : ADF H₀ = racine unitaire, KPSS H₀ = stationnarité |

## Modèle de tableau pour `comparaison.md`

| Thème | Mon interprétation | LLM | Convergence / divergence / erreur | Justification (avec la référence) |
| --- | --- | --- | --- | --- |
| Stationnarité | | | | |
| Choix du modèle de moyenne | | | | |
| Lien XOM / XLE | | | | |
| Volatilité | | | | |
| Deep learning | | | | |
| Recommandations | | | | |
