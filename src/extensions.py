"""Section 7 : extensions (bloc D du barème).

7.1 Corrélation glissante sur 60 jours entre les rendements de XOM et de XLE (et avec le Brent),
    annotée avec les événements documentés dans `docs/sources.md`.
7.2 VARX : VAR(1) des rendements de XOM et XLE avec le rendement du Brent en variable exogène.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats

BRENT = "BZ=F_ret"

# Événements annotés : uniquement ceux dont la date et le contenu sont sourcés dans docs/sources.md.
EVENTS = {
    "2020-03-09": "guerre des prix OPEP+ et COVID-19",
    "2020-04-21": "effondrement du pétrole (WTI négatif le 20 avril)",
    "2020-11-09": "annonce du vaccin Pfizer-BioNTech",
    "2022-02-24": "invasion de l'Ukraine",
    "2022-06-24": "chute de l'énergie, craintes de récession",
    "2025-04-03": "droits de douane américains",
}


# ---------------------------------------------------------------------------
# 7.1 Corrélation glissante
# ---------------------------------------------------------------------------

def rolling_corr(panel: pd.DataFrame, a: str = "XOM_ret", b: str = "XLE_ret", window: int = 60) -> pd.Series:
    """Corrélation de Pearson sur les `window` derniers jours (valeur en t : jours t − window + 1 … t)."""
    return panel[a].rolling(window, min_periods=window).corr(panel[b])


def fisher_band(rho: pd.Series, n: int, level: float = 0.95):
    """Bande de confiance approximative par la transformation de Fisher, z = atanh(ρ), d'écart-type 1/√(n − 3).

    Approximation : elle suppose des observations indépendantes et de variance constante,
    ce que les rendements ne sont pas (effets ARCH). La bande donne un ordre de grandeur
    de l'incertitude d'une corrélation estimée sur 60 jours, pas un test exact.
    """
    q = stats.norm.ppf(0.5 + level / 2) / np.sqrt(n - 3)
    z = np.arctanh(rho.clip(-0.999999, 0.999999))
    return np.tanh(z - q), np.tanh(z + q)


def corr_summary(rc: dict, periods: dict) -> pd.DataFrame:
    """Moyenne, minimum et maximum (avec leur date) de chaque corrélation glissante, par sous-période."""
    rows = []
    for name, s in rc.items():
        for per, (start, end) in periods.items():
            x = s.loc[start:end].dropna()
            rows.append({"paire": name, "période": per, "moyenne": x.mean(), "minimum": x.min(),
                         "date du minimum": x.idxmin().date(), "maximum": x.max(), "date du maximum": x.idxmax().date(),
                         "jours": len(x)})
    return pd.DataFrame(rows).set_index(["paire", "période"])


def static_corr(panel: pd.DataFrame, pairs: dict, periods: dict) -> pd.DataFrame:
    """Corrélation statique (sur toute la sous-période), pour situer les corrélations glissantes."""
    return pd.DataFrame({per: {name: panel.loc[s:e, [a, b]].dropna().corr().iloc[0, 1] for name, (a, b) in pairs.items()}
                         for per, (s, e) in periods.items()})


# ---------------------------------------------------------------------------
# 7.2 VARX avec le Brent
# ---------------------------------------------------------------------------

def varx_design(panel: pd.DataFrame, brent_lag: int, p: int = 1, endog=("XOM_ret", "XLE_ret")) -> pd.DataFrame:
    """Tableau des variables d'un VARX(p) : rendements expliqués, leurs p retards et le Brent décalé de `brent_lag`.

    brent_lag = 0 : Brent du même jour (explicatif, mais inconnu au moment de prévoir) ;
    brent_lag = 1 : Brent de la veille (connu en t, donc utilisable pour prévoir t + 1).
    Les jours où une variable manque (Brent absent, §1.4) sont retirés : aucune imputation.
    """
    d = pd.DataFrame({e: panel[e] for e in endog})
    for k in range(1, p + 1):
        for e in endog:
            d[f"{e} (t−{k})"] = panel[e].shift(k)
    d[f"Brent (t−{brent_lag})" if brent_lag else "Brent (t)"] = panel[BRENT].shift(brent_lag)
    return d.dropna()


def fit_varx(design: pd.DataFrame, endog=("XOM_ret", "XLE_ret")) -> dict:
    """Estime chaque équation par MCO avec erreurs-types robustes HC3 (même choix que le Granger robuste du §3.2).

    Un VAR(X) sans contrainte s'estime équation par équation par MCO : c'est l'estimateur
    du maximum de vraisemblance gaussien, identique à statsmodels.VAR.
    """
    X = sm.add_constant(design.drop(columns=list(endog)))
    return {e: sm.OLS(design[e], X).fit(cov_type="HC3") for e in endog}


def varx_table(fits: dict, fits_var: dict) -> pd.DataFrame:
    """Coefficient du Brent dans chaque équation, son test robuste, et le gain de R² par rapport au VAR(1) seul."""
    rows = []
    for e, res in fits.items():
        bcol = [c for c in res.params.index if c.startswith("Brent")][0]
        rows.append({"équation": e, "variable exogène": bcol, "coefficient": res.params[bcol],
                     "erreur-type HC3": res.bse[bcol], "t": res.tvalues[bcol], "p-value HC3": res.pvalues[bcol],
                     "R² VARX": res.rsquared, "R² VAR(1) seul": fits_var[e].rsquared,
                     "gain de R² (points)": 100 * (res.rsquared - fits_var[e].rsquared), "n": int(res.nobs)})
    return pd.DataFrame(rows).set_index(["équation", "variable exogène"])


def varx_analysis(panel: pd.DataFrame, sample: dict) -> pd.DataFrame:
    """VARX(1) avec Brent du jour et Brent de la veille, sur plusieurs échantillons (robustesse à 2020).

    Le VAR(1) de référence est estimé sur exactement les mêmes jours, pour que le gain de R²
    ne mélange pas deux échantillons différents.
    """
    out = []
    for name, mask_fn in sample.items():
        for lag in (0, 1):
            d = varx_design(panel, lag)
            d = d[mask_fn(d.index)]
            fits = fit_varx(d)
            fits_var = fit_varx(d.drop(columns=[c for c in d.columns if c.startswith("Brent")]))
            t = varx_table(fits, fits_var)
            t.insert(0, "échantillon", name)
            out.append(t)
    return pd.concat(out)
