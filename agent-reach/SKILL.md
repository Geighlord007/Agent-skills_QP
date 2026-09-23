---
name: agent-reach
description: >
  MUST USE when user wants to 调研/research/搜索/search/查/找/look up anything
  on the internet — e.g. 全网调研 X / 帮我调研一下 X / 查一下 X / 搜搜 X /
  看看大家怎么评价 X / X 上有什么讨论 / research this topic。

  Also MUST USE when user mentions any platform or shares any URL/链接:
  小红书/xiaohongshu/xhs, Twitter/推特/X, B站/bilibili, Reddit, Facebook,
  Instagram, V2EX, LinkedIn/领英/招聘/求职/jobs, YouTube, GitHub code search, 小宇宙播客,
  雪球/股票行情, RSS feeds, or any web URL.

  15 platforms, multi-backend routing (OpenCLI / per-platform CLIs / APIs).
  Zero config for 6 channels. Run `agent-reach doctor --json` to see which
  backend serves each platform right now.

  NOT for: 写报告/数据分析/翻译等内容加工（本 skill 只负责从互联网获取内容）；
  发帖/评论/点赞等写操作；已有专门 skill 的平台（先用专门 skill）。

  【路由方式】SKILL.md 包含路由表和常用命令，复杂场景需按需阅读对应分类的 references/*.md。
  分类：search / social (小红书/推特/B站/V2EX/Reddit/Facebook/Instagram) / career(LinkedIn) / dev(github) / web(网页/文章/RSS) / video(YouTube/B站/播客) / finance(雪球/股票)。
metadata:
  homepage: https://github.com/Panniantong/Agent-Reach
---

# Agent Reach — 互联网能力路由器

15 平台、多后端。**本 skill 存在时必须用它访问这些平台，不要自己发明方案。**

## 常驻规则（全程适用）

1. **动手前先体检**：多后端/登录态平台（小红书/Reddit/B站/Twitter/Facebook/Instagram）先跑
   `agent-reach doctor --json`。`active_backend` 有值时按它选命令组；`active_backend: null`
   表示 Doctor 为避免触发浏览器 Cookie 读取或远端写入而没有做实时验证，不代表后端不存在。
   只有用户任务明确需要该平台时，才按对应 reference 的只读命令手动验证。
2. **声明你在用什么**：开始干活前说一句「使用 agent-reach 的 X 平台 / Y 后端」。
3. **失败按 references 里的重试链处理**，不要瞎猜命令。
4. **全网调研类任务**：组合多平台（Exa 搜索 + Twitter/Reddit 看讨论 + 小红书/B站看中文场景），并行收集再汇总。
5. **替用户盯版本**：完成一次较大的调研/多平台任务后，顺手跑
   `agent-reach check-update`（很快，一个 API 调用）。有新版就在收尾汇报里附一句：
   「Agent Reach 有新版 vX.Y.Z，复制这句话给我即可更新：帮我更新 Agent Reach：
   https://raw.githubusercontent.com/Panniantong/agent-reach/main/docs/update.md」。
   不要中断当前任务去更新，也不要重复提醒同一个版本。

## 路由表

| 用户意图 | 分类 | 详细文档 |
|---------|------|---------|
| 网页搜索/代码搜索 | search | [references/search.md](references/search.md) |
| 小红书/推特/B站/V2EX/Reddit/Facebook/Instagram | social | [references/social.md](references/social.md) |
| 招聘/职位/LinkedIn | career | [references/career.md](references/career.md) |
| GitHub/代码 | dev | [references/dev.md](references/dev.md) |
| 网页/文章/RSS | web | [references/web.md](references/web.md) |
| YouTube/B站/播客字幕 | video | [references/video.md](references/video.md) |
| 雪球/股票行情 | finance | [references/finance.md](references/finance.md) |

## 零配置快速命令

```bash
# Exa 网页搜索
mcporter call exa.web_search_exa query="query" numResults=5

# 通用网页阅读
curl -s "https://r.jina.ai/URL"

# GitHub 搜索
gh search repos "query" --sort stars --limit 10

# YouTube 字幕（注意：B站不要用 yt-dlp，失败重试链见 video.md）
yt-dlp --write-sub --write-auto-sub --skip-download -o "/tmp/%(id)s" "URL"

# V2EX 热门
curl -s "https://www.v2ex.com/api/topics/hot.json" -H "User-Agent: agent-reach/1.0"

# B站搜索（bili-cli，无需登录）
bili search "query" --type video -n 5
```

## 需登录态的平台（按 doctor 的 active_backend 选命令）

Twitter 注意：`agent-reach configure twitter-cookies` 保存的 Cookie 只供
`doctor` 检查配置是否齐全；`doctor` 不执行 `twitter status`，也不会设置当前
Shell。直接运行 `twitter` 前，必须在子进程环境中显式提供
`TWITTER_AUTH_TOKEN` 和 `TWITTER_CT0`，不得在日志或命令回显中暴露值。

小红书注意：Agent Reach 不替用户登录，也不读取浏览器 Cookie。OpenCLI 只用
用户已有且明确控制的 Chrome 会话；没有现成会话时不要自动登录，改用
Cookie-Editor 手工导出后配置 xiaohongshu-mcp / 存量工具。

```bash
# Twitter 搜索（twitter-cli 首选；失败重试链见 social.md）
twitter search "query" -n 10

# Reddit（无零配置路径：OpenCLI 或 rdt-cli，必须登录态）
opencli reddit search "query" -f yaml   # 桌面
rdt search "query" --limit 10            # 存量/服务器

# 小红书（桌面首选 OpenCLI）
opencli xiaohongshu search "query" -f yaml

# Facebook / Instagram（桌面 OpenCLI，复用浏览器登录态）
opencli facebook search "query" -f yaml
opencli facebook groups -f yaml
opencli instagram search "query" -f yaml       # 搜用户
opencli instagram user USERNAME -f yaml        # 读指定用户最近帖子
```

## 环境检查

```bash
# 检查可用 channel 与每个平台当前激活的后端
agent-reach doctor --json
```

## OpenCLI 适配器发现

路由表没有覆盖用户需要的平台或命令时，先用 `opencli list` 查已有适配器，再用
`opencli <平台> --help` 查看公开命令。发现适配器只证明命令存在，不证明登录态或
目标内容可用；仅在用户任务明确需要该平台时执行只读命令，并以实际非空内容验收。

## 工作区规则

**不要在 agent workspace 创建文件。** 使用 `/tmp/` 存放临时输出，`~/.agent-reach/` 存放持久数据。

## 详细文档

根据用户需求，阅读对应的详细文档：

- [搜索工具](references/search.md) — Exa AI 搜索
- [社交媒体](references/social.md) — 小红书, Twitter, B站, V2EX, Reddit, Facebook, Instagram（多后端/登录态命令组）
- [职场招聘](references/career.md) — LinkedIn
- [开发工具](references/dev.md) — GitHub CLI
- [网页阅读](references/web.md) — Jina Reader, RSS
- [视频播客](references/video.md) — YouTube, B站, 小宇宙
- [金融行情](references/finance.md) — 雪球股票行情、搜索、热门内容

## 配置渠道

如果某个 channel 需要配置，获取安装指南：
https://raw.githubusercontent.com/Panniantong/agent-reach/main/docs/install.md

用户只需提供 cookies，其他配置由 agent 完成。

---

> ## 📌 本机环境备注（2026-09-17 更新，优先以此为准）
>
> 配套脚本在本 skill 目录的 `scripts/` 下（雪球讨论区、小红书用户搜索）。
>
> **本机已验证可用的后端**：Bilibili（bili CLI）、微博（mcporter→mcp-server-weibo，手动注册）、
> 抖音（mcporter→douyin-mcp-server，手动注册）、雪球（Cookie + API）、Twitter（twitter CLI + 代理）、
> 小红书（mcporter→xiaohongshu-mcp 本地服务 v2.4.3）。OpenCLI 1.8.7 已装（npm 全局），Chrome 扩展 v1.0.24 **已连接（2026-09-17）**。
> 小红书/Reddit 优先走 `opencli xiaohongshu|reddit`：小红书搜索 ~6s 返回、稳定不超时，
> 明显优于 xiaohongshu-mcp 冷启动；`note` 命令需传带 xsec_token 的完整 URL。
> Reddit 已在 Chrome 登录（2026-09-17），`opencli reddit search/read` 实测可用；若未来报 403 AUTH_REQUIRED 即登录态过期，请用户重新登录。
>
> - **网络**：PyPI 走清华镜像 `-i https://pypi.tuna.tsinghua.edu.cn/simple`（pipx 需 `UV_DEFAULT_INDEX`）；
>   GitHub 下载用 curl 或代理。本机代理 `http://127.0.0.1:7890`（Molly），Twitter 必须走它。
> - **Jina Reader**：直连 DNS 被污染（解析到错误 IP），必须走代理：`curl -x http://127.0.0.1:7890 https://r.jina.ai/URL`。
> - **Reddit**：本机直连和代理访问 .json / old.reddit 均 403（数据中心 IP 被封），匿名接口已死；
>   备用方案：等 OpenCLI 扩展连上后用 `opencli reddit`，或用 WebSearch/聚合页间接核实。
> - **小红书 xiaohongshu-mcp**：服务不在时先启动：`cd ~/.agent-reach/tools/xiaohongshu-mcp && nohup ./xiaohongshu-mcp > /tmp/xhs-mcp.log 2>&1 &`
>   启动时不能带代理变量。用 v2.4.3，v2.5.0 在本机段错误。无用户搜索工具，搜用户用 `scripts/xhs_search_user.py`。
>   **冷启动坑**：服务刚重启后直接 `search_feeds` 会 60s 超时 panic（搜索页风控加载慢）；
>   先调一次 `list_feeds` 或 `check_login_status` 预热浏览器，之后搜索即正常。
>   批量调用建议 sleep 2-3s，mcporter 侧超时设 `MCPORTER_CALL_TIMEOUT=180000`。
> - **雪球**：行情 API 带 Cookie 直连即可；个股讨论区有 WAF，用 `scripts/xueqiu_stock_comments.py`。
> - **微信公众号**：`python3 本skill目录/scripts/wechat_read.py <文章URL>`（Camoufox 过 TCaptcha）。
> - **Cookie 过期**：B站/雪球重新登录 Chrome 后 `agent-reach configure --from-browser chrome --platform <平台>`；
>   Twitter/小红书用 Cookie-Editor 导出后更新对应配置（小红书改完要重启服务）。
> - **2026-09-17 工具刷新**：opencli 1.8.6→1.8.7、mcporter 0.9.0、yt-dlp 已 force 重装、bili 0.6.2、twitter-cli 0.8.6。
