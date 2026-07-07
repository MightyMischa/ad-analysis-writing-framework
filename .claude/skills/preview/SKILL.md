---
name: preview
description: Erzeugt eine HTML-Content-Preview des DOCX (Überschriften, Fließtext, Tabellen, Umbrüche, Format-Banner je Sektion) ohne Word/LibreOffice. Aufruf via /preview. Ersetzt NICHT das Render-Gate.
---

# DOCX-Preview (HTML)

Macht das gebaute DOCX sofort sichtbar — für den User im Browser und für Claude
als lesbare HTML-Struktur. Nativ mit `scripts/docx_preview.py` (python-docx),
kein Word, kein LibreOffice nötig.

## Wann aufrufen

- Nach jedem `/compile`, um das Ergebnis schnell zu sichten
- Vor/während `/apply-feedback`, um Kontext um die Patch-Stellen zu sehen
- Wenn der User „zeig mir das Dokument" o. ä. sagt und kein Word offen ist

## Ablauf

### 1. Zielfile bestimmen

- `/preview` ohne Argument → neuestes DOCX in `output/phase-07-docx/` (mtime)
- `/preview <pfad>.docx` → expliziter Pfad

### 2. Preview bauen und öffnen

```bash
python3 scripts/docx_preview.py <docx-pfad> --open
```

Output: `preview_<name>.html` neben dem DOCX. `--open` öffnet den Browser.

### 3. Format-Banner interpretieren

Die Banner oben in der Preview zeigen pro Sektion: Seitengröße, Ränder,
Seitennummerierung (`fmt`/`start`) und `Titelseite anders`. Soll-Werte laut
`.claude/rules/format-checks.md`:

- Sektion 0 (Titelblatt): upperRoman, start=1
- Sektion 1 (Frontmatter): upperRoman, start=2
- Sektion 2 (Body): decimal, start=1

Abweichungen direkt melden (das ergänzt `validate_docx.py`, ersetzt es nicht).

### 4. Content-Sichtung durch Claude

Bei Bedarf die HTML-Datei lesen und prüfen:
- Überschriften-Hierarchie vollständig und richtig verschachtelt
- Seitenumbruch-/Sektionswechsel-Markierungen an den erwarteten Stellen
- Tabellen vorhanden und nicht leer
- TOC-Feld-Platzhalter vorhanden (bzw. statische TOC-Einträge im Final-DOCX)

## Grenzen (WICHTIG)

Die Preview ist eine **Content-Preview**. Sie entscheidet NICHT:
Seitenumfang (7–10 Seiten), Halbseiten-Regel, sichtbare Seitenzahlen,
optische TOC-Fettung nach Feld-Update. Dafür gilt weiterhin das Render-Gate
aus `/preflight` (Schritt 2.6, `measure_pages.py` bzw. Word Strg+A → F9).
