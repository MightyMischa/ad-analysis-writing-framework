---
name: preflight
description: Blockierendes Pre-Compile-Gate. Führt validate_docx + check_lit_verz_drift + Pitfall-Strings + Wordcount in einem Lauf aus. /compile und /approve rufen es vorher auf und blockieren bei Verstößen.
---

# Preflight-Gate

Eine einzige Pass/Fail-Antwort, ob das Projekt abgabereif ist. Ersetzt die manuelle 13-Punkte-Checkliste aus `LESSONS.md` durch ein ausführbares Gate.

## Wann automatisch aufrufen

- Vor jedem `/compile` (außer bei `/compile draft`)
- Vor jedem `/approve` Phase 6 oder Phase 7
- Vor manueller DOCX-Manipulation (`/apply-feedback`)
- Manuell jederzeit via `/preflight` für eine Statusabfrage

## Wann manuell

- Vor finaler Turnitin-Abgabe (Sanity-Check)
- Nach jedem externen Reviewer-Durchlauf, bevor neu geschrieben wird

## Ablauf

### 1. Zielfile bestimmen

Argument-Parsing:
- `/preflight` ohne Argument → neuestes DOCX in `output/phase-07-docx/` (`mtime`-sortiert)
- `/preflight <pfad>.docx` → expliziter Pfad
- `/preflight markdown` → nur Markdown-Quellen prüfen (Volltext aus phase-05-writing)

Falls keine DOCX existiert, Markdown-Modus automatisch.

### 2. Sequenzielle Checks

Reihenfolge spielt Rolle: zuerst die schnellen, dann die Codex-Calls.

**Schritt 2.1 — DOCX-Validator**
```bash
python3 scripts/validate_docx.py <docx-pfad>
```
Output: Liste von Verstößen mit F/S/I/C/M/N-Codes.

**Schritt 2.2 — Lit-Verz-Drift**
```bash
python3 scripts/check_lit_verz_drift.py <docx-pfad>
```
Output: Quellen im DOCX ohne literature.md-Pendant und vice versa.

**Schritt 2.3 — Course-Book-Presence (falls Fallstudie)**
Wird vom Validator (C1-Check) abgedeckt — kein extra Schritt nötig.

**Schritt 2.4 — Wortzahl-Schätzung (NUR grober Richtwert)**
```bash
python3 -c "from docx import Document; ..."
```
Lese `config.yaml → formatierung.seitenumfang.{min,max}`. Schätze die Seitenzahl mit dem
**kalibrierten Richtwert ~330 Wörter/Seite** (Arial 11pt, 1,5-zeilig). Der frühere Wert
250 lag massiv daneben (echter Word-Render ~330) und erzeugte Schwankungen von 7,6 bis
11,8 Seiten für dasselbe Dokument. Das ist NUR eine Schätzung — die tatsächliche
Seitenzahl entscheidet der Word-Render (Schritt 2.6, Render-Gate). Warnung (nicht
blockierend) wenn die Schätzung außerhalb des Soll-Bereichs liegt.

**Schritt 2.5 — R-Reproduzierbarkeit (falls aktiv)**
Wenn `config.yaml → r_toolchain.enabled: true`:
```bash
python3 scripts/validate_r_reproducibility.py
```

**Schritt 2.6 — Render-Gate (VERBINDLICH, nur in Word/LibreOffice prüfbar)**

`validate_docx.py` arbeitet rein auf dem DOCX-XML und kann die am stärksten benoteten
Formalvorgaben NICHT entscheiden — sie sind reine Render-Fragen. Dieser Schritt ist
KEINE Fußnote, sondern ein verbindlicher Gate-Punkt.

Zuerst die **Soft-Messung** (misst die echte Seitenzahl, wenn LibreOffice vorhanden ist;
sonst Hinweis `RENDER_UNAVAILABLE` und Fallback auf die manuelle Checkliste):
```bash
python3 scripts/measure_pages.py <docx-pfad>
```
- Gibt das Skript einen gemessenen Textteil aus, gilt diese Zahl (real gerendert) statt
  der groben Wortschätzung aus Schritt 2.4. Außerhalb des Soll-Bereichs → WARNUNG.
- Bei `RENDER_UNAVAILABLE` ist LibreOffice nicht installiert (Soft-Modus, kein Zwang):
  dann ist die manuelle Sichtprüfung unten verbindlich. Als Vorstufe dazu
  `python3 scripts/docx_preview.py <docx-pfad> --open` (bzw. `/preview`) erzeugen —
  die Content-Preview zeigt Struktur, Umbrüche und die Sektions-Banner
  (Seitennummerierung, Ränder), ersetzt aber die Word-Sichtprüfung NICHT.

Manuelle Sichtprüfung (immer, mindestens als Gegenkontrolle): DOCX in Word öffnen,
**Strg+A → F9 („Gesamtes Verzeichnis aktualisieren")**, dann:

- [ ] **7–10 Seiten Textteil** (Einleitung bis Fazit, ohne Verzeichnisse)
- [ ] **≥ 0,5 Seite je Unterkapitel**
- [ ] **Seitenzahlen**: Titelblatt ohne Zahl, Inhaltsverzeichnis = **II** (römisch),
  Einleitung = **1** (arabisch)
- [ ] **Inhaltsverzeichnis-Ebene 1 optisch fett** (XML wird von F6 geprüft, Optik hier)
- [ ] **letzte Textseite nicht fast leer**

Erst wenn alle Render-Punkte sitzen, ist das Dokument abgabereif.

**Schritt 2.7 — Review-/Humanize-Tracking**
```bash
python3 scripts/review_tracking.py check
```
Warnt (nicht blockierend), wenn ein Kapitel seit seinem letzten `/review` oder
`/humanize` verändert wurde — damit nachträglich ergänzter Text nicht ungeprüft
durchrutscht. Liefert nichts, solange noch keine Markierungen vorliegen.

**Schritt 2.8 — Stil-Linter (Markdown-Quellen)**
```bash
python3 scripts/lint_style.py --all --json
```
Läuft IMMER auf den Markdown-Quellen (auch im `/preflight markdown`-Modus und
wenn ein DOCX geprüft wird — der Stil wird an der Quelle korrigiert):
- **L1–L4 (verbotene Wörter, Floskeln, Em-Dashes, Chatbot-Artefakte/Pitfalls)
  → BLOCKIEREND** (gleiche Stufe wie F-Codes)
- **L5–L13 (Konnektor-Kaskaden, Rhythmus-/Uniformitäts-Metriken, Hedging,
  Wiederholungen) → WARNUNG** (Ermessenssache, nie blockierend)
- **L14/L15 (Passiv-Quote, Statistik) → HINWEIS**

Skip-Flag: `/preflight --skip-style-lint`. Behebung: `/humanize [X.X]` arbeitet
die Linter-Funde gezielt ab.

### 3. Aggregation

`validate_docx.py` und `check_lit_verz_drift.py` prüfen nur das DOCX-**XML**; die
render-abhängigen Vorgaben (Seitenumfang, Halbseiten-Regel, sichtbare Seitenzahlen,
optische TOC-Fettung) entscheidet allein das Render-Gate (Schritt 2.6). „Validator grün"
heißt NICHT „Dokument korrekt".

Sammle alle Funde, gruppiere nach Schwere:
- **Hoch (BLOCKIEREND):** F-Codes (inkl. F6 TOC-Ebenen), C1, M1, N1, Pitfall-Strings
  (S1/S3/S4), **Stil-Linter L1–L4** (Schritt 2.8),
  Lit-Verz-Drift „im DOCX, nicht in literature.md" UND „im Volltext zitiert, fehlt im
  gerenderten Lit-Verz" (Build hat eine Quelle verschluckt — vgl. P1-A)
- **Mittel (WARNUNG):** Wortzahl-Schätzung bzw. gemessener Textteil außerhalb Soll,
  Stammdaten ohne DOCX-Verwendung, R-Reproduzierbarkeit-Warnung, Kapitel seit
  letztem /review oder /humanize verändert (Schritt 2.7), **Stil-Linter L5–L13**
- **Niedrig (HINWEIS):** A1/A2-Aktualitätshinweise (report/website-Jahr < aktuelles Jahr,
  Aktualitäts-Anker aus preferences.md), **Stil-Linter L14/L15**
- **Render-Gate (manuell, verbindlich):** Schritt 2.6 — nicht aus dem XML ableitbar

### 4. Output-Format

```
=== Preflight-Gate ===
Geprüft: output/phase-07-docx/<datei>.docx
Stand: <ISO-Timestamp>

[BLOCKIEREND — N Verstöße]
  ...

[WARNUNG — N Verstöße]
  ...

[HINWEIS — N Verstöße]
  ...

Empfehlung: ENTWEDER
  ✓ FREIGABE — keine blockierenden Verstöße. /compile / /approve kann ausgeführt werden.
ODER
  ✗ BLOCKIERT — N blockierende Verstöße. Bitte beheben, dann erneut /preflight.
```

### 5. Exit-Verhalten

Wenn `config.yaml → preflight.block_on_violation: true` (Default) und blockierende Verstöße vorhanden:
- Skill setzt internen `__preflight_blocked: true`-Flag im Conversation State
- Aufrufende Skills (`/compile`, `/approve`) prüfen dieses Flag und brechen ab
- User muss explizit `/preflight --override` aufrufen, um den Block zu lösen (für Edge-Cases wie absichtliche Draft-Compiles)

Wenn `block_on_violation: false`: nur Report, kein Block.

### 6. Override-Mode

`/preflight --override`:
- Erlaubt einmaliges Bypassen des Blocks für die nächste `/compile`/`/approve`-Aktion
- Loggt den Override in `output/phase-06-review/preflight-overrides.log` mit Timestamp und Begründung (User per `AskUserQuestion` befragen)
- Override gilt nur für die unmittelbar folgende Aktion

## Beispiel-Aufruf

```
/preflight

→ Liest output/phase-07-docx/<latest>.docx
→ Validator: 6 Verstöße (3× F2, F5, F6, F9 — vorbestehende Format-Findings)
→ Drift: 13 Quellen im DOCX ohne literature.md-Pendant
→ Wortzahl: 2628 (Soll 1750–2500 → leicht über)

[BLOCKIEREND — 7 Verstöße]
  - F2: Heading-Farbe nicht schwarz (Heading 1)
  - F2: Heading-Farbe nicht schwarz (Heading 2)
  - F2: Heading-Farbe nicht schwarz (Heading 3)
  - F5: Keine arabische Seitennummerierung im Body
  - F6: Kein TOC-Field
  - F9: Abgabedatum ist Platzhalter
  - Drift: 13 DOCX-Quellen ohne literature.md-Eintrag

[WARNUNG — 1 Verstoss]
  - Wortzahl 2628 leicht über Soll-Maximum 2500

✗ BLOCKIERT — 7 Verstöße müssen behoben werden.
```

## Konfiguration

Schalter in `config.yaml`:

```yaml
preflight:
  enabled: true                  # Gate aktiv
  block_on_violation: true       # /compile + /approve blocken bei Verstoessen
```

Die einzelnen Checks (C1 Course-Book, M1 Methodengrenzen, N1 Zahlen-Eindeutigkeit,
S1/S3/S4 Pitfall-Strings, Stil-Linter, Lit-Verz-Drift) laufen fest in der
Validator-/Skill-Logik und sind NICHT mehr per Config einzeln schaltbar. Wenn ein
einzelner Check für einen Lauf übersprungen werden muss (z. B. bekannter,
akzeptierter Lit-Verz-Drift): `/preflight --skip-lit-verz-drift`,
`/preflight --skip-course-book`, `/preflight --skip-style-lint` usw.

## Verhalten bei Skript-Fehlern

- `validate_docx.py` crasht → klare Fehlermeldung, kein Pseudo-Pass.
- `check_lit_verz_drift.py` findet kein DOCX → nutze Markdown-Modus mit Hinweis.
- python-docx fehlt → Installations-Anweisung, Skill blockiert nicht den Rest.

## Logging

Jeder Preflight-Lauf wird in `output/phase-06-review/preflight-<timestamp>.md` archiviert. Format:

```markdown
# Preflight: <datei>.docx
Stand: <ISO>
Verstoesse: <N> blockierend, <M> warnung, <K> hinweis

## Funde
[Original-Output]

## Aktion
- Override: [ja/nein, von User, Begruendung]
- Block aktiv: [ja/nein]
```

Damit ist auditierbar, welcher Stand wann freigegeben wurde.
