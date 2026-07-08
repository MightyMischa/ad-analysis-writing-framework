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
  S1/S3  Generische Sprach-Pitfalls (dreier, ein solches)
  S4  Projektspezifische Pitfalls aus preferences.md → „Sprach-Pitfalls (Projekt)"

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
    """Erwartet: Body-Fließtext mit line=360 (1,5-zeilig).

    Präzise: Überschriften (Heading*), Verzeichnis-Einträge (TOC*), Caption und
    Tabellenzellen dürfen legitim 1,15-zeilig (line=276) sein und werden NICHT
    gezählt. Nur echte Body-Absätze mit Text fließen in die Heuristik ein.
    """
    # Tabellen komplett ausklammern (Zellen-Absätze sind kein Body-Fließtext)
    no_tables = re.sub(r"<w:tbl\b.*?</w:tbl>", "", doc_xml, flags=re.DOTALL)
    paras = re.findall(r"<w:p\b[^>]*>.*?</w:p>", no_tables, flags=re.DOTALL)
    counts = {"line=360": 0, "line=276": 0, "line=240": 0, "andere": 0, "ohne": 0}
    for para in paras:
        # Überschriften / Verzeichnis-Anker / Caption überspringen
        if re.search(r'<w:pStyle w:val="(?:Heading\d|TOC\d|Caption)"', para):
            continue
        # Leerabsätze (Spacer, ohne sichtbaren Text) überspringen
        if not re.sub(r"<[^>]+>", "", para).strip():
            continue
        line_match = re.search(r'<w:spacing[^>]*\bline="(\d+)"', para)
        if not line_match:
            # Kein explizites Spacing → erbt Normal-Style (line=360) → konform
            counts["ohne"] += 1
            continue
        v = line_match.group(1)
        if v in ("360", "276", "240"):
            counts[f"line={v}"] += 1
        else:
            counts["andere"] += 1
    issues = []
    compliant = counts["line=360"] + counts["ohne"]
    if compliant == 0 and counts["line=276"] > 0:
        issues.append(
            f"F3: Kein Body-Absatz mit 1,5-zeiligem Abstand (line=360). Verteilung: {counts}"
        )
    elif counts["line=276"] > compliant * 0.5:
        issues.append(
            f"F3: Auffällig viele Body-Absätze mit 1,15-zeilig statt 1,5: {counts}. "
            "Body-Fließtext sollte line=360 haben."
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


def _style_block(styles_xml: str, style_id: str):
    m = re.search(
        r'<w:style [^>]*w:styleId="' + style_id + r'".*?</w:style>',
        styles_xml,
        re.DOTALL,
    )
    return m.group(0) if m else None


def _style_is_bold(style_block: str) -> bool:
    """True, wenn der Style fett ist: <w:b/> vorhanden und nicht per val
    abgeschaltet (val='0'/'false'/'off')."""
    m = re.search(r"<w:b\b([^>]*)/>", style_block)
    if not m:
        return False
    val = re.search(r'w:val="([^"]+)"', m.group(1))
    return not (val and val.group(1).lower() in ("0", "false", "off"))


def check_toc_levels(styles_xml: str):
    """F6 (Teil 2): Inhaltsverzeichnis-Ebene 1 fett, Ebenen 2/3 vorhanden + nicht fett.

    Word legt TOC 2/TOC 3 beim Feld-Update sonst selbst an — mit inkonsistenter
    Fett-Optik. Der Build definiert daher TOC 1 (fett) + TOC 2/TOC 3 (nicht fett)
    explizit. python-docx serialisiert den styleId ohne Leerzeichen (TOC1/2/3).
    """
    issues = []
    toc1 = _style_block(styles_xml, "TOC1")
    if toc1 is None:
        issues.append("F6: TOC-1-Style fehlt — Inhaltsverzeichnis-Ebene 1 nicht garantiert fett.")
    elif not _style_is_bold(toc1):
        issues.append("F6: TOC-1-Style ist nicht fett (<w:b/> fehlt) — Ebene 1 muss fett sein.")
    for sid, lvl in (("TOC2", 2), ("TOC3", 3)):
        block = _style_block(styles_xml, sid)
        if block is None:
            issues.append(
                f"F6: TOC-{lvl}-Style fehlt — Word erzeugt ihn sonst selbst, "
                "der Fett/Normal-Kontrast zu Ebene 1 ist dann nicht garantiert."
            )
        elif _style_is_bold(block):
            issues.append(
                f"F6: TOC-{lvl}-Style ist fett — Ebenen 2/3 müssen normal (nicht fett) sein."
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

# Nur GENERISCHE Grammatik-Pitfalls bleiben hartcodiert. Projektspezifische
# Strings (früher S2/S4 SEPA/Counter-Financing und I1/I2 CBDC-Zahlen) stehen
# jetzt in preferences.md → „Sprach-Pitfalls (Projekt)" und werden von dort
# gelesen — damit greift der Check auch bei neuen Themen statt nie.
LANG_PITFALLS = [
    ("S1", "anhand drei typischer", "Genitiv: 'anhand dreier typischer …'"),
    ("S1", "anhand drei ", "Verdacht auf 'anhand drei …' statt 'anhand dreier …'"),
    ("S3", "so ein Szenario", "umgangssprachlich; 'ein solches Szenario'"),
]


def check_language_pitfalls(doc_xml: str):
    text = doc_text(doc_xml)
    issues = []
    for sid, needle, hint in LANG_PITFALLS:
        if needle in text:
            issues.append(f"{sid}: '{needle}' im Text gefunden — {hint}")
    return issues


# ----- Projektspezifische Pitfalls (aus preferences.md) -----------------------

def _read_pref_bullets(repo_root: Path, heading_pattern: str) -> list:
    """Bullets unter einer ##-Überschrift in preferences.md.

    Code-Fences und HTML-Kommentare werden übersprungen (dort stehen Beispiele).
    Gleiche Parser-Konvention wie scripts/lint_style.py.
    """
    pref = repo_root / "preferences.md"
    if not pref.exists():
        return []
    m = re.search(
        r"^##+\s*" + heading_pattern + r".*?$(.*?)(?=^##\s|\Z)",
        pref.read_text(encoding="utf-8"),
        re.MULTILINE | re.DOTALL | re.IGNORECASE,
    )
    if not m:
        return []
    body = re.sub(r"```.*?```", "", m.group(1), flags=re.DOTALL)
    body = re.sub(r"<!--.*?-->", "", body, flags=re.DOTALL)
    items = []
    for raw in re.findall(r"^[-*]\s+(.+?)\s*$", body, re.MULTILINE):
        item = raw.split("#", 1)[0].strip().strip("`").strip('"').strip("'").strip()
        if item:
            items.append(item)
    return items


def check_project_pitfalls(doc_xml: str, repo_root: Path):
    """S4: projektspezifische Sprach-/Fakten-Pitfalls aus preferences.md."""
    needles = _read_pref_bullets(repo_root, r"Sprach-Pitfalls")
    if not needles:
        return []
    text = doc_text(doc_xml)
    issues = []
    for needle in needles:
        if needle in text:
            issues.append(
                f"S4: '{needle}' im Text gefunden — projektspezifischer Pitfall "
                "(preferences.md → Sprach-Pitfalls)."
            )
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


# ----- Quellen-Aktualität (A1/A2, HINWEIS) ----------------------------------

def _parse_lit_blocks(repo_root: Path) -> list[dict]:
    """Minimal-Parser für literature.md PART 1 (ohne yaml-Dependency).

    Gibt je Stammdaten-Block quelle_typ/jahr/titel/reihe/autor zurück.
    """
    lit = repo_root / "sources" / "literature.md"
    if not lit.exists():
        return []
    text = re.split(r"#\s*PART 2", lit.read_text(encoding="utf-8"), maxsplit=1)[0]
    out: list[dict] = []
    for blk in re.split(r"\n---\n", "\n" + text + "\n"):
        if "quelle_id:" not in blk or re.search(r"^id:\s", blk, re.MULTILINE):
            continue

        def field(key: str) -> str:
            m = re.search(r'^' + key + r':\s*"?(.+?)"?\s*$', blk, re.MULTILINE)
            return m.group(1).strip() if m else ""

        out.append(
            {
                "quelle_typ": field("quelle_typ"),
                "jahr": field("jahr"),
                "titel": field("titel"),
                "reihe": field("reihe"),
                "autor": field("autor"),
            }
        )
    return out


def _read_aktualitaets_anker(repo_root: Path) -> list[str]:
    """Anker-Begriffe aus preferences.md (Abschnitt „Aktualitäts-Anker").

    Domänen-spezifisch und optional — fehlt der Abschnitt, gibt es keine Anker
    (das Framework selbst bleibt fachneutral).
    """
    pref = repo_root / "preferences.md"
    if not pref.exists():
        return []
    m = re.search(r"##+\s*Aktualit.ts-Anker.*?\n(.*?)(?=\n##|\Z)", pref.read_text(encoding="utf-8"), re.DOTALL)
    if not m:
        return []
    terms = []
    for raw in re.findall(r"^[-*]\s*(.+?)\s*$", m.group(1), re.MULTILINE):
        term = re.split(r"[(:–—]", raw, maxsplit=1)[0].strip()
        if len(term) >= 3:
            terms.append(term)
    return terms


def check_source_currency(repo_root: Path):
    """A1/A2 (HINWEIS, nicht blockierend): zeitkritische Quellen-Aktualität.

    A1: report/website-Quelle mit Jahr < aktuellem Jahr — evtl. neuere Auflage.
    A2: Quelle trägt einen Aktualitäts-Anker-Begriff (aus preferences.md).

    Reagiert auf den Reviewer-Pitfall „GSMA-Jahresbericht 2025 statt 2026", der
    bisher nur einem Menschen, keinem Skript auffiel.
    """
    from datetime import date

    current_year = date.today().year
    anchors = _read_aktualitaets_anker(repo_root)
    issues = []
    for s in _parse_lit_blocks(repo_root):
        typ = s["quelle_typ"].lower()
        label = (s["titel"] or s["autor"] or "?")[:70]
        ym = re.search(r"(?:19|20)\d{2}", s["jahr"])
        year = int(ym.group(0)) if ym else None
        if typ in ("report", "website") and year and year < current_year:
            issues.append(
                f"A1: {typ}-Quelle «{label}» ist von {year} (< {current_year}); "
                "prüfen, ob eine neuere Auflage/Jahreszahl vorliegt."
            )
        hay = f"{s['titel']} {s['reihe']} {s['autor']}".lower()
        hit = next((a for a in anchors if a.lower() in hay), None)
        if hit:
            issues.append(
                f"A2: Quelle «{label}» trägt Aktualitäts-Anker «{hit}»; "
                "Kennzahlen vor Abgabe frisch gegenprüfen."
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
    issues.extend(check_toc_levels(styles_xml))
    issues.extend(check_table_of_tables(document_xml))
    issues.extend(check_abgabedatum(document_xml))
    issues.extend(check_language_pitfalls(document_xml))
    issues.extend(check_project_pitfalls(document_xml, repo_root))
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

    repo_root = Path.cwd()
    issues = validate(args.docx, repo_root)
    hints = check_source_currency(repo_root)

    if issues:
        print(f"⚠ {args.docx.name}: {len(issues)} Verstöße gegen IU-Vorgaben")
        print()
        for i, msg in enumerate(issues, 1):
            print(f"  {i:2d}. {msg}")
        print()
        print("Begründung jedes Codes (F1, F2, ...) steht in LESSONS.md (Repo-Root).")
    else:
        print(f"✓ {args.docx.name}: keine Verstöße gegen IU-Vorgaben.")

    # A1/A2-Aktualitätshinweise getrennt ausgeben — nie blockierend, zählen nicht
    # als Verstoß und beeinflussen den Exit-Code nicht (auch nicht unter --strict).
    if hints:
        print()
        print(f"ℹ {len(hints)} Aktualitäts-Hinweis(e) (nicht blockierend):")
        for msg in hints:
            print(f"   - {msg}")

    return 1 if (issues and args.strict) else 0


if __name__ == "__main__":
    sys.exit(main())
