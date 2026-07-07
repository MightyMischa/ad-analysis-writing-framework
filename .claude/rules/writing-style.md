---
globs: ["output/**/*.md"]
---

# Regeln für generierte Texte

## Wissenschaftliche Sprache
- Keine Ich-Form ("Ich denke..." -> "Es lässt sich argumentieren...")
- Sachlich-neutral formulieren
- Keine Umgangssprache
- Keine journalistischen Übertreibungen ("revolutionär", "bahnbrechend")
- Keine Absolutismen ohne Beleg ("immer", "nie", "alle")

## Zitationen

**Zitationsdichte nach Arbeitstyp** (config.projekt.typ):
- dissertation: 8-12 Zitationen pro Seite
- master: 6-10 Zitationen pro Seite
- bachelor: 5-10 Zitationen pro Seite
- hausarbeit: 3-6 Zitationen pro Seite
- seminararbeit: 3-5 Zitationen pro Seite
- Bei `quellen.workflow: "keine"`: 0 Zitationen (Argumentation durch Logik und Beispiele)

**Allgemeine Regeln** (nur wenn quellen.workflow NICHT "keine"):
- Jede faktische Behauptung mit Quelle belegen
- Zitate NUR aus sources/literature.md verwenden
- Zitationsformat aus dem konfigurierten Stil laden (config.yaml)
- Ca. 80% indirekte, 20% direkte Zitate

## Absatzstruktur (MEAL)
- Main Point: Kernaussage als erster Satz
- Evidence: Beleg durch Quelle
- Analysis: Eigene Einordnung
- Link: Verbindung zum nächsten Gedanken
- 80-150 Wörter pro Absatz

## Übergänge
- KEIN letzter Satz der das nächste Kapitel ankündigt
- KEIN erster Satz der das vorherige Kapitel zusammenfasst
- KEINE expliziten Kapitelverweise ("Wie in Kapitel X dargelegt...")
- Verbindung durch Konzeptnamen, nicht durch Verweise

## Vermeiden
- Gleiche Wörter in benachbarten Sätzen
- Gedankenstriche (Kommas bevorzugen)
- Eingeschobene Nebensätze die den Lesefluss stören
- Schwache Verben ("Es gibt...", "Man kann sagen...")
- Übertriebene Nominalisierungen

## Beachten
- Fachbegriffe beim ersten Auftreten definieren
- Zahlen in Sätze integrieren (nicht in Klammern)
- Wörter aus preferences.md vermeiden
- Ein Gedanke pro Satz; bei zwei eigenständigen Aussagen in zwei Sätze teilen
- Distinkte Aspekte je eigener Satz statt überladener Sammelsätze (Klarheit vor Kürze; Details: grundprinzipien „Klarheit und Satzbau")

## Sprach-Pitfalls aus Reviewer-Feedback

Diese Fehler wurden in echten Prüfberichten konkret angemerkt. Vor jedem
`/approve` und vor `/compile` automatisch gegen den Volltext prüfen.

### Genus und Genitiv

| Falsch | Richtig | Begründung |
|---|---|---|
| anhand drei typischer Anwendungsfälle | anhand dreier typischer Anwendungsfälle | Genitiv-Plural „dreier" |
| der Single Euro Payments Area | die Single Euro Payments Area | Area = die Area, daher SEPA = die SEPA |
| der SEPA | die SEPA bzw. der SEPA-Raum | gleicher Grund |
| so ein Szenario | ein solches Szenario | „so ein" ist umgangssprachlich |

### Englische Fachterminologie

| Falsch | Richtig |
|---|---|
| Counter-Financing of Terrorism | Countering the Financing of Terrorism |
| AML/CFT als Counter-Financing | AML/CFT als Countering the Financing |

### APA-Erstnennung institutioneller Autoren

Beim ersten Auftreten im Text MUSS die Vollform mit Klammer-Abkürzung stehen:

- „Bundesministerium der Finanzen [BMF] (2023)" oder „(Bundesministerium der Finanzen [BMF], 2023)"
- „Europäische Zentralbank [EZB] (2020)" beim ersten Auftreten
- „Bank for International Settlements [BIS] (2023)"

Spätere Nennungen nur die Abkürzung.

### Pflicht-Check vor /approve und /compile

Folgende Strings dürfen NICHT im Volltext stehen (außer in wörtlichen Zitaten):

```
"anhand drei typischer"
"anhand drei "
"der Single Euro Payments Area"
"so ein Szenario"
"Counter-Financing"
```

Vollständige Sammlung mit Begründungen steht in `LESSONS.md`
(Abschnitt „Sprache-Lessons").
