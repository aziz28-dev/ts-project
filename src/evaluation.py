"""Section 6 : prévision multi-origines sur le test, métriques sur le prix, Diebold-Mariano.

Protocole (cahier §6, plan phase 6) :
- origines : du dernier jour du train à l'avant-dernier jour du test (252 origines) ;
  à chaque origine t, prévision de ln P_{t+1}, …, ln P_{t+10} avec la seule information
  connue en t ;
- modèles classiques ré-estimés tous les `refit_every` = 20 jours sur une fenêtre
  croissante (données jusqu'à l'origine qui ouvre le bloc). Entre deux ré-estimations,
  les paramètres restent fixes, mais l'état du modèle est mis à jour chaque jour
  (filtrage), donc chaque prévision utilise bien toutes les observations jusqu'à t ;
- réseaux (§4) : entraînés une seule fois sur le train, appliqués aux fenêtres du test ;
- métriques MSE, RMSE, MAE et MAPE sur le PRIX en dollars ; jamais de MAPE sur les rendements ;
- prévision ponctuelle du prix : P̂_{t+h} = P_t × exp(prévision du log-rendement cumulé),
  c'est-à-dire la médiane de la loi prévue (convention de reconstruction du §4) ;
- Diebold-Mariano codé à la main : perte quadratique, variance HAC à h − 1 retards,
  correction de Harvey, Leybourne et Newbold (1997), loi de Student à n − 1 ddl.
  Même définition que `forecast::dm.test` en R, pour pouvoir comparer les deux.
"""

from __future__ import annotations

import time
import warnings

import numpy as np
import pandas as pd
from scipy import stats

from src.utils import load_config

_cfg = load_config()
HORIZON = _cfg["forecast"]["horizon"]
EVAL_H = _cfg["forecast"]["eval_horizons"]
REFIT = _cfg["forecast"]["refit_every"]
LEVEL = _cfg["forecast"]["confidence_level"]
Z = float(stats.norm.ppf(0.5 + LEVEL / 2))
HS = np.arange(1, HORIZON + 1)


# ---------------------------------------------------------------------------
# Origines et blocs de ré-estimation
# ---------------------------------------------------------------------------

def origins(panel: pd.DataFrame, train_end: pd.Timestamp) -> np.ndarray:
    """Positions des origines : dernier jour du train → avant-dernier jour du test."""
    return np.arange(panel.index.get_loc(train_end), len(panel) - 1)


def blocks(orig: np.ndarray, every: int = REFIT):
    """Découpe les origines en blocs de `every` jours ; le modèle est ré-estimé au début de chaque bloc."""
    return [np.arange(i, min(i + every, len(orig))) for i in range(0, len(orig), every)]


def _result(name, m, lo=None, hi=None, var1=None, seconds=0.0, n_fit=0, note=""):
    return {"name": name, "m": m, "lo": lo, "hi": hi, "var1": var1, "seconds": seconds, "n_fit": n_fit, "note": note}


# ---------------------------------------------------------------------------
# Modèles : chaque fonction renvoie la prévision de ln P_XOM (n_origines × 10)
# et, si le modèle le permet, les bornes de l'intervalle à 95 % en log-prix.
# ---------------------------------------------------------------------------

def rw(panel: pd.DataFrame, orig: np.ndarray) -> dict:
    """Baseline : marche aléatoire sans dérive, P̂_{t+h} = P_t.

    Intervalle : variance des rendements constante, estimée sur tout le passé connu
    (moyenne de r², cohérente avec une moyenne nulle), ré-estimée tous les 20 jours ;
    l'écart-type du log-prix à h jours vaut σ√h.
    """
    t0 = time.time()
    L, r = panel["XOM_logp"].to_numpy(), panel["XOM_ret"].to_numpy()
    m = np.repeat(L[orig][:, None], HORIZON, axis=1)
    s2 = np.empty(len(orig))
    for b in blocks(orig):
        s2[b] = np.mean(r[1:orig[b[0]] + 1] ** 2)
    half = Z * np.sqrt(s2)[:, None] * np.sqrt(HS) / 100
    return _result("Marche aléatoire (baseline)", m, m - half, m + half, s2, time.time() - t0, len(blocks(orig)),
                   "variance constante")


def arima(panel: pd.DataFrame, orig: np.ndarray, order=(3, 2)) -> dict:
    """ARIMA(p,1,q) estimé comme ARMA(p,q) sur les rendements (convention du §3.1), ré-estimé tous les 20 jours.

    Variance de l'erreur du log-rendement cumulé à h jours : σ² Σ_{j<h} (ψ_0 + … + ψ_j)²,
    où les ψ sont les coefficients de la forme moyenne mobile infinie de l'ARMA.
    """
    from statsmodels.tsa.arima_process import arma2ma

    from src.deep import arima_multi_origin

    t0 = time.time()
    L = panel["XOM_logp"].to_numpy()
    r = panel["XOM_ret"].to_numpy()[1:]           # r[i] = rendement de la position i + 1
    m, lo, hi = (np.empty((len(orig), HORIZON)) for _ in range(3))
    for b in blocks(orig):
        o = orig[b]
        # Estimation sur les rendements jusqu'à l'origine qui ouvre le bloc (positions 1 … o[0]).
        _, F, res = arima_multi_origin(r, fit_end=o[0], order=order)
        cum = np.cumsum(F[o - 1], axis=1) / 100   # ligne o − 1 : état filtré avec l'information jusqu'à o
        m[b] = L[o][:, None] + cum
        psi = arma2ma(np.r_[1, -res.arparams], np.r_[1, res.maparams], lags=HORIZON)
        sd = np.sqrt(res.params[-1] * np.cumsum(np.cumsum(psi) ** 2)) / 100
        lo[b], hi[b] = m[b] - Z * sd, m[b] + Z * sd
    return _result(f"ARIMA({order[0]},1,{order[1]})", m, lo, hi, None, time.time() - t0, len(blocks(orig)))


def var(panel: pd.DataFrame, orig: np.ndarray, p: int = 1) -> dict:
    """VAR(p) sur les rendements de XOM et XLE (§3.2), ré-estimé tous les 20 jours.

    La prévision du log-prix de XOM cumule les rendements prévus. Variance du cumul à h
    jours : Σ_{j<h} C_j Σ_u C_j', où C_j = Φ_0 + … + Φ_j (Φ : forme moyenne mobile du VAR).
    """
    from statsmodels.tsa.api import VAR

    t0 = time.time()
    L = panel["XOM_logp"].to_numpy()
    R = panel[["XOM_ret", "XLE_ret"]].to_numpy()
    m, lo, hi = (np.empty((len(orig), HORIZON)) for _ in range(3))
    for b in blocks(orig):
        o = orig[b]
        v = VAR(R[1:o[0] + 1]).fit(p)
        A, c = v.coefs, v.intercept
        hist = [R[o - k] for k in range(p)]          # y_t, y_{t−1}, … connus à l'origine
        cum = np.zeros(len(o))
        for h in range(HORIZON):
            y = c + sum(hist[k] @ A[k].T for k in range(p))
            hist = [y] + hist[:-1]
            cum = cum + y[:, 0]
            m[b, h] = L[o] + cum / 100
        C = np.cumsum(v.ma_rep(HORIZON - 1), axis=0)
        sd = np.sqrt(np.cumsum([(Cj @ v.sigma_u @ Cj.T)[0, 0] for Cj in C])) / 100
        lo[b], hi[b] = m[b] - Z * sd, m[b] + Z * sd
    return _result(f"VAR({p})", m, lo, hi, None, time.time() - t0, len(blocks(orig)))


def varx(panel: pd.DataFrame, orig: np.ndarray, exog: str = "BZ=F_ret") -> dict:
    """VARX(1) : VAR(1) de XOM et XLE avec le rendement du Brent de la VEILLE en exogène (§7.2).

    y_t = c + A y_{t−1} + B b_{t−1} + u_t, estimé par MCO sur les jours sans valeur manquante,
    ré-estimé tous les 20 jours. Prévision à 1 jour : b_t est connu à l'origine. Au-delà,
    le Brent futur est inconnu : on prend sa prévision de marche aléatoire, un rendement nul.
    Pas d'intervalle : il faudrait aussi modéliser l'incertitude du Brent.
    """
    t0 = time.time()
    L = panel["XOM_logp"].to_numpy()
    R = panel[["XOM_ret", "XLE_ret"]].to_numpy()
    b = panel[exog].to_numpy()
    m = np.empty((len(orig), HORIZON))
    coefs = []
    for blk in blocks(orig):
        o = orig[blk]
        t = np.arange(2, o[0] + 1)
        X = np.column_stack([np.ones(len(t)), R[t - 1], b[t - 1]])
        ok = ~np.isnan(X).any(axis=1) & ~np.isnan(R[t]).any(axis=1)
        beta = np.linalg.lstsq(X[ok], R[t][ok], rcond=None)[0]       # (4, 2) : constante, XOM, XLE, Brent
        c, A, B = beta[0], beta[1:3].T, beta[3]
        coefs.append(pd.Series({"Brent → XOM": B[0], "Brent → XLE": B[1]}, name=str(panel.index[o[0]].date())))
        y = c + R[o] @ A.T + np.outer(b[o], B)
        cum = y[:, 0].copy()
        m[blk, 0] = L[o] + cum / 100
        for h in range(1, HORIZON):
            y = c + y @ A.T
            cum += y[:, 0]
            m[blk, h] = L[o] + cum / 100
    out = _result("VARX(1) + Brent de la veille", m, seconds=time.time() - t0, n_fit=len(blocks(orig)),
                  note="Brent futur = marche aléatoire au-delà de h = 1")
    out["coefs"] = pd.DataFrame(coefs)
    return out


def vecm(panel: pd.DataFrame, orig: np.ndarray) -> dict:
    """VECM (r = 1, sans retard en différences, constante dans la relation), ré-estimé tous les 20 jours.

    Forme en niveaux : y_t = (I + αβ') y_{t−1} + α c + u_t. Cette récurrence est vérifiée
    identique à `VECMResults.predict`. Variance à h jours : Σ_{j<h} A^j Σ_u A^j'.
    """
    from src.classical import fit_vecm

    t0 = time.time()
    Lp = panel[["XOM_logp", "XLE_logp"]]
    m, lo, hi = (np.empty((len(orig), HORIZON)) for _ in range(3))
    for b in blocks(orig):
        o = orig[b]
        v = fit_vecm(Lp.iloc[:o[0] + 1])
        A = np.eye(2) + v.alpha @ v.beta.T
        d = (v.alpha @ v.const_coint.T).ravel()
        Y = Lp.to_numpy()[o]
        P, Ah, sd = np.zeros((2, 2)), np.eye(2), np.empty(HORIZON)
        for h in range(HORIZON):
            Y = Y @ A.T + d
            m[b, h] = Y[:, 0]
            P = P + Ah @ v.sigma_u @ Ah.T
            sd[h] = np.sqrt(P[0, 0])
            Ah = A @ Ah
        lo[b], hi[b] = m[b] - Z * sd, m[b] + Z * sd
    return _result("VECM", m, lo, hi, None, time.time() - t0, len(blocks(orig)))


def rw_garch(panel: pd.DataFrame, orig: np.ndarray, sims: int = 2000, seed: int | None = None) -> dict:
    """Marche aléatoire + GJR-GARCH(1,1) avec loi de Student (modèle retenu au §3.3).

    Même prévision ponctuelle que la baseline (moyenne nulle) ; seuls les intervalles changent.
    Ils viennent de `sims` trajectoires simulées sur 10 jours depuis chaque origine : le
    cumul de rendements de Student à variance GARCH n'a pas de loi connue en forme fermée.
    Paramètres ré-estimés tous les 20 jours, variance conditionnelle filtrée chaque jour.
    Renvoie aussi la variance prévue à 1 jour, évaluée à part (QLIKE).
    """
    from arch.univariate import GARCH, StudentsT, ZeroMean

    from src.classical import fit_garch

    seed =_cfg["seed"] if seed is None else seed
    t0 = time.time()
    L = panel["XOM_logp"].to_numpy()
    r = panel["XOM_ret"].to_numpy()[1:]
    m = np.repeat(L[orig][:, None], HORIZON, axis=1)
    lo, hi = np.empty_like(m), np.empty_like(m)
    var1 = np.empty(len(orig))
    params = []
    for k, b in enumerate(blocks(orig)):
        o = orig[b]
        res = fit_garch(pd.Series(r[:o[0]]), o=1, dist="t")
        params.append(res.params.rename(str(panel.index[o[0]].date())))
        # La graine est portée par la loi de Student : l'option random_state de forecast() n'agit
        # pas sur les tirages de la simulation (vérifié), seul le générateur de la loi le fait.
        fixed = ZeroMean(r, volatility=GARCH(1, 1, 1), distribution=StudentsT(seed=seed + k),
                         rescale=False).fix(res.params)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            fc = fixed.forecast(horizon=HORIZON, start=int(o[0] - 1), method="simulation", simulations=sims,
                                reindex=False)
        rows = o - o[0]                               # la première ligne correspond à l'origine o[0]
        cum = np.cumsum(fc.simulations.values[rows], axis=2) / 100
        lo[b] = L[o][:, None] + np.quantile(cum, 0.5 - LEVEL / 2, axis=1)
        hi[b] = L[o][:, None] + np.quantile(cum, 0.5 + LEVEL / 2, axis=1)
        var1[b] = fc.variance.values[rows, 0]
    out = _result("Marche aléatoire + GJR-GARCH-t", m, lo, hi, var1, time.time() - t0, len(blocks(orig)),
                  f"intervalles par simulation ({sims} trajectoires)")
    out["params"] = pd.DataFrame(params)
    return out


def from_return_forecasts(panel: pd.DataFrame, orig: np.ndarray, df: pd.DataFrame, seconds: dict | None = None) -> list:
    """Prévisions des réseaux (§4), en rendements en %, converties en log-prix ; pas d'intervalle."""
    L = panel["XOM_logp"].to_numpy()
    dates = panel.index[orig]
    out = []
    for name, g in df.groupby("modèle", sort=False):
        piv = g.pivot(index="origine", columns="h", values="rendement prévu (%)").reindex(dates)
        assert not piv.isna().any().any(), f"origines manquantes pour {name}"
        m = L[orig][:, None] + np.cumsum(piv.to_numpy(), axis=1) / 100
        out.append(_result(name, m, seconds=(seconds or {}).get(name, np.nan), note="entraîné une fois sur le train"))
    return out


# ---------------------------------------------------------------------------
# Évaluation sur le prix
# ---------------------------------------------------------------------------

def actual_prices(panel: pd.DataFrame, orig: np.ndarray) -> np.ndarray:
    """Prix réalisés P_{t+h} (NaN quand t + h dépasse la fin du test)."""
    P = panel["XOM_price"].to_numpy()
    A = np.full((len(orig), HORIZON), np.nan)
    for h in HS:
        ok = orig + h < len(P)
        A[ok, h - 1] = P[orig[ok] + h]
    return A


def price_forecast(panel: pd.DataFrame, orig: np.ndarray, fc: dict, key: str = "m") -> np.ndarray:
    """Prix prévu (ou borne d'intervalle) : P_t × exp(log-prix prévu − ln P_t)."""
    P, L = panel["XOM_price"].to_numpy()[orig], panel["XOM_logp"].to_numpy()[orig]
    return P[:, None] * np.exp(fc[key] - L[:, None])


def errors(panel, orig, fcs: list) -> dict:
    """Erreurs de prévision du prix en dollars, e = P_{t+h} − P̂_{t+h}, par modèle."""
    A = actual_prices(panel, orig)
    return {fc["name"]: A - price_forecast(panel, orig, fc) for fc in fcs}


def metrics_table(panel, orig, fcs: list, hs=EVAL_H) -> pd.DataFrame:
    """Tableau unique : MSE, RMSE, MAE (en $) et MAPE (en %) sur le prix, pour chaque horizon."""
    A = actual_prices(panel, orig)
    E = errors(panel, orig, fcs)
    rows = {}
    for name, e in E.items():
        row = {}
        for h in hs:
            ok = ~np.isnan(A[:, h - 1])
            eh, ah = e[ok, h - 1], A[ok, h - 1]
            row[(f"h = {h}", "MSE")] = np.mean(eh ** 2)
            row[(f"h = {h}", "RMSE")] = np.sqrt(np.mean(eh ** 2))
            row[(f"h = {h}", "MAE")] = np.mean(np.abs(eh))
            row[(f"h = {h}", "MAPE (%)")] = 100 * np.mean(np.abs(eh) / ah)
        rows[name] = row
    df = pd.DataFrame(rows).T
    df.columns = pd.MultiIndex.from_tuples(df.columns)
    df.index.name = "modèle"
    return df


def interval_table(panel, orig, fcs: list, hs=EVAL_H) -> pd.DataFrame:
    """Couverture empirique et largeur moyenne des intervalles à 95 %.

    Test binomial de la couverture (H₀ : 95 %) à h = 1 seulement : à h > 1, les
    intervalles se chevauchent d'une origine à l'autre, les dépassements sont
    autocorrélés et le test binomial n'est plus valide.
    """
    A = actual_prices(panel, orig)
    rows = []
    for fc in fcs:
        if fc["lo"] is None:
            continue
        lo, hi = price_forecast(panel, orig, fc, "lo"), price_forecast(panel, orig, fc, "hi")
        row = {"modèle": fc["name"]}
        for h in hs:
            ok = ~np.isnan(A[:, h - 1])
            hit = (A[ok, h - 1] >= lo[ok, h - 1]) & (A[ok, h - 1] <= hi[ok, h - 1])
            row[f"couverture h = {h} (%)"] = 100 * hit.mean()
            row[f"largeur moyenne h = {h} ($)"] = np.mean(hi[ok, h - 1] - lo[ok, h - 1])
            if h == 1:
                row["n (h = 1)"] = int(ok.sum())
                row["p binomial h = 1"] = stats.binomtest(int(hit.sum()), int(ok.sum()), LEVEL).pvalue
        rows.append(row)
    return pd.DataFrame(rows).set_index("modèle")


# ---------------------------------------------------------------------------
# Diebold-Mariano
# ---------------------------------------------------------------------------

def dm_from_loss(d: np.ndarray, h: int) -> dict:
    """Test de Diebold-Mariano sur une série de différences de pertes d_t = L1_t − L2_t.

    H₀ : E[d_t] = 0 (même précision). Variance de la moyenne : autocovariances jusqu'au
    retard h − 1 (des prévisions à h pas se chevauchent, donc leurs erreurs sont
    autocorrélées jusqu'à l'ordre h − 1), divisées par n. Si cette variance est négative,
    on revient à h = 1, comme `forecast::dm.test`. Correction HLN, loi de Student à n − 1 ddl.
    Statistique < 0 : le modèle 1 a une perte moyenne plus faible.
    """
    d = np.asarray(d, float)
    d = d[~np.isnan(d)]
    n = len(d)
    if n < 2 or np.allclose(d, 0):
        return {"n": n, "DM": np.nan, "p-value": np.nan, "repli h = 1": False}
    dc = d - d.mean()
    gam = np.array([np.sum(dc[k:] * dc[:n - k]) / n for k in range(h)])
    v = (gam[0] + 2 * gam[1:].sum()) / n
    if v <= 0:
        # Comme forecast::dm.test : tout le test (variance ET correction HLN) est refait avec h = 1.
        return {**dm_from_loss(d, 1), "repli h = 1": True}
    stat = d.mean() / np.sqrt(v)
    stat *= np.sqrt((n + 1 - 2 * h + h * (h - 1) / n) / n)
    return {"n": n, "DM": stat, "p-value": 2 * stats.t.sf(abs(stat), n - 1), "repli h = 1": False}


def dm_test(e1: np.ndarray, e2: np.ndarray, h: int, power: int = 2) -> dict:
    """Diebold-Mariano sur des erreurs de prévision, perte |e|^power (quadratique par défaut)."""
    return dm_from_loss(np.abs(e1) ** power - np.abs(e2) ** power, h)


def dm_vs_baseline(E: dict, baseline: str, hs=EVAL_H, alpha: float = 0.05) -> pd.DataFrame:
    """Chaque modèle contre la baseline, perte quadratique sur le prix, pour chaque horizon."""
    rows = []
    for name, e in E.items():
        if name == baseline:
            continue
        for h in hs:
            res = dm_test(e[:, h - 1], E[baseline][:, h - 1], h)
            if np.isnan(res["DM"]):
                verdict = "prévisions identiques à la baseline"
            elif res["p-value"] >= alpha:
                verdict = "pas de différence significative"
            else:
                verdict = "significativement meilleur" if res["DM"] < 0 else "significativement moins bon"
            rows.append({"modèle": name, "h": h, **res, "verdict (5 %)": verdict})
    return pd.DataFrame(rows).set_index(["modèle", "h"])


def dm_pvalue_matrix(E: dict, baseline: str) -> pd.DataFrame:
    """p-values de Diebold-Mariano contre la baseline pour h = 1 … 10 (lignes : modèles)."""
    return pd.DataFrame({h: {n: dm_test(e[:, h - 1], E[baseline][:, h - 1], h)["p-value"]
                             for n, e in E.items() if n != baseline} for h in HS})


# ---------------------------------------------------------------------------
# Variance prévue (GARCH) face à r²
# ---------------------------------------------------------------------------

def variance_benchmarks(panel: pd.DataFrame, orig: np.ndarray, lam: float = 0.94) -> dict:
    """Prévisions de variance à 1 jour concurrentes, connues en t.

    - fenêtre de 21 jours : variance réalisée du dernier mois ;
    - EWMA (RiskMetrics, λ = 0,94) : moyenne exponentielle des r², initialisée sur le train.
    """
    r = panel["XOM_ret"].to_numpy()
    v21 = (panel["XOM_vol21"].to_numpy() / np.sqrt(_cfg["features"]["annualization"])) ** 2
    ew = np.empty(len(r))
    ew[1] = r[1] ** 2
    for t in range(2, len(r)):
        ew[t] = lam * ew[t - 1] + (1 - lam) * r[t] ** 2
    return {"Volatilité réalisée 21 jours": v21[orig], "EWMA (λ = 0,94)": ew[orig]}


def variance_eval(panel: pd.DataFrame, orig: np.ndarray, var_fc: dict, reference: str) -> pd.DataFrame:
    """Compare des prévisions de variance à 1 jour à r²_{t+1}.

    QLIKE = ln σ̂² + r²/σ̂² (forme de Patton, 2011, robuste au bruit de r² comme mesure
    de la variance) et MSE = (r² − σ̂²)². Diebold-Mariano (h = 1) contre `reference`.
    """
    r_next = panel["XOM_ret"].to_numpy()[orig + 1]
    y = r_next ** 2
    losses = {n: (np.log(s) + y / s, (y - s) ** 2) for n, s in var_fc.items()}
    rows = []
    for n, (ql, ms) in losses.items():
        row = {"prévision de variance": n, "QLIKE moyen": ql.mean(), "MSE moyen": ms.mean()}
        if n != reference:
            dq = dm_from_loss(ql - losses[reference][0], 1)
            dm = dm_from_loss(ms - losses[reference][1], 1)
            row.update({"DM QLIKE": dq["DM"], "p QLIKE": dq["p-value"], "DM MSE": dm["DM"], "p MSE": dm["p-value"]})
        rows.append(row)
    return pd.DataFrame(rows).set_index("prévision de variance")


# ---------------------------------------------------------------------------
# Prévision opérationnelle depuis la dernière date disponible
# ---------------------------------------------------------------------------

def forecast_from_last(panel: pd.DataFrame, sims: int = 20000, seed: int | None = None):
    """Prévision du modèle final (marche aléatoire + GJR-GARCH-t) depuis la dernière date de l'échantillon.

    Le GARCH est ré-estimé sur toutes les données (train + test), comme on le ferait en
    pratique le jour de la décision. Sert d'entrée au prompt 3 (recommandations simulées).
    """
    from arch.univariate import GARCH, StudentsT, ZeroMean

    from src.classical import fit_garch

    seed = _cfg["seed"] if seed is None else seed
    r = panel["XOM_ret"].to_numpy()[1:]
    res = fit_garch(pd.Series(r), o=1, dist="t")
    fixed = ZeroMean(r, volatility=GARCH(1, 1, 1), distribution=StudentsT(seed=seed), rescale=False).fix(res.params)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        fc = fixed.forecast(horizon=HORIZON, start=len(r) - 1, method="simulation", simulations=sims, reindex=False)
    cum = np.cumsum(fc.simulations.values[0], axis=1) / 100       # (trajectoires, horizon)
    p0 = float(panel["XOM_price"].iloc[-1])
    ann = _cfg["features"]["annualization"]
    tab = pd.DataFrame({
        "h": HS,
        "prévision du prix ($)": p0,
        f"borne basse IC {LEVEL:.0%} ($)": p0 * np.exp(np.quantile(cum, 0.5 - LEVEL / 2, axis=0)),
        f"borne haute IC {LEVEL:.0%} ($)": p0 * np.exp(np.quantile(cum, 0.5 + LEVEL / 2, axis=0)),
        "volatilité prévue du jour h (annualisée, %)": np.sqrt(fc.variance.values[0] * ann),
    }).set_index("h")
    return tab, res
