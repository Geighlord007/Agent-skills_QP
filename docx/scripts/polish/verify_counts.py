#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
verify_counts.py — Structural count invariant check for .docx packages.

Captures exact raw-XML counts (paragraphs, tables, drawings, blips, extents,
media files, ZIP part count, headers/footers/footnotes/comments) before an edit,
and verifies after the edit that zero unrequested structural drift occurred.

Never silently passes on 0 matched files.

Usage:
  python scripts/polish/verify_counts.py capture <doc_or_dir> --out baseline.json
  python scripts/polish/verify_counts.py check <doc_or_dir> --baseline baseline.json
  python scripts/polish/verify_counts.py inspect <doc_or_dir>
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    if hasattr(_s, "reconfigure"):
        _s.reconfigure(encoding="utf-8", errors="replace")

NS = {
    "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
    "wp": "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing",
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
}

STRUCTURAL_KEYS = (
    "paragraphs",
    "tables",
    "drawings",
    "blips",
    "wp_extents",
    "a_ext",
    "media_files",
    "part_count",
    "headers",
    "footers",
    "footnotes",
    "comments",
)


def collect_targets(path_str: str) -> list[Path]:
    p = Path(path_str)
    if p.is_file():
        if p.suffix.lower() != ".docx":
            raise ValueError(f"Not a .docx file: {p}")
        return [p]
    if p.is_dir():
        files = sorted(
            f for f in p.rglob("*.docx")
            if not f.name.startswith("~$") and f.is_file()
        )
        return files
    raise FileNotFoundError(f"Path not found: {p}")


def measure_docx(docx_path: Path) -> dict:
    with zipfile.ZipFile(docx_path, "r") as z:
        names = z.namelist()
        if "word/document.xml" not in names:
            raise ValueError(f"Invalid .docx (missing word/document.xml): {docx_path}")
        doc_xml = z.read("word/document.xml")
        root = ET.fromstring(doc_xml)

        media = sorted(n for n in names if n.startswith("word/media/"))
        headers = [n for n in names if n.startswith("word/header") and n.endswith(".xml")]
        footers = [n for n in names if n.startswith("word/footer") and n.endswith(".xml")]

        footnotes = 0
        if "word/footnotes.xml" in names:
            fn_root = ET.fromstring(z.read("word/footnotes.xml"))
            footnotes = len(fn_root.findall(".//w:footnote", NS))

        comments = 0
        if "word/comments.xml" in names:
            cm_root = ET.fromstring(z.read("word/comments.xml"))
            comments = len(cm_root.findall(".//w:comment", NS))

        return {
            "file": docx_path.name,
            "paragraphs": len(root.findall(".//w:p", NS)),
            "tables": len(root.findall(".//w:tbl", NS)),
            "drawings": len(root.findall(".//w:drawing", NS)),
            "blips": len(root.findall(".//a:blip", NS)),
            "wp_extents": len(root.findall(".//wp:extent", NS)),
            "a_ext": len(root.findall(".//a:ext", NS)),
            "media_files": len(media),
            "part_count": len(names),
            "headers": len(headers),
            "footers": len(footers),
            "footnotes": footnotes,
            "comments": comments,
            "size_bytes": docx_path.stat().st_size,
            "sha256": hashlib.sha256(docx_path.read_bytes()).hexdigest()[:16],
        }


def snapshot_all(target_path: str) -> dict[str, dict]:
    files = collect_targets(target_path)
    if not files:
        raise ValueError(f"No .docx files found under: {target_path} (refusing vacuous pass)")
    base = Path(target_path)
    out: dict[str, dict] = {}
    for f in files:
        key = f.name if base.is_file() else str(f.relative_to(base)).replace("\\", "/")
        out[key] = measure_docx(f)
    return out


def cmd_inspect(args: argparse.Namespace) -> int:
    snap = snapshot_all(args.target)
    print(json.dumps(snap, ensure_ascii=False, indent=2))
    return 0


def cmd_capture(args: argparse.Namespace) -> int:
    snap = snapshot_all(args.target)
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(snap, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Captured baseline for {len(snap)} document(s) -> {out_path}")
    return 0


def cmd_check(args: argparse.Namespace) -> int:
    baseline_path = Path(args.baseline)
    if not baseline_path.is_file():
        print(f"ERROR: baseline not found: {baseline_path}", file=sys.stderr)
        return 2
    baseline = json.loads(baseline_path.read_text(encoding="utf-8"))
    if not baseline:
        print("ERROR: baseline is empty (refusing vacuous pass)", file=sys.stderr)
        return 2

    current = snapshot_all(args.target)
    allow_set = set(args.allow_drift or [])

    failures: list[str] = []
    for key, exp in baseline.items():
        if key not in current:
            failures.append(f"{key}: MISSING in current target")
            continue
        cur = current[key]
        for field in STRUCTURAL_KEYS:
            if field in allow_set:
                continue
            if cur.get(field) != exp.get(field):
                failures.append(
                    f"{key}: {field} drifted {exp.get(field)} -> {cur.get(field)}"
                )
    for key in current:
        if key not in baseline:
            failures.append(f"{key}: UNEXPECTED new file not in baseline")

    if failures:
        print(f"FAIL: {len(failures)} structural count drift(s) detected:", file=sys.stderr)
        for line in failures:
            print(f"  - {line}", file=sys.stderr)
        return 1

    print(
        f"PASS: all {len(baseline)} document(s) match baseline across "
        f"{len(STRUCTURAL_KEYS) - len(allow_set)} structural invariants "
        f"(scope: XML counts only; does not verify visual layout or text wording)."
    )
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Structural count invariant verifier for .docx files.")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p_ins = sub.add_parser("inspect", help="Print structural counts as JSON")
    p_ins.add_argument("target", help=".docx file or directory")
    p_ins.set_defaults(func=cmd_inspect)

    p_cap = sub.add_parser("capture", help="Capture structural baseline JSON")
    p_cap.add_argument("target", help=".docx file or directory")
    p_cap.add_argument("--out", required=True, help="Output baseline JSON path")
    p_cap.set_defaults(func=cmd_capture)

    p_chk = sub.add_parser("check", help="Check current .docx files against baseline JSON")
    p_chk.add_argument("target", help=".docx file or directory")
    p_chk.add_argument("--baseline", required=True, help="Baseline JSON path")
    p_chk.add_argument(
        "--allow-drift",
        action="append",
        default=[],
        help="Optional structural field name allowed to change (repeatable)",
    )
    p_chk.set_defaults(func=cmd_check)

    args = ap.parse_args()
    try:
        return args.func(args)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
