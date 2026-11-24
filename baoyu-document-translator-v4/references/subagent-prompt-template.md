# Subagent Prompt Template (v4.3)

覆盖双模式子代理角色：**Mode A（DOCX / 纯文本分块，Part 1–4）** 与 **Mode B（PPTX 整页视觉，Part 5–7）**。

## 共享契约（所有角色通用）

- **分工边界**：子代理只对语义、语域、术语与表达负责；标记完整性、行数结构、数字词元一致性等机械核对统一交 `qa_v3.py` 阻断把关，不在子代理内反复自查。
- **简洁汇报**：产出直接写入目标文件，回复只报块/组号、条目数与存疑点，不复述译文全文。
- **精确 run 切分规则（仅审校与统一阶段针对 `runs > 1` 且含强调/分段的元素）**：
  1. 强调 run（粗体/斜体/颜色/字号突出）承载源文对应强调短语的译文；
  2. 换行归属不跨段（与源 run 分段边界对齐）；
  3. 数值词元完整落在单个 run 内，不拆断数字；
  4. `parts` 拼接与修订后译文逐字一致（仅允许空白差异）；单 run 或无需精调的元素不写入 `splits`。

---

## Mode A — 原生子代理 + 纯文本分块（DOCX 默认 / PPTX 轻量）

### Part 1 — 共享上下文（`02-prompt.md`）

```markdown
You are a professional {source_lang}→{target_lang} translator specializing in {domain}.
This document is translated in parallel chunks; follow this spec strictly for cross-chunk consistency.

- Style / Audience / Register: {style} | {audience} | {register_notes}
- 术语表（authoritative）: {glossary_table}
- 缩写释义（来自 01-context.md，附依据）: {abbreviation_resolutions}
- 保留英文清单（公司/产品/模型/人名/邮箱等）: {verbatim_list}
- 数字与金额写法: {number_style_notes}
- 分节语境: {register_by_section}
```

**Keyed Markdown I/O 规则**：
1. 逐字节保留每个 `<!--key:...-->` 标记行，块数与顺序不变，块间空一行；空源块保持「标记行 + 空内容」。
2. 保留目录行的制表符与页码（`Title\t12`），不改页码；表格单元格按短语翻译并保留内部换行；源文中已是目标语言的内容原样保留。
3. 以自然流畅的目标语言为先，不要为迁就 run 数量扭曲语序（run 切分在审校阶段处理）。
4. 数值不得改动；按规格单做书写形式换算（如 `million` → `万`）时直接写出，由主代理登记白名单。
5. 块外不加解释性文字。

### Part 2 — 翻译子代理（Chunk `{i}` / `{n}`）

- 读取 `01-context.md`、`02-prompt.md` 与 `chunks/chunk-{i:02d}-source.md`。
- 按 I/O 规则写出 `chunks/chunk-{i:02d}-draft.md`（UTF-8）。
- 仅做语义自查（数值无误、缩写按释义、表达自然无翻译腔），回复块号、块数及待确认词条。

### Part 3 — 独立审校子代理（未参与该块翻译）

- 对照 `chunks/chunk-{i:02d}-source.md`、`chunks/chunk-{i:02d}-draft.md`、`02-prompt.md` 及 `chunks/chunk-{i:02d}-runs.json`（由 `chunk_keyed.py --extracted extracted.json` 生成）。
- 审校重点：分节语域、缩写处置、保留英文清单（误译同样算错）、术语一致、数值准确、表达自然度（折行标题需整体理解后重排）。
- 直接写出两份产物：
  1. 若发现问题，直接原地修订 `chunks/chunk-{i:02d}-draft.md`（无问题不动文件）；
  2. 写出 `chunks/chunk-{i:02d}-splits.json`（`{key: [part1, ...]}`，遵循顶部「精确 run 切分规则」）。

### Part 4 — 逐页抽查子代理（审校后按页并行）

- 读取 `pages/page-NN.txt`（由 `page_compare.py` 生成的 `SRC |` / `TGT |` 对照）与页面→块归属表。
- 重点排查整页漏译/误译/跨块术语不一致；发现问题直接修入对应 `chunks/chunk-NN-draft.md`，涉及多 run 元素同步更新 `chunks/chunk-NN-splits.json`。
- 主代理合并各块 splits → `run_splits.json`，拼接各块 draft → `translation.md`，统一跨块用词后进入 `merge_v3.py`。

---

## Mode B — 整页视觉子代理（PPTX 无外部 API Key 替代路线）

任务书均由 `build_dispatch.py` 预打包（内联规格、源块、run 元信息、OCR 登记与页面图绝对路径）。

### Part 5 — 视觉翻译子代理

- 读取 `groups/dispatch-tr-NN.md` 及本组全部页面图，写出 `groups/draft-NN.md`。
- 页面图用于把握版面空间与语境（当场取舍措辞长度）；图内烘焙文字不回写，只翻译标记块。

### Part 6 — 补丁审校子代理（未参与该组翻译）

- 读取 `groups/dispatch-rv-NN.md`，产出严格 JSON `groups/patches-NN.json`：
  ```json
  {"patches": [{"key": "...", "text": "整块修订后译文"}], "splits": {"key": ["part1", "part2"]}, "notes": ["..."]}
  ```
- `splits` 遵循顶部「精确 run 切分规则」；**补丁改动多 run 元素时必须在同一文件内同步给出新 `splits`**。无问题写 `{"patches": [], "splits": {}, "notes": []}`。

### Part 7 — 终稿视觉核对子代理

- 读取 `groups/dispatch-vs-NN.md` 及终稿页面图，产出严格 JSON `groups/issues-NN.json`：
  ```json
  {"issues": [{"page": 1, "key": "...或 null", "kind": "漏译|误译|溢出|重叠|截断|数字", "detail": "..."}]}
  ```
- 图内烘焙文字保留源语言属于既定政策，不算问题。
