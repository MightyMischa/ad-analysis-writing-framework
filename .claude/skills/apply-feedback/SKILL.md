---
name: apply-feedback
description: Nimmt Reviewer-Feedback (Freitext oder strukturiert) und erzeugt ein Patch-Skript für das finale DOCX. Bewahrt Format-Fixes, die nur im DOCX existieren. Aufruf via /apply-feedback.
---

# Reviewer-Feedback ins DOCX einarbeiten

Formalisiert das Muster, das bei Fallstudie 1 (Digitaler Euro) ad-hoc per `apply_reviewer_feedback.py` gelöst wurde. Zentral, wenn das DOCX die Source-of-Truth ist (Frozen-Mode aktiv).

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

Lies das Ziel-DOCX (Default: jüngstes `_final_konform*.docx` in `output/phase-07-docx/`).

Pro Punkt:
- Lokalisiere den Anker-Absatz via Substring-Suche im DOCX-Text
- Notiere Run-Struktur (1 Run vs. mehrere)
- Plane die exakte String-Operation

Falls Anker nicht eindeutig: AskUserQuestion mit Vorschlägen.

### 4. Patch-Skript generieren

Erzeuge `scripts/apply_<short-id>_feedback.py` analog zur Vorlage in `base/templates/feedback-patch.py.template`. Skript-Struktur:

```python
#!/usr/bin/env python3
"""Wendet Reviewer-Feedback vom <Datum> auf das finale DOCX an."""

from copy import deepcopy
from pathlib import Path
from docx import Document

PROJECT = Path("<absoluter-pfad>")
SRC = PROJECT / "output" / "phase-07-docx" / "<aktuelles-final-docx>"
DST = PROJECT / "output" / "phase-07-docx" / "<aktuelles-final-docx>_v<N+1>.docx"

# Helper: replace_in_single_run_paragraph, insert_paragraph_after
# (siehe base/templates/feedback-patch.py.template)

def main():
    doc = Document(str(SRC))
    paras = doc.paragraphs

    # Punkt 1: <Titel>
    para = next(p for p in paras if "<eindeutiger Anker-Substring>" in p.text)
    replace_in_single_run_paragraph(para, "<old>", "<new>")
    print("✓ Punkt 1: <kurz>")

    # Punkt 2: ...

    # Lit-Verz-Eintrag (falls neue Quelle ergänzt)
    para_anchor = next(
        p for p in paras
        if p.text.startswith("<alphabetisch-davor-stehender-Eintrag>")
    )
    insert_paragraph_after(para_anchor, "<APA7-Lit-Verz-Eintrag>")
    print("✓ Lit-Verz: <neue Quelle> ergänzt")

    doc.save(str(DST))
    print(f"\n✓ Gespeichert: {DST.relative_to(PROJECT)}")


if __name__ == "__main__":
    main()
```

### 5. Vor-Validierung

Vor dem Speichern: nutze `replace_in_single_run_paragraph`-Wrapper, der bei fehlendem Anker explizit fehlschlägt — kein stillschweigendes No-Op.

### 6. Patch-Lauf

Frage User um Bestätigung („Folgende Änderungen werden auf das DOCX angewendet:" + Liste). Bei OK:
```bash
python3 scripts/apply_<short-id>_feedback.py
```

### 7. Post-Validierung

Auto-Run von `/preflight` auf das neue `_v<N+1>.docx`:
- Bei blockierenden Verstößen: melden, anbieten, das Skript anzupassen
- Bei clean: weiter zu Schritt 8

### 8. Markdown-Quellen synchronisieren

Frage User: „Sollen die Markdown-Quellen (`output/phase-05-writing/final/*.md`) parallel angeglichen werden?"
- Ja → analog die Markdown-Stellen patchen, mit klarer Marker-Notiz, dass das DOCX die Source-of-Truth bleibt
- Nein → nur DOCX, Markdown bleibt veralteter Stand

### 9. Logging

Speichere das Feedback selbst in `feedback/<timestamp>-<short-id>.md` mit Verknüpfung zum erzeugten Patch-Skript und Eintrag in `LESSONS.md`-Entwurf (manuell zu approven).

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

Erzeugt `scripts/apply_2026-04-30_feedback.py` mit 5 konkreten Operationen (4 Patches + 1 Lit-Verz-Insertion). User bestätigt, Skript läuft, `/preflight` validiert das neue DOCX.

## Konfiguration

Das Skill nutzt Defaults aus `config.yaml`:
- `docx_frozen.guard_path` für Auto-Pick des Source-DOCX
- `preflight.*` für Post-Validierung
