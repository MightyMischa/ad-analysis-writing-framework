---
name: codex-review
description: Ruft Codex (gpt-5.5, model_reasoning_effort=xhigh) als unabhängige Review-Instanz auf den aktuellen Stand der Arbeit auf. Nutze automatisch nach jedem Schreib-/Approve-/Compile-Schritt, oder manuell via /codex-review.
---

# Codex-Review (gpt-5.5 / xhigh)

Lässt Codex als unabhängige zweite Meinung über den aktuellen Repo-Stand laufen.
Codex liest LESSONS.md, die Regeln und den aktuellen Diff/Volltext und meldet
Reviewer-Pitfalls, bevor sie ein Mensch bemerkt.

Inspiriert vom gstack-`/codex:review`-Pattern, angepasst auf den
Scientific-Writing-Workflow.

## Wann automatisch aufrufen

In den anderen Skills wird der Hook aktiviert, wenn `config.yaml → codex.auto_review: true`:

- Nach `/write` (Kapitel geschrieben → Codex prüft den Draft)
- Nach `/approve` (Kapitel/Phase freigegeben → Codex prüft Konsistenz)
- Nach `/review` (3-Agenten-Review fertig → Codex als 4. Review-Instanz)
- Nach `/compile` (DOCX/PDF gebaut → Codex prüft das Ergebnis)
- Nach `/rewrite` (Kapitel komplett neu → Codex prüft)

## Wann manuell aufrufen

- Vor Abgabe — letzter Sanity-Check
- Nach größeren Edits an mehreren Kapiteln gleichzeitig
- Wenn `/validate` Verstöße meldet, Codex zur Diagnose aufrufen

## Ablauf

### 1. Codex CLI prüfen

Falls `codex` nicht im PATH:
```
codex CLI nicht gefunden. Installation:
  brew install --cask codex
oder npm i -g @openai/codex
Konfiguration in ~/.codex/config.toml: model="gpt-5.5", model_reasoning_effort="xhigh"
```

### 2. Scope bestimmen

Standardmäßig: nicht committete Änderungen (`--uncommitted`). Optionen:

- `/codex-review` (default) → `codex review --uncommitted`
- `/codex-review main` → gegen Branch main: `codex review --base main`
- `/codex-review chapter 2.3` → gezielt eine Kapitel-Datei
- `/codex-review docx` → letzte gebaute DOCX gegen LESSONS.md prüfen
- `/codex-review full` → kompletter Repo-Stand

### 3. Custom Prompt zusammensetzen

Codex bekommt eine Prompt mit:

1. Verweis auf `LESSONS.md` und `.claude/rules/format-checks.md`
2. Konkreter Review-Auftrag je nach Scope
3. Erwartetes Output-Format (strukturierte Liste mit Schwere)

Standard-Prompt (für `--uncommitted`):

```
Du bist Reviewer für eine wissenschaftliche Fallstudie nach IU-Richtlinien.

Lies zuerst:
  - LESSONS.md (kanonische Reviewer-Lessons)
  - .claude/rules/format-checks.md
  - .claude/rules/citation-format.md
  - .claude/rules/writing-style.md
  - preferences.md (Schreibstil + Aktualitäts-Anker)

Prüfe die uncommitteten Änderungen gegen ALLE Lessons aus LESSONS.md.
Schwerpunkte:
  - Format-Lessons (F1–F10)
  - Quellen-Lessons (Q1–Q6: APA-Konformität)
  - Inhalt-Lessons (I1–I5: Aktualität)
  - Methoden-Lessons (M1–M4)
  - Sprache-Lessons (S1–S5)

Output-Format:
  ## Funde
  | Code | Schwere (hoch/mittel/niedrig) | Datei:Zeile | Beschreibung | Fix |
  ## Empfehlung
  Freigabe / Kleine Anpassung / Größere Revision
```

### 4. Codex aufrufen

Bash:
```bash
codex review --uncommitted -- "<prompt>"
# oder für DOCX-Validierung:
python3 scripts/validate_docx.py output/phase-07-docx/<latest>.docx && \
codex exec -- "<docx-prompt>"
```

Codex nutzt automatisch die Defaults aus `~/.codex/config.toml`:
- `model = "gpt-5.5"`
- `model_reasoning_effort = "xhigh"`

Falls in der Repo-`config.yaml` ein anderes Modell gewünscht ist (z. B.
für günstigere Auto-Reviews):
```bash
codex review --uncommitted -c model="gpt-5.5-mini" -c model_reasoning_effort="medium" -- "<prompt>"
```

### 5. Ergebnis darstellen

Codex-Output direkt an den User weiterleiten, plus eine Kurzfassung:

```
=== Codex-Review (gpt-5.5 / xhigh) ===

[Codex-Output]

Zusammenfassung:
  - Hohe Schwere: [N] Funde
  - Mittlere Schwere: [N] Funde
  - Niedrige Schwere: [N] Funde

Empfehlung: [Freigabe / Anpassung / Revision]
```

Bei Freigabe: weiter mit `/approve` oder `/next`.
Bei Anpassung: konkrete Fixes vorschlagen, dann erneut `/codex-review`.

### 6. Logging

Codex-Output in `output/phase-06-review/codex-<timestamp>.md` archivieren,
damit auditierbar ist, was Codex zu welchem Stand gesagt hat.

## Stille Variante (für Auto-Hook)

Wenn der Skill von einem anderen Skill aufgerufen wird (Auto-Hook), in den
Modus „nur Funde mit Schwere `hoch` ausgeben" wechseln, sonst zu viel
Rauschen im Workflow. Schalter: `/codex-review --quiet`.

## Beispiele

```
/codex-review
→ codex review --uncommitted gegen die LESSONS.md

/codex-review docx
→ python3 scripts/validate_docx.py + codex exec auf gebaute DOCX

/codex-review chapter 3.4
→ codex exec auf output/phase-05-writing/final/3-4.md

/codex-review full --strict
→ kompletter Repo-Scan, Exit 1 bei Hochpriorität-Funden
```

## Verhalten bei Fehlern

- `codex` nicht installiert → klare Anleitung, kein Crash.
- `codex` läuft, aber Authentifizierung fehlt → `codex login` empfehlen.
- API-Quota erschöpft → einmal warnen, weiter ohne Auto-Review (Skill nicht blockierend).
