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
| 6 · Qualitätsprüfung | Sprache, Zitate, Argumentation, KI-Stil (4 Agenten parallel, optional + Codex) |
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
| `/review [X.X]` · `/review --all` | Qualitätsprüfung (4 Agenten parallel; `--all` über alle Kapitel + Gesamtwerk-Pass) |
| `/humanize [X.X]` · `/humanize --all` | KI-Schreibspuren entfernen, Stil natürlicher machen (reiner Stilpass; Inhalt, Zitate und Zahlen bleiben unverändert) |
| `/cite` | Quelle hinzufügen (PDF, manuell, BibTeX, Zotero) |
| `/compile` | IU-DOCX + PDF bauen (`scripts/build_docx.py`, PDF via LibreOffice) |
| `/compile draft` | Entwurf bauen, auch mit fehlenden Kapiteln |
| `/approve [X.X]` | Phase oder Kapitel freigeben (draft → final) |
| `/wordcount` | Wortanzahl und Seitenschätzung |
| `/rewrite [X.X]` | Kapitel komplett neu schreiben |
| `/reset [phase]` | Auf frühere Phase zurücksetzen (archiviert Ergebnisse) |
| `/validate` | Projektkonfiguration und Datenintegrität prüfen (`--auto-repair` für stille Reparatur) |
| `/preflight` | Blockierendes Pre-Compile-Gate (validate + Lit-Verz-Drift + Pitfalls + Stil-Linter + Wordcount) |
| `/preview` | HTML-Content-Preview des DOCX (Struktur, Umbrüche, Sektions-Banner) ohne Word |
| `/apply-feedback` | Reviewer-Feedback als YAML-Patch ins finale DOCX einarbeiten (preserves Format-Fixes) |
| `/codex-review` | Externer Codex-Review (gpt-5.5 / xhigh) gegen LESSONS.md |
| `/help` | Kontextsensitive Hilfe |

## Pre-Submit-Workflow (Fallstudien)

Vor jeder finalen Abgabe:

1. `/preflight` — alle Validator-Checks (F1–F9, S1/S3/S4, **C1, M1, N1**, Stil-Linter L1–L15, Lit-Verz-Drift)
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

**Stil-Autorität (bei Konflikten in dieser Reihenfolge):**
`voice-profile.md` (Snapshot im Projekt-Root, Pfad aus `config.yaml → stil.voice_profile`) > `.claude/rules/ai-writing-signs.md` > `.claude/rules/writing-style.md` > `base/guides/*`.
Das Voice-Profil wird von `/setup` aus `../voice-samples/voice-profile.md` kopiert und von Writer, Humanize und Reviewern geladen.

Zitationsformat wird aus `config.yaml` geladen (Agents laden ausschließlich den aktiven Stil).
Schreibpräferenzen: @preferences.md

## Projektstruktur

| Ordner/Datei | Zweck |
|-------------|-------|
| `config.yaml` | Zentrale Konfiguration (von `/setup` generiert) |
| `preferences.md` | Schreibpräferenzen (verbotene Wörter etc.) |
| `voice-profile.md` | Persönliches Stilprofil (Snapshot; Quelle: `../voice-samples/`, Re-Sync via `/setup --refresh-voice`) |
| `sources/` | Quellen, Zitate und Notizen |
| `sources/pdfs/` | Quell-PDFs ablegen |
| `assets/img/` | Hochschul-Logo und Bilder |
| `base/` | Leitfäden, Zitationsstile, Vorlagen |
| `output/` | Generierte Inhalte (pro Phase, draft/final) |
| `docs/` | Ausführliche Dokumentation |
| `LESSONS.md` | Reviewer-Lessons (Format, Quellen, Inhalt, Sprache) — nach jedem Review erweitern |
| `scripts/build_docx.py` | **Kanonischer DOCX-Builder** (config-parametrisiert) + PDF via LibreOffice |
| `scripts/validate_docx.py` | Automatischer DOCX-Validator gegen IU-Vorgaben (F/S/C/M/N-Codes; S4 liest projektspezifische Pitfalls aus preferences.md) |
| `scripts/lint_style.py` | **Deterministischer Stil-Linter** (L1–L15: verbotene Wörter/Floskeln blockierend, Rhythmus-Metriken Warnung); `--digest` erzeugt `output/style-digest.md` |
| `scripts/check_lit_verz_drift.py` | Diff DOCX-Lit-Verz vs. literature.md (bidirektional); „zitiert, aber fehlt im Lit-Verz" blockiert |
| `scripts/measure_pages.py` | Soft-Render: misst echten Textteil-Seitenumfang via LibreOffice, sonst Fallback auf manuelles Gate |
| `scripts/review_tracking.py` | Markiert Kapitel nach /review · /humanize; Preflight warnt bei späterer Änderung |
| `scripts/validate_r_reproducibility.py` | R-Skript-Reproduzierbarkeit (R1–R5), aktiv wenn r_toolchain.enabled |
| `scripts/docx_inspect.py` | DOCX-Inspektion: Outline, Element-JSON, Substring-Suche mit Run-Struktur |
| `scripts/docx_patch.py` | Deklarative DOCX-Punkt-Patches aus YAML (Multi-Run-Replace, Dry-Run) — Motor von /apply-feedback |
| `scripts/docx_preview.py` | DOCX→HTML-Content-Preview mit Format-Banner je Sektion — Motor von /preview |
| `base/templates/feedback-patch.py.template` | Fallback-Vorlage für /apply-feedback (Ops jenseits des Patch-YAML) |

## Kontext-Regeln für Agents

- Lies immer zuerst `config.yaml` für die aktuelle Konfiguration
- Prüfe `config.yaml → quellen.workflow` (bei "keine" entfallen alle Zitationsschritte)
- Lade den Zitationsstil aus `base/guides/citation-systems/{config.formatierung.zitationsstil}.md`
- Lade nicht alle Zitationsstile, nur den aktiven
- Lade `preferences.md` für benutzerdefinierte Schreibpräferenzen
- Lade Base-Guides modular: nur die für die aktuelle Aufgabe relevanten Dateien
- Aktualisiere `output/progress.json` nach jeder abgeschlossenen Aktion
- Writer: Lade nur das vorherige Kapitel komplett; für ältere Kapitel den Stil-Digest (`lint_style.py --all --digest` → `output/style-digest.md`)

## Erste Schritte

Noch kein Projekt eingerichtet? Starte mit `/setup`.

Bereits eingerichtet? Setze fort mit `/next`.

Probleme? Starte mit `/validate`.
