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

**Schritt 2.4 — Wortzahl-Schranke**
```bash
python3 -c "from docx import Document; ..."
```
Lese `config.yaml → formatierung.seitenumfang.{min,max}`. Schätze Seitenzahl (Wörter ÷ 250 für Arial 11pt 1,5-Zeilen). Warnung wenn außerhalb.

**Schritt 2.5 — R-Reproduzierbarkeit (falls aktiv)**
Wenn `config.yaml → r_toolchain.enabled: true`:
```bash
python3 scripts/validate_r_reproducibility.py
```

### 3. Aggregation

Sammle alle Funde, gruppiere nach Schwere:
- **Hoch (BLOCKIEREND):** F-Codes, C1, M1, N1, Pitfall-Strings, Lit-Verz-Drift "im DOCX, nicht in literature.md"
- **Mittel (WARNUNG):** Wortzahl außerhalb, Stammdaten ohne DOCX-Verwendung, R-Reproduzierbarkeit-Warnung
- **Niedrig (HINWEIS):** I1-Aktualitätsanker

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
  block_on_violation: true       # /compile + /approve blocken bei Verstoessen
  course_book_check: true        # C1 in Validator
  methodengrenzen_check: true    # M1 in Validator
  number_source_uniqueness: true # N1 in Validator
  pitfall_strings: true          # S1-S4 in Validator
  lit_verz_drift: true           # check_lit_verz_drift.py
```

Einzelne Checks via `false` deaktivieren — z. B. wenn ein Lit-Verz-Drift bekannt und akzeptiert ist.

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
