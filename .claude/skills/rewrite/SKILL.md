---
name: rewrite
description: Schreibt ein Kapitel komplett neu. Nutze diesen Skill wenn der User /rewrite eingibt mit Kapitelnummer wie /rewrite 2.3.
---

# Kapitel neu schreiben

Verwirft den bestehenden Text eines Kapitels und schreibt es komplett neu.

## Ablauf

### 1. Kapitelnummer bestimmen

**Mit Parameter (z.B. /rewrite 2.3):**
- Verwende die angegebene Kapitelnummer

**Ohne Parameter:**
- Frage: "Welches Kapitel soll neu geschrieben werden? (z.B. 2.3)"

### 2. DOCX-Frozen-Mode-Warnung

Lies `config.yaml → docx_frozen.warn_on_markdown_edit` und `docx_frozen.guard_path`.

**Wenn ein passendes _final_konform-DOCX existiert UND `warn_on_markdown_edit: true`:**
- WARNE: „Ein finalisiertes DOCX existiert bereits. /rewrite ändert nur die Markdown-Quelle, NICHT das DOCX. Für DOCX-Änderungen ist `/apply-feedback` der richtige Weg."
- Frage explizit ab, ob trotzdem fortgefahren werden soll.

### 3. Sicherheitsabfrage

Prüfe ob das Kapitel bereits existiert:

**Falls in final/:**
"Kapitel [X.X] ist bereits freigegeben. Wenn du es neu schreibst,
wird die freigegebene Version archiviert. Bist du sicher?"

**Falls in draft/:**
"Kapitel [X.X] hat einen Entwurf. Dieser wird überschrieben.
Bist du sicher?"

**Falls nicht vorhanden:**
"Kapitel [X.X] wurde noch nicht geschrieben. Nutze /write [X.X] stattdessen."

### 3. Bestehenden Text archivieren

Falls eine Version existiert:
- Benenne die Datei um: `[X-X].md` -> `[X-X].bak.md` (im gleichen Ordner)
- Melde: "Vorherige Version gesichert als [X-X].bak.md"

### 4. Neu schreiben

Starte den Agent `.claude/agents/writer.md` für das Kapitel.
Der Agent folgt dem bestehenden Plan (es sei denn, der Plan wurde auch geändert).

### 5. Ergebnis

```
Kapitel [X.X] wurde neu geschrieben.

Vorherige Version: output/phase-05-writing/[draft|final]/[X-X].bak.md
Neue Version: output/phase-05-writing/draft/[X-X].md
Wörter: [Y] (vorher: [Z])

Prüfe das Ergebnis und nutze /approve um es freizugeben.
Falls die neue Version schlechter ist, kannst du die Backup-Datei
wiederherstellen.
```

### 6. Auto-Codex-Review (wenn aktiv)

Lies `config.yaml → codex.auto_review`.

Wenn `true`:
- Rufe `codex-review chapter [X.X] --quiet` auf den neuen Text auf.
- Codex prüft den Diff zwischen `.bak.md` und der neuen Fassung — sodass keine Reviewer-Lessons verloren gehen.

Wenn `false`: Skip.
