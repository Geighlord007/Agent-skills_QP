---
name: baoyu-document-translator-v4
description: Translate DOCX / PPTX documents into the target language while preserving formatting (runs, fields, shapes, tables, headers/footers, footnotes, speaker notes). Use whenever the user asks to translate, localize, 中文化 or 英文化 a .docx or .pptx file — reports, pitch decks, papers, manuals — or any document translation where page layout must not change. PPTX uses slide-image-guided translation (each slide translated with its rendered page in view) plus OCR registration of image-baked text; DOCX uses keyed chunk translation. Parallel sub-agents, independent review, blocking QA gate. XLSX translation via scripts/xlsx_translate.py (shared strings + sheet names only).
version: 4.1.0
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
        - requests
        - pywin32
---

# Document Translator v4

把 DOCX / PPTX 翻译成目标语言，**格式不变**。XLSX 走独立脚本（Step 0）。

## TL;DR — PPTX 一条链

```bash
python scripts/extract_v3.py input.pptx extracted.json          # 1. 提取（key + run 元信息）
python scripts/render_slides.py input.pptx slides               #    逐页导出页面图
python scripts/ocr_slides.py slides                             #    图内文字登记（保留带位置原始 JSONL）
python scripts/slide_bundles.py extracted.json --out groups     #    按页分组构建翻译单元
python scripts/build_dispatch.py translate groups --context 01-context.md --ocr-dir slides/ocr --images slides
python scripts/api_call.py translate groups --images slides      # 并行调 MiMo 接口产出草稿（看图）
#    …… 全文理解 → 规格确认 → api_call review（补丁）→ api_call unify（统一）……
python scripts/apply_patches.py groups                          # 2. 补丁落稿 + run_splits.json + translation.md
python scripts/merge_v3.py extracted.json translation.md translated.json [run_splits.json]
python scripts/write_v3.py input output translated.json         # 3. 写回
python scripts/qa_v3.py input output translated.json translation.md [--numerals whitelist.json]   # 阻断质检
python scripts/render_slides.py output out_slides               #    终稿页面图（视觉核对用）
```

不可跳过的三件事：

1. 翻译文本之前产出两份产物并经用户确认：`01-context.md`（全文理解）与翻译规格单。
   直接对源块开译是被禁止的路径——译者拿到孤立文本块会丢失语境，缩写与数字写法会随译者默认值漂移。
2. 全部组一次派发；翻译、审校、视觉核对都是并行子代理，任务书由 `build_dispatch.py` 生成
   （内容随任务书下发，子代理零查找），角色规则见 `references/subagent-prompt-template.md`。
3. `qa_v3.py` 任何一项不过即 exit 1，不得交付。

DOCX 没有页面图，沿用分块流程：`references/translation-workflow.md`（全文理解 → 规格单 →
分块并行翻译 → 独立审校 + run 切分 → 逐页文本抽查 → 跨区块统一），合并、写回、质检同上。

其余脚本（体检 / 渲染 QA / 版式本地化 / 分页 / 目录页码 / 回归自测）属于**可选质检包**，
默认不跑，清单见 `references/qa-pack.md`。

## Step 0: 环境与路径选择

- PPTX：`extract_v3.py` / `render_slides.py`（PowerPoint COM 导出页面图）/ `ocr_slides.py`
  （AI Studio OCR 接口；token 在 `~/.agents/keys/aistudio.key` 或 `AISTUDIO_OCR_TOKEN`）/
  `slide_bundles.py` / `build_dispatch.py` / `apply_patches.py` / `merge_v3.py` / `write_v3.py` / `qa_v3.py`。
- DOCX：同一条键控链（提取 / 合并 / 写回 / 质检合一），写回引擎由 `write_v3.py` 调用
  `engine_select.py` 自动分发（Linux/WSL2 → WIR，其余平台 → surgical，见 `references/docx.md`）。
- XLSX：用 `xlsx_translate.py`（只改共享字符串 + 表名；注意 Excel 表名上限 31 字符）。

## Step 1: 提取、页面图、图内文字登记

```bash
python scripts/extract_v3.py input.pptx extracted.json     # key + parts + run_styles + para_splits
python scripts/render_slides.py input.pptx slides          # slide-NN.jpg（宽 1600）
python scripts/ocr_slides.py slides                        # slides/ocr/slide-NN.md + 原始 JSONL（带位置）
```

key 规则与格式细节：`references/pptx.md`（DOCX 读 `references/docx.md`）。图内文字（图片里
烘焙的字）只登记不回写，登记结果随任务书下发给译者作语境。

## Step 2: 全文理解与规格单（阻断，需用户确认）

通读源文产出 `01-context.md`（文档类型与语域、缩写清单与推断依据、数字与金额写法倾向、
强调排布规律、保留英文清单），据此汇总翻译规格单交用户确认，确认后才开译。细则见
`references/translation-workflow.md`。同系列文档可复用已确认的规格。

## Step 3: 并行翻译（整页视觉）+ 独立审校（补丁直出）

```bash
python scripts/slide_bundles.py extracted.json --out groups --per-group 3
python scripts/build_dispatch.py translate groups --context 01-context.md --ocr-dir slides/ocr --images slides
```

每组一个翻译请求：`api_call.py translate` 把任务书与本组页面图发给模型接口（默认
`mimo-v2.6-pro`，密钥 `~/.agents/keys/mimo.key`），并行产出 `groups/draft-NN.md`
（整块译文；页面效果在图上当场取舍措辞与长度）。全部组一次并发。子代理执行方式见
`references/subagent-prompt-template.md` Part 5（无接口密钥时的替代路线）。

每组译完**立即**审校（未参与该组翻译）：

```bash
python scripts/build_dispatch.py review groups --group NN --context 01-context.md
python scripts/api_call.py review groups --group NN
```

审校产出 `groups/patches-NN.json`（修订补丁 + run 切分 + 备注）；
只查语义与表达，机械核对统一交 `qa_v3.py`。

跨组统一：

```bash
python scripts/build_dispatch.py unify groups --context 01-context.md
python scripts/api_call.py unify groups
```

统一补丁改动多 run 元素时须同步给出新切分。然后：

```bash
python scripts/apply_patches.py groups     # 补丁落稿 + run_splits.json + translation.md
```

角色规则与补丁格式见 `references/subagent-prompt-template.md`。

## Step 4: 合并 + 写回

```bash
python scripts/merge_v3.py extracted.json translation.md translated.json [run_splits.json]
python scripts/write_v3.py input.pptx output.pptx translated.json
```

合并按 key 回填并校验拼接（不一致报错退出）；`run_splits.json` 是精确 run 切分覆盖
（强调短语对位、换行不跨段、数值词元完整），不提供时沿用自动切分。写回只写 run 文字节点，
run 数量与 parts 数量不一致即报错退出。合并内部行为见 `references/translation-workflow.md`。

## Step 5: QA（单一入口，阻断）

```bash
python scripts/qa_v3.py input output translated.json translation.md [--numerals whitelist.json]
```

阻断检查（7a）：结构与文本（PPTX 回抽比对 / DOCX `verify_structure.py`）、数字保真
（书写形式转换记入白名单放行）、parts 拼接一致。任何一项不过即 exit 1、不得交付。
检查细目见 `references/qa-pack.md`。

## Step 6: 视觉核对（终稿页面图）

```bash
python scripts/render_slides.py output out_slides
python scripts/build_dispatch.py visual groups --context 01-context.md --images out_slides
python scripts/api_call.py visual groups --images out_slides
```

每组一次视觉核对请求（模型看终稿页面图返回 `groups/issues-NN.json`）：
查漏译、误译、溢出、重叠、截断、数字错误；图内文字保留源语言属于既定政策，不算问题。
发现问题修补后重跑 Step 4–5。交付前必做渲染 QA（转 PDF 查空白页等）见 `references/qa-pack.md` 7b。

## 参考文件

- `references/docx.md` — DOCX：key 规则、提取范围、写回引擎（WIR / surgical）
- `references/pptx.md` — PPTX：key 规则、形状树提取、run 写回
- `references/translation-workflow.md` — DOCX 分块流程细则与工作产物清单
- `references/subagent-prompt-template.md` — 三个角色的任务书规则与补丁格式
- `references/qa-pack.md` — 可选质检包、渲染 QA、CJK→EN 本地化、Troubleshooting
- `references/script-index.md` — 脚本清单（含 legacy）与依赖
- `references/schema-v2.md` — keyed JSON schema
- `references/wir-integration.md` — `docx` skill WIR 引擎的接入说明
- `references/cjk-en-localization-pitfalls.md` — 中→英版式本地化清单
- `references/optimization-notes.md` — v1 → v2 演进记录与上游问题
- `references/safe-docx-evaluation.md` — Safe Docx 实测数据（留痕交付可选）

## License

Same as baoyu-document-translator v1.
