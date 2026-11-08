"""Exécute les deux notebooks de bout en bout : main_python.ipynb puis classical_R.Rmd.

Usage (depuis la racine du projet) : python run_all.py
Le notebook Python est exécuté avec l'environnement créé par `install.py` (chemin lu
dans `.venv-path`, sinon `.venv`). Le Rmd est rendu ensuite, car il relit les
tableaux exportés par le notebook Python (comparaison R / Python).
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

from install import ROOT, find_rscript, venv_python


def python_env() -> Path:
    marker = ROOT / ".venv-path"
    venv_dir = Path(marker.read_text(encoding="utf-8").strip()) if marker.exists() else ROOT / ".venv"
    py = venv_python(venv_dir)
    if not py.exists():
        sys.exit(f"Environnement Python introuvable ({venv_dir}) : lancer d'abord `python install.py`.")
    return py


def pandoc_on_path() -> None:
    """rmarkdown a besoin de Pandoc ; on ajoute l'emplacement d'installation de winget s'il n'est pas dans le PATH."""
    if shutil.which("pandoc"):
        return
    local = Path(os.environ.get("LOCALAPPDATA", "")) / "Pandoc"
    if (local / "pandoc.exe").exists():
        os.environ["PATH"] += os.pathsep + str(local)
    else:
        sys.exit("Pandoc introuvable : l'installer (winget install JohnMacFarlane.Pandoc), il est requis par rmarkdown.")


def main() -> None:
    py = python_env()
    subprocess.run([str(py), "-m", "jupyter", "nbconvert", "--to", "notebook", "--execute", "--inplace",
                    "--ExecutePreprocessor.timeout=3600", "notebooks/main_python.ipynb"], check=True, cwd=ROOT)
    print("Notebook Python exécuté.")
    if "--no-r" in sys.argv:
        return
    rscript = find_rscript()
    if not rscript:
        sys.exit("Rscript introuvable : installer R (≥ 4.3).")
    pandoc_on_path()
    subprocess.run([rscript, "-e", "rmarkdown::render('notebooks/classical_R.Rmd')"], check=True, cwd=ROOT)
    print("Rmd rendu : notebooks/classical_R.html")


if __name__ == "__main__":
    os.chdir(ROOT)
    main()
