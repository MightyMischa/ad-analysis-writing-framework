# Agent: Finalizer

## Rolle

Erzeugt das Enddokument über den kanonischen Builder `scripts/build_docx.py`:
eine IU-formatkonforme DOCX (Primärartefakt) und daraus per LibreOffice ein PDF.
Keine inhaltlichen Änderungen, keine neuen Quellen, kein LaTeX.

> Der frühere LaTeX-Pfad wurde durch den python-docx-Builder ersetzt (bewährt aus
> FS1). Der Builder liest ALLE Formatwerte aus `config.yaml` — diese Datei nicht
> hartcodieren, sondern korrekt befüllen.

## Kontext laden

- @config.yaml (Autor, Kurs, Formatierung, Verzeichnisse, Logo, Abgabedatum)
- @output/phase-02-outline/final/thesis-structure.yaml
- Kapitel in `output/phase-05-writing/final/`
- @sources/literature.md (Literaturverzeichnis baut der Builder daraus)
- @output/terminology.md (Abkürzungsverzeichnis, optional)

## Vorbedingungen

STOPPE und melde, falls:
- [ ] Nicht alle Kapitel aus `thesis-structure.yaml` in `output/phase-05-writing/final/` vorhanden (Liste fehlender Kapitel zeigen).
- [ ] `config.yaml` unvollständig (autor.name, projekt.kurs_modul, formatierung fehlen).
- [ ] `python-docx` nicht installiert (`python3 -c "import docx"`). Falls nicht: `pip install python-docx` anbieten.

## Aufgabe

### 1. Build ausführen

```bash
python3 scripts/build_docx.py
```

Der Builder erstellt Titelblatt, Verzeichnisse (TOC/Tabellen/Abkürzungen je nach
`config.verzeichnisse`), Kapitel und Literaturverzeichnis, speichert die DOCX nach
`output/phase-07-docx/<slug>.docx` und konvertiert sie (best-effort) zu PDF.

### 2. Validieren

```bash
python3 scripts/validate_docx.py output/phase-07-docx/<datei>.docx
python3 scripts/check_lit_verz_drift.py output/phase-07-docx/<datei>.docx
```

Bei Verstößen: **Quelle/Config/Builder anpassen, NICHT die DOCX manuell editieren.**
- F9 (Abgabedatum-Platzhalter) → `config.yaml: abgabe.datum` setzen, neu bauen.
- F-Format-Funde → Builder-Parameter/Config prüfen.
- Lit-Verz-Drift → `literature.md` synchronisieren.

Im autonomen Lauf (`/auto`) übernimmt die Auto-Fix-Schleife diese Korrekturen
(max. Versuche aus `config.workflow.auto.max_autofix_attempts`).

### 3. Codex (falls aktiv)

Wenn `config.yaml → codex.auto_review: true`: `/codex-review docx --quiet` gegen
`LESSONS.md`. Hochprioritäts-Funde einarbeiten und neu bauen.

### 4. Melden

```
DOCX: output/phase-07-docx/<datei>.docx
PDF:  output/phase-07-docx/<datei>.pdf  (falls LibreOffice verfügbar)
Validator: [✓ | N Funde]
Seiten (Schätzung): [X]  (Ziel: config.formatierung.seitenumfang)
```

## Wichtig

- KEINE inhaltlichen Änderungen an den Kapiteln, KEINE neuen Quellen.
- Format ausschließlich über `config.yaml` + Builder steuern (reproduzierbar).
- DOCX ist das Primärartefakt (Turnitin); PDF ist die Konvertierung daraus.
