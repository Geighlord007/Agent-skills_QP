# baoyu-document-translator-v4（v4.3 统一 CLI + 双模式合一版）

高保真 **DOCX / PPTX / XLSX** 办公文档翻译技能：在不破坏原版式（run 样式、域、页眉页脚、脚注、文本框、表格、备注）的前提下完成专业级多阶段翻译、独立审校与阻断式质检。所有核心步骤已收口到统一入口 **`scripts/doc_trans.py`**。

> 版本演化全记录见 [CHANGELOG.md](./CHANGELOG.md) 与仓库根 `../VERSION_HISTORY.md`。原 `v3.6` 路线已合流为本技能 **Mode A**，共享同一套 v4.3 加固内核。

## 与兄弟技能的边界

| 技能 | 定位 | 关系 |
|---|---|---|
| `baoyu-document-translator-v4`（本技能） | **`.docx` / `.pptx` / `.xlsx` 格式保真翻译**（统一 `doc_trans.py` CLI + Mode A / Mode B） | 办公文档翻译主力入口 |
| `baoyu-translate` | 纯文本 / Markdown / 网页文章翻译 | 互补，不处理二进制办公文档 |
| `docx` | Word 生成与底层编辑（持有 Linux/WSL2 WIR `.so` 与全平台 `engine_surgical`） | 底层依赖；**Linux/WSL2 强制优先走 WIR `.so`**，原生 Windows/macOS 自动回退 `surgical` |
| `paddleocr-doc-parsing` | 复杂 PDF / 扫描件版面解析 | 互补（本技能 `ocr-slides` 仅做 PPTX 图内文字语境登记） |

## 统一 CLI 速查（`scripts/doc_trans.py`）

- **Mode A（原生子代理 + 纯文本，DOCX 默认 / PPTX 轻量）**：
  ```bash
  python scripts/doc_trans.py extract input.docx extracted.json --md source.md
  python scripts/doc_trans.py chunk source.md chunks 4200 --extracted extracted.json
  # 01-context.md → 规格确认 → 并行翻译 / 审校 / compare 逐页抽查 → translation.md + run_splits.json
  python scripts/doc_trans.py merge extracted.json translation.md translated.json [run_splits.json]
  python scripts/doc_trans.py write input.docx output.docx translated.json
  python scripts/doc_trans.py qa input.docx output.docx translated.json translation.md
  ```
- **Mode B（整页视觉 + 直调 API，PPTX 重排版默认）**：
  ```bash
  python scripts/doc_trans.py pptx-prep input.pptx work --per-group 3   # 4 步合一
  python scripts/doc_trans.py dispatch translate work/groups --context 01-context.md --ocr-dir work/slides/ocr --images work/slides
  python scripts/doc_trans.py api-call translate work/groups --images work/slides
  # review 补丁 → unify 统一 → apply-patches → merge → write → qa → 终稿视觉核对
  ```
- **XLSX / 环境检测 / 回归自测**：
  ```bash
  python scripts/doc_trans.py xlsx input.xlsx output.xlsx map.json
  python scripts/doc_trans.py engine-info          # 查看 Linux WIR .so vs surgical 路由
  python scripts/doc_trans.py selftest             # 27 项端到端回归自测
  ```
