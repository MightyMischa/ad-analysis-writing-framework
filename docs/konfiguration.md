# Konfiguration

Alle Optionen in `config.yaml` im Überblick. Diese Datei wird von `/setup` automatisch generiert. Defaults sind auf IU-Fallstudien eingestellt (Arial 11, 1,5-zeilig, 2 cm Ränder, 7–10 Seiten, APA7).

## Projekt

```yaml
projekt:
  titel: "Dein Arbeitstitel"        # Wird in Phase 1/2 festgelegt
  sprache: "de"                     # nur Deutsch (kein Englisch-Support implementiert)
  typ: "fallstudie"                 # seminararbeit | fallstudie (weitere Typen archiviert)
  methodik: "literatur"             # literatur | empirisch-qualitativ | empirisch-quantitativ
  kurs_modul: "DLBXYZ01"            # IU-Modulkürzel — PFLICHT bei Fallstudien
  kurs_titel: "Klartext des Kurses"
  course_book_pfad: ""              # Pfad zum Lernskript-PDF (für Pflicht-Zitation C1)
  semester: ""                      # Titelblatt, optional
```

### Arbeitstypen und empfohlene Seitenumfänge

| Typ | Seitenumfang Textteil | Kapitelmodell |
|-----|----------------------|---------------|
| fallstudie | 7-10 Seiten | IU-Fallstudienmodell |
| seminararbeit | 7-10 Seiten | 3-Kapitel |

Weitere Typen (hausarbeit, bachelor, master, dissertation) sind unter
`docs/archive/kapitelmodelle-all.md` archiviert und nicht mehr wählbar.

## Autor

```yaml
autor:
  name: "Max Mustermann"
  matrikelnummer: "12345"
  hochschule: "IU Internationale Hochschule"
  fakultaet: ""
  studiengang: ""
```

## Betreuung und Abgabe

```yaml
betreuung:
  erstgutachter: "Tutor:in"         # IU-Fallstudien: nur ein:e Tutor:in

abgabe:
  datum: "TT.MM.JJJJ"               # PFLICHT vor finalem Build (Validator F9)
  ort: ""
```

## Formatierung

```yaml
formatierung:
  zitationsstil: "apa7"             # IU-Standard seit 01.10.2025 (harvard/ieee/chicago archiviert)
  seitenumfang:
    min: 7                          # Textteil (Einleitung bis Fazit)
    max: 10
  schriftart: "Arial"
  schriftgroesse: 11
  zeilenabstand: 1.5
  seitenränder:
    oben: 2.0                       # in cm (IU: 2,0 rundum)
    unten: 2.0
    links: 2.0
    rechts: 2.0
```

## Stil (Voice-Profil)

```yaml
stil:
  voice_profile: "voice-profile.md"                          # Snapshot im Projekt-Root
  voice_profile_quelle: "../voice-samples/voice-profile.md"  # Single Source of Truth
  voice_profile_hash: ""                                     # sha256 des Snapshots (von /setup gesetzt)
```

Das Voice-Profil steuert Satzrhythmus, Konnektoren und persönliche Stil-Marker
für Writer, Humanize und die Reviewer. `/setup` kopiert es aus der Quelle;
`/validate` warnt, wenn der Snapshot veraltet ist (`/setup --refresh-voice`).

## Verzeichnisse

```yaml
verzeichnisse:
  inhaltsverzeichnis: true
  abbildungsverzeichnis: false      # nur falls Abbildungen vorhanden
  tabellenverzeichnis: false        # nur falls Tabellen mit SEQ-Caption vorhanden
  abkuerzungsverzeichnis: true
  literaturverzeichnis: true
  selbststaendigkeitserklaerung: true
```

## Quellen

```yaml
quellen:
  workflow: "manuell"               # bibtex | pdf-extraktion | manuell | keine
  import_pfad: ""                   # Pfad zur .bib oder Zotero-Exportdatei
```

| Workflow | Beschreibung |
|----------|-------------|
| `bibtex` | Import aus .bib-Datei (BibTeX/BibLaTeX) |
| `pdf-extraktion` | KI-basierte Extraktion aus PDF-Dateien |
| `manuell` | Quellen einzeln per `/cite` erfassen |
| `keine` | Ohne Quellen arbeiten (Phase 3 wird übersprungen) |

## Qualitäts-Gates

```yaml
codex:
  auto_review: true                 # Nach jedem Schritt automatisch /codex-review
  model: "gpt-5.5"
  reasoning_effort: "xhigh"

preflight:
  enabled: true                     # Pre-Compile-Gate aktiv
  block_on_violation: true          # /compile + /approve blockieren bei harten Verstößen

docx_frozen:
  enabled: false                    # Auto-true sobald _final_konform.docx existiert
  block_overwrite: true
  warn_on_markdown_edit: true
```

## Autonomer Lauf

```yaml
workflow:
  auto:
    gates: ["topic", "outline"]     # Menschliche Halte; [] = voll autonom
    max_autofix_attempts: 3
    audit_log: "output/auto-run.log"
```

## Logo

```yaml
logo:
  pfad: "assets/img/iu-logo.png"    # Wird von /setup automatisch erkannt
  erkannt: true
```

## Fortschritt

```yaml
fortschritt:
  aktuelle_phase: 3                 # 0-7
  abgeschlossene_phasen: [1, 2]
  gestartet_am: "2026-03-12"
  letztes_update: "2026-03-15"
```

## Eigenen Zitationsstil hinzufügen

1. Kopiere `base/guides/citation-systems/_vorlage.md`
2. Benenne die Kopie (z.B. `mein-stil.md`)
3. Fülle die Vorlage aus
4. Trage den Dateinamen (ohne .md) in config.yaml ein:
   ```yaml
   formatierung:
     zitationsstil: "mein-stil"
   ```
