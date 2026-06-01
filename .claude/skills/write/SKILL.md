---
name: write
description: Schreibt ein bestimmtes Kapitel oder das nächste ungeschriebene. Nutze diesen Skill wenn der User /write eingibt, optional mit Kapitelnummer wie /write 2.3.
---

# Kapitel schreiben

Schreibt den wissenschaftlichen Fließtext für ein Unterkapitel.

## Ablauf

### 1. Kapitelnummer bestimmen

**Mit Parameter (z.B. /write 2.3):**
- Verwende die angegebene Kapitelnummer

**Ohne Parameter (/write):**
- Lies `output/phase-02-outline/final/thesis-structure.yaml`
- Finde das nächste Kapitel das:
  - Einen freigegebenen Plan hat (`output/phase-04-plans/final/plan-X-X.md`)
  - Noch NICHT geschrieben ist (keine Datei in `output/phase-05-writing/draft/` oder `final/`)
- Falls kein Kapitel gefunden: "Alle geplanten Kapitel sind bereits geschrieben.
  Nutze /review um die Qualitätsprüfung zu starten."

### 2. DOCX-Frozen-Mode-Warnung

Lies `config.yaml → docx_frozen.warn_on_markdown_edit` und `docx_frozen.guard_path`.

Glob den `guard_path` (Default `output/phase-07-docx/*_final_konform*.docx`).

**Wenn ein passendes DOCX existiert UND `warn_on_markdown_edit: true`:**
- WARNE den User: „Ein finalisiertes DOCX existiert bereits. Markdown-Änderungen werden NICHT automatisch ins DOCX propagiert. Wenn du das DOCX patchen willst, nutze `/apply-feedback`. Markdown-Änderungen dienen nur Traceability für zukünftige Builds."
- Frage via AskUserQuestion: „Wie weiter?"
  - Markdown trotzdem ändern (Traceability) — ✓ empfohlen
  - DOCX patchen via /apply-feedback
  - Komplett neu bauen via /compile --override

### 3. Vorbedingungen prüfen

- [ ] config.yaml existiert
- [ ] Freigegebener Plan existiert für dieses Kapitel
- [ ] Alle vorherigen Kapitel sind geschrieben und freigegeben
- [ ] Benötigte Zitate sind in `sources/literature.md`

Falls eine Bedingung fehlt:
- Erkläre was fehlt
- Schlage Lösung vor (z.B. "/next um den Plan zu erstellen")

### 3. Agent starten

Starte den Agent `.claude/agents/writer.md` mit dem Kapitel als Kontext.

### 4. Ergebnis

Nach dem Schreiben:
- Zeige Zusammenfassung: Kapitel [X.X], [Y] Wörter, [Z] geplante Seiten
- Falls Abweichung > 15%: Melde es

### 5. Auto-Codex-Review (wenn aktiv)

Lies `config.yaml → codex.auto_review`.

Wenn `true`:
- Rufe den Skill `codex-review` mit Argument `chapter [X.X] --quiet` auf.
- Der Skill ruft Codex (gpt-5.5, xhigh) gegen den frischen Draft auf und meldet Hochpriorität-Funde direkt im Workflow.
- Bei Codex-Funden: zeige sie und biete an, sie umzusetzen, BEVOR der User /approve aufruft.

Wenn `false` oder Schlüssel fehlt:
- Skip, keine Verzögerung.

### 6. Empfehlung

- "Prüfe das Ergebnis in output/phase-05-writing/draft/[X-X].md und nutze /approve um es freizugeben."
- Falls Codex-Review Funde gemeldet hat: "Bitte zuerst die Codex-Anmerkungen prüfen."
