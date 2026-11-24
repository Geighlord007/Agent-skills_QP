#!/usr/bin/env python3
"""
Markdown -> Word conversion main pipeline (with citation cross-references).

Pipeline: load -> citation conversion -> Pandoc -> OOXML post-processing -> output docx.
All intermediate files (.converted.md, .base.docx) are stored in a TemporaryDirectory
and cleaned up automatically on exit.
"""

import argparse
import json
import logging
import shutil
import subprocess
import sys
import tempfile
import traceback
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).resolve().parent))

from citation_parser import convert_citations, detect_edge_cases
from docx_notes import process_word_document_with_endnotes, process_word_document_with_noteref
from docx_postprocess import process_word_document_with_hyperlinks

logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

STYLES = ("footnote", "endnote", "hyperlink")


def load_citation_db(jsonl_path: Path) -> dict:
    """Load citation.jsonl -> {int_id: entry_dict}."""
    db = {}
    with jsonl_path.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                entry = json.loads(line)
                cid = entry.get("id")
                if cid is not None:
                    db[cid] = entry
    return db


def convert_md_to_docx(
    md_path: str,
    citation_jsonl_path: Optional[str] = None,
    output_dir: Optional[str] = None,
    style: str = "footnote",
) -> str:
    """
    Full Markdown -> Word conversion pipeline with automatic temp-file cleanup.

    Args:
        md_path:             Path to Markdown file
        citation_jsonl_path: Path to citation.jsonl (required)
        output_dir:          Output directory (None uses same directory as MD file)
        style:               footnote / endnote / hyperlink

    Returns:
        Path to generated docx file
    """
    if style not in STYLES:
        raise ValueError(f"style must be one of {STYLES}, got: {style}")

    src_md = Path(md_path).resolve()
    if not src_md.exists():
        raise FileNotFoundError(f"Markdown file not found: {src_md}")

    if not citation_jsonl_path:
        raise ValueError("citation_jsonl_path is required. Specify the path to citation.jsonl.")
    src_citation = Path(citation_jsonl_path).resolve()
    if not src_citation.exists():
        raise FileNotFoundError(f"Citation file not found: {src_citation}")

    pandoc_bin = shutil.which("pandoc")
    if not pandoc_bin:
        raise RuntimeError("pandoc not found on PATH. Install pandoc before running md2docx.")

    out_dir = Path(output_dir).resolve() if output_dir else src_md.parent
    out_dir.mkdir(parents=True, exist_ok=True)

    logger.info("Document: %s | Citation: %s | Style: %s", src_md.name, src_citation.name, style)

    # 1. Load data
    citation_db = load_citation_db(src_citation)
    logger.info("Loaded %d citation records", len(citation_db))
    markdown_content = src_md.read_text(encoding="utf-8")

    # 2. Citation conversion
    converted_md, id_to_display_num, _detection = convert_citations(markdown_content, citation_db)

    # 3. Edge case detection
    for w in detect_edge_cases(markdown_content):
        logger.warning(w)

    # 4 & 5. Intermediate files live inside TemporaryDirectory -> zero leftover clutter
    output_path = out_dir / f"{src_md.stem}.{style}.docx"
    display_db = {v: citation_db[k] for k, v in id_to_display_num.items()}
    processors = {
        "footnote": process_word_document_with_noteref,
        "endnote": process_word_document_with_endnotes,
        "hyperlink": process_word_document_with_hyperlinks,
    }

    with tempfile.TemporaryDirectory(prefix="md2docx_") as tmpdir:
        tmp = Path(tmpdir)
        converted_md_path = tmp / f"{src_md.stem}.converted.md"
        base_docx_path = tmp / f"{src_md.stem}.base.docx"

        converted_md_path.write_text(converted_md, encoding="utf-8")

        pandoc_cmd = [
            pandoc_bin,
            str(converted_md_path),
            "-o",
            str(base_docx_path),
            "--from=markdown",
            "--to=docx",
            f"--resource-path={src_md.parent}",
            "--standalone",
        ]
        result = subprocess.run(
            pandoc_cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        if result.returncode != 0:
            raise RuntimeError(f"Pandoc conversion failed: {result.stderr}")

        # 6. OOXML post-processing
        success = processors[style](str(base_docx_path), str(output_path), citation_db=display_db)

    if success:
        logger.info("Done: %s", output_path.name)
        return str(output_path)
    raise RuntimeError(f"{style} generation failed")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Markdown -> Word conversion (with citation cross-references)"
    )
    parser.add_argument("md_file", help="Path to Markdown file")
    parser.add_argument("--citation", required=True, help="Path to citation.jsonl")
    parser.add_argument("--output-dir", help="Output directory (default: same as MD file)")
    parser.add_argument(
        "--style",
        choices=STYLES,
        default="footnote",
        help="Citation style: footnote / endnote / hyperlink",
    )

    args = parser.parse_args()
    try:
        out = convert_md_to_docx(
            args.md_file,
            citation_jsonl_path=args.citation,
            output_dir=args.output_dir,
            style=args.style,
        )
        print(f"\n{'=' * 60}\nConversion complete: {out}\n{'=' * 60}")
        return 0
    except Exception as exc:
        logger.error("Conversion failed: %s", exc)
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
