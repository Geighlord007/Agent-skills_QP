# CJK→EN Document Localization Pitfalls (v2 addendum)

Lessons from a production run (50+ page Chinese regulatory report → English, 945 keyed
elements). The simple python-docx path preserves *run formatting* but NOT *run structure*,
and Chinese layout parameters become visual defects in English. Apply this checklist
between Step 6 (write-back) and Step 7 (QA).

## 1. Run-structure destruction (python-docx `run.text =` clears ALL run children)

`run.text = x` removes every non-rPr child of the run. Destroyed silently:

| Node | Consequence | Detection |
|------|-------------|-----------|
| `<w:br w:type="page"/>` | manual page breaks become line breaks | count `<w:br w:type="page"/>` src vs out |
| `<w:ptab/>` | right-aligned header dates lose alignment | count `<w:ptab` src vs out |
| `<w:fldChar>/<w:instrText>` | TOC/PAGE/NUMPAGES/DATE fields die (static text left) | count `<w:instrText` src vs out |
| `<w:drawing>` (anchored) | floating images vanish | per-page image count src vs out PDF |
| `<w:pict>`, textboxes | same | |

**Rule**: prefer w:t-level surgical replacement (set only `<w:t>` text nodes, never
`run.text=`), or run the counts above and patch destroyed parts from the source zip
(headers/footers/footnotes/textboxes/anchored-image runs can be restored by paragraph index).

## 2. Font localization (the "everything is SimSun" bug)

Chinese docs routinely set `w:ascii`/`w:hAnsi` to CJK fonts (宋体/黑体/等线) at run AND
style level — invisible in Chinese, catastrophic when all text becomes Latin.

**Fix**: replace `w:ascii`/`w:hAnsi` values in {宋体,黑体,等线,楷体,仿宋,微软雅黑,SimSun,SimHei,
DengXian,KaiTi,FangSong,Microsoft YaHei} with the doc's Latin default (read
`styles.xml` docDefaults `w:ascii`), in document.xml + all header/footer/footnote parts +
styles.xml. Keep `w:eastAsia` untouched.

## 3. CJK layout parameters that must be localized

| Parameter | Chinese effect | English effect | Fix |
|---|---|---|---|
| `w:numFmt decimalFullWidth` (heading lists) | ２.４.１ fullwidth digits | same, looks broken | → `decimal` |
| `w:numFmt chineseCounting*` | 一、二、三 | 一、in English text | → `decimal` (+ `w:suff space` if `nothing`) |
| bullet `w:lvlText` U+F06C/U+2022 + Wingdings/Symbol rFonts | ● / • | — | **NEVER bulk-replace non-ASCII lvlText** (see trap below) |
| rPr `<w:spacing w:val="454"/>` (heading tracking) | 声  明 | S t a t e m e n t | remove rPr spacing val > 40 |
| Normal `w:jc=both` | fine (CJK breaks anywhere) | rivers + one-word-per-line in narrow table cols | set table-cell paragraphs `jc=left` (keep centered headers) |
| empty-paragraph spacers + natural flow | intended page starts | blank pages / mid-page TOC | see §4 |

**TRAP (hit in production)**: a well-meant "normalize non-ASCII lvlText" pass replaced
bullet glyphs (U+F06C Wingdings) with `%1.` → Wingdings rendered "%1." as garbage glyphs.
Only touch the numFmt/lvlText of the *specific* abstractNum you verified (map paragraph
numPr → numId → abstractNumId first).

## 4. Pagination rebuild (Chinese flow ≠ English flow)

English text is 1.3–1.8× longer. Chinese docs rely on natural flow + empty spacer
paragraphs; after translation these strand blank pages or leave headings orphaned.

Checklist:
1. Add `w:pageBreakBefore` to structural headings (TOC title, Executive Summary, every
   Heading-1) — but ONLY where no section break already precedes them (double break =
   blank page; test by rendering).
2. Delete pure-empty paragraphs preceding those headings. **Empty test must be
   text-content based** (`"".join(w:t).strip()==""`), NOT `"<w:t" in para` — write-back
   leaves empty `<w:t></w:t>` runs that fool the substring test.
3. Empty section-break paragraphs (`sectPr` in pPr, empty text): if a blank page remains,
   the break mark or a following empty paragraph is stranding; iterate (delete/zero) and
   re-render until blank-page scan is clean. Zero-height: `spacing before/after=0,
   line=0 exact`.
4. Trailing blank page: collapse trailing empty paragraphs (keep any carrying the final
   body-level sectPr).
5. Always finish with an automated blank-page scan over the rendered PDF.

## 5. TOC page numbers

Source TOC numbers are Chinese-pagination. After write-back they are wrong. Either
rebuild the TOC field, or rewrite the digits-only run of each entry from the rendered
English PDF (match entry title → first page whose text contains the heading/caption
line; strip leading auto-numbers from PDF lines before matching; unescape XML entities
in titles; skip TOC pages when searching). Verify: 0 mismatches entry-vs-actual.

## 6. Coverage blind spots of the simple path

- `section.header` misses first-page/even-page headers (`first_page_header` etc.).
- Footnotes/endnotes: skipped by `write_docx_v2.py`; patch `word/footnotes.xml` w:t nodes
  directly (mirror extraction indexing: skip separator/continuationSeparator notes).
- Textboxes (`w:txbxContent`) are not extracted at all; patch their w:t in document.xml.
- Cover/company-name blocks often bilingual; decide keep-or-translate explicitly.

## 7. Cross-chunk consistency (parallel subagent drafts)

Mandatory reconcile pass before merge:
- TOC entries vs body headings vs table/figure captions: string-equal after stripping
  section numbers (parallel translators WILL diverge: "Checklist" vs "Register",
  "Process" vs "Procedure", singular/plural).
- Contract titles / recurring proper nouns: single canonical rendering.
- Spelling policy (en-US body; EU spelling only inside verbatim EU quotes; official names
  like OECD/ICH keep their spelling).
- Jurisdiction-sensitive terms (China 新食品原料 ≠ EU novel food).

## 8. Merge must be structure-aware

The bundled `markdown_to_json_v2.py` proportional split scatters text into empty spacer
runs and misplaces TOC page numbers (empty runs get `max(len,1)` ratio). Use
`scripts/merge_keyed_structure_aware.py`: source `parts` as template — empty runs stay
empty, `\t`/`\n` delimiter runs preserved, translated text distributed only across real
text runs within each delimiter-bounded segment (boundary-aware split at punctuation).

## 9. Rendered QA is mandatory (text-level QA is not enough)

`qa_check_v2.py` catches text problems only. Every defect class above is visible ONLY in
rendered output. Minimum loop:
1. Word COM (`SaveAs2 ... 17`) or LibreOffice → PDF. (Word COM also proves the file is
   not schema-corrupt — python-docx/regex surgery can produce files Word refuses.)
2. Automated: blank-page scan; CJK residue over ALL xml parts' w:t; per-page image counts
   vs source; TOC entry-vs-actual page compare; heading page-start check.
3. Visual: montage all pages into 3×4 thumbnail sheets (PyMuPDF + PIL) and LOOK at every
   sheet; full-dpi spot checks of cover / TOC / one wide table / one narrow-column table /
   bullet lists / headers-footers.
