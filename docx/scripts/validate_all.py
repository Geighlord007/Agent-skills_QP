#!/usr/bin/env python3
"""
validate_all.py - Unified OOXML validation: element order auto-fix + business rules check.
Cross-platform: uses native `docx_lib` when available (Linux/WSL2 + Py3.12),
and seamlessly falls back to pure-Python OOXML fixers & validators on Windows/macOS/Py3.13+.

Usage: python scripts/validate_all.py <file.docx>
"""

import shutil
import struct
import sys
import tempfile
import zipfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from xml.etree import ElementTree as ET

# Register standard OOXML namespaces so ElementTree preserves prefixes on write
OOXML_NAMESPACES = {
    "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "wp": "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing",
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "pic": "http://schemas.openxmlformats.org/drawingml/2006/picture",
    "c": "http://schemas.openxmlformats.org/drawingml/2006/chart",
    "m": "http://schemas.openxmlformats.org/officeDocument/2006/math",
    "mc": "http://schemas.openxmlformats.org/markup-compatibility/2006",
    "w14": "http://schemas.microsoft.com/office/word/2010/wordml",
    "w15": "http://schemas.microsoft.com/office/word/2012/wordml",
    "v": "urn:schemas-microsoft-com:vml",
    "o": "urn:schemas-microsoft-com:office:office",
}
for _prefix, _uri in OOXML_NAMESPACES.items():
    ET.register_namespace(_prefix, _uri)

W_NS = OOXML_NAMESPACES["w"]
R_NS = OOXML_NAMESPACES["r"]
WP_NS = OOXML_NAMESPACES["wp"]
A_NS = OOXML_NAMESPACES["a"]
REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"
CT_NS = "http://schemas.openxmlformats.org/package/2006/content-types"


def _w(tag: str) -> str:
    return f"{{{W_NS}}}{tag}"


def _local(tag: str) -> str:
    return tag.split("}", 1)[-1] if "}" in tag else tag


# ---------------------------------------------------------------------------
# Pure-Python fallback implementations (used on Windows / macOS / Python 3.13+)
# ---------------------------------------------------------------------------

# Authoritative OOXML WordprocessingML child-element orders for common containers
XSD_ELEMENT_ORDERS: Dict[str, List[str]] = {
    "pPr": [
        "pStyle", "keepNext", "keepLines", "pageBreakBefore", "framePr", "widowControl",
        "numPr", "suppressLineNumbers", "pBdr", "shd", "tabs", "suppressAutoHyphens",
        "kinsoku", "wordWrap", "overflowPunct", "topLinePunct", "autoSpaceDE",
        "autoSpaceDN", "bidi", "adjustRightInd", "snapToGrid", "spacing", "ind",
        "contextualSpacing", "mirrorIndents", "suppressOverlap", "jc", "textDirection",
        "textAlignment", "textboxTightWrap", "outlineLvl", "divId", "cnfStyle",
        "rPr", "sectPr", "pPrChange",
    ],
    "rPr": [
        "rStyle", "rFonts", "b", "bCs", "i", "iCs", "caps", "smallCaps", "strike",
        "dstrike", "outline", "shadow", "emboss", "imprint", "noProof", "snapToGrid",
        "vanish", "webHidden", "color", "spacing", "w", "kern", "position", "sz",
        "szCs", "highlight", "u", "effect", "bdr", "shd", "fitText", "vertAlign",
        "rtl", "cs", "em", "lang", "eastAsianLayout", "specVanish", "oMath", "rPrChange",
    ],
    "tblPr": [
        "tblStyle", "tblpPr", "tblOverlap", "bidiVisual", "tblStyleRowBandSize",
        "tblStyleColBandSize", "tblW", "jc", "tblCellSpacing", "tblInd", "tblBorders",
        "shd", "tblLayout", "tblCellMar", "tblLook", "tblCaption", "tblDescription",
        "tblPrChange",
    ],
    "trPr": [
        "cnfStyle", "divId", "gridBefore", "gridAfter", "wBefore", "wAfter",
        "cantSplit", "trHeight", "tblHeader", "tblCellSpacing", "jc", "hidden",
        "ins", "del", "trPrChange",
    ],
    "tcPr": [
        "cnfStyle", "tcW", "gridSpan", "hMerge", "vMerge", "tcBorders", "shd",
        "noWrap", "tcMar", "textDirection", "tcFitText", "vAlign", "hideMark",
        "headers", "cellIns", "cellDel", "cellMerge", "tcPrChange",
    ],
    "sectPr": [
        "headerReference", "footerReference", "footnotePr", "endnotePr", "type",
        "pgSz", "pgMar", "paperSrc", "pgBorders", "lnNumType", "pgNumType", "cols",
        "formProt", "vAlign", "noEndnote", "titlePg", "textDirection", "bidi",
        "rtlGutter", "docGrid", "printerSettings", "sectPrChange",
    ],
    "tblBorders": ["top", "left", "start", "bottom", "right", "end", "insideH", "insideV"],
    "tcBorders": ["top", "left", "start", "bottom", "right", "end", "insideH", "insideV", "tl2br", "tr2bl"],
    "pBdr": ["top", "left", "bottom", "right", "between", "bar"],
    "tcMar": ["top", "left", "start", "bottom", "right", "end"],
    "tblCellMar": ["top", "left", "start", "bottom", "right", "end"],
}


def _py_fix_element_order_in_tree(root: ET.Element) -> int:
    fixes = 0
    for elem in root.iter():
        order = XSD_ELEMENT_ORDERS.get(_local(elem.tag))
        if not order or len(elem) < 2:
            continue
        rank = {name: idx for idx, name in enumerate(order)}
        children = list(elem)
        sorted_children = sorted(
            children,
            key=lambda c: (rank.get(_local(c.tag), len(order)), children.index(c)),
        )
        if sorted_children != children:
            elem[:] = sorted_children
            fixes += 1

    # Ensure sectPr is the last child of w:body if present
    if _local(root.tag) == "document":
        body = root.find(_w("body"))
        if body is not None:
            sect_prs = [c for c in list(body) if _local(c.tag) == "sectPr"]
            if sect_prs and body[-1] is not sect_prs[-1]:
                for sp in sect_prs:
                    body.remove(sp)
                    body.append(sp)
                fixes += 1
    return fixes


def _py_fix_settings(root: ET.Element) -> int:
    """Minimal safe normalization for word/settings.xml."""
    # Remove duplicate updateFields elements if accidentally appended twice
    fixes = 0
    seen_update = False
    for child in list(root):
        if _local(child.tag) == "updateFields":
            if seen_update:
                root.remove(child)
                fixes += 1
            else:
                seen_update = True
    return fixes


def _py_fix_table_width_conservative(root: ET.Element) -> int:
    """Ensure tables with tblGrid have tblW matching grid total when tblW is missing."""
    fixes = 0
    for tbl in root.iter(_w("tbl")):
        tbl_grid = tbl.find(_w("tblGrid"))
        tbl_pr = tbl.find(_w("tblPr"))
        if tbl_grid is None or tbl_pr is None:
            continue
        if tbl_pr.find(_w("tblW")) is not None:
            continue
        cols = tbl_grid.findall(_w("gridCol"))
        widths = []
        for col in cols:
            w_val = col.get(_w("w"))
            if w_val and w_val.isdigit():
                widths.append(int(w_val))
        if widths:
            tbl_w = ET.Element(_w("tblW"), {_w("w"): str(sum(widths)), _w("type"): "dxa"})
            tbl_pr.insert(0, tbl_w)
            fixes += 1
    return fixes


def _py_fix_relationship_paths(extract_dir: Path) -> int:
    fixes = 0
    ET.register_namespace("", REL_NS)
    for rels_file in extract_dir.rglob("*.rels"):
        try:
            tree = ET.parse(rels_file)
            root = tree.getroot()
        except ET.ParseError:
            continue
        changed = False
        for rel in root:
            target = rel.get("Target")
            if not target or rel.get("TargetMode") == "External":
                continue
            new_target = target.replace("\\", "/")
            if rels_file.parent.name == "_rels" and rels_file.parent.parent.name == "word":
                if new_target.startswith("/word/"):
                    new_target = new_target[len("/word/"):]
                elif new_target.startswith("word/"):
                    new_target = new_target[len("word/"):]
            if new_target != target:
                rel.set("Target", new_target)
                changed = True
                fixes += 1
        if changed:
            tree.write(rels_file, encoding="UTF-8", xml_declaration=True)
    return fixes


def _py_fix_content_types(extract_dir: Path) -> int:
    ct_path = extract_dir / "[Content_Types].xml"
    if not ct_path.exists():
        return 0
    ET.register_namespace("", CT_NS)
    try:
        tree = ET.parse(ct_path)
        root = tree.getroot()
    except ET.ParseError:
        return 0

    known_mime = {
        "png": "image/png",
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "gif": "image/gif",
        "bmp": "image/bmp",
        "svg": "image/svg+xml",
        "emf": "image/x-emf",
        "wmf": "image/x-wmf",
    }
    existing_exts = {
        elem.get("Extension", "").lower()
        for elem in root
        if _local(elem.tag) == "Default"
    }
    needed_exts = {
        f.suffix.lstrip(".").lower()
        for f in (extract_dir / "word" / "media").rglob("*")
        if f.is_file() and f.suffix
    } if (extract_dir / "word" / "media").is_dir() else set()

    fixes = 0
    for ext in sorted(needed_exts - existing_exts):
        mime = known_mime.get(ext)
        if mime:
            ET.SubElement(root, f"{{{CT_NS}}}Default", {"Extension": ext, "ContentType": mime})
            fixes += 1
    if fixes:
        tree.write(ct_path, encoding="UTF-8", xml_declaration=True)
    return fixes


def _py_check_table_grid_consistency(root: ET.Element) -> List[str]:
    errors: List[str] = []
    for idx, tbl in enumerate(root.iter(_w("tbl")), start=1):
        tbl_grid = tbl.find(_w("tblGrid"))
        if tbl_grid is None:
            errors.append(f"TABLE #{idx}: missing <w:tblGrid>")
            continue
        grid_cols = len(tbl_grid.findall(_w("gridCol")))
        if grid_cols == 0:
            errors.append(f"TABLE #{idx}: <w:tblGrid> has 0 <w:gridCol> elements")
            continue
        for r_idx, tr in enumerate(tbl.findall(_w("tr")), start=1):
            span_total = 0
            for tc in tr.findall(_w("tc")):
                tc_pr = tc.find(_w("tcPr"))
                gs = tc_pr.find(_w("gridSpan")) if tc_pr is not None else None
                val = gs.get(_w("val")) if gs is not None else None
                span_total += int(val) if val and val.isdigit() else 1
            if span_total > grid_cols:
                errors.append(
                    f"TABLE #{idx} row {r_idx}: cell span total ({span_total}) exceeds tblGrid columns ({grid_cols})"
                )
    return errors


def _read_image_size(path: Path) -> Optional[Tuple[int, int]]:
    """Read PNG or JPEG pixel dimensions without requiring Pillow."""
    try:
        data = path.read_bytes()
    except OSError:
        return None
    if len(data) >= 24 and data[:8] == b"\x89PNG\r\n\x1a\n":
        w, h = struct.unpack(">II", data[16:24])
        return (w, h) if w > 0 and h > 0 else None
    if len(data) >= 4 and data[:2] == b"\xff\xd8":
        i = 2
        while i + 9 < len(data):
            if data[i] != 0xFF:
                break
            marker = data[i + 1]
            if marker in (0xC0, 0xC1, 0xC2):
                h, w = struct.unpack(">HH", data[i + 5:i + 9])
                return (w, h) if w > 0 and h > 0 else None
            length = struct.unpack(">H", data[i + 2:i + 4])[0]
            if length < 2:
                break
            i += 2 + length
    return None


def _py_check_image_aspect_ratio(root: ET.Element, extract_dir: Path) -> List[str]:
    errors: List[str] = []
    rels_path = extract_dir / "word" / "_rels" / "document.xml.rels"
    if not rels_path.exists():
        return errors
    try:
        rels_root = ET.parse(rels_path).getroot()
    except ET.ParseError:
        return errors
    rid_to_target = {
        rel.get("Id"): rel.get("Target")
        for rel in rels_root
        if rel.get("Id") and rel.get("Target")
    }

    for drawing in root.iter(_w("drawing")):
        extent = drawing.find(f".//{{{WP_NS}}}extent")
        blip = drawing.find(f".//{{{A_NS}}}blip")
        if extent is None or blip is None:
            continue
        cx, cy = extent.get("cx"), extent.get("cy")
        rid = blip.get(f"{{{R_NS}}}embed")
        if not (cx and cy and rid and cx.isdigit() and cy.isdigit()):
            continue
        cx_i, cy_i = int(cx), int(cy)
        if cx_i <= 0 or cy_i <= 0:
            errors.append(f"IMAGE ({rid}): non-positive extent cx={cx}, cy={cy}")
            continue
        target = rid_to_target.get(rid, "")
        img_path = extract_dir / "word" / target.lstrip("/")
        if not img_path.exists():
            continue
        dims = _read_image_size(img_path)
        if not dims:
            continue
        img_ratio = dims[0] / dims[1]
        doc_ratio = cx_i / cy_i
        distortion = abs(doc_ratio - img_ratio) / img_ratio
        if distortion > 0.25:
            errors.append(
                f"IMAGE ({target}): aspect ratio distortion {distortion:.0%} "
                f"(image {dims[0]}x{dims[1]} vs extent {cx_i}x{cy_i})"
            )
    return errors


def _py_check_section_margins(root: ET.Element) -> List[str]:
    warnings: List[str] = []
    for idx, sect in enumerate(root.iter(_w("sectPr")), start=1):
        pg_sz = sect.find(_w("pgSz"))
        pg_mar = sect.find(_w("pgMar"))
        if pg_sz is None or pg_mar is None:
            continue
        try:
            w = int(pg_sz.get(_w("w"), "0"))
            h = int(pg_sz.get(_w("h"), "0"))
            left = int(pg_mar.get(_w("left"), "0"))
            right = int(pg_mar.get(_w("right"), "0"))
            top = int(pg_mar.get(_w("top"), "0"))
            bottom = int(pg_mar.get(_w("bottom"), "0"))
        except ValueError:
            continue
        if min(left, right, top, bottom) < 0:
            warnings.append(f"SECTION #{idx}: negative page margin detected")
        if w > 0 and (left + right) >= w * 0.6:
            warnings.append(f"SECTION #{idx}: horizontal margins ({left}+{right}) >= 60% of page width ({w})")
        if h > 0 and (top + bottom) >= h * 0.6:
            warnings.append(f"SECTION #{idx}: vertical margins ({top}+{bottom}) >= 60% of page height ({h})")
    return warnings


def _py_check_comments_integrity(extract_dir: Path) -> List[str]:
    errors: List[str] = []
    doc_xml = extract_dir / "word" / "document.xml"
    comments_xml = extract_dir / "word" / "comments.xml"
    if not doc_xml.exists():
        return errors
    try:
        doc_root = ET.parse(doc_xml).getroot()
    except ET.ParseError:
        return errors

    ref_ids = {el.get(_w("id")) for el in doc_root.iter(_w("commentReference")) if el.get(_w("id"))}
    if not ref_ids:
        return errors
    if not comments_xml.exists():
        return [f"COMMENTS: document references {len(ref_ids)} comment(s) but word/comments.xml is missing"]

    try:
        c_root = ET.parse(comments_xml).getroot()
    except ET.ParseError as exc:
        return [f"COMMENTS: word/comments.xml XML parse error: {exc}"]

    defined_ids = {el.get(_w("id")) for el in c_root.iter(_w("comment")) if el.get(_w("id"))}
    missing = sorted(ref_ids - defined_ids)
    if missing:
        errors.append(f"COMMENTS: referenced comment IDs missing from word/comments.xml: {', '.join(missing)}")
    return errors


def _py_check_namespace_declarations(extract_dir: Path) -> List[str]:
    errors: List[str] = []
    for xml_file in extract_dir.rglob("*.xml"):
        try:
            ET.parse(xml_file)
        except ET.ParseError as exc:
            rel = xml_file.relative_to(extract_dir)
            errors.append(f"XML PARSE ({rel}): {exc}")
    return errors


def _py_check_id_uniqueness(root: ET.Element) -> List[str]:
    errors: List[str] = []
    seen_docpr: set = set()
    for el in root.iter(f"{{{WP_NS}}}docPr"):
        eid = el.get("id")
        if eid in seen_docpr:
            errors.append(f"ID DUPLICATE: wp:docPr id={eid} appears multiple times")
        elif eid is not None:
            seen_docpr.add(eid)
    return errors


# Try native docx_lib (Linux/WSL2 + Py3.12); fall back to pure-Python implementations
try:
    from docx_lib import (  # type: ignore[import-not-found]
        fix_element_order_in_tree,
        fix_settings,
        fix_table_width_conservative,
        check_table_grid_consistency,
        check_image_aspect_ratio,
        check_comments_integrity,
        check_section_margins,
        check_namespace_declarations,
        check_id_uniqueness,
        fix_relationship_paths,
        fix_content_types,
    )
    USING_NATIVE_LIB = True
except ImportError:
    fix_element_order_in_tree = _py_fix_element_order_in_tree
    fix_settings = _py_fix_settings
    fix_table_width_conservative = _py_fix_table_width_conservative
    check_table_grid_consistency = _py_check_table_grid_consistency
    check_image_aspect_ratio = _py_check_image_aspect_ratio
    check_comments_integrity = _py_check_comments_integrity
    check_section_margins = _py_check_section_margins
    check_namespace_declarations = _py_check_namespace_declarations
    check_id_uniqueness = _py_check_id_uniqueness
    fix_relationship_paths = _py_fix_relationship_paths
    fix_content_types = _py_fix_content_types
    USING_NATIVE_LIB = False


def validate_and_fix(docx_path: Path) -> Tuple[int, List[str], List[str]]:
    """
    One unzip, two passes:
      1. Fix element order & OPC package paths (modifies XML in place)
      2. Business rule validation (read-only)
    Returns: (fix_count, errors, warnings)
    """
    docx_path = Path(docx_path)
    if not docx_path.exists():
        return 0, [f"FILE: not found: {docx_path}"], []

    with tempfile.TemporaryDirectory() as tmpdir:
        extract_dir = Path(tmpdir) / "extracted"

        try:
            with zipfile.ZipFile(docx_path, "r") as zf:
                zf.extractall(extract_dir)
        except zipfile.BadZipFile:
            return 0, ["STRUCTURE: File corrupted or not a valid .docx archive"], []

        total_fixes = 0
        errors: List[str] = []
        warnings: List[str] = []

        # 1. Fix element order in core XML parts
        xml_files = [
            ("word/document.xml", False),
            ("word/styles.xml", False),
            ("word/numbering.xml", False),
            ("word/settings.xml", True),
        ]
        for rel_path, is_settings in xml_files:
            xml_path = extract_dir / rel_path
            if xml_path.exists():
                tree = ET.parse(xml_path)
                root = tree.getroot()
                fixes = fix_element_order_in_tree(root)
                if is_settings:
                    fixes += fix_settings(root)
                if rel_path == "word/document.xml":
                    fixes += fix_table_width_conservative(root)
                if fixes > 0:
                    tree.write(xml_path, encoding="UTF-8", xml_declaration=True)
                    total_fixes += fixes

        # Fix header/footer parts
        word_dir = extract_dir / "word"
        if word_dir.is_dir():
            for xml_file in list(word_dir.glob("header*.xml")) + list(word_dir.glob("footer*.xml")):
                tree = ET.parse(xml_file)
                root = tree.getroot()
                fixes = fix_element_order_in_tree(root)
                if fixes > 0:
                    tree.write(xml_file, encoding="UTF-8", xml_declaration=True)
                    total_fixes += fixes

        # 2. OPC package-level fixes
        total_fixes += fix_relationship_paths(extract_dir)
        total_fixes += fix_content_types(extract_dir)

        # Fix misplaced /media/ directory (SDK sometimes writes /media/ instead of /word/media/)
        root_media = extract_dir / "media"
        word_media = extract_dir / "word" / "media"
        if root_media.is_dir() and not word_media.is_dir():
            word_media.mkdir(parents=True, exist_ok=True)
            for item in root_media.iterdir():
                shutil.move(str(item), str(word_media / item.name))
            root_media.rmdir()
            total_fixes += 1

        # 3. Business rule validation
        doc_xml = extract_dir / "word" / "document.xml"
        if doc_xml.exists():
            tree = ET.parse(doc_xml)
            root = tree.getroot()
            errors.extend(check_table_grid_consistency(root))
            errors.extend(check_image_aspect_ratio(root, extract_dir))
            warnings.extend(check_section_margins(root))

        errors.extend(check_comments_integrity(extract_dir))
        errors.extend(check_namespace_declarations(extract_dir))

        if doc_xml.exists():
            tree = ET.parse(doc_xml)
            root = tree.getroot()
            errors.extend(check_id_uniqueness(root))

        # 4. Repack safely if fixes were applied
        if total_fixes > 0:
            backup_path = docx_path.with_suffix(".docx.bak")
            shutil.copy2(docx_path, backup_path)
            try:
                with zipfile.ZipFile(docx_path, "w", zipfile.ZIP_DEFLATED) as zf:
                    all_files = [f for f in extract_dir.rglob("*") if f.is_file()]

                    def sort_key(f: Path) -> Tuple[int, str]:
                        rel = f.relative_to(extract_dir).as_posix()
                        if rel == "[Content_Types].xml":
                            return (0, rel)
                        if rel.startswith("_rels/"):
                            return (1, rel)
                        if rel.startswith("word/_rels/"):
                            return (2, rel)
                        return (3, rel)

                    for file_path in sorted(all_files, key=sort_key):
                        arcname = file_path.relative_to(extract_dir).as_posix()
                        zf.write(file_path, arcname)
            except Exception:
                shutil.copy2(backup_path, docx_path)
                backup_path.unlink(missing_ok=True)
                raise
            finally:
                backup_path.unlink(missing_ok=True)

        return total_fixes, errors, warnings


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: python validate_all.py <file.docx>")
        return 1

    docx_path = Path(sys.argv[1])
    _fixes, errors, warnings = validate_and_fix(docx_path)

    for warn in warnings:
        print(f"Warning: {warn}")

    if errors:
        for err in errors:
            print(f"Error: {err}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
