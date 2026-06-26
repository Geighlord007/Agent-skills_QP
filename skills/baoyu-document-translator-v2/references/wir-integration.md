# WIR Integration Guide

For business-critical or template-heavy DOCX files, v2 can delegate reading and writing to the `docx` skill's WIR engine instead of `python-docx`. This preserves complex OOXML structures that python-docx may drop when rebuilding runs.

## When to use WIR

- Corporate templates with headers/footers
- Documents with footnotes/endnotes
- Documents with tracked changes or comments you want to keep
- Documents where python-docx produced visible formatting loss
- Documents with nested tables or complex table styles

## When NOT to use WIR

- Simple one-off documents where python-docx is faster
- Documents you are creating from scratch (use `docx` skill Create path instead)
- Files that fail WIR validation due to malformed OOXML (fix the file first)

## Bridge script idea

`scripts/wir_bridge_v2.py` (not yet implemented; implement when first WIR-path document is processed):

```python
import sys
import json
from pathlib import Path

sys.path.insert(0, '/home/adam18294/agent-skills/skills/docx/scripts')
from engine import WIRSession, TextEdit


def extract_to_json(docx_path, out_json):
    session = WIRSession.open(docx_path)
    elements = []

    parts = ['document']
    # Discover headers/footers/footnotes/endnotes by reading document first
    w1, wir, _ = session.read(part='document')
    # Parse WIR XML to find rel IDs, then add header:rIdX etc.
    # ...implementation...

    for part in parts:
        cursor = None
        while True:
            w, wir, cursor = session.read(part=part, cursor=cursor)
            if not wir:
                break
            # Parse <p> and <tbl> blocks, assign keys, store in elements
            # ...implementation...

    session.close()
    Path(out_json).write_text(
        json.dumps({'file_type': 'docx', 'elements': elements}, ensure_ascii=False, indent=2),
        encoding='utf-8'
    )


def write_from_json(docx_path, translated_json, output_path):
    session = WIRSession.open(docx_path)
    data = json.loads(Path(translated_json).read_text(encoding='utf-8'))

    # Build TextEdit list keyed by (part, element_key)
    edits = []
    for elem in data['elements']:
        # Map elem key back to WIR old_string
        # TextEdit(old_string='<r>original</r>', new_string='<r>translated</r>')
        # ...implementation...
        pass

    # Apply edits story by story
    # session.edit(w1, edits)

    session.save(output_path)


if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'extract':
        extract_to_json(sys.argv[2], sys.argv[3])
    elif cmd == 'write':
        write_from_json(sys.argv[2], sys.argv[3], sys.argv[4])
```

## Mapping strategy

1. **Extract:** Read each WIR part, find translatable text blocks, assign v2 keys, and write keyed JSON.
2. **Translate:** Convert keyed JSON to keyed markdown, run baoyu-translate, merge back to keyed JSON.
3. **Write:** For each element, create `TextEdit(old_string='<r>original</r>', new_string='<r>translated</r>')`. Apply edits in batches by story.

## Fidelity advantages

- Original run objects are never deleted or recreated; only text content changes.
- Headers/footers/footnotes/endnotes are edited in place.
- Hyperlinks, bookmarks, fields, and content controls remain intact.
- Template styles and numbering definitions are preserved.

## Validation

After WIR save, run `docx/scripts/docx validate` if available, or open the document in Word/LibreOffice to check for errors.
