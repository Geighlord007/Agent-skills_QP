# baoyu-document-translator v2

This is an optimized fork of `baoyu-document-translator` that addresses several
format-preservation and workflow issues found in v1.

## Quick start

```bash
cd agent-skills/skills/baoyu-document-translator-v2

# DOCX simple path
python scripts/extract_docx_v2.py input.docx extracted.json
python scripts/json_to_markdown_v2.py extracted.json source.md
# ... run baoyu-translate on source.md -> translation.md ...
python scripts/markdown_to_json_v2.py extracted.json translation.md translated.json
python scripts/validate_v2.py translated.json extracted.json
python scripts/write_docx_v2.py input.docx output.docx translated.json

# PPTX
python scripts/extract_pptx_v2.py input.pptx extracted.json
# ... translate ...
python scripts/write_pptx_v2.py input.pptx output.pptx translated.json
```

## Key improvements

1. **Keyed markdown markers** — mapping is by stable key, not paragraph order.
2. **Headers, footers, footnotes, endnotes** extracted in DOCX.
3. **Hyperlinks** preserved in DOCX (URL kept, text translated).
4. **PPTX table cells** fully written back.
5. **WIR high-fidelity path** delegates to the `docx` skill for complex documents.
6. **EXTEND.md passthrough** for baoyu-translate preferences.

## Files

- `SKILL.md` — main workflow and instructions
- `scripts/` — improved extraction/merge/write scripts
- `references/schema-v2.md` — keyed JSON schema
- `references/optimization-notes.md` — v1 issues and v2 fixes
- `references/wir-integration.md` — how to use the `docx` skill WIR engine

## Source files

The original skill at `agent-skills/skills/baoyu-document-translator` is left
untouched. v2 lives in this parallel directory.
