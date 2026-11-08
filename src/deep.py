"""Section 4 : réseaux récurrents (LSTM, GRU) et hybride ARIMA + LSTM — Python uniquement.

Principes (cahier §4.1, plan phase 4) :
- cible : les 10 log-rendements futurs de XOM, en sortie directe (un vecteur de 10
  valeurs), jamais le prix brut (un réseau extrapole mal hors de la plage vue au train) ;
- entrées : fenêtres glissantes de rendements XOM et XLE et de volatilité réalisée ;
- normalisation ajustée sur la partie d'apprentissage seulement, à chaque fold ;
- validation croisée temporelle (walk-forward, fenêtre croissante), jamais de k-fold ;
- un écart (gap) de h = 10 jours sépare toujours apprentissage et évaluation : la cible
  d'une fenêtre d'apprentissage couvre les 10 jours suivants, qui ne doivent pas
  chevaucher la période évaluée.
"""

from __future__ import annotations

import os
import time

os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "3")

import numpy as np
import pandas as pd

from src.utils import load_config

HORIZON = load_config()["forecast"]["horizon"]
FEATURES = ["XOM_ret", "XLE_ret", "XOM_vol21"]


# ---------------------------------------------------------------------------
# Données : fenêtres glissantes
# ---------------------------------------------------------------------------

def make_windows(panel: pd.DataFrame, window: int, features=FEATURES, target: str = "XOM_ret",
                 horizon: int = HORIZON):
    """Construit X (n, window, n_features), Y (n, horizon) et la date d'origine de chaque échantillon.

    Pour une origine t : X = features des jours t−window+1 … t ; Y = rendements de t+1 … t+h.
    Seules les origines dont la fenêtre ne contient aucun NaN sont gardées (début de
    série : rendement du premier jour, volatilité des 21 premiers jours). Les origines
    dont l'horizon dépasse la fin des données ont un Y partiellement NaN : elles ne
    servent qu'à la prévision, jamais à l'apprentissage.
    """
    F = panel[list(features)].to_numpy(dtype="float32")
    r = panel[target].to_numpy(dtype="float32")
    n = len(panel)
    X, Y, origins = [], [], []
    for t in range(window - 1, n):
        x = F[t - window + 1: t + 1]
        if np.isnan(x).any():
            continue
        y = np.full(horizon, np.nan, dtype="float32")
        k = min(horizon, n - 1 - t)
        y[:k] = r[t + 1: t + 1 + k]
        X.append(x)
        Y.append(y)
        origins.append(panel.index[t])
    return np.stack(X), np.stack(Y), pd.DatetimeIndex(origins)


class Scaler:
    """Standardisation ajustée sur l'apprentissage seulement (moyenne et écart-type par variable)."""

    def fit(self, X: np.ndarray, Y: np.ndarray):
        flat = X.reshape(-1, X.shape[-1])
        self.mx, self.sx = flat.mean(axis=0), flat.std(axis=0)
        self.my, self.sy = float(np.nanmean(Y)), float(np.nanstd(Y))
        return self

    def tx(self, X):
        return (X - self.mx) / self.sx

    def ty(self, Y):
        return (Y - self.my) / self.sy

    def inv_y(self, Ys):
        return Ys * self.sy + self.my


# ---------------------------------------------------------------------------
# Modèles
# ---------------------------------------------------------------------------

def set_all_seeds(seed: int):
    """Seed Python, NumPy et TensorFlow + opérations déterministes : deux entraînements
    avec la même seed donnent exactement les mêmes poids."""
    import tensorflow as tf
    import keras

    keras.utils.set_random_seed(seed)
    tf.config.experimental.enable_op_determinism()
    # Avertissements de « retracing » : sans effet sur les résultats (prédictions sur des
    # tableaux de tailles différentes d'un fold à l'autre), masqués pour garder les sorties lisibles.
    tf.get_logger().setLevel("ERROR")


def build_model(kind: str, window: int, n_features: int, units: int, dropout: float,
                horizon: int = HORIZON, lr: float = 1e-3):
    """Une couche récurrente (LSTM ou GRU), dropout, puis une couche dense de sortie à h valeurs.

    Une seule couche récurrente : avec ~2 000 échantillons et un signal très faible
    (rendements ≈ bruit blanc, §2.3), une architecture plus profonde ne ferait
    qu'augmenter le sur-apprentissage.
    """
    import keras

    layer = {"LSTM": keras.layers.LSTM, "GRU": keras.layers.GRU}[kind]
    model = keras.Sequential([
        keras.Input((window, n_features)),
        layer(units),
        keras.layers.Dropout(dropout),
        keras.layers.Dense(horizon),
    ])
    model.compile(optimizer=keras.optimizers.Adam(learning_rate=lr), loss="mse")
    return model


def train(kind: str, cfg: dict, X_tr, Y_tr, seed: int, val_ratio: float, patience: int,
          max_epochs: int = 100, batch_size: int = 64, horizon: int = HORIZON):
    """Entraîne avec early stopping sur les derniers `val_ratio` % de l'apprentissage (ordre chronologique).

    Un écart de h échantillons sépare la fin de l'apprentissage effectif du début de la
    validation (mêmes raisons que le gap du walk-forward). Les poids retenus sont ceux
    de la meilleure époque de validation.
    Renvoie (modèle, scaler, historique, nb d'époques).
    """
    import keras

    set_all_seeds(seed)
    n = len(X_tr)
    n_val = max(int(round(val_ratio * n)), 1)
    fit_end = n - n_val - horizon
    Xf, Yf, Xv, Yv = X_tr[:fit_end], Y_tr[:fit_end], X_tr[n - n_val:], Y_tr[n - n_val:]
    sc = Scaler().fit(Xf, Yf)
    model = build_model(kind, X_tr.shape[1], X_tr.shape[2], cfg["units"], cfg["dropout"], horizon)
    es = keras.callbacks.EarlyStopping(monitor="val_loss", patience=patience, restore_best_weights=True)
    hist = model.fit(sc.tx(Xf), sc.ty(Yf), validation_data=(sc.tx(Xv), sc.ty(Yv)), epochs=max_epochs,
                     batch_size=batch_size, shuffle=True, callbacks=[es], verbose=0)
    # shuffle=True mélange les ÉCHANTILLONS d'apprentissage entre eux (des fenêtres déjà
    # construites dans l'ordre) : cela ne fait pas fuiter le futur, la validation restant postérieure.
    return model, sc, hist.history, len(hist.history["loss"])


def predict(model, sc: Scaler, X) -> np.ndarray:
    return sc.inv_y(model.predict(sc.tx(X), verbose=0))


def rmse(Y_true, Y_pred) -> float:
    m = ~np.isnan(Y_true)
    return float(np.sqrt(np.mean((Y_true[m] - Y_pred[m]) ** 2)))


# ---------------------------------------------------------------------------
# Validation croisée temporelle (walk-forward)
# ---------------------------------------------------------------------------

def walk_forward_splits(n: int, n_splits: int = 5, gap: int = HORIZON):
    """Découpage en fenêtre croissante (TimeSeriesSplit) avec un écart de h échantillons."""
    from sklearn.model_selection import TimeSeriesSplit

    return list(TimeSeriesSplit(n_splits=n_splits, gap=gap).split(np.arange(n)))


def walk_forward(kind: str, cfg: dict, X, Y, origins, seed: int, val_ratio: float, patience: int,
                 n_splits: int = 5) -> pd.DataFrame:
    """Score de chaque fold : RMSE du réseau et de deux références sur la même période.

    - « zéro » : prévoir un rendement nul, c'est-à-dire la marche aléatoire (prix de demain
      = prix d'aujourd'hui), le modèle retenu en §3.1 ;
    - « moyenne » : prévoir le rendement moyen de la partie d'apprentissage.
    Un réseau utile doit battre au moins la marche aléatoire.
    """
    rows = []
    for i, (tr, te) in enumerate(walk_forward_splits(len(X), n_splits), start=1):
        t0 = time.time()
        model, sc, _, epochs = train(kind, cfg, X[tr], Y[tr], seed, val_ratio, patience)
        pred = predict(model, sc, X[te])
        rows.append({"fold": i, "apprentissage": f"{origins[tr[0]].date()} → {origins[tr[-1]].date()}",
                     "évaluation": f"{origins[te[0]].date()} → {origins[te[-1]].date()}",
                     "n apprentissage": len(tr), "n évaluation": len(te), "époques": epochs,
                     "RMSE réseau": rmse(Y[te], pred), "RMSE zéro (marche aléatoire)": rmse(Y[te], np.zeros_like(pred)),
                     "RMSE moyenne": rmse(Y[te], np.full_like(pred, np.nanmean(Y[tr]))),
                     "durée (s)": time.time() - t0})
    df = pd.DataFrame(rows).set_index("fold")
    df["gain vs zéro (%)"] = 100 * (1 - df["RMSE réseau"] / df["RMSE zéro (marche aléatoire)"])
    return df


def grid_search(kinds, grid: list[dict], panel_train: pd.DataFrame, seed: int, val_ratio: float,
                patience: int, n_splits: int = 5) -> tuple[pd.DataFrame, dict]:
    """Évalue chaque configuration par walk-forward sur le train ; renvoie le résumé et le détail par fold."""
    rows, details = [], {}
    cache = {}
    for kind in kinds:
        for cfg in grid:
            w = cfg["window"]
            if w not in cache:
                cache[w] = make_windows(panel_train, w)
            X, Y, origins = cache[w]
            m = ~np.isnan(Y).any(axis=1)          # apprentissage : uniquement des horizons complets
            folds = walk_forward(kind, cfg, X[m], Y[m], origins[m], seed, val_ratio, patience, n_splits)
            key = (kind, w, cfg["units"], cfg["dropout"])
            details[key] = folds
            rows.append({"modèle": kind, "fenêtre": w, "unités": cfg["units"], "dropout": cfg["dropout"],
                         "RMSE moyen": folds["RMSE réseau"].mean(), "écart-type": folds["RMSE réseau"].std(),
                         "RMSE zéro moyen": folds["RMSE zéro (marche aléatoire)"].mean(),
                         "gain moyen vs zéro (%)": folds["gain vs zéro (%)"].mean(),
                         "folds battant le zéro": int((folds["gain vs zéro (%)"] > 0).sum()),
                         "époques moyennes": folds["époques"].mean(), "durée (s)": folds["durée (s)"].sum()})
    return pd.DataFrame(rows), details


# ---------------------------------------------------------------------------
# Hybride ARIMA + LSTM
# ---------------------------------------------------------------------------

def arima_multi_origin(r: np.ndarray, fit_end: int, order=(3, 2), horizon: int = HORIZON):
    """Ajuste un ARMA(p,q) sur r[:fit_end] (rendements en %), puis, SANS ré-estimer,
    calcule pour chaque origine t les résidus in-sample et les prévisions h = 1…10.

    Les paramètres ne voient que l'apprentissage ; le filtrage sur la suite de la série
    n'utilise, à chaque origine, que les observations jusqu'à t (pas de fuite).
    Renvoie (résidus à un pas pour toute la série, prévisions (n, h) depuis chaque origine).
    """
    import warnings
    from statsmodels.tsa.statespace.sarimax import SARIMAX

    p, q = order
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        res = SARIMAX(r[:fit_end], order=(p, 0, q), trend="n").fit(disp=False, maxiter=500)
        full = res.apply(r)                       # mêmes paramètres, filtrage sur toute la série
    resid = np.asarray(full.resid)
    # Prévision multi-pas depuis chaque origine t, à partir de l'état filtré en t.
    # Pour un ARMA sans constante, l'état filtré suffit : x_{t+h|t} = T^h a_{t|t}.
    T = full.filter_results.transition[:, :, 0]
    Z = full.filter_results.design[:, :, 0]
    a = full.filter_results.filtered_state.T      # (n, k) : état filtré en t (information jusqu'à t)
    F = np.empty((len(r), horizon))
    Th = np.eye(T.shape[0])
    for h in range(horizon):
        Th = T @ Th
        F[:, h] = (a @ Th.T @ Z.T).ravel()
    return resid, F, res


def hybrid_windows(panel: pd.DataFrame, resid: np.ndarray, arima_fc: np.ndarray, window: int,
                   horizon: int = HORIZON):
    """Fenêtres pour l'hybride : entrées = résidus ARIMA + autres variables ; cible = résidus futurs.

    La prévision finale de l'hybride est : prévision ARIMA (partie linéaire) + prévision
    du réseau sur les résidus (partie non linéaire). Les tableaux arima_fc et resid sont
    alignés sur les rendements (index de panel sans le premier jour).
    """
    p = panel.iloc[1:].copy()
    p["resid"] = resid
    X, Yres, origins = make_windows(p, window, features=["resid", "XLE_ret", "XOM_vol21"], target="resid",
                                    horizon=horizon)
    pos = p.index.get_indexer(origins)
    _, Yret, _ = make_windows(p, window, features=["resid", "XLE_ret", "XOM_vol21"], target="XOM_ret",
                              horizon=horizon)
    return X, Yres, Yret, arima_fc[pos], origins


def hybrid_walk_forward(panel_train: pd.DataFrame, cfg: dict, seed: int, val_ratio: float, patience: int,
                        n_splits: int = 5, order=(3, 2)) -> pd.DataFrame:
    """Walk-forward de l'hybride sur les mêmes folds que les réseaux seuls.

    À chaque fold, l'ARIMA est ré-estimé sur la seule période d'apprentissage du fold,
    puis le réseau apprend ses résidus. On compare l'hybride à l'ARIMA seul, au réseau
    seul (implicitement, via le tableau des réseaux) et à la marche aléatoire.
    """
    p = panel_train.iloc[1:]
    r = p["XOM_ret"].to_numpy()
    # Les folds sont définis sur les origines à horizon complet, comme pour les réseaux seuls.
    resid0 = np.zeros(len(r))
    _, Y0, _, _, orig0 = hybrid_windows(panel_train, resid0, np.zeros((len(r), HORIZON)), cfg["window"])
    keep = ~np.isnan(Y0).any(axis=1)
    orig_c = orig0[keep]
    rows = []
    for i, (tr, te) in enumerate(walk_forward_splits(len(orig_c), n_splits), start=1):
        t0 = time.time()
        fit_end = p.index.get_loc(orig_c[tr[-1]]) + 1          # ARIMA estimé jusqu'à la dernière origine d'apprentissage
        resid, fc, _ = arima_multi_origin(r, fit_end, order)
        X, Yres, Yret, F, orig = hybrid_windows(panel_train, resid, fc, cfg["window"])
        X, Yres, Yret, F = X[keep], Yres[keep], Yret[keep], F[keep]
        model, sc, _, epochs = train("LSTM", cfg, X[tr], Yres[tr], seed, val_ratio, patience)
        hyb = F[te] + predict(model, sc, X[te])
        rows.append({"fold": i, "évaluation": f"{orig_c[te[0]].date()} → {orig_c[te[-1]].date()}", "époques": epochs,
                     "RMSE hybride": rmse(Yret[te], hyb), "RMSE ARIMA(3,1,2) seul": rmse(Yret[te], F[te]),
                     "RMSE zéro (marche aléatoire)": rmse(Yret[te], np.zeros_like(hyb)),
                     "durée (s)": time.time() - t0})
    df = pd.DataFrame(rows).set_index("fold")
    df["gain hybride vs zéro (%)"] = 100 * (1 - df["RMSE hybride"] / df["RMSE zéro (marche aléatoire)"])
    return df


# ---------------------------------------------------------------------------
# Entraînement final (3 seeds) et prévisions depuis les origines du test
# ---------------------------------------------------------------------------

def final_models(kind: str, cfg: dict, panel: pd.DataFrame, train_end: pd.Timestamp, seeds, val_ratio: float,
                 patience: int, hybrid: bool = False, order=(3, 2)) -> dict:
    """Entraîne la configuration retenue sur tout le train, une fois par seed.

    Apprentissage : uniquement les origines dont les 10 jours cibles sont dans le train
    (aucun rendement du test dans les cibles). Prévision : depuis chaque origine allant
    du dernier jour du train à l'avant-dernier jour du test ; chaque fenêtre d'entrée
    n'utilise que des données connues à sa date d'origine.
    Renvoie les historiques de perte et les prévisions (en % de rendement) par seed.
    """
    p = panel.iloc[1:]
    r = p["XOM_ret"].to_numpy()
    n_fit = p.index.get_loc(train_end) + 1
    if hybrid:
        resid, fc, _ = arima_multi_origin(r, n_fit, order)
        X, Y, Yret, F, origins = hybrid_windows(panel, resid, fc, cfg["window"])
    else:
        X, Y, origins = make_windows(panel, cfg["window"])
        F = np.zeros_like(Y)
        Yret = Y
    # Cibles entièrement dans le train : origine ≤ train_end − h jours de bourse.
    last_fit_origin = p.index[n_fit - 1 - HORIZON]
    fit_mask = (origins <= last_fit_origin) & ~np.isnan(Y).any(axis=1)
    fc_mask = (origins >= train_end) & (origins < panel.index[-1])
    out = {"histories": {}, "forecasts": {}, "epochs": {}, "origins": origins[fc_mask],
           "actual": Yret[fc_mask], "arima": F[fc_mask], "n_fit": int(fit_mask.sum())}
    for s in seeds:
        model, sc, hist, ep = train(kind, cfg, X[fit_mask], Y[fit_mask], s, val_ratio, patience)
        out["histories"][s] = hist
        out["epochs"][s] = ep
        out["forecasts"][s] = F[fc_mask] + predict(model, sc, X[fc_mask])
    return out


def to_price(last_price: np.ndarray, ret_fc: np.ndarray) -> np.ndarray:
    """Prix prévus : P_{t+h} = P_t × exp(Σ_{j≤h} r̂_{t+j} / 100), à partir des log-rendements prévus en %."""
    return last_price[:, None] * np.exp(np.cumsum(ret_fc, axis=1) / 100)
