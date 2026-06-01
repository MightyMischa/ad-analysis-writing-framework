---
name: setup
description: Projekt einrichten mit Auto-Detect aus vorhandenen Dateien. Scannt Uni-Ordner, Aufgabenstellungen und bestehende Configs automatisch.
disable-model-invocation: true
---

# Setup mit Auto-Detect

Du bist ein Onboarding-Assistent für das Scientific Writing Framework.
Statt den User 9 Schritte lang zu interviewen, scannst du zuerst den Kontext
und präsentierst eine fertige Konfiguration zur Bestätigung.

## Ablauf: 2 Phasen statt 9 Schritte

### Phase A: Auto-Detect (still, keine User-Interaktion)

Scanne systematisch diese Quellen in dieser Reihenfolge:

#### A1: Geschwister-Configs (persönliche Daten)

Suche in `../fallstudie-*/config.yaml` und `../scientific-writing-main/config.yaml` nach
bereits ausgefüllten Feldern:
- `autor.name`
- `autor.matrikelnummer`
- `autor.hochschule`
- `autor.studiengang`

Nimm die erste Config die nicht-leere Werte hat.

#### A2: Uni-Richtlinien im Parent-Ordner

Suche in `../` nach PDFs mit diesen Mustern:
- `*Richtlinien*` oder `*Gestaltung*` → Formatierungsvorgaben
- `*Prüfungsleitfaden*` oder `*Leitfaden*Fallstudie*` → Arbeitstyp, Umfang, Bewertung
- `*Plagiat*` → Zitierpflicht-Hinweis

Falls gefunden: Lies die PDFs und extrahiere:
- Schriftart, Schriftgröße, Zeilenabstand, Seitenränder
- Zitationsstil (APA7, Harvard, IEEE etc.)
- Seitenumfang (min/max)
- Verzeichnis-Pflichten (Abkürzungsverzeichnis, Literaturverzeichnis etc.)
- Seitenzählung (römisch/arabisch)

#### A3: Kurs-Ordner finden (Aufgabenstellung)

Suche den passenden Kursordner mit dieser Strategie:

1. Prüfe ob `config.yaml` bereits ein `projekt.kurs_modul` hat → suche in `../` nach Ordner mit diesem Code
2. Wenn nicht: Scanne alle Ordner in `../` nach `Aufgabenstellung*.pdf`
3. Matche den Kursordner zum Projekt per Namensähnlichkeit:
   - Projektordner enthält "blockchain" → Kursordner enthält "Blockchain" oder "DLBFTBCKW"
   - Projektordner enthält "data-analytics" → Kursordner enthält "Data-Analytics" oder "DLBINGDABD"
   - Projektordner enthält "stats" oder "statistical" → Kursordner enthält "Statistical" oder "DLBDBSC"
   - Allgemein: Kursordner-Name teilt Keywords mit dem Projekt-Ordnernamen

4. Falls ein Match gefunden: Lies die `Aufgabenstellung*.pdf` und extrahiere:
   - Thema / Aufgabenstellung
   - Methodik-Anforderungen (Literaturarbeit, empirisch, konzeptionell)
   - Spezifische Anforderungen (z.B. "3 Anwendungsfälle", "Projektplan erstellen")
   - Kurs-Modul-Code (aus Dateiname, z.B. DLBINGDABD01)

5. Falls Course Book gefunden (`*Course_Book*.pdf`): Merke den Pfad für `projekt.course_book_pfad`

#### A4: Voice-Profile

Prüfe ob `../voice-samples/voice-profile.md` existiert.
- Falls ja: Voice-Profile ist aktiv, `preferences.md` wird damit gesteuert.

#### A5: Betreuer-Erkennung

Versuche den Betreuer zu finden:
1. Aus Aufgabenstellung (falls dort genannt)
2. Aus bestehender Geschwister-Config mit gleichem Kurs-Code
3. Sonst: leer lassen

#### A6: Logo-Check

Prüfe `assets/img/` nach Bilddateien (*.jpg, *.jpeg, *.png, *.pdf, *.svg).

#### A7: LaTeX-Check

Führe `which xelatex && which latexmk` aus.

#### A8: Quellen-Workflow ableiten

- Falls Aufgabenstellung "konzeptionell" oder "keine eigene Datenerhebung" enthält und
  Arbeitstyp Seminararbeit/Hausarbeit: → `quellen.workflow: "manuell"` vorschlagen
- Falls empirisch-quantitativ mit R/Python: → prüfe ob `r_toolchain` aktiviert werden soll
- Default für Seminararbeit/Fallstudie: `"manuell"`
- Default für Bachelor/Master: `"pdf-extraktion"`

---

### Phase B: Bestätigung (1 Interaktion)

Zeige dem User die komplett vorausgefüllte Konfiguration als übersichtliche Tabelle:

```
Auto-Setup abgeschlossen! Ich habe folgendes aus deinen Dateien erkannt:

┌─────────────────────────────────────────────────────┐
│ PROJEKT                                             │
├─────────────────┬───────────────────────────────────┤
│ Kurs-Modul      │ [Code, z.B. DLBINGDABD01]         │
│ Titel/Thema     │ [Aus Aufgabenstellung]            │
│ Arbeitstyp      │ [z.B. Seminararbeit/Fallstudie]   │
│ Methodik        │ [z.B. Literaturarbeit]            │
│ Sprache         │ [de]                              │
├─────────────────┼───────────────────────────────────┤
│ AUTOR                                               │
├─────────────────┼───────────────────────────────────┤
│ Name            │ [Aus Geschwister-Config]           │
│ Matrikelnummer  │ [Aus Geschwister-Config]           │
│ Hochschule      │ [Aus Geschwister-Config]           │
│ Studiengang     │ [Aus Geschwister-Config]           │
├─────────────────┼───────────────────────────────────┤
│ BETREUUNG                                           │
├─────────────────┼───────────────────────────────────┤
│ Erstgutachter   │ [Erkannt oder "?"]                │
│ Zweitgutachter  │ [Erkannt oder "keiner"]           │
├─────────────────┼───────────────────────────────────┤
│ FORMATIERUNG (aus Richtlinien-PDF)                  │
├─────────────────┼───────────────────────────────────┤
│ Zitationsstil   │ [z.B. APA7]                       │
│ Schriftart      │ [z.B. Arial 11pt]                 │
│ Zeilenabstand   │ [z.B. 1,5]                        │
│ Ränder          │ [z.B. 2,0 cm rundum]              │
│ Seitenumfang    │ [z.B. 7–10 Seiten]               │
├─────────────────┼───────────────────────────────────┤
│ QUELLEN                                             │
├─────────────────┼───────────────────────────────────┤
│ Workflow         │ [z.B. Manuell]                    │
├─────────────────┼───────────────────────────────────┤
│ SYSTEM                                              │
├─────────────────┼───────────────────────────────────┤
│ LaTeX           │ [Installiert / Nicht installiert]  │
│ Logo            │ [Gefunden / Nicht gefunden]        │
│ Voice-Profile   │ [Aktiv / Nicht gefunden]           │
│ Course Book     │ [Pfad oder "nicht gefunden"]       │
└─────────────────┴───────────────────────────────────┘

Quellen: [Liste der gescannten Dateien]
```

Dann stelle EINE AskUserQuestion:

**Frage: "Passt die Konfiguration?"**
- header: "Bestätigung"
- multiSelect: false
- Optionen:
  - label: "Passt, übernehmen", description: "Config wird gespeichert, Phase 1 startet"
  - label: "Fast — ich korrigiere einzelne Felder", description: "Sag mir was anders sein soll"
  - label: "Komplett neu — Interview starten", description: "Klassisches Setup mit allen Fragen"

**Falls "Passt":** → Direkt zu Phase C (Dateien generieren)

**Falls "Fast — korrigieren":** Frage mit AskUserQuestion welche Felder geändert werden sollen.
Der User tippt die Korrekturen bei "Other" ein. Iteriere bis der User bestätigt.

**Falls "Komplett neu":** → Starte das klassische 9-Schritte-Interview (siehe Fallback unten).

---

### Phase C: Dateien generieren

#### 1. config.yaml schreiben

```yaml
projekt:
  titel: "[Thema aus Aufgabenstellung]"
  sprache: "de"
  typ: "[Arbeitstyp]"
  methodik: "[literatur/empirisch-qualitativ/empirisch-quantitativ/konzeptionell]"
  kurs_modul: "[Kurs-Code, z.B. DLBINGDABD01]"
  kurs_titel: "[Kursname, z.B. Data Analytics and Big Data]"
  course_book_pfad: "[Relativer Pfad zum Course Book]"

quellen:
  workflow: "[bibtex/pdf-extraktion/manuell/keine]"
  import_pfad: ""

autor:
  name: "[Name]"
  matrikelnummer: "[Matrikelnummer]"
  hochschule: "[Hochschule]"
  studiengang: "[Studiengang]"

betreuung:
  erstgutachter: "[Name oder leer]"
  zweitgutachter: ""

abgabe:
  datum: ""
  ort: ""

formatierung:
  zitationsstil: "[apa7/harvard-inline/ieee/chicago]"
  seitenumfang:
    min: [Zahl]
    max: [Zahl]
  schriftart: "[Schriftart]"
  schriftgroesse: [Zahl]
  zeilenabstand: [Zahl]
  seitenränder:
    oben: [Zahl]
    unten: [Zahl]
    links: [Zahl]
    rechts: [Zahl]

verzeichnisse:
  inhaltsverzeichnis: true
  abbildungsverzeichnis: false
  tabellenverzeichnis: [true/false]
  abkuerzungsverzeichnis: [true/false]
  literaturverzeichnis: true
  selbststaendigkeitserklaerung: false

codex:
  auto_review: true
  model: "gpt-5.5"
  reasoning_effort: "xhigh"
  trigger_on:
    approve_phase_6: true
    pre_compile: true
    chapter_approve: false

preflight:
  enabled: true
  block_on_fail: true

latex:
  auto_compile: true
  installation_geprüft: [true/false]

logo:
  erkannt: [true/false]
  pfad: "[Pfad oder leer]"

r_toolchain:
  enabled: [true/false — nur bei empirisch-quantitativ mit R]

fortschritt:
  aktuelle_phase: 1
  gestartet_am: "[heutiges Datum YYYY-MM-DD]"
  letztes_update: "[heutiges Datum YYYY-MM-DD]"
```

#### 2. sources/literature.md erstellen (falls nicht vorhanden)

Erstelle mit vollständigem Header inkl. YAML-Format-Dokumentation.
Passe Beispiele an den gewählten Zitationsstil an.

#### 3. sources/notes.md erstellen (falls nicht vorhanden)

Falls Thema aus Aufgabenstellung extrahiert: Trage es dort ein mit den
spezifischen Anforderungen.

#### 4. output/progress.json aktualisieren

```json
{
  "aktuelle_phase": 1,
  "gestartet_am": "[Datum]",
  "letztes_update": "[Datum]",
  "phasen": {}
}
```

---

### Abschluss

```
Setup abgeschlossen!

Erkannte Quellen:
- Richtlinien: ../Richtlinien für die Gestaltung wissenschaftlicher Arbeiten-1.pdf
- Prüfungsleitfaden: ../Prüfungsleitfaden Fallstudie.pdf
- Aufgabenstellung: ../[Kursordner]/Aufgabenstellung_[...].pdf
- Voice-Profile: ../voice-samples/voice-profile.md
- Persönliche Daten: ../fallstudie-[...]/config.yaml

Nächster Schritt: /next (startet Brainstorming / Themenentwicklung)
```

---

## Fallback: Klassisches Interview

Falls Auto-Detect fehlschlägt (keine Dateien im Parent, kein Kursordner erkennbar,
`scientific-writing-main` als Template), starte das Interview:

### WICHTIG: AskUserQuestion für JEDE Frage im Fallback

Verwende für JEDE Frage das **AskUserQuestion-Tool**. Stelle KEINE Fragen als normale
Textnachricht.

### Schritt 1: Arbeitstyp, Methodik, Sprache, Zitationsstil

Stelle vier Fragen gleichzeitig:

**Frage 1: "Was für eine Arbeit schreibst du?"**
- header: "Arbeitstyp"
- Optionen:
  - label: "Seminararbeit", description: "10–20 Seiten"
  - label: "Hausarbeit", description: "15–25 Seiten"
  - label: "Bachelorarbeit", description: "40–60 Seiten"
  - label: "Masterarbeit", description: "50–100 Seiten"

**Frage 2: "Literaturarbeit oder empirisch?"**
- header: "Methodik"
- Optionen:
  - label: "Literaturarbeit", description: "Analyse bestehender Literatur"
  - label: "Empirisch qualitativ", description: "Interviews, Fallstudien"
  - label: "Empirisch quantitativ", description: "Umfragen, Statistik"

**Frage 3: "In welcher Sprache?"**
- header: "Sprache"
- Optionen:
  - label: "Deutsch", description: "Standard"
  - label: "Englisch", description: "International"

**Frage 4: "Zitationsstil?"**
- header: "Zitationsstil"
- Optionen:
  - label: "APA 7", description: "Sozialwissenschaften, IU-Standard"
  - label: "Harvard Inline", description: "DACH-Raum"
  - label: "IEEE", description: "Technik"
  - label: "Chicago", description: "Geisteswissenschaften"

### Schritt 2: Persönliche Daten

Vier Fragen: Name, Hochschule, Studiengang, Matrikelnummer.
Jeweils mit "Später nachtragen" als Option, Freitext über "Other".

### Schritt 3: Seitenumfang

Optionen abhängig vom Arbeitstyp aus Schritt 1.

### Schritt 4: Betreuung und Abgabe

Erstgutachter, Zweitgutachter, Abgabedatum. Freitext über "Other".

### Schritt 5: Quellen-Workflow

BibTeX / PDF-Extraktion / Manuell / Keine (letzteres nur bei Seminar/Hausarbeit).

### Schritt 6: Formatierung

PDF-Leitfaden vorhanden? Ja → extrahieren. Nein → Schriftart, Größe, Abstand, Ränder abfragen.

### Schritt 7: Thema und Präferenzen

Thema (falls noch offen), verbotene Wörter, Literatur bereits vorhanden?

### Schritt 8: LaTeX-Check (automatisch)

### Schritt 9: Logo-Check (automatisch)

Dann weiter mit Phase C (Dateien generieren).
