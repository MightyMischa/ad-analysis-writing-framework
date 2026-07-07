---
name: apply-feedback
description: Nimmt Reviewer-Feedback (Freitext oder strukturiert) und wendet es als deklaratives YAML-Patch (scripts/docx_patch.py) auf das finale DOCX an. Bewahrt Format-Fixes, die nur im DOCX existieren. Aufruf via /apply-feedback.
---

# Reviewer-Feedback ins DOCX einarbeiten

Formalisiert das Muster, das bei Fallstudie 1 (Digitaler Euro) ad-hoc per `apply_reviewer_feedback.py` gelöst wurde. Zentral, wenn das DOCX die Source-of-Truth ist (Frozen-Mode aktiv).

Seit v3.1 laufen Standard-Patches deklarativ über `scripts/docx_patch.py`
(YAML-Patch, Multi-Run-fähig, Dry-Run) statt über generierte Einweg-Skripte.
Die Skript-Generierung (`base/templates/feedback-patch.py.template`) bleibt
Fallback für Operationen, die das Patch-YAML nicht abdeckt (z. B. Formatierungs-
oder Tabellen-Umbauten).

## Wann aufrufen

- Nach jedem externen Reviewer-Durchlauf, der konkrete Änderungswünsche enthält
- Wenn Markdown-Quellen vom DOCX divergieren (Frozen-Mode) und nur das DOCX gepatcht werden soll
- Vor finaler Abgabe, wenn der Betreuer noch eine Überarbeitungsschleife angefordert hat

## Ablauf

### 1. Feedback-Eingabe

Optionen:
- `/apply-feedback` — Freitext-Modus: User paste Reviewer-Feedback in den Chat
- `/apply-feedback <pfad>.md` — Lese strukturiertes Feedback aus Datei
- `/apply-feedback last` — Suche letzte Feedback-Datei in `feedback/` (sortiert nach mtime)

Erwartete Struktur des Feedbacks (strukturiertes Format):
```markdown
# Reviewer-Feedback <Datum>

## Punkt 1: <Titel>
<Beschreibung>

## Punkt 2: ...
```

Bei Freitext: Skill extrahiert die Punkte heuristisch (Aufzählungen, nummerierte Listen, Sätze mit „klar zuordnen", „mindestens", „explizit benennen").

### 2. Punkt-Klassifikation

Für jeden Feedback-Punkt klassifiziere die Operation:

| Operation | Marker im Feedback | DOCX-Effekt |
|-----------|--------------------|-------------|
| **Citation-Tausch** | „klar … zuordnen", „nicht … sondern" | Substring-Replace mit alternativer Quelle |
| **Citation-Ergänzung** | „mindestens eine … Referenz", „Beleg ergänzen" | Co-Citation einfügen |
| **Quellen-Eindeutigkeit** | „nur der … Quelle", „eindeutig zuordnen" | Compound-Citation aufspalten |
| **Absatz-Ergänzung** | „explizit benennen", „kurz aufnehmen" | Neuen Absatz oder Sätze einfügen |
| **Lit-Verz-Eintrag** | implizit aus Citation-Ergänzung | Eintrag im Literaturverzeichnis ergänzen |
| **Sprach-Korrektur** | konkrete Wort-Vorschläge | Substring-Replace im Volltext |

### 3. DOCX inspizieren

Ziel-DOCX bestimmen (Default: jüngstes `_final_konform*.docx` in `output/phase-07-docx/`).

Pro Punkt den Anker lokalisieren:

```bash
python3 scripts/docx_inspect.py search <docx> "<Anker-Substring>"
```

Der Output zeigt Adresse (`p<N>`), Style, Run-Anzahl und ob der Substring in
einem Run liegt oder Run-Grenzen überspannt (`docx_patch.py` kann beides).
Bei mehreren Treffern: Anker verlängern oder die Adresse notieren.
Für Detailansicht: `python3 scripts/docx_inspect.py get <docx> p<N> --json`.

Falls fachlich unklar, welcher Treffer gemeint ist: AskUserQuestion mit Vorschlägen.

### 4. Patch-YAML erzeugen

Erzeuge `feedback/<timestamp>-<short-id>.patch.yaml`:

```yaml
src: output/phase-07-docx/<aktuelles-final-docx>.docx
# dst optional — Default: automatisches _v<N+1>-Suffix, src bleibt unangetastet
ops:
  # Punkt 1: <Titel> (Citation-Tausch / Sprach-Korrektur)
  - op: replace
    anchor: "<eindeutiger Anker-Substring>"
    old: "<old>"
    new: "<new>"

  # Punkt 2: <Titel> (Absatz-Ergänzung, Style wird vom Anker geklont)
  - op: insert_after
    anchor: "<Anker im Ziel-Kapitel>"
    text: "<Neuer Absatz>"

  # Lit-Verz-Eintrag (falls neue Quelle ergänzt; alphabetisch einsortieren)
  - op: insert_after
    anchor_startswith: "<alphabetisch davor stehender Lit-Verz-Eintrag>"
    text: "<APA7-Lit-Verz-Eintrag>"
```

Verfügbare Ops: `replace` (auch über Run-Grenzen), `insert_after`, `delete`.
Anker-Auflösung via `anchor` (Substring), `anchor_startswith` oder `address: p<N>`.

**Fallback:** Braucht ein Punkt Operationen jenseits dieser drei (Formatierung,
Tabellenzellen, Sektionen), generiere wie früher ein Skript aus
`base/templates/feedback-patch.py.template` — nur für diese Punkte.

### 5. Dry-Run

```bash
python3 scripts/docx_patch.py feedback/<...>.patch.yaml --dry-run
```

Schlägt hart fehl bei fehlendem oder mehrdeutigem Anker — kein stillschweigendes
No-Op. Output zeigt Vorher/Nachher-Fenster um jede Änderungsstelle.

### 6. Patch-Lauf

Zeige dem User den Dry-Run-Output („Folgende Änderungen werden auf das DOCX angewendet:"). Bei OK:
```bash
python3 scripts/docx_patch.py feedback/<...>.patch.yaml
```

Das Ergebnis landet als `_v<N+1>.docx` neben der Source-Datei; die Source bleibt unverändert.

### 7. Post-Validierung

Auto-Run von `/preflight` auf das neue `_v<N+1>.docx`:
- Bei blockierenden Verstößen: melden, anbieten, das Skript anzupassen
- Bei clean: weiter zu Schritt 8

### 8. Markdown-Quellen synchronisieren

Frage User: „Sollen die Markdown-Quellen (`output/phase-05-writing/final/*.md`) parallel angeglichen werden?"
- Ja → analog die Markdown-Stellen patchen, mit klarer Marker-Notiz, dass das DOCX die Source-of-Truth bleibt
- Nein → nur DOCX, Markdown bleibt veralteter Stand

### 9. Logging

Speichere das Feedback selbst in `feedback/<timestamp>-<short-id>.md` mit Verknüpfung zum Patch-YAML (bzw. Fallback-Skript) und Eintrag in `LESSONS.md`-Entwurf (manuell zu approven). Das Patch-YAML bleibt liegen — es dokumentiert den Eingriff und ist reproduzierbar.

## Beispiel — Fallstudie 1 Reviewer-Feedback

Aufruf: `/apply-feedback`

User pastet:
```
Quellenpräzisierung: 919.000 eNaira-Kund:innen klar nur der NIPC-2022-Quelle zuordnen, nicht IMF 2021.
Mindestens eine Course-Book-Referenz aus DLBFTBCKW01 einbauen.
Optional eine Quelle für den einleitenden Bitcoin/Finanzkrise-Bezug.
Im Fazit kurz und explizit die Methodengrenzen der eigenen qualitativen Bewertung benennen.
```

Skill klassifiziert:
- Punkt 1 → Quellen-Eindeutigkeit (Compound-Citation aufspalten)
- Punkt 2 → Citation-Ergänzung + Lit-Verz-Eintrag (Course-Book)
- Punkt 3 → Citation-Ergänzung (Co-Citation in Einleitung)
- Punkt 4 → Absatz-Ergänzung (Methodengrenzen-Sätze ins Fazit)

Erzeugt `feedback/2026-04-30-reviewer1.patch.yaml` mit 5 Ops (3× replace, 2× insert_after inkl. Lit-Verz-Eintrag). Dry-Run zeigt die Vorher/Nachher-Fenster, User bestätigt, Patch läuft, `/preflight` validiert das neue DOCX.

## Konfiguration

Das Skill nutzt Defaults aus `config.yaml`:
- `docx_frozen.guard_path` für Auto-Pick des Source-DOCX
- `preflight.*` für Post-Validierung
