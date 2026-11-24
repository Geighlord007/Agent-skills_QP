#!/usr/bin/env python3
"""
Generate a BG-info Word document from structured JSON data.
Usage: python generate_bg_doc.py --input output/tmp/data.json --output output/Company_BG_info.docx

The JSON schema is defined in references/schema.json.
Narrative string fields support Markdown-style inline hyperlinks: [text](https://...).
"""

import argparse
import json
from pathlib import Path
import re
import sys

for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8", errors="replace")

try:
    from docx import Document
    from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT, WD_TABLE_ALIGNMENT
    from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn
    from docx.shared import Inches, Pt, RGBColor
except ImportError:
    print("ERROR: python-docx is required. Install: pip install python-docx", file=sys.stderr)
    sys.exit(1)

# Allow importing sibling validator regardless of current working directory
_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from validate_bg_json import validate  # noqa: E402

# ── Colour palette ───────────────────────────────────────────────────────────
DARK_GREY = RGBColor(0x33, 0x33, 0x33)
GREEN = RGBColor(0x61, 0x7D, 0x24)
MED_GREY = RGBColor(0x66, 0x66, 0x66)
LIGHT_GREY = "E5E5E5"
LINK_BLUE_HEX = "0563C1"

FONT_NAME = "Schibsted Grotesk"
RE_MD_LINK = re.compile(r"\[([^\]]+)\]\((https?://[^\s\)]+)\)")


def _set_rfonts(rPr, name: str) -> None:
    rFonts = rPr.find(qn("w:rFonts"))
    if rFonts is None:
        rFonts = OxmlElement("w:rFonts")
        rPr.insert(0, rFonts)
    rFonts.set(qn("w:ascii"), name)
    rFonts.set(qn("w:hAnsi"), name)
    rFonts.set(qn("w:eastAsia"), name)


def add_hyperlink(paragraph, text: str, url: str, font_name: str = FONT_NAME, size_pt: float = 10.0):
    """Insert a valid OOXML blue, underlined hyperlink with explicit font and <w:t> node."""
    part = paragraph.part
    r_id = part.relate_to(
        url,
        "http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink",
        is_external=True,
    )
    hyperlink = OxmlElement("w:hyperlink")
    hyperlink.set(qn("r:id"), r_id)
    hyperlink.set(qn("w:history"), "1")

    new_run = OxmlElement("w:r")
    rPr = OxmlElement("w:rPr")
    _set_rfonts(rPr, font_name)

    color = OxmlElement("w:color")
    color.set(qn("w:val"), LINK_BLUE_HEX)
    rPr.append(color)

    half_pts = str(int(round(size_pt * 2)))
    sz = OxmlElement("w:sz")
    sz.set(qn("w:val"), half_pts)
    rPr.append(sz)
    szCs = OxmlElement("w:szCs")
    szCs.set(qn("w:val"), half_pts)
    rPr.append(szCs)

    u = OxmlElement("w:u")
    u.set(qn("w:val"), "single")
    rPr.append(u)

    new_run.append(rPr)

    t_el = OxmlElement("w:t")
    t_el.set(qn("xml:space"), "preserve")
    t_el.text = text
    new_run.append(t_el)

    hyperlink.append(new_run)
    paragraph._p.append(hyperlink)
    return hyperlink


def _style_run(run, name=FONT_NAME, size=Pt(10), color=DARK_GREY, bold=False, italic=False) -> None:
    run.font.name = name
    run.font.size = size
    run.font.color.rgb = color
    run.font.bold = bold
    run.font.italic = italic
    rPr = run._element.get_or_add_rPr()
    _set_rfonts(rPr, name)


def add_rich_text(paragraph, text: str, name=FONT_NAME, size=Pt(10), color=DARK_GREY, bold=False, italic=False) -> None:
    """Append text to paragraph, converting Markdown [label](https://...) links to OOXML hyperlinks."""
    if not text:
        return
    pos = 0
    size_pt = size.pt if hasattr(size, "pt") else 10.0
    for m in RE_MD_LINK.finditer(text):
        if m.start() > pos:
            run = paragraph.add_run(text[pos:m.start()])
            _style_run(run, name=name, size=size, color=color, bold=bold, italic=italic)
        add_hyperlink(paragraph, m.group(1), m.group(2), font_name=name, size_pt=size_pt)
        pos = m.end()
    if pos < len(text):
        run = paragraph.add_run(text[pos:])
        _style_run(run, name=name, size=size, color=color, bold=bold, italic=italic)


def shade_cell(cell, fill: str = LIGHT_GREY) -> None:
    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), fill)
    cell._tc.get_or_add_tcPr().append(shd)


def add_table(doc, headers: list[str], rows: list[list[str]]):
    table = doc.add_table(rows=1, cols=len(headers))
    table.style = "Table Grid"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER

    hdr = table.rows[0].cells
    for i, h in enumerate(headers):
        p = hdr[i].paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        add_rich_text(p, str(h), bold=True, size=Pt(9))
        hdr[i].vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
        shade_cell(hdr[i])

    for row_data in rows:
        row = table.add_row().cells
        for i, txt in enumerate(row_data):
            p = row[i].paragraphs[0]
            add_rich_text(p, str(txt), size=Pt(9))
            row[i].vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER

    return table


def add_styled(
    doc,
    text: str,
    style: str = "Normal",
    bold: bool = False,
    size=Pt(10),
    color=DARK_GREY,
    align=WD_ALIGN_PARAGRAPH.LEFT,
    space_after=Pt(6),
    space_before=None,
    italic: bool = False,
):
    p = doc.add_paragraph(style=style)
    p.alignment = align
    if space_after is not None:
        p.paragraph_format.space_after = space_after
    if space_before is not None:
        p.paragraph_format.space_before = space_before
    if text:
        add_rich_text(p, text, size=size, color=color, bold=bold, italic=italic)
    return p


def add_section_heading(doc, title: str, level: int = 1):
    style = "Heading 1" if level == 1 else "Heading 2"
    space_after = Pt(6) if level == 1 else Pt(4)
    return add_styled(
        doc,
        title,
        style=style,
        bold=True,
        size=Pt(10),
        color=GREEN,
        space_after=space_after,
        space_before=None,  # Preserve Heading 1/2 style's 12pt space_before
    )


def _check_image_path(image_path: str, label: str, allow_missing: bool) -> Path | None:
    p = Path(image_path)
    if p.is_file():
        return p
    msg = f"ERROR: {label} image not found: {image_path}"
    if allow_missing:
        print(f"WARNING: {label} image not found (skipped): {image_path}", file=sys.stderr)
        return None
    print(msg + " (pass --allow-missing-images to skip)", file=sys.stderr)
    sys.exit(1)


def add_image_with_caption(
    doc,
    image_path: str,
    caption: str,
    width=Inches(5.5),
    allow_missing: bool = False,
) -> None:
    resolved = _check_image_path(image_path, "Strategic", allow_missing)
    if resolved is None:
        return
    p_img = doc.add_paragraph()
    p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_img.add_run().add_picture(str(resolved), width=width)
    cap = doc.add_paragraph()
    cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    add_rich_text(cap, caption, size=Pt(8), italic=True, color=MED_GREY)


def build_document(data: dict, output_path: str, allow_missing_images: bool = False) -> None:
    doc = Document()
    section = doc.sections[0]
    section.page_width = Inches(8.27)
    section.page_height = Inches(11.69)
    section.left_margin = Inches(1.0)
    section.right_margin = Inches(1.0)
    section.top_margin = Inches(1.0)
    section.bottom_margin = Inches(1.0)

    # Normal style
    normal = doc.styles["Normal"]
    normal.font.name = FONT_NAME
    normal.font.size = Pt(10)
    normal.font.color.rgb = DARK_GREY
    normal.paragraph_format.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
    _set_rfonts(normal.element.get_or_add_rPr(), FONT_NAME)

    # Heading styles
    for name in ("Heading 1", "Heading 2"):
        s = doc.styles[name]
        s.font.name = FONT_NAME
        s.font.size = Pt(10)
        s.font.bold = True
        s.font.color.rgb = GREEN
        s.paragraph_format.space_before = Pt(12)
        s.paragraph_format.space_after = Pt(6)
        _set_rfonts(s.element.get_or_add_rPr(), FONT_NAME)

    # Optional top-right company logo
    if data.get("logo_path"):
        resolved_logo = _check_image_path(data["logo_path"], "Logo", allow_missing_images)
        if resolved_logo is not None:
            p_logo = doc.add_paragraph()
            p_logo.alignment = WD_ALIGN_PARAGRAPH.RIGHT
            p_logo.paragraph_format.space_after = Pt(4)
            p_logo.add_run().add_picture(str(resolved_logo), width=Inches(1.2))

    # ── 1. Title ────────────────────────────────────────────────────────────
    add_styled(
        doc,
        f"{data['company_name']} BG info",
        size=Pt(14),
        bold=True,
        space_before=Pt(0),
        space_after=Pt(2),
    )

    # ── 2. Main heading ─────────────────────────────────────────────────────
    add_styled(
        doc,
        data["company_name"],
        size=Pt(18),
        bold=True,
        space_before=Pt(0),
        space_after=Pt(8),
    )

    # ── 3. Company overview ─────────────────────────────────────────────────
    for para in str(data.get("overview", "")).split("\n\n"):
        if para.strip():
            add_styled(doc, para.strip(), space_before=Pt(0))

    # ── 4. Strategic context ────────────────────────────────────────────────
    add_section_heading(doc, "Strategic context", level=1)
    add_styled(doc, data.get("strategic_context", ""), space_before=Pt(0))
    if data.get("strategic_image"):
        add_image_with_caption(
            doc,
            data["strategic_image"],
            data.get("strategic_image_caption", "Figure 1."),
            allow_missing=allow_missing_images,
        )

    # ── 5. Operating divisions ──────────────────────────────────────────────
    add_section_heading(doc, "Operating divisions", level=1)
    divs = data.get("divisions", [])
    if divs:
        add_table(
            doc,
            ["Division", "Description", "Key brands / products", "Revenue / EBITDA"],
            [[d.get("name", ""), d.get("description", ""), d.get("brands", ""), d.get("revenue", "")] for d in divs],
        )
    else:
        add_styled(doc, "No division data provided.", italic=True, color=MED_GREY, space_before=Pt(0))

    # ── 6. Selected brands ──────────────────────────────────────────────────
    brands = data.get("brands", {})
    if brands:
        add_section_heading(doc, "Selected ingredient / product brands", level=1)
        for category, items in brands.items():
            add_section_heading(doc, category, level=2)
            for item in items:
                add_styled(doc, f"• {item}", space_before=Pt(0))

    # ── 7. Key financials ───────────────────────────────────────────────────
    fins = data.get("financials", [])
    if fins:
        add_section_heading(doc, "Key financials", level=1)
        headers = ["Metric"] + [f["year"] for f in fins]
        all_metrics = list(dict.fromkeys(
            metric for f in fins for metric in f.get("metrics", {}).keys()
        ))
        rows = [
            [metric] + [f.get("metrics", {}).get(metric, "") for f in fins]
            for metric in all_metrics
        ]
        add_table(doc, headers, rows)

    # ── 8. Alternative proteins / precision fermentation ────────────────────
    add_section_heading(
        doc,
        "Alternative proteins / precision fermentation / relevant technology layout",
        level=1,
    )
    alt = data.get("alternative_proteins", {})
    if not alt or not any(alt.get(k) for k in ("public_statements", "initiatives", "partnerships", "investments", "ma_deals")):
        add_styled(
            doc,
            "No public internal platform announced; strategic interest not yet signalled.",
            space_before=Pt(0),
        )
    else:
        for key in ("public_statements", "initiatives", "partnerships", "investments", "ma_deals"):
            val = alt.get(key)
            if val:
                add_section_heading(doc, key.replace("_", " ").title(), level=2)
                if isinstance(val, list):
                    for v in val:
                        add_styled(doc, f"• {v}", space_before=Pt(0))
                else:
                    add_styled(doc, str(val), space_before=Pt(0))

    # ── 9. Recent M&A / transactions ────────────────────────────────────────
    ma = data.get("ma_transactions", [])
    if ma:
        add_section_heading(doc, "Recent M&A / transactions", level=1)
        add_table(
            doc,
            ["Year", "Target / asset", "Transaction amount", "Description"],
            [[m.get("year", ""), m.get("target", ""), m.get("amount", ""), m.get("description", "")] for m in ma],
        )

    # ── 10. Innovation & partnership landscape ──────────────────────────────
    add_section_heading(doc, "Innovation & partnership landscape", level=1)
    for key in ("open_innovation", "relevant_products", "pf_stance", "collaboration_hook"):
        val = data.get("innovation", {}).get(key)
        if val:
            add_section_heading(doc, key.replace("_", " ").title(), level=2)
            add_styled(doc, str(val), space_before=Pt(0))

    # ── 11. Sources ─────────────────────────────────────────────────────────
    add_section_heading(doc, "Sources", level=1)
    for src in data.get("sources", []):
        p = doc.add_paragraph(style="List Bullet")
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(3)
        add_hyperlink(p, src.get("label") or src["url"], src["url"])

    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(out))
    print(f"Saved: {out}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate BG-info DOCX from JSON")
    parser.add_argument("--input", "-i", required=True, help="Path to JSON data file")
    parser.add_argument("--output", "-o", required=True, help="Output DOCX path")
    parser.add_argument("--allow-missing-images", action="store_true",
                        help="Warn and skip missing logo/strategic images instead of failing")
    parser.add_argument("--skip-validation", action="store_true",
                        help="Skip built-in JSON schema validation before rendering")
    args = parser.parse_args()

    try:
        with open(args.input, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        print(f"ERROR: Could not read JSON file: {e}", file=sys.stderr)
        sys.exit(1)

    if not args.skip_validation:
        errors = validate(data)
        if errors:
            print("VALIDATION FAILED:", file=sys.stderr)
            for err in errors:
                print(f"  - {err}", file=sys.stderr)
            sys.exit(1)

    build_document(data, args.output, allow_missing_images=args.allow_missing_images)


if __name__ == "__main__":
    main()
