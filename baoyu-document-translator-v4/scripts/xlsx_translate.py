# -*- coding: utf-8 -*-
"""XLSX translation without touching anything but the text (v4.3).

Rewrites ONLY `xl/sharedStrings.xml` text nodes and `xl/workbook.xml` sheet names via
`lxml.etree`, so styles, number formats, charts, images, column widths, rich-text runs,
and pivot definitions survive without XML corruption.

Usage:
  python xlsx_translate.py <src.xlsx> <dst.xlsx> <map.json>

map.json:
  {
    "strings":     {"<source text>": "<translated text>", ...},
    "sheet_names": {"<source sheet name>": "<translated sheet name>"}
  }
"""
import json
import re
import sys
import zipfile
from lxml import etree

CJK = re.compile(r"[\u4e00-\u9fff]")
BAD_SHEET_CHARS = re.compile(r"[:\\/?*\[\]]")
SS_NS = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
XML_SPACE = "{http://www.w3.org/XML/1998/namespace}space"


def scan(label, path):
    hits = {}
    with zipfile.ZipFile(path) as z:
        for n in z.namelist():
            if not n.endswith(".xml"):
                continue
            t = z.read(n).decode("utf-8", "ignore")
            flat = "".join(
                a or b
                for a, b in re.findall(
                    r"<(?:w:)?t[^>]*>([^<]*)</(?:w:)?t>|<a:t>([^<]*)</a:t>", t
                )
            )
            c = len(CJK.findall(flat))
            samples = [x for x in re.findall(r"<t[^>]*>([^<]*)</t>", t) if CJK.search(x)][:4]
            names = [x for x in re.findall(r'<sheet name="([^"]+)"', t) if CJK.search(x)]
            if c or names:
                hits[n] = (c, samples + ["sheet:" + x for x in names])
    print("[%s] CJK remaining: %s" % (label, hits or "none"))
    return hits


def _set_t_text(t_elem, text):
    t_elem.text = text
    if text and (text[0].isspace() or text[-1].isspace() or "\n" in text):
        t_elem.set(XML_SPACE, "preserve")


def patch_shared_strings(xml_bytes, mapping):
    root = etree.fromstring(xml_bytes)
    ns = {"s": SS_NS}
    patched = 0
    for si in root.findall("s:si", ns):
        t_nodes = si.findall(".//s:t", ns)
        if not t_nodes:
            continue
        if len(t_nodes) == 1:
            src = t_nodes[0].text or ""
            if src in mapping:
                _set_t_text(t_nodes[0], mapping[src])
                patched += 1
            continue
        # Rich-text <si> with multiple <r><t>: match per-run first, else full-cell text
        any_run = False
        for tn in t_nodes:
            src = tn.text or ""
            if src in mapping:
                _set_t_text(tn, mapping[src])
                any_run = True
        if any_run:
            patched += 1
            continue
        full = "".join(tn.text or "" for tn in t_nodes)
        if full in mapping:
            _set_t_text(t_nodes[0], mapping[full])
            for tn in t_nodes[1:]:
                tn.text = ""
            patched += 1
    return etree.tostring(root, xml_declaration=True, encoding="UTF-8", standalone=True), patched


def patch_workbook(xml_bytes, name_map):
    root = etree.fromstring(xml_bytes)
    ns = {"s": SS_NS}
    renamed = 0
    for sheet in root.findall(".//s:sheet", ns):
        old_name = sheet.get("name", "")
        if old_name in name_map:
            new_name = name_map[old_name]
            if len(new_name) > 31:
                raise SystemExit(f"ERROR: Sheet name exceeds Excel 31-char limit ({len(new_name)}): {new_name!r}")
            if BAD_SHEET_CHARS.search(new_name):
                raise SystemExit(f"ERROR: Sheet name contains illegal Excel character: {new_name!r}")
            sheet.set("name", new_name)
            renamed += 1
    return etree.tostring(root, xml_declaration=True, encoding="UTF-8", standalone=True), renamed


def main():
    if len(sys.argv) < 4:
        raise SystemExit("Usage: python xlsx_translate.py <src.xlsx> <dst.xlsx> <map.json>")
    src, dst, mapf = sys.argv[1], sys.argv[2], sys.argv[3]
    with open(mapf, encoding="utf-8") as fh:
        M = json.load(fh)
    s_map, n_map = M.get("strings", {}), M.get("sheet_names", {})
    scan("before", src)

    with zipfile.ZipFile(src) as zin:
        items = zin.infolist()
        data = {i.filename: zin.read(i.filename) for i in items}

    n_str, n_sheets = 0, 0
    if "xl/sharedStrings.xml" in data and s_map:
        data["xl/sharedStrings.xml"], n_str = patch_shared_strings(data["xl/sharedStrings.xml"], s_map)
    if "xl/workbook.xml" in data and n_map:
        data["xl/workbook.xml"], n_sheets = patch_workbook(data["xl/workbook.xml"], n_map)

    with zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as zout:
        for i in items:
            zi = zipfile.ZipInfo(i.filename, date_time=i.date_time)
            zi.compress_type = i.compress_type
            zi.external_attr = i.external_attr
            zout.writestr(zi, data[i.filename])

    print("shared strings patched: %d | sheet names renamed: %d" % (n_str, n_sheets))
    scan("after", dst)

    invalid = []
    with zipfile.ZipFile(dst) as z:
        for nm in [n for n in z.namelist() if n.endswith((".xml", ".rels"))]:
            try:
                etree.fromstring(z.read(nm))
            except Exception as e:
                invalid.append((nm, str(e)))
                print("!! XML INVALID:", nm, e, file=sys.stderr)
    if invalid:
        raise SystemExit(1)
    print("XML validation: OK")


if __name__ == "__main__":
    main()
