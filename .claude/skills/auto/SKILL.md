---
name: auto
description: Autonomer End-to-End-Lauf der gesamten Arbeit (Phase 1→7). Stoppt nur an den konfigurierten menschlichen Gates (Default Thema + Gliederung) und bei nicht automatisch behebbaren Verstößen. Nutze diesen Skill wenn der User /auto eingibt oder die Arbeit "durchlaufen lassen" will.
disable-model-invocation: true
---

# Autonomer Lauf (Orchestrator)

Treibt das Projekt selbstständig von der aktuellen Phase bis zum fertigen DOCX+PDF.
Ersetzt die manuelle Kette `/next` · `/approve` · `/next` · … durch einen einzigen,
unbeaufsichtigten Lauf mit zwei menschlichen Haltepunkten und einer Auto-Fix-Schleife.

> Dieser Skill orchestriert nur — die eigentliche Arbeit machen dieselben Agenten und
> Skripte wie im manuellen Workflow (brainstorming, outliner, citation-mapper,
> chapter-planner, writer, reviewer-*, finalizer, build_docx.py).

## Konfiguration (`config.yaml → workflow.auto`)

```yaml
workflow:
  auto:
    gates: ["topic", "outline"]      # menschliche Haltepunkte; [] = voll autonom
    max_autofix_attempts: 3          # Korrekturversuche pro Verstoß, dann Stopp + Report
    audit_log: "output/auto-run.log" # Protokoll aller Auto-Approves und Auto-Fixes
```

## Argumente

- `/auto` — läuft ab der aktuellen Phase (aus `progress.json`) bis Phase 7 oder zum nächsten Gate.
- `/auto --until <phase>` — stoppt nach der angegebenen Phase (z. B. `--until 2`).
- `/auto --from <phase>` — startet bei einer früheren Phase (setzt vorher implizit zurück, fragt nach).
- `/auto --no-gates` — ignoriert die Gates für diesen Lauf (überschreibt `workflow.auto.gates`).

## Vorlauf (einmalig, vor dem Loop)

1. **Setup-Check:** `config.yaml` vorhanden und konfiguriert (`autor.name`, `projekt.kurs_modul`,
   `formatierung`)? Wenn nicht → "Bitte zuerst `/setup` ausführen." und Stopp.
2. **Build-Tools:** `python3 -c "import docx"` (Pflicht). Fehlt → Installationshinweis, Stopp.
3. **Self-Repair:** `/validate --auto-repair` still laufen lassen (progress.json/Struktur).
4. **Log eröffnen:** Kopfzeile mit Timestamp + Startphase in `output/auto-run.log`.

## Haupt-Loop

Wiederhole, bis Phase 7 abgeschlossen ODER ein Gate erreicht ODER ein nicht behebbarer Blocker:

1. **Nächsten Schritt bestimmen** — exakt die Phasen-Logik aus `/next` (Phase 0→1→2→3→4/5 interleaved→6→7).
   Phase 3 wird bei `quellen.workflow: "keine"` automatisch übersprungen.
2. **Schritt ausführen** — den zuständigen Agenten starten (siehe `/next`).
3. **Gate prüfen** (vor dem Auto-Approve dieses Schritts):
   - `"topic"` ∈ gates und der eben abgeschlossene Schritt war **Phase 1 (Brainstorming)** →
     Ergebnis zeigen, **STOPP**: „Thema/Forschungsfragen prüfen. Mit `/approve` bestätigen,
     dann `/auto` fortsetzen (oder Ergebnis editieren und dann `/approve`)."
   - `"outline"` ∈ gates und der eben abgeschlossene Schritt war **Phase 2 (Gliederung)** →
     `thesis-structure.yaml` zeigen, **STOPP**: „Gliederung prüfen (wird danach gesperrt).
     Mit `/approve` bestätigen, dann `/auto` fortsetzen."
   - Sonst: weiter zu 4.
4. **Auto-Approve** — `/approve --auto` (draft→final, kein Prompt, Log-Eintrag).
5. **Auto-Fix-Gate** (nach Approve/Build, wo Validatoren laufen — v. a. Phase 6 und 7):
   siehe „Auto-Fix-Schleife".
6. **progress.json** aktualisieren, nächste Iteration.

### Phase-Spezifika im Auto-Lauf

- **Phase 4+5 (interleaved):** Pro Kapitel `chapter-planner` → Auto-Approve → `writer` → Auto-Approve,
  ohne Halt, bis alle Kapitel aus `thesis-structure.yaml` geplant UND geschrieben sind.
- **Phase 6 (Review):** entspricht `/review --all` im Auto-Modus — alle Kapitel, mechanische
  Korrekturen automatisch, nur strukturelle Hochschwere-Funde sammeln.
- **Phase 7 (Finalisierung):** `finalizer` → `build_docx.py` (DOCX + PDF) → `validate_docx.py` +
  `check_lit_verz_drift.py` (+ Codex falls aktiv) → Auto-Fix-Schleife → fertig.

## Auto-Fix-Schleife

Wenn ein Validator (`validate_docx.py`, `check_lit_verz_drift.py`), `/preflight` oder ein
Hochprioritäts-Codex-Fund einen **blockierenden** Verstoß meldet:

```
versuch = 0
solange blockierende Verstöße und versuch < max_autofix_attempts:
    versuch += 1
    Korrektur je Fund-Typ anwenden (siehe Tabelle), Log-Eintrag
    Build/Check wiederholen
wenn weiterhin blockierend:
    STOPP — Report mit verbleibenden Verstößen + was versucht wurde
```

| Fund | Auto-Korrektur |
|---|---|
| F9 Abgabedatum-Platzhalter | `config.abgabe.datum` ist leer → **nicht ratbar** → als Blocker melden (User muss Datum setzen) |
| F1–F8 Format | Builder-Parameter/`config.formatierung` prüfen, neu bauen |
| S1–S4 Pitfall-Strings | betroffene Stelle im Markdown korrigieren (Lessons-Mapping), Kapitel neu setzen |
| Lit-Verz-Drift (DOCX ohne literature.md) | fehlende Quelle in `literature.md` ergänzen bzw. Zitat im Text korrigieren |
| C1 Course-Book fehlt | Course-Book-Zitat im passenden Kapitel ergänzen |
| M1 Methodengrenzen | Limitations-Satz im Fazit ergänzen |
| N1 Zahlen-Mehrdeutigkeit | Compound-Citation an der Zahl auf Primärquelle reduzieren |

Nicht ratbare Lücken (fehlendes Abgabedatum, fehlende Pflicht-Quelle ohne Kandidat) werden
**nicht erfunden**, sondern als Blocker gemeldet — der Lauf stoppt sauber statt zu halluzinieren.

## Stopp-Bedingungen (sauberer Abschluss)

Der Lauf endet immer mit einem klaren Report:
- **Gate erreicht:** welches Gate, welches Artefakt zu prüfen, wie fortsetzen (`/approve` → `/auto`).
- **Fertig:** Pfade zu DOCX + PDF, Validator-Status, geschätzte Seitenzahl, offene Hinweise.
- **Blocker:** welcher Verstoß nach `max_autofix_attempts` blieb, was versucht wurde, was der User tun muss.

## Fortsetzen

Nach einem Gate-Stopp: User prüft, gibt mit `/approve` frei (oder editiert + `/approve`), dann
`/auto` erneut — der Loop nimmt ab `progress.json` wieder auf. Voll idempotent.

## Audit-Log (`output/auto-run.log`)

Eine Zeile je Aktion: `[ISO-Timestamp] PHASE/KAPITEL AKTION DETAIL`. Beispiele:
```
[…] phase-1 auto-approve brainstorming-result.md
[…] gate STOP topic — warte auf /approve
[…] phase-5/2.3 writer→auto-approve 2-3.md
[…] phase-7 build_docx.py → docx ok, pdf ok
[…] phase-7 autofix#1 F-Format → rebuild
[…] DONE docx=…  pdf=…  validator=clean
```
Macht jeden unbeaufsichtigten Lauf nachvollziehbar.
