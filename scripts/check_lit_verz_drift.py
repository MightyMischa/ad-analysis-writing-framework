#!/usr/bin/env python3
"""Lit-Verz-Drift-Detektor.

Vergleicht das Literaturverzeichnis im aktuellen DOCX mit `sources/literature.md`
und meldet Drift in beide Richtungen:

  - Quellen im DOCX, die nicht in literature.md stehen
    (typisch nach manuellen Post-Build-Korrekturen)
  - Quellen in literature.md, die nicht im DOCX-Lit-Verz auftauchen
    (typisch bei nie zitierten Stammdaten)
  - Inline-Citations im DOCX-Volltext, deren Autor:in/Jahr-Paar nicht in
    literature.md existiert (verwaiste Zitationen)

Ausgabe: Pass/Fail + Liste aller Driften, exit-code 0 (clean) oder 1 (Drift).

Reagiert auf das Pattern, das bei Fallstudie 1 (Digitaler Euro) auftrat:
NIPC, IMF, BIS Innovation Hub, Sandner/Grale, Europäische Kommission lebten
nur im DOCX, nicht in literature.md — was den Reviewer-Punkt zur 919.000-
Quellenpräzisierung zunächst unverständlich machte.

Aufruf:
  python3 scripts/check_lit_verz_drift.py [DOCX]
  python3 scripts/check_lit_verz_drift.py output/phase-07-docx/<datei>.docx
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Iterable

try:
    from docx import Document
except ImportError:
    print("ERR: python-docx fehlt. Installation: pip install python-docx", file=sys.stderr)
    sys.exit(2)


# --------------------------------------------------------------------------------------
# literature.md parser
# --------------------------------------------------------------------------------------

LIT_AUTHOR_RE = re.compile(r'^autor:\s*"?(?P<v>[^"\n]+)"?\s*$', re.MULTILINE)
LIT_YEAR_RE = re.compile(r'^jahr:\s*"?(?P<v>[^"\n]+)"?\s*$', re.MULTILINE)
LIT_ID_RE = re.compile(r'^quelle_id:\s*(?P<v>\S+)\s*$', re.MULTILINE)


def parse_literature_md(path: Path) -> list[dict]:
    """Lies literature.md, zerlege in Quellen-Bloecke (PART 1) und gib Liste
    von dicts mit quelle_id/autor/jahr zurueck.

    Heuristik: ein Block beginnt mit '---' und enthaelt 'quelle_id:'.
    Zitat-Bloecke (PART 2) haben 'id:' statt 'quelle_id:' und werden ignoriert.
    """
    if not path.exists():
        return []
    text = path.read_text(encoding="utf-8")
    blocks = re.split(r"\n---\n", "\n" + text + "\n")
    sources: list[dict] = []
    for blk in blocks:
        if "quelle_id:" not in blk:
            continue
        # Stammdaten-Block
        if re.search(r"^id:\s", blk, re.MULTILINE):
            continue  # Zitat-Block (hat sowohl id: als auch quelle_id:)
        m_id = LIT_ID_RE.search(blk)
        m_au = LIT_AUTHOR_RE.search(blk)
        m_yr = LIT_YEAR_RE.search(blk)
        if not (m_id and m_au and m_yr):
            continue
        sources.append(
            {
                "quelle_id": m_id.group("v").strip(),
                "autor": m_au.group("v").strip(),
                "jahr": m_yr.group("v").strip(),
            }
        )
    return sources


def author_lastnames(autor: str) -> list[str]:
    """'Hanl, A./Michaelis, J.' -> ['Hanl', 'Michaelis']
       'Sandner, P./Groß, J./Chung, J.-C.' -> ['Sandner', 'Groß', 'Chung']
       'EZB' -> ['EZB']
       'Central Bank of Nigeria' -> ['Central Bank of Nigeria'] (Institutional)
    """
    parts = [p.strip() for p in autor.split("/") if p.strip()]
    out: list[str] = []
    for p in parts:
        # 'Hanl, A.' -> 'Hanl'
        if "," in p:
            out.append(p.split(",")[0].strip())
        else:
            out.append(p)
    return out


# --------------------------------------------------------------------------------------
# DOCX parser — Lit-Verz + Inline-Citations
# --------------------------------------------------------------------------------------

# (Autor, Jahr) — auch (Autor, Jahr, S. 5) und (Autor & Mitautor, Jahr) und (Autor et al., Jahr)
INLINE_CITE_RE = re.compile(
    r"\(([A-ZÄÖÜ][\wäöüß\.\-]+(?:\s+(?:&|et\s+al\.|und|/)\s*[\wäöüß\.\-]+)*"
    r"(?:,\s*[A-ZÄÖÜ][\wäöüß\.\-]+)*"  # zusaetzliche Co-Autor:innen mit Komma
    r"),\s*((?:n\.\s*d\.|o\.\s*[Dd]\.|\d{4}[a-z]?))"
)

# Lit-Verz-Eintragsmuster: "Autor, V. (Jahr)." am Anfang
LIT_ENTRY_RE = re.compile(
    r"^(?P<author>[^()]+?)\s*\(\s*(?P<year>(?:n\.\s*d\.|o\.\s*[Dd]\.|\d{4}[a-z]?))\s*\)\."
)


def find_lit_verz(doc: Document) -> tuple[int, int]:
    """Finde Start/Ende-Index der Literaturverzeichnis-Paragraphen.

    Heuristik: Heading-Paragraph mit Text 'Literaturverzeichnis' bis
    Dokumentende oder bis nächstes Heading 1.
    """
    paras = doc.paragraphs
    start = None
    for i, p in enumerate(paras):
        if "Literaturverzeichnis" in p.text and p.style.name.startswith(
            ("Heading", "Unnumbered Heading")
        ):
            start = i + 1
            break
    if start is None:
        return -1, -1
    end = len(paras)
    for j in range(start, len(paras)):
        s = paras[j].style.name
        if s.startswith("Heading 1"):
            end = j
            break
    return start, end


def parse_docx_lit_verz(doc: Document) -> list[dict]:
    """Extrahiert Lit-Verz-Eintraege als Liste von {author, year, raw}."""
    start, end = find_lit_verz(doc)
    if start < 0:
        return []
    entries: list[dict] = []
    for p in doc.paragraphs[start:end]:
        text = p.text.strip()
        if not text:
            continue
        m = LIT_ENTRY_RE.match(text)
        if not m:
            continue
        entries.append(
            {
                "author": m.group("author").strip().rstrip(","),
                "year": re.sub(r"\s+", " ", m.group("year").strip()),
                "raw": text,
            }
        )
    return entries


def parse_docx_inline_citations(doc: Document) -> list[tuple[str, str]]:
    """Sammelt alle (Autor, Jahr) Inline-Citations aus dem Body
    (vor dem Literaturverzeichnis)."""
    start, _ = find_lit_verz(doc)
    paras = doc.paragraphs[: start if start > 0 else len(doc.paragraphs)]
    body_text = "\n".join(p.text for p in paras)
    cites = INLINE_CITE_RE.findall(body_text)
    seen: set[tuple[str, str]] = set()
    result: list[tuple[str, str]] = []
    for autor, jahr in cites:
        key = (autor.strip(), jahr.strip())
        if key in seen:
            continue
        seen.add(key)
        result.append(key)
    return result


# --------------------------------------------------------------------------------------
# Match logic
# --------------------------------------------------------------------------------------


def lit_md_keys(sources: Iterable[dict]) -> set[tuple[str, str]]:
    """Reduziere Stammdaten auf {(erster_nachname_lowercase, jahr)}."""
    keys: set[tuple[str, str]] = set()
    for s in sources:
        names = author_lastnames(s["autor"])
        if not names:
            continue
        first = names[0].lower()
        keys.add((first, s["jahr"]))
    return keys


def docx_lit_keys(entries: Iterable[dict]) -> set[tuple[str, str]]:
    """Reduziere DOCX-Lit-Verz-Eintraege auf {(erster_nachname_lowercase, jahr)}."""
    keys: set[tuple[str, str]] = set()
    for e in entries:
        # Nimm den Teil vor dem ersten Komma als ersten Autor
        author_field = e["author"]
        first = author_field.split(",")[0].strip().split("&")[0].strip().lower()
        keys.add((first, e["year"]))
    return keys


def inline_cite_keys(cites: Iterable[tuple[str, str]]) -> set[tuple[str, str]]:
    """Reduziere Inline-Citations auf {(erster_nachname_lowercase, jahr)}."""
    keys: set[tuple[str, str]] = set()
    for autor, jahr in cites:
        first = autor.split("&")[0].split(",")[0].split(" et al")[0].strip().lower()
        # Filter Akronyme: bei BIS, EZB, IMF, etc. bleiben sie wie sie sind
        keys.add((first, jahr))
    return keys


# --------------------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------------------


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        # Default: nimm das letzte _final_konform oder die letzte .docx
        candidates = sorted(
            Path("output/phase-07-docx").glob("*.docx"),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )
        if not candidates:
            print("ERR: Keine DOCX gefunden in output/phase-07-docx/", file=sys.stderr)
            return 2
        docx_path = candidates[0]
        print(f"(auto-pick) DOCX: {docx_path}")
    else:
        docx_path = Path(argv[1])

    if not docx_path.exists():
        print(f"ERR: DOCX nicht gefunden: {docx_path}", file=sys.stderr)
        return 2

    lit_md_path = Path("sources/literature.md")
    if not lit_md_path.exists():
        print(f"ERR: literature.md fehlt: {lit_md_path}", file=sys.stderr)
        return 2

    sources = parse_literature_md(lit_md_path)
    md_keys = lit_md_keys(sources)

    doc = Document(str(docx_path))
    docx_entries = parse_docx_lit_verz(doc)
    docx_keys = docx_lit_keys(docx_entries)
    inline_cites = parse_docx_inline_citations(doc)
    inline_keys = inline_cite_keys(inline_cites)

    only_in_docx = docx_keys - md_keys
    only_in_md = md_keys - docx_keys
    inline_orphans = inline_keys - md_keys

    print(f"\n=== Lit-Verz-Drift-Check: {docx_path.name} ===")
    print(f"literature.md Stammdaten: {len(md_keys)} Quellen")
    print(f"DOCX-Lit-Verz Eintraege:  {len(docx_keys)} Quellen")
    print(f"DOCX-Inline-Citations:    {len(inline_keys)} unique Autor/Jahr-Paare")

    issues = 0

    if only_in_docx:
        issues += len(only_in_docx)
        print(f"\n✗ {len(only_in_docx)} Quelle(n) im DOCX-Lit-Verz, NICHT in literature.md:")
        for k in sorted(only_in_docx):
            matching = next(
                (e["raw"] for e in docx_entries if e["author"].split(",")[0].strip().lower() == k[0] and e["year"] == k[1]),
                f"{k[0]} ({k[1]})",
            )
            print(f"   - {matching[:100]}")

    if only_in_md:
        # Niedriger gewichtet: Stammdaten ohne DOCX-Verwendung sind nicht streng problematisch
        print(f"\n⚠ {len(only_in_md)} Stammdaten ohne DOCX-Verwendung (nicht blockierend):")
        for k in sorted(only_in_md):
            print(f"   - {k[0]} ({k[1]})")

    if inline_orphans:
        # Orphans nur melden, wenn sie auch nicht im DOCX-Lit-Verz stehen — sonst
        # eher Suffix/Naming-Drift
        true_orphans = inline_orphans - docx_keys
        if true_orphans:
            issues += len(true_orphans)
            print(
                f"\n✗ {len(true_orphans)} Inline-Citation(s) ohne Lit-Verz-Eintrag und ohne literature.md-Stammdaten:"
            )
            for k in sorted(true_orphans):
                print(f"   - ({k[0]}, {k[1]})")

    if issues == 0:
        print("\n✓ Lit-Verz und Volltext sind konsistent mit literature.md.")
        return 0
    print(f"\n✗ {issues} Drift-Verstoesse — bitte literature.md aktualisieren.")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
