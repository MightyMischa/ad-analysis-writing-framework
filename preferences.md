# Schreibpräferenzen

> Persönliche Präferenzen für den wissenschaftlichen Schreibstil.
> Diese Datei wird von allen Schreib- und Review-Agenten geladen.
> Bearbeite sie manuell oder nutze `/setup` um sie einzurichten.
>
> Lösche die Beispiele und trage deine eigenen Präferenzen ein.

## Verbotene Wörter

Folgende Wörter/Formulierungen sollen NICHT verwendet werden:

- natürlich
- selbstverständlich
- bekanntlich
- logischerweise
- inhärent

## Bevorzugte Formulierungen

Wenn möglich, verwende diese Alternativen:

- "wichtig" -> "von zentraler Bedeutung"
- "zeigt" -> "verdeutlicht" / "veranschaulicht"
- "benutzen" -> "verwenden" / "einsetzen"
- "machen" -> "durchführen" / "umsetzen"

## Stil-Hinweise

Weitere Hinweise zum gewünschten Schreibstil:

- Kurze, prägnante Sätze bevorzugen (max. 25 Wörter)
- Fachbegriffe bei Erstnennung immer definieren
- Keine verschachtelten Relativsätze

## Reviewer-Lessons

Pitfalls, die in echten Prüfberichten auftauchen, sammelt das Repo in `LESSONS.md`.
Vor jeder Abgabe:

- Sprach-Pitfalls (`dreier`, `die SEPA`, `ein solches`, `Countering the Financing`) prüfen.
- APA-Erstnennung institutioneller Autoren mit Klammer-Abkürzung.
- Format-Checks via `python3 scripts/validate_docx.py <datei>.docx`.
- Bei aktivierter `codex.auto_review` läuft `/codex-review` automatisch nach jedem Schritt.

LESSONS.md sollte nach jedem externen Reviewer-Durchlauf erweitert werden.
