# Häufige Fragen (FAQ)

## Allgemein

### Für welche Arbeiten ist das Framework geeignet?
Optimiert für IU-Fallstudien und Seminararbeiten (7-10 Seiten, Deutsch, APA7).
Besonders gut für Literaturarbeiten und konzeptionelle Arbeiten. Andere
Arbeitstypen (Bachelor/Master/Dissertation) und Zitierstile sind unter
`docs/archive/` archiviert und nicht mehr im Setup wählbar.

### Muss ich Word oder python-docx kennen?
Nein. Das Framework baut die IU-konforme DOCX automatisch über
`scripts/build_docx.py` und konvertiert sie per LibreOffice zu PDF.
Du arbeitest nur mit Markdown und Slash-Befehlen.

### In welcher Sprache kann ich schreiben?
Deutsch. Englisch-Support ist aktuell nicht implementiert
(siehe `config.yaml → projekt.sprache`).

## Setup

### Ich habe kein Merkblatt-PDF. Ist das schlimm?
Nein. Du kannst alle Formatierungsvorgaben manuell eingeben.
Claude schlägt sinnvolle Standardwerte vor.

### Kann ich die Konfiguration später ändern?
Ja. Bearbeite `config.yaml` direkt. Änderungen am Zitationsstil sollten
möglichst früh erfolgen, da spätere Änderungen alle Kapitel betreffen.

## Workflow

### Kann ich die Reihenfolge der Phasen ändern?
Nein. Die Phasen bauen aufeinander auf. Du kannst aber innerhalb einer Phase
Kapitel in beliebiger Reihenfolge bearbeiten.

### Was passiert wenn ich die Gliederung ändern will?
Ab Phase 3 ist die Gliederung gesperrt. Falls nötig, kann ein Reset auf
Phase 2 durchgeführt werden -- dabei gehen aber Zuordnungen und Pläne verloren.

### Kann ich ein Kapitel überspringen?
Nein. Kapitel werden in der Reihenfolge der Gliederung geschrieben,
damit der rote Faden gewahrt bleibt.

### Was bedeutet draft und final?
- `draft/`: Entwurf, noch nicht geprüft/freigegeben
- `final/`: Vom User freigegeben, wird für die nächste Phase verwendet

### Wie füge ich Quellen hinzu?
Drei Wege:
1. `/cite` -- Claude führt dich durch (empfohlen)
2. PDFs in `sources/pdfs/` ablegen und `/cite` mit Pfad ausführen
3. `sources/literature.md` manuell bearbeiten

## Qualität

### Wie gut ist der generierte Text?
Der Text folgt wissenschaftlichen Standards (sachlich, belegt, strukturiert).
Er sollte aber IMMER von dir geprüft und ggf. überarbeitet werden.
Die Qualitätsprüfung (Phase 6) hilft dabei, Schwächen zu finden.

### Ersetzt das Framework mein eigenes Denken?
Nein. Du triffst alle inhaltlichen Entscheidungen: Thema, Forschungsfrage,
Argumentation, Bewertung. Claude unterstützt bei Formulierung und Struktur.

## Technisch

### Der DOCX-Build schlägt fehl. Was tun?
1. Prüfen ob python-docx installiert ist: `python3 -c "import docx"`
2. Falls nicht: `pip install python-docx`
3. Falls installiert: Fehlermeldung an Claude zeigen mit `/compile`
4. PDF fehlt? LibreOffice prüfen: `which soffice` (optional, nur für PDF)

### Kann ich die generierte DOCX manuell bearbeiten?
Besser nicht. Die DOCX in `output/phase-07-docx/` wird bei jedem `/compile`
neu gebaut, manuelle Änderungen gehen verloren. Format-Korrekturen gehören
in `config.yaml` bzw. den Builder; für Reviewer-Feedback am finalen DOCX
gibt es `/apply-feedback` (YAML-Patches, überleben den Frozen-Mode).

### Wie gross wird das Repository?
Ca. 1-5 MB ohne PDFs. PDFs in `sources/pdfs/` sind gitignored.

## Seminar- und Hausarbeiten

### Kann ich eine Seminararbeit ohne Quellen schreiben?
Ja. Wähle bei `/setup` den Quellen-Workflow "Keine Quellen". Phase 3 (Zitat-Zuordnung)
wird dann automatisch übersprungen und die Argumentation stützt sich auf Logik und Beispiele.

### Ist die Struktur für kurze Arbeiten anders?
Ja. Für Seminararbeiten gibt es ein eigenes Kapitelmodell (2-3 Hauptkapitel statt 5-6).
Der Outliner-Agent wählt das passende Modell automatisch basierend auf dem Arbeitstyp.

### Brauche ich weniger Quellen?
Die Mindestanforderung wird an den Arbeitstyp angepasst:
- Fallstudie: 8 Quellen (empfohlen 8-15, inkl. IU-Lernskript)
- Seminararbeit: 3 Quellen (empfohlen 5-10)

## Quellen-Import

### Wie importiere ich eine BibTeX-Datei?
```
/cite -> "BibTeX-Import" -> Pfad zur .bib-Datei angeben
```
Claude liest alle Einträge, konvertiert sie und bietet Batch-Import an.

### Wie importiere ich aus Zotero?
1. In Zotero: Rechtsklick auf Sammlung -> "Exportiere Sammlung..."
2. Format wählen: BibTeX (empfohlen), CSV oder RIS
3. `/cite` -> "Zotero-Import" -> Pfad angeben

### Welche Zotero-Exportformate werden unterstützt?
- BibTeX (.bib) -- empfohlen, genauestes Mapping
- CSV -- tabellarisch, einfach
- RIS (.ris) -- Standard-Austauschformat
