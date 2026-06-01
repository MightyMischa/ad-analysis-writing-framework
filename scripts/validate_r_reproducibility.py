#!/usr/bin/env python3
"""R-Reproduzierbarkeits-Validator.

Prueft fuer empirisch-quantitative Arbeiten mit R-Toolchain:

  R1  Alle R-Skripte in scripts/r/ fuehren ohne Fehler durch
  R2  Datenpfade sind portabel (relative Pfade, keine hartkodierten Heimverzeichnisse)
  R3  Saatwerte (set.seed) sind gesetzt fuer Reproduzierbarkeit zufallsabhaengiger Operationen
  R4  Plot- und Tabellen-Outputs landen in einem konsistenten Output-Verzeichnis
  R5  Jeder generierte Plot/jede Tabelle wird im Volltext der Arbeit referenziert (Citation-Hook)

Aufruf:
  python3 scripts/validate_r_reproducibility.py [--strict]

Aktiv nur wenn config.yaml -> r_toolchain.enabled: true.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path
from typing import Iterable


def _read_config_field(repo_root: Path, dotted_key: str) -> str:
    cfg_path = repo_root / "config.yaml"
    if not cfg_path.exists():
        return ""
    keys = dotted_key.split(".")
    indent_stack: list[tuple[int, str]] = []
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
            key = key.strip()
            value = value.strip()
            indent_stack.append((depth, key))
            if [k for _, k in indent_stack] == keys and value:
                return value.strip().strip('"').strip("'")
    except (OSError, UnicodeDecodeError):
        return ""
    return ""


def _is_truthy(s: str) -> bool:
    return s.lower() in ("true", "yes", "1", "on")


def find_r_scripts(scripts_dir: Path) -> list[Path]:
    if not scripts_dir.exists():
        return []
    return sorted(scripts_dir.rglob("*.R")) + sorted(scripts_dir.rglob("*.r"))


# ----- R1: Skripte ausfuehrbar? ---------------------------------------------


def check_r_executable(scripts: Iterable[Path]) -> list[str]:
    """Checkt nur Syntax via Rscript --vanilla -e 'parse(file=...)'.

    Vollausfuehrung waere zu teuer; Syntax-Check fangt grobe Tipper.
    Falls Rscript nicht installiert: skippe, mit Hinweis.
    """
    issues: list[str] = []
    rscript = subprocess.run(
        ["which", "Rscript"], capture_output=True, text=True, check=False
    )
    if rscript.returncode != 0:
        return ["R1: Rscript nicht installiert. Skippe Syntax-Check. (brew install r)"]
    for script in scripts:
        result = subprocess.run(
            [
                "Rscript",
                "--vanilla",
                "-e",
                f"tryCatch(parse(file='{script}'), error = function(e) {{ cat(conditionMessage(e)); quit(status=1) }})",
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            err = (result.stderr or result.stdout).strip()
            issues.append(f"R1: Syntaxfehler in {script.name}: {err[:200]}")
    return issues


# ----- R2: Portabilitaet ----------------------------------------------------

NON_PORTABLE_PATTERNS = [
    re.compile(r"['\"](/Users/[^'\"]+|/home/[^'\"]+|C:\\\\[^'\"]+)['\"]"),
    re.compile(r"setwd\s*\(\s*['\"](?!\.)[^'\"]+['\"]"),
]


def check_portability(scripts: Iterable[Path]) -> list[str]:
    issues: list[str] = []
    for script in scripts:
        try:
            text = script.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        for line_no, line in enumerate(text.splitlines(), 1):
            stripped = line.strip()
            if stripped.startswith("#"):
                continue
            for pat in NON_PORTABLE_PATTERNS:
                m = pat.search(line)
                if m:
                    issues.append(
                        f"R2: Nicht-portabler Pfad in {script.name}:{line_no}: «{stripped[:80]}»"
                    )
                    break
    return issues


# ----- R3: Saatwerte --------------------------------------------------------

RANDOM_API_RE = re.compile(r"\b(sample|rnorm|runif|rbinom|rpois|rgamma|sample\.int)\s*\(")
SET_SEED_RE = re.compile(r"\bset\.seed\s*\(\s*\d+\s*\)")


def check_seeds(scripts: Iterable[Path]) -> list[str]:
    issues: list[str] = []
    for script in scripts:
        try:
            text = script.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        if RANDOM_API_RE.search(text) and not SET_SEED_RE.search(text):
            issues.append(
                f"R3: {script.name} verwendet Zufalls-API (sample/rnorm/...) ohne set.seed() - nicht reproduzierbar."
            )
    return issues


# ----- R4: Output-Verzeichnis -----------------------------------------------

OUTPUT_WRITE_RE = re.compile(
    r"\b(ggsave|write\.csv|write\.csv2|write\.table|saveRDS|png|pdf|jpeg|svg)\s*\(([^)]+)\)"
)


def check_output_dir(
    scripts: Iterable[Path], expected_dir: str
) -> list[str]:
    issues: list[str] = []
    expected = Path(expected_dir).as_posix().rstrip("/")
    for script in scripts:
        try:
            text = script.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        for m in OUTPUT_WRITE_RE.finditer(text):
            args = m.group(2)
            # Erste Path-aehnliche Argument-Stelle pruefen
            path_arg = re.search(r"['\"]([^'\"]+\.(?:png|jpg|jpeg|pdf|csv|rds|tsv|svg))['\"]", args)
            if not path_arg:
                continue
            target = path_arg.group(1).replace("\\", "/")
            if not target.startswith(expected):
                issues.append(
                    f"R4: Output in {script.name} schreibt nach «{target}», erwartet unter «{expected}/»"
                )
    return issues


# ----- R5: Citation-Hook ----------------------------------------------------


def gather_chapter_text(repo_root: Path) -> str:
    """Sammle Volltext aus phase-05-writing/final/*.md (oder docx falls vorhanden)."""
    final_dir = repo_root / "output" / "phase-05-writing" / "final"
    if final_dir.exists():
        return "\n".join(
            f.read_text(encoding="utf-8", errors="ignore")
            for f in sorted(final_dir.glob("*.md"))
        )
    # Fallback: aus DOCX
    docx_glob = repo_root / "output" / "phase-07-docx"
    if docx_glob.exists():
        candidates = sorted(docx_glob.glob("*.docx"), key=lambda p: p.stat().st_mtime, reverse=True)
        if candidates:
            try:
                from docx import Document  # noqa: import-late
                doc = Document(str(candidates[0]))
                return "\n".join(p.text for p in doc.paragraphs)
            except Exception:
                return ""
    return ""


PLOT_FILENAME_RE = re.compile(
    r"['\"]([\w\-./]+\.(?:png|jpg|jpeg|pdf|svg))['\"]"
)


def check_citation_hook(
    scripts: Iterable[Path], chapter_text: str
) -> list[str]:
    """Pro Plot-Datei pruefen, ob ihr Stem im Kapitel-Volltext genannt wird
    (z. B. als Caption „Abbildung 3: …" oder via Verweis auf Dateinamen).
    """
    if not chapter_text:
        return []
    issues: list[str] = []
    plot_files: set[str] = set()
    for script in scripts:
        try:
            text = script.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        for m in PLOT_FILENAME_RE.finditer(text):
            stem = Path(m.group(1)).stem
            plot_files.add(stem)
    for stem in sorted(plot_files):
        if stem not in chapter_text and stem.replace("_", "-") not in chapter_text:
            issues.append(
                f"R5: Plot/Output «{stem}» nicht im Volltext referenziert — Abbildung/Tabelle einbauen oder Skript-Output entfernen."
            )
    return issues


# ----- Main ------------------------------------------------------------------


def main() -> int:
    ap = argparse.ArgumentParser(description="R-Reproduzierbarkeits-Validator")
    ap.add_argument("--strict", action="store_true", help="Exit 1 bei Funden")
    args = ap.parse_args()

    repo_root = Path.cwd()
    enabled = _read_config_field(repo_root, "r_toolchain.enabled")
    if not _is_truthy(enabled):
        print("R-Toolchain ist deaktiviert (config.yaml: r_toolchain.enabled). Skip.")
        return 0

    scripts_dir = Path(
        _read_config_field(repo_root, "r_toolchain.scripts_dir") or "scripts/r"
    )
    outputs_dir = (
        _read_config_field(repo_root, "r_toolchain.outputs_dir") or "output/r-results"
    )

    scripts = find_r_scripts(scripts_dir)
    if not scripts:
        print(f"⚠ Keine R-Skripte in {scripts_dir}/ gefunden.")
        return 0

    print(f"Gefundene R-Skripte: {len(scripts)} in {scripts_dir}/\n")

    issues: list[str] = []
    issues.extend(check_r_executable(scripts))
    issues.extend(check_portability(scripts))
    issues.extend(check_seeds(scripts))
    issues.extend(check_output_dir(scripts, outputs_dir))

    citation_hook_active = _is_truthy(
        _read_config_field(repo_root, "r_toolchain.citation_hook")
    )
    if citation_hook_active:
        chapter_text = gather_chapter_text(repo_root)
        issues.extend(check_citation_hook(scripts, chapter_text))

    if not issues:
        print("✓ R-Toolchain: keine Reproduzierbarkeitsprobleme.")
        return 0

    print(f"⚠ R-Toolchain: {len(issues)} Verstoesse")
    print()
    for i, msg in enumerate(issues, 1):
        print(f"  {i:2d}. {msg}")
    print()
    print("Codes: R1=Syntax, R2=Portabilitaet, R3=Saatwerte, R4=Output-Pfad, R5=Citation-Hook")
    return 1 if args.strict else 0


if __name__ == "__main__":
    sys.exit(main())
