#!/usr/bin/env python3
"""Convert a research report Markdown file to DOCX.

Supports headings, paragraphs, unordered & ordered lists, blockquotes,
fenced code blocks, Markdown tables (preserving empty cells), inline formatting
(bold, italic, inline code, superscript [N] citations, clickable hyperlinks),
and raster image embedding (PNG/JPG/GIF/BMP, with SVG sibling-PNG fallback).
"""

import argparse
import re
import sys
from pathlib import Path

for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8", errors="replace")


RASTER_EXTS = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tif", ".tiff"}


def ensure_docx():
    try:
        import docx  # noqa: F401
    except ImportError:
        raise SystemExit(
            "python-docx is required. Install with: pip install python-docx"
        )


def _split_table_row(line: str) -> list[str]:
    """Split a Markdown table row while preserving empty inner cells."""
    stripped = line.strip()
    if stripped.startswith("|"):
        stripped = stripped[1:]
    if stripped.endswith("|"):
        stripped = stripped[:-1]
    return [c.strip() for c in stripped.split("|")]


def parse_table(lines: list[str]) -> tuple[list[str], list[list[str]]]:
    """Parse a Markdown table block into header + rows without dropping empty cells."""
    if not lines:
        return [], []
    header = _split_table_row(lines[0])
    ncols = len(header)
    rows: list[list[str]] = []
    # Skip separator line (index 1) if present
    start_idx = 2 if len(lines) >= 2 and re.match(r"^[\s|:-]+$", lines[1]) else 1
    for line in lines[start_idx:]:
        if not line.strip():
            continue
        cells = _split_table_row(line)
        if len(cells) < ncols:
            cells.extend([""] * (ncols - len(cells)))
        elif len(cells) > ncols:
            cells = cells[:ncols]
        rows.append(cells)
    return header, rows


def parse_markdown(text: str):
    blocks = []
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if not stripped:
            i += 1
            continue

        # Fenced code block
        if stripped.startswith("```"):
            code_lines = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith("```"):
                code_lines.append(lines[i])
                i += 1
            if i < len(lines):
                i += 1  # consume closing fence
            blocks.append(("code", "\n".join(code_lines)))
            continue

        # Headings
        m = re.match(r"^(#{1,4})\s+(.*)$", stripped)
        if m:
            level = len(m.group(1))
            blocks.append(("heading", level, m.group(2).strip()))
            i += 1
            continue

        # Standalone image ![alt](path)
        img_m = re.match(r"^!\[([^\]]*)\]\(([^)]+)\)$", stripped)
        if img_m:
            blocks.append(("image", img_m.group(1).strip(), img_m.group(2).strip()))
            i += 1
            continue

        # Horizontal rule
        if re.match(r"^[-*]{3,}$", stripped):
            blocks.append(("rule",))
            i += 1
            continue

        # Table
        if stripped.startswith("|"):
            table_lines = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                table_lines.append(lines[i])
                i += 1
            header, rows = parse_table(table_lines)
            if header:
                blocks.append(("table", header, rows))
            continue

        # Blockquote
        if stripped.startswith(">"):
            quote_lines = []
            while i < len(lines) and lines[i].strip().startswith(">"):
                quote_lines.append(re.sub(r"^>\s?", "", lines[i].strip()))
                i += 1
            blocks.append(("blockquote", " ".join(quote_lines)))
            continue

        # Unordered list
        if re.match(r"^[-*]\s+", stripped):
            items = []
            while i < len(lines) and re.match(r"^[-*]\s+", lines[i].strip()):
                items.append(re.sub(r"^[-*]\s+", "", lines[i].strip()))
                i += 1
            blocks.append(("ul", items))
            continue

        # Ordered list
        if re.match(r"^\d+\.\s+", stripped):
            items = []
            while i < len(lines) and re.match(r"^\d+\.\s+", lines[i].strip()):
                items.append(re.sub(r"^\d+\.\s+", "", lines[i].strip()))
                i += 1
            blocks.append(("ol", items))
            continue

        # Paragraph (stop at next structural block)
        para_lines = []
        while i < len(lines):
            s = lines[i].strip()
            if (
                not s
                or s.startswith("```")
                or s.startswith("|")
                or s.startswith(">")
                or re.match(r"^(#{1,4})\s+", s)
                or re.match(r"^[-*]\s+", s)
                or re.match(r"^\d+\.\s+", s)
                or re.match(r"^!\[[^\]]*\]\([^)]+\)$", s)
                or re.match(r"^[-*]{3,}$", s)
            ):
                break
            para_lines.append(s)
            i += 1
        if para_lines:
            blocks.append(("paragraph", " ".join(para_lines)))

    return blocks


def _add_hyperlink(paragraph, text: str, url: str) -> None:
    """Append a clickable OOXML hyperlink run to *paragraph*."""
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn

    part = paragraph.part
    r_id = part.relate_to(
        url,
        "http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink",
        is_external=True,
    )
    hyperlink = OxmlElement("w:hyperlink")
    hyperlink.set(qn("r:id"), r_id)

    new_run = OxmlElement("w:r")
    r_pr = OxmlElement("w:rPr")
    color = OxmlElement("w:color")
    color.set(qn("w:val"), "0563C1")
    u = OxmlElement("w:u")
    u.set(qn("w:val"), "single")
    r_pr.append(color)
    r_pr.append(u)
    new_run.append(r_pr)

    t = OxmlElement("w:t")
    t.text = text
    new_run.append(t)
    hyperlink.append(new_run)
    paragraph._p.append(hyperlink)


INLINE_TOKEN_RE = re.compile(
    r"(\[[^\]]+\]\([^)]+\)|\*\*[^*]+\*\*|\*[^*]+\*|`[^`]+`|\[\d+\])"
)


def render_inline(runs_parent, text: str):
    """Add text to a paragraph or table cell with inline formatting."""
    parts = INLINE_TOKEN_RE.split(text)
    for part in parts:
        if not part:
            continue
        link_m = re.match(r"^\[([^\]]+)\]\(([^)]+)\)$", part)
        if link_m:
            _add_hyperlink(runs_parent, link_m.group(1), link_m.group(2))
        elif part.startswith("**") and part.endswith("**"):
            runs_parent.add_run(part[2:-2]).bold = True
        elif part.startswith("*") and part.endswith("*"):
            runs_parent.add_run(part[1:-1]).italic = True
        elif part.startswith("`") and part.endswith("`"):
            r = runs_parent.add_run(part[1:-1])
            r.font.name = "Courier New"
        elif re.match(r"^\[\d+\]$", part):
            runs_parent.add_run(part).font.superscript = True
        else:
            runs_parent.add_run(part)


def md_to_docx(input_path: Path, output_path: Path):
    ensure_docx()
    from docx import Document
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.shared import Inches, Pt, RGBColor

    doc = Document()

    style = doc.styles["Normal"]
    style.font.name = "Calibri"
    style.font.size = Pt(11)

    base_dir = input_path.resolve().parent
    blocks = parse_markdown(input_path.read_text(encoding="utf-8"))

    for block in blocks:
        kind = block[0]
        if kind == "heading":
            _, level, text = block
            p = doc.add_heading(level=level)
            render_inline(p, text)
        elif kind == "paragraph":
            _, text = block
            p = doc.add_paragraph()
            render_inline(p, text)
        elif kind == "blockquote":
            _, text = block
            p = doc.add_paragraph()
            p.paragraph_format.left_indent = Inches(0.35)
            r = p.add_run(text)
            r.italic = True
            r.font.color.rgb = RGBColor(0x4A, 0x4A, 0x4A)
        elif kind == "code":
            _, code_text = block
            p = doc.add_paragraph()
            p.paragraph_format.left_indent = Inches(0.25)
            r = p.add_run(code_text)
            r.font.name = "Courier New"
            r.font.size = Pt(9.5)
        elif kind == "ul":
            _, items = block
            for item in items:
                p = doc.add_paragraph(style="List Bullet")
                render_inline(p, item)
        elif kind == "ol":
            _, items = block
            for item in items:
                p = doc.add_paragraph(style="List Number")
                render_inline(p, item)
        elif kind == "image":
            _, alt, rel_src = block
            img_path = (base_dir / rel_src).resolve()
            if img_path.suffix.lower() == ".svg":
                png_alt = img_path.with_suffix(".png")
                if png_alt.is_file():
                    img_path = png_alt
            if img_path.is_file() and img_path.suffix.lower() in RASTER_EXTS:
                doc.add_picture(str(img_path), width=Inches(6.0))
                if alt:
                    cap = doc.add_paragraph(alt)
                    cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    for run in cap.runs:
                        run.italic = True
                        run.font.size = Pt(9.5)
                        run.font.color.rgb = RGBColor(0x55, 0x55, 0x55)
            else:
                note = doc.add_paragraph(
                    f"[Figure omitted in DOCX: {alt or rel_src} ({rel_src})]"
                )
                for run in note.runs:
                    run.italic = True
                    run.font.color.rgb = RGBColor(0x66, 0x66, 0x66)
        elif kind == "table":
            _, header, rows = block
            table = doc.add_table(rows=1, cols=len(header))
            table.style = "Table Grid"
            hdr_cells = table.rows[0].cells
            for j, h in enumerate(header):
                render_inline(hdr_cells[j].paragraphs[0], h)
            for row in rows:
                row_cells = table.add_row().cells
                for j, cell in enumerate(row):
                    if j < len(row_cells):
                        render_inline(row_cells[j].paragraphs[0], cell)
        elif kind == "rule":
            doc.add_paragraph("_" * 50)

    if doc.paragraphs and doc.paragraphs[0].style.name.startswith("Heading 1"):
        doc.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER

    output_path.parent.mkdir(parents=True, exist_ok=True)
    doc.save(output_path)
    print(f"DOCX written to {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Convert Markdown report to DOCX")
    parser.add_argument("input", type=Path, help="Input Markdown file")
    parser.add_argument("output", type=Path, help="Output DOCX file")
    args = parser.parse_args()
    md_to_docx(args.input, args.output)


if __name__ == "__main__":
    main()
