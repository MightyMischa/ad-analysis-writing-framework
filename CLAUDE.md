# Scientific Writing Framework (v3, IU-Fallstudien)

Deine IU-Fallstudie, von der ersten Idee bis zur fertigen DOCX (+ PDF).

Du triffst die Entscheidungen und lieferst die Quellen. Claude übernimmt Strukturierung, Kapitelplanung, wissenschaftliches Schreiben, Qualitätsprüfung und den DOCX-Build. Optimiert für IU-Fallstudien/Seminararbeiten (Deutsch, APA7, 7–10 Seiten). Alles im Terminal, alles in einem Projekt.

## Schnellstart

**Autonom (empfohlen):**
- `/setup` ausführen (scannt Uni-Ordner automatisch, ~30 Sekunden Bestätigung)
- `/auto` ausführen — läuft Phase 1→7 durch und stoppt nur an zwei Stellen zur Freigabe: nach dem **Thema** (Brainstorming) und nach der **Gliederung**. Danach unbeaufsichtigt bis DOCX+PDF, mit Auto-Fix bei Validator-Funden.

**Manuell (Schritt für Schritt):**
1. `/setup` · 2. `/next` (nächste Phase) · 3. mit `/approve` freigeben · 4. wiederholen bis fertig.

## Workflow

`/setup` · `/next` · `/approve` · `/next` · ... · `/compile` · PDF

| Phase | Was passiert |
|-------|-------------|
| 1 · Brainstorming | Thema und Forschungsfragen entwickeln |
| 2 · Gliederung | Kapitelstruktur erstellen (danach gesperrt) |
| 3 · Zitat-Zuordnung | Quellen den Kapiteln zuweisen |
| 4+5 · Planung + Schreiben | Kapitel einzeln planen und direkt schreiben |
| 6 · Qualitätsprüfung | Sprache, Zitate, Argumentation (3 Agenten parallel) |
| 7 · Finalisierung | IU-DOCX (Primärartefakt) + PDF via `scripts/build_docx.py` |

Phase 3 wird automatisch übersprungen wenn `quellen.workflow: "keine"` gesetzt ist.

In Phase 4 und 5 wird verschränkt gearbeitet: Ein Kapitel planen, direkt schreiben, nächstes Kapitel planen, schreiben. Kein stundenlanges Vorausplanen ohne Ergebnis.

## Befehle

| Befehl | Funktion |
|--------|----------|
| `/auto` | **Autonomer End-to-End-Lauf 1→7** (stoppt nur an Thema + Gliederung, Auto-Fix-Schleife) |
| `/setup` | Projekt einrichten (Auto-Detect aus Uni-Ordnern) |
| `/next` | Nächste Phase starten (Einzelschritt) |
| `/status` | Fortschritt anzeigen (mit Self-Healing) |
| `/write [X.X]` | Kapitel schreiben |
| `/review [X.X]` · `/review --all` | Qualitätsprüfung (3 Agenten parallel; `--all` über alle Kapitel) |
| `/cite` | Quelle hinzufügen (PDF, manuell, BibTeX, Zotero) |
| `/compile` | IU-DOCX + PDF bauen (`scripts/build_docx.py`, PDF via LibreOffice) |
| `/compile draft` | Entwurf bauen, auch mit fehlenden Kapiteln |
| `/approve [X.X]` | Phase oder Kapitel freigeben (draft → final) |
| `/wordcount` | Wortanzahl und Seitenschätzung |
| `/rewrite [X.X]` | Kapitel komplett neu schreiben |
| `/reset [phase]` | Auf frühere Phase zurücksetzen (archiviert Ergebnisse) |
| `/validate` | Projektkonfiguration und Datenintegrität prüfen (`--auto-repair` für stille Reparatur) |
| `/preflight` | Blockierendes Pre-Compile-Gate (validate + Lit-Verz-Drift + Pitfalls + Wordcount) |
| `/apply-feedback` | Reviewer-Feedback ins finale DOCX einarbeiten (preserves Format-Fixes) |
| `/codex-review` | Externer Codex-Review (gpt-5.5 / xhigh) gegen LESSONS.md |
| `/help` | Kontextsensitive Hilfe |

## Pre-Submit-Workflow (Fallstudien)

Vor jeder finalen Abgabe:

1. `/preflight` — alle Validator-Checks (F1–F9, S1–S5, I1–I2, **C1, M1, N1**, Lit-Verz-Drift)
2. Bei blockierenden Verstößen: korrigieren, erneut `/preflight`
3. Bei externem Reviewer-Feedback: `/apply-feedback` — generiert Patch-Skript für DOCX
4. Bei `_final_konform.docx` als Source-of-Truth: **DOCX-Frozen-Mode** schützt vor versehentlichem Re-Build

Das Skill `/preflight` blockiert `/compile` und `/approve` bis alle harten Verstöße behoben sind. Override via `/preflight --override` (mit Logging und Begründung).

## Regeln für generierte Texte

Diese Regeln gelten immer:

- Jede Behauptung muss mit einer Quelle belegt sein (Dichte nach Arbeitstyp, siehe writing-style Rule). Ausnahme: Bei `quellen.workflow: "keine"` entfällt die Zitationspflicht.
- Keine Ich-Form, sachlich-neutral schreiben
- Zitate ausschließlich aus `sources/literature.md` verwenden (entfällt bei quellen.workflow "keine")
- Wörter nicht in benachbarten Sätzen wiederholen
- Roter Faden: Jedes Kapitel baut implizit auf dem vorherigen auf
- Keine Gedankenstriche, kein Semicolon, selten Doppelpunkte

Übergänge zwischen Kapiteln:
- Kein letzter Satz der das nächste Kapitel ankündigt
- Kein erster Satz der das vorherige Kapitel zusammenfasst
- Keine expliziten Kapitelverweise ("Wie in Kapitel X dargelegt...")
- Verbindung durch Konzeptnamen, nicht durch Verweise

Zitationsformat wird aus `config.yaml` geladen (Agents laden ausschließlich den aktiven Stil).
Schreibpräferenzen: @preferences.md

## Projektstruktur

| Ordner/Datei | Zweck |
|-------------|-------|
| `config.yaml` | Zentrale Konfiguration (von `/setup` generiert) |
| `preferences.md` | Schreibpräferenzen (verbotene Wörter etc.) |
| `sources/` | Quellen, Zitate und Notizen |
| `sources/pdfs/` | Quell-PDFs ablegen |
| `assets/img/` | Hochschul-Logo und Bilder |
| `base/` | Leitfäden, Zitationsstile, Vorlagen |
| `output/` | Generierte Inhalte (pro Phase, draft/final) |
| `docs/` | Ausführliche Dokumentation |
| `LESSONS.md` | Reviewer-Lessons (Format, Quellen, Inhalt, Sprache) — nach jedem Review erweitern |
| `scripts/build_docx.py` | **Kanonischer DOCX-Builder** (config-parametrisiert) + PDF via LibreOffice |
| `scripts/validate_docx.py` | Automatischer DOCX-Validator gegen IU-Vorgaben (F/S/I/C/M/N-Codes) |
| `scripts/check_lit_verz_drift.py` | Diff DOCX-Lit-Verz vs. literature.md (bidirektional) |
| `scripts/validate_r_reproducibility.py` | R-Skript-Reproduzierbarkeit (R1–R5), aktiv wenn r_toolchain.enabled |
| `base/templates/feedback-patch.py.template` | Vorlage für /apply-feedback-Patch-Skripte |

## Kontext-Regeln für Agents

- Lies immer zuerst `config.yaml` für die aktuelle Konfiguration
- Prüfe `config.yaml → quellen.workflow` (bei "keine" entfallen alle Zitationsschritte)
- Lade den Zitationsstil aus `base/guides/citation-systems/{config.formatierung.zitationsstil}.md`
- Lade nicht alle Zitationsstile, nur den aktiven
- Lade `preferences.md` für benutzerdefinierte Schreibpräferenzen
- Lade Base-Guides modular: nur die für die aktuelle Aufgabe relevanten Dateien
- Aktualisiere `output/progress.json` nach jeder abgeschlossenen Aktion
- Writer: Lade nur das vorherige Kapitel komplett, von älteren nur die letzten 2 Absätze

## Erste Schritte

Noch kein Projekt eingerichtet? Starte mit `/setup`.

Bereits eingerichtet? Setze fort mit `/next`.

Probleme? Starte mit `/validate`.
