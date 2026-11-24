# 视频 / 播客

YouTube、B站、小宇宙播客的字幕和转录。临时文件统一放系统临时目录（Windows PowerShell 使用 `$env:TEMP`，macOS/Linux 使用 `/tmp`）。

## YouTube (`yt-dlp` / OpenCLI)

### 元数据、字幕与评论

```powershell
# 视频元数据 / 搜索
yt-dlp --dump-json "URL"
yt-dlp --dump-json "ytsearch5:query"

# 下载字幕（不下载视频）
yt-dlp --write-sub --write-auto-sub --sub-lang "zh-Hans,zh,en" --skip-download -o "$env:TEMP/%(id)s" "URL"
Get-Content "$env:TEMP\VIDEO_ID.*.vtt"

# 提取评论（best-effort，结果在 .info.json 的 comments 字段）
yt-dlp --write-comments --skip-download --write-info-json --extractor-args "youtube:max_comments=20" -o "$env:TEMP/%(id)s" "URL"
```

> macOS/Linux 将 `$env:TEMP` 替换为 `/tmp`，读取用 `cat /tmp/VIDEO_ID.*.vtt`。自动字幕可能存在行间重复，需后处理。

### 字幕失败重试链（按序执行，拿到非空实质内容即停）

`doctor` 仅确认 `yt-dlp` 与 JS runtime 可执行，不校验具体视频字幕：

1. 先试上述 `yt-dlp --write-sub --write-auto-sub`。
2. 若遇 bot 校验或无字幕文件，且 OpenCLI 已连接：`opencli youtube transcript "URL" -f yaml`。
3. OpenCLI 报 `Caption URL returned empty response` 时最多重试 3 次（带过期时间的字幕 URL 偶发失效，不代表无字幕）。
4. 仍失败或视频无字幕：`agent-reach transcribe "URL"` 下载音频转写。

### 无字幕兜底：Whisper 音频转写

```powershell
agent-reach transcribe "https://www.youtube.com/watch?v=VIDEO_ID"
agent-reach transcribe .\local_audio.mp3 -o "$env:TEMP\transcript.txt"
```

> 仅接收公开 http(s) URL 或本地音频文件（用 `ytsearch5:` 搜索时先取出具体视频 URL）。需先配置 `agent-reach configure groq-key`（免费）或 `agent-reach configure openai-key`。默认 auto 模式仅用第一个已配置服务商，失败即停；`--allow-provider-fallback` 会显式授权跨服务商降级（可能产生 OpenAI 费用，需先确认内容可共享）。

## B站 / Bilibili（`bili-cli` 为主，OpenCLI 补字幕）

> ⚠️ **不要用 `yt-dlp` 读 B站**（风控已全面 412 拦截）。`yt-dlp` 仅用于 YouTube。

```powershell
# 视频详情 / 搜索 / 热门 / 排行 / 音频切分（bili-cli，只读免登录）
bili video BVxxx
bili search "query" --type video -n 5
bili hot -n 10
bili rank -n 10
bili audio BVxxx                       # 导出 ASR-ready WAV，可配合 agent-reach transcribe

# 字幕与备选读取（OpenCLI，需桌面 Chrome）
opencli bilibili subtitle BVxxx
opencli bilibili search "query" -f yaml
opencli bilibili video BVxxx -f yaml
```

### 零配置兜底：搜索 API 直连

- Windows PowerShell：
  ```powershell
  $ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
  $ck = "$env:TEMP\bili_ck.txt"
  curl.exe -s -c $ck -o NUL -A $ua "https://www.bilibili.com/"
  curl.exe -s -b $ck -A $ua -e "https://www.bilibili.com/" "https://api.bilibili.com/x/web-interface/search/all/v2?keyword=QUERY&page=1"
  ```
- macOS / Linux：
  ```bash
  UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
  curl -s -c /tmp/bili_ck.txt -o /dev/null -A "$UA" "https://www.bilibili.com/"
  curl -s -b /tmp/bili_ck.txt -A "$UA" -e "https://www.bilibili.com/" \
    "https://api.bilibili.com/x/web-interface/search/all/v2?keyword=QUERY&page=1"
  ```

> **安装 `bili-cli`**：`pipx install bilibili-cli`（上游 2026-03 起停更但只读功能实测健康）。

## 小宇宙播客 / Xiaoyuzhou Podcast

### 转录单集播客

- **Windows 11**：`~/.agent-reach/tools/xiaoyuzhou/transcribe.sh` 为 Bash 脚本，需在 **Git Bash / WSL** 中运行；或直接使用跨平台的 `agent-reach transcribe "<音频URL或本地文件>"`（配合 `qwen-transcribe` 亦可）。
- **macOS / Linux / Git Bash**：
  ```bash
  # 可选 --polish 用 Groq Llama 3.3 70B 补中文标点与分段（多 ~7 秒）
  ~/.agent-reach/tools/xiaoyuzhou/transcribe.sh --polish "https://www.xiaoyuzhoufm.com/episode/EPISODE_ID"
  ```

### 前置要求

1. **ffmpeg**：Windows 用 `winget install Gyan.FFmpeg`；macOS 用 `brew install ffmpeg`；Linux 用系统包管理器。
2. **Groq API Key**（免费）：`https://console.groq.com/keys`，执行 `agent-reach configure groq-key`。
3. **首次启用通道**（需用户授权）：`agent-reach install --env=auto --system --channels=xiaoyuzhou`，检查用 `agent-reach doctor`。

## 选择指南

| 场景 | 推荐工具 |
|---|---|
| YouTube 字幕 | `yt-dlp` → 失败切 OpenCLI（最多 3 次）→ `agent-reach transcribe` |
| B站视频详情/搜索 | `bili-cli` |
| B站字幕 | `opencli bilibili subtitle` |
| 播客转录 | `transcribe.sh`（macOS/Linux/Git Bash）或 `agent-reach transcribe` |
| 无字幕音视频 | `agent-reach transcribe`（B站先 `bili audio`） |
