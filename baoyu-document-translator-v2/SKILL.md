---
name: baoyu-document-translator-v2
description: Translate DOCX and PPTX while preserving formatting. Two write-back engines chosen by environment — WIR (compiled engine, Linux/WSL2 first choice) and surgical (pure Python, native Windows/macOS) — plus keyed round-trip, all-story extraction (headers/footers/footnotes/textboxes/tracked insertions), structure-aware merge, and an optional QA pack (structure gate, rendered QA, CJK layout localization, pagination pre-pass, regression selftest).
version: 3.0.0
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

## TL;DR — 三步一条链（v3 合一脚本）

```bash
python scripts/extract_v3.py input.docx|input.pptx extracted.json       # 1. 提取（DOCX/PPTX 合一）
python scripts/json_to_markdown_v2.py extracted.json source.md         #    转成可翻译文本
#    …… 全文理解 → 规格确认 → 并行翻译 + 独立审校 → 跨区块统一，写出 translation.md ……
python scripts/merge_v3.py extracted.json translation.md translated.json [run_splits.json]   # 2. 合并 + run 切分一步完成
python scripts/write_v3.py input output translated.json                # 3. 写回（DOCX: WIR/surgical 自适应；PPTX: 嵌套形状）
python scripts/qa_v3.py input output translated.json translation.md [--numerals whitelist.json]   # 阻断质检
```

`run_splits.json` 为精确 run 切分覆盖（强调短语、换行位置），合并时一步写入最终 JSON，
不再产生中间产物。翻译文本之前必须产出两份产物并经用户确认：`01-context.md`（全文理解）与翻译规格单。
直接对 source.md 分块开译是被禁止的路径——译者拿到孤立文本块会丢失语境，
区块之间会各译各的，缩写与数字写法也会随译者默认值漂移。

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
| PPTX 回抽比对（Step 7a） | 重新提取输出文件，逐元素比对：文本一致、run 数量一致、分段切分一致、格式签名（粗体/斜体/字号/颜色）与原件一致 |
| 数字保真核对（Step 7a） | 已翻译元素的数字词元与原文一致；书写形式转换（1.2 billion → 12 亿）记入数字形式白名单后放行 |
| `render_pdf.ps1` + `render_qa.py` | 转 PDF 后检查：空白页 / 残留源语言 / 目录页码 |
| `localize_cjk_en.py` | 中→英版式本地化：字体、编号、字距、版式调整、域开关 |
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
| Terminology/style | Not wired to baoyu-translate preferences | 全文理解产物 `01-context.md` + 用户确认的翻译规格单 + EXTEND.md 设置三者合并使用 |
| 翻译质量 | 译者各自决定语域与缩写处置 | 全文理解 → 规格确认 → 并行翻译（带页面语境）→ 独立审校 → 跨区块统一 |

## Step 0: 环境与路径选择

- DOCX / PPTX：统一用 `extract_v3.py` / `merge_v3.py` / `write_v3.py` / `qa_v3.py`。
  DOCX 写回引擎由 `write_v3.py` 内部调用 `engine_select.py` 自动分发（Linux/WSL2 → WIR，其余平台 → surgical）。
- XLSX：用 `xlsx_translate.py`（只改共享字符串 + 表名，格式/图表/图片零风险；注意 Excel 表名上限 31 字符）。
- 下面的 Step 1–7 是完整参考；**日常按 TL;DR 三步即可**。

## Step 1: Extract document to keyed JSON

```bash
python scripts/extract_v3.py input.docx|input.pptx extracted.json    # 合一提取器
```

按扩展名分发：DOCX 走全部 story 提取（正文/页眉页脚/脚注尾注/文本框/超链接/域 run 守护）；
PPTX 走形状树遍历（含组合形状子级、表格单元格、备注），并记录 `para_splits` 与逐 run 格式签名
（粗体/斜体/字号/颜色）供质检比对。

### DOCX keys

Element keys are stable across extraction runs:
- `p_body_0`, `p_body_1`, ...
- `t_body_0_r0_c0`, ...
- `p_header1_0`, `p_footer1_0`, ...
- `fn_0_p0`, `en_0_p0`, ...
- `shape_body_0_p0`

### PPTX keys

- Shape: `s_0_3`（slide 0, shape 3；组合形状子级追加路径段，如 `s_11_17_1`）
- Table cell: `t_0_5_r1_c2`（含路径段时同理追加）
- Note: `n_0_p0` (slide 0 note paragraph 0)

备注页默认提取，`--no-notes` 关闭。

### DOCX — WIR path (Linux / WSL2 first choice; not loadable on native Windows)

The `docx` skill WIR engine is not loadable on Windows (Linux-only binaries; its docs say
"not yet implemented"). Do not use it for business-critical work. The surgical path
(`write_docx_surgical.py`) is the supported equivalent and covers all stories. Kept here
only for reference on non-Windows hosts where the engine actually loads.

See `references/wir-integration.md`.

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

## Step 3: Translate（全文理解 → 规格确认 → 并行翻译 + 独立审校）

### 3.0 全文理解（`01-context.md`，阻断产物）

分块之前通读整份 `source.md`，写出 `01-context.md`，内容全部来自这份文档自身：

- **文档类型与各部分语域**：每个部分属于什么文体、面向什么读者（例如路演 PPT 的团队页按"职称、学位、机构、顾问、投资方"的排布习惯措辞；研发设施页按实验设施与工艺能力措辞）。
- **缩写清单**：逐个缩写给出语境推断与依据（例如 "PhD in Bioinformatics, BU; Msc, MIT" 中 BU 与 MIT 以学位授予机构并列，同一文档另有 Boston 与 MIT campus 语境，据此判定 BU = Boston University）。判定依据写在清单里；从全文判定不了的缩写列入待确认清单。
- **数字与金额写法倾向**：全文金额、数量级、日期的书写形式（例如金额用 $8M 形式还是 800 万美元），译文沿用同一形式。
- **强调排布规律**：斜体、加粗、颜色 run 通常承载哪类信息（关键词组、数字、成果）。
- **保留英文清单**：公司名、产品名、蛋白缩写、邮箱、模型名等约定保留英文的项。

### 3.1 翻译规格单（阻断式，需用户确认）

基于 `01-context.md` 汇总一份规格单交用户确认：术语表、缩写释义、语域、数字写法、保留英文清单。用户确认后才进入 3.2。用户修改的任何条目写回 `01-context.md`。

### 3.2 分块并行翻译

Run baoyu-translate refined mode on `source.md`, 或用 `chunk_keyed.py` 分块 + 并行子代理。共享上下文（`02-prompt.md`）必须引用 `01-context.md` 的术语表、缩写释义、语域与数字写法，**禁止只给译者孤立文本块**。区块文本之外附页面语境（该页主题、栏目含义）。

Each chunk subagent reads `02-prompt.md`, translates its chunk to `chunks/chunk-NN-draft.md`. 译者只输出完整自然的句子；**run 数量与格式边界不对译者暴露**，run 切分在合并后由主代理处理（见 Step 4）。

Important instruction to add to the translation prompt:

> Preserve every `<!--key:...|runs:N-->` marker exactly as-is. Do not delete, renumber, or move them. Place each marker immediately before the translated text block it belongs to. 译文以完整自然的目标语言句子为先，禁止为对上 run 数量而扭曲语序或截断词组。

### 3.3 独立审校（并行子代理）

每个区块译完后交给**未参与该块翻译**的子代理审校，对照 `01-context.md` 与源块检查：语域贴合页面语境、缩写按全文判定处理、术语与规格单一致、数值与书写形式合规、表达无翻译腔、多分段元素的行数与空行结构和源文本一致。审校发现写入 `chunks/chunk-NN-review.md`，主代理据此修订。

### 3.4 跨区块统一

主代理合并各区块后做全篇用词统一：同一概念在所有区块使用同一译法；同一缩写的展开形式一致；数字书写形式全篇一致。然后写出 `translation.md`。

## Step 4: Merge keyed translation back to JSON（合并 + run 切分一步完成）

```bash
python scripts/merge_v3.py extracted.json translation.md translated.json [run_splits.json]
```

`merge_v3.py` 基于结构化合并（空 run 保持为空、`\t`/`\n` 分隔 run 保留、文本只写入真实文本 run），
并把 `run_splits.json` 的精确切分一步覆盖进最终 `translated.json`——不再产生 `merged.json` 之类的中间产物。
`run_splits.json` 可选；不提供时完全沿用自动切分。

底层逻辑（结构化合并）:
1. Parses HTML comment markers to build a `key → translated text` map
2. Splits translated text into `parts` matching the original `runs` count
3. Warns if any key is missing or any run count cannot be matched
4. Preserves original `text` field for reference

### Run splitting strategy（合并之后处理）

合并脚本按语言边界自动切分只是初稿。对 `runs > 1` 且含强调（粗体/斜体/颜色）或换行（`a:br`）的元素，
主代理按以下原则做**精确切分**，写入 `run_splits.json` 随合并一步生效：

1. 强调 run 承载对应的强调短语（源文本加粗/斜体/彩色的词组，译文中用相应措辞自然突出）
2. 换行位置与原文一致（`a:br` 在 run 之间，切分点必须让断行出现在同样的语义位置）
3. 每个元素的 parts 拼接与译文逐字一致（合并时自动校验，不一致即报错退出）
4. 数值 run（如 "$10 million"、"100 g/L"）保持完整数字词元，禁止把数字截断到两个 run

未覆盖的元素沿用合并脚本的自动切分。

## Step 5: Validate（可选 / optional — 默认不跑）

No separate early gate exists: merge prints per-key warnings (SEG_MISMATCH etc.) and the
blocking gate runs at Step 7a（DOCX 用 `verify_structure.py`；PPTX 用回抽比对 + 数字保真核对）。
Do not invent `--precheck`-style invocations; `validate_v2.py` is LEGACY and weak (key/run sanity only).

Checks:
- JSON is valid
- Every extracted key is present
- No extra keys
- `parts.length == runs` for every element
- Hyperlink targets still point to valid URLs (if present)
- Headers/footers/footnotes are included if source had them

## Step 6: Write back to document

```bash
python scripts/write_v3.py input.docx|input.pptx output translated.json   # 合一写回器
```

`write_v3.py` 按扩展名分发：

- **DOCX**：内部调用 `engine_select.py` 自动选引擎——Linux/WSL2 + CPython 3.12 x86_64 → WIR（`write_docx_wir.py`，
  编译引擎，只改文字节点）；其余平台 → surgical（`write_docx_surgical.py`）。两个引擎均为既有脚本，v3 只做分发。
- **PPTX**：按 key 中的形状路径（含组合形状子级）定位元素，只写 run 文本，排版不碰；
  run 数量与 parts 数量不一致即报错退出。

DOCX surgical 引擎说明：只写 `<w:t>` 文本节点（python-docx 定位元素使合并单元格 key 对应、lxml 改写），
保留分页符、`w:ptab`、域（`w:fldChar`/`w:instrText`）、锚定绘图与 `w:pict`；
短高方差分段（封面/标题样式）合并为单 run 避免排版拼凑；多分段单元格经 `para_splits` 保留换行。

DOCX WIR 引擎说明：生成 `TextEdit` 对象按 story 应用，不重建文档。仅 Linux 可加载编译引擎。
详见 `references/wir-integration.md`。

Legacy fallback（仅当 v3 写回器不可用时）：`write_docx_surgical.py` / `write_docx_wir.py` / `write_pptx_v2.py`。

## Step 7: QA（单一入口）

```bash
python scripts/qa_v3.py source output translated.json translation.md [--numerals whitelist.json] [--render out.pdf]
```

一次跑完全部阻断检查，任何一项不过即 exit 1、不得交付：

1. **结构与文本**：
   - PPTX → 回抽比对：文本一致、run 数量一致、分段切分（`para_splits`）一致、
     格式签名（粗体/斜体/字号/颜色逐 run）一致、key 集合一致。
   - DOCX → `verify_structure.py`（结构节点计数 + 译文覆盖；目标语言含 CJK 时自动改用 `--expect-cjk` 门，
     避免 EN→CJK 被 CJK 残留扫描误报）。
2. **数字保真**：已翻译元素的数字词元与原文一致；书写形式转换（`1.2 billion` → `12 亿`、
   `Oct 2023` → `2023 年 10 月`、`Top-10` → `排名前十`）数值不变，记入数字形式白名单后放行。
3. **拼接一致**：每个元素的 parts 拼接与译文一致（去空白比对）。

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
│   ├── extract_v3.py                 # 合一提取器：DOCX + PPTX（v3 主入口）
│   ├── merge_v3.py                   # 合并 + run 切分一步完成（v3 主入口）
│   ├── write_v3.py                   # 合一写回器：DOCX WIR/surgical 分发 + PPTX 嵌套 key（v3 主入口）
│   ├── qa_v3.py                      # 单一 QA 入口：结构/文本/格式/数字（v3 主入口）
│   ├── extract_docx_v2.py            # DOCX 提取内核（extract_v3 调用；独立可用）
│   ├── json_to_markdown_v2.py        # keyed JSON → keyed markdown (Step 2)
│   ├── chunk_keyed.py                # marker-safe chunk splitter (Step 3)
│   ├── reconcile_consistency.py      # TOC↔headingscaptions reconcile (Step 3/5)
│   ├── merge_keyed_structure_aware.py# 结构化合并内核（merge_v3 调用；独立可用）
│   ├── write_docx_surgical.py        # w:t-level write-back, preserves fields/images（write_v3 分发目标）
│   ├── write_docx_wir.py             # WIR-engine write-back (Linux only)（write_v3 分发目标）
│   ├── engine_select.py              # environment-adaptive engine decision（write_v3 调用）
│   ├── xlsx_translate.py             # XLSX: shared strings + sheet names only (format-safe)
│   ├── localize_cjk_en.py            # CJK→EN layout: fonts/numbering/tracking/justify/fields
│   ├── paginate_plan.py              # pagination pre-pass + bounded --repair (Step 6)
│   ├── toc_pages.py                  # rewrite TOC page numbers from rendered PDF (Step 7)
│   ├── verify_structure.py           # DOCX structure+coverage gate（qa_v3 调用）
│   ├── render_pdf.ps1                # DOCX→PDF via Word COM / LibreOffice (Step 7b)
│   ├── render_qa.py                  # rendered QA: blanks/CJK/TOC-pages/montage (Step 7b)
│   ├── build_fixture.py              # structural fixture generator (selftest)
│   ├── selftest.py                   # one-command regression selftest
│   ├── extract_pptx_v2.py            # legacy: PPTX 顶层形状提取（组合形状子级取不到，已被 extract_v3 取代）
│   ├── markdown_to_json_v2.py        # legacy naive merge（空 run 污染，已被 merge_v3 取代）
│   ├── write_docx_v2.py              # legacy run.text write-back（破坏域/绘图，已被 write_v3 取代）
│   ├── write_pptx_v2.py              # legacy: PPTX 顶层 key 写回（嵌套形状不可写，已被 write_v3 取代）
│   └── validate_v2.py                # keyed JSON sanity (legacy, weak — see Troubleshooting)
├── references/
│   ├── schema-v2.md                  # Keyed JSON schema
│   ├── wir-integration.md            # How to use docx skill WIR engine
│   ├── optimization-notes.md         # v1 → v2 rationale and upstream issues
│   ├── cjk-en-localization-pitfalls.md  # CJK→EN localization checklist (v2.1)
│   └── subagent-prompt-template.md   # parallel-chunk prompt template (v2.3：翻译+审校双角色)

工作产物（任务目录内，按生成顺序）：
01-context.md（全文理解，含缩写推断依据）→ 翻译规格单（用户确认）→ 02-prompt.md（共享上下文）
→ chunks/chunk-NN-draft.md（并行翻译）→ chunks/chunk-NN-review.md（独立审校）
→ translation.md + run_splits.json（精确 run 切分）→ translated.json（merge_v3 一步产出，无中间件）
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
| 译文语域错位（设施页译成团队口吻） | 译者只拿到孤立文本块，缺页面语境 | Step 3.0 全文理解 + 3.2 每区块附页面语境；禁止只投喂文本块 |
| 缩写误译（BU 留白或错判） | 缩写处置被固化在模板里，未按全文推断 | Step 3.0 缩写清单须给出语境推断与依据；判定不了的进待确认清单交用户 |
| 区块间同一概念用词不一（同类最优/同类最佳） | 各区块独立翻译缺共享术语表 | Step 3.0 术语表 + 3.4 跨区块统一 |
| 译文翻译腔（语序迁就数字位置） | 译者为保数字位置扭曲句子 | 译者只输出自然句子；run 切分后置（Step 4），数值 run 完整保留数字词元 |
| 标题被切成不相干的词（Core / Expertise） | 多分段元素逐段孤立翻译 | 译者按整块理解后重排行文；审校子代理专查此项（Step 3.3） |
| 数字书写形式与全篇冲突（800 万美元 vs $8.0M） | 数字写法未按全文统一 | Step 3.0 数字写法倾向 + 7a 数字保真核对与白名单 |
| Missing header/footer text | First/even-page variants or fused WPS fields not written | Surgical path covers all three header/footer variants; run `localize_cjk_en.py fields` for CJK field switches; verify with gate (non-body coverage check) |
| PPTX table cells not translated | Used v1 `write_pptx.py` | Use `scripts/write_v3.py` |
| Hyperlink URL lost | Used v1 extraction | Use v2 extraction + write |
| Markdown mapping failed | Translator moved/deleted `<!--key:...-->` markers | Add stronger marker-preservation instructions |
| Image text not caught | Heuristic only | Enable OCR pass |
| Whole English doc renders in SimSun/CJK font | Source set `w:ascii/hAnsi` to CJK fonts | `references/cjk-en-localization-pitfalls.md` §2 |
| Garbage bullet glyphs after numbering edits | Bulk-replaced non-ASCII `w:lvlText` (Wingdings PUA glyphs) | Pitfalls §3 TRAP — edit only the verified abstractNum |
| Blank pages / TOC not on its own page | CJK natural flow + empty spacer paras + double page breaks | `scripts/paginate_plan.py` (+`--h1-always`), then `--repair` once; figure-only page = plate, not blank |
| Header/date reverts to Chinese after Word export | Field instrText keeps CJK format switch (`Time \@ "yyyy年M月d日"`) | `localize_cjk_en.py fields` (sanitizes switch + Time→TIME); confirm via `render_qa.py --cjk-scan` |
| Wrong TOC page numbers | Source pagination kept | `scripts/toc_pages.py` (rewrites from rendered PDF); verify with `render_qa.py --toc-check` |
| Text scattered into empty runs, page numbers misplaced | Bundled proportional merge gives empty runs a ratio | Use `scripts/merge_v3.py`（底层即结构化合并） |
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
6. Cross-chunk consistency reconcile: `scripts/reconcile_consistency.py` (exit 1 = 先统一用词);
   分块 + 并行提示词按 Step 3 流程（01-context.md → 规格单 → 并行翻译 + 独立审校 → 跨区块统一），
   提示词模板见 `references/subagent-prompt-template.md`
7. Structure-aware merge: `scripts/merge_keyed_structure_aware.py`
8. **Rendered QA (mandatory)**: `scripts/render_pdf.ps1 -Docx out.docx`, then
   `python scripts/render_qa.py out.pdf src.pdf --toc-check --cjk-scan --montage sheets`
   and visually review EVERY montage sheet. Text-level QA cannot see any of the above.

## License

Same as baoyu-document-translator v1.
