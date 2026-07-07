#!/usr/bin/env python3
"""Review-/Humanize-Tracking je Kapitel (Pitfall: nachträglich ergänzter Text).

Problem: Text, der NACH einem /review- oder /humanize-Lauf in ein Kapitel
ergänzt wird, läuft ungeprüft durch — das musste bisher ein Mensch bemerken.

Lösung: Nach /review und /humanize legt `mark` den Body-Hash des Kapitels in
output/progress.json ab. `check` (von /preflight aufgerufen) vergleicht den
aktuellen Body-Hash mit dem zuletzt geprüften und warnt, wenn ein Kapitel seit
seinem letzten /review oder /humanize verändert wurde. Nicht blockierend.

Gehasht wird nur der Fließtext OHNE YAML-Frontmatter, damit reine Metadaten-
Änderungen (z. B. Status-Feld) keinen Fehlalarm auslösen.

Aufruf:
  python3 scripts/review_tracking.py mark <kapitel-pfad> <stage>   # stage: review | humanize
  python3 scripts/review_tracking.py check [--project DIR]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime
from pathlib import Path

CHAPTER_RE = re.compile(r"^kapitel-\d+(?:[.\-]\d+)*\.md$")
STAGES = ("review", "humanize")


def project_root(start: Path) -> Path:
    """Nächstgelegenes Verzeichnis mit config.yaml (sonst start selbst)."""
    for d in (start, *start.parents):
        if (d / "config.yaml").exists():
            return d
    return start


def progress_path(project: Path) -> Path:
    return project / "output" / "progress.json"


def body_hash(chapter: Path) -> str:
    """SHA-256 des Kapiteltexts ohne führenden YAML-Frontmatter-Block."""
    text = chapter.read_text(encoding="utf-8")
    body = re.sub(r"^---\n.*?\n---\n", "", text, count=1, flags=re.DOTALL)
    return hashlib.sha256(body.encode("utf-8")).hexdigest()


def load_progress(project: Path) -> dict:
    p = progress_path(project)
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text(encoding="utf-8")) or {}
    except (json.JSONDecodeError, OSError):
        return {}


def cmd_mark(args) -> int:
    chapter = Path(args.chapter).resolve()
    if not chapter.exists():
        print(f"FEHLER: Kapitel nicht gefunden: {chapter}", file=sys.stderr)
        return 2
    if args.stage not in STAGES:
        print(f"FEHLER: stage muss {STAGES} sein, war '{args.stage}'", file=sys.stderr)
        return 2

    project = project_root(chapter.parent)
    p = progress_path(project)
    # Bestehende progress.json NICHT zerstören, wenn sie unparsebar ist.
    if p.exists():
        try:
            data = json.loads(p.read_text(encoding="utf-8")) or {}
        except (json.JSONDecodeError, OSError):
            print(f"FEHLER: {p} ist kein gültiges JSON — nicht überschrieben.", file=sys.stderr)
            return 2
    else:
        data = {}

    tracking = data.setdefault("review_tracking", {})
    entry = tracking.setdefault(chapter.name, {})
    entry[args.stage] = {
        "hash": body_hash(chapter),
        "mtime": chapter.stat().st_mtime,
        "at": datetime.now().isoformat(timespec="seconds"),
    }
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"✓ {chapter.name}: {args.stage} markiert (Hash {entry[args.stage]['hash'][:12]}…).")
    return 0


def cmd_check(args) -> int:
    project = project_root(Path(args.project).resolve())
    data = load_progress(project)
    tracking = data.get("review_tracking", {})
    chap_dir = project / "output" / "phase-05-writing" / "final"

    if not tracking:
        print("Review-Tracking: keine Markierungen in progress.json (noch kein /review oder /humanize).")
        return 0

    stale = []
    for chapter in sorted(p for p in chap_dir.glob("kapitel-*.md") if CHAPTER_RE.match(p.name)):
        rec = tracking.get(chapter.name)
        if not rec:
            continue
        current = body_hash(chapter)
        for stage in STAGES:
            info = rec.get(stage)
            if info and info.get("hash") and info["hash"] != current:
                stale.append((chapter.name, stage, info.get("at", "?")))

    if not stale:
        print("✓ Review-Tracking: kein Kapitel seit dem letzten /review oder /humanize verändert.")
        return 0

    print(f"⚠ Review-Tracking: {len(stale)} Kapitel seit Prüfung verändert (nicht blockierend):")
    for name, stage, at in stale:
        print(f"   - {name}: seit /{stage} ({at}) geändert — erneut /{stage} erwägen.")
    return 0


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Review-/Humanize-Tracking je Kapitel.")
    sub = ap.add_subparsers(dest="command", required=True)
    m = sub.add_parser("mark", help="Kapitel nach /review oder /humanize markieren")
    m.add_argument("chapter", help="Pfad zur Kapiteldatei (kapitel-X.md)")
    m.add_argument("stage", help="review | humanize")
    c = sub.add_parser("check", help="prüfen, ob Kapitel seit Markierung geändert wurden")
    c.add_argument("--project", default=".", help="Projektverzeichnis (Default: cwd)")
    args = ap.parse_args(argv[1:])
    if args.command == "mark":
        return cmd_mark(args)
    return cmd_check(args)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
