# 报告设计语言 PAPER-INK EDITORIAL v1.0（纸墨编辑体）

> **本文件是 synbio-weekly 技能包内置的完整设计规范，可独立使用。** 原作者另有跨行业母本存于其本地项目目录（不随包分发）；两者并存时修改须同步。
> **定位**：所有 AI 生成报告/周报/简报的统一设计标准——换行业、换关键词，视觉标准不变。
> **血统**：tokens 与图表语法取自 nice-baogao `styles/synbio-editorial`（生物风格，雕版技术感）；反 AI 套路原则取自 Geighlord007/frontend-slides（Anti-AI-Slop）；图表工作流取自 Lieflat Charts（数据契约先行、真实单位做视觉原子、每图一个结论）；生图风格 Skill 化取自《4 个视觉 Skill｜130 种 AI 图片风格大赏》（固定风格预设 + 主题编译提示词）。
> **原则**：写数字，不写形容词。本文出现的每个数值都是可执行的规范。

---

## 1. 设计意图

一份报告的可信度一半来自内容，一半来自它长什么样。本规范要的气质是**印刷品**——科学画册、财经周报、雕版技术插图——而不是"AI 生成感"。以下特征合起来就是 AI 味，逐条禁用：

- 白底 + 蓝紫渐变 + 圆角卡片 + 投影发光（frontend-slides 原话：bye-bye, purple gradients on white）
- 粗体标题、emoji 当图标、彩色胶囊标签满天飞
- 配色随意（默认 matplotlib 色环）、刻度含糊、装饰性图表堆砌（Lieflat 批评的三大老毛病）
- 每个栏目一个颜色的"彩虹式"分类

**身份来自克制**：纸色底、纯墨字、发丝线、一种语义强调色、衬线斜体承载批注。字重只用 400——没有粗体可用，强调只能靠 字号 → 留白 → 一个强调色 → 斜体（顺序即优先级）。

## 2. 色彩 Tokens（取自 synbio-editorial，hex 一律照抄，不得另调）

### 2.1 纸与墨

| Token | Hex | 用途 |
|---|---|---|
| `PAPER` | `#F7F5EB` | 页面底色（本规范唯一画布） |
| `BONE` | `#EDEADB` | 次级面板、表头带、KPI 带 |
| `INK` | `#000000` | 正文与线条 |
| `INK_2` | `#3A3A38` | 长正文（纯黑太硬时） |
| `INK_MUTED` | `#6B6B66` | 图注、来源行、元数据、译文 |
| `RULE` | `#000000` | 发丝线（1px，标题线用 0.55 透明度） |
| `RULE_SOFT` | `#D8D3C4` | 浅网格线、行分隔线 |

### 2.2 语义强调色（按含义分配，不按审美）

| Token | Hex | 语义 |
|---|---|---|
| `MOSS` | `#9EA617` | natural / 可获得、已披露 |
| `MEADOW` | `#617D24` | 数据系列 / 正向、达成值 |
| `CLAY` | `#E05E3D` | engineered（工程化）/ 图的主角 / 最大值 / 阈值 |
| `ROSE` | `#C28775` | 时间与过程（时间轴、引线）/ 证据 |
| `SEED_BROWN` | `#D1B594` | 中性 / 低强调 / 背景带 / 次要系列 |

财务子色板（金额、融资场景用）：`JPM_INK #0B2A4A` 主系列、`JPM_BRONZE #8F5A39` 强调项（**"棕=唯一重要的那个"**）、`JPM_SKY #A6D7F0` 次系列、`JPM_SLATE #5A6470` 坐标与注释。

**规则**：
1. 同一语义类只用一个色相；两个色相必须属不同语义类（主角 vs 背景）。
2. **一图一主角**：条形图恰好一根用 `CLAY`（或 `JPM_BRONZE`）高亮——编辑判断"最重要的那根"，其余用 `MEADOW`/`INK`。
3. 色盲安全：文字用色仅限 `MOSS/MEADOW/CLAY`；`CLAY` 上纸面对比 ≈3.6:1，只用于大字。
4. 信号档颜色映射（固定）：`KEY/重点 = CLAY`、`WATCH/关注 = MEADOW`、`BRIEF/简讯 = INK_MUTED`、`WATCHLIST 命中 = JPM_BRONZE`。

## 3. 字体与字阶

### 3.1 四个字体槽（CSS font-family 栈照抄；拉丁与中文按槽独立回退）

```
--font-serif: "Newsreader","Georgia","Times New Roman","Songti SC","SimSun",serif;        ← 标题/正文/斜体批注
--font-sans:  "Schibsted Grotesk","Segoe UI","Helvetica Neue","PingFang SC","Microsoft YaHei",sans-serif;  ← 栏目名/条目claim/字段正文
--font-mono:  "DM Mono","Consolas","SFMono-Regular",monospace;                            ← 数字/kicker/微标签/来源行
```

**三款拉丁面随技能包 `assets/fonts/` 分发**（latin 子集 woff2，SIL OFL，授权见同目录 OFL.txt），生成 HTML 时内联为 data URI——跨机渲染一致。CJK 面继续走系统回退栈（Songti SC/SimSun/PingFang SC/Microsoft YaHei），不内嵌。

### 3.2 用法（face-per-element，照 synbio-editorial C8.2）

- **mono 专管**：所有数字、金额、日期、编号（GRN 等）、kicker、微标签、来源行、表头、图表刻度与数值标签
- **sans 专管**：栏目标题、条目 claim 行、字段正文、导航
- **serif 专管**：大标题、正文叙述、斜体批注（deck line / 图注 / 方法注）
- **斜体 = 语义槽，不是强调**：英文 one-liner、译文、方法注、结论句用 serif italic

### 3.3 字阶（web px，正文 15px 为基准；只用 400 字重）

| 角色 | px | 字体 | 备注 |
|---|---|---|---|
| 大标题 display | 34 | serif | tracking −0.01em |
| 栏目标题 h2 | 22 | serif | |
| 条目 claim | 16 | sans | |
| 字段正文 body | 14.5 | sans，行高 1.75 | |
| 正文叙述 body-serif | 15 | serif，行高 1.8 | 深度展开用 |
| 英文 deck/译文 | 13 | serif italic，`INK_MUTED` | 比所属元素小一号 |
| kicker / 微标签 | 11.5 | mono uppercase，tracking +0.14em | `INK_MUTED` |
| 数字 KPI | 30 | mono | |
| 来源行 | 12 | mono，`INK_MUTED` | |
| 图注 | 13 | serif italic，`INK_MUTED` | |

**强调阶梯**（无粗体系统）：① 加大字号 ② 加留白 ③ 用一个语义色 ④ 斜体。同一元素最多用两级。

## 4. 版面与家具（furniture）

内容列宽 **780px**，页边距 ≥ 24px，行宽约 66–70 字符。全局 `border-radius: 0`。

**页面头**（顺序固定）：
```
[kicker]   mono uppercase letterspaced —— 路径不是标签：SYNBIO WEEKLY · ISSUE 01 · 2026-W39
[title]    serif 34px 中文主标题（主语言）
[subtitle] serif italic 15px INK_MUTED —— 英文标题（译文，小一号灰）
[rule]     1px INK @0.55 透明度，通栏
[deck]     serif italic —— 本期一句话结论（takeaway）
```

**栏目头**：`01 · FUNDING & CAPITAL` kicker + serif 中文栏目名 + 灰色英文名 + 通栏发丝线。

**页脚**（顺序固定）：
```
1  serif italic 方法/口径注（可多段，首词可用 VERIFIED:/ESTIMATED:/UNVERIFIED:）
2  mono 来源行：Source: <来源>, <细节> · Retrieved YYYY-MM-DD
3  mono 状态行：全大写关键词 + 冒号 + 句子（可选）
```

**来源行是强制项**——没有来源行的图/表/条目是缺陷不是风格。日期一律 ISO。

## 5. 双语规则（引自 synbio-editorial C17.6，扩展到网页）

1. **堆叠不混排**：主语言一行（黑、该元素主字体），译文紧随其下一行（灰 `INK_MUTED`、小一号、serif italic）。一行之内绝不中英夹杂成句。
2. 主语言 = 文档语言（中文）；译文永远从属。
3. **成对范围**：大标题、栏目名、条目 claim、图表标题、KPI 标签、信号档标签——这些导航与结论元素必须成对；深度正文（PROFILE/TECH/TERMS/WHY）以中文展开，专名（公司/物质/技术名）保留英文原名；另设一块 **ENGLISH ABSTRACT**（3–5 句英文全刊摘要）供只读英文的读者。
4. 数字、金额、编号两种语言共用同一 mono 写法，不翻译单位。

## 6. 图表语法

### 6.1 图表目录（报告固定四种，不新增形态）

| 形态 | 用途 | 构造 |
|---|---|---|
| **横条图（Glance 档）** | 金额、数量对比 | 粗条（28px），降序排列，值标签 mono 打在条右；一根 `CLAY` 高亮=主角；无坐标轴框 |
| **分布条形** | 构成/分类计数 | 同上但条更细（18px），分类标签右对齐 mono |
| **时间轴** | 事件流 | 一条 `INK` 横线即轴，`ROSE` 实心点标事件，标签上下交错，mono 日期 |
| **表格** | GRAS/多字段清单 | 仅横向发丝线（表头下 0.9 权重、行线 0.45），无竖线无斑马纹；表头 `BONE` 带 + mono uppercase |

### 6.2 通则（Lieflat + synbio-editorial 合并）

- **每图一个结论**：图表标题写结论不写变量名（"Moonwalk 领衔，本期披露融资 ≈US$155M"，不是"融资金额"）。
- **真实单位做视觉原子**：一格=一个百分点、一条=一百万美元；不造装饰性密度。
- 平涂实色，无渐变/阴影/立体/圆角；alpha 梯队只用 0.14/0.16/0.22/0.28/0.35/0.55/0.75/0.85。
- 值标签直接印在图元旁（mono），此时不需要坐标刻度；轴标题永不写"value"，写单位和口径（`USD m, disclosed rounds`）。
- 网格线仅当读者需要读值时出现：`RULE_SOFT`，0.5px，垂直于值轴。
- 不确定性写成文字区间（`40-45 °C`、`金额未披露`），不画误差棒；口径存疑用 `ESTIMATED` 标签。
- 空栏目写"本期无"，不放装饰图。

## 7. 条目结构（信息类报告的基本单元）

```
[chip 行]   信号档方形标签：KEY · 重点 / WATCH · 关注 / BRIEF · 简讯 ；WATCHLIST 命中追加 MARK 标签（棕）
[claim]     sans 16px 中文事实句（公司名 + 事实 + 关键数字）
[deck]      serif italic 13px 英文 one-liner（完整英文事实句）
[fields]    mono 微标签 + sans/serif 正文：
            PROFILE · 公司是谁（成立地/背景/阶段一句话起）
            TECH    · 技术是什么（外行能懂的解释）
            TERMS   · 交易/条款细节（金额/轮次/投资方/用途/合作条款）
            WHY     · 为什么重要（仅 KEY 档）
[source]    Source: <站名> · Retrieved YYYY-MM-DD（+ 链接）
```

盒子用 **左强调条**（synbio-editorial C15.1 的招牌器件）：1px `INK` 发丝边框 + 左内缘 3px 语义色竖条，零圆角。多源同事件合并为一条，其余列"另见"。

**深度红线**：融资/合作条目缺 PROFILE/TECH/TERMS 任意一项即不合格——"某公司完成融资"一句话带过是被明令退回的旧病。

## 8. 生图规范（豆包 Seedream，风格 Skill 化）

1. **风格锚**（固定前缀，任何主题都不改）：`engraved technical illustration, scientific plate style, warm ivory paper ground (#F7F5EB), fine ink hairlines, muted moss-green and clay-terracotta accents, flat restrained editorial composition, no gradients, no shadows, no 3D, no text, no letters, no logos, no watermark`。
2. **提示词编译** = 风格锚 + 主题物（本期意象：发酵罐/菌落/分子结构/工厂轮廓）+ 构图（宽幅 banner、留白、居中偏左主体）。每期换主题物不换风格——同系列报告的封面放在一起像一套丛书。
3. **用量**：每期封面 1 张（宽幅 1512×648）；栏目插图最多 2 张且仅当栏目 ≥3 条目。禁止生成真人面孔、真实公司 logo、可识别品牌元素。
4. 生成文件存 `briefings/assets/`，HTML 内联（base64）保持单文件可转发；图下配 serif italic 图注一行（英文，说明是 AI 生成插图）。

## 9. 可信度标注（引自 synbio-editorial C5）

`VERIFIED`（有出处核实）/ `ESTIMATED`（换算或推断）/ `UNVERIFIED`（信源单一或口径存疑）——mono uppercase letterspaced，永不单独用颜色表意，贴在被限定的内容旁。金额换算必须标注口径（如 `SEK 75M（Dealroom 折 US$9.07M）`）。

## 10. 禁用清单（每条都曾是真实缺陷）

渐变 · 投影 · 发光 · 斜角 · **圆角（border-radius 一律 0）** · **粗体（700+）** · 3D · 饼图与环形图加光泽 · emoji 当图标/当标签 · 蓝紫渐变 AI 默认配色 · matplotlib 默认色环 · 彩虹式栏目配色 · 表格竖线与斑马纹 · 正文字距 · 居中正文段 · 无结论装饰图 · 无来源行的图表/条目 · 一行内中英混排成句 · 一页内两个不同风格的图。

## 11. 变更管理

- 本规范跨行业复用：换行业只换内容与主题物意象，**tokens、字阶、家具、图表语法、双语规则一字不改**。
- 任何偏离记录到该报告的生成说明里（哪一条、为什么）；累计偏离 ≥3 条时升版本修订规范，而不是让报告继续漂移。
- 参考资产：nice-baogao `styles/synbio-editorial/STYLE.md`（tokens/图表/禁用清单原文）、frontend-slides（Anti-AI-Slop 宣言与编辑体模板谱系）、Lieflat Charts（图表三档风格与整页双语模板工作流）、wibi-style/Phil-design-skills 等生图风格 Skill 包（风格预设组织方式）。

*v1.0 · 2026-09-24 固化。维护：改规范先改母本，再同步本副本。*
