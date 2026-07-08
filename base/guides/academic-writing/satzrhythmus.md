# Satzrhythmus und Varianz (Burstiness)

Menschliches Schreiben schwankt: kurze Sätze neben langen, dichte Absätze neben
knappen. KI-Text konvergiert auf gleichförmige Mittellagen — alle Sätze 15-20
Wörter, alle Absätze 4-5 Sätze. Diese Gleichförmigkeit ist der am besten
messbare Unterschied zwischen menschlichem und generiertem Text. Dieser Guide
definiert die Zielwerte; `scripts/lint_style.py` misst dieselben Werte (L8, L9,
L13). Guide und Linter dürfen nie divergieren — Änderungen immer in beiden.

> **Autorität:** Das Voice-Profil (`config.yaml → stil.voice_profile`) geht vor.
> Dessen Faustregel „jeder dritte Satz kürzer" ist als **Tendenz** zu lesen,
> nicht als Takt — ein exaktes 3er-Muster wäre selbst eine detektierbare
> Regularität. Die Verteilungs-Zielwerte unten setzen dieselbe Absicht
> mechanik-frei um.

## Zielwerte Satzlängen (= Linter-Schwellen L8)

- **Variationskoeffizient (CV) der Satzlängen ≥ 0,35** pro Kapitel
  (CV = Standardabweichung / Mittelwert; darunter warnt der Linter)
- **Verteilung pro ~10 Sätze:** 2-3 kurze (≤ 12 Wörter), 4-5 mittlere (13-22),
  2-3 lange (23-32). Sätze über 32 Wörter teilen (ein Gedanke pro Satz).
- **Kurzsatz-Anteil ≥ 10 %** — der kurze Satz ist das wichtigste Rhythmus-Werkzeug.
- **Nie 3 Sätze in Folge mit annähernd gleicher Länge** (± 3 Wörter).
- **Nach 2 langen Sätzen (> 20 Wörter) bewusst brechen** — der nächste Satz kurz.

Der kurze Satz trägt dabei eine Funktion: Anker, Zuspitzung, Voraussetzung,
Konsequenz. Kein Deko-Fragment.

## Zielwerte Absätze (= Linter-Schwellen L9, L13)

- **Folge-Absätze unterscheiden sich in der Länge um ≥ 20 %** (Wortzahl).
- **Wortzahl-CV über die Absätze eines Kapitels ≥ 0,25.**
- **Keine identische Satzzahl in 3 Folge-Absätzen** (der „MEAL-Takt" 4-4-4 ist
  ein Struktur-Tell).
- **Höchstens 1 von 3 Absätzen beginnt mit einem Konnektor** (zudem, daher,
  jedoch, ...). Absätze dürfen mit dem Subjekt, einer Zahl, einem Fachbegriff
  oder einer Bedingung beginnen.

## Positiv-Exemplare (aus echten, benoteten IU-Arbeiten)

> **Nur Rhythmus und Struktur übernehmen — keine Formulierungen oder
> Fachinhalte kopieren.** Die Exemplare stammen aus anderen Themen; wörtliche
> Übernahmen färben die neue Arbeit thematisch ein.

### Exemplar 1 — Definition mit kurzem Anker-Satz (Methodik-Kapitel, ML-Fallstudie)

> Unter unüberwachtem Lernen werden jene Verfahren des maschinellen Lernens
> verstanden, die Strukturen in Daten ohne vorgegebene Zielvariable erkennen
> (Hastie et al., 2009). Da die Mitarbeiterbefragung keine vorab definierte
> Klassifikation der Teilnehmenden enthält, eignet sich dieser Zugang zur
> Gruppierung der Antworten. **Voraussetzung ist eine geeignete Aufbereitung
> der Merkmale.** Feature Engineering umfasst die Erzeugung, Transformation und
> Auswahl von Merkmalen und beeinflusst die Qualität der Ergebnisse maßgeblich
> (Kuhn & Johnson, 2019).

Satzlängen: **21 → 19 → 7 → 18**. Der 7-Wörter-Satz bricht die Kette langer
Sätze und trägt zugleich die Überleitung zum nächsten Konzept. Definition per
klassischer Vollform („Unter X versteht man"), Beleg an der Behauptung, kein
Signposting.

### Exemplar 2 — Einleitung mit Zahl als Einstieg (Hausarbeit Finanzwesen)

> Weltweit verfügen rund 1,4 Milliarden Erwachsene über kein Konto bei einer
> Bank oder einem mobilen Anbieter (Demirgüç-Kunt et al., 2022). Diese Lücke
> schließt große Teile der Bevölkerung von formellen Finanzdienstleistungen aus
> und beschränkt ihre wirtschaftlichen Handlungsmöglichkeiten. Mobile
> Finanztechnologien gelten als Hebel, um diese Versorgungslücke zu verringern,
> weil sie den Zugang über das Mobiltelefon und ohne klassisches Bankkonto
> eröffnen. **Ihre Bedeutung reicht über den Finanzsektor hinaus.**

Satzlängen: **16 → 16 → 22 → 7**. Einstieg mit konkreter, belegter Zahl statt
„In der heutigen digitalisierten Welt". Der kurze Schlusssatz öffnet das
nächste Argument, ohne es anzukündigen.

### Exemplar 3 — Kurzer Absatzauftakt (gleiche Hausarbeit)

> **Daraus ergibt sich eine doppelte Relevanz.** In wissenschaftlicher Hinsicht
> verbindet das Thema die Forschung zur finanziellen Inklusion mit der
> Nachhaltigkeitsdebatte. Aus wirtschaftlicher Sicht stehen Märkte mit
> erheblichem Wachstumspotenzial und realem Versorgungsbedarf im Blick.

Ein 6-Wörter-Satz als Absatzauftakt setzt die Kernaussage, die folgenden Sätze
entfalten sie. Parallelität („In wissenschaftlicher Hinsicht … Aus
wirtschaftlicher Sicht") ist hier gewollt und endet nach zwei Gliedern — keine
erzwungene Dreierreihe.

### Kontrastpaar aus dem Voice-Profil (§ 6)

**Gut** (menschlicher Rhythmus, konkret):

> Ein mittelständisches Unternehmen wird heutzutage immer mehr mit steigenden
> Anforderungen an IT-Skalierbarkeit, Datensicherheit und internationaler
> Zusammenarbeit konfrontiert. Dabei wird die Migration von veralteten
> On-Premise-Strukturen hin zu cloud-basierten Lösungen immer stärker notwendig,
> um weiterhin wettbewerbsfähig und innovativ zu bleiben. Diese Fallstudie
> untersucht Ausgangssituation, Entscheidungsprozesse und Umsetzungsschritte.

**Zu vermeiden** (7 KI-Tells in 3 Sätzen):

> In der heutigen, zunehmend digitalisierten Geschäftswelt spielt die
> Cloud-Migration eine entscheidende Rolle. Dabei ist es wichtig zu beachten,
> dass sowohl technische als auch organisatorische Aspekte berücksichtigt
> werden müssen. Im Folgenden wird die Thematik ganzheitlich beleuchtet.

## Anti-Beispiel — uniforme Gleichförmigkeit (synthetisch)

> Die Digitalisierung verändert die Geschäftsmodelle vieler Unternehmen
> nachhaltig und umfassend. Die neuen Technologien ermöglichen dabei effizientere
> Prozesse in nahezu allen Bereichen. Die Unternehmen müssen ihre Strategien
> deshalb an die veränderten Bedingungen anpassen. Die Mitarbeitenden benötigen
> dafür neue Kompetenzen im Umgang mit digitalen Werkzeugen.

Satzlängen: **11 → 11 → 12 → 12** (CV ≈ 0,05). Dazu: jeder Satz beginnt mit
Artikel + Substantiv, jeder Satz gleiche Struktur (Subjekt-Verb-Objekt-Adverb).
Inhaltlich sagt der Absatz viermal dasselbe. So liest sich Text, den der
Linter mit L8/L13 flaggt — auch wenn kein einziges verbotenes Wort vorkommt.

## Arbeitsweise beim Schreiben

1. Absatz inhaltlich schreiben (Argument, Beleg, Einordnung).
2. Rhythmus lesen: Wo stehen drei mittellange Sätze in Folge? Einen davon
   zum Anker-Satz kürzen oder zwei verschmelzen.
3. Satzanfänge prüfen: beginnen mehrere Sätze oder Absätze gleich
   (Konnektor, „Die/Der/Das" + Substantiv)? Variieren.
4. Nicht auf die Metrik schreiben: Die Zielwerte beschreiben, wie natürlicher
   Text aussieht — sie sind Diagnose, nicht Bauanleitung. Wer Satz für Satz
   zählt, produziert neue Mechanik. Im Zweifel: laut lesen.
