---
name: review
description: Startet die Qualitätsprüfung für ein Kapitel. Nutze diesen Skill wenn der User /review eingibt, optional mit Kapitelnummer wie /review 2.3.
---

# Qualitätsprüfung

Prüft ein geschriebenes Kapitel durch vier spezialisierte Reviewer-Agenten.

## Ablauf

### 1. Kapitelnummer bestimmen

**Mit Parameter (z.B. /review 2.3):**
- Verwende die angegebene Kapitelnummer

**Ohne Parameter (/review):**
- Finde das nächste Kapitel das geschrieben aber noch nicht reviewed ist
- Falls kein Kapitel gefunden: "Alle Kapitel sind bereits geprüft."

### 2. Vorbedingungen prüfen

- [ ] Kapitel existiert in `output/phase-05-writing/final/[X-X].md`
  (oder in draft/ falls der User explizit draft prüfen will)
- [ ] config.yaml existiert

Falls das Kapitel noch nicht geschrieben ist:
"Kapitel [X.X] ist noch nicht geschrieben. Nutze /write [X.X] zuerst."

### 3.0 Deterministischer Vor-Pass (Stil-Linter)

Vor dem Start der Agenten:

```bash
python3 scripts/lint_style.py output/phase-05-writing/[final|draft]/[X-X].md --json
```

Das JSON ist Ground-Truth für die mechanischen Funde und wird den Agenten
`reviewer-language` und `reviewer-ai-style` mitgegeben, mit der Anweisung:
**„Nicht erneut suchen, was der Linter bereits fand (L1–L13) — konzentriere dich
auf die nicht-deterministischen Muster"** (Bedeutungs-Aufblähung, Synonym-Karussell,
Analogien, Pivot, inhaltliche Passung). Das spart Redundanz und lenkt die
LLM-Aufmerksamkeit auf das, was nur ein LLM erkennen kann.

### 3. Vier Reviewer PARALLEL starten

Erkläre dem User:
"Ich prüfe Kapitel [X.X] mit vier spezialisierten Agenten parallel:
1. Sprachprüfung (Stil, verbotene Wörter, Wiederholungen)
2. Zitationsprüfung (Format, Dichte, Vollständigkeit)
3. Argumentationsprüfung (Logik, Roter Faden, Übergänge)
4. KI-Stil-Prüfung (Anzeichen KI-generierten Schreibens, Natürlichkeit)
Das dauert einen Moment..."

**WICHTIG: Starte alle vier Agents gleichzeitig (parallel), nicht nacheinander.**
Die vier Reviews sind unabhängig voneinander und können parallel laufen:

- Starte `.claude/agents/reviewer-language.md`
- Starte `.claude/agents/reviewer-citations.md`
- Starte `.claude/agents/reviewer-argumentation.md`
- Starte `.claude/agents/reviewer-ai-style.md`

### 4. Ergebnisse konsolidieren

Sobald alle vier fertig sind, fasse die Berichte zusammen:

```
=== Review-Ergebnis: Kapitel [X.X] ===

| Prüfbereich | Funde | Schwere |
|-------------|-------|---------|
| Sprache & Stil | [X] | [hoch/mittel/niedrig] |
| Zitationen | [X] | [hoch/mittel/niedrig] |
| Argumentation | [X] | [hoch/mittel/niedrig] |
| KI-Stil & Natürlichkeit | [X] | [hoch/mittel/niedrig] |

Gesamtempfehlung: [Freigabe / Kleine Überarbeitung / Größere Revision]
```

Falls Korrekturen nötig:
- Zeige die wichtigsten Funde (max. 10)
- Biete an: "Soll ich die Korrekturen automatisch umsetzen?"

### 5. Korrekturen umsetzen (falls gewünscht)

Wenn der User zustimmt:
- Behebe zuerst die blockierenden Linter-Funde (L1–L4) aus Schritt 3.0
- Setze sprachliche Korrekturen um
- Setze eindeutige KI-Stil-Korrekturen um (für umfangreiche Umschreibungen: `/humanize [X.X]`)
- Setze Zitationskorrekturen um
- Melde Argumentations-Probleme die manuelle Entscheidung brauchen
- Danach Linter erneut ausführen: blockierende Funde müssen 0 sein

### 6. Speichern

Speichere den Review-Bericht in: `output/phase-06-review/draft/[X-X]-reviewed.md`
Falls Korrekturen umgesetzt: Aktualisiere das Kapitel in `output/phase-05-writing/draft/`

### 7. Auto-Codex-Review (wenn aktiv)

Lies `config.yaml → codex.auto_review`.

Wenn `true`:
- Rufe `codex-review chapter [X.X] --quiet` auf — Codex (gpt-5.5, xhigh) liefert eine 5. unabhängige Review-Sicht zusätzlich zu den vier internen Agenten.
- Codex erkennt typischerweise andere Klassen von Fehlern als die vier spezialisierten Agenten (z. B. Format-Pitfalls, APA-Suffix-Inkonsistenzen, Aktualität von Fakten).

Wenn `false`: Skip.

### 8. Empfehlung

- "Prüfe die Änderungen und nutze /approve um das Review freizugeben."
- Falls Codex zusätzliche Funde meldet: zuerst diese adressieren.

### 9. Review-Tracking markieren

Nach Abschluss des Reviews den geprüften Stand des Kapitels markieren, damit
`/preflight` später erkennt, ob danach noch Text ergänzt wurde (sonst läuft
nachträglicher Text ungeprüft durch):

```bash
python3 scripts/review_tracking.py mark output/phase-05-writing/final/kapitel-[N].md review
```

Im Batch-Modus (`/review --all`) für jedes geprüfte Kapitel ausführen.

## Batch-Modus (`/review --all`)

Prüft ALLE geschriebenen, noch ungeprüften Kapitel nacheinander:

1. Ermittle aus `thesis-structure.yaml` alle Kapitel, die in `phase-05-writing/final/`
   vorliegen, aber noch kein Review in `phase-06-review/final/[X-X]-reviewed.md` haben.
2. Führe für jedes dieser Kapitel den 4-Agenten-Review (Schritt 3–6) aus.
3. Mechanische Korrekturen (Sprache, Zitationsformat) werden direkt umgesetzt;
   Argumentations-Funde, die menschliche Entscheidung brauchen, werden gesammelt gemeldet.
4. **Gesamtwerk-Pass:** Nach den Einzel-Reviews den Agenten
   `.claude/agents/reviewer-gesamtwerk.md` starten. Vorher den Digest erzeugen:
   ```bash
   python3 scripts/lint_style.py --all --digest --json
   ```
   Der Agent liest alle final-Kapitel am Stück + Voice-Profil + Digest und prüft
   NUR werkübergreifend: Register-/Rhythmus-Drift zwischen Kapiteln,
   Konnektor-Übernutzung, wiederholte Kapitel-Eröffnungsmuster,
   Triaden-/Selbstreferenz-Budget. Sein Drift-Bericht wird in
   `output/phase-06-review/draft/gesamtwerk-reviewed.md` gespeichert.
5. Abschluss-Tabelle über alle Kapitel mit Schwere-Einstufung + Gesamtwerk-Befund;
   Empfehlung `/humanize [X.X]` je betroffenem Kapitel.

## Auto-Modus (vom `/auto`-Orchestrator genutzt)

Wenn aus `/auto` aufgerufen (oder mit `--auto`):
- Mechanische Korrekturen (Sprach-Pitfalls, APA-Format, Wortwiederholungen,
  verbotene Wörter) werden OHNE Rückfrage angewendet und in `output/auto-run.log` protokolliert.
- Nur **inhaltlich-strukturelle** Funde hoher Schwere (z. B. fehlender roter Faden,
  unbelegte Kernbehauptung) werden als Blocker gesammelt und am Ende des Laufs gemeldet.
- Kein interaktives "Soll ich umsetzen?" — der Lauf bleibt unbeaufsichtigt.
