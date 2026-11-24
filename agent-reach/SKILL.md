---
name: agent-reach
description: >
  Multi-platform read-only content acquisition via OpenCLI, per-platform CLIs,
  MCP, and public APIs for specific platforms: 小红书/xhs, Twitter/X, B站/bilibili,
  Reddit, Facebook, Instagram, V2EX, LinkedIn, Boss直聘, YouTube, 小宇宙播客,
  雪球/股票行情, GitHub CLI, and RSS/Jina Reader.

  Use when the user explicitly targets one of these platforms, needs authenticated
  browser/CLI scraping (OpenCLI / CDP / cookies), or needs multi-platform social
  discussion lookup across these channels.

  NOT for: routine web search or general research better served by native search,
  `exa-search`, or `deep-research`; standalone audio/video transcription when
  `qwen-transcribe` is preferred; write operations
  (posting/commenting/liking); or downstream report writing/translation.
metadata:
  homepage: https://github.com/Panniantong/Agent-Reach
---

# Agent Reach — 多平台只读采集路由器

覆盖 16 个平台的只读内容获取（OpenCLI / 平台 CLI / MCP / 公开 API）。按需阅读对应 `references/*.md`，遇到命令失败按文档重试链排查，不盲猜参数。

## 运行原则

1. **按需体检**：多后端或需登录态的平台（小红书/Reddit/Twitter/Facebook/Instagram/Boss直聘）在首次不确定激活后端或命令报错时，运行 `agent-reach doctor --json` 查看 `active_backend`（`null` 表示未做实时 Cookie 探测，不代表不可用）。
2. **只读与认证边界**：不替用户代登录，不盲读浏览器全部 Cookie；OpenCLI 仅复用用户明确控制的 Chrome 会话。
3. **跨平台临时目录**：**不要在 agent workspace 创建临时文件**。临时输出放系统临时目录（Windows PowerShell 用 `$env:TEMP`，POSIX 用 `/tmp`），持久配置放 `~/.agent-reach/`。
4. **OpenCLI 扩展发现**：路由表未覆盖的平台可先查 `opencli list` 与 `opencli <平台> --help`，仅在用户任务明确需要时执行只读命令，并以非空内容验收。

## 平台路由表（单一事实源）

| 平台 / 场景 | 详细文档与排障 Runbook |
|---|---|
| Exa 网页与技术搜索 | [references/search.md](references/search.md) |
| 小红书、Twitter/X、B站、V2EX、Reddit、Facebook、Instagram | [references/social.md](references/social.md) |
| LinkedIn、Boss直聘（含严格 CDP 与登录态 Runbook） | [references/career.md](references/career.md) |
| GitHub 仓库/代码/Issue（`gh` CLI） | [references/dev.md](references/dev.md) |
| 通用网页阅读（Jina Reader）、RSS | [references/web.md](references/web.md) |
| YouTube、B站字幕与音频转写、小宇宙播客 | [references/video.md](references/video.md) |
| 雪球股票行情、搜索、热门讨论 | [references/finance.md](references/finance.md) |

## 常用快速命令

### 零配置通道

```powershell
# Exa 搜索
mcporter call exa.web_search_exa query="query" numResults=5

# 通用网页阅读（Jina Reader）
curl.exe -s "https://r.jina.ai/URL"

# GitHub 搜索
gh search repos "query" --sort stars --limit 10

# YouTube 字幕（注意：B站禁用 yt-dlp，会 412；重试链见 references/video.md）
yt-dlp --write-sub --write-auto-sub --skip-download -o "$env:TEMP/%(id)s" "URL"

# V2EX 热门
curl.exe -s "https://www.v2ex.com/api/topics/hot.json" -H "User-Agent: agent-reach/1.0"

# B站搜索（bili-cli，只读免登录）
bili search "query" --type video -n 5
```

### 需登录态通道（先按需查 `agent-reach doctor --json`）

```powershell
# 小红书（桌面首选 OpenCLI；读笔记须带 xsec_token，详见 references/social.md）
opencli xiaohongshu search "query" -f yaml

# Twitter/X（需显式提供 TWITTER_AUTH_TOKEN / TWITTER_CT0 或用 OpenCLI，详见 references/social.md）
twitter search "query" -n 10

# Reddit（必须登录态，桌面首选 OpenCLI）
opencli reddit search "query" -f yaml

# Facebook / Instagram（桌面 OpenCLI）
opencli facebook search "query" -f yaml
opencli instagram search "query" -f yaml

# Boss直聘（必须严格 CDP 模式；配置/登录判定/错误码详见 references/career.md）
boss --browser-source existing-browser --cdp-url http://localhost:9222 search "大模型" --city 深圳 --page 1
```

## 平台关键红线索引

- **Boss直聘**：配置、专用 Chrome 9222 拉起、双登录态（`session.enc` vs 浏览器 `wt2`）、`security-check` 区分及 `AUTH_EXPIRED` / `ENVIRONMENT_RISK` 处置，**务必先读 [references/career.md](references/career.md)**。
- **Twitter / 小红书**：凭据注入方式、`xsec_token` 约束与失败重试链见 [references/social.md](references/social.md)。
- **渠道配置与帮助**：如需检查或配置渠道，运行本地 `agent-reach doctor` 或 `agent-reach --help`（不拉取未锁定的远程脚本或在线文档）。
