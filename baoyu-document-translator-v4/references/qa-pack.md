# 质检包与质量检查

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
| `selftest.py` | 脚本自身回归测试（24 项） |
| `references/safe-docx-evaluation.md` | **留痕交付（可选）**：第三方 Safe Docx 的实测数据与组合写回方案 |

## 合并阶段没有独立的校验环节

merge 打印按 key 的警告（SEG_MISMATCH 等），阻断门统一在 Step 7a（DOCX 用 `verify_structure.py`；
PPTX 用回抽比对 + 数字保真核对）。不要自造 `--precheck` 之类的调用方式；`validate_v2.py`
是 legacy，能力弱（只做 key/run 合法性检查）。校验覆盖的内容：
- JSON is valid
- Every extracted key is present
- No extra keys
- `parts.length == runs` for every element
- Hyperlink targets still point to valid URLs (if present)
- Headers/footers/footnotes are included if source had them

## 7a. 阻断检查（结构 / 文本 / 数字 / 拼接）

一次跑完全部阻断检查，任何一项不过即 exit 1、不得交付：

1. **结构与文本**：
   - PPTX → 回抽比对：文本一致、run 数量一致、分段切分（`para_splits`）一致、
     格式签名（粗体/斜体/字号/颜色逐 run）一致、key 集合一致。
   - DOCX → `verify_structure.py`（结构节点计数 + 译文覆盖；目标语言含 CJK 时自动改用 `--expect-cjk` 门，
     避免 EN→CJK 被 CJK 残留扫描误报）。
2. **数字保真**：已翻译元素的数字词元与原文一致；书写形式转换（`1.2 billion` → `12 亿`、
   `Oct 2023` → `2023 年 10 月`、`Top-10` → `排名前十`）数值不变，记入数字形式白名单后放行。
3. **拼接一致**：每个元素的 parts 拼接与译文一致（去空白比对）。

## 7b. Rendered QA (mandatory)

```bash
pwsh -File scripts/render_pdf.ps1 -Docx output.docx                 # Word COM (also validates schema)
python scripts/render_qa.py output.pdf input-rendered-src.pdf --cjk-scan --toc-check --montage sheets
```

Blank pages (auto-detected chrome), rendered CJK residue, TOC page-number accuracy,
and 3×4 thumbnail sheets. **Visually review every sheet** — text-level QA cannot see
layout defects. For CJK→EN jobs also apply
`cjk-en-localization-pitfalls.md` (fonts, numbering, tracking, pagination).

## 7c. Image QA (optional)

Embedded raster figures may keep source-language text. `qa_images_v2.py` is NOT shipped
with this revision; use `render_qa.py --montage` sheets for visual inspection and report
text-heavy figures to the user (do not auto-localize unless asked).

For OCR image QA (optional): `pip install paddleocr`。

## 7d. Legacy visual QA

```bash
libreoffice --headless --convert-to pdf output.docx
pdftoppm -jpeg -r 150 output.pdf page
```

## CJK→EN localization addendum (v2.1)

For Chinese→English (or any CJK→Latin) jobs the simple path needs a localization pass
between write-back and QA. Read **`cjk-en-localization-pitfalls.md`** and apply:

1. Run-structure audit (page breaks / `w:ptab` / fields / anchored images survived?)
2. Font / numbering / tracking localization: `scripts/localize_cjk_en.py fonts|numbering|tracking`
3. Table justify in narrow columns: `scripts/localize_cjk_en.py justify`
4. Pagination rebuild (structural page breaks, empty-paragraph cleanup, blank-page scan)
5. TOC page-number rewrite from the rendered PDF
6. Cross-chunk consistency reconcile: `scripts/reconcile_consistency.py` (exit 1 = 先统一用词);
   分块 + 并行提示词按 Step 3 流程（01-context.md → 规格单 → 并行翻译 + 独立审校 → 跨区块统一），
   提示词模板见 `subagent-prompt-template.md`
7. Structure-aware merge: `scripts/merge_keyed_structure_aware.py`
8. **Rendered QA (mandatory)**: `scripts/render_pdf.ps1 -Docx out.docx`, then
   `python scripts/render_qa.py out.pdf src.pdf --toc-check --cjk-scan --montage sheets`
   and visually review EVERY montage sheet. Text-level QA cannot see any of the above.

## Troubleshooting

| Issue | Likely cause | Fix |
|-------|--------------|-----|
| `parts length != runs` | Agent merged runs or deleted marker | Re-translate with explicit marker-preservation instructions |
| 译文语域错位（设施页译成团队口吻） | 译者只拿到孤立文本块，缺页面语境 | Step 3.0 全文理解 + 3.2 每区块附页面语境；禁止只投喂文本块 |
| 缩写误译（BU 留白或错判） | 缩写处置被固化在模板里，未按全文推断 | Step 3.0 缩写清单须给出语境推断与依据；判定不了的进待确认清单交用户 |
| 区块间同一概念用词不一（同类最优/同类最佳） | 各区块独立翻译缺共享术语表 | Step 3.0 术语表 + 3.5 跨区块统一 |
| 译文翻译腔（语序迁就数字位置） | 译者为保数字位置扭曲句子 | 译者只输出自然句子；run 切分后置（Step 4），数值 run 完整保留数字词元 |
| 标题被切成不相干的词（Core / Expertise） | 多分段元素逐段孤立翻译 | 译者按整块理解后重排行文；审校子代理专查此项（Step 3.3） |
| 数字书写形式与全篇冲突（800 万美元 vs $8.0M） | 数字写法未按全文统一 | Step 3.0 数字写法倾向 + 7a 数字保真核对与白名单 |
| Missing header/footer text | First/even-page variants or fused WPS fields not written | Surgical path covers all three header/footer variants; run `localize_cjk_en.py fields` for CJK field switches; verify with gate (non-body coverage check) |
| PPTX table cells not translated | Used v1 `write_pptx.py` | Use `scripts/write_v3.py` |
| Hyperlink URL lost | Used v1 extraction | Use v2 extraction + write |
| Markdown mapping failed | Translator moved/deleted `<!--key:...-->` markers | Add stronger marker-preservation instructions |
| Image text not caught | Heuristic only | Enable OCR pass |
| Whole English doc renders in SimSun/CJK font | Source set `w:ascii/hAnsi` to CJK fonts | `cjk-en-localization-pitfalls.md` §2 |
| Garbage bullet glyphs after numbering edits | Bulk-replaced non-ASCII `w:lvlText` (Wingdings PUA glyphs) | Pitfalls §3 TRAP — edit only the verified abstractNum |
| Blank pages / TOC not on its own page | CJK natural flow + empty spacer paras + double page breaks | `scripts/paginate_plan.py` (+`--h1-always`), then `--repair` once; figure-only page = plate, not blank |
| Header/date reverts to Chinese after Word export | Field instrText keeps CJK format switch (`Time \@ "yyyy年M月d日"`) | `localize_cjk_en.py fields` (sanitizes switch + Time→TIME); confirm via `render_qa.py --cjk-scan` |
| Wrong TOC page numbers | Source pagination kept | `scripts/toc_pages.py` (rewrites from rendered PDF); verify with `render_qa.py --toc-check` |
| Text scattered into empty runs, page numbers misplaced | Bundled proportional merge gives empty runs a ratio | Use `scripts/merge_v3.py`（底层即结构化合并） |
| Word refuses to open the output | Regex surgery broke OOXML child order | Always render via `scripts/render_pdf.ps1` (Word COM validates the file) |
| EN→CJK job flagged by CJK gate | Gate assumes CJK→EN | Pass `--expect-cjk` to `verify_structure.py` |
| Mixed CN/EN doc wastes translation tokens | English-only blocks sent to LLM | Filter CJK-only blocks before chunking (missing keys keep source text at merge) |
| Regression after script edits | No fixture coverage | Run `scripts/selftest.py` (24 checks) before shipping changes |
| `qa_check_v2.py` / `qa_images_v2.py` missing | Not shipped with this skill revision | Use `scripts/render_qa.py` + manual XML checks (pitfalls §1-2) |
