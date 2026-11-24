# 质检包与质量检查（v4.3）

## 可选质检包（默认不跑，按需启用）

| 工具 | 作用 |
|---|---|
| `verify_structure.py` | DOCX 体检：结构节点计数 + 译文覆盖（`exit 1` = 不得交付） |
| `render_pdf.ps1` + `render_qa.py` | 转 PDF 后检查空白页 / 残留源语言 / 目录页码，生成 3×4 缩略图拼图 |
| `localize_cjk_en.py` | 中→英版式本地化：字体、编号、字距、窄列对齐、域开关 |
| `paginate_plan.py` / `toc_pages.py` | 分页预 pass / 按渲染 PDF 回写目录页码 |
| `reconcile_consistency.py` | 目录 ↔ 标题 ↔ 图注跨块一致性核对 |
| `selftest.py` | 技能脚本自身回归自测（24 项） |

---

## 7a. 阻断检查（`qa_v3.py`，必跑）

一次运行全部阻断项，任何一项失败即 `exit 1`、不得交付：

1. **结构与文本**：
   - PPTX：回抽输出文件，逐元素比对 key 集合、文本、run 数量、分段切分（`para_splits`）与逐 run 格式签名（粗体/斜体/字号/颜色）。
   - DOCX：调用 `verify_structure.py` 检查结构节点与译文覆盖（EN→CJK 自动启用 `--expect-cjk`，避免误报）。
2. **数字保真**：已翻译元素的数字词元与原文一致；书写形式换算（如 `1.2 billion` → `12 亿`、`Oct 2023` → `2023 年 10 月`、`Top-10` → `排名前十`）经 `--numerals whitelist.json` 放行。
3. **拼接一致**：每个元素的 `parts` 拼接与译文去空白比对完全一致。

## 7b. 渲染 QA（交付前必做）

```bash
# Windows（Word COM，同时做 Word 原生 schema 校验；注意传绝对路径）
pwsh -File scripts/render_pdf.ps1 -Docx output.docx -Pdf output.pdf
# Linux / macOS 无 Office 时回退 LibreOffice
libreoffice --headless --convert-to pdf output.docx

python scripts/render_qa.py output.pdf input-src.pdf --cjk-scan --toc-check --montage sheets
```

逐张目检生成的 3×4 缩略图拼图（文本级 QA 看不出排版溢出、空白页或目录错页）。

## 7c. 图内文字说明（可选）

嵌入式栅格图片中的文字不自动回写：PPTX 已在 Step 1 由 `ocr_slides.py`（百度 AI Studio `PaddleOCR-VL-1.6`）登记为译者语境；复杂 PDF/扫描件如需完整版面识别请配合 `paddleocr-doc-parsing` skill。交付时向用户说明含大量文字的图片保持原语言。

---

## CJK→EN 版式本地化清单（中译英专用）

中→英翻译在写回与 QA 之间追加本地化处理（详见 `references/cjk-en-localization-pitfalls.md`）：

1. 字体 / 编号 / 字距 / 窄列对齐 / 域开关：`scripts/localize_cjk_en.py fonts|numbering|tracking|justify|fields`
2. 分页修复与目录页码回写：`scripts/paginate_plan.py` → `scripts/render_pdf.ps1` → `scripts/toc_pages.py`
3. 跨块一致性核对：`scripts/reconcile_consistency.py`（`exit 1` 时先统一用词再写回）
4. 全套 7b 渲染 QA 并目检全部缩略图。

---

## 常见故障排查

| 现象 | 常见原因 | 处理方式 |
|---|---|---|
| `parts length != runs` | 译文删改了 `<!--key:...-->` 或手动改坏了 splits | 保留原标记行重跑 `merge_v3.py`，或核对 `run_splits.json` |
| 译文语域错位 / 缩写误译 / 术语不统一 | 跳过 `01-context.md` 或未跨块统一 | 严格执行 Step 2 全文理解与规格确认 + 跨组统一 |
| 翻译腔或标题被切碎 | 译者迁就 run 数量或孤立翻折行标题 | 译者先出自然整句，run 切分交给审校与 `merge_v3.py` |
| 页眉/页脚/日期回退中文 | 首页/偶数页变体或域开关残留 `yyyy年M月d日` | 走 `write_v3.py`（覆盖全 story）+ `localize_cjk_en.py fields` |
| 英文全文渲染成宋体 | 源文档将 `w:ascii/hAnsi` 设为中文字体 | 运行 `localize_cjk_en.py fonts`（见 `cjk-en-localization-pitfalls.md` §2） |
| 项目符号变成乱码 | 批量替换了 Wingdings PUA 符号 | 仅修改已核实的 `abstractNum`（见 pitfalls §3） |
| 出现多余空白页 / 目录页码错位 | CJK 流式空段或双分页符 | 跑 `paginate_plan.py --repair` 与 `toc_pages.py`（纯图页不算空白页） |
| EN→CJK 被 CJK 残留门误拦 | 未告知目标语言含中文 | `verify_structure.py` 加 `--expect-cjk` |
| 中英混排文档消耗多余 token | 含大量无需翻译的纯英文块 | 分块前过滤纯目标语言块（缺 key 在合并时自动保留原文） |
| 修改脚本后防回归 | 缺少基线验证 | 运行 `python scripts/selftest.py ./selftest_run`（24 项全过） |
