# 社交媒体 & 社区

小红书、Twitter/X、B站、V2EX、Reddit、Facebook、Instagram。

## 小红书 / XiaoHongShu（多后端）

不确定当前激活后端时，先运行 `agent-reach doctor --json` 查看 `xiaohongshu` 的 `active_backend`。

### 后端 A：OpenCLI（桌面首选）

```powershell
opencli xiaohongshu search "query" -f yaml
opencli xiaohongshu note "NOTE_URL" -f yaml      # 须使用搜索结果中的完整 URL（含 xsec_token）
opencli xiaohongshu comments NOTE_ID -f yaml
opencli xiaohongshu feed -f yaml
opencli xiaohongshu user USER_ID -f yaml
```

> 要求 Chrome 打开且装了 OpenCLI 扩展。OpenCLI 只复用用户明确控制的 Chrome 会话；Agent Reach 不替用户登录，也不读取浏览器 Cookie。`agent-reach configure xhs-cookies` 不会将 Cookie 注入 OpenCLI。

### 后端 B：xiaohongshu-mcp（服务器/无 OpenCLI 场景）

```powershell
agent-reach configure xhs-cookies                                                   # 先用 Cookie-Editor 手工导出
mcporter call xiaohongshu.check_login_status --timeout 120000
mcporter call xiaohongshu.search_feeds keyword="query" --timeout 120000
mcporter call xiaohongshu.get_feed_detail feed_id="..." xsec_token="..." --timeout 120000
```

> 首次调用会自动下载约 150MB 无头浏览器，务必带 `--timeout 120000`。仅保存 xiaohongshu.com 同域 Cookie。

### 存量备选：`xhs-cli`（已停更）

> `xhs-cli` 上游自 2026-03 起停更，`user` / `user-posts` / `favorites` 可能报 API 错误。仅存量环境保留 `xhs search` / `xhs read NOTE_URL` / `xhs comments`，新环境直接使用后端 A 或 B。

### 通用注意事项

- **xsec_token 限制**：不能用裸 `note_id` 直接读笔记；必须先搜索/feed 获取含 `xsec_token` 的完整 URL 或参数。
- **频率控制**：每次操作间隔 2–3 秒，避免触发验证码。
- **只读原则**：不执行发帖/评论/点赞等写操作。

## Twitter/X (`twitter-cli` / OpenCLI)

### 认证前置条件

`agent-reach configure twitter-cookies` 保存的 Cookie 仅用于 `doctor` 检查，不会设置当前 Shell。运行 `twitter` CLI 前，必须在当前会话或子进程中显式注入环境变量（切勿在日志或回显中泄露值）：

- Windows PowerShell：
  ```powershell
  $env:TWITTER_AUTH_TOKEN = "..."
  $env:TWITTER_CT0 = "..."
  ```
- macOS / Linux (bash/zsh)：
  ```bash
  export TWITTER_AUTH_TOKEN="..."
  export TWITTER_CT0="..."
  ```

> 桌面装了 OpenCLI 时可直接用 `opencli twitter search/article/user-posts -f yaml`（复用浏览器登录态，无需环境变量）。

### 常用命令

```powershell
# 稳定命令
twitter feed -n 20
twitter tweet URL_OR_ID
twitter article URL_OR_ID
twitter user-posts @username -n 20
twitter user @username

# 可能不稳定（GraphQL 端点偶发 404）
twitter search "query" -n 10
```

### `search` 失败重试链（按序执行，成功即停）

1. 直接重试一次：`twitter search "query" -n 10`
2. 升级后再试：`pipx upgrade twitter-cli` 后重试
3. 切 OpenCLI 桌面备选：`opencli twitter search "query" -f yaml`
4. 改用 `twitter feed` / `twitter user-posts @username` 绕路

> **注意**：`pipx install twitter-cli`（建议 v0.8.5+）；建议加 `--yaml` 或 `--json` 输出；避免在数据中心/VPS IP 上高频调用（有封号风险）。

## B站 / Bilibili

> ⚠️ **不要用 `yt-dlp` 读 B站**（风控已全面 412 拦截）。统一使用 `bili-cli` / OpenCLI。

```powershell
bili search "query" --type video -n 5
bili hot -n 10
bili video BVxxx
opencli bilibili subtitle BVxxx
```

> 音频转写与 API 直连兜底见 [references/video.md](video.md)。

## V2EX（公开 JSON API，免认证）

```powershell
# 热门主题
curl.exe -s "https://www.v2ex.com/api/topics/hot.json" -H "User-Agent: agent-reach/1.0"

# 节点主题（node_name 如 python, tech, jobs, qna, programmers）
curl.exe -s "https://www.v2ex.com/api/topics/show.json?node_name=python&page=1" -H "User-Agent: agent-reach/1.0"

# 主题详情与回复
curl.exe -s "https://www.v2ex.com/api/topics/show.json?id=TOPIC_ID" -H "User-Agent: agent-reach/1.0"
curl.exe -s "https://www.v2ex.com/api/replies/show.json?topic_id=TOPIC_ID&page=1" -H "User-Agent: agent-reach/1.0"

# 用户信息
curl.exe -s "https://www.v2ex.com/api/members/show.json?username=USERNAME" -H "User-Agent: agent-reach/1.0"
```

> 节点列表：`https://www.v2ex.com/planes`（Python 如需解析可直接用标准库 `urllib.request` + `json`，不依赖隔离环境内的内部包）。

## Reddit（必须登录态）

匿名 `.json` 已 403，官方 API 审批基本关闭。桌面首选 OpenCLI（需 Chrome 已登录 reddit.com，中国大陆需代理）：

```powershell
opencli reddit search "query" -f yaml
opencli reddit read POST_ID -f yaml
opencli reddit subreddit LocalLLaMA -f yaml
opencli reddit hot -f yaml
opencli reddit popular -f yaml
opencli reddit subreddit-info LocalLLaMA -f yaml
```

> **存量备选**：`rdt-cli`（上游 2026-03 起停更，仅旧环境保留 `rdt search` / `rdt read` / `rdt sub`）。已有 2025-11 前官方 script app 凭证的用户可自行使用 PRAW，不推荐新申请。

## Facebook（OpenCLI，必须登录态）

复用 Chrome 中 `facebook.com` 登录态，不推荐 Jina/Exa/Graph API 作为默认路径：

```powershell
opencli facebook search "query" -f yaml
opencli facebook profile zuck -f yaml
opencli facebook feed --limit 10 -f yaml
opencli facebook groups --limit 20 -f yaml
```

> Groups 仅保证读取当前账号可见的群组列表与最近动态。

## Instagram（OpenCLI，必须登录态）

复用 Chrome 中 `instagram.com` 登录态（不推荐使用不稳定的 `instaloader`）：

```powershell
opencli instagram search "query" -f yaml         # 搜用户（非全站帖子搜索）
opencli instagram profile nasa -f yaml
opencli instagram user nasa --limit 12 -f yaml   # 读指定用户最近帖子
opencli instagram explore --limit 20 -f yaml
opencli instagram saved --limit 20 -f yaml
```

> 遇到 429 或 login required 时，让用户在 Chrome 中重新登录并降低请求频率。
