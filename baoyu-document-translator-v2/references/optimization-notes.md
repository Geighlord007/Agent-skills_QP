# v1 → v2 Optimization Notes

This document explains why v2 changes exist, which v1 issues they fix, and what still requires upstream fixes (i.e., should be solved in `baoyu-document-translator` or `baoyu-translate` itself rather than hacked around in v2).

## Issues found in v1 scripts

### 1. Fragile markdown → JSON mapping (`markdown_to_json.py`)

**v1 behavior:**
- Splits `translation.md` by `\n\n` and maps lines to elements by index.
- If the translator merges two short paragraphs into one, or splits one long paragraph into two, every subsequent element shifts and the mapping is wrong.
- `split_into_parts()` splits translated text by character count near punctuation, which can put the wrong words into a bold run or link run.

**v2 fix:**
- HTML comment markers (`<!--key:p_body_0|runs:3-->`) make mapping key-based rather than order-based.
- The translator is explicitly instructed to preserve markers.
- Run splitting uses language-aware punctuation + source-part hints before falling back to proportional split.

**Upstream fix needed?** No — this is a local pipeline issue and is solved in v2.

### 2. DOCX scope limited to body

**v1 behavior:**
- `extract_docx.py` only iterates `doc.element.body` paragraphs and tables.
- Headers, footers, footnotes, endnotes, text boxes, and hyperlinks are ignored.

**v2 fix:**
- `extract_docx_v2.py` iterates all document stories and extracts text boxes/shapes.
- Hyperlink text and URLs are captured so links keep working after translation.

**Upstream fix needed?** Ideally yes — the v1 skill should support all stories. v2 demonstrates the approach.

### 3. PPTX table cells not written back

**v1 behavior:**
- `extract_pptx.py` extracts table cells with keys like `(0, 5, 1, 2)`.
- `write_pptx.py` only iterates elements that have `slide` and `shape` and checks `shape.has_text_frame`; it never handles `shape.has_table`.
- Therefore table cells are extracted but never written.

**v2 fix:**
- `write_pptx_v2.py` handles both `has_text_frame` shapes and `has_table` shapes.
- Table cells are located by slide/shape/row/col and written back run-by-run.

**Upstream fix needed?** Yes — this is a clear bug in v1 `write_pptx.py`.

### 4. No integration with `docx` skill

**v1 behavior:**
- Uses only `python-docx` for read/write.
- Complex documents can lose formatting because python-docx rebuilds structure.

**v2 fix:**
- Defines a WIR high-fidelity path that delegates to the `docx` skill's WIR engine.
- Provides `references/wir-integration.md` showing how to bridge keyed JSON with `WIRSession`.

**Upstream fix needed?** No — this is an optional enhancement; simple path remains available.

### 5. No EXTEND.md passthrough

**v1 behavior:**
- baoyu-translate supports rich EXTEND.md preferences (glossary, audience, style, mode).
- baoyu-document-translator does not mention or pass them through.

**v2 fix:**
- SKILL.md instructs the agent to load baoyu-translate EXTEND.md and apply it to the document translation.

**Upstream fix needed?** Ideally yes — v1 should consume baoyu-translate preferences directly.

### 6. Image QA is heuristic-only

**v1 behavior:**
- `qa_images.py` extracts images and flags them by extension + size.
- It cannot actually tell whether an image contains source-language text.

**v2 improvement:**
- Optional `qa_images_ocr_v2.py` uses `paddleocr-doc-parsing` (if available) to detect text in images.

**Upstream fix needed?** No — this is an optional add-on.

## What v2 deliberately leaves to upstream

The following are real limitations, but fixing them properly belongs in the upstream `python-docx` / `baoyu-document-translator` layer rather than in a local wrapper:

1. **Run-level semantic splitting.** `python-docx` can tell us how many runs exist but not *why* (bold, color, link, language). v2 preserves run count, but it cannot automatically ensure a translated bold segment stays bold if the translator changed the sentence structure.

2. **Complex PPTX animations / grouped shapes.** `python-pptx` does not expose all OOXML features. Deep shape hierarchies, grouped shapes, charts, and SmartArt may require direct OOXML editing.

3. **Tracked changes / comments / content controls.** Full fidelity for these requires the `docx` skill WIR engine or direct OOXML manipulation.

4. **Font substitution for CJK.** If the target language is Chinese but the original font has no CJK glyphs, Word will substitute fonts. This is a document/font issue, not a translation issue.

## Recommended upstream PRs

If contributing back to `baoyu-document-translator`:

1. Fix `write_pptx.py` to write table cells.
2. Add header/footer/footnote/endnote extraction to `extract_docx.py`.
3. Add hyperlink preservation to `extract_docx.py` / `write_docx.py`.
4. Replace plain-markdown mapping with keyed markers in `json_to_markdown.py` / `markdown_to_json.py`.
5. Read baoyu-translate EXTEND.md and pass settings through.

v2 can be used immediately while waiting for upstream adoption.
