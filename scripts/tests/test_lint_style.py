"""Unit-Tests für scripts/lint_style.py.

Aufruf:  python3 -m unittest discover scripts/tests
Kein pytest, keine Dependencies — stdlib unittest (Framework-Konvention).
"""

import json
import subprocess
import sys
import unicodedata
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import lint_style  # noqa: E402


def run_lint(md_body: str, cfg: dict | None = None, is_fazit: bool = False) -> list:
    """Hilfsfunktion: lintet einen Markdown-Body, gibt Findings zurück."""
    heading = "## 5 Fazit" if is_fazit else "## 3.1 Testkapitel"
    doc = lint_style.preprocess(f"---\nphase: 5\n---\n\n{heading}\n\n{md_body}\n")
    cfg = cfg or {
        "words": ["natürlich", "selbstverständlich", "inhärent", "bekanntlich"],
        "floskeln": sorted(
            {f.casefold() for f in lint_style.DEFAULT_FLOSKELN}, key=len, reverse=True
        ),
        "pitfalls": ["der Single Euro Payments Area"],
        "terms": set(),
    }
    findings, _stats, _agg = lint_style.lint_file(doc, cfg)
    return findings


def codes(findings: list) -> set:
    return {f["code"] for f in findings}


class TestVerboteneWoerter(unittest.TestCase):
    def test_l1_umlaut_und_satzanfang(self):
        f = run_lint("Selbstverständlich ist das Ergebnis korrekt. "
                     "Das Modell ist natürlich fehlerfrei.")
        l1 = [x for x in f if x["code"] == "L1"]
        self.assertEqual({x["match"] for x in l1}, {"selbstverständlich", "natürlich"})

    def test_l1_exakte_wortgrenze_keine_flexion(self):
        # Dokumentiertes Verhalten: "inhärenten" matcht NICHT bei Eintrag "inhärent"
        f = run_lint("Die inhärenten Risiken sind bekannt und messbar dokumentiert.")
        self.assertNotIn("L1", codes(f))

    def test_l1_kein_treffer_in_kompositum(self):
        f = run_lint("Die Natürlichkeitsprüfung läuft; das natürlich-basierte Verfahren nicht.")
        self.assertNotIn("L1", codes(f))

    def test_l1_nfd_eingabe_wird_normalisiert(self):
        nfd = unicodedata.normalize("NFD", "Das ist natürlich ein Problem für alle Beteiligten.")
        f = run_lint(nfd)
        self.assertIn("L1", codes(f))


class TestFloskeln(unittest.TestCase):
    def test_l2_floskel_gefunden(self):
        f = run_lint("Es wird deutlich, dass der Ansatz trägt und die Ziele erreicht werden.")
        self.assertIn("L2", codes(f))

    def test_l2_fazit_ausnahme_erstes_vorkommen_erlaubt(self):
        f = run_lint("Zusammenfassend lässt sich festhalten, dass die Ziele erreicht wurden.",
                     is_fazit=True)
        self.assertNotIn("L2", codes(f))

    def test_l2_fazit_ausnahme_nur_einmal(self):
        body = ("Zusammenfassend lässt sich festhalten, dass A gilt und trägt.\n\n"
                "Zusammenfassend lässt sich festhalten, dass B gilt und trägt.")
        f = run_lint(body, is_fazit=True)
        self.assertIn("L2", codes(f))

    def test_l2_ausserhalb_fazit_blockiert(self):
        f = run_lint("Zusammenfassend lässt sich festhalten, dass A gilt und trägt.")
        self.assertIn("L2", codes(f))

    def test_l2_zitat_maskierung(self):
        f = run_lint('Hanl und Michaelis beschreiben das als „in der heutigen Ökonomie '
                     'zentral" und ordnen es ein (Hanl & Michaelis, 2019).')
        self.assertNotIn("L2", codes(f))


class TestTypografie(unittest.TestCase):
    def test_l3_em_dash_blockiert(self):
        f = run_lint("Das Verfahren ist etabliert — es wird breit eingesetzt und geprüft.")
        self.assertIn("L3", codes(f))

    def test_l3_zwei_gedankenstrich_paare_blockieren(self):
        f = run_lint("Das Verfahren – etabliert seit Jahren – ist verbreitet – und geprüft "
                     "in vielen Studien weltweit.")
        self.assertIn("L3", codes(f))

    def test_l3_ein_gedankenstrich_und_zahlenbereich_ok(self):
        f = run_lint("Der Umfang beträgt 7–10 Seiten und bleibt – wie vorgegeben – stabil.")
        self.assertNotIn("L3", codes(f))


class TestPitfallsUndArtefakte(unittest.TestCase):
    def test_l4_projekt_pitfall(self):
        f = run_lint("Die Regeln der Single Euro Payments Area gelten unverändert weiter.")
        self.assertIn("L4", codes(f))

    def test_l4_chatbot_artefakt(self):
        f = run_lint("Ich hoffe, das hilft bei der weiteren Einordnung der Ergebnisse.")
        self.assertIn("L4", codes(f))


class TestRhythmus(unittest.TestCase):
    def test_l5_konnektor_kaskade(self):
        f = run_lint("Zudem steigt der Aufwand für alle Beteiligten spürbar. "
                     "Ferner sinkt die Qualität der Ergebnisse deutlich. "
                     "Daher braucht es eine neue Lösung im Betrieb.")
        self.assertIn("L5", codes(f))

    def test_l6_korrelativ_dichte(self):
        body = ("Der Ansatz umfasst sowohl technische als auch organisatorische Fragen. "
                "Er betrifft nicht nur die Kosten, sondern auch die Qualität im Betrieb.")
        f = run_lint(body)
        self.assertIn("L6", codes(f))

    def test_l8_uniforme_satzlaengen(self):
        s = "Die Systeme verändern dabei die internen Abläufe vieler Unternehmen deutlich. "
        f = run_lint(s * 10)
        self.assertIn("L8", codes(f))

    def test_l8_varianter_text_ok(self):
        body = ("Die Migration betrifft alle Fachabteilungen des Unternehmens gleichermaßen "
                "und verändert deren tägliche Arbeit spürbar. Das ist messbar. "
                "Erste Auswertungen zeigen eine deutliche Verschiebung der Aufwände hin zu "
                "koordinierenden Tätigkeiten mit externem Bezug. Kurz gesagt sinkt die Routinelast. "
                "Ob dieser Effekt dauerhaft trägt, hängt von der Qualifizierung der Beschäftigten "
                "und der Stabilität der neuen Prozesse im internationalen Umfeld ab. "
                "Offen bleibt die Kostenfrage. "
                "Verlässliche Zahlen zur Gesamtbetriebsrechnung liegen erst nach dem zweiten "
                "vollständigen Geschäftsjahr vor und erlauben dann einen belastbaren Vergleich.")
        l8 = [x for x in run_lint(body) if x["code"] == "L8"]
        self.assertEqual(l8, [])

    def test_l10_wiederholung_und_frequenz_whitelist(self):
        # "Datenbestand" nur 2× → Fund; "Cluster" 4× → de-facto Terminologie, kein Fund
        body = ("Der Datenbestand umfasst dreitausend Zeilen mit vielen Merkmalen im Detail. "
                "Der Datenbestand wurde zuvor umfassend bereinigt und geprüft im Vorfeld. "
                "Cluster bilden dabei die zentrale Einheit der weiteren Analyse und Bewertung. "
                "Jedes Cluster erhält eine eigene fachliche Interpretation durch das Projektteam. "
                "Kleine Cluster werden mit benachbarten Gruppen zusammengelegt nach Bedarf. "
                "Große Cluster teilt das Verfahren in homogene Untergruppen mit klaren Grenzen.")
        l10 = [x for x in run_lint(body) if x["code"] == "L10"]
        self.assertEqual({x["match"] for x in l10}, {"datenbestand"})

    def test_l11_hedging_stapel(self):
        f = run_lint("Dies könnte möglicherweise eventuell zu erheblichen Problemen führen.")
        self.assertIn("L11", codes(f))


class TestKonfigParser(unittest.TestCase):
    def test_bullet_section_ignoriert_code_fences(self):
        md = ("## Sprach-Pitfalls (Projekt)\n\nText.\n\n```\n- nur ein Beispiel\n```\n\n"
              "- echter Eintrag\n\n## Nächste Sektion\n\n- fremder Eintrag\n")
        self.assertEqual(lint_style._bullet_section(md, r"Sprach-Pitfalls"),
                         ["echter Eintrag"])

    def test_profile_floskeln_nur_zitierte_mehrwort(self):
        prof = ("### Verbotene Floskeln\n"
                '- "Es ist wichtig …" / "Es sei angemerkt, dass …"\n'
                "- `ganzheitlich`, `zukunftsweisend` als Schmuckwörter\n")
        got = lint_style._profile_floskeln(prof)
        self.assertIn("Es ist wichtig", got)
        self.assertNotIn("ganzheitlich", [g.casefold() for g in got])

    def test_apa_klammern_entfernt_vor_satzsplit(self):
        doc = lint_style.preprocess(
            "## 2.1 T\n\nDas Modell trägt weit (Hastie et al., 2009, S. 12). "
            "Die Anwendung folgt daraus direkt und unmittelbar."
        )
        self.assertEqual(len(doc["paras"][0]["sentences"]), 2)
        self.assertNotIn("Hastie", doc["paras"][0]["text"])

    def test_abkuerzungen_splitten_nicht(self):
        doc = lint_style.preprocess(
            "## 2.1 T\n\nDies gilt z. B. für kleine Betriebe mit knappen Budgets im Alltag."
        )
        self.assertEqual(len(doc["paras"][0]["sentences"]), 1)


class TestCLI(unittest.TestCase):
    def _write_tmp(self, name: str, body: str) -> Path:
        import tempfile
        d = Path(tempfile.mkdtemp(prefix="lint_style_test_"))
        p = d / name
        p.write_text(body, encoding="utf-8")
        return p

    def test_exit_0_bei_nur_warnungen_strict(self):
        p = self._write_tmp("2-1.md", "## 2.1 T\n\n" +
                            ("Die Systeme verändern die internen Abläufe vieler Firmen deutlich. " * 10))
        r = subprocess.run(
            [sys.executable, "scripts/lint_style.py", str(p), "--strict", "--no-profile"],
            cwd=REPO_ROOT, capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_exit_1_bei_blocker_strict_und_json_schema(self):
        p = self._write_tmp("2-2.md", "## 2.2 T\n\nEs wird deutlich, dass der Ansatz trägt "
                                      "und die Ziele im Betrieb erreicht werden.")
        r = subprocess.run(
            [sys.executable, "scripts/lint_style.py", str(p), "--strict", "--json", "--no-profile"],
            cwd=REPO_ROOT, capture_output=True, text=True)
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        data = json.loads(r.stdout)
        self.assertGreaterEqual(data["summary"]["blockierend"], 1)
        self.assertIn("findings", data["files"][0])
        self.assertIn("stats", data["files"][0])

    def test_exit_2_ohne_dateien(self):
        r = subprocess.run(
            [sys.executable, "scripts/lint_style.py", "gibt-es-nicht.md", "--no-profile"],
            cwd=REPO_ROOT, capture_output=True, text=True)
        self.assertEqual(r.returncode, 2)

    def test_prehum_wird_uebersprungen(self):
        p = self._write_tmp("2-3.prehum.md", "## 2.3 T\n\nEs wird deutlich, dass X gilt.")
        r = subprocess.run(
            [sys.executable, "scripts/lint_style.py", str(p), "--no-profile"],
            cwd=REPO_ROOT, capture_output=True, text=True)
        self.assertEqual(r.returncode, 2)  # keine analysierbaren Dateien übrig


if __name__ == "__main__":
    unittest.main()
