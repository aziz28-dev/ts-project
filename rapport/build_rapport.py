"""Construit le rapport Word : rapport.md + annexes tirées de llm/, converti par Pandoc.

Usage (depuis la racine du projet) : python rapport/build_rapport.py
Sortie : rapport/rapport.docx (et, si Microsoft Word est installé, rapport/rapport.pdf).

Les annexes B à D sont recopiées automatiquement depuis llm/ : elles restent donc
identiques aux fichiers archivés (prompts et réponses intégrales, sans retouche).
"""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "rapport"
LLM = ROOT / "llm"


def pandoc() -> str:
    exe = shutil.which("pandoc")
    if exe:
        return exe
    local = Path.home() / "AppData/Local/Pandoc/pandoc.exe"
    if local.exists():
        return str(local)
    sys.exit("Pandoc introuvable : l'installer (https://pandoc.org) ou l'ajouter au PATH.")


def demote(md: str, levels: int) -> str:
    """Abaisse les titres Markdown de `levels` niveaux (les annexes sont sous « # Annexes »)."""
    return re.sub(r"^(#{1,6}) ", lambda m: "#" * min(6, len(m.group(1)) + levels) + " ", md, flags=re.M)


def body_after_rule(md: str) -> str:
    """Partie d'un fichier de prompt ou de réponse située après la ligne « --- » (le texte envoyé / reçu)."""
    parts = re.split(r"^---\s*$", md, maxsplit=1, flags=re.M)
    return parts[1].strip() if len(parts) == 2 else md.strip()


def header_lines(md: str) -> str:
    """En-tête de traçabilité (modèle, date, statut) situé avant la ligne « --- », sans le titre."""
    head = re.split(r"^---\s*$", md, maxsplit=1, flags=re.M)[0]
    return "\n".join(l for l in head.strip().splitlines() if not l.startswith("#")).strip()


def verbatim(text: str, keep_tables: bool) -> str:
    """Rend un texte ligne par ligne (bloc de lignes Pandoc) : chaque retour à la ligne est conservé.

    Sans cela, Markdown fusionnerait les lignes des réponses du LLM en un seul paragraphe.
    Les tableaux Markdown des prompts (lignes commençant par « | ») restent des tableaux.
    """
    out, in_table = [], False
    for line in text.splitlines():
        is_table = keep_tables and line.lstrip().startswith("|")
        if is_table != in_table:
            out.append("")
            in_table = is_table
        if is_table:
            out.append(line)
        elif line.strip():
            # Caractères Markdown échappés : le texte du LLM (dont ses formules LaTeX) est reproduit tel quel.
            esc = re.sub(r"([\\`*_{}\[\]<>#^~$|])", r"\\\1", line.replace("\t", " · "))
            out.append("| " + esc)
        else:
            out.append("")
    return "\n".join(out)


def hard_breaks_header(md: str) -> str:
    """Retour à la ligne forcé entre les lignes « **Auteurs :** » et « **Date** » des fichiers de llm/."""
    return re.sub(r"^(\*\*Auteurs? :\*\*[^\n]*)\n(\*\*Date)", r"\1\\\n\2", md, flags=re.M)


def annexes() -> str:
    page = "\n```{=openxml}\n<w:p><w:r><w:br w:type=\"page\"/></w:r></w:p>\n```\n"
    out = [page, "## Annexe B — Interprétation personnelle (rédigée avant le LLM)\n",
           demote(hard_breaks_header((LLM / "interpretation_personnelle.md").read_text(encoding="utf-8").split("\n", 1)[1]), 2)]
    out += [page, "## Annexe C — Prompts et réponses intégrales du LLM\n",
            "Chaque prompt a été envoyé dans une nouvelle conversation. Les réponses sont reproduites sans retouche.\n"]
    pairs = [("01_hypotheses.md", "01_hypotheses_chatgpt-gpt6_2026-11-08.md", "C.1 Tâche 1 — Hypothèses de modèles"),
             ("02_vulgarisation.md", "02_vulgarisation_chatgpt-gpt6_2026-11-08.md", "C.2 Tâche 2 — Vulgarisation pour un décideur"),
             (None, "03a_recommandations_sans-donnees_chatgpt-gpt6_2026-11-08.md", "C.3 Tâche 3 — Essai envoyé sans données"),
             ("03_recommandations.md", "03_recommandations_chatgpt-gpt6_2026-11-08.md", "C.4 Tâche 3 — Recommandations simulées")]
    for prompt, resp, title in pairs:
        out.append(f"\n### {title}\n")
        if prompt:
            out += ["\n#### Prompt envoyé\n",
                    verbatim(body_after_rule((LLM / "prompts" / prompt).read_text(encoding="utf-8")), keep_tables=True)]
        r = (LLM / "responses" / resp).read_text(encoding="utf-8")
        out += ["\n#### Réponse du LLM\n", header_lines(r), "\n", verbatim(body_after_rule(r), keep_tables=False)]
    comp = hard_breaks_header((LLM / "comparaison.md").read_text(encoding="utf-8").split("\n", 1)[1])
    out += [page, "## Annexe D — Comparaison détaillée entre notre interprétation et le LLM\n", demote(comp, 2)]
    return "\n".join(out)


def reference_docx(pd: str) -> Path:
    """Modèle Word dérivé de celui de Pandoc : format A4, marges de 2 cm, tableaux encadrés."""
    ref = OUT / "reference.docx"
    raw = subprocess.run([pd, "--print-default-data-file", "reference.docx"], capture_output=True, check=True).stdout
    tmp = OUT / "_ref_default.docx"
    tmp.write_bytes(raw)
    with zipfile.ZipFile(tmp) as zin, zipfile.ZipFile(ref, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename == "word/document.xml":
                s = data.decode("utf-8")
                s = re.sub(r"<w:pgSz[^>]*/>", '<w:pgSz w:w="11906" w:h="16838"/>', s)
                s = re.sub(r"<w:pgMar[^>]*/>", '<w:pgMar w:top="1134" w:right="1134" w:bottom="1134" w:left="1134" '
                           'w:header="567" w:footer="567" w:gutter="0"/>', s)
                data = s.encode("utf-8")
            if item.filename == "word/styles.xml":
                s = data.decode("utf-8")
                borders = ('<w:tblBorders><w:top w:val="single" w:sz="4" w:space="0" w:color="999999"/>'
                           '<w:left w:val="single" w:sz="4" w:space="0" w:color="999999"/>'
                           '<w:bottom w:val="single" w:sz="4" w:space="0" w:color="999999"/>'
                           '<w:right w:val="single" w:sz="4" w:space="0" w:color="999999"/>'
                           '<w:insideH w:val="single" w:sz="4" w:space="0" w:color="999999"/>'
                           '<w:insideV w:val="single" w:sz="4" w:space="0" w:color="999999"/></w:tblBorders>')
                # Texte des tableaux en 9 pt (rPr avant tblPr, ordre imposé par le schéma) et bordures fines.
                small = '<w:rPr><w:sz w:val="18"/><w:szCs w:val="18"/></w:rPr>'
                s = re.sub(r'(<w:style w:type="table"[^>]*w:styleId="Table">.*?)<w:tblPr>', r"\1" + small + "<w:tblPr>" + borders,
                           s, count=1, flags=re.S)
                data = s.encode("utf-8")
            zout.writestr(item, data)
    tmp.unlink()
    return ref


def to_pdf(docx: Path) -> None:
    """Conversion PDF par Microsoft Word (si présent) : sert aussi à compter les pages."""
    ps = (f"$w = New-Object -ComObject Word.Application; $w.Visible = $false; "
          f"$d = $w.Documents.Open('{docx}'); $d.Fields.Update() | Out-Null; $d.TablesOfContents | ForEach-Object {{ $_.Update() }}; "
          f"$d.SaveAs2('{docx.with_suffix('.pdf')}', 17); "
          f"Write-Output ('pages : ' + $d.ComputeStatistics(2)); $d.Close($false); $w.Quit()")
    r = subprocess.run(["powershell", "-NoProfile", "-Command", ps], capture_output=True, text=True)
    print(r.stdout.strip() or r.stderr.strip()[:300])


def main():
    pd = pandoc()
    md = (OUT / "rapport.md").read_text(encoding="utf-8") + "\n" + annexes()
    full = OUT / "_rapport_complet.md"
    full.write_text(md, encoding="utf-8")
    out = OUT / "rapport.docx"
    subprocess.run([pd, str(full), "-o", str(out), "--toc", "--toc-depth=2", f"--reference-doc={reference_docx(pd)}",
                    f"--resource-path={OUT}", "--from=markdown+tex_math_dollars+lists_without_preceding_blankline"], check=True, cwd=OUT)
    full.unlink()
    print("écrit :", out.relative_to(ROOT))
    if sys.platform == "win32":
        to_pdf(out)


if __name__ == "__main__":
    main()
