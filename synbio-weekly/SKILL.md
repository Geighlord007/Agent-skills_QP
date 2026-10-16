---
name: synbio-weekly
description: 生成《合成生物行业周简报》——国外合成生物公司的融资、商业化、技术信号与法规动态（FDA GRAS 周申报为核心板块），中英双语、PAPER-INK 编辑体设计、可配封面生图，产出 Markdown + 单文件 HTML 并维护跨期去重状态。Use when 用户要生成、更新、重跑合成生物行业周简报/行业周报/weekly briefing，要汇总本周 GRAS 申报/GRAS 新动态，或定时任务「每周一早8点合成生物行业周简报」被触发，或说"本周合成生物简报""跑一下周报"。
---

# synbio-weekly：合成生物行业周简报

自包含技能包：运行所需的一切都在本目录（`assets/`、`scripts/`），运行时只读写一个**工作区**目录。不依赖任何会话历史——单凭本文件即可完整出刊。

**前置条件**：Node.js 18+；exa-search 技能（需 `EXA_API_KEY`）；可选 `ARK_API_KEY`（生图，不用图可关）。

## 工作区标准布局（技能负责建立与维护）

工作区 = 调用时由调用方指定的目录（写在调用语句/定时任务 prompt 里；原作者项目示例为 `<用户文档目录>\每周报告\synbio`）。首次运行按下表建目录：

```
<workspace>/
├── config.json          # 由 assets/config.defaults.json 复制生成；用户个性化（含 api_key）只写这里
├── data/state.json      # 跨期去重记录（自动维护）：seen_urls / seen_grns / seen_grn_letters / last_issue
├── briefings/           # 每期产出：YYYY-MM-DD.md + YYYY-MM-DD.html（单文件，封面已内联）
├── briefings/assets/    # 封面图存档
└── research/            # 调研类产出，命名 YYYY-MM-DD-主题.md
```

## 技能包文件（相对本技能目录）

| 文件 | 用途 |
|---|---|
| `assets/design-language.md` | 设计契约（色彩/字阶/图表/双语/禁用清单）——视觉不合即返工 |
| `assets/fonts/` | 打包字体：Newsreader / Schibsted Grotesk / DM Mono（latin 子集 woff2，SIL OFL，见 OFL.txt）；embed 时内联进 HTML，跨机渲染一致 |
| `assets/config.defaults.json` | 配置默认值：信息源/关键词/watchlist/法规线/生图；缺 config.json 时复制到工作区 |
| `assets/briefing.md.tpl` · `assets/briefing.html.tpl` | 两版模板，占位符填写，结构与 class 不改 |
| `scripts/gen-image.mjs` | 生图：`node scripts/gen-image.mjs <workspace> "<主题意象>" [size] [outfile] [--raw]` |
| `scripts/embed-images.mjs` | 封面内联：`node scripts/embed-images.mjs <html文件>` |

## 流程（十步，按序执行）

1. **定位工作区**，读 `<workspace>/config.json` 与 `data/state.json`；缺 config 则从 `assets/config.defaults.json` 复制生成（api_key 留空时可用环境变量 `ARK_API_KEY`）。
2. **定窗口**：今天往前 `config._meta.window_days` 天（默认 10 天滚动。比一周长是故意的：行业新闻稀疏，7 天易出空窗；重复由去重兜底）。
3. **新闻发现**：用 exa-search 技能（Exa 引擎，用户指定）跑 `config.sources[]` 中每个 `enabled: true` 源的 `exa_queries`（时效类加 `--category news`）与 `urls` 列表页；再补一轮 watchlist 公司名 × funding/partnership/GRAS 通用查询。只保留窗口内且 `state.seen_urls` 未收录的条目（URL 归一化后比对）。
4. **深挖**：每个入选的融资/合作/重要技术条目补 1–2 次检索（官网/Dealroom/AgFunderNews/大学新闻页），凑齐 PROFILE（公司是谁）、TECH（技术是什么，外行能懂）、TERMS（金额/轮次/投资方/用途/条款）；简讯至少补一个从句说明公司业务。信息缺口标 ESTIMATED/UNVERIFIED，不编造。
5. **法规采集**（GRAS 核心）：按 `config.regulatory.gras.weekly_method`——抓 `db_list_url` 前 50 行 GRN 降序 → 与 `state.seen_grns` 差集 = 本期新申报（首期回溯 10 条作基线）；逐条抓 `detail_url_pattern` 拿物质/申请人/用途/状态；抓 `recent_letters_url` 提取 FDA "no questions" 回函。明细页不显示 filing date，勿编造日期。其余法规线按各自 `enabled` 处理。
6. **筛选与分档**：blacklist 丢弃；多源同事件合并（主链取最全，其余列「另见」）；boost_terms / watchlist 命中升档并加 WATCHLIST 标签。分档：**KEY/重点**=融资/基金关闭/监管申报或批准/大额合作/产能落地；**WATCH/关注**=中小合作/grant/技术验证；**BRIEF/简讯**=周边动态。金额换算 USD 标口径。
7. **写 MD**：按 `assets/briefing.md.tpl` 填占位符。条目 = 档位 + 中文事实句 + *英文 one-liner* + PROFILE/TECH/TERMS（KEY 加 WHY）+ 来源行 `Source: X · Retrieved YYYY-MM-DD`。
8. **写 HTML**：按 `assets/briefing.html.tpl` 并遵守 `assets/design-language.md`——零圆角、仅 400 字重、双语堆叠不混排、条目左强调条盒子（key=CLAY/watch=MEADOW/brief=SEED_BROWN）、图表一图一结论（.subj 高亮主角）、来源行强制。
9. **封面图**：`node scripts/gen-image.mjs <workspace> "<本期主题物意象>"`（风格锚自动前置）；失败一次则无封面出刊并在状态行注明。HTML 写完后先确认 `<html所在目录>/assets/fonts/` 存在（缺则从技能包 `assets/fonts/` 复制），再 `node scripts/embed-images.mjs <html>` 把封面与打包字体一并内联为 data URI。
10. **更新与汇报**：state.json 追加 seen_urls/seen_grns/seen_grn_letters、写 last_issue；汇报各板块条目数、KEY 条目 1–2 句、两个文件完整路径、空栏目与失败源（如有）。

## 质量红线（与设计合规同等刚性）

- 每条必有原文链接 + 日期 + 来源；无链接不收录；绝不虚构条目、金额或英文句；
- 融资/合作条目缺 PROFILE/TECH/TERMS 任意一项即不合格——"某公司完成融资"一句话带过是被退回的旧病；
- 空栏目如实写「本期无 / None this issue」；
- 圆角、粗体、渐变、emoji 图标、中英混排行、无结论装饰图、缺来源行 = 返工项。

## 故障处理

- 缺 exa-search 技能或 `EXA_API_KEY`：停下来告知用户安装与配置，不静默换引擎；
- Exa 429/5xx：等 10 秒重试一次，仍失败在汇报里注明（不换引擎，用户指定 Exa）；
- FDA 页面改版：从 `db_home_url` 重核字段/参数，更新工作区 config 并汇报；
- 某源抓取失败：板块照常出，页脚注明「XX 源本周抓取失败」；
- 生图失败：无封面出刊，状态行注明。

## 定时任务标准调用（模板；prompt 与下文仅差 `<工作区路径>` 一处替换）

> 使用 synbio-weekly 技能生成本期《合成生物行业周简报》。工作区：<工作区路径>。严格按该技能 SKILL.md 的十步流程执行（定位工作区读 config 与 state → 定窗口 → EXA 新闻发现 → 条目深挖 PROFILE/TECH/TERMS → GRAS 增量采集 → 筛选分档 → 写 MD → 写 HTML（遵守技能 assets/design-language.md）→ 生图嵌图 → 更新 state），完成后汇报各板块条目数、KEY 条目 1-2 句、产出文件完整路径、空栏目与失败源（如有）。本任务从技能出发执行，不依赖任何会话上下文。

创建定时任务时把 `<工作区路径>` 替换为实际目录写入 prompt；此后 prompt 与本模板不得单方面改动（改一处须改两处）。
