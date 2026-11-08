"""Section 3 : modèles économétriques classiques et leurs diagnostics.

3.1 ARIMA / SARIMA ; 3.2 VAR, Granger, cointégration, VECM ; 3.3 GARCH.

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


# ===========================================================================
# 3.2 VAR, causalité de Granger, cointégration, VECM
# ===========================================================================

def _versions(R: pd.DataFrame, vol_window: int = 21) -> dict:
    """Trois versions d'un panel de rendements : complet, hors 2020, standardisé par la vol. passée."""
    d = R.index
    return {
        "échantillon complet": R.reset_index(drop=True),
        "hors 2020": R[d.year != 2020].reset_index(drop=True),
        "standardisé (vol. 21 j passée)": (R / R.rolling(vol_window).std().shift(1)).dropna().reset_index(drop=True),
    }


def var_order_selection(R: pd.DataFrame, maxlags: int = 10) -> pd.DataFrame:
    """Ordre du VAR choisi par AIC, BIC, HQ et FPE, sur les trois versions des rendements.

    Même logique qu'en 3.1 : un retard retenu seulement sur l'échantillon complet,
    et qui disparaît hors 2020 ou après standardisation, reflète l'hétéroscédasticité
    et non une dynamique exploitable.
    """
    from statsmodels.tsa.api import VAR

    rows = {name: VAR(X).select_order(maxlags).selected_orders for name, X in _versions(R).items()}
    return pd.DataFrame(rows).T.rename(columns=str.upper)


def var_ic_table(R: pd.DataFrame, maxlags: int = 10) -> pd.DataFrame:
    """Valeur de chaque critère pour chaque ordre (échantillon complet)."""
    from statsmodels.tsa.api import VAR

    sel = VAR(R.reset_index(drop=True)).select_order(maxlags)
    return pd.DataFrame({k.upper(): v for k, v in sel.ics.items()}).rename_axis("ordre p")


def fit_var(R: pd.DataFrame, p: int):
    from statsmodels.tsa.api import VAR

    return VAR(R.reset_index(drop=True)).fit(p)


def hosking_portmanteau(resid, h: int, var_order: int) -> dict:
    """Portmanteau multivarié ajusté (Hosking, 1980) : H0 = pas d'autocorrélation jusqu'au retard h.

    Écrit explicitement pour pouvoir l'appliquer aussi aux résidus standardisés.
    ddl = K² (h − p), où p est l'ordre du VAR.
    """
    e = np.asarray(resid, dtype=float)
    e = e - e.mean(axis=0)
    T, K = e.shape
    c0_inv = np.linalg.inv(e.T @ e / T)
    q = 0.0
    for j in range(1, h + 1):
        cj = e[j:].T @ e[:-j] / T
        q += np.trace(cj.T @ c0_inv @ cj @ c0_inv) / (T - j)
    q *= T ** 2
    df = K ** 2 * (h - var_order)
    return {"Q": q, "ddl": df, "p-value": stats.chi2.sf(q, df) if df > 0 else np.nan}


def _standardize(e: np.ndarray, vol_window: int = 21) -> np.ndarray:
    z = pd.DataFrame(e)
    return (z / z.rolling(vol_window).std().shift(1)).dropna().to_numpy()


def var_diagnostics(res, name: str, hs=(10, 20)) -> dict:
    """Diagnostic complet d'un VAR : stabilité, autocorrélation, normalité, effets ARCH.

    - Stabilité : valeurs propres de la matrice compagnon de module < 1.
    - Portmanteau de Hosking ajusté, sur résidus bruts puis standardisés par leur
      volatilité passée (même contrôle qu'en §2.3 et §3.1).
    - Jarque-Bera multivarié (Lütkepohl).
    - ARCH-LM d'Engle équation par équation.
    """
    e = res.resid.to_numpy()
    p = res.k_ar
    # VAR(0) : pas de retard, donc pas de racine ; il est stable par construction.
    out = {"modèle": name, "stable": bool(res.is_stable()) if p else True,
           "module max (matrice compagnon)": float(np.abs(1 / res.roots).max()) if p else 0.0}
    z = _standardize(e)
    for h in hs:
        out[f"p Portmanteau({h})"] = hosking_portmanteau(e, h, p)["p-value"]
    for h in hs:
        out[f"p Portmanteau({h}) standardisé"] = hosking_portmanteau(z, h, p)["p-value"]
    nt = res.test_normality()
    out["JB multivarié"] = float(nt.test_statistic)
    out["p JB"] = float(nt.pvalue)
    for j, col in enumerate(res.names):
        out[f"ARCH-LM(5) {col}"] = het_arch(e[:, j], nlags=5)[0]
        out[f"p ARCH-LM(5) {col}"] = het_arch(e[:, j], nlags=5)[1]
    out["corrélation des résidus"] = float(np.corrcoef(e.T)[0, 1])
    return out


def granger_tests(R: pd.DataFrame, lags=(1, 7, 9), hac_lags: int = 7) -> pd.DataFrame:
    """Causalité de Granger dans les deux sens : Wald F classique, robuste HC3 et HAC.

    Le test F classique du VAR suppose des erreurs homoscédastiques ; avec des
    effets ARCH massifs, il rejette trop souvent. HC3 corrige l'hétéroscédasticité,
    HAC (Newey-West) aussi l'autocorrélation. On refait le tout hors 2020.
    Chaque test : OLS d'une équation du VAR, H0 = tous les retards de l'autre variable nuls.
    """
    import statsmodels.api as sm

    cols = list(R.columns)
    samples = {"échantillon complet": R, "hors 2020": R[R.index.year != 2020]}
    rows = []
    for sname, S in samples.items():
        S = S.reset_index(drop=True)
        for p in lags:
            X = pd.concat({f"{c}_L{l}": S[c].shift(l) for c in cols for l in range(1, p + 1)}, axis=1)
            X = sm.add_constant(X).dropna()
            for y, x in ((cols[0], cols[1]), (cols[1], cols[0])):
                Y = S[y].loc[X.index]
                hyp = ", ".join(f"{x}_L{l} = 0" for l in range(1, p + 1))
                row = {"échantillon": sname, "retards p": p, "sens": f"{x} → {y}"}
                for lab, cov, kw in (("classique", "nonrobust", None), ("HC3", "HC3", None),
                                     ("HAC", "HAC", {"maxlags": hac_lags})):
                    fit = sm.OLS(Y, X).fit(cov_type=cov, cov_kwds=kw)
                    row[f"p {lab}"] = float(fit.wald_test(hyp, scalar=True, use_f=True).pvalue)
                rows.append(row)
    return pd.DataFrame(rows).set_index(["échantillon", "retards p", "sens"])


def engle_granger(L: pd.DataFrame) -> pd.DataFrame:
    """Engle-Granger dans les deux sens, avec constante puis constante + tendance.

    H0 : pas de cointégration (le résidu de la régression de long terme a une racine
    unitaire). Valeurs critiques de MacKinnon, plus sévères qu'un ADF simple car le
    résidu est estimé.
    """
    from statsmodels.tsa.stattools import coint

    a, b = L.columns
    rows = []
    for y, x in ((a, b), (b, a)):
        for trend, lab in (("c", "constante"), ("ct", "constante + tendance")):
            stat, p, cv = coint(L[y], L[x], trend=trend, autolag="aic")
            rows.append({"régression": f"{y} sur {x}", "déterministe": lab, "statistique": stat,
                         "valeur critique 5 %": cv[1], "p-value": p, "H0 rejetée (5 %)": p < ALPHA})
    return pd.DataFrame(rows).set_index(["régression", "déterministe"])


def johansen_table(L: pd.DataFrame, k_list: dict, det_order: int = 0) -> pd.DataFrame:
    """Tests de la trace et de la valeur propre maximale pour plusieurs nombres de retards.

    k_list : {libellé: k_ar_diff}. det_order = 0 : constante non restreinte.
    Lecture séquentielle : on teste r = 0 ; si rejeté, on teste r ≤ 1.
    """
    from statsmodels.tsa.vector_ar.vecm import coint_johansen

    rows = []
    for lab, k in k_list.items():
        j = coint_johansen(L.reset_index(drop=True), det_order, k)
        for i, h0 in enumerate(("r = 0", "r ≤ 1")):
            rows.append({"retards (Δ)": lab, "H0": h0,
                         "trace": j.lr1[i], "VC trace 10 %": j.cvt[i, 0], "VC trace 5 %": j.cvt[i, 1],
                         "λmax": j.lr2[i], "VC λmax 10 %": j.cvm[i, 0], "VC λmax 5 %": j.cvm[i, 1]})
    df = pd.DataFrame(rows).set_index(["retards (Δ)", "H0"])

    def verdict(stat, cv10, cv5):
        return np.where(stat > cv5, "rejet à 5 %", np.where(stat > cv10, "rejet à 10 % seulement", "non rejet"))

    df["trace : décision"] = verdict(df["trace"], df["VC trace 10 %"], df["VC trace 5 %"])
    df["λmax : décision"] = verdict(df["λmax"], df["VC λmax 10 %"], df["VC λmax 5 %"])
    return df


def cointegration_subperiods(L: pd.DataFrame, periods: dict) -> pd.DataFrame:
    """Stabilité de la relation : Engle-Granger et Johansen (k = 0) par sous-période."""
    from statsmodels.tsa.stattools import coint
    from statsmodels.tsa.vector_ar.vecm import coint_johansen

    a, b = L.columns
    rows = []
    for name, (start, end) in periods.items():
        S = L.loc[start:end]
        eg = coint(S[a], S[b], trend="c", autolag="aic")
        j = coint_johansen(S.reset_index(drop=True), 0, 0)
        rows.append({"période": name, "n": len(S), "Engle-Granger p-value": eg[1],
                     "Johansen trace (r = 0)": j.lr1[0], "VC 10 %": j.cvt[0, 0], "VC 5 %": j.cvt[0, 1]})
    return pd.DataFrame(rows).set_index("période")


def fit_vecm(L: pd.DataFrame, k_ar_diff: int = 0, rank: int = 1):
    """VECM avec constante restreinte à la relation de cointégration ('ci').

    'ci' plutôt qu'une constante libre : la dérive des rendements n'est pas
    significative (§2.2, §3.1), donc pas de tendance linéaire dans les niveaux ;
    la constante fixe seulement le niveau moyen de l'écart d'équilibre.
    """
    from statsmodels.tsa.vector_ar.vecm import VECM

    return VECM(L.reset_index(drop=True), k_ar_diff=k_ar_diff, coint_rank=rank, deterministic="ci").fit()


def vecm_summary(v, names) -> pd.DataFrame:
    """β normalisé, α avec p-values, vitesse β'α et demi-vie de l'écart à l'équilibre.

    L'écart z_t = β'y_t suit z_t = (1 + β'α) z_{t−1} + bruit : sa vitesse de retour
    β'α combine l'ajustement des DEUX actifs. Demi-vie = ln(0,5) / ln(1 + β'α).
    La formule à un seul α, ln(0,5)/ln(1 + α_i), ne vaut que si un seul actif s'ajuste.
    """
    a, b = v.alpha.ravel(), v.beta.ravel()
    speed = float(b @ a)
    rows = [{"paramètre": f"β ({n})", "valeur": b[i], "p-value": np.nan} for i, n in enumerate(names)]
    rows.append({"paramètre": "constante de la relation", "valeur": float(v.const_coint.ravel()[0]), "p-value": np.nan})
    rows += [{"paramètre": f"α ({n})", "valeur": a[i], "p-value": float(v.pvalues_alpha.ravel()[i])}
             for i, n in enumerate(names)]
    rows.append({"paramètre": "vitesse de l'écart β'α", "valeur": speed, "p-value": np.nan})
    rows.append({"paramètre": "demi-vie de l'écart (jours de bourse)",
                 "valeur": float(np.log(0.5) / np.log(1 + speed)) if -2 < speed < 0 else np.inf, "p-value": np.nan})
    return pd.DataFrame(rows).set_index("paramètre")


def spread_half_life(z: pd.Series) -> dict:
    """Demi-vie d'un écart par AR(1) : z_t = ρ z_{t−1} + u_t ⇒ demi-vie = ln(0,5)/ln(ρ)."""
    import statsmodels.api as sm

    zc = (z - z.mean()).to_numpy()
    rho = float(sm.OLS(zc[1:], zc[:-1]).fit().params[0])
    return {"rho": rho, "demi-vie (jours)": float(np.log(0.5) / np.log(rho)) if 0 < rho < 1 else np.inf}


def vecm_diagnostics(v, name: str, hs=(10, 20)) -> dict:
    """Mêmes diagnostics qu'un VAR, sur les résidus du VECM."""
    e = np.asarray(v.resid)
    p = v.k_ar  # ordre du VAR en niveaux = k_ar_diff + 1
    out = {"modèle": name}
    z = _standardize(e)
    for h in hs:
        out[f"p Portmanteau({h})"] = hosking_portmanteau(e, h, p)["p-value"]
    for h in hs:
        out[f"p Portmanteau({h}) standardisé"] = hosking_portmanteau(z, h, p)["p-value"]
    nt = v.test_normality()
    out["JB multivarié"] = float(nt.test_statistic)
    out["p JB"] = float(nt.pvalue)
    for j in range(e.shape[1]):
        out[f"p ARCH-LM(5) éq. {j + 1}"] = het_arch(e[:, j], nlags=5)[1]
    return out


# ===========================================================================
# 3.3 GARCH
# ===========================================================================
# Notation de la bibliothèque arch, reprise partout :
#   σ²_t = ω + Σ α_i ε²_{t−i} + Σ γ_j ε²_{t−j}·1[ε_{t−j} < 0] + Σ β_k σ²_{t−k}
#   p = nombre de termes ARCH (α), o = termes asymétriques GJR (γ), q = termes GARCH (β).
#   « GARCH(1,2) » = 1 terme α et 2 termes β.

def garch_label(p: int = 1, o: int = 0, q: int = 1, dist: str = "t") -> str:
    name = "GJR" if o else "GARCH"
    law = {"normal": "loi normale", "t": "loi de Student", "skewt": "Student asymétrique"}[dist]
    return f"{name}({p},{q}) — {law}"


def fit_garch(r: pd.Series, p: int = 1, o: int = 0, q: int = 1, dist: str = "t", mean: str = "Zero"):
    """GARCH sur les rendements en %, par maximum de vraisemblance.

    mean="Zero" par défaut : la moyenne retenue en 3.1 est la marche aléatoire sans
    dérive (rendement moyen non significatif). Le modèle complet est donc
    « ARIMA(0,1,0) + erreurs GARCH ». Erreurs-types robustes (Bollerslev-Wooldridge),
    valeur par défaut de arch.
    """
    from arch import arch_model

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        return arch_model(r, mean=mean, vol="GARCH", p=p, o=o, q=q, dist=dist,
                          rescale=False).fit(disp="off")


def persistence(res) -> float:
    """Persistance de la variance : Σα + Σβ + Σγ/2.

    Le terme GJR γ ne joue que pour les chocs négatifs, soit la moitié des cas
    pour une loi symétrique, d'où le facteur 1/2.
    """
    pr = res.params
    return float(pr.filter(like="alpha").sum() + pr.filter(like="beta").sum() + pr.filter(like="gamma").sum() / 2)


def half_life(pers: float) -> float:
    """Nombre de jours pour qu'un choc de variance perde la moitié de son effet : ln(0,5)/ln(persistance)."""
    return float(np.log(0.5) / np.log(pers)) if 0 < pers < 1 else np.inf


def garch_compare(r: pd.Series, specs: dict, dists=("normal", "t", "skewt"), mean: str = "Zero") -> pd.DataFrame:
    """Tableau comparatif : vraisemblance, critères, contraintes de positivité, persistance."""
    rows = []
    for dist in dists:
        for name, kw in specs.items():
            res = fit_garch(r, dist=dist, mean=mean, **kw)
            pr = res.params
            var_pars = pr.drop([k for k in pr.index if k in ("mu", "nu", "lambda")])
            pers = persistence(res)
            rows.append({
                "modèle": name, "loi": dist, "nb paramètres": len(pr),
                "log-vraisemblance": res.loglikelihood, "AIC": res.aic, "BIC": res.bic,
                "ω > 0 et α, γ, β ≥ 0": bool((var_pars > 0).iloc[0] and (var_pars.iloc[1:] >= 0).all()),
                "persistance": pers, "persistance < 1": pers < 1, "demi-vie (jours)": half_life(pers),
                "converge": res.convergence_flag == 0,
            })
    df = pd.DataFrame(rows).set_index(["modèle", "loi"])
    df.insert(4, "ΔAIC", df["AIC"] - df["AIC"].min())
    df.insert(6, "ΔBIC", df["BIC"] - df["BIC"].min())
    return df.sort_values("BIC")


def garch_params(res) -> pd.DataFrame:
    """Coefficients, erreurs-types robustes et p-values."""
    return pd.DataFrame({"coefficient": res.params, "erreur-type robuste": res.std_err,
                         "statistique t": res.tvalues, "p-value": res.pvalues})


def garch_diagnostics(res, name: str, lb_lags=(10, 20), arch_lags=(5, 10)) -> dict:
    """Diagnostic des résidus standardisés z_t = ε_t / σ_t.

    Si le modèle capte bien la variance, z_t doit être un bruit blanc (Ljung-Box
    sur z), sans effet ARCH restant (Ljung-Box sur z², ARCH-LM), et suivre la loi
    supposée : on teste l'adéquation à la loi de Student estimée par
    Kolmogorov-Smirnov, et la normalité par Jarque-Bera (comparaison).
    Pas de correction de ddl au Ljung-Box sur z : la moyenne n'a aucun paramètre ARMA.
    """
    z = pd.Series(res.std_resid).dropna()
    out = {"modèle": name}
    lb = acorr_ljungbox(z, lags=list(lb_lags))
    lb2 = acorr_ljungbox(z ** 2, lags=list(lb_lags))
    for lag in lb_lags:
        out[f"p LB z ({lag})"] = lb.loc[lag, "lb_pvalue"]
    for lag in lb_lags:
        out[f"p LB z² ({lag})"] = lb2.loc[lag, "lb_pvalue"]
    for lag in arch_lags:
        lm, p, _, _ = het_arch(z, nlags=lag)
        out[f"ARCH-LM({lag})"] = lm
        out[f"p ARCH-LM({lag})"] = p
    out["excès kurtosis z"] = stats.kurtosis(z)
    out["p JB (normalité)"] = stats.jarque_bera(z).pvalue
    if "nu" in res.params:
        nu = float(res.params["nu"])
        # Student standardisée (variance 1) : t(ν) multipliée par √((ν−2)/ν).
        scale = np.sqrt((nu - 2) / nu)
        out["ν"] = nu
        out["p KS (Student ν)"] = stats.kstest(z, "t", args=(nu, 0, scale)).pvalue
    return out


def garch_subperiods(r: pd.Series, periods: dict, **kw) -> pd.DataFrame:
    """Stabilité des paramètres : même GARCH estimé sur des sous-périodes."""
    rows = []
    for name, (start, end) in periods.items():
        res = fit_garch(r.loc[start:end], **kw)
        pers = persistence(res)
        rows.append({"période": name, "n": int(res.nobs), **res.params.to_dict(),
                     "persistance": pers, "demi-vie (jours)": half_life(pers)})
    return pd.DataFrame(rows).set_index("période")


def news_impact(res, eps=np.linspace(-6, 6, 241)) -> pd.Series:
    """Courbe d'impact des chocs : variance du lendemain en fonction du choc d'aujourd'hui,
    la variance d'aujourd'hui étant fixée à son niveau moyen sur l'échantillon."""
    pr = res.params
    sigma2_bar = float(np.mean(res.conditional_volatility ** 2))
    a = pr.get("alpha[1]", 0.0)
    g = pr.get("gamma[1]", 0.0)
    b = pr.filter(like="beta").sum()
    s2 = pr["omega"] + a * eps ** 2 + g * eps ** 2 * (eps < 0) + b * sigma2_bar
    return pd.Series(s2, index=eps, name="variance conditionnelle du lendemain")
