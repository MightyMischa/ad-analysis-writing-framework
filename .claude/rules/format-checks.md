# Format-Checks gegen IU-Vorgaben

Diese Regeln gelten für jeden DOCX/PDF-Export. Sie werden vom Validator
(`scripts/validate_docx.py`) und vom `/codex-review`-Skill geprüft.

Die ausführliche Begründung steht in `LESSONS.md` (Abschnitt „Format-Lessons").

## Pflichtwerte im DOCX-XML

| Eigenschaft | Soll-Wert | XML-Pattern |
|---|---|---|
| Papierformat | DIN A4 | `<w:pgSz w:w="11906" w:h="16838"/>` in jeder Sektion |
| Seitenränder | 2,0 cm rundum | `<w:pgMar w:top="1134" w:bottom="1134" w:left="1134" w:right="1134"/>` |
| Heading 1 Farbe | Schwarz | `<w:color w:val="000000"/>` im Heading 1 Style |
| Heading 2 Farbe | Schwarz | dito Heading 2 |
| Heading 3 Farbe | Schwarz | dito Heading 3 |
| Body line spacing | 1,5 (Multiple) | `<w:spacing w:line="360" w:lineRule="auto"/>` |
| Lit-Verz Einzug | 1,27 cm hängend | `<w:ind w:left="720" w:hanging="720"/>` |
| Lit-Verz line spacing | 1,5 | `<w:spacing w:line="360" w:lineRule="auto"/>` |

## Seitenzählung — drei Sektionen

```
Sektion 0 (Titelblatt):    pgNumType fmt="upperRoman" start="1" + different_first_page = True
Sektion 1 (Frontmatter):   pgNumType fmt="upperRoman" start="2"   → TOC=II, Abk=III
Sektion 2 (Body):          pgNumType fmt="decimal"    start="1"   → Einleitung=1
```

## Heading-Stile als TOC-Anker

Damit Word-TOC-Field die Verzeichnisse aufnimmt:

- `p_inhaltsverzeichnis.style = doc.styles['Heading 1']`
- `p_abkuerzungsverzeichnis.style = doc.styles['Heading 1']`
- `p_literaturverzeichnis.style = doc.styles['Heading 1']`

### TOC-Ebenen-Stile (Ebene 1 fett, 2/3 normal)

Frühere Annahme war, `doc.styles['TOC 1'].font.bold = True` allein genüge. Das
stimmt NICHT: Word legt `TOC 2`/`TOC 3` beim Feld-Update selbst an — mit
inkonsistenter Fett-Optik, sodass Ebene 1 nicht zuverlässig fett wirkt. Daher
alle drei Ebenen explizit definieren:

- `TOC 1` → fett (IU-Vorgabe „erste Ebene fett")
- `TOC 2` → ausdrücklich `font.bold = False`
- `TOC 3` → ausdrücklich `font.bold = False`

Geprüft von `validate_docx.py::check_toc_levels`: TOC1 muss `<w:b/>` tragen,
TOC2/TOC3 müssen vorhanden und nicht fett (`<w:b w:val="0"/>`) sein.

## Tabellenverzeichnis (wenn Tabellen-Caption mit SEQ)

- Caption-Format: `Tabelle [SEQ Tabelle \* ARABIC]: <Beschriftung>`
- Tabellenverzeichnis-Field: `TOC \h \z \c "Tabelle"`
- In `config.yaml`: `verzeichnisse.tabellenverzeichnis: true`

## Defensive Defaults für jede neue Sektion

python-docx erbt Sektions-Attribute NICHT von der Vorgängersektion. Daher
nach jedem `doc.add_section(WD_SECTION.NEW_PAGE)` explizit setzen:

```python
section.page_width = Cm(21.0)
section.page_height = Cm(29.7)
section.top_margin = Cm(2)
section.bottom_margin = Cm(2)
section.left_margin = Cm(2)
section.right_margin = Cm(2)
```

## Body-Spacing erzwingen

`pf.line_spacing = 1.5` allein kann zu wenig sein. Gründe siehe LESSONS.md F3.
Sicherstellen, dass das Spacing-Element explizit `line=360` enthält:

```python
pf = paragraph.paragraph_format
pf.line_spacing_rule = WD_LINE_SPACING.MULTIPLE
pf.line_spacing = 1.5
pf.space_before = Pt(0)
pf.space_after = Pt(6)
```

## Heading-Farbe doppelt absichern

```python
# Style-Ebene
for h_name, h_size in [('Heading 1', 16), ('Heading 2', 14), ('Heading 3', 11)]:
    style = doc.styles[h_name]
    style.font.color.rgb = RGBColor(0, 0, 0)

# Run-Ebene zusätzlich nach jedem add_run für Heading-Paragraphen
run.font.color.rgb = RGBColor(0, 0, 0)
```

## Pflicht-Verifikation nach Build

Validator-Skript ausführen:

```bash
python3 scripts/validate_docx.py output/phase-07-docx/<datei>.docx
```

Bei Verstößen → Build-Skript anpassen, NICHT manuell in Word korrigieren
(verloren beim nächsten Build).

## Nur im echten Render prüfbar (nicht im XML)

`validate_docx.py` arbeitet rein auf dem DOCX-XML. Die am stärksten benoteten
Formalvorgaben sind aber **Render-Fragen**, die das XML NICHT entscheidet:

- **Seitenumfang 7–10 Seiten Textteil** (Einleitung bis Fazit, ohne Verzeichnisse)
- **≥ 0,5 Seite je Unterkapitel**
- **Seitenzahlen sichtbar korrekt**: Titelblatt ohne Zahl, Frontmatter römisch
  (Inhaltsverzeichnis = II), Body arabisch ab Einleitung = 1
- **Inhaltsverzeichnis-Ebene 1 optisch fett** nach Feld-Update
- **letzte Textseite nicht fast leer**

„`validate_docx.py` grün" heißt also NICHT „Dokument korrekt". Die Wort-→-Seiten-
Heuristik ist nur eine grobe Schätzung: kalibrierter Richtwert **~330 Wörter/Seite**
(Arial 11, 1,5-zeilig), nicht 250. Die Render-Punkte gehören in die verbindliche
Word-Gate-Checkliste des `/preflight`-Skills (Schritt „F9 + Sichtprüfung"), nicht
in eine Fußnote.
