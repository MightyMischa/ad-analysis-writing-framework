# Schreibpräferenzen

> Persönliche Präferenzen für den wissenschaftlichen Schreibstil.
> Diese Datei wird von allen Schreib- und Review-Agenten geladen UND von
> `scripts/lint_style.py` maschinell ausgewertet (Sektionen „Verbotene Wörter",
> „Verbotene Floskeln (Stil-Linter)" und „Sprach-Pitfalls (Projekt)").
>
> Autoritativ für Rhythmus und Stimme ist das Voice-Profil
> (`config.yaml → stil.voice_profile`). Diese Datei ergänzt es projektspezifisch.

## Verbotene Wörter

Folgende Wörter sollen NICHT verwendet werden (Linter-Check L1, blockierend;
exakte Wortgrenze, Groß-/Kleinschreibung egal — Flexionsformen ggf. einzeln listen):

- natürlich
- selbstverständlich
- bekanntlich
- logischerweise
- inhärent
- ganzheitlich
- zukunftsweisend
- bahnbrechend
- revolutionär
- beleuchten
- beleuchtet

## Verbotene Floskeln (Stil-Linter)

Wörtliche Mehrwort-Strings, die nicht im Fließtext stehen dürfen (Linter-Check L2,
blockierend; Treffer in direkten Zitaten werden ignoriert). Die Liste ergänzt die
eingebaute Default-Liste des Linters (Voice-Profil §5 + Anti-KI-Katalog):

- es ist wichtig zu
- es sei angemerkt
- in der heutigen
- im Folgenden wird
- im folgenden Kapitel
- das nächste Kapitel beschäftigt sich
- zusammenfassend lässt sich festhalten
- vor diesem Hintergrund zeigt sich
- es wird deutlich, dass
- dies führt zu der Erkenntnis
- von besonderer Bedeutung
- im Kern geht es
- aufgrund der Tatsache, dass
- spielt eine entscheidende Rolle
- tauchen wir ein

Hinweis: „zusammenfassend lässt sich festhalten" ist 1× im echten Fazit-Kapitel
erlaubt (der Linter kennt diese Ausnahme).

## Sprach-Pitfalls (Projekt)

Projektspezifische Fehler-Strings aus echtem Reviewer-Feedback (Linter-Check L4,
blockierend). Bei Projektstart leer; nach jedem Prüfbericht erweitern.
Format: ein wörtlicher String pro Bullet.

Beispiele aus früheren Projekten (im Code-Block, damit der Linter sie NICHT lädt):

```
- anhand drei typischer
- der Single Euro Payments Area
- so ein Szenario
- Counter-Financing
- 114 Staaten            # veraltete Zahl, aktueller Stand siehe Aktualitäts-Anker
```

<!-- Ab hier echte Einträge als Bullets: -->

## Bevorzugte Formulierungen

Wenn möglich, verwende diese Alternativen (präzise statt aufgebläht):

- "benutzen" -> "verwenden" / "einsetzen"
- "machen" -> "durchführen" / "umsetzen"
- "Es gibt viele X, die..." -> "Zahlreiche X ..." (starkes Verb)

Nicht mehr empfohlen (blähen das Register auf, KI-Tell — Muster 7):
~~"wichtig" -> "von zentraler Bedeutung"~~, ~~"zeigt" -> "verdeutlicht"~~.
Einfache, präzise Verben ("ist", "hat", "zeigt") sind erwünscht.

## Voice-Essentials (Kurzfassung des Voice-Profils)

Autoritativ ist das vollständige Profil; diese Kurzfassung dient als Erinnerung:

- **Satzrhythmus:** bewusste Varianz — kurze Sätze (≤ 12 Wörter) nach langen,
  nie drei gleich lange Sätze in Folge. Details: `base/guides/academic-writing/satzrhythmus.md`
- **Konnektoren bevorzugt:** zudem, ferner, des Weiteren (additiv);
  folglich, somit, daher, demnach (schlussfolgernd)
- **Konnektoren meiden:** dabei, hierbei, wobei, darüber hinaus (als Dauer-Füller)
- **Passiv-Quote:** 35-45 % (wissenschaftliches Passiv ist erwünscht, nicht totales Passiv)
- **Eigenheiten-Budget:** "immer mehr" max. 1× pro Absatz, "heutzutage" max. 1× pro Werk,
  Komma-Triaden ("X, Y und Z") max. 3-4× pro Werk
- **Selbstreferenz-Budget:** "Die vorliegende Arbeit" / "Diese Fallstudie" max. 2× im Werk

## Stil-Hinweise

- Satzlängen variieren statt pauschal kürzen — Details und Zielwerte in
  `base/guides/academic-writing/satzrhythmus.md` (lange Sätze sind erlaubt,
  uniforme Kürze ist selbst ein KI-Tell)
- Fachbegriffe bei Erstnennung immer definieren
- Keine verschachtelten Relativsätze
- Fachbegriffe konsistent wiederholen statt Synonym-Karussell

## Aktualitäts-Anker

Zahlen und Fakten, die vor Abgabe frisch geprüft werden müssen (Validator A2).
Format: ein Anker pro Bullet, bei Projektstart leer.

<!-- - Beispiel: Atlantic Council CBDC Tracker (Stand 2026: 137 Länder) -->

## Reviewer-Lessons

Pitfalls, die in echten Prüfberichten auftauchen, sammelt das Repo in `LESSONS.md`.
Vor jeder Abgabe:

- `python3 scripts/lint_style.py --all` — Stil-Linter (verbotene Wörter, Floskeln, Rhythmus)
- Format-Checks via `python3 scripts/validate_docx.py <datei>.docx`
- APA-Erstnennung institutioneller Autoren mit Klammer-Abkürzung prüfen
- Bei aktivierter `codex.auto_review` läuft `/codex-review` automatisch nach jedem Schritt

LESSONS.md sollte nach jedem externen Reviewer-Durchlauf erweitert werden;
neue wörtliche Fehler-Strings zusätzlich oben in „Sprach-Pitfalls (Projekt)" eintragen.
