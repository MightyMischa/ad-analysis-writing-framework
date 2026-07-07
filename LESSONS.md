# Lessons aus Reviewer-Feedback

Diese Datei sammelt alle Lessons aus echten Prüf- und Reviewer-Durchläufen.
Sie wird von Schreib- und Review-Agenten geladen und sollte nach jedem
externen Review-Zyklus erweitert werden — nicht ersetzt.

**Aktualisierungs-Regel:** Wenn ein Reviewer einen Fehler findet, hier eintragen,
sonst wird er beim nächsten Mal wieder gemacht.

---

## Format-Lessons (IU-Richtlinien)

### F1 — Papierformat MUSS DIN A4 sein
- **Pitfall:** python-docx verwendet ohne explizite Konfiguration den Word-Default (US Letter, 21,59 × 27,94 cm).
- **Korrekt:** Nach `Document()` für JEDE Sektion `section.page_width = Cm(21.0); section.page_height = Cm(29.7)` setzen, auch für später erzeugte Sektionen.
- **Verifikation:** `<w:pgSz w:w="11906" w:h="16838"/>` in document.xml.

### F2 — Überschriften MUSS schwarz sein
- **Pitfall:** Word-Default-Theme rendert Heading 1/2/3 in Blau (`themeColor="accent1"`, RGB 4F81BD).
- **Korrekt:** Heading-Stile zentral patchen: `doc.styles['Heading X'].font.color.rgb = RGBColor(0, 0, 0)` plus auf jedem Run zusätzlich `r.font.color.rgb = RGBColor(0, 0, 0)`.
- **Achtung:** Heading 3 ist besonders anfällig, weil viele Word-Builder es übersehen.

### F3 — Body-Zeilenabstand MUSS 1,5 sein
- **Pitfall:** Word-`docDefaults` setzen `line=276` (1,15-zeilig). Wenn ein Paragraph ein `<w:spacing>`-Element ohne `line`-Attribut hat, fällt Word auf den docDefault zurück, NICHT auf den Normal-Style.
- **Korrekt:** Auf JEDEM Body-Paragraph explizit `pf.line_spacing = 1.5` setzen, damit `line=360` ins XML geschrieben wird. Style-Vererbung allein reicht nicht.
- **Ausnahme:** Tabellenzellen, leere Spacer und Heading-Stile dürfen 1,15 oder 1,0 sein.

### F4 — Hängender Einzug im Literaturverzeichnis = 1,27 cm
- **Pitfall:** 1,0 cm wirkt zu schmal, wird vom Reviewer angemerkt.
- **Korrekt:** `pf.left_indent = Cm(1.27); pf.first_line_indent = Cm(-1.27)` → ergibt `hanging="720"` Twips im XML.

### F5 — Seitenzählung Vorspann römisch, Body arabisch
- **Schema:** Titelblatt = I (nicht angezeigt) → Inhaltsverzeichnis = II → Abkürzungsverzeichnis = III → Einleitung = arabisch ab 1.
- **Pitfall:** Wenn Titelblatt-Sektion keine eigene `pgNumType`-Konfiguration hat, springt Word auf decimal default.
- **Korrekt:** Drei Sektionen explizit konfigurieren:
  - Titelblatt: `<w:pgNumType w:fmt="upperRoman" w:start="1"/>` (different_first_page → keine Anzeige)
  - Frontmatter (TOC + Abk.): `<w:pgNumType w:fmt="upperRoman" w:start="2"/>`
  - Body: `<w:pgNumType w:fmt="decimal" w:start="1"/>`

### F6 — Inhaltsverzeichnis erste Ebene fett + alle Verzeichnisse drin
- **Pitfall:** Das Word-TOC-Field nimmt nur Paragraphen mit Heading-Style auf. Wenn „Abkürzungsverzeichnis" oder „Literaturverzeichnis" nur als formatierter Paragraph existieren, fehlen sie im TOC.
- **Korrekt:**
  - `p_abk.style = doc.styles['Heading 1']` für Abk-Verz, Lit-Verz, Inhaltsverzeichnis selbst.
  - `doc.styles['TOC 1'].font.bold = True` damit erste Ebene fett erscheint.

### F7 — Tabellenverzeichnis nötig, sobald eine Tabelle nummeriert wird
- **Pitfall:** Reviewer erwartet bei einer methodisch sichtbaren Tabelle (z. B. Bewertungsmatrix) auch ein Tabellenverzeichnis.
- **Korrekt:**
  - SEQ-Field unter der Tabelle: `SEQ Tabelle \* ARABIC` mit Caption-Style.
  - Tabellenverzeichnis-Field: `TOC \h \z \c "Tabelle"`.

### F8 — Deckblatt: Hochschulname als Text, nicht nur Logo
- **Pitfall:** Bei strenger Auslegung gilt Logo allein als unzureichend.
- **Korrekt:** Direkt unter dem Logo eine zentrierte fette Textzeile „IU Internationale Hochschule".
- **Bonus:** „Prüfungsform: Fallstudie" statt „Fallstudie -" (kein Hänge-Bindestrich).

### F9 — Abgabedatum auf Titelblatt MUSS gesetzt sein
- **Pitfall:** `[Abgabedatum ergänzen]` als Platzhalter wirkt unfertig und kostet Punkte.
- **Korrekt:** Vor PDF-Export `config.yaml → abgabe.datum` füllen, Build neu laufen lassen.

### F10 — Abgabe als PDF, nicht DOCX
- **Pitfall:** Turnitin verlangt PDF.
- **Korrekt:** Word „Speichern als → PDF" oder `libreoffice --headless --convert-to pdf …`.

---

## Quellen-Lessons (APA 7 nach IU-Standard ab 01.10.2025)

### Q1 — Working Papers vollständig zitieren
- **Pitfall:** „CESifo Working Paper Series" allein reicht nicht.
- **Korrekt:** Working-Paper-Nummer + Reihe + URL/DOI.
  - Beispiel: `Auer, R. A., Cornelli, G., & Frost, J. (2020). Rise of the Central Bank Digital Currencies. CESifo Working Paper No. 8655. https://www.cesifo.org/...`

### Q2 — Suffix-Konsistenz: kein `_b` ohne `_a`
- **Pitfall:** `(EZB, 2023b)` im Text + nur `EZB (2023b)` im Lit-Verz, ohne irgendwo eine 2023a-Quelle.
- **Korrekt:**
  - Wenn nur eine Quelle desselben Autors/Jahres existiert: ohne Suffix.
  - Bei zwei oder mehr: `_a`, `_b`, `_c` durchgängig im Text UND im Lit-Verz.
- **Beispiel:** `EZB (2025a). Preparation phase report.` + `EZB (2025b). Eurosystem moving to next phase.`

### Q3 — Institutionelle Erstnennung mit Klammer-Abkürzung
- **APA-Regel:** Erstnennung „Bundesministerium der Finanzen [BMF] (2023)" oder „(Bundesministerium der Finanzen [BMF], 2023)". Spätere Nennung nur „BMF, 2023".
- **Pitfall:** Nur „BMF, 2023" im Text, voller Name nur im Lit-Verz wirkt inkonsistent.

### Q4 — Undatierte Webseiten: `n. d.` statt Jahr
- **Pitfall:** Webseiten wie Atlantic Council CBDC Tracker oder Sand Dollar Übersicht haben kein festes Veröffentlichungsdatum, mit „2023" wird die Quelle bei jedem späteren Zugriff veraltet.
- **Korrekt:** APA-Konvention `n. d.` (no date) plus Abrufdatum: `Atlantic Council. (n. d.). Central Bank Digital Currency Tracker. Abgerufen am DD.MM.YYYY, von URL`.

### Q5 — Journal-Artikel mit DOI
- **Pitfall:** Journal-Artikel ohne DOI wirken oberflächlich recherchiert.
- **Korrekt:** DOI als URL anhängen: `https://doi.org/10.1007/s10273-020-2702-7`.

### Q6 — Online-Quellen mit aktuellem Abrufdatum
- **Pitfall:** Tracker und Projektseiten ändern Inhalte. Ohne Abrufdatum ist die Quelle nicht reproduzierbar.
- **Korrekt:** `abruf: "DD.MM.YYYY"` im YAML, im Lit-Verz als „Abgerufen am ..., von URL".

---

## Inhalt-Lessons (Aktualität von Fakten)

### I1 — CBDC-Tracker-Zahlen aktuell halten
- **Stand 2026 (Atlantic Council CBDC Tracker):** 137 Länder/Währungsräume / 98 % des globalen BIP / drei vollständig eingeführte Retail-CBDCs: Bahamas, Jamaika, Nigeria.
- **Pitfall:** „114 Staaten / 95 %" ist Stand 2023 und veraltet.

### I2 — Sand Dollar (Bahamas) ist die WELTWEIT ERSTE CBDC
- **Datum:** 20.10.2020 landesweit eingeführt.
- **Pitfall:** „eNaira als weltweit erste CBDC" ist falsch. Nigeria startete eNaira erst 25.10.2021 als ZWEITES Retail-CBDC (und erstes afrikanisches).
- **Korrekt:** Sand Dollar als weltweit erstes, eNaira als zweites/erstes-afrikanisches benennen.

### I3 — EZB-Vorbereitungsphase wurde Oktober 2025 abgeschlossen
- **Stand 2026:**
  - Vorbereitungsphase: November 2023 – Oktober 2025 (abgeschlossen).
  - EZB-Rat hat den Übergang in die nächste Projektphase beschlossen.
  - Pilot: zweite Jahreshälfte 2027 (12 Monate).
  - Mögliche erste Ausgabe: 2029 (vorbehaltlich EU-Gesetzgebung).
- **Pitfall:** „Vorbereitungsphase im November 2023 gestartet" ohne Hinweis auf Abschluss wirkt veraltet.

### I4 — Reverse-Waterfall-Funktion erwähnen
- **Aktuelles EZB-Konzept:** Bei unzureichendem Wallet-Guthaben wird der fehlende Betrag automatisch vom verknüpften Bankkonto nachgeladen. Umgekehrt (Waterfall) werden überschüssige Beträge automatisch aufs Konto zurückgeführt.
- **Relevanz:** Wichtig für 2.3 Technische Funktionsweise und für die Bewertung von Haltegrenzen.

### I5 — Kryptowährungs-Abgrenzung in 2.1 ist Pflicht
- **Pitfall:** Wenn der Digitale Euro nicht klar von Bitcoin und Stablecoins abgegrenzt wird, fehlt eine zentrale Begriffsdimension.
- **Korrekt:** Bitcoin (dezentrales Kryptonetzwerk, kein Zentralbank-Anspruch), Stablecoin (privater Emittent, eigene Risiken), digitaler Euro (Forderung gegen Eurosystem, gesetzliches Zahlungsmittel) abgrenzen.

---

## Methoden-Lessons (Fallstudien-Charakteristika)

### M1 — Fallrahmen aus Endnutzer:innen-Perspektive setzen
- **Pitfall:** Reviewer-Kritik „wirkt eher wie kompakte Literaturarbeit" entsteht, wenn keine konkrete Entscheidungssituation skizziert wird.
- **Korrekt:** In 1.2 eine konkrete Endnutzerin beschreiben (Girokonto, Banking-App, P2P, Reisen, Krisenfall) und alle drei Anwendungsfälle aus ihrer Perspektive bewerten.

### M2 — Bewertungsmatrix als sichtbare Tabelle
- **Pitfall:** Reine Fließtext-Bewertung wirkt nicht methodisch transparent.
- **Korrekt:** Tabelle mit Anwendungsfällen × 5–6 Kriterien (Alltagsnutzen, Resilienz, Datenschutz, Stabilitätsrisiko, Umsetzbarkeit, Gesamtnutzen). Stufen niedrig/mittel/hoch oder 1–5.
- **Bonus:** Bewertungs-Schema schon in 1.2 ankündigen → roter Faden.

### M3 — Blockchain-/DLT-Bezug muss vertieft sein, nicht nur erwähnt
- **Pitfall:** „CBDC nutzt DLT" reicht im Blockchain-Kursbuch nicht.
- **Korrekt:** Token-Modell (UTXO vs. Account), permissioned vs. public DLT, Double-Spending-Mechanismus, Wallet-Sicherheit (Secure Element / Secure Enclave), kryptografische Signaturen.

### M4 — Empfehlung im Fazit muss konkret sein
- **Pitfall:** „Differenzierte Einschätzung" ohne Aussage, welcher Anwendungsfall am stärksten ist, wirkt unentschlossen.
- **Korrekt:** Klar benennen: Offline-Anwendungsfall hat den größten Alleinstellungsnutzen, weil keine bestehende digitale Lösung diese Resilienz bietet. Plus drei konkrete Mindestbedingungen für die Nutzung (kostenlose Wallet, Offline-Limits, technisch nachvollziehbarer Datenschutz).

### M5 — Methodengrenzen im Fazit explizit benennen (Reviewer FS1)
- **Pitfall:** Fazit ohne kritische Reflexion der eigenen qualitativen Bewertung.
- **Korrekt:** Mindestens zwei bis drei Sätze, die Methode (qualitative Sekundärquellenanalyse, kein standardisiertes Bewertungsinstrument), Auswahl-Begründung (drei exemplarische Anwendungsfälle, keine Vollerhebung) und Datenlimitationen (z. B. „belastbare Aussagen setzen empirische Daten aus der Pilotphase voraus") benennen.
- **Auto-Check:** `validate_docx.py → check_methodengrenzen` (Code M1).
- **Begründung:** Bewertungskriterium „Ergebnis 25 % — kritische Reflexion" verlangt diese Aussage.

### M6 — Course-Book-Referenz pflicht bei IU-Fallstudien (Reviewer FS1)
- **Pitfall:** Keine Inline-Citation auf das IU-Lernskript des jeweiligen Moduls (DLBxxxxx).
- **Korrekt:** Mindestens eine Co-Citation an einer organischen Stelle (z. B. neben dem Hauptautor in Kapitel 2.x), Form: „(Autor, Jahr; IU Internationale Hochschule [IU], Jahr, Lektion X.Y)".
- **Auto-Check:** `validate_docx.py → check_course_book_presence` (Code C1) bei `projekt.kurs_modul` gesetzt.
- **Auto-Setup:** `/setup` legt `projekt.kurs_modul`, `projekt.kurs_titel`, `projekt.course_book_pfad` an.

### M7 — Konkrete Zahlen brauchen genau eine Primärquelle (Reviewer FS1)
- **Pitfall:** Statistik mit Compound-Citation, z. B. „919.000 Kund:innen (IMF, 2021; NIPC, 2022)" — unklar, welche Quelle die Zahl belegt.
- **Korrekt:** Aufsplitten in zwei Sätze mit je einer Primärquelle. Einzeln zugewiesene Zahlen, eindeutige Belege.
- **Auto-Check:** `validate_docx.py → check_number_source_uniqueness` (Code N1).

---

## Sprache-Lessons (häufige Fehler)

### S1 — `dreier` statt `drei` in Genitiv-Konstruktion
- **Pitfall:** „anhand drei typischer Anwendungsfälle" ist falsch.
- **Korrekt:** „anhand dreier typischer Anwendungsfälle" oder „anhand von drei typischen Anwendungsfällen".

### S2 — `die` SEPA, nicht `der` SEPA
- **Begründung:** Single Euro Payments Area → Area = die Area.
- **Pitfall:** „der Single Euro Payments Area" oder „der SEPA" ist genusfalsch.

### S3 — `ein solches`, nicht `so ein`
- **Pitfall:** „so ein Szenario" ist umgangssprachlich.
- **Korrekt:** „ein solches Szenario".

### S4 — `Countering the Financing of Terrorism`, nicht `Counter-Financing`
- **Pitfall:** Falscher englischer Fachterminus.
- **Korrekt:** CFT = Countering the Financing of Terrorism (FATF-Standard-Terminologie).

### S5 — Abkürzungsverzeichnis: nur tatsächlich genutzte Abkürzungen
- **Pitfall:** MiCAR im Verzeichnis, aber nicht im Text → wirkt unfertig.
- **Pitfall:** BIS und SEPA im Text, aber nicht im Verzeichnis → wirkt inkonsistent.
- **Korrekt:** Vor Abgabe Abkürzungsverzeichnis gegen Volltext abgleichen.

---

## R-Toolchain-Lessons (für empirisch-quantitative Fallstudien mit R)

Aktiv bei `config.yaml → r_toolchain.enabled: true`. Validator: `scripts/validate_r_reproducibility.py`.

### R1 — R-Skripte müssen ohne Syntaxfehler parsen
- **Pitfall:** Ein Tippfehler in einem späten Abschnitt blockiert den ganzen Lauf, fällt aber erst beim Reproduzieren auf.
- **Korrekt:** `parse(file=...)` per Rscript prüft alle Skripte ohne Side-Effects.

### R2 — Pfade müssen portabel sein
- **Pitfall:** `/Users/<name>/...` oder `setwd("/absolute/path")` macht das Repo auf einem anderen Rechner unbenutzbar.
- **Korrekt:** Relative Pfade ab Repo-Root, `here::here()` oder Project-Root-Variable verwenden.

### R3 — `set.seed()` bei Zufalls-API
- **Pitfall:** `sample()`, `rnorm()`, `runif()` ohne `set.seed()` produzieren bei jedem Lauf andere Werte — Reviewer kann Tabellen/Plots nicht replizieren.
- **Korrekt:** Direkt am Anfang des Skripts oder vor jedem zufallsabhängigen Block ein expliziter `set.seed(<int>)`.

### R4 — Output-Pfade konsistent
- **Pitfall:** Plots in `/tmp/`, Tabellen in `~/Desktop/`, jede Datei woanders → reproduzierbare Verzeichnisstruktur fehlt.
- **Korrekt:** Alle generierten Outputs in `output/r-results/` (Default aus `config.yaml → r_toolchain.outputs_dir`).

### R5 — Citation-Hook: jeder Plot/Output im Volltext referenziert
- **Pitfall:** R-Skript erzeugt fünf Plots, von denen nur drei im Text auftauchen — ungenutzte Outputs irritieren den Reviewer.
- **Korrekt:** Jeder generierte Dateiname (Stem) erscheint mindestens einmal im Volltext (als Caption „Abbildung X: …" oder Verweis). `validate_r_reproducibility.py → check_citation_hook` prüft das automatisch.

---

## Pflicht-Checks vor jeder Abgabe

**Empfohlener Workflow:** `/preflight` ausführen — bündelt alle Checks unten in einem blockierenden Gate.

Vor `/compile` oder `/finalize` werden geprüft:

**Format (F1–F10):**
1. [ ] DIN A4 (`pgSz w="11906" h="16838"`) — alle Sektionen (F1)
2. [ ] Heading 1/2/3 schwarz (`color val="000000"`) (F2)
3. [ ] Body line=360 (1,5-zeilig) auf allen Fließtext-Paragraphen (F3)
4. [ ] Hängender Einzug 1,27 cm (`hanging="720"` Twips) im Lit-Verz, line=360 (F4)
5. [ ] Seitenzählung: Titelblatt blank → II → III → arabisch 1 (F5)
6. [ ] Inhaltsverzeichnis enthält Abk-Verz, Lit-Verz; erste Ebene fett (F6)
7. [ ] Tabellenverzeichnis aktiv falls Tabellen mit SEQ (F7)
8. [ ] Abkürzungsverzeichnis konsistent mit Volltext (S5)
9. [ ] Abgabedatum auf Titelblatt eingetragen (F9)

**Quellen (Q1–Q6):**
10. [ ] Working Papers vollständig zitiert (Q1)
11. [ ] Suffix-Konsistenz im Lit-Verz und Inline (Q2)
12. [ ] Institutionelle Erstnennung mit Klammer-Abkürzung (Q3)
13. [ ] Lit-Verz APA: DOIs, n. d., Abrufdaten (Q4–Q6)
14. [ ] **Lit-Verz-Drift-Check via `check_lit_verz_drift.py`** (jede DOCX-Quelle hat literature.md-Eintrag)

**Inhalt (I1–I5):**
15. [ ] Aktualität: Atlantic-Council-Zahlen, Bahamas-Reihenfolge, EZB-2025-Status (I1–I5)

**Methode (M1–M7):**
16. [ ] Fallrahmen aus Endnutzer:innen-Perspektive (M1)
17. [ ] Bewertungsmatrix als sichtbare Tabelle (M2)
18. [ ] Blockchain-/DLT-Bezug vertieft (M3)
19. [ ] Fazit: konkrete Empfehlung (M4)
20. [ ] **Fazit: Methodengrenzen explizit benannt (M5 — neuer Validator-Code M1)**
21. [ ] **Course-Book-Referenz vorhanden bei IU-Fallstudien (M6 — Validator-Code C1)**
22. [ ] **Konkrete Zahlen mit eindeutiger Primärquelle (M7 — Validator-Code N1)**

**Sprache (S1–S5):**
23. [ ] Sprachfehler-Check: `dreier`, `die SEPA`, `ein solches`, `Countering the Financing`

**R-Toolchain (nur wenn aktiv, R1–R5):**
24. [ ] R-Skripte parsen ohne Syntaxfehler (R1)
25. [ ] Pfade portabel, kein /Users/, kein setwd (R2)
26. [ ] set.seed bei Zufalls-API (R3)
27. [ ] Outputs in `r_toolchain.outputs_dir` (R4)
28. [ ] Plot/Output im Volltext referenziert (R5)

**Abgabe:**
29. [ ] PDF-Export, Turnitin-Konvention beim Dateinamen (F10)

Der `/codex-review`-Skill ruft Codex (`gpt-5.5`, `model_reasoning_effort=xhigh`) auf,
um diesen Katalog gegen den aktuellen Repo-Stand automatisch zu prüfen.

---

## Build-/Tooling-Lessons (Builder-Bugs, behoben 2026-06-18 in „nova", zurückportiert ins Framework)

### B-Table — Markdown-Tabellen brauchen feste, inhaltsproportionale Spaltenbreiten
- **Pitfall:** `add_markdown_table` setzte `table.autofit = True` ohne Spaltenbreiten. python-docx/Word schreibt dann GLEICH breite Spalten, wodurch eine lange Textspalte (z. B. User-Story) genauso schmal wird wie eine winzige Nr.-Spalte und in 6–7 Zeilen umbricht.
- **Korrekt:** `autofit = False` (→ `tblLayout fixed`), Breiten inhaltsproportional (`compute_col_widths_cm`, Mindestbreite + Deckel), je Zelle `tcW` UND `gridCol` setzen, Tabellenschrift `TFSIZE` (Default 10 pt), einzeiliger Zellabstand.
- **Bonus:** `w:cantSplit` je Zeile + `keep_with_next` auf allen Zeilen außer der letzten → Tabelle bricht nicht über den Seitenumbruch. `insideV single` für vertikale Spaltentrennlinie (APA: optional).

### B-Bib — Lit-Verz muss journal-DOI, Sammelband- und Konferenz-Felder rendern
- **Pitfall:** `add_bib_entry` hatte nur `journal/buch/website/report`-Branches; `sammelband` und `konferenz` fielen in den `else`-Zweig → nur der Titel wurde gerendert (Sammelbandtitel, Seiten, Verlag, Konferenz, URL verschwanden). journal ohne DOI.
- **Symptom:** Quelldaten in literature.md komplett, im DOCX aber Titel-Fragmente. Der Drift-Check bleibt grün (zählt nur Existenz) und schlägt NICHT an.
- **Korrekt:** journal um DOI ergänzen, eigene Branches für `sammelband` („In Sammelbandtitel (S. x–y). Verlag. DOI") und `konferenz` („Konferenz/Ort. Abgerufen am …, von URL").

### B-Glob — `.prehum`-Backups aus dem Kapitel-Glob ausschließen
- **Pitfall:** `/humanize` legt Sicherungen als `X.prehum.md` im selben `final/`-Ordner ab. `CHAP_DIR.glob("*.md")` zieht sie mit → betroffene Kapitel inkl. Tabellen werden DOPPELT gerendert.
- **Korrekt:** Im Glob `if ".prehum." not in p.name` filtern (Body- UND Anhang-Glob, falls getrennt).

### B-TOC — Tabellenverzeichnis als Heading 1, Inhaltsverzeichnis NICHT
- **Pitfall:** Das Tabellenverzeichnis hatte keinen Heading-1-Stil → fehlte als Eintrag im Inhaltsverzeichnis. Das Inhaltsverzeichnis war selbst Heading 1 → listete sich selbst.
- **Korrekt:** `p_tab_title.style = Heading 1` (erscheint im TOC), Inhaltsverzeichnis-Titel NICHT als Heading 1 (Optik per Run-Format halten). F6 verlangt nur ≥ 4 Heading-1-Absätze → bleibt grün.

## Build-/Tooling-Lessons (zurückportiert 2026-06-24 aus „nachhaltigkeit-innovation-finanzwesen" / M-Pesa)

### B-CiteCI — In-Text-Zitate case-insensitiv matchen (sonst fällt eine Quelle aus dem Lit-Verz)
- **Pitfall:** `build_docx.get_used_sources` matchte In-Text-Zitate als CASE-SENSITIVE Substring (Pattern aus Nachname + Jahr). Ein satzinitial großgeschriebener Partikel-Nachname („De Vries (2018") matchte die Stammform „de Vries (2018" NICHT → die zitierte Quelle fehlte im Literaturverzeichnis (echter APA-Fehler). Beinahe abgegeben.
- **Korrekt:** `_cite_in_text()` matcht case-insensitiv (`re.IGNORECASE`) mit Wortgrenzen-Guard `(?<!\w)`, damit ein Kürzel nicht mitten in einem Wort matcht (z. B. „un, 2015" in „Jun, 2015" für eine UN-Quelle). Verankerung durch Jahr + „(" / „, " hält Falsch-Positive nahe null.

### B-DriftBlock — „zitiert, aber nicht im Lit-Verz" ist BLOCKIEREND, nicht nur Warnung
- **Pitfall:** `check_lit_verz_drift` meldete eine im Volltext zitierte, aber im gerenderten Lit-Verz fehlende Quelle nur als nicht-blockierende Warnung („Stammdaten ohne DOCX-Verwendung"). Genau das Symptom von B-CiteCI rutschte so durch.
- **Korrekt:** `only_in_md` aufteilen: im Volltext zitiert + fehlt im Lit-Verz → BLOCKIEREND (`source_cited_in_text`, gespiegelte Match-Logik); nirgends zitierte Stammdaten bleiben Warnung. Zusätzlich `abk`-Feld als Inline-Schlüssel (institutionelle Zitate „(UN, 2015)") gegen Falsch-Orphans.

### B-TOCLevels — TOC 1 fett UND TOC 2/3 explizit nicht fett (war nur halb umgesetzt)
- **Pitfall:** Der Build setzte nur `TOC 1` fett; `TOC 2`/`TOC 3` existierten nicht und wurden von Word beim Feld-Update selbst angelegt — mit inkonsistenter Fett-Optik. `format-checks.md` behauptete fälschlich „erledigt". Ebene 1 war nicht zuverlässig fett (Notenkriterium).
- **Korrekt:** Build definiert `TOC 1` (fett) + `TOC 2`/`TOC 3` (`bold=False`) explizit. `validate_docx.check_toc_levels` prüft: TOC1 hat `<w:b/>`, TOC2/TOC3 vorhanden + nicht fett. format-checks.md ehrlich korrigiert.

### B-RenderGate — „validate_docx grün" ≠ „Dokument korrekt"
- **Pitfall:** Die stärkst benoteten Vorgaben (7–10 Seiten Textteil, ≥ 0,5 Seite je Unterkapitel, sichtbare Seitenzahlen II/1, optische TOC-Fettung) sind reine Render-Fragen, die der XML-Validator nicht prüfen kann. Die Heuristik Wörter ÷ 250 lag massiv daneben (echter Render ~330/Seite) → Schätzungen 7,6 bis 11,8 Seiten für dasselbe Dokument.
- **Korrekt:** Preflight trennt „XML-verifiziert" von „nur im Render prüfbar" und führt eine VERBINDLICHE Word-Gate-Checkliste (Schritt 2.6: F9-Feldupdate, Seitenzahlen, TOC-Ebene-1 fett, letzte Seite nicht fast leer, 7–10 Seiten). Wortzahl-Richtwert auf ~330 kalibriert und als grobe Schätzung gekennzeichnet.
- **Soft-Messung:** `scripts/measure_pages.py` misst den Textteil real, wenn LibreOffice (soffice) vorhanden ist (Lit-Verz-Anker = LETZTES Vorkommen, robust gegen gefüllten TOC); fehlt LibreOffice, meldet es `RENDER_UNAVAILABLE` und das manuelle Gate greift. Kein harter LibreOffice-Zwang.

### B-GlobStrict — strikte Kapitel-Whitelist statt „*.md minus .prehum."
- **Pitfall:** Der Kapitel-Glob `*.md` minus `.prehum.` zog andere Backups in `final/` mit (`.bak3`, `.precodex.md`, `.precodex2.md`) → als zusätzliche „Kapitel" gerendert.
- **Korrekt:** Strikte Whitelist `kapitel-<Zahl>.md` über `glob("kapitel-*.md")` + Regex `^kapitel-\d+(?:[.\-]\d+)*\.md$`.

### B-JournalURL — Journal ohne DOI braucht URL-Fallback
- **Pitfall:** Der journal-Branch rendert nur `doi`, nicht `url`. Law-/SSRN-Journals ohne DOI (z. B. Arner 2016) verloren ihren stabilen Link.
- **Korrekt:** `elif e.get("url")` als Fallback im journal-Branch.

### B-WorkingPaper — `quelle_typ: working_paper` mit `reihe`/`nummer`
- **Pitfall:** Der report-Branch ignorierte `reihe`/`nummer`; die Reihe musste ins `verlag`-Feld geschmuggelt werden (Reviewer-Pitfall Q1).
- **Korrekt:** Neuer Typ `working_paper` (und `report`) rendern „<Titel>. <Reihe> <Nummer>. <URL>", `doi` als Fallback ohne URL.

### B-SourceCurrency — Quellen-Aktualität als nicht-blockierender Hinweis
- **Pitfall:** Veraltete zeitkritische Quellen (z. B. GSMA-Jahresbericht 2025 statt 2026) fielen nur einem externen Reviewer auf, keinem Skript.
- **Korrekt:** `validate_docx.check_source_currency` meldet report/website-Quellen mit Jahr < aktuellem Jahr (A1) und Treffer von Aktualitäts-Ankern aus preferences.md (A2) als HINWEIS — nie blockierend, separat vom Verstoß-Zähler und ohne Einfluss auf den Exit-Code.

### B-CodexStdin — `codex exec`/`codex review` MUSS stdin auf /dev/null umleiten
- **Pitfall:** `codex exec "$PROMPT" …` ohne `< /dev/null` blockiert im Hintergrund lesend auf stdin (real beobachtet: stundenlanger Hänger im Auto-Hook).
- **Korrekt:** Jeder Codex-Aufruf endet auf `< /dev/null`, dazu `-C "$(pwd)"` und `-s read-only` bei `codex exec`.

### B-ReviewTracking — Kapitel-Änderungen nach /review und /humanize erkennen
- **Pitfall:** Text, der NACH einem /review- oder /humanize-Lauf ergänzt wurde, lief ungeprüft durch; das musste ein Mensch bemerken.
- **Korrekt:** `scripts/review_tracking.py mark <kapitel> <stage>` legt den Body-Hash (ohne Frontmatter) in `output/progress.json` ab; `review_tracking.py check` (Preflight-Schritt 2.7) warnt nicht-blockierend, wenn der aktuelle Hash abweicht. /review und /humanize rufen `mark` am Ende auf.

---

## Prozess-/Workflow-Lessons (Session 2026-06-18)

### P-Render — finales PDF visuell prüfen, nicht nur Validator + Markdown
- **Pitfall:** Validator und Markdown sahen sauber aus; erst im gerenderten PDF fielen eine über zwei Seiten zerrissene Tabelle, eine fehlende Spaltentrennlinie und eine inhaltliche Überzeichnung (s. P-Team) auf. Ohne lokales LibreOffice war die Seitenzahl nur geschätzt.
- **Korrekt:** Vor Abgabe das echte PDF rendern (LibreOffice installieren oder vom User anfordern) und Layout, Tabellen, Seitenumbrüche und Seitenzahl visuell prüfen.

### P-Integrity — kein erfundenes Feedback, keine erfundenen Rollen
- **Pitfall:** Ein externes Modell schlug vor, ein Stakeholder-Feedback (Product Owner/Lead Developer/QA) zu ERFINDEN. Das wäre Fabrikation und widerspricht „keine eigene empirische Erhebung".
- **Korrekt:** Nichts erfinden. Reale Konstellation abbilden (hier: Zwei-Personen-Startup), Personen nur als Rollen. Bei Unsicherheit über die Realität nachfragen statt ausschmücken.

### P-Team-Konsistenz — bei bekannt gewordener realer Teamgröße ALLE Kapitel prüfen
- **Pitfall:** Nach „wir sind nur zu zweit" nur die offensichtliche Stelle korrigiert; eine zweite überzeichnete Rollenbeschreibung (Lead Developer, Frontend, QA, Beirat) blieb stehen und fiel erst im PDF auf.
- **Korrekt:** Wird ein faktischer Anker bekannt (Teamgröße, Tool, Zahl), den GESAMTEN Text dagegen greppen, nicht nur die zuerst genannte Stelle.

### P-Feedback-adversarial — externes Reviewer-Feedback gegen die echten Dateien verifizieren
- **Pitfall:** Externes Feedback war überwiegend gut, aber punktuell falsch: „Literaturverzeichnis unvollständig" stimmte im Ergebnis, war aber in der URSACHE falsch (Quelldaten komplett → Builder-Bug, nicht Quelle).
- **Korrekt:** Jeden Punkt gegen die echten Dateien prüfen, Ursache von Symptom trennen, Fabrikations-Vorschläge ablehnen.

### P-Datei-Locks — vor rm/Umbenennen auf offene Word-Dateien (`~$`) prüfen
- **Pitfall:** Eine DOCX gelöscht, die der User noch in Word offen hatte (Lock-Datei `~$…docx` übersehen). Beim Speichern kann Word die veraltete Datei neu anlegen.
- **Korrekt:** Vor `rm`/Umbenennen auf `~$<name>`-Locks prüfen; umbenennen statt löschen; auf offene Fenster hinweisen.

### P-Abgabename — Dateiname-Datum aus `config.abgabe.datum`, nicht aus dem Build-Tag
- **Pitfall:** Turnitin-DOCX auf dem Vortagsdatum belassen, während Titelblatt/Abgabe das aktuelle Datum trugen.
- **Korrekt:** Den Turnitin-Dateinamen aus `abgabe.datum` ableiten.
