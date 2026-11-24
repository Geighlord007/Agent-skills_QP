---
name: consulting-chart
description: 全仓唯一咨询级图表生成与知识库进化技能：输入页面简报与数据，先做恒等式勾稽与数据关系识别，再经内置轻量知识库检索配方卡（或生成视觉画册共创），自动路由三层出图引擎（Tier 1 zerox-thinkcell 55 种常规图与可编辑 PPTX/HTML、Tier 2 自研高频 SVG 母题、Tier 3 第 56+ 种约束积木合成 SVG），最后通过 Scale Law 6.5pt 算术护栏与视觉验收，并支持将新研报/满意成品图反哺入库。适用于 Word/PDF 静态出版级图表、PPT 可编辑图表、复杂财报/桥接/组合图及“这页该画什么图”的场景。
---

# consulting-chart（统一三层出图 + 内置读写知识库）

全仓唯一咨询制图入口（`< 10 MB` 自包含同步；`vendor/` 外部大仓库通过 `.gitignore` 留在本地，绝不污染 Git）。

## 标准 5 步流水线

```text
① 数据勾稽与关系识别 → ② kb.py 检索/翻画册 → ③ 三层出图(Tier 1/2/3) → ④ Scale Law ≥6.5pt + 视觉验收 → ⑤ 可选反哺入库
```

### Step 1 — 简报、数据勾稽与关系指纹（失败即停）

```bash
python scripts/validate.py --data <case>/data.json
```

**关键关系判据（划分 vs 顺序桥接）**：`129 - 95 = 34` 与 `95 + 34 = 129` 算术等价，唯一判据是**后列是否沿用母列的全部分类维度并逐项加总成立**（成立 → `partition` 浮空划分桥；否则 → `bridge` 顺序瀑布）。任一恒等式不成立立即报错停止，绝不强行绘图。

### Step 2 — 知识库介入（1C 双路径：常规静默检索 + 关键页翻画册）

内置热索引 `kb/recipes.jsonl` 覆盖 **Tier 1（zerox 61 例 / 55 图型）+ Tier 2（自研 31 高频 SVG 渲染器）+ Tier 3（麦肯锡/BCG/德勤/经济学人 20+ 签名技法母题）**：

```bash
# 路径 A（常规图，0.05 秒低 token 精准命中 Top 3 配方卡）：
python scripts/kb.py query --rel <partition|deviation|change-over-time|ranking|part-to-whole|correlation> --intent "<一句话结论>" --format <docx|pptx|html>

# 路径 B（关键页 / 第 56+ 种创新图：生成 3 格带编号视觉画册让用户选方向）：
python scripts/kb.py lookbook --ids <id1,id2,id3> --out work/lookbook.html
```

### Step 3 — 三层出图路由（解决 55 种图上限问题）

| 层级 | 触发条件 | 执行命令 / 机制 |
|---|---|---|
| **Tier 1 · 工业标准层** | 常规 55 种图型、Dashboard/Facet 拼版，或明确要 **可编辑 PPTX 形状 / 离线改字 HTML** | `python scripts/zerox_adapter.py advise\|validate\|render ...`（调度本机 `vendor/zerox-thinkcell` 或 `ZEROX_DIR`，不单独注册抢触发 Skill） |
| **Tier 2 · 高频母题层** | 命中内置 31 种自研咨询语法（TOM 浮空划分桥、财报三联、AI 三面板、预测折线等）且需静态出版级 SVG/PNG | `python scripts/pipeline.py --case <dir> [--skin house\|mckinsey\|bcg\|deloitte\|economist]` |
| **Tier 3 · 第 56+ 种约束积木合成** | 两者均未覆盖的长尾/创新组合图（**绝不硬塞错图型，也绝不先改引擎注册表**） | 1. 走 `kb.py lookbook` 选定参考骨架与皮肤；<br>2. 强制复用 `references/skins/*.json` + `scripts/chartlib.py`（Exhibit 骨架 + `tw()` 测宽）+ `scripts/annotations.py`（括线/圆标/胶囊/强调带 + 碰撞检测）；<br>3. 仅针对本页写 50–100 行一次性组装脚本产出 SVG，参考 `kb/notes/consulting-checklist.md` 10 条硬清单。 |

### Step 4 — 统一后置护栏（Scale Law 算术检查 + 渲染目检）

```bash
# 1. 上版字号算术护栏（Word A4 栏宽 456.69pt / PPT 720pt；底线 6.0pt，目标 ≥ 6.5pt）
python scripts/scale_law.py <out>/chart.svg --display-pt 456.69

# 2. Edge 无头渲染 PNG（支持中文路径）并做视觉自检（零重叠、零截断、配色合规）
python scripts/render_png.py <out>/chart.svg
```

### Step 5 — 2B 读写进化闭环（新研报 / 满意成品图反哺入库）

```bash
# 把新研报 PDF 截图或经济学人新图蒸馏进 kb/（裁 600px 缩略图 + 追加 recipes.jsonl）：
python scripts/kb.py ingest-image <chart.png> --id <slug> --title "<名>" --source "<出处>" --rel "<关系>" --intent "<关键词>" --signature "<一句话机理>"

# 把手调满意的 Tier-3 组装脚本反哺入库（use_count ≥ 3 时自动提示晋升为 Tier-2 注册渲染器）：
python scripts/kb.py harvest <script.py> <chart.png> --id <slug> --title "<名>"

# 查看知识库统计与待晋升候选：
python scripts/kb.py stats
```

## 外部参考仓库（Git 忽略，本地保留）

`vendor/` 下的外部参考仓库（EconomistStyle / chart-doctor / The-Python-Graph-Gallery）仅写进 `.gitignore`，本地原样保留不进 Git；新机器如需查阅可按 `vendor/VENDOR.md` 里的地址按需 `git clone --depth 1`。查看 Tier-1 后端是否就绪：

```bash
python scripts/zerox_adapter.py status
```

## 核心目录速览

- `kb/recipes.jsonl` — 热索引（86 KB，112 条配方，跨设备随 Git 同步）
- `kb/thumbnails/` & `kb/snippets/` & `kb/notes/consulting-checklist.md` — 样张缩略图、积木样例与 10 条质检清单
- `references/skins/` & `references/grammar-registry.json` — 咨询/经济学人皮肤令牌与 Tier-2 语法注册表
- `scripts/` — `kb.py`、`scale_law.py`、`zerox_adapter.py`、`pipeline.py`、`validate.py`、`chartlib.py`、`annotations.py`、`renderers*.py`、`render_png.py`
