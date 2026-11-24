---
name: baoyu-document-translator-v4
description: Format-preserving translation and localization for DOCX and PPTX documents (runs, fields, shapes, tables, headers/footers, footnotes, speaker notes), plus format-safe XLSX translation (shared strings and sheet names only). Use when translating or localizing .docx, .pptx, or .xlsx files where page layout and styling must remain intact. Do not use for plain text or Markdown translation (use baoyu-translate instead).
version: 4.3.0
metadata:
  openclaw:
    homepage: https://github.com/JimLiu/baoyu-skills
    requires:
      anyBins:
        - python
        - python3
      pythonPackages:
        - python-docx
        - python-pptx
        - lxml
        - pymupdf
        - Pillow
        - requests
        - pywin32
---

# Document Translator v4（v4.3 统一 CLI + 双模式合一版）

把 DOCX / PPTX / XLSX 翻译成目标语言，**格式不变**。所有核心动作收口至单一入口 **`scripts/doc_trans.py`**（`python scripts/doc_trans.py --help`）。

## 双模式决策表（原 v3.6 与 v4 思路合一，共用 v4.3 内核）

| 模式 | 核心思路 | 适用场景 | 外部依赖 |
|---|---|---|---|
| **Mode A：原生子代理 + 纯文本流**（原 v3.6） | `extract --md` → `chunk --extracted` → 当前宿主 Agent 并行翻译/审校/抽查 → `merge` → `write` → `qa` | **DOCX 默认路线**；无 Office/无外部 API Key；或希望直接用当前旗舰 Agent（Claude/Gemini/DSH）精翻；或做 A/B 对比 | **零额外密钥**，全平台开箱即用 |
| **Mode B：整页视觉 + 直调 API 流**（原 v4） | `pptx-prep`（4 步合一）→ `dispatch` → `api-call`（或子代理看图）→ `apply-patches` → `merge` → `write` → `qa` → 终稿视觉核对 | **重排版/多图 PPTX 默认路线**；需看图控长度、登记图内烘焙字、做终稿视觉验收；或大批量追求极低 token 成本 | PowerPoint COM 或 LibreOffice；可选 `AISTUDIO_OCR_TOKEN`；兼容 OpenAI 的视觉模型 API Key |

> **默认路由**：DOCX → Mode A；PPTX → Mode B（无外部 API Key 时改走 Mode B 原生子代理看图或 Mode A）。用户可随时显式指定「用 Mode A」或「用 Mode B」做效果对比。
> **DOCX 写回引擎路由**：Linux / WSL2 优先调用 `docx` skill 的编译版 **WIR `.so` 引擎**（`write_docx_wir.py`，支持翻窗与全 part 写回）；原生 Windows / macOS 自动回退纯 Python **`write_docx_surgical.py`**（支持 `--engine auto|wir|surgical` 显式指定）。

## TL;DR — Mode A（DOCX 默认 / PPTX 轻量）

```bash
python scripts/doc_trans.py extract input.docx extracted.json --md source.md
python scripts/doc_trans.py chunk source.md chunks 4200 --extracted extracted.json
# …… 01-context.md 全文理解 → 规格确认 → 并行子代理翻译 / 独立审校 / compare 逐页抽查 → translation.md + run_splits.json ……
python scripts/doc_trans.py merge extracted.json translation.md translated.json [run_splits.json]
python scripts/doc_trans.py write input.docx output.docx translated.json
python scripts/doc_trans.py qa input.docx output.docx translated.json translation.md [--numerals whitelist.json]
```

## TL;DR — Mode B（PPTX 整页视觉默认）

```bash
python scripts/doc_trans.py pptx-prep input.pptx work --per-group 3
python scripts/doc_trans.py dispatch translate work/groups --context 01-context.md --ocr-dir work/slides/ocr --images work/slides
python scripts/doc_trans.py api-call translate work/groups --images work/slides   # 无 Key 改走原生子代理看图
# …… review（补丁）→ unify（统一）……
python scripts/doc_trans.py apply-patches work/groups
python scripts/doc_trans.py merge work/extracted.json translation.md translated.json [run_splits.json]
python scripts/doc_trans.py write input.pptx output.pptx translated.json
python scripts/doc_trans.py qa input.pptx output.pptx translated.json translation.md [--numerals whitelist.json]
python scripts/doc_trans.py render-slides output.pptx work/out_slides            # 终稿页面图视觉核对
```

## TL;DR — XLSX（共享字符串 + 表名安全写回）

```bash
python scripts/doc_trans.py xlsx input.xlsx output.xlsx map.json
```

---

## 不可跳过的三条硬规则

1. **先理解后开译**：翻译前必须产出并经用户确认 `01-context.md`（文档语域、缩写释义与依据、数字与金额写法、强调规律、保留英文清单）与翻译规格单。禁止对孤立文本块直接开译（同系列文档可复用已确认规格）。
2. **并行派发 + 独立审校**：全部块/组一次并行派发，审校方不得参与该块/组翻译；角色契约与补丁格式见 `references/subagent-prompt-template.md`。
3. **阻断式质检**：`doc_trans.py qa` 任何一项未通过即 `exit 1`，不得交付；交付前按 `references/qa-pack.md` 完成渲染 QA 目检。

---

## 关键步骤细则

- **环境检查**：`python scripts/doc_trans.py engine-info` 查看当前平台推荐的 DOCX 写回引擎（Linux/WSL2 报告 `wir`，原生 Windows/macOS 报告 `surgical`）；修改脚本后运行 `python scripts/doc_trans.py selftest`（27 项端到端回归自测）。
- **Mode B 审校与跨组统一**：
  ```bash
  python scripts/doc_trans.py dispatch review work/groups --group NN --context 01-context.md
  python scripts/doc_trans.py api-call review work/groups --group NN
  python scripts/doc_trans.py dispatch unify work/groups --context 01-context.md
  python scripts/doc_trans.py api-call unify work/groups
  python scripts/doc_trans.py apply-patches work/groups
  ```
- **Mode B 终稿视觉核对**：
  ```bash
  python scripts/doc_trans.py render-slides output.pptx work/out_slides
  python scripts/doc_trans.py dispatch visual work/groups --context 01-context.md --images work/out_slides
  python scripts/doc_trans.py api-call visual work/groups --images work/out_slides
  ```
  查漏译、误译、溢出、重叠、截断与数字错误（图内烘焙文字保留源语言属既定政策）；发现问题修补后重跑 `merge` → `write` → `qa`。
- **Mode A 逐页/逐 story 对照抽查**：
  ```bash
  python scripts/doc_trans.py compare extracted.json translated.json pages
  ```

---

## 参考文件（按需加载）

- `references/docx.md` — DOCX：key 规则、提取范围、写回引擎（Linux/WSL2 WIR `.so` vs Windows/macOS surgical）
- `references/pptx.md` — PPTX：key 规则、形状树提取、run 写回
- `references/translation-workflow.md` — Mode A（DOCX 分块）流程细则与共用 01-context / 规格单规范
- `references/subagent-prompt-template.md` — Mode A / Mode B 共享契约、角色提示词与补丁格式
- `references/qa-pack.md` — 阻断 QA、渲染 QA、CJK→EN 本地化与故障排查
- `references/script-index.md` — 统一 CLI 子命令与底层脚本清单
- `references/schema-v2.md` — keyed JSON schema
- `references/cjk-en-localization-pitfalls.md` — 中→英版式本地化清单

## License

MIT License (derived from `baoyu-document-translator` in `JimLiu/baoyu-skills`).
