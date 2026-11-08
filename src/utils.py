"""Utilitaires communs : chemins, configuration, seed, sauvegardes, versions."""

from __future__ import annotations

import os
import random
import sys
from functools import lru_cache
from importlib import metadata
from pathlib import Path

import numpy as np
import yaml

# Racine déduite de l'emplacement du fichier : aucun chemin absolu, le projet
# s'exécute tel quel sur n'importe quelle machine (critère reproductibilité).
ROOT = Path(__file__).resolve().parents[1]


@lru_cache(maxsize=1)
def load_config() -> dict:
    """Lit config.yaml une seule fois : source unique des paramètres de l'étude."""
    with open(ROOT / "config.yaml", encoding="utf-8") as f:
        return yaml.safe_load(f)


def path(key: str) -> Path:
    """Renvoie un dossier déclaré dans config.yaml (section paths), créé si absent."""
    p = ROOT / load_config()["paths"][key]
    p.mkdir(parents=True, exist_ok=True)
    return p


def set_seed(seed: int | None = None) -> int:
    """Fixe toutes les sources d'aléa pour que LSTM/GRU et bootstrap soient reproductibles."""
    seed = load_config()["seed"] if seed is None else seed
    os.environ["PYTHONHASHSEED"] = str(seed)
    random.seed(seed)
    np.random.seed(seed)
    # TensorFlow n'est importé que s'il est déjà chargé : évite 5 s de démarrage
    # pour les parties purement économétriques.
    if "tensorflow" in sys.modules:
        import tensorflow as tf

        tf.random.set_seed(seed)
        # Opérations déterministes : sinon deux runs avec la même seed divergent sur CPU multi-thread.
        tf.config.experimental.enable_op_determinism()
    return seed


def save_fig(fig, number: int, name: str, dpi: int = 150) -> Path:
    """Sauvegarde sous figNN_nom.png : la numérotation suit l'ordre du rapport."""
    out = path("figures") / f"fig{number:02d}_{name}.png"
    fig.savefig(out, dpi=dpi, bbox_inches="tight")
    return out


def save_table(df, name: str, index: bool = True) -> Path:
    """Sauvegarde un tableau du rapport en CSV pour le réutiliser sans recalcul."""
    out = path("tables") / f"{name}.csv"
    df.to_csv(out, index=index, encoding="utf-8")
    return out


TRACKED_PACKAGES = [
    "numpy", "pandas", "scipy", "statsmodels", "pmdarima", "arch", "scikit-learn",
    "tensorflow", "prophet", "yfinance", "matplotlib", "seaborn", "pyyaml",
]


def package_versions() -> dict[str, str]:
    """Versions installées, affichées en tête de notebook (exigence cahier §9.1)."""
    versions = {"python": sys.version.split()[0]}
    for pkg in TRACKED_PACKAGES:
        try:
            versions[pkg] = metadata.version(pkg)
        except metadata.PackageNotFoundError:
            versions[pkg] = "NON INSTALLÉ"
    return versions


def print_versions() -> None:
    for pkg, v in package_versions().items():
        print(f"{pkg:<14} {v}")


if __name__ == "__main__":
    # Contrôle rapide de l'installation : python -m src.utils
    print(f"Racine du projet : {ROOT}")
    print(f"Tickers : {load_config()['data']['tickers']}")
    print(f"Seed : {set_seed()}")
    print_versions()
