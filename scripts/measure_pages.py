#!/usr/bin/env python3
"""Misst die reale Seitenzahl des gerenderten DOCX (Soft-Mode für /preflight).

„validate_docx grün" heißt NICHT „Dokument korrekt": die am stärksten benoteten
Vorgaben (7–10 Seiten Textteil) sind reine Render-Fragen. Wenn LibreOffice
(soffice) verfügbar ist, rendert dieses Skript das DOCX nach PDF und MISST den
Textteil — statt ihn aus der Wortzahl zu schätzen (Wörter ÷ 330 ist nur grob).

Soft-Degradation (kein harter LibreOffice-Zwang):
  1. soffice vorhanden            -> rendern und messen
  2. sonst frisches Geschwister-PDF (z. B. von build_docx) -> messen
  3. sonst                        -> RENDER_UNAVAILABLE: manuelles Render-Gate nötig

Gemessen wird der TEXTTEIL (Einleitung bis Fazit, ohne Titel/Verzeichnisse/
Literaturverzeichnis). Der Lit-Verz-Anker wird als LETZTES Vorkommen von
„Literaturverzeichnis" gesucht, damit ein (ggf. per F9 gefüllter) TOC-Eintrag
nicht fälschlich als Lit-Verz-Seite zählt.

Aufruf:
  python3 scripts/measure_pages.py [DOCX] [--min N] [--max N] [--project DIR]
Exit-Code immer 0 — reines Messwerkzeug, die Gate-Entscheidung trifft /preflight.
"""
from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path

FRONTMATTER_HEADINGS = (
    "Inhaltsverzeichnis",
    "Tabellenverzeichnis",
    "Abbildungsverzeichnis",
    "Abkürzungsverzeichnis",
)


def find_soffice() -> str | None:
    s = shutil.which("soffice") or shutil.which("libreoffice")
    if s:
        return s
    mac = Path("/Applications/LibreOffice.app/Contents/MacOS/soffice")
    return str(mac) if mac.exists() else None


def render_pdf(docx: Path) -> Path | None:
    soffice = find_soffice()
    if not soffice:
        return None
    try:
        subprocess.run(
            [soffice, "--headless", "--convert-to", "pdf",
             "--outdir", str(docx.parent), str(docx)],
            check=True, capture_output=True, timeout=180,
        )
        pdf = docx.with_suffix(".pdf")
        return pdf if pdf.exists() else None
    except Exception:
        return None


def get_pdf(docx: Path) -> tuple[Path | None, str]:
    """soffice-Render bevorzugen; sonst frisches Geschwister-PDF; sonst (None,...)."""
    pdf = render_pdf(docx)
    if pdf:
        return pdf, "soffice-render"
    sibling = docx.with_suffix(".pdf")
    if sibling.exists() and sibling.stat().st_mtime >= docx.stat().st_mtime:
        return sibling, "vorhandenes PDF (kein soffice)"
    return None, ""


def count_pages(pdf: Path) -> int | None:
    if shutil.which("pdfinfo"):
        try:
            out = subprocess.run(
                ["pdfinfo", str(pdf)], capture_output=True, text=True, timeout=30
            ).stdout
            m = re.search(r"^Pages:\s*(\d+)", out, re.MULTILINE)
            if m:
                return int(m.group(1))
        except Exception:
            pass
    try:  # Fallback: rohe Page-Objekte zählen
        n = len(re.findall(rb"/Type\s*/Page\b(?!s)", pdf.read_bytes()))
        if n:
            return n
    except Exception:
        pass
    return None


def page_texts(pdf: Path) -> list[str]:
    """Pro-Seiten-Text via pdftotext (Form-Feed-getrennt). Leer, wenn nicht da."""
    if not shutil.which("pdftotext"):
        return []
    try:
        out = subprocess.run(
            ["pdftotext", "-layout", str(pdf), "-"],
            capture_output=True, text=True, timeout=60,
        ).stdout
        return out.split("\f")
    except Exception:
        return []


def textteil_pages(pages: list[str]) -> tuple[int | None, int | None, int | None]:
    """(textteil, body_start_1based, litverz_1based); None bei Unklarheit."""
    if len(pages) < 2:
        return None, None, None
    body_start = None
    for i in range(1, len(pages)):  # Seite 1 = Titelblatt überspringen
        if not any(h in pages[i] for h in FRONTMATTER_HEADINGS):
            body_start = i + 1
            break
    litverz = None
    for i in range(len(pages) - 1, -1, -1):  # LETZTES Vorkommen
        if "Literaturverzeichnis" in pages[i]:
            litverz = i + 1
            break
    if body_start and litverz and litverz > body_start:
        return litverz - body_start, body_start, litverz
    return None, body_start, litverz


def read_seitenumfang(project: Path) -> tuple[int, int]:
    cfg = project / "config.yaml"
    lo, hi = 7, 10
    if cfg.exists():
        try:
            import yaml
            data = yaml.safe_load(cfg.read_text()) or {}
            su = (((data.get("formatierung") or {}).get("seitenumfang")) or {})
            lo = int(su.get("min", lo))
            hi = int(su.get("max", hi))
        except Exception:
            pass
    return lo, hi


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Misst reale Seitenzahl (Soft-Render).")
    ap.add_argument("docx", nargs="?", type=Path)
    ap.add_argument("--min", type=int, default=None)
    ap.add_argument("--max", type=int, default=None)
    ap.add_argument("--project", type=Path, default=Path.cwd())
    args = ap.parse_args(argv[1:])

    docx = args.docx
    if docx is None:
        cands = sorted(
            (args.project / "output" / "phase-07-docx").glob("*.docx"),
            key=lambda p: p.stat().st_mtime, reverse=True,
        )
        cands = [c for c in cands if not c.name.startswith("~$")]
        if not cands:
            print("MESSUNG: keine DOCX in output/phase-07-docx/ gefunden.")
            return 0
        docx = cands[0]
    if not docx.exists():
        print(f"MESSUNG: DOCX nicht gefunden: {docx}")
        return 0

    lo, hi = read_seitenumfang(args.project)
    if args.min is not None:
        lo = args.min
    if args.max is not None:
        hi = args.max

    pdf, how = get_pdf(docx)
    if not pdf:
        print(
            "RENDER_UNAVAILABLE: kein LibreOffice (soffice) und kein frisches PDF. "
            "Seitenzahl NICHT messbar — manuelles Render-Gate erforderlich "
            "(Word: Strg+A, F9 + Sichtprüfung der 7–10 Seiten / Halbseiten-Regel)."
        )
        return 0

    print(f"=== Render-Messung: {docx.name} ({how}) ===")
    total = count_pages(pdf)
    print(f"PDF-Gesamtseiten: {total if total is not None else 'unbekannt'}")

    textteil, body_start, litverz = textteil_pages(page_texts(pdf))
    if textteil is not None:
        verdict = "im Soll" if lo <= textteil <= hi else "AUSSERHALB Soll"
        print(
            f"Textteil (Einleitung–Fazit): ~{textteil} Seiten "
            f"(Body ab S. {body_start}, Lit-Verz ab S. {litverz}) "
            f"— Soll {lo}–{hi} → {verdict}."
        )
        if not (lo <= textteil <= hi):
            print(
                "  HINWEIS: gemessener Textteil außerhalb des Soll-Bereichs. "
                "Final im Word-Render mit aktualisierten Feldern gegenprüfen."
            )
    elif total is not None:
        print(
            f"Textteil nicht eindeutig abgrenzbar (pdftotext fehlt?). "
            f"Nur Gesamtseiten bekannt: {total}. Soll-Textteil {lo}–{hi} manuell prüfen."
        )
    else:
        print("Seitenzahl nicht messbar — manuelles Render-Gate erforderlich.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
