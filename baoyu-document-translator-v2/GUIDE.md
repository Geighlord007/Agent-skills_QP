# 一页纸说明 — baoyu-document-translator-v2（v2.2.2）

## 这个 skill 干什么

把 DOCX / PPTX 翻译成目标语言，**尽量不动原排版**（字体、表格、页眉页脚、编号、图片都保留）。

## 日常只需要这三步

```bash
# 1) 提取（把文档里的文字抽出来，带上稳定编号）
python scripts/extract_docx_v2.py input.docx extracted.json
python scripts/json_to_markdown_v2.py extracted.json source.md

# 2) 翻译 source.md（大文档用 chunk_keyed.py 分块并行翻；产出 translation.md）
#    注意：翻译时必须原样保留每行的 <!--key:...--> 标记

# 3) 合并 + 写回
python scripts/merge_keyed_structure_aware.py extracted.json translation.md translated.json
python scripts/write_docx_surgical.py input.docx output.docx translated.json
```

## 写回引擎怎么选（按环境自动判断）

```bash
python scripts/engine_select.py     # 打印 {"recommended": "wir" | "surgical"}
```

| 环境 | 用哪个 | 为什么 |
|---|---|---|
| **Linux / WSL2** | **WIR**（`write_docx_wir.py`） | 第三方写好的编译引擎，只改文字节点，保真最省事。**首选** |
| **原生 Windows / macOS** | **surgical**（`write_docx_surgical.py`） | 同一思路的纯 Python 实现，全平台可跑、出问题能当场改 |

> WIR 只有 Linux 版编译产物（无源码），所以原生 Windows 加载不了。
> 想在 Windows 上用 WIR：装 WSL2 后直接跑现成那份。

## 文件清单：哪些必需、哪些可选

**必需（三步会用到）**
- `extract_docx_v2.py` — 提取（正文/表格/页眉页脚/脚注/文本框/内容控件）
- `json_to_markdown_v2.py` — 转成可翻译文本
- `chunk_keyed.py` — 大文档分块（可选，但长文档建议用）
- `merge_keyed_structure_aware.py` — 把译文合回结构
- `write_docx_surgical.py` / `write_docx_wir.py` — 写回
- `engine_select.py` — 判断该用哪个写回引擎

**可选质检包（默认不跑，出问题时再用）**
- `verify_structure.py` — 体检：结构有没有丢、译文有没有真的写进去（exit 1 = 别交付）
- `render_pdf.ps1` + `render_qa.py` — 转 PDF 查：空白页 / 残留源语言 / 目录页码
- `localize_cjk_en.py` — 中→英版式本地化（字体、编号、字距、对齐、域开关）
- `paginate_plan.py` — 分页预 pass（标题另起页、清理空段）
- `toc_pages.py` — 按实际页回写目录页码
- `reconcile_consistency.py` — 目录 ↔ 标题 ↔ 图注一致性核对
- `selftest.py` — 脚本自身回归测试（23 项）

**参考文档（按需查）**
- `references/cjk-en-localization-pitfalls.md` — 中→英踩坑清单
- `references/subagent-prompt-template.md` — 分块翻译给子代理的提示词模板
- `references/schema-v2.md` — 中间 JSON 的字段说明
- `references/wir-integration.md` — WIR 引擎接入说明

## 翻 Excel（XLSX）怎么办

xlsx 和 docx 一样是"zip + XML"，但文字集中放在**共享字符串表**里，所以只要改这一处：

```bash
# 1) 先看清有哪些文字（sharedStrings 与表名）
python scripts/xlsx_translate.py <src.xlsx> <tmp.xlsx> <map.json>   # 会打印 before/after 的中文残留
# map.json: {"strings": {"中文A": "English A", ...}, "sheet_names": {"中文表名": "Sheet Name"}}

# 2) 用真实译文生成输出
python scripts/xlsx_translate.py 原件.xlsx 输出-EN.xlsx map.json
```

- 只改文字：**样式、数字格式、列宽行高、图表、图片、公式全部不动**。
- 两个坑（脚本已在注释里写明）：Excel **表名上限 31 字符**；表名里的 `&` 要写成 `&amp;`。
- **图片里的文字改不了**（像素），交付时要单独告知客户。

## 三句话记住怎么用

1. 三步：**提取 → 翻译 → 写回**。
2. 环境：**Linux/WSL2 用 WIR，Windows 用 surgical**（一个小命令就能问出来）。
3. 交付前想稳一点：跑一次 `verify_structure.py`；其余检查按需。

## 留痕/审阅版（可选，需要 Node）

如果客户要"在 Word 里看到改了哪、能逐条接受/拒绝"，可以用第三方的 Safe Docx 出**留痕版**
（Word 原生修订痕迹，一次产出干净版 + 留痕版）：

- 安装：`npm install -g @usejunior/safe-docx@0.19.1`（免费 Apache-2.0，纯本地运行）
- 实测：可写回约 **92%** 的段落并产出留痕版；**跨域结果（页码/SEQ/REF）的段落它不支持**，
  这类段落仍用本 skill 的 surgical 写回
- 完整实测数据与组合方案：`references/safe-docx-evaluation.md`

## 已知限制（简短）

- WIR 引擎：原生 Windows 不可用（无源码、只有 Linux 版）；无修订痕迹/批注能力。
- surgical：批注、公式、内容控件内部的复杂结构不保证；艺术封面类的极端排版可能仍需人工看一眼。
- 图片里的文字不会自动翻译（图片是图片）。
