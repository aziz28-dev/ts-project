"""Exécute les deux notebooks de bout en bout : main_python.ipynb puis classical_R.Rmd.

Usage (depuis la racine du projet) : python run_all.py
Le notebook Python est exécuté avec l'environnement créé par `install.py` (chemin lu
dans `.venv-path`, sinon `.venv`), même si un autre environnement est activé. Il est
enregistré après chaque cellule, ce qui permet de suivre l'exécution dans VS Code.
Le Rmd est rendu ensuite, car il relit les tableaux exportés par le notebook Python
(comparaison R / Python).
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


def activated_env(py: Path) -> dict:
    """Variables d'environnement de l'environnement choisi, comme après une activation.

    Pourquoi : si un autre environnement est déjà activé (terminal d'un IDE par exemple),
    Jupyter prend le noyau `python3` de celui-ci (VIRTUAL_ENV, PATH) et non celui de `py`.
    """
    venv_dir = py.parent.parent
    env = os.environ.copy()
    env.pop("PYTHONHOME", None)
    env["VIRTUAL_ENV"] = str(venv_dir)
    env["PATH"] = str(py.parent) + os.pathsep + env.get("PATH", "")
    return env


NOTEBOOK = ROOT / "notebooks" / "main_python.ipynb"


def execute_notebook_live(path: Path) -> None:
    """Exécute le notebook en l'enregistrant après chaque cellule (lancé dans l'environnement du projet).

    Pourquoi pas `nbconvert --execute` : il n'écrit le notebook qu'à la fin (environ 12 min).
    Ici, le fichier ouvert dans VS Code ou Jupyter se remplit cellule par cellule.
    """
    import nbformat
    from nbclient import NotebookClient

    nb = nbformat.read(path, as_version=4)
    code_cells = [c for c in nb.cells if c.cell_type == "code"]
    # Les sorties de l'exécution précédente sont effacées : à l'écran, tout ce qui est affiché vient de ce run.
    for c in code_cells:
        c.outputs, c.execution_count = [], None
    nbformat.write(nb, path)
    done = 0

    def save(cell, cell_index, execute_reply):
        nonlocal done
        if cell.cell_type == "code":
            done += 1
            print(f"cellule {done}/{len(code_cells)}", flush=True)
        nbformat.write(nb, path)

    NotebookClient(nb, timeout=3600, kernel_name="python3", on_cell_executed=save,
                   resources={"metadata": {"path": str(path.parent)}}).execute()
    nbformat.write(nb, path)


def main() -> None:
    py = python_env()
    env = activated_env(py)
    # Le noyau `python3` lance « python » trouvé dans le PATH : on affiche lequel, pour contrôle.
    print(f"Python du noyau Jupyter : {shutil.which('python', path=env['PATH'])}", flush=True)
    print(f"Pour suivre l'exécution, ouvrir {NOTEBOOK} (mis à jour après chaque cellule).", flush=True)
    subprocess.run([str(py), Path(__file__).resolve(), "--executer-notebook"], check=True, cwd=ROOT, env=env)
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
    # Console Windows (cp1252) : un caractère non affichable ne doit pas interrompre l'installation.
    sys.stdout.reconfigure(errors="replace")
    os.chdir(ROOT)
    if "--executer-notebook" in sys.argv:
        execute_notebook_live(NOTEBOOK)
    else:
        main()
