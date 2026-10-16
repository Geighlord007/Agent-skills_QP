# synbio-weekly · 合成生物行业周简报生成技能

一个自包含的 Agent Skill（SKILL.md 标准格式）：每周自动生成**中英双语**的合成生物行业简报——国外公司的融资 / 商业化 / 技术信号 / 法规动态（FDA GRAS 周申报为核心板块），Markdown + 单文件 HTML 双产出，PAPER-INK 编辑体设计，可配 AI 封面图。

> A self-contained Agent Skill that generates a bilingual weekly briefing on the synthetic biology industry — funding, commercialisation, technology signals and FDA GRAS filings — as Markdown + a single-file HTML with a fixed editorial design language.

## 特点

- **GRAS 周申报跟踪**：FDA GRAS Notice Inventory 官方库，GRN 号增量差集法识别每周新申报 + "no questions" 回函跟踪（明细页不显示 filing date，此法最稳）
- **融资稀疏的行业有解**：行业媒体 + PR 通稿社关键词监控 + 结构化融资库三路补位，10 天滚动窗口 + 跨期去重
- **深度条目**：融资/合作强制 PROFILE（公司是谁）/ TECH（技术是什么）/ TERMS（条款细节），拒绝一句话带过
- **中英双语**：导航与结论元素中英成对 + ENGLISH ABSTRACT，深度正文中文展开、专名保留英文
- **固定设计语言**（PAPER-INK EDITORIAL v1.0）：纸墨编辑体、语义强调色、每图一个结论、来源行强制——换行业/关键词只换内容不换视觉
- **打包字体，跨机渲染一致**：Newsreader / Schibsted Grotesk / DM Mono（SIL OFL）随包分发并内联进 HTML；CJK 走系统字体栈
- **AI 封面图**：豆包 Seedream（火山方舟 Ark API），风格锚固定保证同系列封面成套

## 安装

把本目录放到技能搜索路径之一即可：

```
~/.agents/skills/synbio-weekly/     # 用户级（推荐，任何项目可用）
<project>/.agents/skills/synbio-weekly/   # 或项目级
```

## 快速开始

1. **建工作区**（运行数据与产出的目录，任意位置）：
   ```
   my-briefing/
   ├── config.json      ← 从 assets/config.defaults.json 复制
   └── (首次运行自动建 data/、briefings/、research/)
   ```
2. 在 `config.json` 里配置生图密钥（`image_gen.api_key`，或用环境变量 `ARK_API_KEY`；不用图可 `image_gen.enabled: false`）。
3. 对 Agent 说「生成本周合成生物周简报」，或直接运行技能。

定时运行（以 cron 为例，prompt 与 SKILL.md 末节的「标准调用」保持一致）：

```
使用 synbio-weekly 技能生成本期《合成生物行业周简报》。工作区：<你的工作区路径>。
严格按该技能 SKILL.md 的十步流程执行……本任务从技能出发执行，不依赖任何会话上下文。
```

## 自定义（都只改工作区 config.json）

| 想做什么 | 改哪里 |
|---|---|
| 加/减信息源 | `sources[]`（`enabled` 一行开关；EXA 语义检索，无需 RSS） |
| 关键词 | `keywords`：召回词 + `blacklist` + `boost_terms`（升档） |
| 盯特定公司 | `watchlist_companies[]`（命中打 WATCHLIST 标签） |
| 法规线 | `regulatory.gras / fda_other / eu_uk / apac` 各自开关 |
| 回溯天数 | `_meta.window_days`（默认 10 天滚动 + 去重） |
| 条目深度 | `depth_rules` |

## 包结构

```
synbio-weekly/
├── SKILL.md               # 流程契约：十步 + 质量红线 + 故障降级 + 定时任务标准调用
├── assets/
│   ├── design-language.md # PAPER-INK EDITORIAL v1.0 设计契约（色彩/字阶/图表/双语/禁用清单）
│   ├── fonts/             # 打包字体 woff2（Newsreader/Schibsted Grotesk/DM Mono，SIL OFL）
│   ├── config.defaults.json  # 配置默认值（信息源/关键词/法规线/生图，无密钥）
│   ├── briefing.md.tpl    # MD 模板
│   └── briefing.html.tpl  # HTML 模板
└── scripts/
    ├── gen-image.mjs      # 豆包 Seedream 生图（Node 18+，零依赖）
    └── embed-images.mjs   # 封面 base64 内联，单文件可转发
```

## 前置条件与依赖

- Node.js 18+（脚本零第三方依赖）
- [exa-search](https://exa.ai) 技能 + `EXA_API_KEY`（新闻检索，必需）
- `ARK_API_KEY`（豆包 Seedream 生图，可选；不用图可 `image_gen.enabled: false`）

自由使用与修改（MIT）。设计语言母本与同步规则见 `assets/design-language.md` 头部注记。
