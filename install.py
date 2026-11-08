"""Installation complète du projet, quel que soit l'emplacement du dossier.

Usage (depuis la racine du projet, avec Python 3.11) :
    python install.py            # environnement Python + packages R
    python install.py --no-r     # environnement Python seulement

Pourquoi ce script : sous Windows, sans l'option « chemins longs », un chemin de
fichier ne peut pas dépasser 260 caractères. TensorFlow installe un fichier dont
le chemin, relatif à l'environnement, fait 161 caractères. Si le projet est dans
un dossier profond, `.venv` dépasse la limite et l'installation échoue
(`OSError: No such file or directory … tensorflow\\include\\…`). Le script place
alors l'environnement dans un dossier court et l'indique dans `.venv-path`, que
`run_all.py` relit pour exécuter les notebooks.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
# Chemin relatif le plus long créé dans l'environnement par requirements.txt (TensorFlow 2.16.2), mesuré.
LONGEST_REL = 161
MAX_PATH = 260
MARGIN = 10          # séparateurs, caractère nul final, fichiers temporaires de pip


def long_paths_enabled() -> bool:
    """Lit l'option Windows « LongPathsEnabled » (registre) ; toujours vrai hors Windows."""
    if os.name != "nt":
        return True
    try:
        import winreg

        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\FileSystem") as k:
            return winreg.QueryValueEx(k, "LongPathsEnabled")[0] == 1
    except OSError:
        return False


def fits(venv_dir: Path) -> bool:
    return len(str(venv_dir)) + 1 + LONGEST_REL + MARGIN <= MAX_PATH


def choose_venv() -> Path:
    """`.venv` dans le projet si le chemin le permet, sinon un dossier court dans le profil utilisateur."""
    default = ROOT / ".venv"
    if long_paths_enabled() or fits(default):
        return default
    for candidate in (Path(os.environ.get("USERPROFILE", "C:\\")) / ".venvs" / "ts-project",
                      Path(os.environ.get("SystemDrive", "C:") + "\\") / "venvs" / "ts-project"):
        if fits(candidate):
            return candidate
    sys.exit("Aucun emplacement assez court pour l'environnement : activer les chemins longs de Windows "
             "(https://pip.pypa.io/warnings/enable-long-paths) puis relancer.")


def venv_python(venv_dir: Path) -> Path:
    return venv_dir / ("Scripts/python.exe" if os.name == "nt" else "bin/python")


def run(cmd: list) -> None:
    print(">", " ".join(str(c) for c in cmd), flush=True)
    subprocess.run([str(c) for c in cmd], check=True)


def find_rscript() -> str | None:
    exe = shutil.which("Rscript")
    if exe:
        return exe
    if os.name == "nt":
        found = sorted(Path("C:/Program Files/R").glob("R-*/bin/Rscript.exe"))
        if found:
            return str(found[-1])
    return None


def main() -> None:
    if sys.version_info[:2] != (3, 11):
        print(f"Attention : Python {sys.version.split()[0]} détecté ; les versions figées supposent Python 3.11.")

    venv_dir = choose_venv()
    if venv_dir != ROOT / ".venv":
        print(f"Dossier du projet trop profond pour TensorFlow sans chemins longs ({len(str(ROOT))} caractères) :\n"
              f"l'environnement Python est créé dans {venv_dir}")
    if not venv_python(venv_dir).exists():
        run([sys.executable, "-m", "venv", venv_dir])
    py = venv_python(venv_dir)
    run([py, "-m", "pip", "install", "--upgrade", "pip"])
    run([py, "-m", "pip", "install", "-r", ROOT / "requirements.txt"])
    run([py, "-m", "pip", "check"])
    (ROOT / ".venv-path").write_text(str(venv_dir), encoding="utf-8")
    run([py, "-m", "src.utils"])

    if "--no-r" not in sys.argv:
        rscript = find_rscript()
        if rscript:
            run([rscript, ROOT / "install_packages.R"])
        else:
            print("Rscript introuvable : installer R (≥ 4.3) puis lancer `Rscript install_packages.R`.")

    print(f"\nInstallation terminée. Environnement Python : {venv_dir}\n"
          f"Exécution des deux notebooks : {py} run_all.py")


if __name__ == "__main__":
    # Console Windows (cp1252) : un caractère non affichable ne doit pas interrompre l'installation.
    sys.stdout.reconfigure(errors="replace")
    os.chdir(ROOT)
    main()
