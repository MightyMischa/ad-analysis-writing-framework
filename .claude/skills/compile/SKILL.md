---
name: compile
description: Baut die Arbeit als IU-konforme DOCX (+ PDF) aus den fertigen Kapiteln. Nutze diesen Skill wenn der User /compile eingibt.
---

# Kompilieren — DOCX + PDF

Erzeugt das Enddokument über den kanonischen Builder `scripts/build_docx.py`:
eine IU-formatkonforme DOCX (Primärartefakt, Turnitin) und daraus per
LibreOffice ein layout-identisches PDF.

> Kein LaTeX mehr. Der frühere LaTeX→PDF-Pfad wurde durch den python-docx-Builder
> ersetzt (bewährt aus FS1, dem real abgegebenen Digitaler-Euro-DOCX).
> LaTeX-Konventionen liegen archiviert unter `docs/archive/latex-conventions.md`.

## Ablauf

### 1. Modus bestimmen

- **Normal (`/compile`):** Alle Kapitel müssen in `output/phase-05-writing/final/` liegen.
- **Draft (`/compile draft`):** Baut den aktuellen Stand auch unvollständig (fehlende
  Kapitel fehlen einfach), zum Prüfen von Umfang/Layout. Überspringt das Preflight-Gate.

### 1a. DOCX-Frozen-Mode-Check

Lies `config.yaml → docx_frozen.enabled` und `docx_frozen.guard_path`
(Default `output/phase-07-docx/*_final_konform*.docx`).

**Wenn ein passendes DOCX existiert UND `docx_frozen.block_overwrite: true`:**
- BLOCKIERE den Build und zeige:
  „Ein finalisiertes DOCX existiert ([Pfad]). /compile würde Format-Korrekturen
   überschreiben. Optionen:
   1. `/apply-feedback` für gezielte Änderungen am DOCX (preserves Format-Fixes).
   2. `/compile --override` um wirklich neu zu bauen (Format-Fixes gehen verloren).
   3. `/preflight` um nur den aktuellen Stand zu prüfen."
- Exit ohne Build.

**Mit `--override`:** Grund via AskUserQuestion erfragen, in
`output/phase-06-review/compile-overrides.log` mit Timestamp loggen, weiter.

### 1b. Preflight-Gate

Wenn nicht `--draft` und nicht `--override-preflight`:
- Rufe `/preflight` auf den aktuellen Stand auf.
- Bei blockierenden Verstößen: Build abbrechen, Preflight-Output anzeigen.
- Bei nur Warnungen: weiter, Hinweis ausgeben.

### 1c. Vorbedingungen

- [ ] `config.yaml` vollständig konfiguriert (autor, projekt.kurs_modul, formatierung).
- [ ] `output/phase-02-outline/final/thesis-structure.yaml` vorhanden.
- [ ] Alle Kapitel in `output/phase-05-writing/final/` (nur im Normal-Modus; sonst Liste fehlender Kapitel zeigen).

### 2. Build ausführen

```bash
python3 scripts/build_docx.py
```

Der Builder:
1. Liest `config.yaml` (Autor, Kurs, Formatierung, Verzeichnisse, Logo, Abgabedatum).
2. Baut Titelblatt, Verzeichnisse (TOC/Tabellen/Abkürzungen je nach config), Kapitel, Literaturverzeichnis.
3. Speichert die DOCX nach `output/phase-07-docx/<slug>.docx`.
4. Konvertiert per `soffice --headless --convert-to pdf` zu PDF (Best-effort; fehlt LibreOffice, bleibt die DOCX das Primärartefakt und es folgt ein Hinweis).

Optionale Projekt-Dateien, die der Builder berücksichtigt:
- `output/terminology.md` → Abkürzungsverzeichnis (`## Abkürzungen`, dann `- ABK — Bedeutung`).
- `output/tables.yaml` → Tabellen-Captions je Abschnitts-ID, z. B. `{"3.4": "Vergleichende Bewertung"}`.

### 3. Post-Build-Validierung

**Immer** nach dem Build:
```bash
python3 scripts/validate_docx.py output/phase-07-docx/<datei>.docx
python3 scripts/check_lit_verz_drift.py output/phase-07-docx/<datei>.docx
```

Bei Verstößen: **Build-Skript / Quelle anpassen, NICHT die DOCX manuell editieren**
(geht beim nächsten Build verloren). Häufige Fälle und Auto-Fixes siehe `/preflight`.

**Wenn `config.yaml → codex.auto_review: true` und `trigger_on.pre_compile`/`approve_phase_6`:**
- `/codex-review docx --quiet` — Codex prüft XML-Eigenschaften + Volltext gegen `LESSONS.md`.
- Hochprioritäts-Funde fließen in die Korrektur (im autonomen Lauf: Auto-Fix-Schleife, siehe `/auto`).

### 4. Ergebnis melden

```
DOCX erstellt: output/phase-07-docx/<datei>.docx
PDF erstellt:  output/phase-07-docx/<datei>.pdf   (falls LibreOffice verfügbar)
Validator: [✓ sauber | N Funde]
Seiten (Schätzung): [X]   (Zielbereich aus config.formatierung.seitenumfang)

Vor Abgabe:
  1. DOCX öffnen, Strg+A + F9 (TOC/Tabellenverzeichnis-Felder aktualisieren).
  2. Abgabedatum auf dem Titelblatt prüfen (config.yaml: abgabe.datum).
  3. Turnitin-Upload via myCampus.
```
