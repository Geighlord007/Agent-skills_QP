---
name: agent-reach
description: >
  Give your AI agent eyes to see the entire internet.
  Search and read 17 platforms: Twitter/X, Reddit, YouTube, GitHub, Bilibili,
  XiaoHongShu, Douyin, Weibo, WeChat Articles, Xiaoyuzhou Podcast, LinkedIn,
  V2EX, Xueqiu, RSS, Exa web search, and any web page.
  Zero config for 8 channels. Use when user asks to search, read, or interact
  on any supported platform, shares a URL, or asks to search the web.
  Triggers: "搜推特", "搜小红书", "看视频", "搜一下", "上网搜", "帮我查",
  "search twitter", "youtube transcript", "search reddit", "read this link",
  "B站", "bilibili", "抖音视频", "微信文章", "公众号", "微博", "V2EX",
  "小宇宙", "播客", "podcast", "雪球", "股票", "stock quote",
  "web search", "research", "帮我安装".
metadata:
  openclaw:
    homepage: https://github.com/Panniantong/Agent-Reach
---

# Agent Reach — Usage Guide

Upstream tools for 13+ platforms. Call them directly.

Run `agent-reach doctor` to check which channels are available.

> ## 📌 本机环境备注（2026-08 实测，优先以此为准）
>
> 配套脚本在本 skill 目录的 `scripts/` 下（雪球讨论区、小红书用户搜索）。
>
> **本机已验证可用的六平台后端**：Bilibili（yt-dlp + bili CLI）、微博（mcporter→mcp-server-weibo）、
> 抖音（mcporter→douyin-mcp-server）、雪球（Cookie + API/Playwright）、Twitter（twitter CLI + 代理）、
> 小红书（mcporter→xiaohongshu-mcp 本地服务）。
>
> - **网络**：PyPI 一律走清华镜像 `-i https://pypi.tuna.tsinghua.edu.cn/simple`（pipx 内部用 uv，需 `UV_DEFAULT_INDEX`）；
>   GitHub 下载用 curl 或代理。本机代理为 `http://127.0.0.1:7890`（Molly），Twitter 必须走它。
> - **微博/抖音不在 agent-reach 包里**：是手动注册到 mcporter 的社区 MCP 服务（见 `~/.mcporter/mcporter.json`）。
>   微博免登录；抖音免登录但 venv 内有补丁（见下方抖音节）。
> - **小红书**：服务不在时需先启动：`cd ~/.agent-reach/tools/xiaohongshu-mcp && nohup ./xiaohongshu-mcp > /tmp/xhs-mcp.log 2>&1 &`
>   启动时不能带代理变量。用 v2.4.3，v2.5.0 在本机段错误。无用户搜索工具，搜用户用本 skill 目录 `scripts/xhs_search_user.py`。
> - **雪球**：行情 API 带 Cookie 直连即可；个股讨论区有 WAF，用本 skill 目录 `scripts/xueqiu_stock_comments.py`。
> - **微信公众号（2026-08-14 新增可用）**：`python3 本skill目录/scripts/wechat_read.py <文章URL>`。
>   curl/普通 Chrome 都会被 TCaptcha 墙拦，只有 Camoufox 能过（本机已修复，见下方公众号节）。
> - **Cookie 过期**：B站/雪球重新登录 Chrome 后 `agent-reach configure --from-browser chrome --platform <平台>`；
>   Twitter/小红书用 Cookie-Editor 导出后更新对应配置（小红书改完要重启服务）。

## ⚠️ Workspace Rules

**Never create files in the agent workspace.** Use `/tmp/` for temporary output and `~/.agent-reach/` for persistent data.

## Web — Any URL

```bash
curl -s "https://r.jina.ai/URL"
```

## Web Search (Exa)

```bash
mcporter call 'exa.web_search_exa(query: "query", numResults: 5)'
mcporter call 'exa.get_code_context_exa(query: "code question", tokensNum: 3000)'
```

## Twitter/X (twitter-cli)

```bash
# 需先配置 Cookie（见下方说明），然后在同一 shell 中导出环境变量：
export TWITTER_AUTH_TOKEN="..."
export TWITTER_CT0="..."
twitter search "query" -n 10                  # search
twitter read URL_OR_ID                        # read tweet
twitter user-tweets @username -n 20           # user timeline
```

> 获取 Cookie：Chrome 登录 x.com → Cookie-Editor 扩展 → Export → Header String，
> 然后运行 `agent-reach configure twitter-cookies` 保存。
> 注意：SKILL.md 旧版写的 `bird` 已弃用，本机安装的是 twitter-cli（命令为 `twitter`）。
> 本机备注：twitter-cli 必须走代理，本机代理为 `http://127.0.0.1:7890`（Molly），
> 使用前 `export HTTPS_PROXY=http://127.0.0.1:7890 HTTP_PROXY=http://127.0.0.1:7890`。

## YouTube (yt-dlp)

```bash
yt-dlp --dump-json "URL"                     # video metadata
yt-dlp --write-sub --write-auto-sub --sub-lang "zh-Hans,zh,en" --skip-download -o "/tmp/%(id)s" "URL"
                                             # download subtitles, then read the .vtt file
yt-dlp --dump-json "ytsearch5:query"         # search
```

## Bilibili (yt-dlp)

```bash
yt-dlp --dump-json "https://www.bilibili.com/video/BVxxx"
yt-dlp --write-sub --write-auto-sub --sub-lang "zh-Hans,zh,en" --convert-subs vtt --skip-download -o "/tmp/%(id)s" "URL"
```

> Server IPs may get 412. Use `--cookies-from-browser chrome` or configure proxy.

## Reddit

```bash
curl -s "https://www.reddit.com/r/SUBREDDIT/hot.json?limit=10" -H "User-Agent: agent-reach/1.0"
curl -s "https://www.reddit.com/search.json?q=QUERY&limit=10" -H "User-Agent: agent-reach/1.0"
```

> Server IPs may get 403. Search via Exa instead, or configure proxy.

## GitHub (gh CLI)

```bash
gh search repos "query" --sort stars --limit 10
gh repo view owner/repo
gh search code "query" --language python
gh issue list -R owner/repo --state open
gh issue view 123 -R owner/repo
```

## 小红书 / XiaoHongShu (mcporter)

```bash
mcporter call 'xiaohongshu.search_feeds(keyword: "query")'
mcporter call 'xiaohongshu.get_feed_detail(feed_id: "xxx", xsec_token: "yyy")'
mcporter call 'xiaohongshu.get_feed_detail(feed_id: "xxx", xsec_token: "yyy", load_all_comments: true)'
```

> 本机后端（2026-08 实测可用）：xiaohongshu-mcp v2.4.3 本地服务。
> 注意 v2.5.0 的 linux 二进制在本机会段错误，勿升级。
> 启动方式（服务不在时先启动）：
> ```bash
> cd ~/.agent-reach/tools/xiaohongshu-mcp && nohup ./xiaohongshu-mcp > /tmp/xhs-mcp.log 2>&1 &
> ```
> Cookie 存于 `~/.agent-reach/tools/xiaohongshu-mcp/cookies.json`（改后需重启服务生效）。
> 启动时务必不要带 HTTP(S)_PROXY（小红书是国内站，走代理会导致页面加载超时）。

> **Tip: Clean bloated output.** XHS API returns large JSON with many unused fields.
> Pipe through the formatter to save context:
> ```bash
> mcporter call 'xiaohongshu.search_feeds(keyword: "query")' | agent-reach format xhs
> ```
> This keeps only: title, content, author, engagement counts, image URLs, and tags.

## 抖音 / Douyin (mcporter)

```bash
mcporter call 'douyin.parse_douyin_video_info(share_link: "https://v.douyin.com/xxx/")'
mcporter call 'douyin.get_douyin_download_link(share_link: "https://v.douyin.com/xxx/")'
```

> No login needed.
> ⚠️ 本机备注（2026-08）：douyin-mcp-server 与 mcp 2.x 不兼容，venv 内需 `mcp<2`
> （`pipx inject douyin-mcp-server 'mcp<2' --force`）；且抖音有蜘蛛检测，
> venv 里的 `server.py` 已打补丁（先访问 iesdouyin.com 主站拿会话 Cookie + 带 Referer）。
> 若 `pipx reinstall/upgrade douyin-mcp-server` 后失效，需重新打这两个补丁。

## 微信公众号 / WeChat Articles

**Search** (miku_ai，本机已装，系统 python3 直接可用，2026-08-14 实测):
```bash
python3 -c "
import asyncio
from miku_ai import get_wexin_article
async def s():
    for a in await get_wexin_article('关键词', 5):
        print(f'{a[\"title\"]} | {a[\"url\"]}')
asyncio.run(s())
"
```
> 返回的是带签名和时间戳的临时链接（几小时内有效），可直接喂给 wechat_read.py 读正文。

**Read**（本机可用，2026-08-14 实测）：
```bash
python3 ~/.kimi-code/skills/agent-reach/scripts/wechat_read.py "https://mp.weixin.qq.com/s/ARTICLE_ID"
```

> WeChat articles cannot be read with Jina Reader or curl（会弹 TCaptcha 验证码墙 / poc_token 挑战）。
> 本机用 Camoufox（反指纹 Firefox）自动过挑战。
> ⚠️ 本机 Camoufox 0.5.4 有两处手动修复，pip 升级 camoufox 后会失效需重做：
> 1. uBlock 插件手动安装：官方下载直连返回 451，需走代理下载 xpi 并**解压**到
>    `~/.cache/camoufox/addons/UBO/`（解压后的目录，含 manifest.json，不是 xpi 文件本身）。
> 2. `camoufox/pkgman.py` 的 `Version.is_supported()` 版本门对新命名格式误判导致无限递归，
>    已补丁为直接返回 True。
> 旧路径 `~/.agent-reach/tools/wechat-article-for-ai` 从未安装，忽略。

## 微博 / Weibo (mcporter)

```bash
# 热搜榜
mcporter call 'weibo.get_trendings(limit: 20)'

# 搜索用户
mcporter call 'weibo.search_users(keyword: "雷军", limit: 10)'

# 获取用户资料
mcporter call 'weibo.get_profile(uid: "1195230310")'

# 获取用户微博动态
mcporter call 'weibo.get_feeds(uid: "1195230310", limit: 20)'

# 获取用户热门微博
mcporter call 'weibo.get_hot_feeds(uid: "1195230310", limit: 10)'

# 搜索微博内容
mcporter call 'weibo.search_content(keyword: "人工智能", limit: 20)'

# 搜索话题
mcporter call 'weibo.search_topics(keyword: "AI", limit: 10)'

# 获取微博评论
mcporter call 'weibo.get_comments(mid: "5099916367123456", limit: 50)'

# 获取粉丝列表
mcporter call 'weibo.get_fans(uid: "1195230310", limit: 20)'

# 获取关注列表
mcporter call 'weibo.get_followers(uid: "1195230310", limit: 20)'
```

> Zero config. No login needed. Uses mobile API with auto visitor cookies.

## 小宇宙播客 / Xiaoyuzhou Podcast (groq-whisper + ffmpeg)

```bash
# 转录单集播客（输出文本到 /tmp/）
~/.agent-reach/tools/xiaoyuzhou/transcribe.sh "https://www.xiaoyuzhoufm.com/episode/EPISODE_ID"
```

> 需要 ffmpeg + Groq API Key（免费）。  
> 配置 Key：`agent-reach configure groq-key YOUR_KEY`  
> 首次运行需安装工具：`agent-reach install --env=auto`  
> 运行 `agent-reach doctor` 检查状态。  
> 输出 Markdown 文件默认保存到 `/tmp/`。


## LinkedIn (mcporter)

```bash
mcporter call 'linkedin.get_person_profile(linkedin_url: "https://linkedin.com/in/username")'
mcporter call 'linkedin.search_people(keyword: "AI engineer", limit: 10)'
```

Fallback: `curl -s "https://r.jina.ai/https://linkedin.com/in/username"`

## V2EX (public API)

```bash
# 热门主题
curl -s "https://www.v2ex.com/api/topics/hot.json" -H "User-Agent: agent-reach/1.0"

# 节点主题（node_name 如 python、tech、jobs、qna）
curl -s "https://www.v2ex.com/api/topics/show.json?node_name=python&page=1" -H "User-Agent: agent-reach/1.0"

# 主题详情（topic_id 从 URL 获取，如 https://www.v2ex.com/t/1234567）
curl -s "https://www.v2ex.com/api/topics/show.json?id=TOPIC_ID" -H "User-Agent: agent-reach/1.0"

# 主题回复
curl -s "https://www.v2ex.com/api/replies/show.json?topic_id=TOPIC_ID&page=1" -H "User-Agent: agent-reach/1.0"

# 用户信息
curl -s "https://www.v2ex.com/api/members/show.json?username=USERNAME" -H "User-Agent: agent-reach/1.0"
```

Python 调用示例（V2EXChannel）：

```python
from agent_reach.channels.v2ex import V2EXChannel

ch = V2EXChannel()

# 获取热门帖子（默认 20 条）
# 返回字段：id, title, url, replies, node_name, node_title, content(前200字), created
topics = ch.get_hot_topics(limit=10)
for t in topics:
    print(f"[{t['node_title']}] {t['title']} ({t['replies']} 回复) {t['url']}")
    print(f"  id={t['id']} created={t['created']}")

# 获取指定节点的最新帖子
# 返回字段：id, title, url, replies, node_name, node_title, content(前200字), created
node_topics = ch.get_node_topics("python", limit=5)
for t in node_topics:
    print(t["id"], t["title"], t["url"])

# 获取单个帖子详情 + 回复列表
# 返回字段：id, title, url, content, replies_count, node_name, node_title,
#           author, created, replies (list of {author, content, created})
topic = ch.get_topic(1234567)
print(topic["title"], "—", topic["author"])
for r in topic["replies"]:
    print(f"  {r['author']}: {r['content'][:80]}")

# 获取用户信息
# 返回字段：id, username, url, website, twitter, psn, github, btc, location, bio, avatar, created
user = ch.get_user("Livid")
print(user["username"], user["bio"], user["github"])

# 搜索（V2EX 公开 API 不支持，会返回说明信息）
result = ch.search("asyncio")
print(result[0]["error"])  # 提示使用站内搜索或 Exa channel
```

> No auth required. Results are public JSON. V2EX 节点名见 https://www.v2ex.com/planes

## 雪球 / Xueqiu (public API)

```python
from agent_reach.channels.xueqiu import XueqiuChannel

ch = XueqiuChannel()

# 获取股票行情（符号格式：SH600519 沪市、SZ000858 深市、AAPL 美股、00700 港股）
# 返回字段：symbol, name, current, percent, chg, high, low, open, last_close,
#           volume, amount, market_capital, turnover_rate, pe_ttm, timestamp
quote = ch.get_stock_quote("SH600519")
print(f"{quote['name']} ({quote['symbol']}): {quote['current']} ({quote['percent']}%)")

# 搜索股票
# 返回字段：symbol, name, exchange
stocks = ch.search_stock("茅台", limit=5)
for s in stocks:
    print(f"{s['name']} ({s['symbol']}) - {s['exchange']}")

# 热门帖子
# 返回字段：id, title, text(前200字), author, likes, url
posts = ch.get_hot_posts(limit=10)
for p in posts:
    print(f"{p['author']}: {p['text'][:50]}... ({p['likes']} 赞)")

# 热门股票（stock_type=10 人气榜，stock_type=12 关注榜）
# 返回字段：symbol, name, current, percent, rank
hot = ch.get_hot_stocks(limit=10, stock_type=10)
for s in hot:
    print(f"#{s['rank']} {s['name']} ({s['symbol']}): {s['current']} ({s['percent']}%)")
```

> ⚠️ 2026-08 实测：雪球已不再发游客 token，`XueqiuChannel` 免登录路径返回 400016。
> 必须先在 Chrome 登录 xueqiu.com，然后运行
> `agent-reach configure --from-browser chrome --platform xueqiu` 导入登录 Cookie。

## RSS (feedparser)

## RSS

```python
python3 -c "
import feedparser
for e in feedparser.parse('FEED_URL').entries[:5]:
    print(f'{e.title} — {e.link}')
"
```

## Troubleshooting

- **Channel not working?** Run `agent-reach doctor` — shows status and fix instructions.
- **Twitter fetch failed?** Ensure `undici` is installed: `npm install -g undici`. Configure proxy: `agent-reach configure proxy URL`.

## Setting Up a Channel ("帮我配 XXX")

If a channel needs setup (cookies, Docker, etc.), fetch the install guide:
https://raw.githubusercontent.com/Panniantong/agent-reach/main/docs/install.md

User only provides cookies. Everything else is your job.
