---
name: baoyu-document-translator-v2
description: Translate DOCX and PPTX while preserving formatting. Two write-back engines chosen by environment — WIR (compiled engine, Linux/WSL2 first choice) and surgical (pure Python, native Windows/macOS) — plus keyed round-trip, all-story extraction (headers/footers/footnotes/textboxes/tracked insertions), structure-aware merge, and an optional QA pack (structure gate, rendered QA, CJK layout localization, pagination pre-pass, regression selftest).
version: 2.2.1
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
        - pymupdf
        - Pillow
---

# Document Translator v2

把 DOCX / PPTX 翻译成目标语言，**格式不变**。

## TL;DR — 日常只需要这三步

```bash
python scripts/extract_docx_v2.py input.docx extracted.json            # 1. 提取
python scripts/json_to_markdown_v2.py extracted.json source.md         #    转成可翻译文本
#    …… 翻译 source.md（chunk_keyed.py 分块 + 子代理），写出 translation.md ……
python scripts/merge_keyed_structure_aware.py extracted.json translation.md translated.json
python scripts/write_docx_surgical.py input.docx output.docx translated.json   # 3. 写回
```

其余脚本（体检 / 渲染 QA / 版式本地化 / 分页 / 目录页码 / 回归自测）都属于
**可选质检包**，默认不跑；需要时按下面各 Step 或 `scripts/selftest.py` 使用。

## 写回引擎怎么选（环境自适应）

```bash
python scripts/engine_select.py     # 打印 {"recommended": "wir" | "surgical"}
```

| 环境 | 用哪个 | 说明 |
|---|---|---|
| **Linux / WSL2**（CPython 3.12 x86_64） | **WIR**（`docx` skill 自带引擎，`scripts/write_docx_wir.py`） | 只改文字节点、其余一律不碰，保真最省事。**首选。** |
| 原生 Windows / macOS / 引擎缺失 | **surgical**（本 skill 自带 `write_docx_surgical.py`） | 同一思路的纯 Python 实现：全平台可用、出问题可当场改 |

> WIR 说明：那个引擎是第三方写好的**编译产物**（C++，只发布了 Linux 版 `.so`，未附源码），
> 所以**原生 Windows 加载不了**——这不是思路问题。想在 Windows 上用 WIR：装 WSL2 直接跑现成那份；
> 或者用本 skill 自带的 surgical（已验证可用）。

## 可选质检包（默认不跑）

| 工具 | 作用 |
|---|---|
| `verify_structure.py` | 体检：结构是否丢失、译文是否真的写进文件（exit 1 = 不要交付） |
| `render_pdf.ps1` + `render_qa.py` | 转 PDF 后检查：空白页 / 残留源语言 / 目录页码 |
| `localize_cjk_en.py` | 中→英版式本地化：字体、编号、字距、对齐、域开关 |
| `paginate_plan.py` / `toc_pages.py` | 分页预 pass / 目录页码回写 |
| `reconcile_consistency.py` | 目录 ↔ 标题 ↔ 图注一致性核对 |
| `selftest.py` | 脚本自身回归测试（23 项） |
| `references/safe-docx-evaluation.md` | **留痕交付（可选）**：第三方 Safe Docx 的实测数据与组合写回方案 |

## 能力范围（v1 → 现在）

| Area | v1 | 现在 |
|------|-----|-----|
| Mapping | Plain markdown split by `\n\n` (fragile when translator merges/splits paragraphs) | Keyed markdown: each element carries a stable `key` so reassembly is order-independent |
| DOCX scope | Body paragraphs + table cells only | All stories: headers/footers (default+first+even), footnotes, endnotes, text boxes, tracked insertions; merged cells deduped to one key per physical `w:tc` |
| Write-back | `run.text =` (destroys page breaks, tabs, fields, drawings) | w:t-level only（surgical 或 WIR）; field-run guard; fused WPS field runs handled |
| PPTX scope | Shape text frames only; table cells extracted but not written back | Shape text frames + table cells fully round-tripped |
| CJK→EN layout | Not addressed | `localize_cjk_en.py` (fonts/numbering/tracking/justify/field switches) + `paginate_plan.py` |
| QA | Text-level only | 可选质检包：structure gate + rendered QA (blanks/CJK/TOC/montage) + regression selftest |
| Terminology/style | Not wired to baoyu-translate preferences | EXTEND.md settings passed through automatically |

## Step 0: 环境与路径选择

- DOCX：先跑 `engine_select.py` → Linux/WSL2 用 WIR 写回，原生 Windows/macOS 用 surgical。
- PPTX：用 `extract_pptx_v2.py` / `write_pptx_v2.py`。
- 下面的 Step 1–7 是完整参考；**日常按 TL;DR 三步即可**。

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

### DOCX — WIR path (Linux / WSL2 first choice; not loadable on native Windows)

The `docx` skill WIR engine is not loadable on Windows (Linux-only binaries; its docs say
"not yet implemented"). Do not use it for business-critical work. The surgical path
(`write_docx_surgical.py`) is the supported equivalent and covers all stories. Kept here
only for reference on non-Windows hosts where the engine actually loads.

See `references/wir-integration.md`.

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

**Default (structure-aware)** — uses the source `parts` as a template so empty spacer runs
stay empty and `\t`/`\n` delimiter runs are preserved; text is distributed only across real
text runs. The naive proportional splitter scatters text into empty/field runs and corrupts
TOC page numbers — do NOT use it as the default.

```bash
python scripts/merge_keyed_structure_aware.py extracted.json translation.md translated.json
```

Legacy naive merge (only if structure-aware unavailable; expect empty-run pollution):

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

## Step 5: Validate（可选 / optional — 默认不跑）

No separate early gate exists: merge prints per-key warnings (SEG_MISMATCH etc.) and the
blocking gate runs at Step 7a (`verify_structure.py` on the written docx). Do not invent
`--precheck`-style invocations; `validate_v2.py` is LEGACY and weak (key/run sanity only).

Checks:
- JSON is valid
- Every extracted key is present
- No extra keys
- `parts.length == runs` for every element
- Hyperlink targets still point to valid URLs (if present)
- Headers/footers/footnotes are included if source had them

## Step 6: Write back to document

### Engine selection (environment-adaptive / 环境自适应)

```bash
python scripts/engine_select.py     # {"recommended": "wir"|"surgical", ...}
```

- **Linux / WSL2 + CPython 3.12 x86_64** → `wir`（编译引擎可加载）。**首选**：
  只改文字节点，其它一律不碰。
- **原生 Windows / macOS / 引擎缺失** → `surgical`（同思路的纯 Python 实现）。

### DOCX — surgical path (preferred on native Windows)

```bash
python scripts/write_docx_surgical.py input.docx output.docx translated.json   # PREFERRED
python scripts/verify_structure.py input.docx output.docx translated.json      # gate: exit 0 or fix
```

`write_docx_surgical.py` sets ONLY `<w:t>` text nodes (python-docx locates elements so
merged-cell keys align; mutation is lxml). It preserves page breaks, `w:ptab`, fields
(`w:fldChar`/`w:instrText`), anchored drawings and `w:pict` that `run.text =` destroys;
short high-variance paragraphs (cover/title style) are consolidated into one run to avoid
formatting patchwork; multi-paragraph cells keep line breaks via `para_splits`.
`verify_structure.py` fails (exit 1) on any structure loss or missing translated text —
never ship a docx without it passing.

Legacy fallback (destroys the nodes above; only if surgical writer unavailable):

```bash
python scripts/write_docx_v2.py input.docx output.docx translated.json
```

### DOCX — WIR path (Linux / WSL2 first choice; not loadable on native Windows)

Generates `TextEdit` objects applied story-by-story without rebuilding the document.
Preferred write-back engine on Linux / WSL2 (the compiled engine loads there).
On native Windows it cannot load — use `write_docx_surgical.py` instead.

See `references/wir-integration.md`.

### PPTX

```bash
python scripts/write_pptx_v2.py input.pptx output.pptx translated.json
```

Writes back:
- Shape text frames by run map
- Table cells by slide/shape/row/col key
- Notes pages if extracted

## Step 7: QA（可选质检包 / optional — 默认不跑）

### 7a. Structure & content gate (mandatory, blocking)

```bash
python scripts/verify_structure.py input.docx output.docx translated.json   # exit 1 = do not ship
```

Checks run-structure preservation (fields/drawings/ptab/page-breaks counts vs source)
and that every translated element's text is present in the output.

### 7b. Rendered QA (mandatory)

```bash
pwsh -File scripts/render_pdf.ps1 -Docx output.docx                 # Word COM (also validates schema)
python scripts/render_qa.py output.pdf input-rendered-src.pdf --cjk-scan --toc-check --montage sheets
```

Blank pages (auto-detected chrome), rendered CJK residue, TOC page-number accuracy,
and 3×4 thumbnail sheets. **Visually review every sheet** — text-level QA cannot see
layout defects. For CJK→EN jobs also apply
`references/cjk-en-localization-pitfalls.md` (fonts, numbering, tracking, pagination).

### 7c. Image QA (optional)

Embedded raster figures may keep source-language text. `qa_images_v2.py` is NOT shipped
with this revision; use `render_qa.py --montage` sheets for visual inspection and report
text-heavy figures to the user (do not auto-localize unless asked).

### 7d. Legacy visual QA

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
│   ├── json_to_markdown_v2.py        # keyed JSON → keyed markdown (Step 2)
│   ├── chunk_keyed.py                # marker-safe chunk splitter (Step 3)
│   ├── reconcile_consistency.py      # TOC↔headingscaptions reconcile (Step 3/5)
│   ├── merge_keyed_structure_aware.py# keyed markdown → JSON, structure-preserving (Step 4 default)
│   ├── markdown_to_json_v2.py        # legacy naive merge (Step 4 fallback)
│   ├── write_docx_surgical.py        # w:t-level write-back, preserves fields/images (Step 6 default)
│   ├── write_docx_wir.py             # WIR-engine write-back (Linux only; see engine_select)
│   ├── engine_select.py              # environment-adaptive engine decision (Step 6)
│   ├── write_docx_v2.py              # legacy run.text write-back (Step 6 fallback)
│   ├── write_pptx_v2.py              # keyed JSON → PPTX (includes table cells)
│   ├── localize_cjk_en.py            # CJK→EN layout: fonts/numbering/tracking/justify/fields
│   ├── paginate_plan.py              # pagination pre-pass + bounded --repair (Step 6)
│   ├── toc_pages.py                  # rewrite TOC page numbers from rendered PDF (Step 7)
│   ├── verify_structure.py           # structure+coverage gate (Step 7a, blocking)
│   ├── render_pdf.ps1                # DOCX→PDF via Word COM / LibreOffice (Step 7b)
│   ├── render_qa.py                  # rendered QA: blanks/CJK/TOC-pages/montage (Step 7b)
│   ├── build_fixture.py              # structural fixture generator (selftest)
│   ├── selftest.py                   # one-command regression selftest (8 checks)
│   └── validate_v2.py                # keyed JSON sanity (legacy, weak — see Troubleshooting)
├── references/
│   ├── schema-v2.md                  # Keyed JSON schema
│   ├── wir-integration.md            # How to use docx skill WIR engine
│   ├── optimization-notes.md         # v1 → v2 rationale and upstream issues
│   ├── cjk-en-localization-pitfalls.md  # CJK→EN localization checklist (v2.1)
│   └── subagent-prompt-template.md   # parallel-chunk prompt template (v2.1)
```

## Dependencies

```bash
pip install python-docx python-pptx lxml PyMuPDF Pillow
```

For OCR image QA (optional):
```bash
pip install paddleocr
```

The optional WIR path (experimental, non-Windows only) additionally needs the `docx`
skill with an importable `scripts/engine/`.

## Integration with `docx` skill

v2 does not replace the `docx` skill. The relationship:

- **baoyu-document-translator-v2** owns the translation workflow, the keyed JSON schema,
  and the surgical write-back (its supported high-fidelity route).
- **docx** skill is only needed for the experimental WIR path (non-Windows).

## Troubleshooting

| Issue | Likely cause | Fix |
|-------|--------------|-----|
| `parts length != runs` | Agent merged runs or deleted marker | Re-translate with explicit marker-preservation instructions |
| Missing header/footer text | First/even-page variants or fused WPS fields not written | Surgical path covers all three header/footer variants; run `localize_cjk_en.py fields` for CJK field switches; verify with gate (non-body coverage check) |
| PPTX table cells not translated | Used v1 `write_pptx.py` | Use v2 `write_pptx_v2.py` |
| Hyperlink URL lost | Used v1 extraction | Use v2 extraction + write |
| Markdown mapping failed | Translator moved/deleted `<!--key:...-->` markers | Add stronger marker-preservation instructions |
| Image text not caught | Heuristic only | Enable OCR pass |
| Whole English doc renders in SimSun/CJK font | Source set `w:ascii/hAnsi` to CJK fonts | `references/cjk-en-localization-pitfalls.md` §2 |
| Garbage bullet glyphs after numbering edits | Bulk-replaced non-ASCII `w:lvlText` (Wingdings PUA glyphs) | Pitfalls §3 TRAP — edit only the verified abstractNum |
| Blank pages / TOC not on its own page | CJK natural flow + empty spacer paras + double page breaks | `scripts/paginate_plan.py` (+`--h1-always`), then `--repair` once; figure-only page = plate, not blank |
| Header/date reverts to Chinese after Word export | Field instrText keeps CJK format switch (`Time \@ "yyyy年M月d日"`) | `localize_cjk_en.py fields` (sanitizes switch + Time→TIME); confirm via `render_qa.py --cjk-scan` |
| Wrong TOC page numbers | Source pagination kept | `scripts/toc_pages.py` (rewrites from rendered PDF); verify with `render_qa.py --toc-check` |
| Text scattered into empty runs, page numbers misplaced | Bundled proportional merge gives empty runs a ratio | Use `scripts/merge_keyed_structure_aware.py` |
| Word refuses to open the output | Regex surgery broke OOXML child order | Always render via `scripts/render_pdf.ps1` (Word COM validates the file) |
| EN→CJK job flagged by CJK gate | Gate assumes CJK→EN | Pass `--expect-cjk` to `verify_structure.py` |
| Mixed CN/EN doc wastes translation tokens | English-only blocks sent to LLM | Filter CJK-only blocks before chunking (missing keys keep source text at merge) |
| Regression after script edits | No fixture coverage | Run `scripts/selftest.py` (8 structural checks) before shipping changes |
| `qa_check_v2.py` / `qa_images_v2.py` missing | Not shipped with this skill revision | Use `scripts/render_qa.py` + manual XML checks (pitfalls §1-2) |

## CJK→EN localization addendum (v2.1)

For Chinese→English (or any CJK→Latin) jobs the simple path needs a localization pass
between write-back and QA. Read **`references/cjk-en-localization-pitfalls.md`** and apply:

1. Run-structure audit (page breaks / `w:ptab` / fields / anchored images survived?)
2. Font / numbering / tracking localization: `scripts/localize_cjk_en.py fonts|numbering|tracking`
3. Table justify in narrow columns: `scripts/localize_cjk_en.py justify`
4. Pagination rebuild (structural page breaks, empty-paragraph cleanup, blank-page scan)
5. TOC page-number rewrite from the rendered PDF
6. Cross-chunk consistency reconcile: `scripts/reconcile_consistency.py` (exit 1 = align first);
   chunking + parallel prompts: `scripts/chunk_keyed.py` +
   `references/subagent-prompt-template.md`
7. Structure-aware merge: `scripts/merge_keyed_structure_aware.py`
8. **Rendered QA (mandatory)**: `scripts/render_pdf.ps1 -Docx out.docx`, then
   `python scripts/render_qa.py out.pdf src.pdf --toc-check --cjk-scan --montage sheets`
   and visually review EVERY montage sheet. Text-level QA cannot see any of the above.

## License

Same as baoyu-document-translator v1.
