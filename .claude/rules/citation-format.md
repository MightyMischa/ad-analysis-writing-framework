---
globs: ["sources/**"]
---

# Regeln für Quellendateien

## literature.md Format
- YAML-Blöcke mit --- Trennern
- Zweistufig: PART 1 (Stammdaten) und PART 2 (Zitate)
- quelle_id: immer nachname_jahr (lowercase, underscore)
- Bei Namenskollision: Suffix a, b, c

## Pflichtfelder Quelle
- quelle_id, autor, jahr, titel, quelle_typ

## Pflichtfelder Zitat
- id, quelle_id, seite (empfohlen), typ, inhalt

## Autorenformat
- Einzeln: "Nachname, V."
- Mehrere: "Nachname1/Nachname2" (Slash-getrennt)
- Bei 3+: Alle auflisten (Slash-getrennt)

## Quellentypen
- buch, journal, sammelband, konferenz, website, report, working_paper

## Zitat-Typen
- indirekt: Paraphrase (sinngemäß)
- direkt: Wörtliches Zitat (in Anführungszeichen)

## Validierung
- Jede quelle_id in PART 2 muss in PART 1 existieren
- Keine verwaisten Zitate (ohne gültige quelle_id)
- Seitenzahlen müssen zur Quelle passen

## APA-Konformität (IU-Standard ab 01.10.2025)

Begründung jedes Punktes steht in `LESSONS.md` (Abschnitt „Quellen-Lessons").

### Working Papers vollständig zitieren
- **Pflichtfelder:** Reihen-Name, Nummer, URL oder DOI.
- **Beispiel:** „Auer, R. A., Cornelli, G., & Frost, J. (2020). Rise of the Central Bank Digital Currencies. CESifo Working Paper No. 8655. https://www.cesifo.org/..."
- **YAML:** `quelle_typ: working_paper` mit eigenen Feldern `reihe:` und `nummer:`
  (statt die Reihe ins `verlag`-Feld zu schmuggeln). `build_docx.py` rendert dann
  „<Titel>. <Reihe> <Nummer>. <URL>"; ohne URL greift `doi` als Fallback. `report`
  unterstützt dieselben Felder. Beispiel-YAML:
  ```yaml
  quelle_typ: working_paper
  reihe: "CESifo Working Paper"
  nummer: "No. 8655"
  url: "https://www.cesifo.org/..."
  ```

### Suffix-Konsistenz: kein _b ohne _a
- Wenn nur EINE Quelle eines Autors/Jahres existiert → kein Suffix.
- Bei zwei oder mehr → durchgängig `_a`, `_b`, `_c` im Text UND Lit-Verz.
- **Antipattern:** `(EZB, 2023b)` im Text, aber kein `(EZB, 2023a)` zitiert.

### Institutionelle Erstnennung mit Klammer-Abkürzung
- Erste Nennung: „Bundesministerium der Finanzen [BMF] (2023)" oder „(Bundesministerium der Finanzen [BMF], 2023)".
- Spätere Nennungen: nur „BMF, 2023".
- Auch für: Europäische Zentralbank [EZB], Bank for International Settlements [BIS], Internationaler Währungsfonds [IWF].

### Undatierte Webseiten: n. d.
- Atlantic Council CBDC Tracker, Sand-Dollar-Übersicht, EZB-Projekt-Übersichtsseiten haben kein festes Veröffentlichungsdatum.
- Format: `Atlantic Council. (n. d.). Central Bank Digital Currency Tracker. Abgerufen am DD.MM.YYYY, von https://...`
- Im YAML: `jahr: "n. d."` (in Anführungszeichen).

### Journal-Artikel mit DOI
- Format: `Autor (Jahr). Titel. Zeitschrift, Band(Heft), Seiten. https://doi.org/<DOI>`
- DOI als URL anhängen, nicht als „doi:..." schreiben.

### Online-Quellen mit Abrufdatum
- Tracker und Projektseiten ändern Inhalte → Abrufdatum für Reproduzierbarkeit.
- Im YAML: `abruf: "DD.MM.YYYY"`.
- Im Lit-Verz: „Abgerufen am DD.MM.YYYY, von URL".

## Quellen-Aktualität

Vor jeder Abgabe Tracker und Projektseiten frisch prüfen, weil Zahlen sich ändern:

- Atlantic Council CBDC Tracker (Stand 2026: 137 Länder, 98 % BIP)
- Sand-Dollar-Statistiken
- eNaira-Adoption
- EZB-Projektphase

Aktuelle Anker stehen in `preferences.md` (Abschnitt „Aktualitäts-Anker").
