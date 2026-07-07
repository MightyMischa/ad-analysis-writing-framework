---
name: humanize
description: Entfernt KI-typische Schreibspuren aus einem Kapitel und macht den Stil natuerlicher, ohne den wissenschaftlichen Charakter, die Fakten oder die Zitate zu veraendern. Nutze diesen Skill wenn der User /humanize eingibt, optional mit Kapitelnummer wie /humanize 2.3 oder /humanize --all.
---

# Humanize (KI-Spuren entfernen)

Ueberarbeitet einen geschriebenen Text so, dass typische Anzeichen KI-generierten Schreibens verschwinden und die Prosa natuerlicher klingt — **innerhalb des wissenschaftlichen Registers**. Reine Stilbearbeitung: Inhalt, Zahlen, Argumente, Reihenfolge und Zitate bleiben unveraendert.

Grundlage ist `.claude/rules/ai-writing-signs.md` (33 Muster, an wiss. Deutsch angepasst). Die **Akademischen Leitplanken** dort haben Vorrang vor jeder Einzelregel.

## Wichtige Grenzen (immer beachten)

- **Keine Ich-Form** ergaenzen, kein Blog-Ton. Natuerlich heisst nicht locker.
- **Zitate (APA) niemals entfernen, verschieben oder abschwaechen.**
- **Keine Fakten/Zahlen aendern.** Wenn eine KI-Floskel nur durch eine inhaltliche Aussage ersetzbar waere, fuer die kein Beleg vorliegt: Floskel ersatzlos streichen, nichts erfinden.
- Kein Hinweis im Text darauf, dass humanisiert wurde.

## Ablauf

### 1. Ziel bestimmen

**Mit Kapitelnummer (z.B. /humanize 2.3):** dieses Kapitel.
**`/humanize --all`:** alle freigegebenen Kapitel nacheinander.
**Ohne Parameter:** das zuletzt geschriebene/gepruefte Kapitel; im Zweifel fragen: „Welches Kapitel soll humanisiert werden? (z.B. 2.3)".

Quelle ist `output/phase-05-writing/final/[X-X].md` (sonst `draft/`).

### 2. DOCX-Frozen-Mode-Warnung

Lies `config.yaml → docx_frozen`. Wenn ein finalisiertes/konformes DOCX existiert UND `warn_on_markdown_edit: true`:
- WARNE: „Ein finalisiertes DOCX existiert bereits. /humanize aendert nur die Markdown-Quelle, NICHT das DOCX. Fuer DOCX-Aenderungen ist `/apply-feedback` der richtige Weg." Frage, ob trotzdem fortgefahren werden soll.

### 3. Kontext laden

- `.claude/rules/ai-writing-signs.md` (Musterkatalog + Leitplanken)
- `.claude/rules/writing-style.md` (Stilregeln)
- `voice-samples/voice-profile.md` (Stilprofil des Autors — falls vorhanden)
- `preferences.md` (verbotene Woerter, projektspezifisch)
- Das Zielkapitel

### 4. Voice-Kalibrierung

Wenn `voice-samples/voice-profile.md` existiert: Satzrhythmus, Konnektor-Vorlieben und Stilentscheidungen daraus uebernehmen, statt generisch „glatt" zu schreiben. Wenn der User im Aufruf eine eigene Schreibprobe mitliefert, hat diese Vorrang fuer die Kalibrierung. Ohne Profil und Probe: am vorhandenen Kapiteltext orientieren (Rhythmus beibehalten).

### 5. Pass 1 — Umschreiben

Gehe den Text Satz fuer Satz durch und entferne die Muster aus dem Regelwerk:
- KI-Vokabular, Kopula-Vermeidung, Synonym-Karussell, Dreierregel-Zwang, Bedeutungs-Aufblaehung, Werbe-/Hochglanzsprache, Autoritaets- und Signpost-Floskeln, Fuellfloskeln, uebermaessiges Hedging, generische Schluesse.
- Gedankenstrich-Haeufung, Fett-/Title-Case-/Emoji-/Fragment-Muster, Inline-Header-Listen.
- Analogien/dekorative Bildsprache, gestapelte rhetorische Fragen, Reveal-Doppelpunkt, dramatischer Pivot (Muster 30–33) — Akademische Nuance beachten: eine einzelne Leitfrage, eine fachuebliche Veranschaulichung, ein Definitions-Doppelpunkt und eine belegte kritische Wuerdigung bleiben erhalten.
- Satzlaengen variieren (vgl. Voice-Profil: jeder dritte Satz kuerzer).

Dabei strikt die Leitplanken halten: Register wissenschaftlich, keine Ich-Form, Zitate und Zahlen unangetastet.

### 6. Pass 2 — „Offensichtlich KI"-Audit + Klausel-Oekonomie

Lies das Ergebnis aus Pass 1 noch einmal mit zwei Fragen.

**(a) KI-Audit:** „Welche Stelle wuerde eine erfahrene Pruefungsperson sofort als KI-Text erkennen?" Markiere die 3–5 verdaechtigsten Stellen und schreibe sie ein zweites Mal um. Dieser Durchgang faengt erfahrungsgemaess die Reste, die Pass 1 uebersieht.

**(b) Klausel-Oekonomie:** Gehe Satz fuer Satz, Klausel fuer Klausel und frage: „Traegt diese Klausel etwas bei, das die Leserin braucht?" Reine Fuellklauseln, leere Verstaerker und nachgeschobene Schein-Analysen (Muster 6, 23, 24) ersatzlos streichen.

**Strikte Grenze fuer (b):** Gestrichen werden NUR inhaltsleere Klauseln. Niemals gestrichen werden belegte Aussagen, Argumente, Zahlen, Definitionen, Fachbegriffe oder Quellenbelege (APA). Im Zweifel behalten. Kein Absatz wird unter seine MEAL-Struktur (Main–Evidence–Analysis–Link) oder unter die Zitationsdichte des Arbeitstyps gekuerzt.

### 7. Speichern

- Sichere die Vorversion: `[X-X].md` → `[X-X].prehum.md` (gleicher Ordner).
- Schreibe das Ergebnis nach `output/phase-05-writing/draft/[X-X].md`.
- Aendere `progress.json` NICHT (Stilpass, keine Phasenaenderung).

### 8. Revisions-Diff (optional, zur Pruefung empfohlen)

Wenn Pass 1 oder Pass 2 Saetze umgeschrieben oder gestrichen haben, erzeuge ein HTML-Artefakt zur Sicht-Pruefung der Aenderungen. Besonders fuer die Integritaets-Pruefung wertvoll: Im Diff laesst sich direkt kontrollieren, dass kein Zitat und keine Zahl veraendert wurde. Bei nur minimalen Aenderungen ueberspringen.

1. Baue eine Aenderungsliste auf Satzebene, gruppiert nach Absatz (`para`-Nummer). Jeder Eintrag hat einen Typ:
   - `keep` — Satz unveraendert. Felder: `type`, `text`.
   - `edit` — Satz umgeschrieben. Felder: `type`, `old`, `new`, `why`.
   - `del` — Satz gestrichen. Felder: `type`, `old`, `why`.

   `why` ist ein kurzer Grund auf Deutsch (z. B. „Fuellfloskel", „Muster 30: Analogie", „Dreierregel"). Form:

   ```json
   [
     { "para": 1, "items": [
       { "type": "edit", "old": "…", "new": "…", "why": "…" },
       { "type": "del",  "old": "…", "why": "…" }
     ]},
     { "para": 2, "items": [ { "type": "keep", "text": "…" } ] }
   ]
   ```

2. Nimm `.claude/skills/humanize/assets/revision_template.html`, ersetze die Zeile `const DATA = __DATA__;` exakt durch `const DATA = <json>;` und speichere als `output/phase-05-writing/draft/[X-X].humdiff.html`. Pruefe, dass kein `__DATA__` mehr im File steht.
3. Drei Tabs: „Erster Entwurf", „Bereinigt", „Diff". Im Diff ist Gestrichenes rot, Umgeschriebenes gruen; der Grund erscheint beim Ueberfahren mit der Maus.
4. Nenne dem User den Pfad im Bericht.

Das Diff ist nur Pruefhilfe; massgeblich bleibt die Markdown-Datei aus Schritt 7. Die Aenderungsliste muss die echten Aenderungen exakt abbilden (kein nachtraegliches „Schoenen").

### 9. Bericht

```
=== Humanize: Kapitel [X.X] ===
Muster entfernt: [Liste der Kategorien, z.B. KI-Vokabular, Dreierregel, Fuellfloskeln]
Woerter: [neu] (vorher: [alt])
Zitate unveraendert: [Anzahl Belege vorher = nachher]  ✓
Vorversion gesichert: output/phase-05-writing/[draft|final]/[X-X].prehum.md
Revisions-Diff: output/phase-05-writing/draft/[X-X].humdiff.html  (falls erzeugt — zur Sicht-Pruefung oeffnen)

Pruefe das Ergebnis. Mit /approve freigeben oder die Vorversion wiederherstellen.
```

### 10. Integritaets-Hinweis (einmalig, beim ersten Aufruf eines Projekts)

Weise den User einmal freundlich darauf hin:
„`/humanize` verbessert nur den Stil. Der Inhalt muss dein eigenes Denken widerspiegeln — KI-Nutzung ist an der IU zulaessig, solange wissenschaftliche Standards eingehalten werden. Dieser Skill ist kein Werkzeug zur Verschleierung von Autorschaft."

### 11. Humanize-Tracking markieren

Nach dem Stilpass den humanisierten Stand markieren, damit `/preflight` spaeter
warnt, falls das Kapitel danach noch veraendert wird:

```bash
python3 scripts/review_tracking.py mark output/phase-05-writing/final/kapitel-[N].md humanize
```

Im Batch-Modus fuer jedes humanisierte Kapitel ausfuehren. (Wird das Kapitel im
draft humanisiert, denselben Befehl mit dem draft-Pfad aufrufen — der Schluessel
ist der Dateiname, der beim /approve-Verschieben nach final gleich bleibt.)

## Batch-Modus (`/humanize --all`)

Fuer jedes freigegebene, noch nicht humanisierte Kapitel Schritt 3–9 ausfuehren. Abschluss mit einer Tabelle (Kapitel, entfernte Muster-Kategorien, Wortzahl vorher/nachher, Zitate konstant ja/nein).

## Verhaeltnis zu /review

`/review` enthaelt den Agenten `reviewer-ai-style`, der dieselben Muster nur **meldet**. `/humanize` ist der aktive Gegenpart, der sie **umschreibt**. Im Normalfluss: erst `/review` (inkl. KI-Stil-Befund), dann `/humanize` fuer die Umsetzung, dann `/approve`.
