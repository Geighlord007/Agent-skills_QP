---
name: baoyu-document-translator
description: Translate documents (DOCX, PPTX) while preserving original formatting, styles, and structure. Uses baoyu-translate's refined workflow for high-quality translation + run-level precision for format preservation. Use when user wants to translate a Word document, PowerPoint, or any formatted document without losing layout, fonts, colors, tables, or merged cells.
version: 1.0.0
metadata:
  openclaw:
    homepage: https://github.com/JimLiu/baoyu-skills#baoyu-document-translator
    requires:
      anyBins:
        - python
      pythonPackages:
        - python-docx
        - python-pptx
---

# Document Translator

Translate DOCX and PPTX files using **baoyu-translate's refined workflow** while preserving all original formatting.

## Workflow

```
Step 1: Extract document to JSON (structure + text)
         ↓
Step 2: Convert JSON to markdown for baoyu-translate
         ↓
Step 3: Run baoyu-translate refined mode on markdown
         ↓
Step 4: Merge translated markdown back into JSON
         ↓
Step 5: Validate JSON (runs count, completeness)
         ↓
Step 6: Write translated JSON back to document
         ↓
Step 7: QA — generate preview images for visual check
```

## Supported Formats

| Format | Status | Notes |
|--------|--------|-------|
| DOCX | ✅ Supported | Paragraphs, tables, merged cells, styles |
| PPTX | ✅ Supported | Shapes, table cells, run-level formatting |
| PDF | ❌ Not yet | Planned for v2 |

## Step 1: Extract Document

### DOCX

```bash
python scripts/extract_docx.py input.docx extracted.json
```

Extracts:
- Paragraphs (with style: Heading 1, Normal, etc.)
- Table cells (skipping merged cell continuations)
- Run-level text fragments

### PPTX

```bash
python scripts/extract_pptx.py input.pptx extracted.json
```

Extracts:
- Shapes with text frames
- Table cells within shapes
- Run counts per shape

**Output**: `extracted.json` with structure:
```json
{
  "file_type": "docx",
  "elements": [
    {"key": "p0", "type": "paragraph", "runs": 3, "text": "...", "parts": ["..."]},
    {"key": "t0_r0_c0", "type": "table_cell", "runs": 1, "text": "...", "parts": ["..."]}
  ]
}
```

## Step 2: Convert to Markdown

```bash
python scripts/json_to_markdown.py extracted.json source.md
```

Converts JSON elements to markdown:
- Paragraphs → markdown paragraphs
- Headings → `# Heading` format
- Table cells → plain text

## Step 3: Translate with baoyu-translate

Use baoyu-translate's **refined mode** on `source.md`:

1. Analyze → `01-analysis.md`
2. Translate → `02-prompt.md` → `03-draft.md` → `04-critique.md` → `05-revision.md`
3. Polish → `translation.md`

This gives you publication-quality translation.

## Step 4: Merge Translation into JSON

```bash
python scripts/markdown_to_json.py extracted.json translation.md translated.json
```

Maps translated text back to JSON elements, splitting into `parts` to match original `runs` count.

**Note**: For complex documents with multi-line paragraphs or table structures, the agent may need to manually align translations to elements to ensure accuracy.

## Step 5: Validate

```bash
python scripts/validate.py translated.json extracted.json
```

Checks:
- ✅ JSON is valid
- ✅ `parts.length == runs` for every element
- ✅ No missing elements
- ✅ No extra elements

**If validation fails**: Fix the JSON before proceeding to Step 6.

## Step 6: Write Back to Document

### DOCX

```bash
python scripts/write_docx.py input.docx output.docx translated.json
```

Strategy:
1. Clear all runs in each paragraph/cell
2. Write translated parts back to runs by index
3. Original font/size/color/format preserved

### PPTX

```bash
python scripts/write_pptx.py input.pptx output.pptx translated.json
```

Strategy:
1. Build run map (para_idx, run_idx) for each shape
2. Clear all runs
3. Write translated parts back by run map
4. Original font properties preserved

## Step 7: QA

### 7a. Content QA

Check for untranslated text, element count mismatch, and format integrity:

```bash
python scripts/qa_check.py extracted.json output.docx qa_report.txt
```

Checks:
- ❌ Untranslated source-language text remaining
- ❌ Missing or extra elements
- ⚠️ Runs count mismatch per element
- ⚠️ Empty text elements

### 7b. Image QA

Extract embedded images and check for source-language text:

```bash
python scripts/qa_images.py output.docx qa_images/
```

This extracts all images to `qa_images/` and identifies text-heavy candidates (screenshots, diagrams, charts) that may need localization.

**Example output:**
```
⚠️  Images that MAY contain source-language text:
  - image1.jpeg (page header: company name in Chinese)
  - image2.jpeg (page footer: contact info in Chinese)

Reminder: Do not automatically localize images unless the user asks.
```

### 7c. Visual QA (Optional)

For final verification, convert to PDF and inspect:

```bash
# DOCX → PDF
libreoffice --headless --convert-to pdf output.docx

# PDF → Images
pdftoppm -jpeg -r 150 output.pdf page
```

Spawn subagents to inspect images for:
- Text overflow or truncation
- Font size changes
- Formatting issues

## Key Design Principles

### Run-Level Precision

Documents contain **runs** — text segments with different formatting:

```
[Red Bold]Click here[/Red Bold] [Blue Link]to view details[/Blue Link]
```

This is 2 runs. Translation MUST produce exactly 2 parts:
```json
{"runs": 2, "parts": ["点击这里", "查看详情"]}
```

If you merge into 1 part, the second run loses its blue/link formatting.

### Clear-Then-Write

Never overwrite runs directly. Always:
1. `run.text = ''` — clear all runs first
2. `run.text = parts[i]` — write translations by index

This prevents "Chinese + English" mixed残留 text.

### Merged Cells (DOCX)

Merged cells are handled by:
- **Extraction**: Only physical cells are extracted (skipping `vMerge="continue"`)
- **Writing**: Each physical cell is written once
- **Result**: All merged cell references show the same translated text

## Directory Structure

```
baoyu-document-translator/
├── SKILL.md                          # This file
├── scripts/
│   ├── extract_docx.py               # DOCX → JSON
│   ├── extract_pptx.py               # PPTX → JSON
│   ├── write_docx.py                 # JSON → DOCX
│   ├── write_pptx.py                 # JSON → PPTX
│   ├── validate.py                   # Validate translated JSON
│   ├── json_to_markdown.py           # JSON → markdown
│   ├── markdown_to_json.py           # markdown → JSON
│   ├── qa_check.py                   # Content QA
│   └── qa_images.py                  # Image QA
└── references/
    └── schema.md                     # JSON format specification
```

## Dependencies

```bash
pip install python-docx python-pptx
```

## Troubleshooting

| Issue | Cause | Fix |
|-------|-------|-----|
| `parts length != runs` | Agent merged runs during translation | Re-translate with explicit run-count instructions |
| Missing elements | Markdown had fewer paragraphs than JSON | Check for multi-line paragraphs merged into one |
| Table cells not translated | Non-physical cells skipped | Ensure physical cells are properly extracted |
| Format lost | Runs were recreated instead of reused | Use "clear then write" strategy, never delete runs |

## License

Same as baoyu-translate.
