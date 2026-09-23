#!/usr/bin/env python3
"""
Extract DOCX text and run structure as keyed JSON, including headers, footers,
footnotes, endnotes, and hyperlinks.

Usage: python extract_docx_v2.py input.docx [output.json]
"""
import sys
import json
import re
from pathlib import Path
from docx import Document
from docx.oxml.ns import qn


NSMAP = {
    "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
}


def is_physical_cell(cell):
    """Check if cell is a physical cell (not a vMerge continuation)."""
    tcPr = cell._tc.find(qn("w:tcPr"))
    if tcPr is not None:
        vMerge = tcPr.find(qn("w:vMerge"))
        if vMerge is not None:
            val = vMerge.get(qn("w:val"))
            if val is None:
                return False
    return True


def get_hyperlinks(para, doc):
    """Return list of (start_run_index, end_run_index_exclusive, url) for hyperlinks in paragraph."""
    links = []
    p = para._p
    rel_part = doc.part.rels

    run_idx = 0
    for child in p:
        tag = child.tag.split("}")[-1] if "}" in child.tag else child.tag
        if tag == "r":
            run_idx += 1
        elif tag == "hyperlink":
            rId = child.get(qn("r:id"))
            if not rId:
                continue
            rel = rel_part.get(rId)
            if not rel:
                continue
            url = rel.target_ref

            # Count run children to determine run span
            child_runs = len([c for c in child if c.tag.split("}")[-1] == "r"])
            if child_runs == 0:
                continue
            start = run_idx
            end = run_idx + child_runs
            run_idx = end
            links.append((start, end, url))

    return links


def para_runs(para):
    """Direct w:r children plus runs inside w:ins and w:hyperlink (document order).
    Field control/result runs inside hyperlinks (PAGEREF etc.) are excluded so page
    numbers are never overwritten; their w:tab runs are kept."""
    from docx.text.run import Run
    out = []
    state = {"mode": None}  # shared across direct runs, w:ins and w:hyperlink children
    def consider(r):
        fc = r.find(qn("w:fldChar"))
        ftype = fc.get(qn("w:fldCharType")) if fc is not None else None
        has_t = r.find(qn("w:t")) is not None
        has_instr = r.find(qn("w:instrText")) is not None
        if ftype == "begin":
            if has_t:
                out.append(Run(r, para))  # fused WPS run: cached result translatable
            state["mode"] = "inside"
            return
        if ftype == "separate":
            state["mode"] = "result"
            return
        if ftype == "end":
            state["mode"] = None
            return
        if has_instr:
            return
        if state["mode"] in ("inside", "result"):
            # field RESULT runs: exclude only purely-numeric generated results
            # (SEQ/PAGEREF/PAGE); static content inside field results (TOC entry
            # titles, cached dates, alphanumeric codes) is translatable
            txt = "".join(t.text or "" for t in r.findall(qn("w:t")))
            if re.fullmatch(r"[\d\.\,\;\:\s\/\-\%]*", txt):
                return
        out.append(Run(r, para))
    def collect(runs_container):
        for r in runs_container:
            if r.tag.split("}")[-1] == "r":
                consider(r)
    for child in para._p:
        tag = child.tag.split("}")[-1]
        if tag == "r":
            collect([child])
        elif tag == "ins":
            collect(list(child))
        elif tag == "hyperlink":
            collect(list(child))
    return out


def extract_paragraph(para, key_prefix, story, index, doc=None):
    """Extract a paragraph element; returns dict or None if empty."""
    text = para.text.strip()
    if not text:
        return None

    runs = para_runs(para)
    parts = [r.text for r in runs]

    elem = {
        "key": f"{key_prefix}{index}",
        "type": "paragraph",
        "story": story,
        "index": index,
        "style": para.style.name if para.style else "Normal",
        "runs": len(runs),
        "text": "".join(parts),
        "parts": parts,
    }

    if doc:
        links = get_hyperlinks(para, doc)
        if links:
            elem["hyperlink"] = {
                "runs": list(range(links[0][0], links[0][1])),
                "url": links[0][2],
            }
            # If multiple hyperlinks in one paragraph, store all in a list
            if len(links) > 1:
                elem["hyperlinks"] = [
                    {"runs": list(range(s, e)), "url": url} for s, e, url in links
                ]

    return elem


def extract_table(table, key_prefix, story, table_index):
    """Yield table_cell elements (one per PHYSICAL cell: vMerge continuations and
    horizontal gridSpan duplicates are skipped so two keys never share one w:tc)."""
    seen = set()
    for ri, row in enumerate(table.rows):
        for ci, cell in enumerate(row.cells):
            if not is_physical_cell(cell):
                continue
            tc = cell._tc
            if tc in seen:      # hold references: id() of temporary lxml proxies is reused
                continue
            seen.add(tc)

            cell_text = cell.text.strip()
            if not cell_text:
                continue

            all_runs = [r for para in cell.paragraphs for r in para_runs(para)]
            parts = [r.text for r in all_runs]
            # paragraph boundaries inside the cell (cumulative run counts) so merge can
            # keep multi-paragraph cells' line breaks aligned; `text` joins paragraph
            # texts with \n so translators see the paragraph structure
            para_splits = []
            para_texts = []
            acc = 0
            for para in cell.paragraphs:
                pruns = para_runs(para)
                acc += len(pruns)
                para_splits.append(acc)
                para_texts.append("".join(r.text for r in pruns))
            yield {
                "key": f"{key_prefix}{table_index}_r{ri}_c{ci}",
                "type": "table_cell",
                "story": story,
                "table": table_index,
                "row": ri,
                "col": ci,
                "runs": len(all_runs),
                "text": "\n".join(para_texts),
                "parts": parts,
                "para_splits": para_splits,
            }


def get_container_element(container):
    """Return the underlying CT_* element for body, header, or footer."""
    if hasattr(container, "_element"):
        return container._element
    return container


def extract_story_elements(container_elem, paragraphs, tables, para_prefix, table_prefix, story, doc=None):
    """Extract paragraphs and tables from a body/header/footer container."""
    elements = []
    para_index = 0
    table_index = 0

    for child in container_elem:
        tag = child.tag.split("}")[-1] if "}" in child.tag else child.tag

        if tag == "p":
            para = next((p for p in paragraphs if p._p is child), None)
            if para is None:
                continue
            elem = extract_paragraph(para, para_prefix, story, para_index, doc)
            if elem:
                elements.append(elem)
            para_index += 1

        elif tag == "tbl":
            table = next((t for t in tables if t._tbl is child), None)
            if table is None:
                continue
            elements.extend(extract_table(table, table_prefix, story, table_index))
            table_index += 1

    return elements


def extract_footnotes_endnotes(docx_path):
    """Extract footnotes/endnotes via direct OOXML parsing."""
    import zipfile
    from lxml import etree

    elements = []

    def parse_part(archive_path, key_prefix, story_prefix):
        found = []
        try:
            with zipfile.ZipFile(docx_path, "r") as zf:
                xml = zf.read(archive_path)
        except KeyError:
            return found

        root = etree.fromstring(xml)
        ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}

        for note in root.findall(".//w:footnote", ns) if "footnote" in archive_path else root.findall(".//w:endnote", ns):
            note_id = note.get(qn("w:id"))
            # Skip separator/continuation-separator notes
            note_type = note.get(qn("w:type"))
            if note_type in ("separator", "continuationSeparator"):
                continue

            para_index = 0
            table_index = 0
            story = f"{story_prefix}:{note_id}"
            key_prefix_full = f"{key_prefix}{note_id}"

            for child in note:
                tag = child.tag.split("}")[-1] if "}" in child.tag else child.tag
                if tag == "p":
                    # Build text from runs manually
                    runs = child.findall(".//w:r", ns)
                    texts = []
                    for r in runs:
                        t = r.find("w:t", ns)
                        if t is not None:
                            texts.append(t.text or "")
                    full_text = "".join(texts).strip()
                    if not full_text:
                        continue
                    found.append({
                        "key": f"{key_prefix_full}_p{para_index}",
                        "type": "paragraph",
                        "story": story,
                        "index": para_index,
                        "runs": len(texts),
                        "text": full_text,
                        "parts": texts,
                    })
                    para_index += 1
                elif tag == "tbl":
                    # Basic table extraction in footnotes
                    for ri, row in enumerate(child.findall("w:tr", ns)):
                        for ci, cell in enumerate(row.findall("w:tc", ns)):
                            cell_runs = cell.findall(".//w:r", ns)
                            cell_texts = []
                            for r in cell_runs:
                                t = r.find("w:t", ns)
                                if t is not None:
                                    cell_texts.append(t.text or "")
                            cell_full = "".join(cell_texts).strip()
                            if not cell_full:
                                continue
                            found.append({
                                "key": f"{key_prefix_full}_t{table_index}_r{ri}_c{ci}",
                                "type": "table_cell",
                                "story": story,
                                "table": table_index,
                                "row": ri,
                                "col": ci,
                                "runs": len(cell_runs),
                                "text": cell_full,
                                "parts": cell_texts,
                            })
                    table_index += 1

        return found

    elements.extend(parse_part("word/footnotes.xml", "fn_", "footnote"))
    elements.extend(parse_part("word/endnotes.xml", "en_", "endnote"))
    return elements


def extract_docx(docx_path, out_path=None):
    doc = Document(docx_path)
    elements = []
    stories = ["body"]

    # Body
    elements.extend(extract_story_elements(
        get_container_element(doc.element.body), doc.paragraphs, doc.tables,
        "p_body_", "t_body_", "body", doc
    ))

    # Headers and footers (default + first-page + even-page variants)
    for si, section in enumerate(doc.sections):
        for attr, suffix in (("header", ""), ("first_page_header", "first"),
                             ("even_page_header", "even")):
            part = getattr(section, attr, None)
            if part is None or part.is_linked_to_previous:
                continue
            story = f"header{suffix}:{si}"
            stories.append(story)
            elements.extend(extract_story_elements(
                get_container_element(part), part.paragraphs, part.tables,
                f"p_header{suffix}_{si}_", f"t_header{suffix}_{si}_", story, doc
            ))
        for attr, suffix in (("footer", ""), ("first_page_footer", "first"),
                             ("even_page_footer", "even")):
            part = getattr(section, attr, None)
            if part is None or part.is_linked_to_previous:
                continue
            story = f"footer{suffix}:{si}"
            stories.append(story)
            elements.extend(extract_story_elements(
                get_container_element(part), part.paragraphs, part.tables,
                f"p_footer{suffix}_{si}_", f"t_footer{suffix}_{si}_", story, doc
            ))

    # Text boxes / shapes in body (w:txbxContent)
    from docx.text.paragraph import Paragraph
    body_elem = get_container_element(doc.element.body)
    for n, tb in enumerate(body_elem.findall(".//" + qn("w:txbxContent"))):
        pi = 0
        for p in tb.findall(qn("w:p")):
            para = Paragraph(p, doc)
            elem = extract_paragraph(para, f"txbx_{n}_p", "textbox", pi, doc)
            if elem:
                elements.append(elem)
                pi += 1
        # tables nested inside text boxes (pict/shape > textbox > txbxContent > tbl)
        for ti, tbl in enumerate(tb.findall(qn("w:tbl"))):
            for ri, tr_el in enumerate(tbl.findall(qn("w:tr"))):
                seen_tc, ci = set(), 0
                for tc in tr_el.findall(qn("w:tc")):
                    if id(tc) in seen_tc:
                        continue
                    seen_tc.add(id(tc))
                    parts = []
                    for p in tc.findall(".//" + qn("w:p")):
                        parts.extend(r.text for r in para_runs(Paragraph(p, doc)))
                    if "".join(parts).strip():
                        elements.append({
                            "key": f"t_txbx_{n}_{ti}_r{ri}_c{ci}",
                            "type": "table_cell",
                            "story": "textbox",
                            "table": f"txbx_{n}_{ti}",
                            "row": ri,
                            "col": ci,
                            "runs": len(parts),
                            "text": "".join(parts),
                            "parts": parts,
                        })
                    ci += 1

    # text boxes inside header/footer parts (running-head branding, page-number frames)
    from docx.text.paragraph import Paragraph as _P
    for si, section in enumerate(doc.sections):
        for attr, scope in (("header", "h"), ("footer", "f"),
                            ("first_page_header", "hfirst"), ("first_page_footer", "ffirst")):
            part = getattr(section, attr, None)
            if part is None or part.is_linked_to_previous:
                continue
            for n, tb in enumerate(part._element.findall(".//" + qn("w:txbxContent"))):
                pi = 0
                for p in tb.findall(qn("w:p")):
                    para = _P(p, part)
                    elem = extract_paragraph(para, f"txbx_{scope}{si}_{n}_p", "textbox", pi, doc)
                    if elem:
                        elements.append(elem)
                        pi += 1

    # paragraphs inside SDT content controls (body level)
    seen_sdt = set()
    for idx, sdt in enumerate(body_elem.findall(".//" + qn("w:sdt"))):
        if id(sdt) in seen_sdt:
            continue
        seen_sdt.add(id(sdt))
        pi = 0
        for p in sdt.findall(".//" + qn("w:p")):
            para = Paragraph(p, doc)
            elem = extract_paragraph(para, f"p_sdt_{idx}_p", "sdt", pi, doc)
            if elem:
                elements.append(elem)
                pi += 1

    # Footnotes and endnotes
    fn_elements = extract_footnotes_endnotes(docx_path)
    if fn_elements:
        stories.extend(sorted({e["story"] for e in fn_elements}))
        elements.extend(fn_elements)

    # TODO: text boxes / shapes in body and headers/footers
    # These require parsing w:drawing / w:pict / mc:AlternateContent elements.

    result = {
        "file_type": "docx",
        "source_file": str(docx_path),
        "elements": elements,
        "stories": stories,
        "total_elements": len(elements),
        "total_runs": sum(e["runs"] for e in elements),
    }

    json_str = json.dumps(result, ensure_ascii=False, indent=2)

    if out_path:
        Path(out_path).write_text(json_str, encoding="utf-8")
        print(f"Written to {out_path}")
    else:
        print(json_str)

    return result


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: python {sys.argv[0]} input.docx [output.json]")
        sys.exit(1)

    extract_docx(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
