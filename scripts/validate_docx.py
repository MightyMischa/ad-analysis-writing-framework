#!/usr/bin/env python3
"""Validiert eine generierte DOCX gegen die IU-Format-Vorgaben.

Prüft die kritischen Reviewer-Punkte aus LESSONS.md:
  F1  DIN A4 in jeder Sektion
  F2  Heading 1/2/3 schwarz
  F3  Body-Zeilenabstand 1,5 (line=360)
  F4  Lit-Verz hängender Einzug 1,27 cm
  F5  Drei pgNumType-Sektionen (upperRoman + decimal)
  F6  Heading-1-Anker für Inhalts-/Abkürzungs-/Literaturverzeichnis
  F7  Tabellenverzeichnis-Field falls Tabellen mit SEQ
  F9  Abgabedatum gesetzt (kein Platzhalter)
  S*  Sprach-Pitfalls (dreier, die SEPA, ein solches, Countering the Financing)

Aufruf:
  python3 scripts/validate_docx.py output/phase-07-docx/<datei>.docx [--strict]

`--strict` lässt das Skript bei jedem Fund mit Exit-Code 1 enden, sonst nur Warnungen.

Begründung jedes Checks: siehe LESSONS.md im Repo-Root.
"""

import sys
import re
import zipfile
import argparse
from pathlib import Path


# ----- Helpers ---------------------------------------------------------------

def read_xml(zf: zipfile.ZipFile, name: str) -> str:
    try:
        return zf.read(name).decode("utf-8")
    except KeyError:
        return ""


def doc_text(document_xml: str) -> str:
    """Strip all XML tags to get a flat plain-text view of the body."""
    text = document_xml.replace("</w:p>", "\n")
    text = re.sub(r"<[^>]+>", "", text)
    return text


# ----- Format-Checks --------------------------------------------------------

def check_din_a4(doc_xml: str):
    sizes = re.findall(r'<w:pgSz w:w="(\d+)" w:h="(\d+)"', doc_xml)
    if not sizes:
        return ["F1: kein <w:pgSz> gefunden"]
    bad = [(w, h) for w, h in sizes if (w, h) != ("11906", "16838")]
    if bad:
        return [f"F1: Sektion mit Nicht-A4-Format gefunden: {bad}"]
    return []


def check_heading_colors(styles_xml: str):
    issues = []
    for hname in ("Heading1", "Heading2", "Heading3"):
        m = re.search(
            r'<w:style [^>]*styleId="' + hname + r'".*?</w:style>',
            styles_xml,
            re.DOTALL,
        )
        if not m:
            issues.append(f"F2: Style {hname} nicht gefunden")
            continue
        block = m.group(0)
        color = re.search(r'<w:color [^/]*/>', block)
        if not color:
            issues.append(f"F2: {hname} hat keine explizite Farbe (wird vermutlich blau gerendert)")
            continue
        if 'val="000000"' not in color.group(0):
            issues.append(f"F2: {hname} ist nicht schwarz: {color.group(0)}")
    return issues


def check_body_line_spacing(doc_xml: str):
    """Erwartet: Mehrheit der Body-Paragraphen mit line=360 (1,5-zeilig)."""
    spacings = re.findall(r"<w:spacing[^/]*/>", doc_xml)
    counts = {"line=360": 0, "line=276": 0, "line=240": 0, "andere": 0, "ohne": 0}
    for sp in spacings:
        line_match = re.search(r'line="(\d+)"', sp)
        if not line_match:
            counts["ohne"] += 1
            continue
        v = line_match.group(1)
        if v == "360":
            counts["line=360"] += 1
        elif v == "276":
            counts["line=276"] += 1
        elif v == "240":
            counts["line=240"] += 1
        else:
            counts["andere"] += 1
    issues = []
    if counts["line=360"] == 0:
        issues.append(
            f"F3: Kein Paragraph mit 1,5-zeiligem Abstand gefunden (line=360). Spacing-Verteilung: {counts}"
        )
    elif counts["line=276"] > counts["line=360"] * 0.5:
        issues.append(
            f"F3: Auffällig viele Paragraphen mit 1,15-zeilig statt 1,5: {counts}. "
            "Body-Paragraphen sollten line=360 haben."
        )
    return issues


def check_hanging_indent(doc_xml: str):
    hangings = set(re.findall(r'hanging="(\d+)"', doc_xml))
    if not hangings:
        return ["F4: Kein hängender Einzug gefunden — Lit-Verz formatiert korrekt?"]
    if "720" not in hangings:
        return [f"F4: Lit-Verz-Einzug nicht 1,27 cm (720 Twips). Gefunden: {hangings}"]
    return []


def check_page_numbering(doc_xml: str):
    types = re.findall(r"<w:pgNumType[^/]*/>", doc_xml)
    if len(types) < 2:
        return [
            "F5: Weniger als 2 pgNumType-Blöcke. Erwartet: römisch im Vorspann + arabisch im Body."
        ]
    has_roman = any('fmt="upperRoman"' in t for t in types)
    has_decimal = any('fmt="decimal"' in t for t in types)
    issues = []
    if not has_roman:
        issues.append("F5: Keine römische Seitennummerierung im Vorspann gefunden.")
    if not has_decimal:
        issues.append("F5: Keine arabische Seitennummerierung im Body gefunden.")
    return issues


def check_toc_anchors(doc_xml: str):
    issues = []
    # TOC-Field vorhanden?
    if 'TOC \\o' not in doc_xml and 'instrText>TOC' not in doc_xml:
        issues.append("F6: Kein TOC-Field im Dokument gefunden.")
    # Headings für Verzeichnisse
    headings_with_h1 = doc_xml.count('<w:pStyle w:val="Heading1"/>')
    if headings_with_h1 < 4:
        issues.append(
            f"F6: Nur {headings_with_h1} Heading-1-Paragraphen — Inhalts-/Abk-/Lit-Verz "
            "und Hauptkapitel sollten alle Heading 1 sein."
        )
    return issues


def check_table_of_tables(doc_xml: str):
    has_seq = "SEQ Tabelle" in doc_xml
    has_toc_table = re.search(r'TOC[^"]*\\c\s*"Tabelle"', doc_xml) is not None
    if has_seq and not has_toc_table:
        return ["F7: Tabelle mit SEQ-Field gefunden, aber kein Tabellenverzeichnis-Field."]
    return []


def check_abgabedatum(doc_xml: str):
    text = doc_text(doc_xml)
    if "[Abgabedatum" in text or "Abgabedatum ergänzen" in text:
        return ["F9: Abgabedatum ist Platzhalter — config.yaml/abgabe.datum füllen."]
    return []


# ----- Sprach-Pitfalls ------------------------------------------------------

LANG_PITFALLS = [
    ("S1", "anhand drei typischer", "Genitiv: 'anhand dreier typischer …'"),
    ("S1", "anhand drei ", "Verdacht auf 'anhand drei …' statt 'anhand dreier …'"),
    ("S2", "der Single Euro Payments Area", "SEPA = die Area, also 'die Single Euro Payments Area'"),
    ("S2", "des Single Euro Payments Area", "SEPA = die Area"),
    ("S3", "so ein Szenario", "umgangssprachlich; 'ein solches Szenario'"),
    ("S4", "Counter-Financing of Terrorism", "Korrekt: 'Countering the Financing of Terrorism'"),
]


def check_language_pitfalls(doc_xml: str):
    text = doc_text(doc_xml)
    issues = []
    for sid, needle, hint in LANG_PITFALLS:
        if needle in text:
            issues.append(f"{sid}: '{needle}' im Text gefunden — {hint}")
    return issues


# ----- Inhalt-Lessons (Aktualität) ------------------------------------------

CONTENT_PITFALLS = [
    (
        "I1",
        re.compile(r"\b114\s+Staaten\b"),
        "Atlantic-Council-Zahl 114 ist Stand 2023. Aktuell: 137 Länder/Währungsräume.",
    ),
    (
        "I2",
        re.compile(r"eNaira\s+[^.]*?weltweit\s+erste"),
        "eNaira ist NICHT die weltweit erste CBDC. Sand Dollar (Bahamas) ging 20.10.2020 live.",
    ),
]


def check_content_actuality(doc_xml: str):
    text = doc_text(doc_xml)
    issues = []
    for cid, pattern, hint in CONTENT_PITFALLS:
        if pattern.search(text):
            issues.append(f"{cid}: {hint}")
    return issues


# ----- Course-Book-Presence (C1) --------------------------------------------

def _read_config_field(repo_root: Path, dotted_key: str) -> str:
    """Liest ein dotted-key Feld aus config.yaml ohne YAML-Lib-Dependency.

    Akzeptiert nur primitive String-Werte. Genug für kurs_modul/kurs_titel.
    """
    cfg_path = repo_root / "config.yaml"
    if not cfg_path.exists():
        return ""
    keys = dotted_key.split(".")
    indent_stack: list[tuple[int, str]] = []
    target_depth = len(keys)
    try:
        for raw in cfg_path.read_text(encoding="utf-8").splitlines():
            stripped = raw.lstrip()
            if not stripped or stripped.startswith("#"):
                continue
            depth = (len(raw) - len(stripped)) // 2
            indent_stack = [(d, k) for d, k in indent_stack if d < depth]
            if ":" not in stripped:
                continue
            key, _, value = stripped.partition(":")
            key = key.strip()
            value = value.strip()
            indent_stack.append((depth, key))
            path = [k for _, k in indent_stack]
            if path == keys and value:
                return value.strip().strip('"').strip("'")
    except (OSError, UnicodeDecodeError):
        return ""
    return ""


def check_course_book_presence(doc_xml: str, repo_root: Path):
    """C1: Wenn projekt.kurs_modul gesetzt ist, muss mindestens eine Inline-
    Citation oder Lit-Verz-Eintrag das Course-Book referenzieren.

    Heuristik: 'IU Internationale Hochschule', 'IU [Modulkürzel]', oder
    Modulkürzel im Volltext.
    """
    kurs_modul = _read_config_field(repo_root, "projekt.kurs_modul")
    kurs_titel = _read_config_field(repo_root, "projekt.kurs_titel")
    typ = _read_config_field(repo_root, "projekt.typ")
    if not kurs_modul:
        if typ == "fallstudie":
            return [
                "C1: projekt.kurs_modul fehlt in config.yaml — bei Fallstudien Pflicht."
            ]
        return []
    text = doc_text(doc_xml)
    needles = [
        kurs_modul,
        "IU Internationale Hochschule",
        "Lernskript",
    ]
    if kurs_titel:
        needles.append(kurs_titel)
    if not any(n in text for n in needles if n):
        return [
            f"C1: Keine Course-Book-Referenz gefunden (gesucht: '{kurs_modul}', "
            "'IU Internationale Hochschule', 'Lernskript'). Bei Fallstudien Pflicht."
        ]
    return []


# ----- Methodengrenzen-Pflichtcheck (M1) ------------------------------------

METHOD_LIMIT_MARKERS = [
    re.compile(r"qualitativ\w*\s+(Sekundär|Inhalts|Literatur)"),
    re.compile(r"keine\s+Vollerhebung"),
    re.compile(r"Stichprobe\w*\s+\w+\s+(begrenz|klein)"),
    re.compile(r"setzen\s+empirische\s+Daten\s+\w+\s+\w+\s+voraus"),
    re.compile(r"methodische\s+(Limitation|Grenze)"),
    re.compile(r"beanspruch\w+\s+(jedoch\s+)?keine\s+(Vollerhebung|Repräsentativität)"),
    re.compile(r"exempl\w+\s+\w+\b", re.IGNORECASE),  # "exemplarisch", "exemplarische Auswahl"
]


def check_methodengrenzen(doc_xml: str):
    """M1: Fazit-Kapitel muss mindestens einen Methodengrenzen-Marker enthalten."""
    text = doc_text(doc_xml)
    fazit_match = re.search(
        r"(?:^|\n)\s*(?:\d+\.?\s*)?Fazit\b(.*?)(?:Literaturverzeichnis|\Z)",
        text,
        re.DOTALL | re.IGNORECASE,
    )
    if not fazit_match:
        return []  # Kein Fazit-Kapitel — nicht in Scope
    fazit_text = fazit_match.group(1)
    if any(m.search(fazit_text) for m in METHOD_LIMIT_MARKERS):
        return []
    return [
        "M1: Fazit enthält keinen Methodengrenzen-Marker — "
        "kritische Reflexion fehlt (z. B. 'qualitative Sekundärquellenanalyse', "
        "'beanspruchen keine Vollerhebung', 'setzen empirische Daten voraus')."
    ]


# ----- Number-Source-Uniqueness (N1) ----------------------------------------

CONCRETE_NUMBER_RE = re.compile(
    # Tausender-Trenner: 919.000, 1.234.567 — explizit mehrere Punkt/Leerzeichen-Gruppen
    r"\b\d{1,3}(?:[.\s]\d{3}){1,}\b"
    # ODER Zahl mit Mio/Mrd/Prozent-Marker (auch dezimal)
    r"|\b\d+(?:[,.]\d+)?\s*(?:Mio|Mrd|Prozent|%)\b"
)
COMPOUND_CITATION_RE = re.compile(r"\(([^()]+;[^()]+)\)")


def check_number_source_uniqueness(doc_xml: str, proximity_chars: int = 220):
    """N1: Konkrete Zahlen sollten nicht mit ZWEI Quellen co-zitiert sein,
    weil das Mehrdeutigkeit zur Primaerquelle erzeugt (Reviewer-Pitfall).

    Heuristik: fuer jede Compound-Citation (Klammer mit Semikolon-Trenner und
    mindestens zwei verschiedenen Erstautor:innen) pruefe, ob in den letzten
    `proximity_chars` Zeichen davor eine konkrete Zahl mit Tausender-Trenner
    oder Mio/Mrd/Prozent-Marker steht. Treffer => N1-Warnung.
    """
    text = doc_text(doc_xml)
    issues: list[str] = []
    seen_snippets: set[str] = set()
    for m in COMPOUND_CITATION_RE.finditer(text):
        cite_body = m.group(1)
        if cite_body.strip().lower().startswith(("vgl.", "siehe", "u. a.", "u.a.")):
            continue
        parts = [p.strip() for p in cite_body.split(";")]
        first_authors = [
            re.sub(r"\s*,\s*\d{4}.*$", "", p).strip().lower() for p in parts
        ]
        if len(set(first_authors)) < 2:
            continue
        # Lookback: gibt es eine konkrete Zahl im Satz davor?
        start = max(0, m.start() - proximity_chars)
        window = text[start : m.start()]
        if not CONCRETE_NUMBER_RE.search(window):
            continue
        snippet = (window[-100:] + m.group(0))[:200].replace("\n", " ").strip()
        if snippet in seen_snippets:
            continue
        seen_snippets.add(snippet)
        issues.append(
            f"N1: Konkrete Zahl in Naehe einer Compound-Citation — "
            f"Primaerquelle eindeutig zuordnen. Stelle: «...{snippet}»"
        )
    return issues


# ----- Main ------------------------------------------------------------------

def validate(docx_path: Path, repo_root: Path | None = None):
    if not docx_path.exists():
        print(f"FEHLER: Datei {docx_path} nicht gefunden", file=sys.stderr)
        return [f"Datei nicht gefunden: {docx_path}"]

    if repo_root is None:
        repo_root = Path.cwd()

    with zipfile.ZipFile(docx_path) as zf:
        document_xml = read_xml(zf, "word/document.xml")
        styles_xml = read_xml(zf, "word/styles.xml")

    issues = []
    issues.extend(check_din_a4(document_xml))
    issues.extend(check_heading_colors(styles_xml))
    issues.extend(check_body_line_spacing(document_xml))
    issues.extend(check_hanging_indent(document_xml))
    issues.extend(check_page_numbering(document_xml))
    issues.extend(check_toc_anchors(document_xml))
    issues.extend(check_table_of_tables(document_xml))
    issues.extend(check_abgabedatum(document_xml))
    issues.extend(check_language_pitfalls(document_xml))
    issues.extend(check_content_actuality(document_xml))
    issues.extend(check_course_book_presence(document_xml, repo_root))
    issues.extend(check_methodengrenzen(document_xml))
    issues.extend(check_number_source_uniqueness(document_xml))
    return issues


def main():
    ap = argparse.ArgumentParser(
        description="Validiert eine DOCX gegen IU-Format- und Inhalts-Vorgaben.",
    )
    ap.add_argument("docx", type=Path, help="Pfad zur DOCX-Datei")
    ap.add_argument("--strict", action="store_true", help="Exit 1 bei Funden")
    args = ap.parse_args()

    issues = validate(args.docx)
    if not issues:
        print(f"✓ {args.docx.name}: keine Verstöße gegen IU-Vorgaben.")
        return 0

    print(f"⚠ {args.docx.name}: {len(issues)} Verstöße gegen IU-Vorgaben")
    print()
    for i, msg in enumerate(issues, 1):
        print(f"  {i:2d}. {msg}")
    print()
    print("Begründung jedes Codes (F1, F2, ...) steht in LESSONS.md (Repo-Root).")
    return 1 if args.strict else 0


if __name__ == "__main__":
    sys.exit(main())
