#!/usr/bin/env python3
"""
Extract a specific page from a PDF as a high-resolution PNG.
Usage: python extract_pdf_page.py --input report.pdf --page 5 --output output/tmp/slide.png [--dpi 200]
"""

import argparse
from pathlib import Path
import sys

for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8", errors="replace")

try:
    import fitz  # PyMuPDF
except ImportError:
    print("ERROR: PyMuPDF is required. Install: pip install PyMuPDF", file=sys.stderr)
    sys.exit(1)


def extract_page(pdf_path: str, page_number: int, output_path: str, dpi: int = 200) -> None:
    src = Path(pdf_path)
    if not src.is_file():
        print(f"ERROR: Input PDF not found: {pdf_path}", file=sys.stderr)
        sys.exit(1)

    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)

    with fitz.open(str(src)) as doc:
        if page_number < 0 or page_number >= len(doc):
            print(f"ERROR: Page {page_number} out of range (0-{len(doc) - 1})", file=sys.stderr)
            sys.exit(1)
        page = doc[page_number]
        zoom = dpi / 72.0
        pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom))
        pix.save(str(out))
        print(f"Saved page {page_number} to {out} ({pix.width}x{pix.height}px @ {dpi}dpi)")


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract PDF page as PNG")
    parser.add_argument("--input", "-i", required=True, help="Input PDF path")
    parser.add_argument("--page", "-p", type=int, required=True, help="0-based page number")
    parser.add_argument("--output", "-o", required=True, help="Output PNG path")
    parser.add_argument("--dpi", type=int, default=200, help="Output DPI (default 200)")
    args = parser.parse_args()
    extract_page(args.input, args.page, args.output, args.dpi)


if __name__ == "__main__":
    main()
