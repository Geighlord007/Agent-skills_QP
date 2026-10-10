# 版本优化记录 — Document Translator

每个版本的优化要点与取回方式。取回单个文件：`git show <标签>:baoyu-document-translator-<版本>/SKILL.md`；
看整个版本的文件夹：GitHub 标签页 `https://github.com/Geighlord007/Agent-skills_QP/tree/<标签>`。
详细条目见各版本文件夹内的 `CHANGELOG.md`。

## v2.2.2（提交 1df41f1，2026-09-22）

- XLSX 支持（只重写共享字符串与表名，格式零风险）
- keyed markdown 往返：每个元素带稳定 key，回填与段落顺序无关
- DOCX 全部 story 提取（页眉页脚三种、脚注、文本框、修订）、PPTX 表格单元格完整往返
- w:t 级写回（surgical / WIR 双引擎）、结构化合并、阻断门与渲染 QA

## v3（标签 `v3`，提交 97fe399）

- 合一管线：`extract_v3.py` / `merge_v3.py` / `write_v3.py` / `qa_v3.py` 四个入口按扩展名分发
- 合并与 run 切分一步完成，不再产生中间产物
- 单一阻断质检入口：回抽比对（文本、run 数量、分段、逐 run 格式签名）、数字保真白名单、拼接一致
- 翻译前置产物 `01-context.md`（全文理解）与翻译规格单（用户确认）

## v3.5（标签 `v3.5`）

- 子代理效率纪律：工具回合上限（翻译 4 / 审校 8 / 抽查 6），机械核对统一交 `qa_v3.py`
- 审校流水线触发，直出修订与 run 切分；逐页抽查与写回重叠
- `page_compare.py` 逐页中英对照视图；`subagent-prompt-template.md` v2.5 三角色
- 实测：V7 运行约 12 分钟、约 486 万 token

## v3.6（标签 `v3.6`，现与 v4.2 并存于仓库）

- 文档分层：SKILL.md 缩为流程骨架（140 行），明细按格式与职能移入 references/
- `docx.md` / `pptx.md` 按格式分开，任务是哪种格式只读哪种
- 触发式 description、能力范围对照表入 CHANGELOG

## v4.0（标签 `v4`）

- PPTX 整页视觉流水线：译者随任务书读入渲染页面图，翻译与长度取舍当场完成
- `render_slides.py`（PowerPoint COM 逐页导出）、`ocr_slides.py`（图内文字登记，保留带位置原始 JSONL）
- `slide_bundles.py` / `build_dispatch.py` / `apply_patches.py`：按页分组、任务书直发、补丁落稿
- 独立审校补丁直出、终稿渲染视觉核对（渲染层问题当场可见）

## v4.1（标签 `v4.1`）

- `api_call.py`：任务书 → MiMo 接口（`mimo-v2.6-pro`，同一模型）→ 产出文件，四角色全部接口化
- 网络重试、输出清洗（工具调用片段、markdown 强调符、汇报文字）
- token 计费只剩载荷与产出：实测整链约 35 万（对照子代理路线 486 万），几十万量级达成

## v4.2（标签 `v4.2`，当前版本）

- 切分范围收窄：审校只对含强调或分段的多 run 元素出精确切分，其余交自动切分（审校输出降六到七成）
- 合并内核加固：切分守恒兜底（丢失文本时整段放入首个文本 run 并告警）、切分边界不切数值词元
- 强调判定纳入同元素内字号差异（仅字号突出的元素回到精确切分范围）
- 验证：selftest 24 项通过；强制全量自动切分下合并 → 写回 → qa_v3 全部通过

## v1（已删除）

旧 `python-docx` 路线（`run.text =` 写回会丢域与分页），2026-09-23 移除，见 `DEPRECATIONS.md`；
用 `git log --diff-filter=D --name-only -- baoyu-document-translator` 定位删除提交。
