---
name: baoyu-document-translator-v2
description: Translate DOCX and PPTX while preserving formatting. v2 adds high-fidelity WIR editing for complex documents, robust keyed markdown round-trip, headers/footers/footnotes/hyperlinks/text-box extraction, fixed PPTX table-cell writing, and EXTEND.md passthrough. Use when v1 loses complex formatting, misses header/footer text, fails on PPTX tables, or when source documents are business-critical.
version: 2.0.0
metadata:
  openclaw:
    homepage: https://github.com/JimLiu/baoyu-skills#baoyu-document-translator-v2
    requires:
      anyBins:
        - python
        - bun
        - npx
      pythonPackages:
        - python-docx
        - python-pptx
        - lxml
---

# Document Translator v2

Translate DOCX and PPTX files while preserving formatting, with two fidelity paths:

- **Simple path** (`python-docx`): fast, good for documents whose formatting is mostly paragraphs, runs, and tables.
- **High-fidelity path** (`docx` skill WIR engine): preserves complex OOXML structures (headers, footers, footnotes, endnotes, hyperlinks, text boxes, tracked changes, comments, nested tables) by editing the document directly instead of rebuilding it.

Both paths use the same baoyu-translate refined workflow for the actual translation.

## What v2 improves over v1

| Area | v1 | v2 |
|------|-----|-----|
| Mapping | Plain markdown split by `\n\n` (fragile when translator merges/splits paragraphs) | Keyed markdown: each element carries a stable `key` so reassembly is order-independent |
| DOCX scope | Body paragraphs + table cells only | Adds headers, footers, footnotes, endnotes, text boxes, shapes, hyperlinks |
| PPTX scope | Shape text frames only; table cells extracted but not written back | Shape text frames + table cells fully round-tripped |
| Complex formatting | python-docx rebuild can drop template fidelity | Optional WIR editing keeps the original OOXML intact |
| Terminology/style | Not wired to baoyu-translate preferences | EXTEND.md settings passed through automatically |
| Image QA | Heuristic only (extension + size) | Optional OCR pass via `paddleocr-doc-parsing` to detect embedded source-language text |

## Workflow overview

```
Step 0: Choose fidelity path (simple vs. WIR)
         ↓
Step 1: Extract document to keyed JSON
         ↓
Step 2: Convert JSON to keyed markdown for baoyu-translate
         ↓
Step 3: Translate with baoyu-translate (refined mode, EXTEND-aware)
         ↓
Step 4: Merge keyed translation back into JSON
         ↓
Step 5: Validate (runs count, keys, missing/extra)
         ↓
Step 6: Write translated JSON back to document
         ↓
Step 7: QA — content, structure, images (+ optional OCR)
```

## Step 0: Choose fidelity path

Use the **simple path** when:
- Document is mostly body text and simple tables
- No complex headers/footers need translation
- No embedded hyperlinks or footnotes
- Speed matters more than pixel-perfect fidelity

Use the **WIR high-fidelity path** when:
- Document is a corporate template with headers/footers
- Contains footnotes/endnotes
- Contains hyperlinks that must keep their URLs
- Contains text boxes / floating shapes
- v1 produced visible formatting loss
- Document is business-critical

## Step 1: Extract document to keyed JSON

### DOCX — simple path

```bash
python scripts/extract_docx_v2.py input.docx extracted.json
```

Extracts from **all document stories**:
- Body paragraphs and tables
- Header/footer paragraphs and tables
- Footnotes and endnotes
- Text boxes / shapes in body and headers/footers
- Hyperlink text and URL (URL preserved, text translated)

Element keys are stable across extraction runs:
- `p_body_0`, `p_body_1`, ...
- `t_body_0_r0_c0`, ...
- `p_header1_0`, `p_footer1_0`, ...
- `fn_0_p0`, `en_0_p0`, ...
- `shape_body_0_p0`

### DOCX — WIR path

Use the `docx` skill WIR engine. Read all relevant parts (`document`, `header:rIdX`, `footer:rIdX`, `footnotes`, `endnotes`) and convert them to the same keyed JSON schema.

See `references/wir-integration.md` for the helper script.

### PPTX

```bash
python scripts/extract_pptx_v2.py input.pptx extracted.json
```

Extracts:
- Shape text frames (all paragraphs/runs)
- Table cells (all rows/columns)
- Slide notes pages (optional, `--include-notes`)

Keys:
- Shape: `s_0_3` (slide 0, shape 3)
- Table cell: `t_0_5_r1_c2` (slide 0, shape 5, row 1, col 2)
- Note: `n_0_p0` (slide 0 note paragraph 0)

## Step 2: Convert to keyed markdown

```bash
python scripts/json_to_markdown_v2.py extracted.json source.md
```

Output format (`source.md`):

```markdown
<!--key:p_body_0|runs:3-->
# Introduction

<!--key:t_body_0_r0_c0|runs:1-->
Column header
```

Each translatable block is preceded by an HTML comment carrying:
- `key`: stable element identifier
- `runs`: expected run count after translation
- `type`: paragraph/table_cell/shape/etc. (optional)

This lets the merge step map translations back by key rather than by paragraph order, so translators can split or merge paragraphs for natural flow without breaking the document.

## Step 3: Translate with baoyu-translate

Run baoyu-translate refined mode on `source.md`. The v2 skill automatically:

1. Loads EXTEND.md from the usual baoyu-translate locations
2. Applies target language, mode, audience, style, and glossary
3. Preserves keyed HTML comments in the output

If you are invoking baoyu-translate manually, pass the same EXTEND.md or use `--glossary` / `--style` / `--audience` flags.

Important instruction to add to the translation prompt:

> Preserve every `<!--key:...|runs:N-->` marker exactly as-is. Do not delete, renumber, or move them. Place each marker immediately before the translated text block it belongs to. The text following the marker must split into exactly N runs at natural formatting boundaries (e.g., bold segments, color changes, links).

## Step 4: Merge keyed translation back to JSON

```bash
python scripts/markdown_to_json_v2.py extracted.json translation.md translated.json
```

This script:
1. Parses HTML comment markers to build a `key → translated text` map
2. Splits translated text into `parts` matching the original `runs` count
3. Warns if any key is missing or any run count cannot be matched
4. Preserves original `text` field for reference

### Run splitting strategy

For `runs > 1`, the agent should produce natural splits. When the agent did not split explicitly, the script uses a language-aware strategy:

1. Try punctuation boundaries in target language (`。`, `，`, `.`, `,`, `;`, `!`, `?`)
2. Try formatting hints in the source `parts` (e.g., source had `[Bold word][rest]`)
3. Fall back to proportional split with a warning

## Step 5: Validate

```bash
python scripts/validate_v2.py translated.json extracted.json
```

Checks:
- JSON is valid
- Every extracted key is present
- No extra keys
- `parts.length == runs` for every element
- Hyperlink targets still point to valid URLs (if present)
- Headers/footers/footnotes are included if source had them

## Step 6: Write back to document

### DOCX — simple path

```bash
python scripts/write_docx_v2.py input.docx output.docx translated.json
```

Strategy:
1. Locate each element by key in the correct story (body/header/footer/footnote/endnote/shape)
2. Clear existing runs (`run.text = ''`)
3. Write translated parts back by run index
4. Preserve original font/size/color/bold/italic/hyperlink URL

### DOCX — WIR path

Use the `docx` skill WIR engine. Generate `TextEdit` objects from the keyed JSON and apply them story-by-story. This never rebuilds the document, so template fidelity is preserved.

See `references/wir-integration.md`.

### PPTX

```bash
python scripts/write_pptx_v2.py input.pptx output.pptx translated.json
```

Writes back:
- Shape text frames by run map
- Table cells by slide/shape/row/col key
- Notes pages if extracted

## Step 7: QA

### 7a. Content QA

```bash
python scripts/qa_check_v2.py extracted.json output.docx qa_report.txt
```

Checks:
- Untranslated source-language text remaining
- Missing or extra elements
- Runs count mismatch per element
- Empty text elements
- Header/footer/footnote presence
- Hyperlink URL integrity

### 7b. Image QA (basic)

```bash
python scripts/qa_images_v2.py output.docx qa_images/
```

Extracts embedded images and flags text-heavy candidates.

### 7c. Image QA with OCR (optional)

If `paddleocr-doc-parsing` is installed and the source language is CJK, run OCR on extracted images to detect remaining source-language text.

```bash
python scripts/qa_images_ocr_v2.py output.docx qa_images/ --lang zh
```

### 7d. Visual QA

Convert to PDF/images and inspect for overflow or formatting issues:

```bash
libreoffice --headless --convert-to pdf output.docx
pdftoppm -jpeg -r 150 output.pdf page
```

## Directory structure

```
baoyu-document-translator-v2/
├── SKILL.md                          # This file
├── scripts/
│   ├── extract_docx_v2.py            # DOCX → keyed JSON (all stories)
│   ├── extract_pptx_v2.py            # PPTX → keyed JSON (shapes + tables + notes)
│   ├── write_docx_v2.py              # keyed JSON → DOCX
│   ├── write_pptx_v2.py              # keyed JSON → PPTX (includes table cells)
│   ├── json_to_markdown_v2.py        # keyed JSON → keyed markdown
│   ├── markdown_to_json_v2.py        # keyed markdown → keyed JSON
│   ├── validate_v2.py                # Validate keyed JSON
│   ├── qa_check_v2.py                # Content QA
│   ├── qa_images_v2.py               # Image extraction + heuristic QA
│   └── qa_images_ocr_v2.py           # Optional OCR image QA
├── references/
│   ├── schema-v2.md                  # Keyed JSON schema
│   ├── wir-integration.md            # How to use docx skill WIR engine
│   └── optimization-notes.md         # v1 → v2 rationale and upstream issues
```

## Dependencies

```bash
pip install python-docx python-pptx lxml
```

For OCR image QA (optional):
```bash
pip install paddleocr
```

For WIR high-fidelity path, the `docx` skill must be available and its `scripts/engine/` importable.

## Integration with `docx` skill

v2 does not replace the `docx` skill; it delegates to it for the high-fidelity path. The relationship:

- **baoyu-document-translator-v2** owns the translation workflow and the keyed JSON schema.
- **docx** skill owns document reading/writing fidelity.

When WIR path is chosen, v2 scripts call `docx/scripts/engine/WIRSession` to read and edit the document, then use baoyu-translate for the actual text transformation.

## Troubleshooting

| Issue | Likely cause | Fix |
|-------|--------------|-----|
| `parts length != runs` | Agent merged runs or deleted marker | Re-translate with explicit marker-preservation instructions |
| Missing header/footer text | Used simple path on template document | Switch to WIR high-fidelity path |
| PPTX table cells not translated | Used v1 `write_pptx.py` | Use v2 `write_pptx_v2.py` |
| Hyperlink URL lost | Used v1 extraction | Use v2 extraction + write |
| Markdown mapping failed | Translator moved/deleted `<!--key:...-->` markers | Add stronger marker-preservation instruction |
| Image text not caught | Heuristic only | Enable OCR pass |

## License

Same as baoyu-document-translator v1.
