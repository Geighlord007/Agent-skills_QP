#!/usr/bin/env python3
"""
Extract DOCX text and run structure as JSON.

Usage: python extract_docx.py input.docx [output.json]

Outputs JSON:
{
  "file_type": "docx",
  "elements": [
    {
      "key": "p0",
      "type": "paragraph",
      "index": 0,
      "style": "Heading 1",
      "runs": 3,
      "text": "full text",
      "parts": ["run0", "run1", "run2"]
    },
    {
      "key": "t0_r0_c0",
      "type": "table_cell",
      "table": 0,
      "row": 0,
      "col": 0,
      "runs": 1,
      "text": "cell text",
      "parts": ["run0"]
    }
  ]
}
"""
import sys
import json
from pathlib import Path
from docx import Document
from docx.oxml.ns import qn


def is_physical_cell(cell):
    """Check if cell is a physical cell (not a vMerge continuation)."""
    tcPr = cell._tc.find(qn('w:tcPr'))
    if tcPr is not None:
        vMerge = tcPr.find(qn('w:vMerge'))
        if vMerge is not None:
            val = vMerge.get(qn('w:val'))
            if val is None:
                return False  # Default is "continue"
    return True


def get_runs_from_para(para):
    """Extract non-empty runs from a paragraph."""
    return [r for r in para.runs if r.text.strip() or True]


def extract_docx(docx_path, out_path=None):
    doc = Document(docx_path)
    elements = []

    para_map = {id(p._p): p for p in doc.paragraphs}
    table_map = {id(t._tbl): t for t in doc.tables}

    para_idx = 0
    table_idx = 0

    for child in doc.element.body:
        tag = child.tag.split('}')[-1] if '}' in child.tag else child.tag

        if tag == 'p':
            para = para_map.get(id(child))
            if para is None:
                continue
            para_idx += 1

            text = para.text.strip()
            if not text:
                continue

            runs = get_runs_from_para(para)
            style_name = para.style.name if para.style else "Normal"

            elements.append({
                "key": f"p{para_idx - 1}",
                "type": "paragraph",
                "index": para_idx - 1,
                "style": style_name,
                "runs": len(runs),
                "text": para.text,
                "parts": [r.text for r in runs]
            })

        elif tag == 'tbl':
            table = table_map.get(id(child))
            if table is None:
                continue
            table_idx += 1

            for ri, row in enumerate(table.rows):
                for ci, cell in enumerate(row.cells):
                    text = cell.text.strip()
                    if not text:
                        continue

                    # Skip non-physical cells (merged cell continuations)
                    if not is_physical_cell(cell):
                        continue

                    all_runs = [r for para in cell.paragraphs
                                for r in get_runs_from_para(para)]

                    elements.append({
                        "key": f"t{table_idx - 1}_r{ri}_c{ci}",
                        "type": "table_cell",
                        "table": table_idx - 1,
                        "row": ri,
                        "col": ci,
                        "runs": len(all_runs),
                        "text": cell.text,
                        "parts": [r.text for r in all_runs]
                    })

    result = {
        "file_type": "docx",
        "source_file": str(docx_path),
        "elements": elements,
        "total_elements": len(elements),
        "total_runs": sum(e["runs"] for e in elements)
    }

    json_str = json.dumps(result, ensure_ascii=False, indent=2)

    if out_path:
        Path(out_path).write_text(json_str, encoding='utf-8')
        print(f'Written to {out_path}')
    else:
        print(json_str)

    return result


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(f'Usage: python {sys.argv[0]} input.docx [output.json]')
        sys.exit(1)

    docx_path = sys.argv[1]
    out_path = sys.argv[2] if len(sys.argv) > 2 else None
    extract_docx(docx_path, out_path)
