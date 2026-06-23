#!/usr/bin/env python3
"""
Convert extracted JSON to markdown for baoyu-translate.

Usage: python json_to_markdown.py extracted.json source.md

Strategy:
- Paragraphs become markdown paragraphs/headings
- Table cells become plain text (preserved in context)
- Each element's text is preserved so baoyu-translate can translate naturally
"""
import sys
import json
from pathlib import Path


def element_to_markdown(elem):
    """Convert a single JSON element to markdown."""
    text = elem.get("text", "").strip()
    if not text:
        return ""

    elem_type = elem.get("type", "paragraph")
    style = elem.get("style", "")

    if elem_type == "paragraph":
        # Handle heading styles
        if style.startswith("Heading"):
            try:
                level = int(style.replace("Heading", "").strip())
                return f"{'#' * level} {text}"
            except ValueError:
                pass
        return text

    elif elem_type == "table_cell":
        # Table cells are just text
        return text

    elif elem_type == "shape":
        return text

    return text


def json_to_markdown(json_path, md_path=None):
    data = json.loads(Path(json_path).read_text(encoding='utf-8'))
    elements = data.get("elements", [])

    lines = []
    for elem in elements:
        md = element_to_markdown(elem)
        if md:
            lines.append(md)
            lines.append("")  # Blank line between elements

    markdown = "\n".join(lines).strip()

    if md_path:
        Path(md_path).write_text(markdown, encoding='utf-8')
        print(f'Written to {md_path}')
    else:
        print(markdown)

    return markdown


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(f'Usage: python {sys.argv[0]} extracted.json [source.md]')
        sys.exit(1)

    json_path = sys.argv[1]
    md_path = sys.argv[2] if len(sys.argv) > 2 else None
    json_to_markdown(json_path, md_path)
