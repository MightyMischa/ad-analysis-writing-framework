#!/usr/bin/env python3
"""Deklarative DOCX-Punkt-Patches aus einer YAML-Datei.

Ersetzt das Muster „pro Reviewer-Feedback ein generiertes Python-Skript"
(base/templates/feedback-patch.py.template) durch wiederverwendbare,
deklarative Patches. Kann im Gegensatz zur alten Vorlage auch Substrings
ersetzen, die über mehrere Runs verteilt sind (Formatierung des ersten
betroffenen Runs bleibt erhalten).

Aufruf:
  python3 scripts/docx_patch.py <patch>.yaml [--dry-run]

YAML-Format:
  src: output/phase-07-docx/arbeit_final_konform.docx   # Pflicht
  dst: output/phase-07-docx/arbeit_final_konform_v2.docx # optional, sonst auto _vN
  ops:
    - op: replace                # Substring ersetzen (auch über Run-Grenzen)
      anchor: "919.000"          # eindeutiger Substring zur Absatz-Lokalisierung
      old: "(IMF, 2021; NIPC, 2022)"
      new: "(NIPC, 2022)"
    - op: insert_after           # neuen Absatz nach Anker einfügen (Style geklont)
      anchor: "Methodengrenzen"  # oder anchor_startswith: "..."
      text: "Neuer Absatz."
    - op: delete                 # Absatz entfernen
      anchor: "..."

Anker-Regeln (kein stillschweigendes No-Op):
  - 0 Treffer  -> Abbruch mit Fehler
  - >1 Treffer -> Abbruch mit Kandidatenliste; eindeutiger machen oder
                  address: p<N> (Adresse aus docx_inspect.py) angeben
"""

import argparse
import re
import sys
from copy import deepcopy
from pathlib import Path

import yaml
from docx import Document
from docx.text.paragraph import Paragraph

from docx_inspect import iter_addressed_paragraphs


class PatchError(RuntimeError):
    pass


def find_paragraph(doc, op, op_idx):
    """Lokalisiert exakt einen Absatz via address, anchor oder anchor_startswith."""
    address = op.get("address")
    anchor = op.get("anchor")
    startswith = op.get("anchor_startswith")
    if not (address or anchor or startswith):
        raise PatchError(f"Op {op_idx}: braucht address, anchor oder anchor_startswith.")

    hits = []
    for addr, p in iter_addressed_paragraphs(doc):
        if address:
            if addr == address:
                hits.append((addr, p))
        elif anchor and anchor in p.text:
            hits.append((addr, p))
        elif startswith and p.text.startswith(startswith):
            hits.append((addr, p))

    label = address or anchor or startswith
    if not hits:
        raise PatchError(f"Op {op_idx}: Anker nicht gefunden: {label!r}")
    if len(hits) > 1:
        lines = "\n".join(f"    {a}: {p.text[:80]!r}" for a, p in hits[:8])
        raise PatchError(
            f"Op {op_idx}: Anker {label!r} ist mehrdeutig ({len(hits)} Treffer).\n"
            f"  Kandidaten:\n{lines}\n"
            f"  -> Anker verlängern oder address: <adresse> setzen."
        )
    return hits[0]


def replace_across_runs(p, old, new, op_idx):
    """Ersetzt old durch new, auch wenn old über mehrere Runs verteilt ist."""
    concat = "".join(r.text for r in p.runs)
    n = concat.count(old)
    if n == 0:
        if old in p.text:
            raise PatchError(
                f"Op {op_idx}: {old!r} liegt außerhalb normaler Runs "
                "(z. B. in einem Hyperlink) — manueller Eingriff nötig."
            )
        raise PatchError(
            f"Op {op_idx}: {old!r} nicht im Anker-Absatz.\n"
            f"  Volltext: {p.text[:200]!r}"
        )
    if n > 1:
        raise PatchError(
            f"Op {op_idx}: {old!r} kommt {n}× im Absatz vor — "
            "old-String eindeutiger machen."
        )

    start = concat.index(old)
    end = start + len(old)
    pos = 0
    affected = []
    for r in p.runs:
        r_start, r_end = pos, pos + len(r.text)
        if r_end > start and r_start < end:
            affected.append((r, r_start, r_end))
        pos = r_end

    first, f_start, _ = affected[0]
    if len(affected) == 1:
        i = start - f_start
        first.text = first.text[:i] + new + first.text[i + len(old):]
    else:
        last, l_start, _ = affected[-1]
        first.text = first.text[: start - f_start] + new
        for r, _, _ in affected[1:-1]:
            r.text = ""
        last.text = last.text[end - l_start:]


def insert_paragraph_after(target, text):
    """Klont den Anker-Absatz (Style + Formatierung), ersetzt den Text."""
    new_el = deepcopy(target._element)
    target._element.addnext(new_el)
    new_para = Paragraph(new_el, target._parent)
    src_run = target.runs[0] if target.runs else None
    for r in list(new_para.runs):
        r._element.getparent().remove(r._element)
    new_run = new_para.add_run(text)
    if src_run is not None:
        new_run.font.name = src_run.font.name
        if src_run.font.size is not None:
            new_run.font.size = src_run.font.size
        if src_run.bold is not None:
            new_run.bold = src_run.bold
        if src_run.italic is not None:
            new_run.italic = src_run.italic
    return new_para


def _window(text, needle, ctx=45):
    """Textfenster um die Fundstelle für die Vorher/Nachher-Anzeige."""
    i = text.find(needle)
    if i < 0:
        return text[:2 * ctx]
    lo, hi = max(0, i - ctx), i + len(needle) + ctx
    prefix = "…" if lo > 0 else ""
    suffix = "…" if hi < len(text) else ""
    return f"{prefix}{text[lo:hi]}{suffix}"


def auto_dst(src: Path) -> Path:
    m = re.fullmatch(r"(.*)_v(\d+)", src.stem)
    if m:
        return src.with_name(f"{m.group(1)}_v{int(m.group(2)) + 1}{src.suffix}")
    return src.with_name(f"{src.stem}_v2{src.suffix}")


def apply_ops(doc, ops, dry_run):
    for i, op in enumerate(ops, start=1):
        kind = op.get("op")
        if kind not in ("replace", "insert_after", "delete"):
            raise PatchError(f"Op {i}: unbekannte Operation {kind!r} "
                             "(erwartet replace, insert_after, delete).")
        addr, para = find_paragraph(doc, op, i)

        if kind == "replace":
            if "old" not in op or "new" not in op:
                raise PatchError(f"Op {i}: replace braucht old und new.")
            before = para.text
            replace_across_runs(para, op["old"], op["new"], i)
            print(f"✓ Op {i} replace @ {addr}")
            print(f"    - {_window(before, op['old'])!r}")
            print(f"    + {_window(para.text, op['new'])!r}")
        elif kind == "insert_after":
            if "text" not in op:
                raise PatchError(f"Op {i}: insert_after braucht text.")
            insert_paragraph_after(para, op["text"])
            print(f"✓ Op {i} insert_after @ {addr}")
            print(f"    + {op['text'][:120]!r}")
        else:
            before = para.text
            para._element.getparent().remove(para._element)
            print(f"✓ Op {i} delete @ {addr}")
            print(f"    - {before[:120]!r}")

    if dry_run:
        print("\n[DRY-RUN] Alle Ops anwendbar — nichts gespeichert.")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("patch", type=Path, help="Patch-Datei (.yaml)")
    ap.add_argument("--dry-run", action="store_true",
                    help="Ops validieren und anzeigen, aber nicht speichern")
    args = ap.parse_args()

    if not args.patch.exists():
        sys.exit(f"FEHLER: Patch-Datei nicht gefunden: {args.patch}")
    spec = yaml.safe_load(args.patch.read_text(encoding="utf-8"))
    if not isinstance(spec, dict) or "src" not in spec or "ops" not in spec:
        sys.exit("FEHLER: Patch-YAML braucht mindestens src: und ops:.")
    if not spec["ops"]:
        sys.exit("FEHLER: ops: ist leer.")

    src = Path(spec["src"])
    if not src.is_absolute():
        for base in (Path.cwd(), args.patch.parent, args.patch.parent.parent):
            if (base / src).exists():
                src = base / src
                break
    if not src.exists():
        sys.exit(f"FEHLER: Source-DOCX nicht gefunden: {src}")

    dst = Path(spec["dst"]) if spec.get("dst") else auto_dst(src)
    if dst.resolve() == src.resolve():
        sys.exit("FEHLER: dst darf nicht identisch mit src sein "
                 "(Source-DOCX bleibt unangetastet).")

    doc = Document(str(src))
    print(f"Patch: {args.patch.name} -> {src.name}\n")
    try:
        apply_ops(doc, spec["ops"], args.dry_run)
    except PatchError as e:
        sys.exit(f"\n✗ ABBRUCH (nichts gespeichert): {e}")

    if not args.dry_run:
        doc.save(str(dst))
        print(f"\n✓ Gespeichert: {dst}")
        print("  -> jetzt /preflight auf die neue Datei laufen lassen.")


if __name__ == "__main__":
    main()
