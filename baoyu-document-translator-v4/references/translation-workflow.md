# 翻译流程细则（Step 3）

工作产物（任务目录内，按生成顺序）：
01-context.md（全文理解，含缩写推断依据）→ 翻译规格单（用户确认）→ 02-prompt.md（共享上下文）
→ chunks/chunk-NN-draft.md（并行翻译）→ chunks/chunk-NN-splits.json（审校 + 修订 + 精确切分，直接产出）
→ pages/page-NN.txt（逐页抽查，直接修改草稿，与写回重叠）
→ translation.md + run_splits.json（主代理汇总）→ translated.json（merge_v3 一步产出，无中间件）

## 3.0 全文理解（`01-context.md`，阻断产物）

分块之前通读整份 `source.md`，写出 `01-context.md`，内容全部来自这份文档自身：

- **文档类型与各部分语域**：每个部分属于什么文体、面向什么读者（例如路演 PPT 的团队页按"职称、学位、机构、顾问、投资方"的排布习惯措辞；研发设施页按实验设施与工艺能力措辞）。
- **缩写清单**：逐个缩写给出语境推断与依据（例如 "PhD in Bioinformatics, BU; Msc, MIT" 中 BU 与 MIT 以学位授予机构并列，同一文档另有 Boston 与 MIT campus 语境，据此判定 BU = Boston University）。判定依据写在清单里；从全文判定不了的缩写列入待确认清单。
- **数字与金额写法倾向**：全文金额、数量级、日期的书写形式（例如金额用 $8M 形式还是 800 万美元），译文沿用同一形式。
- **强调排布规律**：斜体、加粗、颜色 run 通常承载哪类信息（关键词组、数字、成果）。
- **保留英文清单**：公司名、产品名、蛋白缩写、邮箱、模型名等约定保留英文的项。

## 3.1 翻译规格单（阻断式，需用户确认）

基于 `01-context.md` 汇总一份规格单交用户确认：术语表、缩写释义、语域、数字写法、保留英文清单。用户确认后才进入 3.2。用户修改的任何条目写回 `01-context.md`。

## 3.2 分块并行翻译

Run baoyu-translate refined mode on `source.md`, 或用 `chunk_keyed.py` 分块 + 并行子代理。共享上下文（`02-prompt.md`）必须引用 `01-context.md` 的术语表、缩写释义、语域与数字写法，**禁止只给译者孤立文本块**。区块文本之外附页面语境（该页主题、栏目含义）。

**全部区块一次派发**，禁止分批（分批会让后批的审校跟着串行等待）。每个翻译子代理
按 `subagent-prompt-template.md` Part 2 执行：每个文件只读一遍，只做语义自查，
机械核对（标记完整性、行数结构、数字词元、违禁字）不查，统一交 `qa_v3.py` 阻断把关。
译者只输出完整自然的句子；run 数量与格式边界不对译者暴露。

Important instruction to add to the translation prompt:

> Preserve every `<!--key:...|runs:N-->` marker exactly as-is. Do not delete, renumber, or move them. Place each marker immediately before the translated text block it belongs to. 译文以完整自然的目标语言句子为先，禁止为对上 run 数量而扭曲语序或截断词组。

## 3.3 独立审校 + 修订 + run 切分（并行子代理，流水线触发）

每个区块译完后**立即**交给未参与该块翻译的子代理审校——某块译完就派那块的审校，
不等整波翻译结束（后台派发，审校与后续翻译重叠进行）。
按 `subagent-prompt-template.md` Part 3 执行，工具回合上限 8 次。
审校只查语义与表达（语域贴合、缩写处理、保留英文清单、术语一致、数值改动、翻译腔与语义走样），
机械项不查。

审校子代理直接产出两份文件，主代理不再逐条修订：
- `chunks/chunk-NN-draft.md` — 发现问题直接改好覆盖（无问题不动）；
- `chunks/chunk-NN-splits.json` — 本块多 run 元素的精确 run 切分（强调短语对位、
  换行不跨段、数值词元完整、拼接与译文一致）。

主代理把各块 splits 合并成 `run_splits.json`，合并各块 draft 成 `translation.md`。

## 3.4 逐页抽查（并行子代理，与写回重叠）

全部审校完成后生成 `pages/page-NN.txt`（`page_compare.py`），按页分 3–4 路并行派发抽查
（模板 Part 4，工具回合上限 6 次）。抽查是第二双眼睛，**直接修入所属 chunk 草稿**并同步
该块切分，主代理只汇总。

抽查与合并、写回**同时进行**（合并写回只需 30 秒，抽查约 1.5 分钟）；
若抽查改动了译文，重新合并 + 写回 + 跑一次 qa_v3 即可，改动通常只涉及少量元素。

## 3.5 跨区块统一

主代理合并各区块后做全篇用词统一：同一概念在所有区块使用同一译法；同一缩写的展开形式一致；数字书写形式全篇一致。然后写出 `translation.md`。

## run 切分（审校阶段产出，合并时一步生效）

适用范围：`runs > 1` 且含强调（粗体/斜体/颜色）或换行（`a:br`）的元素。合并脚本按语言边界
自动切分只是初稿，精确切分由审校子代理产出（`chunks/chunk-NN-splits.json`），
主代理汇总成 `run_splits.json` 随合并一步生效。切分规则以 `subagent-prompt-template.md`
Part 3 为准（强调短语对位、换行不跨段、数值词元完整、拼接与译文逐字一致，合并时自动校验，
不一致即报错退出）。未覆盖的元素沿用合并脚本的自动切分。

## 合并的内部行为（merge_v3.py / merge_keyed_structure_aware.py）

1. Parses HTML comment markers to build a `key → translated text` map
2. Splits translated text into `parts` matching the original `runs` count
3. Warns if any key is missing or any run count cannot be matched
4. Preserves original `text` field for reference

结构化合并：空 run 保持为空、`\t`/`\n` 分隔 run 保留、文本只写入真实文本 run；
`run_splits.json` 的精确切分一步覆盖进最终 `translated.json`，不产生中间产物。
