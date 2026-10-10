#!/usr/bin/env python3
"""
Write keyed translations back to DOCX, preserving headers, footers, and hyperlinks.

Usage: python write_docx_v2.py input.docx output.docx translations.json

Note: Footnotes/endnotes are best handled by the WIR high-fidelity path.
This script handles body, header, and footer paragraphs and tables.
"""
import sys
import json
import re
from pathlib import Path
from docx import Document
from docx.oxml.ns import qn


def clear_all_runs(container):
    for para in container.paragraphs:
        for run in para.runs:
            run.text = ""


def write_parts_to_paragraph(para, parts):
    runs = para.runs
    if not runs:
        if parts:
            para.add_run(parts[0])
        return

    for run in runs:
        run.text = ""

    for i, run in enumerate(runs):
        if i < len(parts):
            run.text = parts[i]


def write_parts_to_cell(cell, parts):
    all_runs = [r for para in cell.paragraphs for r in para.runs]
    if not all_runs:
        if parts and cell.paragraphs:
            cell.paragraphs[0].add_run(parts[0])
        return

    for run in all_runs:
        run.text = ""

    for i, run in enumerate(all_runs):
        if i < len(parts):
            run.text = parts[i]


def write_hyperlink_url(para, hyperlink_info, doc):
    """Re-apply hyperlink URL to the runs specified in hyperlink_info."""
    if not hyperlink_info:
        return

    # python-docx does not expose hyperlink editing directly.
    # The hyperlink relationship is on the w:hyperlink element wrapping runs.
    # Since we only changed run text, the relationship should still exist.
    # This function is a placeholder for future direct OOXML hyperlink rewriting.
    pass


def get_story_container(doc, story):
    """Map a story string to its container."""
    if story == "body":
        return doc.element.body, doc.paragraphs, doc.tables

    m = re.match(r"header:(\d+)", story)
    if m:
        si = int(m.group(1))
        if si < len(doc.sections):
            h = doc.sections[si].header
            return h, h.paragraphs, h.tables

    m = re.match(r"footer:(\d+)", story)
    if m:
        si = int(m.group(1))
        if si < len(doc.sections):
            f = doc.sections[si].footer
            return f, f.paragraphs, f.tables

    return None, [], []


def get_container_element(container):
    """Return the underlying CT_* element for body, header, or footer."""
    if hasattr(container, "_element"):
        return container._element
    return container


def write_docx(input_path, output_path, json_path):
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    translations = {e["key"]: e for e in data.get("elements", [])}
    doc = Document(input_path)

    written = 0
    skipped = 0
    warnings = []

    # Group elements by story
    by_story = {}
    for elem in data.get("elements", []):
        story = elem.get("story", "body")
        by_story.setdefault(story, []).append(elem)

    for story, elems in by_story.items():
        if story.startswith("footnote") or story.startswith("endnote"):
            warnings.append(
                f"Skipping {len(elems)} {story} element(s); use WIR high-fidelity path for footnotes/endnotes."
            )
            skipped += len(elems)
            continue

        container, all_paras, all_tables = get_story_container(doc, story)
        if container is None:
            warnings.append(f"Unknown story: {story}")
            skipped += len(elems)
            continue

        # Build ordered maps for this container
        para_map = {id(p._p): p for p in all_paras}
        table_map = {id(t._tbl): t for t in all_tables}

        para_idx = 0
        table_idx = 0

        for child in get_container_element(container):
            tag = child.tag.split("}")[-1] if "}" in child.tag else child.tag

            if tag == "p":
                para = para_map.get(id(child))
                if para is None:
                    continue

                key = f"p_{story.replace(':', '_')}_{para_idx}"
                if key in translations:
                    elem = translations[key]
                    write_parts_to_paragraph(para, elem.get("parts", []))
                    write_hyperlink_url(para, elem.get("hyperlink"), doc)
                    written += 1
                elif para.text.strip():
                    skipped += 1

                para_idx += 1

            elif tag == "tbl":
                table = table_map.get(id(child))
                if table is None:
                    continue

                for ri, row in enumerate(table.rows):
                    for ci, cell in enumerate(row.cells):
                        key = f"t_{story.replace(':', '_')}_{table_idx}_r{ri}_c{ci}"
                        if key in translations:
                            elem = translations[key]
                            write_parts_to_cell(cell, elem.get("parts", []))
                            written += 1
                        elif cell.text.strip():
                            skipped += 1

                table_idx += 1

    doc.save(output_path)

    print(f"\n{'='*50}")
    print("DOCX Write Complete (v2)")
    print(f"{'='*50}")
    print(f"  Written: {written} elements")
    if skipped > 0:
        print(f"  Skipped: {skipped} elements")
    if warnings:
        print("  Warnings:")
        for w in warnings[:10]:
            print(f"    - {w}")
    print(f"  Output: {output_path}")


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python write_docx_v2.py <input.docx> <output.docx> <translations.json>")
        sys.exit(1)

    write_docx(sys.argv[1], sys.argv[2], sys.argv[3])
