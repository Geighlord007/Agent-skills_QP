#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
DOCX brand engine — applies a document standard to a set of files.

One function applies the whole visual identity to an existing .docx, so that every
document produced by any workstream is indistinguishable in style:

    from docx_brand import apply_brand
    apply_brand("path/to/report.docx", kicker="PLATFORM / HOST & STRAIN",
                title="A. niger Strain Selection",
                statement="Thirteen candidates, one decision.",
                revision=dict(date="2026-09-11", status="VERIFIED",
                              supersedes="(none)", original="2026-04-30"))

Restyling is non-destructive: paragraph text is never altered, only formatting. It is
safe to run on a document that has already been translated.

Rationale for every value: _admin/DESIGN_SYSTEM.md.
"""
from __future__ import annotations

import copy
import os

try:
    import _paths as _P
except ImportError:  # when bundled elsewhere
    import importlib.util as _u, os as _o
    _sp = _u.spec_from_file_location("_paths", _o.path.join(_o.path.dirname(_o.path.abspath(__file__)), "_paths.py"))
    _P = _u.module_from_spec(_sp); _sp.loader.exec_module(_P)
import re

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from design import brand as B  # noqa: E402

CJK = re.compile(r"[\u4e00-\u9fff]")

FONTS = {"serif": B.FONT_SERIF, "sans": B.FONT_SANS, "mono": B.FONT_MONO}
# Word needs an East-Asian face too or it silently substitutes a CJK font
# The East-Asian face, from the specification. Was hard-coded to "SimSun",
# which the spec does not name; Word applies this face to every CJK run.
EA_FACE = getattr(B, "FONT_CJK", "Arial")


# ---------------------------------------------------------------------------
# low-level helpers
# ---------------------------------------------------------------------------
def _rgb(hexstr: str) -> RGBColor:
    h = hexstr.lstrip("#")
    return RGBColor(int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


def _set_run(run, font_key: str, size_pt: float, color: str,
             italic: bool = False, caps: bool = False, tracking_pt: float | None = None):
    run.font.name = FONTS[font_key]
    run.font.size = Pt(size_pt)
    run.font.color.rgb = _rgb(color)
    run.font.italic = italic
    run.font.bold = False                       # system has no bold headlines
    rpr = run._element.get_or_add_rPr()
    rf = rpr.find(qn("w:rFonts"))
    if rf is None:
        rf = OxmlElement("w:rFonts")
        rpr.insert(0, rf)
    for attr in ("w:ascii", "w:hAnsi", "w:cs"):
        rf.set(qn(attr), FONTS[font_key])
    rf.set(qn("w:eastAsia"), EA_FACE)
    if caps:
        _insert_rpr(rpr, "w:caps").set(qn("w:val"), "1")
    if tracking_pt is not None:                 # w:spacing is in twentieths of a point
        # OOXML fixes the order of w:rPr children (CT_RPr). w:spacing belongs AFTER
        # w:color and BEFORE w:sz. Appending it blindly, as this used to, also left
        # duplicates on runs that were styled twice. Word tolerates both, but a
        # schema-ordered, deduplicated rPr is what Word round-trips unchanged.
        for old in rpr.findall(qn("w:spacing")):
            rpr.remove(old)
        _insert_rpr(rpr, "w:spacing").set(qn("w:val"), str(int(tracking_pt * 20)))


# CT_RPr child order, truncated to the elements this module ever writes.
_RPR_ORDER = ("w:rStyle", "w:rFonts", "w:b", "w:bCs", "w:i", "w:iCs", "w:caps",
              "w:smallCaps", "w:strike", "w:dstrike", "w:color", "w:spacing", "w:w",
              "w:kern", "w:position", "w:sz", "w:szCs", "w:highlight", "w:u")


def _insert_rpr(rpr, tag: str):
    """Insert a child into w:rPr at its schema position, not blindly at the end."""
    el = OxmlElement(tag)
    try:
        idx = _RPR_ORDER.index(tag)
    except ValueError:
        rpr.append(el)
        return el
    for child in rpr:
        name = child.tag.split("}")[-1]
        if "w:" + name in _RPR_ORDER[_RPR_ORDER.index(tag) + 1:]:
            child.addprevious(el)
            return el
    rpr.append(el)
    return el


def _paragraph_spacing(p, before=0, after=0, line=1.52):
    pf = p.paragraph_format
    pf.space_before = Pt(before)
    pf.space_after = Pt(after)
    pf.line_spacing_rule = WD_LINE_SPACING.MULTIPLE
    pf.line_spacing = line


def _hairline(p, position: str = "bottom", size: int = 6, color: str = "000000"):
    """size is in eighths of a point: 6 = 0.75pt, 4 = 0.5pt."""
    ppr = p._element.get_or_add_pPr()
    borders = ppr.find(qn("w:pBdr"))
    if borders is None:
        borders = OxmlElement("w:pBdr")
        ppr.append(borders)
    el = OxmlElement(f"w:{position}")
    el.set(qn("w:val"), "single")
    el.set(qn("w:sz"), str(size))
    el.set(qn("w:space"), "6")
    el.set(qn("w:color"), color)
    borders.append(el)


TEXT_WIDTH_CM = 16.6          # A4 minus the 2.2 cm margins


def _tab_stops(p, centre: float | None = None, right: float | None = None):
    """Explicit tab stops. Without them Word falls back to 1.25 cm, which collapses the
    header and footer furniture into the left-hand text."""
    from docx.enum.text import WD_TAB_ALIGNMENT
    ts = p.paragraph_format.tab_stops
    if centre is not None:
        ts.add_tab_stop(Cm(centre), WD_TAB_ALIGNMENT.CENTER)
    if right is not None:
        ts.add_tab_stop(Cm(right), WD_TAB_ALIGNMENT.RIGHT)


def _shade(cell, hexcolor: str):
    tcpr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), hexcolor.lstrip("#"))
    tcpr.append(shd)


def _cell_borders(cell, color="000000", size=4, edges=("top", "left", "bottom", "right")):
    tcpr = cell._tc.get_or_add_tcPr()
    existing = tcpr.find(qn("w:tcBorders"))
    if existing is not None:
        tcpr.remove(existing)
    borders = OxmlElement("w:tcBorders")
    for edge in ("top", "left", "bottom", "right"):
        e = OxmlElement(f"w:{edge}")
        if edge in edges:
            e.set(qn("w:val"), "single")
            e.set(qn("w:sz"), str(size))
            e.set(qn("w:color"), color)
        else:
            e.set(qn("w:val"), "none")
            e.set(qn("w:sz"), "0")
        borders.append(e)
    tcpr.append(borders)


def _set_col_widths(table, widths_cm: list[float]):
    """python-docx needs the width set on every cell, not just the column."""
    table.autofit = False
    tblpr = table._tbl.tblPr
    layout = OxmlElement("w:tblLayout")
    layout.set(qn("w:type"), "fixed")
    tblpr.append(layout)
    for row in table.rows:
        for i, cell in enumerate(row.cells):
            if i < len(widths_cm):
                cell.width = Cm(widths_cm[i])
    for i, col in enumerate(table.columns):
        if i < len(widths_cm):
            col.width = Cm(widths_cm[i])


def _force_fonts(doc):
    """Make the brand faces the document defaults so unstyled runs inherit them."""
    styles = doc.styles.element
    dd = styles.find(qn("w:docDefaults"))
    if dd is None:
        return
    rpr_def = dd.find(qn("w:rPrDefault"))
    if rpr_def is None:
        return
    rpr = rpr_def.find(qn("w:rPr"))
    if rpr is None:
        rpr = OxmlElement("w:rPr")
        rpr_def.append(rpr)
    rf = rpr.find(qn("w:rFonts"))
    if rf is None:
        rf = OxmlElement("w:rFonts")
        rpr.insert(0, rf)
    for attr, val in (("w:ascii", B.FONT_SERIF), ("w:hAnsi", B.FONT_SERIF),
                      ("w:cs", B.FONT_SERIF), ("w:eastAsia", EA_FACE)):
        rf.set(qn(attr), val)


def _page_setup(doc):
    for s in doc.sections:
        s.page_width, s.page_height = Cm(21.0), Cm(29.7)
        s.top_margin = s.bottom_margin = Cm(2.2)
        s.left_margin = s.right_margin = Cm(2.2)
        s.header_distance = Cm(1.2)
        s.footer_distance = Cm(1.2)


def _field(paragraph, instr: str, font_key="mono", size=8.0, color=B.INK_MUTED):
    """Insert a Word field (PAGE, NUMPAGES, TOC)."""
    run = paragraph.add_run()
    _set_run(run, font_key, size, color)
    fld_begin = OxmlElement("w:fldChar")
    fld_begin.set(qn("w:fldCharType"), "begin")
    instr_el = OxmlElement("w:instrText")
    instr_el.set(qn("xml:space"), "preserve")
    instr_el.text = instr
    fld_end = OxmlElement("w:fldChar")
    fld_end.set(qn("w:fldCharType"), "end")
    run._element.append(fld_begin)
    run._element.append(instr_el)
    run._element.append(fld_end)


# ---------------------------------------------------------------------------
# page furniture
# ---------------------------------------------------------------------------
def _header_footer(doc, title: str, section_label: str = ""):
    for s in doc.sections:
        # the cover is its own visual space: no header, no footer on page 1
        s.different_first_page_header_footer = True
        s.first_page_header.is_linked_to_previous = False
        s.first_page_footer.is_linked_to_previous = False
        for p in list(s.first_page_header.paragraphs) + list(s.first_page_footer.paragraphs):
            for r in list(p.runs):
                r._element.getparent().remove(r._element)

        hdr = s.header
        hdr.is_linked_to_previous = False
        p = hdr.paragraphs[0] if hdr.paragraphs else hdr.add_paragraph()
        for r in list(p.runs):
            r._element.getparent().remove(r._element)
        p.text = ""
        run = p.add_run(title[:70])
        _set_run(run, "mono", 8, B.INK_MUTED)
        if section_label:
            run2 = p.add_run("\t" + section_label[:40])
            _set_run(run2, "mono", 8, B.INK_MUTED)
        _paragraph_spacing(p, 0, 6, 1.0)
        _tab_stops(p, right=TEXT_WIDTH_CM)          # right-align the section label
        _hairline(p, "bottom", size=4)

        ftr = s.footer
        ftr.is_linked_to_previous = False
        fp = ftr.paragraphs[0] if ftr.paragraphs else ftr.add_paragraph()
        for r in list(fp.runs):
            r._element.getparent().remove(r._element)
        fp.text = ""
        r1 = fp.add_run(_P.DOCSET_TITLE)
        _set_run(r1, "mono", 7.5, B.INK_MUTED)
        r2 = fp.add_run("\t")
        _set_run(r2, "mono", 7.5, B.INK_MUTED)
        _field(fp, " PAGE ")
        r3 = fp.add_run("\tVERIFIED · ESTIMATED · UNVERIFIED")
        _set_run(r3, "mono", 7.5, B.INK_MUTED)
        _paragraph_spacing(fp, 6, 0, 1.0)
        _tab_stops(fp, centre=TEXT_WIDTH_CM / 2, right=TEXT_WIDTH_CM)   # page number centred
        _hairline(fp, "top", size=4)


# ---------------------------------------------------------------------------
# cover + revision block
# ---------------------------------------------------------------------------
def _cover(doc, kicker: str, title: str, statement: str, theme: str = "synbio"):
    """A cover that is a distinct visual space, not a big first paragraph.

    Vertical rhythm: a deliberate band of air at the top, the identity block at the
    optical upper-third, the statement set off by a hairline, then a long fall of
    whitespace before the colophon sitting just above the page break.
    """
    for _ in range(5):
        doc.add_paragraph()

    p = doc.add_paragraph()
    _paragraph_spacing(p, 0, 14, 1.1)
    r = p.add_run((kicker or _P.DOCSET_TITLE).upper())
    _set_run(r, "mono", 8.5, B.INK_MUTED, caps=True, tracking_pt=0.9)

    p = doc.add_paragraph()
    _paragraph_spacing(p, 0, 4, 1.12)
    r = p.add_run(title)
    _set_run(r, "sans", B.TYPE["display"], B.INK, tracking_pt=-0.3)

    if statement:
        p = doc.add_paragraph()
        # 22 pt of space before the rule, and a 1.45 line so the italic ascenders of a
        # 31 pt line never reach the hairline
        _paragraph_spacing(p, 0, 0, 1.45)
        p.paragraph_format.space_before = Pt(22)
        _hairline(p, "top", size=4)
        r = p.add_run(statement)
        # the signature move: italic serif phrase set LARGER than the surrounding sans
        _set_run(r, "serif", B.TYPE["display"] + 1.0, B.INK_2, italic=True)

    # Deterministic fall of whitespace: ONE paragraph carrying an explicit space-before,
    # rather than a run of empty paragraphs whose height depends on the inherited style
    # (which overflows differently per page setup and pushes the colophon onto page 2).
    p = doc.add_paragraph()
    _paragraph_spacing(p, 0, 8, 1.15)
    p.paragraph_format.space_before = Pt(270)
    _hairline(p, "top", size=4)
    r = p.add_run(_P.BRAND_NAME)
    _set_run(r, "mono", 8, B.INK)
    r = p.add_run("\t" + _P.DOCSET_TITLE)
    _set_run(r, "mono", 8, B.INK_MUTED)
    doc.add_page_break()


def _revision_block(doc, rev: dict):
    if not rev:
        return
    p = doc.add_paragraph()
    _paragraph_spacing(p, 0, 4, 1.15)
    r = p.add_run(f"Revision Note — {rev.get('date', '')}")
    _set_run(r, "sans", 12, B.INK)
    _hairline(p, "bottom", size=4)

    rows = [
        ("Verified / updated", rev.get("updated", "—")),
        ("Confidence", rev.get("status", "UNVERIFIED")),
        ("Supersedes", rev.get("supersedes", "(none)")),
        ("Original research", rev.get("original", "—")),
    ]
    t = doc.add_table(rows=0, cols=2)
    t.alignment = WD_TABLE_ALIGNMENT.LEFT
    for k, v in rows:
        cells = t.add_row().cells
        for cell, txt, key in ((cells[0], k, True), (cells[1], v, False)):
            cell.text = ""
            par = cell.paragraphs[0]
            _paragraph_spacing(par, 3, 3, 1.2)
            run = par.add_run(txt)
            _set_run(run, "mono" if key else "sans", 7.5 if key else 9,
                     B.INK_MUTED if key else B.INK_2, caps=key)
            # editorial tables carry horizontal rules only, never a full grid
            _cell_borders(cell, size=4, edges=("bottom",))
    _set_col_widths(t, [4.2, 12.4])
    doc.add_paragraph()


# ---------------------------------------------------------------------------
# body restyle
# ---------------------------------------------------------------------------
def furniture_elements(doc):
    """The cover and the revision block, as stable XPath keys to leave alone.

    `_restyle_body` would otherwise re-style them on a second pass: they are ordinary
    Normal-styled body paragraphs and an ordinary table, so nothing distinguishes them
    structurally. The owner reviews the Revision Note by eye, so it must stay
    byte-identical through any restyle.

    Keys are `getroottree().getpath(...)` strings, NOT `id(el)`: lxml hands out a fresh
    proxy object on every attribute access, so `id(p._p)` never matches the `id()` of
    the element found while walking the body -- an identity set silently matches nothing.
    """
    from docx.oxml.ns import qn as _qn

    def key(el):
        return el.getroottree().getpath(el)

    paras, tables = set(), set()
    children = list(doc.element.body.iterchildren())
    # cover = everything up to and including the first explicit page break
    for i, el in enumerate(children):
        if el.tag == _qn("w:p") and any(
                br.get(_qn("w:type")) == "page" for br in el.iter(_qn("w:br"))):
            for prev in children[:i + 1]:
                if prev.tag == _qn("w:p"):
                    paras.add(key(prev))
            break
    # revision block = the "Revision Note" paragraph, its table, and the spacer after
    for i, el in enumerate(children):
        if el.tag == _qn("w:p") and el.xpath("string(.)").strip().startswith("Revision Note"):
            paras.add(key(el))
            j = i + 1
            while j < len(children) and children[j].tag != _qn("w:tbl"):
                if children[j].tag == _qn("w:p"):
                    paras.add(key(children[j]))
                j += 1
            if j < len(children):
                tables.add(key(children[j]))
                k = j + 1
                while k < len(children) and children[k].tag == _qn("w:p"):
                    if not children[k].xpath("string(.)").strip():
                        paras.add(key(children[k]))
                        break
                    k += 1
            break
    return paras, tables


def _para_key(p):
    return p._p.getroottree().getpath(p._p)


def _restyle_body(doc, skip_paras=frozenset()):
    for p in doc.paragraphs:
        if _para_key(p) in skip_paras:
            continue
        style = (p.style.name or "") if p.style is not None else ""
        text = p.text.strip()
        if not text:
            continue
        # flush left, no first-line indent -- DOCUMENT_STANDARD.md section 4
        p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.first_line_indent = None
        p.paragraph_format.widow_control = True

        lower = style.lower()
        if "heading 1" in lower or lower == "title":
            for r in p.runs:
                _set_run(r, "sans", B.TYPE["h1"], B.INK)
            _paragraph_spacing(p, 20, 8, 1.18)
            _hairline(p, "bottom", size=4)
            p.paragraph_format.keep_with_next = True
        elif "heading 2" in lower:
            for r in p.runs:
                _set_run(r, "sans", B.TYPE["h2"], B.INK)
            _paragraph_spacing(p, 16, 6, 1.25)
            p.paragraph_format.keep_with_next = True
        elif "heading" in lower or "subtitle" in lower:
            for r in p.runs:
                _set_run(r, "sans", B.TYPE["h3"], B.INK)
            _paragraph_spacing(p, 12, 4, 1.30)
            p.paragraph_format.keep_with_next = True
        elif text.lower().startswith("source:"):
            for r in p.runs:
                _set_run(r, "mono", B.TYPE["kicker"], B.INK_MUTED)
            _paragraph_spacing(p, 0, 14, 1.35)
        elif lower.startswith("caption") or text.lower().startswith(("figure ", "table ")):
            for r in p.runs:
                _set_run(r, "serif", B.TYPE["caption"], B.INK_2, italic=True)
            _paragraph_spacing(p, 0, 2, 1.40)
        else:
            # body copy is SANS per the standard; the serif italic phrase is the accent
            for r in p.runs:
                _set_run(r, "sans", B.TYPE["body"], B.INK_2, tracking_pt=B.TRACKING_BODY_PT)
            _paragraph_spacing(p, 0, 6, B.LEADING_BODY)


def _restyle_tables(doc, skip_tables=frozenset(), skip_paras=frozenset()):
    """Editorial tables: a shaded header band, horizontal hairlines only, no grid."""
    for t in doc.tables:
        if t._tbl.getroottree().getpath(t._tbl) in skip_tables:
            continue
        t.alignment = WD_TABLE_ALIGNMENT.LEFT
        # fixed layout: three contradictory width declarations under autofit is what
        # once fragmented 'SKINCEUTICALS' into 'SKINCEUTI CALS'
        tblPr = t._tbl.tblPr
        for tag in ("w:tblLayout",):
            for el in tblPr.findall(qn(tag)):
                tblPr.remove(el)
        lay = OxmlElement("w:tblLayout")
        lay.set(qn("w:type"), "fixed")
        tblPr.append(lay)
        n = len(t.rows)
        for i, row in enumerate(t.rows):
            # Row-level borders live in w:tblPrEx and are NOT overridden by cell
            # borders. Styling only the cells is why Lignin Peroxidase still drew
            # 408 vertical segments after restyling: the row-level copy is what
            # actually strokes them. Remove it, then style the cells.
            trPr = row._tr.find(qn("w:trPr"))
            if trPr is not None:
                ex = trPr.find(qn("w:tblPrEx"))
                if ex is not None:
                    trPr.remove(ex)
            if i == 0:
                trPr = row._tr.get_or_add_trPr()
                for el in trPr.findall(qn("w:tblHeader")):
                    trPr.remove(el)
                hdr = OxmlElement("w:tblHeader")
                trPr.append(hdr)
            for cell in row.cells:
                if i == 0:
                    _cell_borders(cell, size=6, edges=("top", "bottom"))
                elif i == n - 1:
                    _cell_borders(cell, size=6, edges=("bottom",))
                else:
                    _cell_borders(cell, size=4, edges=("bottom",))
                if i == 0:
                    _shade(cell, B.BONE)
                for p in cell.paragraphs:
                    if p._p.getroottree().getpath(p._p) in skip_paras:
                        continue
                    # the standard is flush left everywhere, table cells included
                    p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT
                    p.paragraph_format.first_line_indent = None
                    _paragraph_spacing(p, 3, 3, 1.25)
                    for r in p.runs:
                        txt = r.text or ""
                        numeric = bool(re.fullmatch(r"[\s\d.,%$€£+\-/()<>~≈]*", txt)) and bool(txt.strip())
                        if i == 0:
                            _set_run(r, "mono", 7.5, B.INK, caps=True)
                        elif numeric:
                            _set_run(r, "mono", B.TYPE["numeric"], B.INK)
                        else:
                            _set_run(r, "sans", 9, B.INK_2)


# ---------------------------------------------------------------------------
# public entry point
# ---------------------------------------------------------------------------
def _drop_leading_title(doc, title: str, path: str = "") -> bool:
    """Remove a leading line that merely labels the document.

    Source documents usually open with their own label (the document's own title,
    'Chitin industry'). With a cover in place that line reads as a stray heading.
    Removed only when it is short, unpunctuated, and shares a meaningful token with
    the cover title or the filename — so genuine first paragraphs are never lost.
    """
    stop = {
        "the", "and", "for", "with", "from", "into", "info", "notes", "report", "study",
        "case", "market", "analysis", "overview", "group", "bg", "docx", "final", "draft",
    }
    def toks(s: str) -> set[str]:
        return {t for t in re.split(r"[^a-z0-9]+", (s or "").lower()) if len(t) >= 4 and t not in stop}

    ref = toks(title) | toks(os.path.splitext(os.path.basename(path))[0])
    for p in doc.paragraphs[:6]:
        txt = p.text.strip()
        if not txt:
            continue
        if len(txt) > 90 or len(txt.split()) > 9 or txt.rstrip().endswith((".", "?", "!", ":", ";")):
            return False
        if toks(txt) & ref:
            p._element.getparent().remove(p._element)
            return True
        return False
    return False


def has_brand_furniture(doc) -> bool:
    """True if `doc` already carries the injected cover and/or revision block.

    Detection keys on two strings that only this module ever writes: the cover's
    trailing tab-prefixed title mark, and the `Revision Note —` kicker.
    """
    for p in doc.paragraphs:
        t = p.text
        if t.startswith("Revision Note \u2014") or t == "\t" + _P.DOCSET_TITLE:
            return True
    return False


def apply_brand(path: str, kicker: str = "", title: str = "", statement: str = "",
                section_label: str = "", revision: dict | None = None,
                add_cover: bool = True, drop_leading_title: bool = True,
                theme: str = "synbio", out_path: str | None = None,
                force_furniture: bool = False) -> str:
    """Apply the whole brand identity to `path`. Returns the written path.

    Idempotent with respect to the cover and revision block: they are injected as
    new block-level content, so a second call on an already-branded file used to
    give it a second cover and a second revision table. Workstreams share these
    documents, so that is a real corruption vector and the guard below is an
    interlock. Pass `force_furniture=True` only to deliberately *refresh* the
    furniture of an already-branded file.
    """
    doc = Document(path)
    if not force_furniture and has_brand_furniture(doc):
        print(f"[docx_brand] {os.path.basename(path)} is already branded \u2014 "
              f"skipping cover and revision block (idempotent re-entry).",
              file=sys.stderr)
        add_cover, revision = False, None
    # The owner reviews the Revision Note by eye, so it must survive a restyle
    # byte-identically. The cover goes with it: both are ordinary body content as far
    # as python-docx is concerned, so they have to be excluded explicitly.
    f_paras, f_tables = furniture_elements(doc)
    if drop_leading_title and add_cover:
        _drop_leading_title(doc, title, path)
    _force_fonts(doc)
    _page_setup(doc)
    _restyle_body(doc, skip_paras=f_paras)
    _restyle_tables(doc, skip_tables=f_tables, skip_paras=f_paras)
    _header_footer(doc, title or os.path.basename(path), section_label)

    if add_cover:
        body = doc.element.body
        first = body.find(qn("w:p"))
        cover_doc = Document()
        _cover(cover_doc, kicker, title, statement, theme)
        anchor = first if first is not None else None
        for el in list(cover_doc.element.body):
            if el.tag == qn("w:sectPr"):
                continue
            if anchor is not None:
                anchor.addprevious(copy.deepcopy(el))
            else:
                body.append(copy.deepcopy(el))

    if revision:
        rev_doc = Document()
        _revision_block(rev_doc, revision)
        body = doc.element.body
        # place directly after the cover's page break
        anchor = None
        seen_break = False
        for el in body.iter():
            if el.tag == qn("w:br") and el.get(qn("w:type")) == "page":
                seen_break = True
                continue
            if seen_break and el.tag == qn("w:p"):
                anchor = el
                break
        for el in list(rev_doc.element.body):
            if el.tag == qn("w:sectPr"):
                continue
            if anchor is not None:
                anchor.addprevious(copy.deepcopy(el))
            else:
                body.append(copy.deepcopy(el))

    dst = out_path or path
    doc.save(dst)
    return dst


def cjk_report(path: str) -> dict:
    """Count residual Chinese characters, for the verification gate."""
    doc = Document(path)
    parts = [p.text for p in doc.paragraphs]
    for t in doc.tables:
        for row in t.rows:
            for c in row.cells:
                parts.append(c.text)
    txt = " ".join(parts)
    n = len(CJK.findall(txt))
    return {"cjk_chars": n, "words": len(txt.split()),
            "cjk_pct": round(100 * n / max(1, n + len(txt.split())), 2)}


if __name__ == "__main__":
    import argparse
    import json

    ap = argparse.ArgumentParser()
    ap.add_argument("docx")
    ap.add_argument("--kicker", default="")
    ap.add_argument("--title", default="")
    ap.add_argument("--statement", default="")
    ap.add_argument("--section", default="")
    ap.add_argument("--no-cover", action="store_true")
    ap.add_argument("--check", action="store_true", help="only report residual CJK")
    a = ap.parse_args()

    if a.check:
        print(json.dumps(cjk_report(a.docx), ensure_ascii=False))
    else:
        print(apply_brand(a.docx, kicker=a.kicker, title=a.title, statement=a.statement,
                          section_label=a.section, add_cover=not a.no_cover))
