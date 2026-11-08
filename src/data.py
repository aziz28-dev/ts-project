"""Phase 1 : téléchargement, cache, alignement, variables dérivées et split (cahier §1)."""

from __future__ import annotations

import numpy as np
import pandas as pd

from src.utils import load_config, path

RAW_COLUMNS = ["Open", "High", "Low", "Close", "Adj Close", "Volume"]


# ---------------------------------------------------------------------------
# Téléchargement et cache
# ---------------------------------------------------------------------------

def _cache_file(ticker: str):
    # "BZ=F" -> "BZ_F.csv" : le signe "=" est mal géré par certains outils.
    return path("raw") / f"{ticker.replace('=', '_')}.csv"


def download_ticker(ticker: str, refresh: bool = False) -> pd.DataFrame:
    """Renvoie les cours journaliers bruts d'un ticker, depuis le cache CSV si présent.

    Le cache passe avant le téléchargement : Yahoo recalcule l'Adj Close
    rétroactivement à chaque dividende, donc seul un fichier figé garantit
    des résultats identiques d'une exécution (ou d'une machine) à l'autre.
    """
    cache = _cache_file(ticker)
    if cache.exists() and not refresh:
        return pd.read_csv(cache, index_col="Date", parse_dates=True)

    cfg = load_config()["data"]
    import yfinance as yf

    # end est exclusive dans yfinance : +1 jour pour inclure la date de fin de config.yaml.
    end = (pd.Timestamp(cfg["end"]) + pd.Timedelta(days=1)).strftime("%Y-%m-%d")
    try:
        df = yf.download(ticker, start=cfg["start"], end=end, auto_adjust=False,
                         progress=False, actions=False)
    except Exception as exc:  # réseau coupé, API Yahoo modifiée...
        raise RuntimeError(f"Téléchargement de {ticker} impossible et pas de cache {cache}") from exc
    if df.empty:
        raise RuntimeError(f"Yahoo n'a renvoyé aucune donnée pour {ticker} (et pas de cache)")

    # yfinance renvoie des colonnes MultiIndex (champ, ticker) : on garde le champ seul.
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    df = df[RAW_COLUMNS]
    df.index = pd.DatetimeIndex(df.index).tz_localize(None).normalize()
    df.index.name = "Date"
    df.to_csv(cache)
    return df


def load_raw(refresh: bool = False) -> dict[str, pd.DataFrame]:
    """Cours bruts des trois tickers de config.yaml, clés = rôle (target, sector, exogenous)."""
    tickers = load_config()["data"]["tickers"]
    return {role: download_ticker(t, refresh) for role, t in tickers.items()}


# ---------------------------------------------------------------------------
# Alignement et contrôle des manquants
# ---------------------------------------------------------------------------

def missing_report(raw: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Bilan des manquants par ticker : NaN, période couverte, dates absentes du calendrier XOM/XLE."""
    tickers = load_config()["data"]["tickers"]
    col = load_config()["data"]["price_column"]
    common = raw["target"].index.intersection(raw["sector"].index)
    rows = []
    for role, df in raw.items():
        rows.append({
            "rôle": role,
            "ticker": tickers[role],
            "début": df.index.min().date(),
            "fin": df.index.max().date(),
            "observations": len(df),
            f"NaN {col}": int(df[col].isna().sum()),
            "NaN toutes colonnes": int(df.isna().sum().sum()),
            "dates dupliquées": int(df.index.duplicated().sum()),
            "jours communs XOM/XLE absents": len(common.difference(df.index)),
            "jours en plus du calendrier commun": len(df.index.difference(common)),
        })
    return pd.DataFrame(rows).set_index("rôle")


def align_prices(raw: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Panel des prix ajustés sur le calendrier commun XOM/XLE.

    Jointure interne XOM/XLE : on ne garde que les jours où les deux actifs cotent.
    Le Brent (contrat à terme ICE, autre calendrier) est rattaché par jointure à
    gauche SANS ffill : un trou reste NaN plutôt que de créer un rendement nul fictif.
    """
    cfg = load_config()["data"]
    col, t = cfg["price_column"], cfg["tickers"]
    core = pd.concat({t["target"]: raw["target"][col], t["sector"]: raw["sector"][col]},
                     axis=1, join="inner")
    prices = core.join(raw["exogenous"][col].rename(t["exogenous"]), how="left")
    prices.index.name = "Date"
    return prices.sort_index()


# ---------------------------------------------------------------------------
# Variables dérivées
# ---------------------------------------------------------------------------

def build_features(prices: pd.DataFrame) -> pd.DataFrame:
    """Ajoute log-prix, log-rendement en %, volatilité réalisée et moyenne mobile.

    Toutes les fenêtres sont glissantes vers le passé : la valeur en t n'utilise
    que des données jusqu'à t, donc aucune fuite du test vers le train.
    """
    f = load_config()["features"]
    out = {}
    for tk in prices.columns:
        p = prices[tk]
        # Log-prix : rend la tendance additive et sert à la cointégration (séries I(1)).
        out[f"{tk}_price"] = p
        out[f"{tk}_logp"] = np.log(p)
        # Rendement log en % : variable stationnaire attendue pour VAR/GARCH, en % pour la lisibilité.
        out[f"{tk}_ret"] = 100 * np.log(p).diff()
        # Volatilité réalisée annualisée : indicateur technique exigé (cahier §1.1).
        out[f"{tk}_vol21"] = (np.sqrt(f["annualization"])
                              * out[f"{tk}_ret"].rolling(f["realized_vol_window"]).std())
        out[f"{tk}_ma50"] = p.rolling(f["moving_average_window"]).mean()
    return pd.DataFrame(out, index=prices.index)


def variables_table() -> pd.DataFrame:
    """Tableau des variables du rapport (nom, définition, unité)."""
    cfg = load_config()
    f, t = cfg["features"], cfg["data"]["tickers"]
    # Un contrat à terme ne verse pas de dividende : son Adj Close est le cours brut.
    price_def = {
        "target": f"Prix de clôture ajusté (dividendes, splits) de {t['target']}",
        "sector": f"Prix de clôture ajusté (dividendes, splits) de {t['sector']}",
        "exogenous": f"Cours de clôture du contrat à terme Brent {t['exogenous']} (échéance la plus proche, sans ajustement)",
    }
    rows = []
    for role, tk in t.items():
        rows += [
            (f"{tk}_price", price_def[role], "USD" if role != "exogenous" else "USD/baril"),
            (f"{tk}_logp", f"Log-prix l_t = ln(P_t)", "log(USD)"),
            (f"{tk}_ret", "Log-rendement r_t = 100 × ln(P_t / P_{t-1})", "%"),
            (f"{tk}_vol21", f"Volatilité réalisée : √{f['annualization']} × écart-type glissant "
                            f"de r_t sur {f['realized_vol_window']} jours", "% annualisé"),
            (f"{tk}_ma50", f"Moyenne mobile de P_t sur {f['moving_average_window']} jours", "USD"),
        ]
    df = pd.DataFrame(rows, columns=["variable", "définition", "unité"])
    df.insert(1, "rôle", [r for r in t for _ in range(5)])
    return df


# ---------------------------------------------------------------------------
# Split chronologique
# ---------------------------------------------------------------------------

def train_test_split_time(df: pd.DataFrame, ratio: float | None = None):
    """Coupure chronologique : les premiers 90 % des dates en train, la suite en test.

    Jamais de tirage aléatoire : le test doit être strictement postérieur au train,
    comme en situation réelle de prévision.
    """
    ratio = load_config()["split"]["train_ratio"] if ratio is None else ratio
    n_train = int(np.floor(ratio * len(df)))
    return df.iloc[:n_train], df.iloc[n_train:]


# ---------------------------------------------------------------------------
# Pipeline complet
# ---------------------------------------------------------------------------

def prepare(refresh: bool = False, save: bool = True):
    """Exécute toute la phase 1 et renvoie (raw, panel, train, test)."""
    raw = load_raw(refresh)
    panel = build_features(align_prices(raw))
    train, test = train_test_split_time(panel)
    if save:
        out = path("processed")
        panel.to_csv(out / "panel.csv")
        train.to_csv(out / "train.csv")
        test.to_csv(out / "test.csv")
    return raw, panel, train, test
