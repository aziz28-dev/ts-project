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


# ---------------------------------------------------------------------------
# 7.3 DCC-GARCH : corrélation conditionnelle dynamique (Engle, 2002)
# ---------------------------------------------------------------------------

def dcc_standardized(panel: pd.DataFrame, fit_end: pd.Timestamp, cols=("XOM_ret", "XLE_ret")):
    """Étape 1 : un GJR(1,1)-t de moyenne nulle par actif (spécification du §3.3), estimé sur le train.

    Les paramètres sont ensuite fixés et la variance filtrée sur tout l'échantillon : les
    résidus standardisés z_t = r_t / σ_t du test n'utilisent aucun paramètre estimé sur le test.
    Renvoie les résidus standardisés (DataFrame) et les résultats univariés.
    """
    from arch.univariate import GARCH, StudentsT, ZeroMean

    from src.classical import fit_garch

    r = panel[list(cols)].iloc[1:]
    Z, fits = {}, {}
    for c in cols:
        res = fit_garch(r.loc[:fit_end, c], o=1, dist="t")
        full = ZeroMean(r[c].to_numpy(), volatility=GARCH(1, 1, 1), distribution=StudentsT(), rescale=False).fix(res.params)
        Z[c] = r[c].to_numpy() / full.conditional_volatility
        fits[c] = res
    return pd.DataFrame(Z, index=r.index), fits


def _dcc_path(Z: np.ndarray, a: float, b: float, Qbar: np.ndarray):
    """Récurrence Q_t = (1 − a − b) Q̄ + a z_{t−1} z_{t−1}' + b Q_{t−1}, puis R_t = Q_t normalisée."""
    T, k = Z.shape
    Q = Qbar.copy()
    R = np.empty((T, k, k))
    for t in range(T):
        if t > 0:
            Q = (1 - a - b) * Qbar + a * np.outer(Z[t - 1], Z[t - 1]) + b * Q
        d = np.sqrt(np.diag(Q))
        R[t] = Q / np.outer(d, d)
    return R


def dcc_loglik(params, Z: np.ndarray, Qbar: np.ndarray) -> float:
    """Partie « corrélation » de la quasi-vraisemblance gaussienne : −½ Σ (ln|R_t| + z_t' R_t⁻¹ z_t − z_t' z_t)."""
    a, b = params
    R = _dcc_path(Z, a, b, Qbar)
    det = R[:, 0, 0] * R[:, 1, 1] - R[:, 0, 1] ** 2            # k = 2 : formule fermée, plus rapide
    inv_quad = (R[:, 1, 1] * Z[:, 0] ** 2 - 2 * R[:, 0, 1] * Z[:, 0] * Z[:, 1] + R[:, 0, 0] * Z[:, 1] ** 2) / det
    return float(-0.5 * np.sum(np.log(det) + inv_quad - np.sum(Z ** 2, axis=1)))


def dcc_fit(Z: np.ndarray) -> dict:
    """Étape 2 : estimation de (a, b) par maximum de la quasi-vraisemblance, sous a, b ≥ 0 et a + b < 1.

    Q̄ = moyenne des z_t z_t' (« correlation targeting »), comme rmgarch. Les erreurs-types
    viennent du hessien numérique de cette seule étape : elles ignorent l'incertitude de
    l'étape 1 et sont donc un peu trop petites (approximation usuelle).
    """
    from scipy.optimize import minimize

    Qbar = Z.T @ Z / len(Z)
    obj = lambda p: -dcc_loglik(p, Z, Qbar)
    cons = {"type": "ineq", "fun": lambda p: 0.9999 - p[0] - p[1]}
    best = min((minimize(obj, x0, method="SLSQP", bounds=[(0, 1), (0, 1)], constraints=cons)
                for x0 in ([0.02, 0.95], [0.05, 0.90], [0.10, 0.80])), key=lambda r: r.fun)
    a, b = best.x
    # Hessien numérique (différences centrées) de −log-vraisemblance.
    h, H = 1e-4, np.zeros((2, 2))
    for i in range(2):
        for j in range(2):
            ei, ej = np.eye(2)[i] * h, np.eye(2)[j] * h
            H[i, j] = (obj(best.x + ei + ej) - obj(best.x + ei - ej) - obj(best.x - ei + ej) + obj(best.x - ei - ej)) / (4 * h * h)
    try:
        se = np.sqrt(np.diag(np.linalg.inv(H)))
    except np.linalg.LinAlgError:
        se = np.array([np.nan, np.nan])
    ll_dcc = -best.fun
    ll_ccc = dcc_loglik([0.0, 0.0], Z, Qbar)
    return {"a": a, "b": b, "se_a": se[0], "se_b": se[1], "Qbar": Qbar, "loglik_dcc": ll_dcc, "loglik_ccc": ll_ccc,
            "converged": bool(best.success)}


def dcc_correlation(Z: pd.DataFrame, fit: dict) -> pd.Series:
    """Corrélation conditionnelle ρ_t filtrée sur tout l'échantillon avec les paramètres du train."""
    R = _dcc_path(Z.to_numpy(), fit["a"], fit["b"], fit["Qbar"])
    return pd.Series(R[:, 0, 1], index=Z.index, name="corrélation DCC")


def engle_sheppard(Z: np.ndarray, lags: int = 5) -> dict:
    """Test d'Engle et Sheppard (2001), H₀ : corrélation constante (CCC).

    On « blanchit » les résidus standardisés par la corrélation constante, ŝ_t = R̄^(−1/2) z_t.
    Sous H₀, Y_t = ŝ_1t ŝ_2t (partie hors diagonale de ŝ_t ŝ_t' − I) n'est pas prévisible.
    On régresse Y_t sur une constante et ses `lags` retards : la statistique δ'X'Xδ / σ̂²
    suit un χ² à lags + 1 degrés de liberté.
    """
    Rbar = np.corrcoef(Z.T)
    w, V = np.linalg.eigh(Rbar)
    S = Z @ (V @ np.diag(w ** -0.5) @ V.T)
    Y = S[:, 0] * S[:, 1]
    X = np.column_stack([np.ones(len(Y) - lags)] + [Y[lags - k:len(Y) - k] for k in range(1, lags + 1)])
    y = Y[lags:]
    delta = np.linalg.lstsq(X, y, rcond=None)[0]
    s2 = np.mean((y - X @ delta) ** 2)
    stat = float(delta @ X.T @ X @ delta / s2)
    return {"statistique": stat, "ddl": lags + 1, "p-value": float(stats.chi2.sf(stat, lags + 1))}
