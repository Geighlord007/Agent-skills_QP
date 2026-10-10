---
name: baoyu-document-translator-v3.6
description: Translate DOCX / PPTX documents into the target language while preserving formatting (runs, fields, shapes, tables, headers/footers, footnotes, speaker notes). Use whenever the user asks to translate, localize, 中文化 or 英文化 a .docx or .pptx file — reports, pitch decks, papers, manuals — or any document translation where page layout must not change. Keyed round-trip extraction and write-back (WIR on Linux/WSL2, surgical elsewhere), parallel chunk translation with independent review and page-level spot-check, blocking QA gate. XLSX translation via scripts/xlsx_translate.py (shared strings + sheet names only).
version: 3.6.0
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

# Document Translator v3.6

把 DOCX / PPTX 翻译成目标语言，**格式不变**。XLSX 走独立脚本（Step 0）。

## TL;DR — 三步一条链

```bash
python scripts/extract_v3.py input.docx|input.pptx extracted.json       # 1. 提取（DOCX/PPTX 合一）
python scripts/json_to_markdown_v2.py extracted.json source.md         #    转成可翻译文本
#    …… 全文理解 → 规格确认 → 并行翻译 + 独立审校 → 逐页抽查 → 跨区块统一，写出 translation.md ……
python scripts/merge_v3.py extracted.json translation.md translated.json [run_splits.json]   # 2. 合并 + run 切分一步完成
python scripts/write_v3.py input output translated.json                # 3. 写回（DOCX: WIR/surgical 自适应；PPTX: 嵌套形状）
python scripts/qa_v3.py input output translated.json translation.md [--numerals whitelist.json]   # 阻断质检
```

不可跳过的三件事：

1. 翻译文本之前产出两份产物并经用户确认：`01-context.md`（全文理解）与翻译规格单。
   直接对 source.md 分块开译是被禁止的路径——译者拿到孤立文本块会丢失语境，
   区块之间会各译各的，缩写与数字写法也会随译者默认值漂移。
2. 全部区块一次派发，翻译、审校、逐页抽查都是并行子代理；提示词按
   `references/subagent-prompt-template.md`，流程细则按 `references/translation-workflow.md`。
3. `qa_v3.py` 任何一项不过即 exit 1，不得交付。

其余脚本（体检 / 渲染 QA / 版式本地化 / 分页 / 目录页码 / 回归自测）属于**可选质检包**，
默认不跑，清单见 `references/qa-pack.md`。

## Step 0: 环境与路径选择

- DOCX / PPTX：统一用 `extract_v3.py` / `merge_v3.py` / `write_v3.py` / `qa_v3.py`。
  DOCX 写回引擎由 `write_v3.py` 内部调用 `engine_select.py` 自动分发
  （Linux/WSL2 → WIR，其余平台 → surgical，见 `references/docx.md`）。
- XLSX：用 `xlsx_translate.py`（只改共享字符串 + 表名，格式/图表/图片零风险；注意 Excel 表名上限 31 字符）。

## Step 1: Extract document to keyed JSON

```bash
python scripts/extract_v3.py input.docx|input.pptx extracted.json    # 合一提取器
```

按扩展名分发：DOCX 走全部 story 提取，PPTX 走形状树遍历（含组合形状子级、表格单元格、备注），
并记录 `para_splits` 与逐 run 格式签名（粗体/斜体/字号/颜色）供质检比对。
key 规则与格式细节：DOCX 读 `references/docx.md`，PPTX 读 `references/pptx.md`。

## Step 2: Convert to keyed markdown

```bash
python scripts/json_to_markdown_v2.py extracted.json source.md
```

每个可翻译块前置一个 HTML 注释标记：

```markdown
<!--key:p_body_0|runs:3-->
# Introduction
```

- `key`：稳定的元素标识；`runs`：译文预期的 run 数量；`type`：paragraph/table_cell/shape 等（可选）。
- 合并按 key 回填，译者可以为行文自然分合段落而不破坏文档结构。

## Step 3: Translate（全文理解 → 规格确认 → 并行翻译 + 独立审校 + 逐页抽查）

流程与产物顺序：`01-context.md`（全文理解）→ 翻译规格单（用户确认）→ 分块并行翻译
→ 独立审校 + 修订 + run 切分 → 逐页抽查（与写回重叠）→ 跨区块统一 → `translation.md`。
每一步的细则与产物格式见 `references/translation-workflow.md`；
三个子代理角色（翻译 / 审校 / 逐页抽查）的提示词见 `references/subagent-prompt-template.md`，
run 切分规则以其 Part 3 为准。

## Step 4: Merge keyed translation back to JSON（合并 + run 切分一步完成）

```bash
python scripts/merge_v3.py extracted.json translation.md translated.json [run_splits.json]
```

基于结构化合并按 key 回填；`run_splits.json` 为精确 run 切分覆盖（审校阶段产出），
不提供时完全沿用自动切分，合并一步写入最终 `translated.json`，不产生中间产物。
合并的内部行为见 `references/translation-workflow.md`。

## Step 5: Validate — 没有独立的校验环节

合并时按 key 报警（缺少 key、run 数不匹配等），阻断门统一在 Step 7a。
`validate_v2.py` 是 legacy，不要使用。详见 `references/qa-pack.md`。

## Step 6: Write back to document

```bash
python scripts/write_v3.py input.docx|input.pptx output translated.json   # 合一写回器
```

按扩展名分发：DOCX 自动选引擎（`references/docx.md`），PPTX 按 key 中的形状路径只写 run 文本、
排版不碰（`references/pptx.md`）。run 数量与 parts 数量不一致即报错退出。

## Step 7: QA（单一入口，阻断）

```bash
python scripts/qa_v3.py source output translated.json translation.md [--numerals whitelist.json] [--render out.pdf]
```

阻断检查（7a）：结构与文本（PPTX 回抽比对 / DOCX `verify_structure.py`）、数字保真
（书写形式转换记入白名单放行）、parts 拼接一致。任何一项不过即 exit 1、不得交付。
交付前必做渲染 QA（7b）：转 PDF 后检查空白页、残留源语言、目录页码，缩略图表逐张查看。
检查细目、可选检查（7c/7d）、CJK→EN 版式本地化八条与 Troubleshooting 全表见 `references/qa-pack.md`。

## 参考文件

- `references/docx.md` — DOCX：key 规则、提取范围、写回引擎（WIR / surgical）
- `references/pptx.md` — PPTX：key 规则、形状树提取、run 写回
- `references/translation-workflow.md` — 翻译流程细则与工作产物清单
- `references/subagent-prompt-template.md` — 翻译 / 审校 / 逐页抽查三个角色的提示词
- `references/qa-pack.md` — 可选质检包、渲染 QA、CJK→EN 本地化、Troubleshooting
- `references/script-index.md` — 脚本清单（含 legacy）与依赖
- `references/schema-v2.md` — keyed JSON schema
- `references/wir-integration.md` — `docx` skill WIR 引擎的接入说明
- `references/cjk-en-localization-pitfalls.md` — 中→英版式本地化清单
- `references/optimization-notes.md` — v1 → v2 演进记录与上游问题
- `references/safe-docx-evaluation.md` — Safe Docx 实测数据（留痕交付可选）

## License

Same as baoyu-document-translator v1.
