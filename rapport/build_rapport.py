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
    out = [page, "## Annexe B. Interprétation personnelle, rédigée avant l'usage du LLM\n",
           demote(hard_breaks_header((LLM / "interpretation_personnelle.md").read_text(encoding="utf-8").split("\n", 1)[1]), 2)]
    out += [page, "## Annexe C. Prompts et réponses intégrales du LLM\n",
            "Chaque prompt a été envoyé dans une nouvelle conversation. Les réponses sont reproduites sans retouche.\n"]
    pairs = [("01_hypotheses.md", "01_hypotheses_chatgpt-gpt6_2026-11-08.md", "C.1 Tâche 1 : hypothèses de modèles"),
             ("02_vulgarisation.md", "02_vulgarisation_chatgpt-gpt6_2026-11-08.md", "C.2 Tâche 2 : vulgarisation pour un décideur"),
             (None, "03a_recommandations_sans-donnees_chatgpt-gpt6_2026-11-08.md", "C.3 Tâche 3 : essai envoyé sans données"),
             ("03_recommandations.md", "03_recommandations_chatgpt-gpt6_2026-11-08.md", "C.4 Tâche 3 : recommandations simulées")]
    for prompt, resp, title in pairs:
        out.append(f"\n### {title}\n")
        if prompt:
            out += ["\n#### Prompt envoyé\n",
                    verbatim(body_after_rule((LLM / "prompts" / prompt).read_text(encoding="utf-8")), keep_tables=True)]
        r = (LLM / "responses" / resp).read_text(encoding="utf-8")
        out += ["\n#### Réponse du LLM\n", header_lines(r), "\n", verbatim(body_after_rule(r), keep_tables=False)]
    comp = hard_breaks_header((LLM / "comparaison.md").read_text(encoding="utf-8").split("\n", 1)[1])
    out += [page, "## Annexe D. Comparaison détaillée entre notre interprétation et celle du LLM\n", demote(comp, 2)]
    return "\n".join(out)


FONT = "Times New Roman"
NAVY = "1F3864"


def _rfonts(font: str = FONT) -> str:
    return f'<w:rFonts w:ascii="{font}" w:hAnsi="{font}" w:eastAsia="{font}" w:cs="{font}"/>'


def _pstyle(sid: str, name: str, ppr: str, rpr: str = "", based: str = "Normal", nxt: str = "") -> str:
    """Définition complète d'un style de paragraphe (remplace celle du modèle Pandoc si elle existe)."""
    nxt = f'<w:next w:val="{nxt}"/>' if nxt else ""
    # Les styles intégrés de Word (titres, légende…) ne sont pas « personnalisés » : la table des matières en dépend.
    custom = "" if name.islower() or name in ("Normal", "Body Text", "Caption", "TOC Heading", "Bibliography") \
        else ' w:customStyle="1"'
    return (f'<w:style w:type="paragraph"{custom} w:styleId="{sid}"><w:name w:val="{name}"/>'
            f'<w:basedOn w:val="{based}"/>{nxt}<w:qFormat/><w:pPr>{ppr}</w:pPr><w:rPr>{rpr}</w:rPr></w:style>')


def _styles() -> list[tuple[str, str]]:
    """Styles du rapport : Times New Roman, texte justifié, titres bleu nuit, page de garde centrée."""
    center = '<w:jc w:val="center"/>'
    heading = lambda lvl, size, before, extra="": (
        f'<w:keepNext/><w:keepLines/><w:spacing w:before="{before}" w:after="120"/><w:outlineLvl w:val="{lvl}"/>',
        f'{_rfonts()}<w:b/><w:bCs/>{extra}<w:color w:val="{NAVY}"/><w:sz w:val="{size}"/><w:szCs w:val="{size}"/>')
    h1, h2, h3, h4 = heading(0, 32, 480), heading(1, 26, 320), heading(2, 24, 240, "<w:i/>"), heading(3, 22, 200, "<w:i/>")
    return [
        ("Normal", '<w:style w:type="paragraph" w:default="1" w:styleId="Normal"><w:name w:val="Normal"/><w:qFormat/>'
                   '<w:pPr><w:spacing w:after="0" w:line="276" w:lineRule="auto"/></w:pPr></w:style>'),
        ("BodyText", _pstyle("BodyText", "Body Text", '<w:spacing w:before="80" w:after="80" w:line="276" w:lineRule="auto"/>'
                             '<w:jc w:val="both"/>')),
        ("TOC1", _pstyle("TOC1", "toc 1", '<w:spacing w:before="100" w:after="20"/>', "<w:b/>", nxt="Normal")),
        ("TOC2", _pstyle("TOC2", "toc 2", '<w:spacing w:before="0" w:after="20"/><w:ind w:left="360"/>', nxt="Normal")),
        ("FirstParagraph", _pstyle("FirstParagraph", "First Paragraph", "", based="BodyText", nxt="BodyText")),
        ("Compact", _pstyle("Compact", "Compact", '<w:spacing w:before="20" w:after="20" w:line="240" w:lineRule="auto"/>'
                            '<w:jc w:val="left"/>', based="BodyText")),
        ("Heading1", _pstyle("Heading1", "heading 1", h1[0], h1[1], nxt="BodyText")),
        ("Heading2", _pstyle("Heading2", "heading 2", h2[0], h2[1], nxt="BodyText")),
        ("Heading3", _pstyle("Heading3", "heading 3", h3[0], h3[1], nxt="BodyText")),
        ("Heading4", _pstyle("Heading4", "heading 4", h4[0], h4[1], nxt="BodyText")),
        ("Caption", _pstyle("Caption", "Caption", f'<w:spacing w:before="60" w:after="200"/>{center}',
                            '<w:i/><w:sz w:val="20"/><w:szCs w:val="20"/>')),
        ("ImageCaption", _pstyle("ImageCaption", "Image Caption", "", based="Caption")),
        # Titre de tableau au-dessus du tableau (convention française), collé à celui-ci.
        ("TableCaption", _pstyle("TableCaption", "Table Caption", '<w:keepNext/><w:spacing w:before="200" w:after="80"/>',
                                 based="Caption")),
        ("Figure", _pstyle("Figure", "Figure", f'<w:spacing w:before="200" w:after="0"/>{center}')),
        ("CaptionedFigure", _pstyle("CaptionedFigure", "Captioned Figure", "<w:keepNext/>", based="Figure")),
        ("TOCHeading", _pstyle("TOCHeading", "TOC Heading", f'<w:spacing w:before="0" w:after="360"/>{center}',
                               f'{_rfonts()}<w:b/><w:color w:val="{NAVY}"/><w:sz w:val="32"/><w:szCs w:val="32"/>',
                               nxt="BodyText")),
        ("FrontHeading", _pstyle("FrontHeading", "Front Heading", f'<w:keepNext/><w:spacing w:before="240" w:after="240"/>{center}',
                                 f'<w:b/><w:color w:val="{NAVY}"/><w:sz w:val="32"/><w:szCs w:val="32"/>')),
        ("Bibliography", _pstyle("Bibliography", "Bibliography",
                                 '<w:spacing w:before="0" w:after="100"/><w:ind w:left="567" w:hanging="567"/><w:jc w:val="both"/>',
                                 '<w:sz w:val="22"/><w:szCs w:val="22"/>', based="BodyText")),
        # Page de garde
        ("CoverLogo", _pstyle("CoverLogo", "Cover Logo", f'<w:spacing w:before="0" w:after="480"/>{center}')),
        ("CoverText", _pstyle("CoverText", "Cover Text", f'<w:spacing w:before="0" w:after="60"/>{center}',
                              '<w:sz w:val="26"/><w:szCs w:val="26"/>')),
        ("CoverKind", _pstyle("CoverKind", "Cover Kind", f'<w:spacing w:before="1100" w:after="240"/>{center}',
                              f'<w:caps/><w:spacing w:val="20"/><w:color w:val="{NAVY}"/><w:sz w:val="28"/><w:szCs w:val="28"/>')),
        ("CoverTitle", _pstyle("CoverTitle", "Cover Title",
                               f'<w:pBdr><w:top w:val="single" w:sz="12" w:space="12" w:color="{NAVY}"/>'
                               f'<w:bottom w:val="single" w:sz="12" w:space="12" w:color="{NAVY}"/></w:pBdr>'
                               f'<w:spacing w:before="120" w:after="240" w:line="300" w:lineRule="auto"/>{center}',
                               f'<w:b/><w:color w:val="{NAVY}"/><w:sz w:val="40"/><w:szCs w:val="40"/>')),
        ("CoverSubtitle", _pstyle("CoverSubtitle", "Cover Subtitle", f'<w:spacing w:before="120" w:after="0"/>{center}',
                                  '<w:i/><w:sz w:val="28"/><w:szCs w:val="28"/>')),
        ("CoverNames", _pstyle("CoverNames", "Cover Names", f'<w:spacing w:before="1100" w:after="240"/>{center}',
                               '<w:sz w:val="26"/><w:szCs w:val="26"/>')),
        ("CoverYear", _pstyle("CoverYear", "Cover Year", f'<w:spacing w:before="1100" w:after="0"/>{center}',
                              '<w:sz w:val="24"/><w:szCs w:val="24"/>')),
    ]


def _patch_styles(s: str) -> str:
    # Police et langue par défaut.
    s = re.sub(r"<w:docDefaults>.*?</w:docDefaults>",
               f'<w:docDefaults><w:rPrDefault><w:rPr>{_rfonts()}<w:sz w:val="24"/><w:szCs w:val="24"/>'
               '<w:lang w:val="fr-FR" w:eastAsia="fr-FR" w:bidi="ar-SA"/></w:rPr></w:rPrDefault>'
               '<w:pPrDefault><w:pPr><w:spacing w:after="0"/></w:pPr></w:pPrDefault></w:docDefaults>', s, count=1, flags=re.S)
    for sid, xml in _styles():
        s = re.sub(r'<w:style [^>]*w:styleId="%s"[^>]*>.*?</w:style>' % sid, "", s, count=1, flags=re.S)
        s = s.replace("</w:styles>", xml + "</w:styles>")
    # Tableaux : texte en 9 pt, bordures fines, ligne d'en-tête en gras sur fond bleu clair.
    borders = "".join(f'<w:{b} w:val="single" w:sz="4" w:space="0" w:color="7F7F7F"/>'
                      for b in ("top", "left", "bottom", "right", "insideH", "insideV"))
    small = '<w:rPr><w:sz w:val="18"/><w:szCs w:val="18"/></w:rPr>'
    # Ordre imposé par le schéma OOXML (sinon Word ignore le réglage) : jc, tblInd, tblBorders dans tblPr ;
    # tcBorders puis shd dans tcPr.
    s = re.sub(r'(<w:style w:type="table"[^>]*w:styleId="Table">.*?)<w:tblPr>', r"\1" + small + '<w:tblPr><w:jc w:val="center"/>',
               s, count=1, flags=re.S)
    s = re.sub(r'(<w:style w:type="table"[^>]*w:styleId="Table">.*?<w:tblInd [^>]*/>)',
               r"\1<w:tblBorders>" + borders + "</w:tblBorders>", s, count=1, flags=re.S)
    s = re.sub(r'(<w:tblStylePr w:type="firstRow">)', r'\1<w:rPr><w:b/></w:rPr>', s, count=1)
    s = re.sub(r'(<w:tblStylePr w:type="firstRow">.*?</w:tcBorders>)', r'\1<w:shd w:val="clear" w:color="auto" w:fill="DCE3EF"/>',
               s, count=1, flags=re.S)
    return s


FOOTER = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
          '<w:ftr xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
          '<w:p><w:pPr><w:jc w:val="center"/></w:pPr>'
          '<w:r><w:rPr><w:sz w:val="20"/></w:rPr><w:fldChar w:fldCharType="begin"/></w:r>'
          '<w:r><w:rPr><w:sz w:val="20"/></w:rPr><w:instrText xml:space="preserve"> PAGE </w:instrText></w:r>'
          '<w:r><w:rPr><w:sz w:val="20"/></w:rPr><w:fldChar w:fldCharType="separate"/></w:r>'
          '<w:r><w:rPr><w:sz w:val="20"/></w:rPr><w:t>1</w:t></w:r>'
          '<w:r><w:rPr><w:sz w:val="20"/></w:rPr><w:fldChar w:fldCharType="end"/></w:r></w:p></w:ftr>')

# A4, marges de 2,5 cm, numéro de page en pied de page sauf sur la première page (page de garde).
SECTPR = ('<w:sectPr><w:footerReference w:type="default" r:id="rIdFooter1"/>'
          '<w:footnotePr><w:numRestart w:val="eachSect"/></w:footnotePr>'
          '<w:pgSz w:w="11906" w:h="16838"/>'
          '<w:pgMar w:top="1418" w:right="1418" w:bottom="1418" w:left="1418" w:header="709" w:footer="709" w:gutter="0"/>'
          '<w:titlePg/></w:sectPr>')


def reference_docx(pd: str) -> Path:
    """Modèle Word dérivé de celui de Pandoc : styles académiques, A4, pied de page numéroté."""
    ref = OUT / "reference.docx"
    raw = subprocess.run([pd, "--print-default-data-file", "reference.docx"], capture_output=True, check=True).stdout
    tmp = OUT / "_ref_default.docx"
    tmp.write_bytes(raw)
    with zipfile.ZipFile(tmp) as zin, zipfile.ZipFile(ref, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename == "word/document.xml":
                data = re.sub(r"<w:sectPr>.*?</w:sectPr>", SECTPR, data.decode("utf-8"), flags=re.S).encode("utf-8")
            elif item.filename == "word/styles.xml":
                data = _patch_styles(data.decode("utf-8")).encode("utf-8")
            elif item.filename == "word/settings.xml":
                # Texte justifié : ne pas étirer les lignes terminées par un retour à la ligne forcé
                # (réponses du LLM reproduites ligne par ligne en annexe C).
                data = data.decode("utf-8").replace("<w:rsids>", "<w:compat><w:doNotExpandShiftReturn/></w:compat><w:rsids>",
                                                    1).encode("utf-8")
            elif item.filename == "word/_rels/document.xml.rels":
                data = data.decode("utf-8").replace(
                    "</Relationships>", '<Relationship Id="rIdFooter1" Target="footer1.xml" Type="http://schemas.'
                    'openxmlformats.org/officeDocument/2006/relationships/footer"/></Relationships>').encode("utf-8")
            elif item.filename == "[Content_Types].xml":
                data = data.decode("utf-8").replace(
                    "</Types>", '<Override PartName="/word/footer1.xml" ContentType="application/vnd.openxmlformats-'
                    'officedocument.wordprocessingml.footer+xml"/></Types>').encode("utf-8")
            zout.writestr(item, data)
        zout.writestr("word/footer1.xml", FOOTER)
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
    # Pas d'option --toc : la table des matières est un champ Word placé dans rapport.md, après la page de garde.
    subprocess.run([pd, str(full), "-o", str(out), f"--reference-doc={reference_docx(pd)}",
                    f"--resource-path={OUT}", "--from=markdown+tex_math_dollars+lists_without_preceding_blankline"], check=True, cwd=OUT)
    full.unlink()
    print("écrit :", out.relative_to(ROOT))
    if sys.platform == "win32":
        to_pdf(out)


if __name__ == "__main__":
    main()
