#!/usr/bin/env python3
"""
Extract a specific page from a PDF as a high-resolution PNG.
Usage: python extract_pdf_page.py --input report.pdf --page 5 --output /tmp/slide.png [--dpi 200]
"""

import argparse
import sys

try:
    import fitz  # PyMuPDF
except ImportError as e:
    print("ERROR: PyMuPDF is required. Install: pip install --user PyMuPDF")
    sys.exit(1)


def extract_page(pdf_path, page_number, output_path, dpi=200):
    doc = fitz.open(pdf_path)
    if page_number < 0 or page_number >= len(doc):
        print(f"ERROR: Page {page_number} out of range (0–{len(doc)-1})")
        sys.exit(1)
    page = doc[page_number]
    zoom = dpi / 72.0
    mat = fitz.Matrix(zoom, zoom)
    pix = page.get_pixmap(matrix=mat)
    pix.save(output_path)
    print(f"Saved page {page_number} to {output_path} ({pix.width}x{pix.height}px @ {dpi}dpi)")
    doc.close()


def main():
    parser = argparse.ArgumentParser(description="Extract PDF page as PNG")
    parser.add_argument("--input", "-i", required=True, help="Input PDF path")
    parser.add_argument("--page", "-p", type=int, required=True, help="0-based page number")
    parser.add_argument("--output", "-o", required=True, help="Output PNG path")
    parser.add_argument("--dpi", type=int, default=200, help="Output DPI (default 200)")
    args = parser.parse_args()
    extract_page(args.input, args.page, args.output, args.dpi)


if __name__ == "__main__":
    main()
