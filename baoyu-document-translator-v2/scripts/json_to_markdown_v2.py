#!/usr/bin/env python3
"""
Convert keyed extracted JSON to keyed markdown for baoyu-translate.

Usage: python json_to_markdown_v2.py extracted.json source.md

Output format:
  <!--key:p_body_0|runs:3|type:paragraph-->
  Introduction

  <!--key:t_body_0_r0_c0|runs:1|type:table_cell-->
  Cell text

The HTML comment markers are stable keys. The translator must preserve them.
"""
import sys
import json
from pathlib import Path


def marker(key, runs, elem_type):
    return f"<!--key:{key}|runs:{runs}|type:{elem_type}-->"


def element_to_markdown(elem):
    text = elem.get("text", "").strip()
    if not text:
        return ""

    elem_type = elem.get("type", "paragraph")
    key = elem.get("key", "")
    runs = elem.get("runs", 1)

    lines = [marker(key, runs, elem_type)]

    # Do not add markdown heading syntax here; the document style is preserved
    # in JSON and we do not want '# ' characters written back into the DOCX.
    # If needed, the marker's type/style fields inform the translator.
    lines.append(text)

    return "\n".join(lines)


def json_to_markdown(json_path, md_path=None):
    data = json.loads(Path(json_path).read_text(encoding="utf-8"))
    elements = data.get("elements", [])

    blocks = []
    for elem in elements:
        block = element_to_markdown(elem)
        if block:
            blocks.append(block)

    markdown = "\n\n".join(blocks).strip()

    if md_path:
        Path(md_path).write_text(markdown, encoding="utf-8")
        print(f"Written to {md_path}")
    else:
        print(markdown)

    return markdown


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: python {sys.argv[0]} extracted.json [source.md]")
        sys.exit(1)

    json_path = sys.argv[1]
    md_path = sys.argv[2] if len(sys.argv) > 2 else None
    json_to_markdown(json_path, md_path)
