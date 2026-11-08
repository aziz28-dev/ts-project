"""Phase 2 : analyse exploratoire (cahier §2) — statistiques, ACF/PACF, STL, outliers, stationnarité."""

from __future__ import annotations

import warnings

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from statsmodels.stats.diagnostic import acorr_ljungbox
from statsmodels.tools.sm_exceptions import InterpolationWarning
from statsmodels.tsa.seasonal import STL
from statsmodels.tsa.stattools import acf, adfuller, kpss, pacf

from src.utils import load_config

ALPHA = 0.05


# ---------------------------------------------------------------------------
# Statistiques descriptives
# ---------------------------------------------------------------------------

def descriptive_stats(df: pd.DataFrame) -> pd.DataFrame:
    """Moments et test de Jarque-Bera de chaque colonne (rendements en %).

    La kurtosis rapportée est l'excès de kurtosis (0 pour une loi normale) :
    c'est la mesure directe des queues épaisses qui motivent la loi de Student en GARCH.
    """
    rows = {}
    for col in df.columns:
        x = df[col].dropna()
        jb = stats.jarque_bera(x)
        rows[col] = {
            "n": len(x),
            "moyenne": x.mean(),
            "écart-type": x.std(),
            "variance": x.var(),
            "skewness": stats.skew(x),
            "excès de kurtosis": stats.kurtosis(x),  # Fisher : normale = 0
            "min": x.min(),
            "max": x.max(),
            "Jarque-Bera": jb.statistic,
            "p-value JB": jb.pvalue,
        }
    return pd.DataFrame(rows)


def mean_test(r: pd.Series) -> pd.DataFrame:
    """Test H0 : moyenne nulle, avec écart-type classique puis robuste HAC (Newey-West).

    L'écart-type classique suppose des rendements i.i.d. ; or ils sont hétéroscédastiques
    (et faiblement autocorrélés). Le HAC corrige les deux. Nombre de retards :
    règle usuelle floor(4 (n/100)^(2/9)).
    """
    import statsmodels.api as sm

    r = r.dropna()
    n = len(r)
    lags = int(np.floor(4 * (n / 100) ** (2 / 9)))
    model = sm.OLS(r.to_numpy(), np.ones(n))
    rows = {}
    for label, fit in {
        "classique (i.i.d.)": model.fit(),
        f"HAC Newey-West ({lags} retards)": model.fit(cov_type="HAC", cov_kwds={"maxlags": lags}),
    }.items():
        rows[label] = {"moyenne": fit.params[0], "écart-type": fit.bse[0],
                       "statistique t": fit.tvalues[0], "p-value": fit.pvalues[0]}
    return pd.DataFrame(rows).T


# ---------------------------------------------------------------------------
# Autocorrélations
# ---------------------------------------------------------------------------

def plot_acf_pacf(series: dict[str, pd.Series], lags: int, title: str):
    """ACF (gauche) et PACF (droite), une ligne par série, bande de confiance à 95 %."""
    fig, axes = plt.subplots(len(series), 2, figsize=(13, 3.2 * len(series)), squeeze=False)
    for row, (name, x) in zip(axes, series.items()):
        x = x.dropna()
        plot_acf(x, lags=lags, ax=row[0], zero=False, alpha=ALPHA)
        # Méthode "ywm" : stable même quand la série est proche d'une racine unitaire.
        plot_pacf(x, lags=lags, ax=row[1], zero=False, alpha=ALPHA, method="ywm")
        row[0].set_title(f"ACF — {name}")
        row[1].set_title(f"PACF — {name}")
        for ax in row:
            ax.set_xlabel("retard (jours de bourse)")
            ax.grid(alpha=0.3)
    fig.suptitle(title, y=1.0)
    fig.tight_layout()
    return fig


def ljungbox_robustness(r: pd.Series, lags=(5, 10, 20), vol_window: int = 21) -> pd.DataFrame:
    """Ljung-Box sur trois versions des rendements, pour savoir d'où vient un éventuel rejet.

    Le test de Ljung-Box suppose une variance constante. Sous hétéroscédasticité
    (regroupement de volatilité), il rejette trop souvent : on le refait donc sur
    les rendements divisés par leur volatilité passée (shift(1) : pas de fuite)
    et sur l'échantillon privé de 2020. Si le rejet disparaît, l'autocorrélation
    apparente venait de la variance, pas de la moyenne.
    """
    r = r.dropna()
    versions = {
        "rendements bruts": r,
        f"standardisés par la vol. passée ({vol_window} j)": (r / r.rolling(vol_window).std().shift(1)).dropna(),
        "hors année 2020": r[r.index.year != 2020],
    }
    out = {name: acorr_ljungbox(x, lags=list(lags))["lb_pvalue"].to_numpy() for name, x in versions.items()}
    return pd.DataFrame(out, index=[f"p-value Q({k})" for k in lags]).T


def weekday_effect(r: pd.Series) -> dict:
    """Effet jour de la semaine (saisonnalité s = 5) sur la moyenne et la variance.

    Kruskal-Wallis plutôt qu'ANOVA pour la moyenne : il ne suppose pas la normalité,
    clairement rejetée par Jarque-Bera. Levene (centré sur la médiane) pour la variance.
    """
    r = r.dropna()
    groups = [g.to_numpy() for _, g in r.groupby(r.index.dayofweek)]
    kw, lev = stats.kruskal(*groups), stats.levene(*groups)
    table = r.groupby(r.index.dayofweek).agg(["mean", "std", "count"])
    table.index = ["lundi", "mardi", "mercredi", "jeudi", "vendredi"][: len(table)]
    return {"table": table, "Kruskal-Wallis stat": kw.statistic, "Kruskal-Wallis p": kw.pvalue,
            "Levene stat": lev.statistic, "Levene p": lev.pvalue}


def acf_summary(x: pd.Series, lags: int, show=(1, 2, 5, 10, 21)) -> dict:
    """Valeurs chiffrées qui servent à écrire l'interprétation des graphes ACF/PACF.

    La bande ±1,96/√n est la bande de bruit blanc : un retard qui en sort est
    significatif à 5 %. Sur 40 retards, environ 2 sortent par pur hasard.
    """
    x = x.dropna()
    n = len(x)
    band = 1.96 / np.sqrt(n)
    a = acf(x, nlags=lags, fft=True)[1:]
    p = pacf(x, nlags=lags, method="ywm")[1:]
    lb = acorr_ljungbox(x, lags=[10, 20], return_df=True)
    return {
        "n": n,
        "bande 95 %": band,
        **{f"ACF({k})": a[k - 1] for k in show},
        **{f"PACF({k})": p[k - 1] for k in show},
        "nb retards ACF hors bande": int((np.abs(a) > band).sum()),
        "retards ACF hors bande": [k + 1 for k in np.flatnonzero(np.abs(a) > band)][:15],
        "nb retards PACF hors bande": int((np.abs(p) > band).sum()),
        "retards PACF hors bande": [k + 1 for k in np.flatnonzero(np.abs(p) > band)][:15],
        "Ljung-Box Q(10)": lb.loc[10, "lb_stat"],
        "p-value Q(10)": lb.loc[10, "lb_pvalue"],
        "Ljung-Box Q(20)": lb.loc[20, "lb_stat"],
        "p-value Q(20)": lb.loc[20, "lb_pvalue"],
    }


# ---------------------------------------------------------------------------
# Décomposition STL
# ---------------------------------------------------------------------------

def stl_decompose(x: pd.Series, period: int):
    """STL robuste : résistante aux chocs de 2020 qui fausseraient une décomposition classique."""
    # Index positionnel : STL exige une période entière en nombre d'observations,
    # et le calendrier boursier n'a pas de fréquence pandas régulière.
    res = STL(x.dropna().to_numpy(), period=period, robust=True).fit()
    idx = x.dropna().index
    comp = pd.DataFrame({"observé": res.observed, "tendance": res.trend,
                         "saisonnier": res.seasonal, "résidu": res.resid}, index=idx)
    return comp


def stl_strength(comp: pd.DataFrame) -> dict:
    """Force de la tendance et de la saisonnalité (Wang, Smith & Hyndman 2006).

    F = max(0, 1 - Var(résidu) / Var(composante + résidu)) : 0 = composante
    inexistante, 1 = composante dominante. Chiffre objectif pour juger la saisonnalité.
    """
    r, t, s = comp["résidu"], comp["tendance"], comp["saisonnier"]
    return {
        "force tendance F_T": max(0.0, 1 - r.var() / (t + r).var()),
        "force saisonnalité F_S": max(0.0, 1 - r.var() / (s + r).var()),
        "amplitude saisonnière (max - min)": s.max() - s.min(),
        "écart-type résidu": r.std(),
    }


def plot_stl(comp: pd.DataFrame, title: str):
    fig, axes = plt.subplots(4, 1, figsize=(12, 8), sharex=True)
    for ax, col in zip(axes, comp.columns):
        ax.plot(comp.index, comp[col], lw=0.8, color="tab:blue" if col != "résidu" else "tab:gray")
        ax.set_ylabel(col)
        ax.grid(alpha=0.3)
    axes[0].set_title(title)
    fig.tight_layout()
    return fig


# ---------------------------------------------------------------------------
# Valeurs aberrantes
# ---------------------------------------------------------------------------

def detect_outliers(r: pd.Series, window: int | None = None, k: float | None = None) -> pd.DataFrame:
    """Repère les rendements extrêmes par IQR glissant.

    Les quartiles sont calculés sur les `window` jours PRÉCÉDENTS (shift(1)) :
    le jour testé n'influence pas son propre seuil, et la règle n'utilise que
    le passé, donc elle est applicable telle quelle en prévision.
    Une règle glissante s'adapte au régime de volatilité : un mouvement de 4 %
    est banal en mars 2020 mais exceptionnel en 2017.
    """
    f = load_config()["features"]
    window = f["outlier_window"] if window is None else window
    k = f["outlier_iqr_k"] if k is None else k
    q1 = r.rolling(window).quantile(0.25).shift(1)
    q3 = r.rolling(window).quantile(0.75).shift(1)
    iqr = q3 - q1
    low, high = q1 - k * iqr, q3 + k * iqr
    flag = (r < low) | (r > high)
    return pd.DataFrame({"rendement": r, "borne basse": low, "borne haute": high,
                         "outlier": flag.astype(int)})


def outlier_sensitivity(r: pd.Series, test_index: pd.Index, windows=(21, 63, 126, 252),
                        ks=(2.0, 2.5, 3.0, 3.5), core_share: float = 0.75):
    """Sensibilité de la détection au couple (fenêtre, k).

    Renvoie (grille, noyau) : la grille donne, pour chaque réglage, le nombre de jours
    signalés et combien de jours du réglage de référence (config.yaml) il retrouve ;
    le noyau liste les jours signalés par au moins `core_share` des réglages, donc
    indépendants d'un choix de paramètre particulier.
    """
    ref = detect_outliers(r)["outlier"]
    flags, rows = {}, []
    for w in windows:
        for k in ks:
            o = detect_outliers(r, window=w, k=k)["outlier"]
            flags[(w, k)] = o
            rows.append({"fenêtre": w, "k": k, "total": int(o.sum()),
                         "dont 2020": int(o[o.index.year == 2020].sum()),
                         "dont test": int(o.loc[test_index].sum()),
                         "jours de la référence retrouvés": int((o & ref).sum())})
    grid = pd.DataFrame(rows).set_index(["fenêtre", "k"])
    freq = pd.concat(flags, axis=1).sum(axis=1)
    n_cfg = len(flags)
    core = freq[freq >= core_share * n_cfg]
    core = pd.DataFrame({"rendement": r.loc[core.index], "réglages qui le signalent": core.astype(int),
                         "dans la référence": ref.loc[core.index].astype(bool)})
    return grid, core


# ---------------------------------------------------------------------------
# Stationnarité : ADF et KPSS
# ---------------------------------------------------------------------------

_SPEC = {"c": "constante", "ct": "constante + tendance"}


def adf_test(x: pd.Series, regression: str = "c") -> dict:
    """ADF, H0 : racine unitaire. Retards choisis par AIC pour blanchir les résidus du test."""
    stat, p, lags, nobs, crit, _ = adfuller(x.dropna(), regression=regression, autolag="AIC")
    return {"test": "ADF", "H0": "racine unitaire (non stationnaire)", "spécification": _SPEC[regression],
            "retards": lags, "n": nobs, "statistique": stat, "valeur critique 5 %": crit["5%"],
            "p-value": p, "p-value affichée": f"{p:.4f}", "H0 rejetée (5 %)": p < ALPHA}


def kpss_test(x: pd.Series, regression: str = "c") -> dict:
    """KPSS, H0 : stationnarité (autour d'une constante, ou d'une tendance si 'ct').

    statsmodels interpole la p-value dans une table bornée à [0,01 ; 0,10] :
    hors de cet intervalle on affiche « < 0,01 » ou « > 0,10 » plutôt qu'une
    fausse valeur exacte. La décision se prend sur la statistique vs la valeur critique.
    """
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always", InterpolationWarning)
        stat, p, lags, crit = kpss(x.dropna(), regression=regression, nlags="auto")
    bounded = any(issubclass(m.category, InterpolationWarning) for m in w)
    shown = ("< 0.01" if p <= 0.01 else "> 0.10") if bounded else f"{p:.4f}"
    return {"test": "KPSS", "H0": "stationnaire" + (" autour d'une tendance" if regression == "ct" else ""),
            "spécification": _SPEC[regression], "retards": lags, "n": len(x.dropna()),
            "statistique": stat, "valeur critique 5 %": crit["5%"], "p-value": p,
            "p-value affichée": shown, "H0 rejetée (5 %)": stat > crit["5%"]}


def zivot_andrews_table(series: dict[str, pd.Series], regressions=("c", "ct")) -> pd.DataFrame:
    """Zivot-Andrews, H0 : racine unitaire SANS rupture ; H1 : stationnaire avec UNE rupture à date inconnue.

    Contrôle de robustesse : en présence d'une rupture structurelle (krach de 2020),
    l'ADF a tendance à ne pas rejeter à tort la racine unitaire (Perron, 1989).
    """
    from statsmodels.tsa.stattools import zivot_andrews

    labels = {"c": "rupture de niveau", "ct": "rupture de niveau et de pente"}
    rows = []
    for name, x in series.items():
        x = x.dropna()
        for reg in regressions:
            stat, p, crit, lags, bp = zivot_andrews(x.to_numpy(), regression=reg, autolag="AIC")
            rows.append({"série": name, "spécification": labels[reg], "statistique": stat,
                         "valeur critique 5 %": crit["5%"], "p-value": p, "retards": lags,
                         "date de rupture estimée": x.index[bp].date(), "H0 rejetée (5 %)": p < ALPHA})
    return pd.DataFrame(rows).set_index(["série", "spécification"])


def joint_conclusion(adf_rejects: bool, kpss_rejects: bool) -> str:
    """Croisement ADF/KPSS du plan (§2) : les hypothèses nulles sont opposées."""
    return {
        (True, False): "stationnaire",
        (False, True): "non stationnaire : différencier",
        (True, True): "contradictoire : à discuter",
        (False, False): "peu informatif : à discuter",
    }[(adf_rejects, kpss_rejects)]


def stationarity_table(series: dict[str, pd.Series], regressions=("c", "ct")) -> pd.DataFrame:
    """ADF et KPSS, même spécification, pour chaque série : une ligne par (série, spécification)."""
    rows = []
    for name, x in series.items():
        for reg in regressions:
            a, k = adf_test(x, reg), kpss_test(x, reg)
            rows.append({
                "série": name, "spécification": _SPEC[reg],
                "ADF stat": a["statistique"], "ADF VC 5 %": a["valeur critique 5 %"],
                "ADF retards": a["retards"], "ADF p": a["p-value affichée"],
                "ADF rejette H0": a["H0 rejetée (5 %)"],
                "KPSS stat": k["statistique"], "KPSS VC 5 %": k["valeur critique 5 %"],
                "KPSS retards": k["retards"], "KPSS p": k["p-value affichée"],
                "KPSS rejette H0": k["H0 rejetée (5 %)"],
                "conclusion": joint_conclusion(a["H0 rejetée (5 %)"], k["H0 rejetée (5 %)"]),
            })
    return pd.DataFrame(rows).set_index(["série", "spécification"])
