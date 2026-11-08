"""Section 3 : modèles économétriques classiques et leurs diagnostics.

3.1 ARIMA / SARIMA (ce module, première partie). VAR, VECM et GARCH suivront.

Convention : un ARIMA(p,1,q) sur le log-prix est estimé sous sa forme équivalente
ARMA(p,q) sur le rendement r_t = 100 × Δ ln P_t (en %). La constante éventuelle
de l'ARMA est alors exactement la dérive du log-prix. Tous les modèles sont
estimés sur la même série (mêmes n observations), donc leurs AIC/BIC sont comparables.
"""

from __future__ import annotations

import warnings

import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.stats.diagnostic import acorr_ljungbox, het_arch
from statsmodels.tsa.statespace.sarimax import SARIMAX

ALPHA = 0.05


# ---------------------------------------------------------------------------
# Estimation
# ---------------------------------------------------------------------------

def returns_for_model(logp: pd.Series) -> pd.Series:
    """Rendement en % sur index positionnel : r_t = 100 × (ln P_t − ln P_{t−1}).

    - ×100 : coefficients et variance des chocs se lisent en % (et l'optimiseur
      est mieux conditionné qu'avec des chocs de l'ordre de 0,01).
    - index positionnel : le calendrier boursier n'a pas de fréquence pandas
      régulière ; statsmodels en a besoin pour indexer les prévisions.
    """
    return pd.Series(100 * np.diff(logp.to_numpy()), name="r")


def fit_arima(r: pd.Series, p: int, q: int, drift: bool = False, seasonal=(0, 0, 0)):
    """ARIMA(p,1,q)(P,0,Q)[5] du log-prix, estimé comme (S)ARMA sur les rendements.

    Maximum de vraisemblance exacte (filtre de Kalman). Erreurs-types « robustes »
    (sandwich QMLE) : les résidus sont hétéroscédastiques (effets ARCH, §2.3), ce
    qui rend les erreurs-types classiques trop optimistes.
    seasonal = (P, 0, Q) avec une période fixée à s = 5 jours de bourse.
    """
    P, D, Q = seasonal
    model = SARIMAX(r, order=(p, 0, q), seasonal_order=(P, D, Q, 5 if (P or Q or D) else 0),
                    trend="c" if drift else "n")
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        return model.fit(disp=False, cov_type="robust", maxiter=500)


def label(p: int, q: int, drift: bool = False, seasonal=(0, 0, 0)) -> str:
    s = f"ARIMA({p},1,{q})"
    if any(seasonal):
        s = f"SARIMA({p},1,{q})({seasonal[0]},{seasonal[1]},{seasonal[2]})[5]"
    return s + (" + dérive" if drift else "")


def n_arma(res) -> int:
    """Nombre de paramètres ARMA (AR, MA, saisonniers) : ddl à retirer au Ljung-Box."""
    return sum(n.startswith(("ar.", "ma.")) for n in res.model.param_names)


def summary_row(res, name: str) -> dict:
    """Ligne du tableau comparatif : critères d'information et significativité."""
    params = res.params.drop("sigma2", errors="ignore")
    pvals = res.pvalues.drop("sigma2", errors="ignore")
    coefs = "; ".join(f"{k} = {v:.4f} (p = {pvals[k]:.3f})" for k, v in params.items()) or "—"
    return {
        "modèle": name,
        "nb paramètres": len(res.params),
        "log-vraisemblance": res.llf,
        "AIC": res.aic,
        "BIC": res.bic,
        "σ² (%²)": res.params["sigma2"],
        "coefficients (p-value robuste)": coefs,
        "coefficients tous significatifs (5 %)": ("—" if not len(pvals)
                                                  else "oui" if (pvals < ALPHA).all() else "non"),
    }


def compare(fits: dict) -> pd.DataFrame:
    """Tableau trié par AIC, avec l'écart à la meilleure valeur de chaque critère."""
    df = pd.DataFrame([summary_row(r, n) for n, r in fits.items()]).set_index("modèle")
    df.insert(4, "ΔAIC", df["AIC"] - df["AIC"].min())
    df.insert(6, "ΔBIC", df["BIC"] - df["BIC"].min())
    return df.sort_values("AIC")


def ic_grid(r: pd.Series, max_p: int = 3, max_q: int = 3) -> pd.DataFrame:
    """AIC et BIC de tous les ARIMA(p,1,q) sans dérive, p, q ≤ max."""
    rows = []
    for p in range(max_p + 1):
        for q in range(max_q + 1):
            res = fit_arima(r, p, q)
            rows.append({"p": p, "q": q, "AIC": res.aic, "BIC": res.bic})
    return pd.DataFrame(rows)


def lr_test(restricted, full) -> dict:
    """Rapport de vraisemblance entre modèles emboîtés (H0 : le modèle restreint suffit)."""
    stat = 2 * (full.llf - restricted.llf)
    df = len(full.params) - len(restricted.params)
    return {"LR": stat, "ddl": df, "p-value": stats.chi2.sf(stat, df)}


def ic_robustness(r: pd.Series, dates: pd.DatetimeIndex, specs: dict, vol_window: int = 21) -> pd.DataFrame:
    """ΔAIC et ΔBIC de chaque spécification par rapport à ARIMA(0,1,0), sur trois versions des rendements.

    Le gain d'AIC d'un terme ARMA peut venir d'une vraie dynamique de la moyenne
    ou de quelques jours extrêmes (la vraisemblance gaussienne suppose une variance
    constante). On refait donc la comparaison sans 2020 et sur les rendements
    divisés par leur volatilité passée (shift(1)) : un gain réel doit survivre.
    specs : {nom: dict(p=, q=, seasonal=(P, 0, Q))}.
    """
    keep = np.asarray(dates.year != 2020)
    versions = {
        "échantillon complet": r,
        "hors 2020": pd.Series(r.to_numpy()[keep]),
        "standardisé (vol. 21 j passée)": (r / r.rolling(vol_window).std().shift(1)).dropna().reset_index(drop=True),
    }
    rows = []
    for vname, x in versions.items():
        base = fit_arima(x, 0, 0)
        for name, s in specs.items():
            res = fit_arima(x, s.get("p", 0), s.get("q", 0), seasonal=s.get("seasonal", (0, 0, 0)))
            rows.append({"modèle": name, "version": vname,
                         "ΔAIC vs (0,1,0)": res.aic - base.aic, "ΔBIC vs (0,1,0)": res.bic - base.bic})
    out = pd.DataFrame(rows).pivot(index="modèle", columns="version")
    # Ordre de lecture : échantillon complet d'abord, puis les deux contrôles.
    return out.reindex(columns=list(versions), level="version").reindex(list(specs))


def roots_table(res) -> pd.DataFrame:
    """Racines AR et MA (module, argument) pour détecter une quasi-annulation.

    Des racines AR et MA presque identiques se simplifient dans le polynôme
    φ(L)/θ(L) : le modèle est alors quasi non identifié et équivaut à un modèle
    plus petit. Un module proche de 1 signale aussi une quasi-non-stationnarité
    (AR) ou une quasi-non-inversibilité (MA).
    """
    rows = []
    for kind, roots in (("AR", res.arroots), ("MA", res.maroots)):
        for z in roots:
            angle = np.angle(z)
            rows.append({"polynôme": kind, "racine": complex(np.round(z, 4)), "module": abs(z),
                         "période du cycle (jours)": (2 * np.pi / abs(angle)) if abs(angle) > 1e-8 else np.inf})
    return pd.DataFrame(rows)


def auto_arima(r: pd.Series, criterion: str = "aic", max_order: int = 5):
    """Recherche automatique pmdarima, exhaustive (stepwise=False), d = 0 sur les rendements.

    d est imposé à 0 sur les rendements (donc d = 1 sur le log-prix) : l'ordre
    d'intégration a été établi en §2.6, on ne le laisse pas redécider.
    """
    import pmdarima as pm

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        return pm.auto_arima(r, d=0, seasonal=False, stepwise=False, max_p=5, max_q=5,
                             max_order=max_order, information_criterion=criterion,
                             with_intercept="auto", suppress_warnings=True, error_action="ignore")


# ---------------------------------------------------------------------------
# Diagnostics des résidus
# ---------------------------------------------------------------------------

def residual_diagnostics(res, name: str, lb_lags=(10, 20), arch_lags=(5, 10)) -> dict:
    """Diagnostic complet exigé par le cahier (§3.1) pour un modèle.

    - Ljung-Box (H0 : pas d'autocorrélation) avec ddl corrigés du nombre de
      paramètres ARMA estimés : sans correction, le test est trop indulgent.
    - Jarque-Bera (H0 : normalité) : adapté à n ≈ 2 000, où Shapiro-Wilk rejette
      au moindre écart et n'est de toute façon défini que jusqu'à n = 5 000.
    - ARCH-LM d'Engle (H0 : pas d'effet ARCH) : régression de e_t² sur ses retards.
    """
    e = pd.Series(res.resid)
    k = n_arma(res)
    out = {"modèle": name, "ddl retirés (p+q)": k}
    lb = acorr_ljungbox(e, lags=list(lb_lags), model_df=k)
    for lag in lb_lags:
        out[f"Ljung-Box Q({lag})"] = lb.loc[lag, "lb_stat"]
        out[f"p LB({lag})"] = lb.loc[lag, "lb_pvalue"]
    jb = stats.jarque_bera(e)
    out.update({"skewness": stats.skew(e), "excès kurtosis": stats.kurtosis(e),
                "Jarque-Bera": jb.statistic, "p JB": jb.pvalue})
    for lag in arch_lags:
        lm, lm_p, _, _ = het_arch(e, nlags=lag)
        out[f"ARCH-LM({lag})"] = lm
        out[f"p ARCH({lag})"] = lm_p
    # Même contrôle qu'en §2.3 : Ljung-Box sur résidus divisés par leur volatilité passée.
    z = (e / e.rolling(21).std().shift(1)).dropna()
    lbz = acorr_ljungbox(z, lags=list(lb_lags), model_df=k)
    for lag in lb_lags:
        out[f"p LB({lag}) standardisé"] = lbz.loc[lag, "lb_pvalue"]
    return out


def diagnostics_table(fits: dict) -> pd.DataFrame:
    return pd.DataFrame([residual_diagnostics(r, n) for n, r in fits.items()]).set_index("modèle")


def decisions(diag: pd.DataFrame) -> pd.DataFrame:
    """Lecture des p-values au seuil de 5 % : ce que chaque test détecte."""
    cols = {"p LB(10)": "autocorrélation LB(10)", "p LB(20)": "autocorrélation LB(20)",
            "p LB(10) standardisé": "autocorrélation LB(10) standardisé",
            "p JB": "non-normalité (JB)", "p ARCH(5)": "effet ARCH(5)", "p ARCH(10)": "effet ARCH(10)"}
    return diag[list(cols)].lt(ALPHA).rename(columns=cols).replace({True: "détecté", False: "non détecté"})
