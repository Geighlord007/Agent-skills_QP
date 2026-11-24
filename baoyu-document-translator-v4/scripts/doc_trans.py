#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""doc_trans.py — Unified single CLI entry point for baoyu-document-translator-v4 (v4.3).

Unifies Mode A (DOCX / plain-text native subagents), Mode B (PPTX slide-image-guided +
API/subagent), and XLSX translation behind one discoverable CLI while keeping Linux/WSL2
WIR `.so` write-back as first-class default on Linux.

Subcommands:
  extract        Extract DOCX/PPTX to keyed JSON (and optional --md source.md)
  chunk          Split keyed source.md into chunks (+ optional --extracted chunk-NN-runs.json)
  pptx-prep      4-in-1 PPTX prep: extract + render-slides + ocr-slides + slide-bundles
  render-slides  Export PPTX slides to JPG (COM on Windows, LibreOffice fallback elsewhere)
  ocr-slides     Register image-baked text via AI Studio OCR (graceful skip if no token)
  bundles        Group PPTX elements by slide into groups/
  dispatch       Build translate/review/unify/visual dispatch prompts
  api-call       Call OpenAI-compatible vision/text API concurrently
  apply-patches  Apply review/unify JSON patches into translation.md + run_splits.json
  merge          Merge translation.md (+ optional run_splits.json) into translated.json
  write          Write translated.json back to DOCX (Linux/WSL2: WIR .so; Win/Mac: surgical) or PPTX
  qa             Blocking QA gate (structure + roundtrip + numbers + concat + optional render)
  compare        Generate page-by-page SRC/TGT comparison files (PPTX slides or DOCX stories)
  xlsx           Translate XLSX sharedStrings + sheet names via lxml
  engine-info    Show current platform and DOCX write-back engine selection (WIR vs surgical)
  selftest       Run 24-check regression selftest
"""
import argparse
import importlib
import io
import json
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

if sys.platform == "win32":
    for _s in (sys.stdout, sys.stderr):
        if hasattr(_s, "reconfigure"):
            _s.reconfigure(encoding="utf-8", errors="replace")


def _invoke_module(mod_name: str, argv: list) -> int:
    import runpy

    mod = importlib.import_module(mod_name)
    saved = sys.argv[:]
    try:
        sys.argv = [str(SCRIPTS / f"{mod_name}.py")] + [str(a) for a in argv]
        if hasattr(mod, "main"):
            rc = mod.main()
            return 0 if rc is None else int(rc)
        runpy.run_path(str(SCRIPTS / f"{mod_name}.py"), run_name="__main__")
        return 0
    except SystemExit as exc:
        if exc.code is None:
            return 0
        if isinstance(exc.code, int):
            return exc.code
        print(exc.code, file=sys.stderr)
        return 1
    finally:
        sys.argv = saved


def cmd_extract(args) -> int:
    extra = ["--no-notes"] if args.no_notes else []
    rc = _invoke_module("extract_v3", [args.input, args.output] + extra)
    if rc != 0:
        return rc
    if args.md:
        rc = _invoke_module("json_to_markdown_v2", [args.output, args.md])
    return rc


def cmd_chunk(args) -> int:
    argv = [args.source, args.outdir, str(args.max_chars)]
    if args.extracted:
        argv += ["--extracted", args.extracted]
    return _invoke_module("chunk_keyed", argv)


def cmd_pptx_prep(args) -> int:
    work = Path(args.work_dir)
    work.mkdir(parents=True, exist_ok=True)
    extracted = work / "extracted.json"
    slides_dir = work / "slides"
    groups_dir = work / "groups"

    print("[1/4] Extracting PPTX...")
    extra = ["--no-notes"] if args.no_notes else []
    rc = _invoke_module("extract_v3", [args.input, extracted] + extra)
    if rc != 0:
        return rc

    print("[2/4] Rendering slide images...")
    rc = _invoke_module("render_slides", [args.input, slides_dir, "--backend", args.backend])
    if rc != 0:
        return rc

    if args.no_ocr:
        print("[3/4] Skipping OCR (--no-ocr).")
    else:
        print("[3/4] Registering image-baked text (OCR)...")
        rc = _invoke_module("ocr_slides", [slides_dir])
        if rc != 0:
            return rc

    print("[4/4] Building slide bundles...")
    return _invoke_module("slide_bundles", [extracted, "--out", groups_dir, "--per-group", str(args.per_group)])


def cmd_merge(args) -> int:
    argv = [args.extracted, args.translation, args.output]
    if args.splits:
        argv.append(args.splits)
    return _invoke_module("merge_v3", argv)


def cmd_write(args) -> int:
    return _invoke_module("write_v3", [args.input, args.output, args.translated, "--engine", args.engine])


def cmd_qa(args) -> int:
    import qa_v3

    return qa_v3.run_qa(
        args.source,
        args.output,
        args.translated,
        args.translation,
        numerals_path=args.numerals,
        render_pdf=args.render,
    )


def cmd_engine_info(_args) -> int:
    import engine_select

    info = engine_select.decide()
    print(json.dumps(info, ensure_ascii=False, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(
        prog="doc_trans.py",
        description="Unified CLI for baoyu-document-translator-v4 (Mode A DOCX/text + Mode B PPTX visual + XLSX).",
    )
    sp = ap.add_subparsers(dest="cmd", required=True)

    p = sp.add_parser("extract", help="Extract DOCX/PPTX to keyed JSON (and optional --md)")
    p.add_argument("input")
    p.add_argument("output")
    p.add_argument("--md", default=None, help="Also export keyed Markdown to this path")
    p.add_argument("--no-notes", action="store_true")
    p.set_defaults(fn=cmd_extract)

    p = sp.add_parser("chunk", help="Split keyed source.md into chunks (+ optional chunk-NN-runs.json)")
    p.add_argument("source")
    p.add_argument("outdir")
    p.add_argument("max_chars", nargs="?", type=int, default=4200)
    p.add_argument("--extracted", default=None)
    p.set_defaults(fn=cmd_chunk)

    p = sp.add_parser("pptx-prep", help="4-in-1 PPTX prep: extract + render-slides + ocr-slides + bundles")
    p.add_argument("input")
    p.add_argument("work_dir")
    p.add_argument("--per-group", type=int, default=3)
    p.add_argument("--backend", choices=("auto", "com", "libreoffice"), default="auto")
    p.add_argument("--no-ocr", action="store_true")
    p.add_argument("--no-notes", action="store_true")
    p.set_defaults(fn=cmd_pptx_prep)

    p = sp.add_parser("merge", help="Merge translation.md (+ optional run_splits.json) into translated.json")
    p.add_argument("extracted")
    p.add_argument("translation")
    p.add_argument("output")
    p.add_argument("splits", nargs="?", default=None)
    p.set_defaults(fn=cmd_merge)

    p = sp.add_parser("write", help="Write translated.json back to DOCX (Linux: WIR .so; Win/Mac: surgical) or PPTX")
    p.add_argument("input")
    p.add_argument("output")
    p.add_argument("translated")
    p.add_argument("--engine", choices=("auto", "wir", "surgical"), default="auto")
    p.set_defaults(fn=cmd_write)

    p = sp.add_parser("qa", help="Blocking QA gate (structure, numbers, concat, optional --render)")
    p.add_argument("source")
    p.add_argument("output")
    p.add_argument("translated")
    p.add_argument("translation")
    p.add_argument("--numerals", default=None)
    p.add_argument("--render", default=None)
    p.set_defaults(fn=cmd_qa)

    p = sp.add_parser("engine-info", help="Show platform and DOCX write-back engine routing (WIR vs surgical)")
    p.set_defaults(fn=cmd_engine_info)

    # Pass-through subcommands (preserve full native flags of each module)
    passthrough = [
        ("render-slides", "render_slides", "Export PPTX slides to JPG"),
        ("ocr-slides", "ocr_slides", "OCR image-baked text on rendered slides"),
        ("bundles", "slide_bundles", "Group PPTX elements into slide bundles"),
        ("dispatch", "build_dispatch", "Generate translate/review/unify/visual dispatch files"),
        ("api-call", "api_call", "Call OpenAI-compatible model API concurrently"),
        ("apply-patches", "apply_patches", "Apply review/unify JSON patches to translation.md"),
        ("compare", "page_compare", "Generate page-by-page SRC/TGT comparison files"),
        ("xlsx", "xlsx_translate", "Translate XLSX sharedStrings + sheet names"),
        ("selftest", "selftest", "Run 24-check regression selftest"),
    ]
    for cmd_name, mod_name, help_txt in passthrough:
        p = sp.add_parser(cmd_name, help=help_txt)
        p.add_argument("rest", nargs=argparse.REMAINDER)
        p.set_defaults(fn=lambda a, _m=mod_name: _invoke_module(_m, a.rest))

    return ap


def main() -> int:
    ap = build_parser()
    args = ap.parse_args()
    return int(args.fn(args))


if __name__ == "__main__":
    sys.exit(main())
