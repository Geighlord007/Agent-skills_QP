#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
verify_word_open.py — Serialized host-application open test for .docx deliverables.

Why this exists:
  Passing OOXML XSD validation does not guarantee Microsoft Word opens a file
  without a repair prompt. Conversely, running multiple Word COM processes in
  parallel produces phantom corruption reports on healthy files.

Design rules:
  1. SERIALIZED ONLY: Opens one Word COM instance (`Visible=False`, `DisplayAlerts=0`)
     and processes files sequentially; never invoke in parallel across agents.
  2. ASCII STAGING: Copies each .docx to an ASCII temp filename inside
     `tempfile.TemporaryDirectory()` so CJK/space paths cannot trigger COM path bugs.
  3. NO SILENT PASS: Refuses 0 matched files and fails loudly if neither Word COM
     nor LibreOffice (`--engine libreoffice`) is available.

Usage:
  python scripts/polish/verify_word_open.py <doc_or_dir>
  python scripts/polish/verify_word_open.py <doc_or_dir> --engine libreoffice
"""
from __future__ import annotations

import argparse
import json
import platform
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    if hasattr(_s, "reconfigure"):
        _s.reconfigure(encoding="utf-8", errors="replace")


def collect_targets(path_str: str) -> list[Path]:
    p = Path(path_str)
    if p.is_file():
        if p.suffix.lower() != ".docx":
            raise ValueError(f"Not a .docx file: {p}")
        return [p]
    if p.is_dir():
        return sorted(
            f for f in p.rglob("*.docx")
            if not f.name.startswith("~$") and f.is_file()
        )
    raise FileNotFoundError(f"Path not found: {p}")


def verify_with_word_com(files: list[Path]) -> tuple[list[dict], list[dict]]:
    import win32com.client  # type: ignore

    passed: list[dict] = []
    failed: list[dict] = []
    word = None
    try:
        word = win32com.client.DispatchEx("Word.Application")
        word.Visible = False
        word.DisplayAlerts = 0
        with tempfile.TemporaryDirectory(prefix="docx_word_open_") as tmpdir:
            for idx, src in enumerate(files, 1):
                staged = Path(tmpdir) / f"doc_{idx:04d}.docx"
                shutil.copy2(src, staged)
                doc = None
                try:
                    doc = word.Documents.Open(
                        FileName=str(staged.resolve()),
                        ConfirmConversions=False,
                        ReadOnly=True,
                        AddToRecentFiles=False,
                        OpenAndRepair=False,
                        NoEncodingDialog=True,
                    )
                    passed.append({
                        "file": str(src),
                        "engine": "word_com",
                        "sections": int(doc.Sections.Count),
                        "paragraphs": int(doc.Paragraphs.Count),
                        "inline_shapes": int(doc.InlineShapes.Count),
                    })
                except Exception as exc:
                    failed.append({"file": str(src), "engine": "word_com", "error": str(exc)})
                finally:
                    if doc is not None:
                        try:
                            doc.Close(SaveChanges=False)
                        except Exception:
                            pass
    finally:
        if word is not None:
            try:
                word.Quit(SaveChanges=False)
            except Exception:
                pass
    return passed, failed


def verify_with_libreoffice(files: list[Path], soffice: str) -> tuple[list[dict], list[dict]]:
    passed: list[dict] = []
    failed: list[dict] = []
    with tempfile.TemporaryDirectory(prefix="docx_lo_open_") as tmpdir:
        out_dir = Path(tmpdir) / "out"
        out_dir.mkdir(parents=True, exist_ok=True)
        for idx, src in enumerate(files, 1):
            staged = Path(tmpdir) / f"doc_{idx:04d}.docx"
            shutil.copy2(src, staged)
            cmd = [
                soffice,
                "--headless",
                "--norestore",
                "--convert-to",
                "pdf",
                "--outdir",
                str(out_dir),
                str(staged),
            ]
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=120,
            )
            pdf_out = out_dir / f"doc_{idx:04d}.pdf"
            if proc.returncode == 0 and pdf_out.is_file() and pdf_out.stat().st_size > 0:
                passed.append({
                    "file": str(src),
                    "engine": "libreoffice",
                    "pdf_bytes": pdf_out.stat().st_size,
                })
            else:
                failed.append({
                    "file": str(src),
                    "engine": "libreoffice",
                    "returncode": proc.returncode,
                    "stderr": (proc.stderr or proc.stdout or "").strip()[:300],
                })
    return passed, failed


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Serialized Word COM / LibreOffice open verification for .docx files."
    )
    ap.add_argument("target", help=".docx file or directory")
    ap.add_argument(
        "--engine",
        choices=("auto", "word", "libreoffice"),
        default="auto",
        help="Verification engine (default: auto -> Word COM on Windows, else LibreOffice)",
    )
    ap.add_argument("--json", action="store_true", help="Emit structured JSON output")
    args = ap.parse_args()

    try:
        files = collect_targets(args.target)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    if not files:
        print(f"ERROR: no .docx files found under {args.target} (refusing vacuous pass)", file=sys.stderr)
        return 2

    use_word = False
    soffice = shutil.which("soffice") or shutil.which("libreoffice")

    if args.engine == "word":
        use_word = True
    elif args.engine == "libreoffice":
        if not soffice:
            print("ERROR: LibreOffice (soffice) not found on PATH", file=sys.stderr)
            return 2
    else:
        if platform.system() == "Windows":
            try:
                import win32com.client  # noqa: F401
                use_word = True
            except ImportError:
                use_word = False
        if not use_word and not soffice:
            print(
                "ERROR: Neither pywin32 (Word COM) nor LibreOffice (soffice) is available. "
                "Install pywin32 on Windows with Word, or install LibreOffice.",
                file=sys.stderr,
            )
            return 2

    if use_word:
        passed, failed = verify_with_word_com(files)
    else:
        passed, failed = verify_with_libreoffice(files, soffice)  # type: ignore[arg-type]

    summary = {
        "engine": "word_com" if use_word else "libreoffice",
        "total": len(files),
        "passed": len(passed),
        "failed": len(failed),
        "results": passed,
        "errors": failed,
        "scope_note": "Verifies serialized host-app open without error; does not check visual overlap or prose.",
    }
    if args.json:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    else:
        print(f"[{summary['engine']}] opened {summary['passed']}/{summary['total']} cleanly.")
        for err in failed:
            print(f"  FAIL {err['file']}: {err.get('error') or err.get('stderr')}", file=sys.stderr)

    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
