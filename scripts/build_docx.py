#!/usr/bin/env python3
"""Kanonischer IU-DOCX-Builder (config-parametrisiert).

Baut aus den fertigen Kapiteln (output/phase-05-writing/final/*.md) ein
IU-formatkonformes DOCX: DIN A4, 2 cm Ränder, Arial 11/1,5, schwarze
Überschriften, römische/arabische Seitenzählung, TOC-/Tabellen-/Abkürzungs-/
Literaturverzeichnis, hängender Einzug im Lit-Verz.

Alle projektspezifischen Werte kommen aus config.yaml — keine hartcodierten
Namen/Kurse/Pfade mehr (Vorgänger: fallstudie-blockchain/scripts/build_iu_docx.py).

Aufruf:
    python3 scripts/build_docx.py [PROJEKT_DIR]
    (ohne Argument: aktuelles Arbeitsverzeichnis)

Optionale Projekt-Dateien:
    output/terminology.md   # Abkürzungen (## Abkürzungen, dann "- ABK — Bedeutung")
    output/tables.yaml       # {"3.4": "Caption-Text"} → Tabellen-Beschriftungen je Abschnitt
"""
import re
import sys
import subprocess
import shutil
import yaml
from pathlib import Path
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_LINE_SPACING, WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.enum.section import WD_SECTION
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

# ========== Projekt + Config ==========

PROJECT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path.cwd()
config = yaml.safe_load((PROJECT / "config.yaml").read_text()) or {}


def cfg(path, default=None):
    """Liest verschachtelten config-Wert per Punkt-Pfad, mit Fallback."""
    cur = config
    for key in path.split("."):
        if isinstance(cur, dict) and cur.get(key) is not None:
            cur = cur[key]
        else:
            return default
    return cur


# Titelblatt-Metadaten
autor_name = cfg("autor.name", "")
matrikel = cfg("autor.matrikelnummer", "")
hochschule = cfg("autor.hochschule", "IU Internationale Hochschule")
studiengang = cfg("autor.studiengang", "")
erstgut = cfg("betreuung.erstgutachter", "")
titel = cfg("projekt.titel", "")
abgabedat = cfg("abgabe.datum") or "[Abgabedatum ergänzen]"
kurs_code = cfg("projekt.kurs_modul", "")
kurs_name = cfg("projekt.kurs_titel", "")
semester = cfg("projekt.semester", "")
typ = (cfg("projekt.typ", "fallstudie") or "fallstudie")
pruefungsform = "Fallstudie" if typ == "fallstudie" else typ.capitalize()

# Formatierung (IU-Defaults)
FONT = cfg("formatierung.schriftart", "Arial")
FSIZE = int(cfg("formatierung.schriftgroesse", 11))
LINESP = float(cfg("formatierung.zeilenabstand", 1.5))
M_TOP = float(cfg("formatierung.seitenränder.oben", 2.0))
M_BOT = float(cfg("formatierung.seitenränder.unten", 2.0))
M_LEFT = float(cfg("formatierung.seitenränder.links", 2.0))
M_RIGHT = float(cfg("formatierung.seitenränder.rechts", 2.0))

# Verzeichnisse
SHOW_TOC = cfg("verzeichnisse.inhaltsverzeichnis", True)
SHOW_TAB = cfg("verzeichnisse.tabellenverzeichnis", False)
SHOW_ABK = cfg("verzeichnisse.abkuerzungsverzeichnis", True)
SHOW_LIT = cfg("verzeichnisse.literaturverzeichnis", True)

# Logo (config → Auto-Detect → keins)
logo_rel = cfg("logo.pfad", "")
LOGO = (PROJECT / logo_rel) if logo_rel else None
if not (LOGO and LOGO.exists()):
    LOGO = None
    for cand in ("iu-logo.png", "logo.png", "logo.jpg", "logo.jpeg"):
        p = PROJECT / "assets" / "img" / cand
        if p.exists():
            LOGO = p
            break

# Tabellen-Captions (optional)
TABLE_CAPTIONS = {}
_tables_file = PROJECT / "output" / "tables.yaml"
if _tables_file.exists():
    TABLE_CAPTIONS = yaml.safe_load(_tables_file.read_text()) or {}

CHAP_DIR = PROJECT / "output" / "phase-05-writing" / "final"
OUTPUT = PROJECT / "output" / "phase-07-docx"
OUTPUT.mkdir(parents=True, exist_ok=True)

# ========== Helper ==========

def set_font(run, name=None, size=None, bold=False, italic=False):
    name = name or FONT
    size = size or FSIZE
    run.font.name = name
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.italic = italic
    rPr = run._element.get_or_add_rPr()
    rFonts = rPr.find(qn("w:rFonts"))
    if rFonts is None:
        rFonts = OxmlElement("w:rFonts")
        rPr.append(rFonts)
    for attr in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
        rFonts.set(qn(attr), name)


def add_para(doc, text, bold=False, italic=False, size=None, align=None,
             space_before=0, space_after=0, line_spacing=None):
    p = doc.add_paragraph()
    if align is not None:
        p.alignment = align
    pf = p.paragraph_format
    pf.line_spacing = line_spacing or LINESP
    pf.space_before = Pt(space_before)
    pf.space_after = Pt(space_after)
    for i, line in enumerate(text.split("\n")):
        if i > 0:
            p.add_run().add_break()
        set_font(p.add_run(line), FONT, size, bold, italic)
    return p


def add_empty_para(doc, count=1, size=None):
    for _ in range(count):
        p = doc.add_paragraph()
        p.paragraph_format.line_spacing = 1.15
        set_font(p.add_run(), FONT, size)


def add_page_break(doc):
    p = doc.add_paragraph()
    p.add_run().add_break(WD_BREAK.PAGE)


def set_margins(section):
    section.page_width = Cm(21.0)
    section.page_height = Cm(29.7)
    section.top_margin = Cm(M_TOP)
    section.bottom_margin = Cm(M_BOT)
    section.left_margin = Cm(M_LEFT)
    section.right_margin = Cm(M_RIGHT)


def set_page_number_format(section, fmt="decimal", start=None):
    sectPr = section._sectPr
    pgNumType = sectPr.find(qn("w:pgNumType"))
    if pgNumType is None:
        pgNumType = OxmlElement("w:pgNumType")
        sectPr.append(pgNumType)
    pgNumType.set(qn("w:fmt"), fmt)
    if start is not None:
        pgNumType.set(qn("w:start"), str(start))


def add_page_number_footer(section):
    footer = section.footer
    for para in footer.paragraphs:
        para.clear()
    p = footer.paragraphs[0] if footer.paragraphs else footer.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run()
    set_font(run, FONT, FSIZE)
    fld1 = OxmlElement("w:fldChar")
    fld1.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = "PAGE"
    fld2 = OxmlElement("w:fldChar")
    fld2.set(qn("w:fldCharType"), "end")
    run._element.append(fld1)
    run._element.append(instr)
    run._element.append(fld2)


def add_field(run, instr_text, placeholder):
    """Word-Feld (TOC/SEQ) mit Platzhalter einfügen."""
    fc1 = OxmlElement("w:fldChar"); fc1.set(qn("w:fldCharType"), "begin")
    it = OxmlElement("w:instrText"); it.set(qn("xml:space"), "preserve"); it.text = instr_text
    sep = OxmlElement("w:fldChar"); sep.set(qn("w:fldCharType"), "separate")
    ph = OxmlElement("w:t"); ph.text = placeholder
    end = OxmlElement("w:fldChar"); end.set(qn("w:fldCharType"), "end")
    for el in (fc1, it, sep, ph, end):
        run._element.append(el)


# ========== Dokument-Grundgerüst ==========

doc = Document()
for section in doc.sections:
    set_margins(section)

for h_name, h_size in (("Heading 1", 16), ("Heading 2", 14), ("Heading 3", 11)):
    style = doc.styles[h_name]
    style.font.color.rgb = RGBColor(0, 0, 0)
    style.font.name = FONT
    style.font.size = Pt(h_size)
    style.font.bold = True

try:
    toc1 = doc.styles["TOC 1"]
except KeyError:
    from docx.enum.style import WD_STYLE_TYPE
    toc1 = doc.styles.add_style("TOC 1", WD_STYLE_TYPE.PARAGRAPH)
toc1.font.bold = True
toc1.font.name = FONT
toc1.font.size = Pt(FSIZE)
toc1.font.color.rgb = RGBColor(0, 0, 0)

normal = doc.styles["Normal"]
normal.font.name = FONT
normal.font.size = Pt(FSIZE)
_rPr = normal.element.get_or_add_rPr()
_rFonts = _rPr.find(qn("w:rFonts"))
if _rFonts is None:
    _rFonts = OxmlElement("w:rFonts")
    _rPr.append(_rFonts)
for _a in ("w:ascii", "w:hAnsi", "w:cs"):
    _rFonts.set(qn(_a), FONT)
normal.paragraph_format.line_spacing = LINESP
normal.paragraph_format.space_before = Pt(0)
normal.paragraph_format.space_after = Pt(0)

# ========== Titelblatt ==========

section0 = doc.sections[0]
section0.different_first_page_header_footer = True
add_empty_para(doc, 1)

if LOGO:
    p_logo = doc.add_paragraph()
    p_logo.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_logo.add_run().add_picture(str(LOGO), width=Cm(10))

add_para(doc, hochschule, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER)
add_empty_para(doc, 3)
add_para(doc, f"Prüfungsform: {pruefungsform}", bold=True, align=WD_ALIGN_PARAGRAPH.CENTER)
add_empty_para(doc, 1)
add_para(doc, titel, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER)
add_empty_para(doc, 1)
add_para(doc, f"Verfasser: {autor_name}", bold=True, align=WD_ALIGN_PARAGRAPH.CENTER)
add_empty_para(doc, 2)

modul_zeile = f"Modul: {kurs_code}" + (f" – {kurs_name}" if kurs_name else "")
for zeile in (
    modul_zeile,
    f"Tutor: {erstgut}" if erstgut else None,
    f"Semester: {semester}" if semester else None,
    f"Studiengang: {studiengang}" if studiengang else None,
    f"Matrikelnummer: {matrikel}",
    f"Eingereicht am: {abgabedat}",
):
    if zeile:
        add_para(doc, zeile, bold=True, align=WD_ALIGN_PARAGRAPH.LEFT)

# ========== Frontmatter (römisch) ==========

fm = doc.add_section(WD_SECTION.NEW_PAGE)
set_margins(fm)
set_page_number_format(fm, fmt="upperRoman", start=2)
fm.footer.is_linked_to_previous = False
add_page_number_footer(fm)
section0.footer.is_linked_to_previous = False

if SHOW_TOC:
    p_toc_title = doc.add_paragraph()
    p_toc_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_toc_title.style = doc.styles["Heading 1"]
    r = p_toc_title.add_run("Inhaltsverzeichnis")
    set_font(r, FONT, 14, bold=True); r.font.color.rgb = RGBColor(0, 0, 0)
    p_toc_title.paragraph_format.space_after = Pt(18)
    r = doc.add_paragraph().add_run(); set_font(r, FONT, FSIZE)
    add_field(r, r'TOC \o "1-3" \h \z \u',
              "Rechtsklick → Feld aktualisieren, um das Inhaltsverzeichnis anzuzeigen.")

if SHOW_TAB:
    add_empty_para(doc, 1)
    p_tab_title = doc.add_paragraph()
    rr = p_tab_title.add_run("Tabellenverzeichnis")
    set_font(rr, FONT, 14, bold=True); rr.font.color.rgb = RGBColor(0, 0, 0)
    p_tab_title.paragraph_format.space_before = Pt(18)
    p_tab_title.paragraph_format.space_after = Pt(12)
    r = doc.add_paragraph().add_run(); set_font(r, FONT, FSIZE)
    add_field(r, r'TOC \h \z \c "Tabelle"',
              "Rechtsklick → Feld aktualisieren, um das Tabellenverzeichnis anzuzeigen.")

term_file = PROJECT / "output" / "terminology.md"
if SHOW_ABK and term_file.exists():
    add_page_break(doc)
    p_abk_title = doc.add_paragraph()
    p_abk_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_abk_title.style = doc.styles["Heading 1"]
    r = p_abk_title.add_run("Abkürzungsverzeichnis")
    set_font(r, FONT, 14, bold=True); r.font.color.rgb = RGBColor(0, 0, 0)
    p_abk_title.paragraph_format.space_after = Pt(18)
    term_content = term_file.read_text()
    abk_match = re.search(r"## Abk.rzungen.*?\n(.+?)(?=\n##|\Z)", term_content, re.DOTALL)
    abk_lines = re.findall(r"^- (\S+)\s+[—-]+\s+(.+)$", abk_match.group(1), re.MULTILINE) if abk_match else []
    if abk_lines:
        table = doc.add_table(rows=len(abk_lines), cols=2)
        table.autofit = False
        for row in table.rows:
            row.cells[0].width = Cm(4)
            row.cells[1].width = Cm(13)
        for i, (abk, bedeut) in enumerate(abk_lines):
            c0 = table.rows[i].cells[0]; c0.text = ""
            set_font(c0.paragraphs[0].add_run(abk), FONT, FSIZE, bold=True)
            c1 = table.rows[i].cells[1]; c1.text = ""
            set_font(c1.paragraphs[0].add_run(bedeut), FONT, FSIZE)

# ========== Body (arabisch) ==========

body = doc.add_section(WD_SECTION.NEW_PAGE)
set_margins(body)
set_page_number_format(body, fmt="decimal", start=1)
body.footer.is_linked_to_previous = False
add_page_number_footer(body)


def add_table_caption(doc, table_index, caption_text):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    pf = p.paragraph_format
    pf.line_spacing = 1.15; pf.space_before = Pt(2); pf.space_after = Pt(8)
    try:
        p.style = doc.styles["Caption"]
    except KeyError:
        pass
    r1 = p.add_run("Tabelle "); set_font(r1, FONT, 10, bold=True); r1.font.color.rgb = RGBColor(0, 0, 0)
    r_seq = p.add_run(); set_font(r_seq, FONT, 10, bold=True); r_seq.font.color.rgb = RGBColor(0, 0, 0)
    add_field(r_seq, r" SEQ Tabelle \* ARABIC ", str(table_index))
    r2 = p.add_run(f": {caption_text}"); set_font(r2, FONT, 10); r2.font.color.rgb = RGBColor(0, 0, 0)


def add_markdown_table(doc, header_cells, body_rows, caption=None, table_index=1):
    table = doc.add_table(rows=1 + len(body_rows), cols=len(header_cells))
    table.autofit = True
    for j, txt in enumerate(header_cells):
        cell = table.rows[0].cells[j]; cell.text = ""
        p = cell.paragraphs[0]; p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.line_spacing = 1.15
        run = p.add_run(txt.strip()); set_font(run, FONT, FSIZE, bold=True)
        run.font.color.rgb = RGBColor(0, 0, 0)
    for i, row in enumerate(body_rows, start=1):
        for j, txt in enumerate(row):
            cell = table.rows[i].cells[j]; cell.text = ""
            p = cell.paragraphs[0]; p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            p.paragraph_format.line_spacing = 1.15
            run = p.add_run(txt.strip()); set_font(run, FONT, FSIZE)
            run.font.color.rgb = RGBColor(0, 0, 0)
    tbl = table._tbl
    tblPr = tbl.find(qn("w:tblPr"))
    tblBorders = OxmlElement("w:tblBorders")
    for edge in ("top", "bottom"):
        b = OxmlElement(f"w:{edge}")
        b.set(qn("w:val"), "single"); b.set(qn("w:sz"), "8"); b.set(qn("w:color"), "000000")
        tblBorders.append(b)
    for edge in ("left", "right", "insideV"):
        b = OxmlElement(f"w:{edge}"); b.set(qn("w:val"), "nil")
        tblBorders.append(b)
    insideH = OxmlElement("w:insideH")
    insideH.set(qn("w:val"), "single"); insideH.set(qn("w:sz"), "4"); insideH.set(qn("w:color"), "000000")
    tblBorders.append(insideH)
    tblPr.append(tblBorders)
    if caption:
        add_table_caption(doc, table_index, caption)


def process_chapter_line(doc, line):
    if not line.strip():
        return
    h_match = re.match(r"^(#+)\s+(.+)$", line)
    if h_match:
        level = len(h_match.group(1))
        text = h_match.group(2).strip()
        adj_level = max(1, level - 1)
        size = {1: 16, 2: 14, 3: 11}.get(adj_level, 11)
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        pf = p.paragraph_format
        pf.space_before = Pt(12); pf.space_after = Pt(12 if adj_level == 1 else 6); pf.line_spacing = 1.15
        p.add_run(text)
        p.style = doc.styles[f"Heading {min(adj_level, 3)}"]
        for r in p.runs:
            set_font(r, FONT, size, bold=True); r.font.color.rgb = RGBColor(0, 0, 0)
        return
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    pf = p.paragraph_format
    pf.line_spacing = LINESP; pf.space_before = Pt(0); pf.space_after = Pt(6)
    for part in re.split(r"(\*\*[^*]+\*\*|\*[^*]+\*)", line):
        if not part:
            continue
        if part.startswith("**") and part.endswith("**"):
            set_font(p.add_run(part[2:-2]), FONT, FSIZE, bold=True)
        elif part.startswith("*") and part.endswith("*"):
            set_font(p.add_run(part[1:-1]), FONT, FSIZE, italic=True)
        else:
            set_font(p.add_run(part), FONT, FSIZE)


all_chapter_text = ""
for cf in sorted(CHAP_DIR.glob("*.md")):
    content = re.sub(r"^---\n.*?\n---\n", "", cf.read_text(), count=1, flags=re.DOTALL)
    all_chapter_text += content + "\n\n"

table_counter = 0
last_section_id = None
for para in re.split(r"\n\s*\n", all_chapter_text):
    para = para.strip()
    if not para:
        continue
    sec_match = re.match(r"^###\s+(\d+(?:\.\d+)?)", para)
    if sec_match:
        last_section_id = sec_match.group(1)
    if para.startswith("|") and re.search(r"^\|[\s:|-]+\|\s*$", para, flags=re.MULTILINE):
        rows = [r for r in para.split("\n") if r.strip().startswith("|")]
        rows = [r for r in rows if not re.match(r"^\|[\s:|-]+\|\s*$", r)]
        parsed = [[c.strip() for c in r.strip().strip("|").split("|")] for r in rows]
        if len(parsed) >= 2:
            table_counter += 1
            add_markdown_table(doc, parsed[0], parsed[1:],
                               caption=TABLE_CAPTIONS.get(last_section_id), table_index=table_counter)
            continue
    lines = para.split("\n")
    if len(lines) == 1:
        process_chapter_line(doc, para)
    else:
        for h in (l for l in lines if re.match(r"^#+\s", l)):
            process_chapter_line(doc, h)
        body_lines = [l for l in lines if not re.match(r"^#+\s", l) and l.strip()]
        if body_lines:
            process_chapter_line(doc, " ".join(body_lines))

# ========== Literaturverzeichnis ==========

def parse_literature():
    lit_file = PROJECT / "sources" / "literature.md"
    if not lit_file.exists():
        return []
    content = lit_file.read_text()
    parts = re.split(r"#\s*PART 2", content, maxsplit=1)
    blocks = re.findall(r"^---\n(.+?)\n---", parts[0], re.MULTILINE | re.DOTALL)
    entries = []
    for block in blocks:
        try:
            data = yaml.safe_load(block)
            if isinstance(data, dict) and "quelle_id" in data:
                entries.append(data)
        except Exception:
            pass
    return entries


def format_authors_apa(autor_str):
    authors = [a.strip() for a in autor_str.split("/")]
    if len(authors) == 1:
        return authors[0]
    if len(authors) == 2:
        return f"{authors[0]}, & {authors[1]}"
    return ", ".join(authors[:-1]) + f", & {authors[-1]}"


def get_year_with_suffix(e):
    m = re.search(r"_(\d{4})([a-z])$", e.get("quelle_id", ""))
    return f"{e.get('jahr', '')}{m.group(2) if m else ''}"


def is_institution(autor_full):
    return "," not in autor_full.split("/")[0]


def get_used_sources(chapters_text):
    """Generisch (datengetrieben, keine hartcodierten Institutionsnamen)."""
    used = []
    for e in parse_literature():
        autor_full = e.get("autor", "")
        year = get_year_with_suffix(e)
        patterns = []
        if is_institution(autor_full):
            name = autor_full.split("/")[0].strip()
            patterns += [f"{name} ({year}", f"{name}, {year}"]
            abk = e.get("abk", "")
            if abk:
                patterns += [f"{abk} ({year}", f"{abk}, {year}", f"[{abk}] ({year}", f"[{abk}], {year}"]
        else:
            first = autor_full.split("/")[0].split(",")[0].strip()
            patterns += [f"{first} ({year}", f"{first}, {year}",
                         f"{first} et al. ({year}", f"{first} et al., {year}"]
            if "/" in autor_full:
                surnames = [a.split(",")[0].strip() for a in autor_full.split("/")]
                if len(surnames) == 2:
                    patterns += [f"{surnames[0]} & {surnames[1]} ({year}",
                                 f"{surnames[0]} & {surnames[1]}, {year}",
                                 f"{surnames[0]} und {surnames[1]} ({year}",
                                 f"{surnames[0]}/{surnames[1]} ({year}"]
                else:
                    patterns.append(f"{first} et al.")
        if any(p in chapters_text for p in patterns):
            used.append(e)
    used.sort(key=lambda e: (e.get("autor", "").split("/")[0].split(",")[0].strip().lower(),
                             e.get("quelle_id", "")))
    return used


def add_bib_entry(doc, e):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    pf = p.paragraph_format
    pf.line_spacing = LINESP; pf.space_before = Pt(0); pf.space_after = Pt(10)
    pf.left_indent = Cm(1.27); pf.first_line_indent = Cm(-1.27)

    def r_text(txt, italic=False, bold=False):
        r = p.add_run(txt); set_font(r, FONT, FSIZE, bold=bold, italic=italic)
        r.font.color.rgb = RGBColor(0, 0, 0)

    r_text(f"{format_authors_apa(e.get('autor', ''))} ({get_year_with_suffix(e)}). ")
    titel_e = e.get("titel", "")
    typ_e = e.get("quelle_typ", "")
    if typ_e == "journal":
        r_text(titel_e + ". ")
        r_text(e.get("journal", ""), italic=True)
        if e.get("jahrgang"):
            r_text(", "); r_text(str(e["jahrgang"]), italic=True)
        if e.get("ausgabe"):
            r_text(f"({e['ausgabe']})")
        if e.get("seiten"):
            r_text(f", {e['seiten']}")
        r_text(".")
    elif typ_e == "buch":
        r_text(titel_e, italic=True)
        if e.get("auflage"):
            r_text(f" ({e['auflage']}. Aufl.)")
        r_text(". ")
        if e.get("ort"):
            r_text(f"{e['ort']}: ")
        r_text(f"{e.get('verlag', '')}.")
    elif typ_e == "website":
        r_text(titel_e, italic=True); r_text(". ")
        if e.get("verlag"):
            r_text("In "); r_text(e["verlag"], italic=True); r_text(". ")
        if e.get("abruf"):
            r_text(f"Abgerufen am {e['abruf']}, von ")
        if e.get("url"):
            r_text(e["url"])
    elif typ_e == "report":
        r_text(titel_e, italic=True); r_text(". ")
        if e.get("verlag"):
            r_text(f"{e['verlag']}. ")
        if e.get("url"):
            r_text(e["url"])
    else:
        r_text(titel_e, italic=True); r_text(".")


if SHOW_LIT:
    add_page_break(doc)
    p_lit = doc.add_paragraph()
    p_lit.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p_lit.style = doc.styles["Heading 1"]
    p_lit.add_run("Literaturverzeichnis")
    p_lit.paragraph_format.space_before = Pt(12)
    p_lit.paragraph_format.space_after = Pt(18)
    for r in p_lit.runs:
        set_font(r, FONT, 16, bold=True); r.font.color.rgb = RGBColor(0, 0, 0)
    for e in get_used_sources(all_chapter_text):
        add_bib_entry(doc, e)

# ========== Speichern + PDF ==========

def slugify(text):
    s = re.sub(r"[^a-z0-9]+", "-", (text or "").lower()).strip("-")
    return s or "arbeit"


out_name = slugify(kurs_code or titel or "fallstudie")
docx_path = OUTPUT / f"{out_name}.docx"
doc.save(docx_path)
print(f"✓ DOCX gebaut: {docx_path}  ({docx_path.stat().st_size} bytes)")


def export_pdf(docx_path):
    """DOCX → PDF via LibreOffice headless (layout-identisch). Best-effort."""
    soffice = shutil.which("soffice") or shutil.which("libreoffice")
    if not soffice:
        mac = Path("/Applications/LibreOffice.app/Contents/MacOS/soffice")
        soffice = str(mac) if mac.exists() else None
    if not soffice:
        print("⚠ PDF übersprungen: LibreOffice (soffice) nicht gefunden. "
              "DOCX ist das Primärartefakt; PDF später via 'Speichern als PDF'.")
        return None
    try:
        subprocess.run([soffice, "--headless", "--convert-to", "pdf",
                        "--outdir", str(docx_path.parent), str(docx_path)],
                       check=True, capture_output=True, timeout=180)
        pdf_path = docx_path.with_suffix(".pdf")
        if pdf_path.exists():
            print(f"✓ PDF gebaut: {pdf_path}  ({pdf_path.stat().st_size} bytes)")
            return pdf_path
    except Exception as exc:
        print(f"⚠ PDF-Konvertierung fehlgeschlagen: {exc}")
    return None


export_pdf(docx_path)
print()
print("Nächste Schritte vor Abgabe:")
print("  1. DOCX öffnen, Strg+A + F9 (Felder/TOC aktualisieren)")
print("  2. Abgabedatum auf dem Titelblatt prüfen (config.yaml: abgabe.datum)")
print(f"  3. Validator: python3 scripts/validate_docx.py {docx_path}")
