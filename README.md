# Scientific Writing Framework

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Claude Code](https://img.shields.io/badge/Built%20with-Claude%20Code-blueviolet)](https://claude.com/claude-code)

Deine wissenschaftliche Arbeit, von der ersten Idee bis zum fertigen PDF. Komplett im Terminal mit [Claude Code](https://claude.com/claude-code).

Du triffst die Entscheidungen und lieferst die Quellen. Claude übernimmt Strukturierung, Kapitelplanung, wissenschaftliches Schreiben, Qualitätsprüfung und den DOCX-Build (+ PDF). Optimiert für IU-Fallstudien/Seminararbeiten (Deutsch, APA7, 7–10 Seiten). Mit `/auto` läuft die ganze Arbeit unbeaufsichtigt durch und stoppt nur an zwei Freigaben (Thema, Gliederung).

> **English:** AI-powered academic writing framework for [Claude Code](https://claude.com/claude-code), tuned for IU case studies. German-language, APA7, DOCX+PDF output.

## Schnellstart

### 1. Repository klonen

```bash
# Dieses Repository als Template verwenden (GitHub: "Use this template")
# oder direkt klonen:
git clone https://github.com/koljaschoepe/scientific-writing.git meine-arbeit
cd meine-arbeit
```

### 2. Claude Code starten

```bash
claude
```

### 3. Projekt einrichten

```
/setup
```

Das interaktive Interview führt dich in etwa 5 Minuten durch alle Einstellungen: Arbeitstyp, Seitenumfang, Methodik, Zitationsstil, Quellen-Workflow, Formatierung und mehr. Jede Frage bietet dir Auswahlmöglichkeiten, die du mit einem Klick bestätigen oder frei beantworten kannst.

### 4. Los geht's

```
/next
```

Ab hier wiederholst du `/next` und `/approve`, bis die Arbeit fertig ist.

## Workflow

`/setup` · `/next` · `/approve` · `/next` · ... · `/compile` · PDF

| Phase | Was passiert |
|-------|-------------|
| Setup | Interaktives Interview (ca. 5 Minuten) |
| 1 · Brainstorming | Thema und Forschungsfragen entwickeln |
| 2 · Gliederung | Kapitelstruktur erstellen |
| 3 · Zitat-Zuordnung | Quellen den Kapiteln zuweisen* |
| 4+5 · Planung + Schreiben | Kapitel einzeln planen und direkt schreiben |
| 6 · Qualitätsprüfung | 3 Agenten prüfen parallel |
| 7 · Finalisierung | IU-DOCX (Primärartefakt) + PDF |

*Phase 3 wird automatisch übersprungen wenn du im Setup "keine Quellen" gewählt hast.

## Features

- **Autonomer Lauf** (`/auto`): Phase 1→7 unbeaufsichtigt, Halt nur an Thema + Gliederung, Auto-Fix-Schleife bei Validator-Funden
- **7-Phasen-Workflow** von Brainstorming bis fertigem Dokument
- **Interaktives Setup** mit Auto-Detect aus den Uni-Ordnern
- **Verschränktes Arbeiten** (Kapitel einzeln planen und direkt schreiben)
- **Flexible Quellenarbeit** (BibTeX, Zotero, PDF-Extraktion, manuell oder ohne Quellen)
- **APA7** als IU-Standard (Harvard/IEEE/Chicago archiviert unter `docs/archive/`)
- **Kanonischer DOCX-Builder** (`scripts/build_docx.py`, config-parametrisiert) + PDF via LibreOffice
- **3 parallele Reviewer** für Sprache, Zitationen und Argumentation, plus blockierendes `/preflight`-Gate
- **Self-Healing** erkennt und repariert inkonsistente Projektzustände (`/validate --auto-repair`)

## Befehle

| Befehl | Beschreibung |
|--------|-------------|
| `/auto` | **Autonomer Lauf 1→7** (Halt nur an Thema + Gliederung) |
| `/setup` | Projekt einrichten (Auto-Detect aus Uni-Ordnern) |
| `/next` | Nächste Phase starten (Einzelschritt) |
| `/status` | Fortschritt anzeigen (mit Self-Healing) |
| `/write [X.X]` | Kapitel schreiben |
| `/review [X.X]` · `--all` | Qualitätsprüfung (3 Agenten parallel) |
| `/humanize [X.X]` · `--all` | KI-Schreibspuren entfernen, Stil natürlicher (Stilpass; Inhalt/Zitate/Zahlen unverändert) |
| `/cite` | Quelle hinzufügen (PDF, manuell, BibTeX, Zotero) |
| `/preflight` | Blockierendes Pre-Compile-Gate |
| `/compile` | IU-DOCX + PDF bauen |
| `/compile draft` | Entwurf, auch mit fehlenden Kapiteln |
| `/apply-feedback` | Reviewer-Feedback ins finale DOCX patchen |
| `/codex-review` | Externer Codex-Review (gpt-5.5 / xhigh) |
| `/approve [X.X]` | Phase oder Kapitel freigeben |
| `/wordcount` | Wortanzahl und Seitenschätzung |
| `/rewrite [X.X]` | Kapitel komplett neu schreiben |
| `/reset [phase]` | Auf frühere Phase zurücksetzen |
| `/validate` | Projektkonfiguration prüfen (`--auto-repair`) |
| `/help` | Kontextsensitive Hilfe |

## Quellen importieren

```
/cite
```

Vier Wege:
1. **BibTeX-Import** (.bib-Datei direkt importieren)
2. **Zotero-Import** (CSV, RIS oder BibTeX aus Zotero)
3. **PDF-Analyse** (Claude extrahiert Metadaten und Zitate)
4. **Manuell** (schrittweise Eingabe)

## Voraussetzungen

- [Claude Code CLI](https://claude.com/claude-code) installiert
- **python-docx** (Pflicht für den DOCX-Build): `pip install python-docx`
- **LibreOffice** (optional, für die PDF-Konvertierung der DOCX): ohne LibreOffice bleibt die DOCX das Primärartefakt; PDF dann via „Speichern als PDF" in Word/LibreOffice
  - macOS: `brew install --cask libreoffice`
  - Linux: `sudo apt install libreoffice`

## Dokumentation

- [Einstieg](docs/einstieg.md) (Schritt-für-Schritt-Anleitung)
- [Konfiguration](docs/konfiguration.md) (alle config.yaml-Optionen)
- [Literaturdatenbank](docs/literaturdatenbank.md) (Format, BibTeX, Zotero)
- [FAQ](docs/faq.md) (häufige Fragen)
- Andere Hochschulen / Zitierstile: archiviert unter [docs/archive/](docs/archive/)

## Contributing

Beiträge sind willkommen! Siehe [CONTRIBUTING.md](CONTRIBUTING.md).

## Lizenz

[MIT](LICENSE)
