#!/usr/bin/env python3
"""Stil-Linter für Markdown-Kapitel — misst KI-Schreibspuren deterministisch.

Arbeitet auf den Markdown-Quellen (output/phase-05-writing/), NICHT auf der DOCX:
Stil wird an der Quelle geprüft und korrigiert. Ergänzt validate_docx.py
(Format) um die Sprachdimension. Schwellenwerte sind mit
base/guides/academic-writing/satzrhythmus.md synchron zu halten (Guide = Linter).

Checks (Codes L1–L15), Severity nach User-Entscheidung „gemischt":
  BLOCKIEREND (Exit 1 unter --strict):
    L1  Verbotene Wörter        (preferences.md → „Verbotene Wörter")
    L2  Verbotene Floskeln      (preferences.md + Voice-Profil + Default-Liste)
    L3  Em-Dash / Gedankenstrich-Häufung
    L4  Chatbot-Artefakte + projektspezifische Sprach-Pitfalls
  WARNUNG (melden, nie blockieren):
    L5  Konnektor-Kaskade (Folge-Sätze beginnen mit Konnektor)
    L6  Korrelativ-Dichte (nicht nur…sondern / sowohl…als auch)
    L7  Triaden-Dichte (X, Y und Z)
    L8  Satzlängen-Uniformität (CV, Gleichlängen-Serie, Kurzsatz-Anteil)
    L9  Absatz-Uniformität (Wortzahl-CV, identische Satzzahlen)
    L10 Inhaltswort-Wiederholung in benachbarten Sätzen
    L11 Hedging-Stapel
    L12 Selbstreferenz-Budget (Werk-Aggregat, nur --all)
    L13 Satzanfangs-Monotonie
  HINWEIS:
    L14 Passiv-Quote außerhalb des Zielbands
    L15 Statistik (immer im JSON; Konsole mit --stats)

False-Positive-Schutz: direkte Zitate werden maskiert, APA-Klammern vor der
Satz-Segmentierung entfernt, deutsche Abkürzungen geschützt, Unicode-NFC-
Normalisierung (macOS-NFD!), Bindestrich-Komposita zählen als ein Wort.

Aufruf:
  python3 scripts/lint_style.py [pfad ...] [--all] [--json] [--stats]
                                [--strict] [--digest] [--no-profile]

Ohne Pfade: alle Kapitel in output/phase-05-writing/final/ (Fallback draft/).
`--strict`  Exit 1 NUR bei blockierenden Funden (L1–L4). Warnungen blockieren nie.
`--digest`  schreibt output/style-digest.md (Kompakt-Übersicht je Kapitel,
            Input für Writer-Kontext und Gesamtwerk-Review).
"""

import argparse
import json
import re
import statistics
import sys
import unicodedata
from pathlib import Path

# ----- Schwellenwerte (synchron mit satzrhythmus.md) -------------------------

CV_SENTENCE_MIN = 0.35     # L8: Variationskoeffizient Satzlängen pro Kapitel
CV_PARA_MIN = 0.25         # L9: Variationskoeffizient Absatz-Wortzahlen
SHORT_SENT_MAX = 12        # Wörter: „kurzer Satz"
SHORT_RATIO_MIN = 0.10     # L8: Mindestanteil kurzer Sätze
EQUAL_RUN = 3              # L8/L9: so viele gleiche Folge-Elemente sind ein Fund
EQUAL_TOL = 3              # L8: ±Wörter gelten als „gleich lang"
MIN_SENTENCES_FOR_STATS = 8
MIN_PARAS_FOR_STATS = 4
CONNECTOR_PARA_RATIO = 0.30  # L13: max. Anteil Absätze mit Konnektor-Beginn
KORRELATIV_PER_WORDS = 330   # L6: max. 1 Korrelativ-Paar pro ~Seite
TRIAD_PER_FILE = 1           # L7: max. Triaden pro Unterkapitel-Datei
TRIAD_PER_WORK = 4           # L7: max. Triaden im Gesamtwerk (--all)
SELF_REF_MAX = 2             # L12: Selbstreferenzen im Gesamtwerk
HEDGE_PER_SENTENCE = 2       # L11: ab so vielen Abschwächern pro Satz
PASSIV_MIN, PASSIV_MAX = 0.25, 0.55  # L14: Zielband (Voice-Profil: 35–45 %)
GEDANKENSTRICH_PER_PARA = 2  # L3: max. ' – '-Vorkommen pro Absatz (= 1 Einschub-Paar ODER 1 Einzelstrich)

BLOCKING_CODES = {"L1", "L2", "L3", "L4"}
HINT_CODES = {"L14", "L15"}

# ----- Wortlisten -------------------------------------------------------------

CONNECTORS = {
    "zudem", "ferner", "des", "außerdem", "zusätzlich", "darüber",
    "folglich", "somit", "daher", "demnach", "dabei", "hierbei",
    "jedoch", "allerdings", "hingegen", "dennoch", "gleichwohl",
    "weiterhin", "zunächst", "schließlich", "insgesamt",
}
# „des Weiteren" / „darüber hinaus" beginnen mit des/darüber → über Erstwort abgedeckt.

HEDGES = [
    "könnte", "könnten", "möglicherweise", "eventuell", "unter umständen",
    "tendenziell", "gewissermaßen", "in gewisser weise", "vermutlich",
    "wohl", "gegebenenfalls",
]

# Eingebaute Floskel-Blockliste (Voice-Profil §5 + ai-writing-signs Muster 23/27/28).
# preferences.md → „Verbotene Floskeln (Stil-Linter)" ERGÄNZT diese Liste.
DEFAULT_FLOSKELN = [
    "es ist wichtig zu",
    "es ist wichtig, zu",
    "ist es wichtig zu",
    "wichtig zu betonen",
    "es sei angemerkt",
    "es gilt zu beachten",
    "in der heutigen",
    "in der heutigen schnelllebigen",
    "im folgenden wird",
    "im folgenden kapitel",
    "das nächste kapitel beschäftigt sich",
    "das folgende kapitel",
    "zusammenfassend lässt sich festhalten",
    "zusammenfassend lässt sich sagen",
    "vor diesem hintergrund zeigt sich",
    "es wird deutlich, dass",
    "dies führt zu der erkenntnis",
    "von besonderer bedeutung",
    "im kern geht es",
    "aufgrund der tatsache, dass",
    "spielt eine entscheidende rolle",
    "spielt eine zentrale rolle",
    "tauchen wir ein",
    "eintauchen in die welt",
    "die zukunft sieht",
    "zukunft rosig",
    "hier das wichtigste",
    "navigieren durch",
]
FAZIT_EXEMPT = "zusammenfassend lässt sich festhalten"  # 1× im Fazit erlaubt

CHATBOT_ARTIFACTS = [
    "als ki", "als sprachmodell", "ich hoffe, das hilft", "sag bescheid",
    "gerne helfe ich", "lass es mich wissen", "großartige frage",
]

SELF_REF_RE = re.compile(
    r"\b(die vorliegende arbeit|die vorliegende fallstudie|diese fallstudie|"
    r"im rahmen dieser arbeit|im rahmen dieser untersuchung|im rahmen dieser fallstudie)\b",
    re.IGNORECASE,
)

STOPWORDS = {
    "aber", "alle", "allem", "allen", "aller", "alles", "auch", "beim", "bereits",
    "besonders", "bzw", "dabei", "dadurch", "dafür", "damit", "danach", "daneben",
    "daran", "darauf", "daraus", "darin", "davon", "dazu", "dementsprechend",
    "demnach", "denen", "deren", "derselben", "dessen", "deshalb", "deutlich",
    "diese", "diesem", "diesen", "dieser", "dieses", "doch", "durch", "eigenen",
    "einem", "einen", "einer", "eines", "einige", "einigen", "erst", "erste",
    "ersten", "etwa", "folglich", "gegen", "gegenüber", "gemäß", "haben", "hierbei",
    "hierzu", "hingegen", "immer", "indem", "innerhalb", "insbesondere", "jedoch",
    "jeweils", "kann", "keine", "keinen", "können", "lassen", "lässt", "mehr",
    "mehrere", "mittels", "muss", "müssen", "nach", "neben", "nicht", "noch",
    "nur", "ohne", "oder", "seit", "sich", "sind", "sollen", "sollte", "sollten",
    "somit", "sowie", "sowohl", "über", "unter", "während", "weitere", "weiteren",
    "weiterer", "welche", "welchem", "welchen", "welcher", "wenn", "werden",
    "wird", "worden", "wurde", "wurden", "zudem", "zwischen", "zunächst",
    "ebenso", "ebenfalls", "anhand", "aufgrund", "hinsichtlich", "bezüglich",
    "daher", "dennoch", "ferner", "allerdings", "außerdem", "zugleich",
}

ABBREVIATIONS = [
    "z. B.", "z.B.", "d. h.", "d.h.", "u. a.", "u.a.", "u. U.", "u.U.",
    "i. d. R.", "i.d.R.", "bzw.", "vgl.", "ca.", "S.", "Abs.", "Abb.", "Tab.",
    "et al.", "ggf.", "inkl.", "Mio.", "Mrd.", "Nr.", "Kap.", "bspw.", "sog.",
    "evtl.", "etc.", "usw.", "bzgl.", "Dr.", "Prof.", "Aufl.", "Hrsg.", "Jg.",
    "o. J.", "n. d.",
]

WORD_RE = re.compile(r"[\wÀ-ſ]+(?:-[\wÀ-ſ]+)*")
APA_PAREN_RE = re.compile(r"\((?=[^()]*(?:\d{4}|n\. ?d\.))[^()]*\)")
QUOTE_RES = [
    re.compile(r"„[^“”\"]{0,600}[“”\"]"),
    re.compile(r"»[^«]{0,600}«"),
    re.compile(r"\"[^\"]{0,600}\""),
]
EM_DASH = "—"
GEDANKENSTRICH_RE = re.compile(r"\s–\s")  # nur gespreizter Halbgeviertstrich
TRIAD_RE = re.compile(
    r"\b([\wÀ-ſ-]{3,}),\s+([\wÀ-ſ-]{3,})\s+und\s+([\wÀ-ſ-]{3,})\b"
)
PASSIV_RE = re.compile(r"\b(wird|werden|wurde|wurden|worden)\b", re.IGNORECASE)


# ----- Konfiguration lesen -----------------------------------------------------

def _read_config_field(repo_root: Path, dotted_key: str) -> str:
    """Dotted-key-Feld aus config.yaml ohne YAML-Lib (wie validate_docx.py)."""
    cfg_path = repo_root / "config.yaml"
    if not cfg_path.exists():
        return ""
    keys = dotted_key.split(".")
    indent_stack: list = []
    try:
        for raw in cfg_path.read_text(encoding="utf-8").splitlines():
            stripped = raw.lstrip()
            if not stripped or stripped.startswith("#"):
                continue
            depth = (len(raw) - len(stripped)) // 2
            indent_stack = [(d, k) for d, k in indent_stack if d < depth]
            if ":" not in stripped:
                continue
            key, _, value = stripped.partition(":")
            value = value.split("#", 1)[0].strip()
            indent_stack.append((depth, key.strip()))
            if [k for _, k in indent_stack] == keys and value:
                return value.strip().strip('"').strip("'")
    except (OSError, UnicodeDecodeError):
        return ""
    return ""


def _bullet_section(md_text: str, heading_pattern: str) -> list:
    """Bullets unter einer ##-Überschrift; Code-Fences werden übersprungen."""
    m = re.search(
        r"^##+\s*" + heading_pattern + r".*?$(.*?)(?=^##\s|\Z)",
        md_text, re.MULTILINE | re.DOTALL | re.IGNORECASE,
    )
    if not m:
        return []
    body = re.sub(r"```.*?```", "", m.group(1), flags=re.DOTALL)
    body = re.sub(r"<!--.*?-->", "", body, flags=re.DOTALL)
    items = []
    for raw in re.findall(r"^[-*]\s+(.+?)\s*$", body, re.MULTILINE):
        item = raw.split("#", 1)[0].strip().strip("`").strip('"').strip("'").strip()
        if item:
            items.append(item)
    return items


def _profile_floskeln(profile_text: str) -> list:
    """Sichere Teilmenge aus dem Voice-Profil: nur ZITIERTE MEHRWORT-Floskeln.

    Einzelwörter mit Kontext-Qualifizierer („nachhaltig als Schmuckwort") werden
    bewusst NICHT geladen — kontextabhängige Fälle gehören dem LLM-Review, nicht
    einem Blocker. Ellipsen am Ende werden abgeschnitten.
    """
    m = re.search(
        r"^###\s*Verbotene Floskeln.*?$(.*?)(?=^#{2,3}\s|\Z)",
        profile_text, re.MULTILINE | re.DOTALL | re.IGNORECASE,
    )
    if not m:
        return []
    out = []
    for quoted in re.findall(r"[„\"]([^““”\"]{4,80})[““”\"]", m.group(1)):
        phrase = quoted.replace("…", " ").strip(" .").strip()
        if len(phrase.split()) >= 2:
            out.append(phrase)
    return out


def load_lint_config(repo_root: Path, use_profile: bool = True) -> dict:
    prefs_path = repo_root / "preferences.md"
    prefs = prefs_path.read_text(encoding="utf-8") if prefs_path.exists() else ""
    prefs = unicodedata.normalize("NFC", prefs)

    words = _bullet_section(prefs, r"Verbotene W.rter")
    floskeln = [f.casefold() for f in _bullet_section(prefs, r"Verbotene Floskeln")]
    pitfalls = _bullet_section(prefs, r"Sprach-Pitfalls")

    if use_profile:
        profile_rel = _read_config_field(repo_root, "stil.voice_profile")
        candidates = [p for p in (profile_rel, "../voice-samples/voice-profile.md") if p]
        for cand in candidates:
            p = (repo_root / cand).resolve()
            if p.exists():
                floskeln += [
                    f.casefold()
                    for f in _profile_floskeln(
                        unicodedata.normalize("NFC", p.read_text(encoding="utf-8"))
                    )
                ]
                break

    floskeln += [f.casefold() for f in DEFAULT_FLOSKELN]
    # Dedupe, längste zuerst (verhindert Doppel-Funde bei Teilstrings)
    floskeln = sorted(set(floskeln), key=len, reverse=True)

    terms: set = set()
    term_path = repo_root / "output" / "terminology.md"
    if term_path.exists():
        for row in re.findall(
            r"^\|\s*([^|]+?)\s*\|\s*([^|]*?)\s*\|", term_path.read_text(encoding="utf-8"), re.MULTILINE
        ):
            for cell in row:
                cell = cell.strip()
                if cell and not set(cell) <= {"-", ":", " "} and cell.lower() not in ("begriff", "abkürzung"):
                    for w in WORD_RE.findall(cell):
                        terms.add(w.casefold())
    return {"words": words, "floskeln": floskeln, "pitfalls": pitfalls, "terms": terms}


# ----- Text-Vorverarbeitung -----------------------------------------------------

def preprocess(raw: str) -> dict:
    """Zerlegt eine Kapitel-Datei in analysierbare Absätze.

    Rückgabe: {"paras": [ {line, text, sentences: [(text, words)]} ],
               "is_fazit": bool, "headings": [str]}
    Zitate sind maskiert, APA-Klammern entfernt, Frontmatter/Headings/Tabellen raus.
    """
    text = unicodedata.normalize("NFC", raw)
    # YAML-Frontmatter
    fm = re.match(r"\A---\n.*?\n---\n", text, re.DOTALL)
    offset_lines = fm.group(0).count("\n") if fm else 0
    if fm:
        text = text[fm.end():]

    headings = re.findall(r"^#{1,4}\s+(.+?)\s*$", text, re.MULTILINE)
    is_fazit = any(re.search(r"\bfazit\b", h, re.IGNORECASE) for h in headings)

    lines = text.split("\n")
    paras = []
    buf: list = []
    buf_start = 0
    in_fence = False

    def flush():
        nonlocal buf
        if buf:
            paras.append((buf_start + offset_lines + 1, " ".join(buf)))
            buf = []

    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("```"):
            in_fence = not in_fence
            flush()
            continue
        if in_fence or not stripped or stripped.startswith(("#", "|", "<!--", "> ", ">")):
            flush()
            continue
        if not buf:
            buf_start = i
        buf.append(stripped)
    flush()

    out_paras = []
    for line_no, ptext in paras:
        masked = ptext
        for qre in QUOTE_RES:
            masked = qre.sub(" «Zitat» ", masked)
        masked = APA_PAREN_RE.sub(" ", masked)
        masked = re.sub(r"\s{2,}", " ", masked).strip()
        sentences = [
            (s, len(WORD_RE.findall(s)))
            for s in split_sentences(masked)
            if len(WORD_RE.findall(s)) >= 2
        ]
        if sentences:
            out_paras.append({"line": line_no, "text": masked, "sentences": sentences})
    return {"paras": out_paras, "is_fazit": is_fazit, "headings": headings}


def split_sentences(text: str) -> list:
    protected = text
    for abbr in ABBREVIATIONS:
        protected = protected.replace(abbr, abbr.replace(".", "\x00"))
    protected = re.sub(r"(?<=\d)\.(?=\d)", "\x00", protected)  # 1.234 / 3.5
    parts = re.split(r"(?<=[.!?])\s+", protected)
    return [p.replace("\x00", ".").strip() for p in parts if p.strip()]


# ----- Einzel-Checks -------------------------------------------------------------

def _word_hits(word: str, text: str) -> int:
    pat = re.compile(
        r"(?<![\wÀ-ſ-])" + re.escape(word) + r"(?![\wÀ-ſ-])",
        re.IGNORECASE,
    )
    return len(pat.findall(text))


def lint_file(doc: dict, cfg: dict) -> tuple:
    """Alle Datei-lokalen Checks. Rückgabe: (findings, stats, aggregates)."""
    findings: list = []
    paras = doc["paras"]
    all_sentences = [s for p in paras for s in p["sentences"]]
    full_text = " ".join(p["text"] for p in paras)
    total_words = sum(n for _, n in all_sentences)

    def add(code, line, match, hint):
        sev = "blockierend" if code in BLOCKING_CODES else (
            "hinweis" if code in HINT_CODES else "warnung")
        findings.append({"code": code, "severity": sev, "line": line,
                         "match": match, "hint": hint})

    # --- L1 verbotene Wörter
    for w in cfg["words"]:
        for p in paras:
            n = _word_hits(w, p["text"])
            if n:
                add("L1", p["line"], w,
                    f"verbotenes Wort ({n}×) — preferences.md → Verbotene Wörter")

    # --- L2 Floskeln (Fazit-Ausnahme für die eine erlaubte)
    fazit_budget = 1 if doc["is_fazit"] else 0
    for phrase in cfg["floskeln"]:
        for p in paras:
            cnt = p["text"].casefold().count(phrase)
            if not cnt:
                continue
            if phrase == FAZIT_EXEMPT and fazit_budget > 0:
                fazit_budget -= cnt
                if fazit_budget >= 0:
                    continue
                cnt = -fazit_budget
            add("L2", p["line"], phrase,
                "verbotene Floskel (Voice-Profil §5 / preferences.md / Anti-KI-Katalog)")

    # --- L3 Em-Dash + Gedankenstrich-Häufung
    for p in paras:
        if EM_DASH in p["text"]:
            add("L3", p["line"], "—",
                "Em-Dash im Fließtext — durch Komma oder Punkt ersetzen")
        g = len(GEDANKENSTRICH_RE.findall(p["text"]))
        if g > GEDANKENSTRICH_PER_PARA:
            add("L3", p["line"], f"{g}× ' – '",
                "mehr als ein Gedankenstrich-Einschub pro Absatz — Kommas bevorzugen")

    # --- L4 Chatbot-Artefakte + Projekt-Pitfalls
    for needle in CHATBOT_ARTIFACTS:
        for p in paras:
            if needle in p["text"].casefold():
                add("L4", p["line"], needle, "Chatbot-Artefakt — entfernen")
    for needle in cfg["pitfalls"]:
        for p in paras:
            if needle.casefold() in p["text"].casefold():
                add("L4", p["line"], needle,
                    "projektspezifischer Sprach-Pitfall (preferences.md)")

    # --- L5 Konnektor-Kaskade
    for p in paras:
        streak_start = None
        streak = 0
        for idx, (s, _) in enumerate(p["sentences"]):
            first = WORD_RE.findall(s.casefold())
            if first and first[0] in CONNECTORS:
                streak += 1
                if streak == 1:
                    streak_start = idx
            else:
                if streak >= 2:
                    add("L5", p["line"], p["sentences"][streak_start][0][:60],
                        f"{streak} Folge-Sätze beginnen mit Konnektor")
                streak = 0
        if streak >= 2:
            add("L5", p["line"], p["sentences"][streak_start][0][:60],
                f"{streak} Folge-Sätze beginnen mit Konnektor")

    # --- L6 Korrelativ-Dichte
    korrelativ = 0
    for s, _ in all_sentences:
        low = s.casefold()
        if ("sowohl" in low and "als auch" in low) or \
           ("nicht nur" in low and "sondern" in low):
            korrelativ += 1
    allowed = max(1, total_words // KORRELATIV_PER_WORDS)
    if korrelativ > allowed:
        add("L6", paras[0]["line"] if paras else 1, f"{korrelativ} Korrelativ-Paare",
            f"max. {allowed} pro {KORRELATIV_PER_WORDS} Wörter (sowohl…als auch / nicht nur…sondern)")

    # --- L7 Triaden (Datei-Ebene; Werk-Ebene im Aggregat)
    # Bindestrich-Ellipsen („Filter-, Wrapper- und Embedded-Methoden") sind
    # legitimes akademisches Deutsch, keine Dreierregel — ausschließen.
    triads = []
    for p in paras:
        for m in TRIAD_RE.finditer(p["text"]):
            if any(g.endswith("-") for g in m.groups()):
                continue
            triads.append((p["line"], m.group(0)))
    if len(triads) > TRIAD_PER_FILE:
        line, sample = triads[TRIAD_PER_FILE]
        add("L7", line, sample,
            f"{len(triads)} Komma-Triaden in dieser Datei (max. {TRIAD_PER_FILE}; Dreierregel-Tell)")

    # --- L8 Satzlängen-Uniformität
    lengths = [n for _, n in all_sentences]
    stats = {
        "saetze": len(lengths),
        "woerter": total_words,
        "mittel": round(statistics.mean(lengths), 1) if lengths else 0,
        "cv": round(statistics.pstdev(lengths) / statistics.mean(lengths), 3)
        if len(lengths) >= 2 and statistics.mean(lengths) > 0 else None,
        "kurzsatz_anteil": round(
            sum(1 for n in lengths if n <= SHORT_SENT_MAX) / len(lengths), 2)
        if lengths else None,
    }
    if len(lengths) >= MIN_SENTENCES_FOR_STATS:
        if stats["cv"] is not None and stats["cv"] < CV_SENTENCE_MIN:
            add("L8", paras[0]["line"], f"CV={stats['cv']}",
                f"Satzlängen zu gleichförmig (Ziel ≥ {CV_SENTENCE_MIN}, satzrhythmus.md)")
        if stats["kurzsatz_anteil"] < SHORT_RATIO_MIN:
            add("L8", paras[0]["line"],
                f"Kurzsatz-Anteil {int(stats['kurzsatz_anteil']*100)} %",
                f"zu wenige kurze Sätze ≤ {SHORT_SENT_MAX} Wörter (Ziel ≥ {int(SHORT_RATIO_MIN*100)} %)")
        run = 1
        for i in range(1, len(lengths)):
            if abs(lengths[i] - lengths[i - 1]) <= EQUAL_TOL:
                run += 1
                if run == EQUAL_RUN:
                    add("L8", paras[0]["line"],
                        f"{EQUAL_RUN} Folge-Sätze ~{lengths[i]} Wörter",
                        "gleich lange Sätze in Serie — Rhythmus brechen")
            else:
                run = 1

    # --- L9 Absatz-Uniformität
    para_words = [sum(n for _, n in p["sentences"]) for p in paras]
    para_sents = [len(p["sentences"]) for p in paras]
    if len(paras) >= MIN_PARAS_FOR_STATS:
        mean_pw = statistics.mean(para_words)
        cv_p = statistics.pstdev(para_words) / mean_pw if mean_pw else 0
        if cv_p < CV_PARA_MIN:
            add("L9", paras[0]["line"], f"Absatz-CV={round(cv_p, 3)}",
                f"Absatzlängen zu gleichförmig (Ziel ≥ {CV_PARA_MIN})")
        for i in range(len(para_sents) - EQUAL_RUN + 1):
            window = para_sents[i:i + EQUAL_RUN]
            if len(set(window)) == 1:
                add("L9", paras[i]["line"], f"{EQUAL_RUN} Absätze mit je {window[0]} Sätzen",
                    "identische Satzzahl in Folge-Absätzen (MEAL-Takt-Tell)")
                break

    # --- L10 Inhaltswort-Wiederholung in Nachbar-Sätzen
    # Wörter mit ≥ 4 Vorkommen im Kapitel sind de-facto Fachterminologie —
    # konsistente Wiederholung des klarsten Fachbegriffs ist erwünscht
    # (ai-writing-signs Muster 11), nur beiläufige Doppelungen sind ein Fund.
    word_freq: dict = {}
    for w in WORD_RE.findall(full_text):
        wl = w.casefold()
        if len(wl) >= 5:
            word_freq[wl] = word_freq.get(wl, 0) + 1
    frequent_terms = {w for w, n in word_freq.items() if n >= 4}
    l10_count = 0
    for p in paras:
        sents = p["sentences"]
        for i in range(len(sents) - 1):
            w1 = {w.casefold() for w in WORD_RE.findall(sents[i][0]) if len(w) >= 5}
            w2 = {w.casefold() for w in WORD_RE.findall(sents[i + 1][0]) if len(w) >= 5}
            rep = (w1 & w2) - STOPWORDS - cfg["terms"] - frequent_terms - {"zitat"}
            for w in sorted(rep):
                if l10_count < 8:
                    add("L10", p["line"], w,
                        "Inhaltswort in benachbarten Sätzen wiederholt (Fachbegriffe via terminology.md whitelisten)")
                l10_count += 1
    if l10_count > 8:
        add("L10", paras[-1]["line"], f"+{l10_count - 8} weitere",
            "weitere Wiederholungs-Funde (gekürzt)")

    # --- L11 Hedging-Stapel
    for p in paras:
        for s, _ in p["sentences"]:
            low = s.casefold()
            hits = sum(low.count(h) for h in HEDGES)
            if hits >= HEDGE_PER_SENTENCE:
                add("L11", p["line"], s[:60],
                    f"{hits} Abschwächer in einem Satz — einer genügt")

    # --- L13 Satzanfangs-Monotonie
    if len(paras) >= MIN_PARAS_FOR_STATS:
        conn_starts = 0
        for p in paras:
            first = WORD_RE.findall(p["sentences"][0][0].casefold())
            if first and first[0] in CONNECTORS:
                conn_starts += 1
        ratio = conn_starts / len(paras)
        if ratio > CONNECTOR_PARA_RATIO:
            add("L13", paras[0]["line"], f"{conn_starts}/{len(paras)} Absätze",
                f"zu viele Absätze beginnen mit Konnektor (max. {int(CONNECTOR_PARA_RATIO*100)} %)")
    for p in paras:
        firsts = [WORD_RE.findall(s.casefold())[:1] for s, _ in p["sentences"]]
        firsts = [f[0] for f in firsts if f]
        for w in set(firsts):
            if firsts.count(w) >= 3 and w not in ("die", "der", "das"):
                add("L13", p["line"], w,
                    f"gleiches Anfangswort in {firsts.count(w)} Sätzen eines Absatzes")

    # --- L14 Passiv-Quote (Hinweis)
    if len(all_sentences) >= MIN_SENTENCES_FOR_STATS:
        passiv = sum(1 for s, _ in all_sentences if PASSIV_RE.search(s))
        quote = passiv / len(all_sentences)
        stats["passiv_quote"] = round(quote, 2)
        if not (PASSIV_MIN <= quote <= PASSIV_MAX):
            add("L14", paras[0]["line"], f"Passiv-Quote ~{int(quote*100)} %",
                f"außerhalb Zielband {int(PASSIV_MIN*100)}–{int(PASSIV_MAX*100)} % (Voice-Profil: 35–45 %)")

    # Aggregat-Daten für Werk-Checks / Digest
    connectors_hist: dict = {}
    for s, _ in all_sentences:
        first = WORD_RE.findall(s.casefold())
        if first and first[0] in CONNECTORS:
            connectors_hist[first[0]] = connectors_hist.get(first[0], 0) + 1
    aggregates = {
        "triads": len(triads),
        "self_refs": len(SELF_REF_RE.findall(full_text)),
        "connectors": connectors_hist,
        "first_sentence": all_sentences[0][0][:140] if all_sentences else "",
        "last_sentence": all_sentences[-1][0][:140] if all_sentences else "",
        "korrelativ": korrelativ,
    }
    return findings, stats, aggregates


# ----- Werk-Checks (nur --all) ----------------------------------------------------

def work_level_findings(per_file: list) -> list:
    findings = []
    total_triads = sum(f["aggregates"]["triads"] for f in per_file)
    if total_triads > TRIAD_PER_WORK:
        findings.append({
            "code": "L7", "severity": "warnung", "line": 0,
            "match": f"{total_triads} Triaden im Werk",
            "hint": f"max. {TRIAD_PER_WORK} Komma-Triaden pro Werk (Voice-Profil §3)",
        })
    total_refs = sum(f["aggregates"]["self_refs"] for f in per_file)
    if total_refs > SELF_REF_MAX:
        findings.append({
            "code": "L12", "severity": "warnung", "line": 0,
            "match": f"{total_refs} Selbstreferenzen",
            "hint": f"max. {SELF_REF_MAX}x 'Die vorliegende Arbeit/Diese Fallstudie' im Werk",
        })
    return findings


# ----- Digest ---------------------------------------------------------------------

def write_digest(per_file: list, out_path: Path):
    lines = [
        "# Style-Digest (generiert von scripts/lint_style.py --digest)",
        "",
        "Kompakt-Übersicht je Kapitel: Register-Anker für den Writer und den",
        "Gesamtwerk-Review. Wird bei jedem Lauf überschrieben.",
        "",
    ]
    for f in per_file:
        st, ag = f["stats"], f["aggregates"]
        conn = ", ".join(f"{k} ({v}×)" for k, v in
                         sorted(ag["connectors"].items(), key=lambda kv: -kv[1])[:5]) or "—"
        lines += [
            f"## {Path(f['path']).name}",
            "",
            f"- Erster Satz: „{ag['first_sentence']}\"",
            f"- Letzter Satz: „{ag['last_sentence']}\"",
            f"- Sätze: {st['saetze']} · Wörter: {st['woerter']} · Ø Satzlänge: {st['mittel']}"
            f" · CV: {st['cv']} · Kurzsatz-Anteil: {st['kurzsatz_anteil']}",
            f"- Satz-Konnektoren: {conn}",
            f"- Selbstreferenzen: {ag['self_refs']} · Triaden: {ag['triads']}"
            f" · Korrelative: {ag['korrelativ']}",
            "",
        ]
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines), encoding="utf-8")


# ----- Main -----------------------------------------------------------------------

def default_paths(repo_root: Path) -> list:
    final = sorted((repo_root / "output/phase-05-writing/final").glob("*.md"))
    final = [p for p in final if not p.name.endswith(".prehum.md")]
    if final:
        return final
    draft = sorted((repo_root / "output/phase-05-writing/draft").glob("*.md"))
    return [p for p in draft if not p.name.endswith(".prehum.md")]


def main():
    ap = argparse.ArgumentParser(
        description="Stil-Linter für Markdown-Kapitel (L1–L15, gemischte Härte)."
    )
    ap.add_argument("pfade", nargs="*", type=Path, help="Kapitel-Dateien (ohne: alle final/, sonst draft/)")
    ap.add_argument("--all", action="store_true", help="Werk-Aggregate (L7/L12) + alle Kapitel")
    ap.add_argument("--json", action="store_true", help="JSON-Output (für /humanize, /preflight)")
    ap.add_argument("--stats", action="store_true", help="Statistik (L15) auch auf der Konsole")
    ap.add_argument("--strict", action="store_true", help="Exit 1 NUR bei blockierenden Funden (L1–L4)")
    ap.add_argument("--digest", action="store_true", help="output/style-digest.md schreiben")
    ap.add_argument("--no-profile", action="store_true", help="Voice-Profil-Floskeln nicht laden")
    args = ap.parse_args()

    repo_root = Path.cwd()
    paths = list(args.pfade) if args.pfade else default_paths(repo_root)
    paths = [p for p in paths if not p.name.endswith(".prehum.md")]
    if not paths:
        print("⚠ Keine Kapitel-Dateien gefunden (output/phase-05-writing/{final,draft}/*.md).",
              file=sys.stderr)
        return 2
    missing = [p for p in paths if not p.exists()]
    if missing:
        print(f"FEHLER: Datei(en) nicht gefunden: {', '.join(str(m) for m in missing)}",
              file=sys.stderr)
        return 2

    cfg = load_lint_config(repo_root, use_profile=not args.no_profile)

    per_file = []
    for path in paths:
        doc = preprocess(path.read_text(encoding="utf-8"))
        findings, stats, aggregates = lint_file(doc, cfg)
        per_file.append({"path": str(path), "findings": findings,
                         "stats": stats, "aggregates": aggregates})

    work_findings = work_level_findings(per_file) if (args.all or len(paths) > 1) else []

    if args.digest:
        write_digest(per_file, repo_root / "output" / "style-digest.md")

    all_findings = [f for pf in per_file for f in pf["findings"]] + work_findings
    n_block = sum(1 for f in all_findings if f["severity"] == "blockierend")
    n_warn = sum(1 for f in all_findings if f["severity"] == "warnung")
    n_hint = sum(1 for f in all_findings if f["severity"] == "hinweis")

    if args.json:
        print(json.dumps({
            "files": [{"path": pf["path"], "findings": pf["findings"], "stats": pf["stats"]}
                      for pf in per_file],
            "work_findings": work_findings,
            "summary": {"blockierend": n_block, "warnung": n_warn, "hinweis": n_hint},
        }, ensure_ascii=False, indent=2))
    else:
        for pf in per_file:
            name = Path(pf["path"]).name
            fnd = pf["findings"]
            if not fnd:
                print(f"✓ {name}: keine Stil-Funde.")
            else:
                b = sum(1 for f in fnd if f["severity"] == "blockierend")
                w = sum(1 for f in fnd if f["severity"] == "warnung")
                h = sum(1 for f in fnd if f["severity"] == "hinweis")
                print(f"⚠ {name}: {len(fnd)} Stil-Funde ({b} blockierend, {w} Warnungen, {h} Hinweise)")
                for i, f in enumerate(fnd, 1):
                    print(f"  {i:2d}. {f['code']} [{f['severity'].upper()}] Z. {f['line']}: "
                          f"„{f['match']}\" — {f['hint']}")
            if args.stats:
                print(f"     Statistik: {pf['stats']}")
        for f in work_findings:
            print(f"⚠ WERK: {f['code']} [{f['severity'].upper()}] „{f['match']}\" — {f['hint']}")
        print()
        print(f"Gesamt: {n_block} blockierend · {n_warn} Warnungen · {n_hint} Hinweise "
              f"({len(paths)} Datei(en))")
        if n_block:
            print("Blockierende Funde (L1–L4) vor /compile beheben — Codes siehe Docstring.")

    return 1 if (args.strict and n_block) else 0


if __name__ == "__main__":
    sys.exit(main())
