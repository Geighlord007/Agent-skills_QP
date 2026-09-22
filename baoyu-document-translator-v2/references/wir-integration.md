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

## Bridge script (implemented, v2.1.2)

`scripts/write_docx_wir.py` applies translated parts via `TextEdit` old→new
replacements per story. Resolve the engine location with `scripts/engine_select.py`
(sibling skill dir / `~/.agents/skills/docx/scripts` / `$DSH_SKILLS_DIR/docx/scripts` /
`/root/agent-skills/skills/docx/scripts`) — never hardcode machine-specific paths.

**Platform reality**: the engine ships only `_core.cpython-312-x86_64-linux-gnu.so`,
so it imports only on matching Linux + CPython 3.12 x86_64. On Windows/macOS
`engine_select.py` reports `{"recommended": "surgical"}` and you must use
`scripts/write_docx_surgical.py` (the verified, platform-independent equivalent).
On a Linux host, run `engine_select.py`; if `engine_importable=true`, prefer WIR for
comment/tracked-change/nested-table-heavy documents and keep the v2 gates around it
(`verify_structure.py` + `render_qa.py` are engine-agnostic).

If the wrapper hits an API mismatch on the target machine it prints the engine's
`TextEdit` signature and exits 3 — adapt the wrapper to the printed signature there
and commit the fix back.

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
