---
globs: ["output/**/*.md"]
---

# Anti-KI-Regelwerk (Signs of AI Writing)

Katalog typischer Anzeichen KI-generierten Schreibens und ihrer Korrektur. Grundlage ist der von WikiProject AI Cleanup gepflegte Leitfaden „Signs of AI writing" (Wikipedia), uebersetzt und an das **wissenschaftliche Deutsch der IU** angepasst.

Verwendung:
- Der Skill `/humanize` wendet diesen Katalog aktiv an (umschreiben).
- Der Agent `reviewer-ai-style` prueft Kapitel gegen diesen Katalog (melden).

## Akademische Leitplanken (WICHTIG, gelten ueber allem)

Die Originalmuster stammen aus Blog-/Enzyklopaedie-Kontext. Beim Entfernen von KI-Spuren in einer **Pruefungsleistung** gelten zusaetzlich diese Grenzen — sie haben Vorrang vor jeder Einzelregel unten:

1. **Register bleibt wissenschaftlich.** Ziel ist natuerliche, abwechslungsreiche, konkrete *akademische* Prosa — nicht Umgangssprache und nicht Blog-Ton. „Natuerlicher" heisst hier nicht „lockerer".
2. **Keine Ich-Form.** Niemals zu „ich", „wir", „man" umschreiben. Unpersoenlich/Passiv bleibt korrekt (z. B. „Es laesst sich argumentieren …", „Unter X versteht man …").
3. **Zitate sind unantastbar.** Quellenbelege (APA) werden NIE entfernt, verschoben oder abgeschwaecht. Wo der Originalkatalog „vage Zuschreibung durch konkrete Quelle ersetzen" sagt, heisst das in der Arbeit: Beleg **behalten/staerken**, niemals streichen.
4. **Keine Fakten/Zahlen aendern.** `/humanize` ist eine reine Stilbearbeitung. Inhalte, Zahlen, Argumente und ihre Reihenfolge bleiben identisch.
5. **Vorrang-Reihenfolge bei Konflikt:** `voice-samples/voice-profile.md` + dieses Regelwerk > `.claude/rules/writing-style.md`.

## Inhaltliche Muster

| # | Muster | Vorher | Nachher (akademisch) |
|---|---|---|---|
| 1 | Bedeutungs-Aufblaehung | „markiert einen Wendepunkt in der Evolution von …" | „wurde 1989 zur Erhebung regionaler Statistiken eingefuehrt" |
| 2 | Renommee-Name-Dropping | „zitiert in NYT, BBC, FT und The Hindu" | konkrete, belegte Einzelaussage statt Markenaufzaehlung |
| 3 | Oberflaechliche -end/-ung-Analysen | „symbolisierend … widerspiegelnd … verdeutlichend …" | streichen oder mit belegter Aussage ausfuellen |
| 4 | Werbe-/Hochglanzsprache | „eingebettet in die atemberaubende Region" | „liegt in der Region Gonder" |
| 5 | Vage Zuschreibungen | „Experten gehen davon aus, dass es eine zentrale Rolle spielt" | mit konkretem Beleg: „Nach Hollensen (2020) …" — **Beleg behalten, nie streichen** |
| 6 | Floskelhafte „Herausforderungen" | „Trotz Herausforderungen … floriert weiterhin" | konkrete, belegte Fakten zur tatsaechlichen Schwierigkeit |

## Sprachliche Muster

| # | Muster | Vorher | Nachher (akademisch) |
|---|---|---|---|
| 7 | KI-Vokabular | „ein Beleg fuer … die Landschaft … nahtlos … verdeutlichend" | praezise Fachsprache; leere Schlagwoerter streichen |
| 8 | Kopula-Vermeidung | „dient als … fungiert als … weist auf" | „ist … hat", wo es klarer ist |
| 9 | Negative Parallelismen / nachgestellte Verneinung | „Es ist nicht nur X, sondern Y", „…, ohne Raten" | Aussage direkt formulieren |
| 10 | Dreierregel (rule of three) | „Innovation, Inspiration und Erkenntnis" | natuerliche Anzahl; nicht jede Aufzaehlung auf drei zwingen |
| 11 | Synonym-Karussell | „Protagonist … Hauptfigur … zentrale Gestalt … Held" | denselben Fachbegriff konsistent wiederholen, wenn er am klarsten ist |
| 12 | Falsche Spannweiten | „vom Urknall bis zur dunklen Materie" | Themen direkt benennen |
| 13 | Passiv / subjektlose Fragmente | „Keine Konfiguration noetig" | Akteur nennen, wo es hilft — **aber: wiss. Passiv ist erlaubt und oft korrekt** (Ausnahme zu Bladers Original) |

## Stilistische Muster

| # | Muster | Vorher | Nachher (akademisch) |
|---|---|---|---|
| 14 | Gedankenstrich-Haeufung | „Institutionen — nicht die Menschen — doch das setzt sich fort —" | Kommas oder Punkte (deckt sich mit `writing-style.md`) |
| 15 | Fett-Uebernutzung | „**OKRs**, **KPIs**, **BMC**" | „OKRs, KPIs, BMC" |
| 16 | Inline-Header-Listen | „**Leistung:** Die Leistung stieg" | in Fliesstext aufloesen (passt zur IU-Regel: keine Bulletpoints) |
| 17 | Title-Case-Ueberschriften | „Strategische Verhandlungen Und Partnerschaften" | normale Gross-/Kleinschreibung |
| 18 | Emojis | Emoji-Marker vor Ueberschriften | entfernen |
| 19 | Typografische Anfuehrung uneinheitlich | gemischte gerade/typografische Zeichen | einheitlich nach Vorlage |
| 26 | Bindestrich-Wortpaare | „cross-funktional, daten-getrieben, kunden-orientiert" | gaengige Paare ohne Bindestrich, wo zulaessig |
| 27 | Autoritaets-Floskeln | „Im Kern geht es darum, dass …" | Aussage direkt formulieren |
| 28 | Signpost-Ankuendigungen | „Tauchen wir ein", „Hier das Wichtigste" | mit dem Inhalt beginnen |
| 29 | Fragment-Ueberschriften | Ueberschrift + nachgeschobener Halbsatz | die Ueberschrift fuer sich stehen lassen |

## Kommunikations-Muster

| # | Muster | Vorher | Nachher (akademisch) |
|---|---|---|---|
| 20 | Chatbot-Artefakte | „Ich hoffe, das hilft! Sag Bescheid, wenn …" | vollstaendig entfernen |
| 21 | Cutoff-Disclaimer | „Soweit die verfuegbaren Quellen erkennen lassen …" | Quelle suchen/belegen oder Satz streichen |
| 22 | Sykophantischer Ton | „Grossartige Frage! Du hast voellig recht!" | entfernen (in Fliesstext selten; in Chat-Resten pruefen) |

## Fuell- und Hedging-Muster

| # | Muster | Vorher | Nachher (akademisch) |
|---|---|---|---|
| 23 | Fuellfloskeln | „im Rahmen von", „aufgrund der Tatsache, dass" | „bei", „weil" |
| 24 | Uebermaessiges Hedging | „koennte moeglicherweise eventuell" | „kann" / „duerfte" |
| 25 | Generische Schluesse | „Die Zukunft sieht rosig aus" | konkrete, belegte Aussage oder konkreter Ausblick |

## Rhetorische Muster (Ergaenzung aus plain-writing)

Vier zusaetzliche Muster, extrahiert aus shreyashankar/plain-writing-skill und an wiss. Deutsch angepasst. Sie ergaenzen die Punkte oben; bei Konflikt gelten die Akademischen Leitplanken.

| # | Muster | Vorher | Nachher (akademisch) |
|---|---|---|---|
| 30 | Analogien & Bildsprache | „Die Blockchain fungiert als Brueckentechnologie, vergleichbar mit einem Hauptbuch, das niemandem gehoert" | Sachverhalt literal benennen: „In einer Blockchain fuehren alle Teilnehmer dasselbe, fortlaufend verkettete Transaktionsregister (Nakamoto, 2008)" |
| 31 | Gestapelte rhetorische Fragen | „Was bedeutet das fuer die Praxis? Und wie laesst sich dieser Befund einordnen?" | Aussage direkt formulieren: „Fuer die Praxis ergeben sich daraus zwei Konsequenzen …" |
| 32 | Reveal-Doppelpunkt | „Ein Befund sticht hervor: Die Adaptionsrate steigt" | Doppelpunkt nur fuer echte Aufzaehlung/Definition; sonst eigenstaendiger Satz: „Die Adaptionsrate steigt deutlich (Autor, Jahr)" |
| 33 | Dramatischer Pivot | „Der Ansatz gilt als etabliert. Doch er greift zu kurz." (Aufbau, dann Untergrabung) | vollstaendige Aussage in einem Zug; echte Einschraenkung sachlich und belegt: „Der Ansatz ist etabliert, vernachlaessigt aber X (Autor, Jahr)" |

### Akademische Nuance zu 30–33

- **30 Analogien:** Eine einzelne, fachlich uebliche Veranschaulichung kann zulaessig sein, wenn sie einen Begriff praezisiert (z. B. ein in der Fachliteratur gaengiger Vergleich). KI-typisch und zu streichen ist die *dekorative* Metapher, die nichts erklaert. Beruehrt teils Muster 9 (negative Parallelismen, „nicht nur X, sondern Y").
- **31 Fragen:** Eine einzelne, sachlich gestellte Leitfrage (etwa die Forschungsfrage selbst) ist erlaubt. KI-typisch ist das *Stapeln* zweier oder dreier Fragen als Stilmittel.
- **32 Doppelpunkt:** Deckt sich mit `writing-style.md` („selten Doppelpunkte"). Erlaubt bleibt der Doppelpunkt vor echten Aufzaehlungen und Definitionen (vgl. Muster 1 in grundprinzipien: „[Begriff] ([Abk.]) bezeichnet …").
- **33 Pivot:** Echte kritische Wuerdigung („einschraenkend ist anzumerken …", belegt) ist erwuenscht und kein Pivot. Gemeint ist nur der *rhetorische* Spannungsaufbau ohne inhaltlichen Mehrwert.

## Querbezug

Mehrere Punkte ueberschneiden sich mit `.claude/rules/writing-style.md` (Gedankenstriche, schwache Verben, Nominalisierungen, Wortwiederholungen, keine Uebertreibungen). Dieses Regelwerk ergaenzt sie um die KI-spezifischen Muster (1–12, 20–22, 27–33) und die akademischen Leitplanken oben.

## Quellen

- Wikipedia: „Signs of AI writing" (WikiProject AI Cleanup) — Primaerquelle
- Adaption: blader/humanizer (MIT-Lizenz), an wiss. Deutsch + IU-Register angepasst
- Muster 30–33: shreyashankar/plain-writing-skill, an wiss. Deutsch + IU-Register angepasst
