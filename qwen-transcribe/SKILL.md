---
name: qwen-transcribe
description: "基于阿里云百炼 Qwen ASR / Qwen3.8 / Qwen-VL 的一站式音视频转写、会议纪要与视频理解工具（统一承接原 video-transcribe 与 qwen-asr-transcribe）。支持本地长音频（mp3/wav/m4a，≤2GB/12h）与 B站/YouTube/抖音视频链接异步转写（说话人分离、中英混合、时间戳、断点恢复），输出 Markdown + SRT + JSON，含会议八步校对清洗与带关键帧截图的 docx 纪要装配；支持 qwen3.8 整段直传或混合抽帧视频理解，以及 Qwen-VL 镜头抽帧并发抠图归档（logo/软件截图/图表）和可选 SMTP 邮件投递。Use when 用户要语音转文字/录音转写/会议录音转写/区分说话人/校对转写稿/B站或YouTube或抖音视频转文字/整理会议录像/出带图会议纪要/看懂视频/视频问答/收集视频素材/抠视频logo。"
version: 2.0.0
tags: ["asr", "transcription", "video", "audio", "meeting-minutes", "qwen", "dashscope", "oss", "yt-dlp", "vlm", "video-understanding", "asset-harvest", "diarization", "语音转写", "视频转写", "会议纪要", "素材收集", "视频理解"]
platforms: ["windows", "linux", "macos"]
---

# QwenTranscribe 音视频转写、会议纪要与视频理解

统一入口覆盖**本地长音频转写**（原 `qwen-asr-transcribe`）与**视频链接转写 / 会议纪要 / 视频理解 / 素材收集**（原 `video-transcribe`）：

- 本地音频（≤2GB / ≤12h，开说话人分离建议 ≤2h 单声道）或视频链接 → 转写稿（`Markdown` + `SRT` + `JSON`）
- 会议校对清洗 + 说话人实名化 + 带关键帧截图的会议纪要 `.docx`（见 [references/meeting-minutes.md](references/meeting-minutes.md)）
- `qwen3.8` 整段直传 / 混合抽帧视频理解（见 [references/video-understanding.md](references/video-understanding.md)）
- 镜头抽帧 + `Qwen-VL` 并发检测抠图归档 + 可选 SMTP 邮件投递

不适合：需要实时流式字幕的场景。

## 工作流：先出方案，用户确认后再执行

单文件简单指令（"转写这个录音/链接"）直接执行。**批量整理任务必须分两阶段**：
ASR、校对、纪要、docx 属于重处理，开始前必须拿到用户对方案的确认。

1. **盘点与判定**（本地、低成本）：列媒体文件清单与时长/分辨率；已有转写/帧等中间产物先复用；
   按 [references/meeting-minutes.md](references/meeting-minutes.md) 第一节做类型判定
   （会议 / 语音记录 / 游戏与录屏 / 碎片），判定依据写入产出物。
2. **出方案**：逐文件列处理计划——类型、产出物（纪要 docx / 校对版 / 内容说明）、输出命名、
   抽帧策略（混合抽帧，见 [references/video-understanding.md](references/video-understanding.md)）、
   docx 嵌图数量——等用户确认。
3. **确认后执行**：转写 → 校对清洗与纪要（`meeting-minutes.md` 第二、三节）→ docx 装配
   （第四节）→ 总览索引。原文件永不删除。

## 依赖与凭据配置

- Python 3.10+（标准库可直接跑，内置阿里云 virtual-hosted OSS 流式上传/清理；装 `oss2` 可自动启用大文件分片断点续传；`python-docx` + `Pillow` 用于 docx 装配与高速进程内感知哈希）
- `yt-dlp`（URL 模式）；`ffmpeg`（视频抽帧 / 混合抽帧 / 素材抠图 / 非标录音转码）
- **凭据合并顺序**（后者覆盖前者，环境变量始终最高优先）：
  1. `~/.config/qwen-asr/env`（只读兼容旧配置，每行 `KEY=VALUE`，支持 UTF-8 与行内 `#` 注释）
  2. `~/.config/video-transcribe/config.json`（若新路径尚不存在时自动只读兼容）
  3. `~/.config/qwen-transcribe/config.json`
  4. 环境变量：`DASHSCOPE_API_KEY`、`DASHSCOPE_WORKSPACE_ID`（可选）、`OSS_ACCESS_KEY_ID`、`OSS_ACCESS_KEY_SECRET`、`OSS_BUCKET`、`OSS_ENDPOINT`（可选，默认 `https://oss-cn-beijing.aliyuncs.com`）

首次缺配置向用户索取后写入配置，并用 `python {baseDir}/scripts/qtranscribe.py status` 核对（只读不写盘）。

## 用法

```bash
# 1. 本地音频转写（默认开说话人分离，输出到 <音频同级>/transcript/，转完自动删 OSS 临时文件）
python {baseDir}/scripts/qtranscribe.py audio "会议录音.m4a"
python {baseDir}/scripts/qtranscribe.py audio "录音.mp3" -o ./out --language-hints zh,en --no-email

# 2. 在线视频链接转写（B站 / YouTube / 抖音等；--no-email 跳过发信）
python {baseDir}/scripts/qtranscribe.py url "https://www.bilibili.com/video/BVxxxx" --no-email

# 3. 长任务网络中断后按 task_id 断点恢复取回结果
python {baseDir}/scripts/qtranscribe.py resume <task_id> --title "项目例会" -o ./transcript

# 4. 会议纪要装配：校对清洗 → <会议名>_校对版.md + <会议名>_会议纪要.md → docx
python {baseDir}/scripts/make_meeting_docx.py --config meetings.json \
  --minutes-dir <纪要目录> --out-dir <输出目录>

# 5. 视频理解：qwen3.8 整段直传（≤2h/≤2GB）或混合抽帧精控
python {baseDir}/scripts/qtranscribe.py understand 录像.mp4
python {baseDir}/scripts/qtranscribe.py understand 录像.mp4 --mode frames --max-frames 16

# 6. 素材收集：场景抽帧 → Qwen-VL 并发 bbox 检测 → 抠图归档
python {baseDir}/scripts/qtranscribe.py url "<链接>" --assets

# 7. 截图/帧分析、SMTP 测试、体检
python {baseDir}/scripts/qtranscribe.py analyze 帧1.png 帧2.png --transcript 转写.md
python {baseDir}/scripts/qtranscribe.py email-test
python {baseDir}/scripts/qtranscribe.py status
```

`audio` 默认输出到 `<音频同级>/transcript/`（产出 `原名_转写.md`、`原名_转写.srt`、`原名_转写_transcription.json`）；`url` / `understand` / `analyze` 默认落在 `~/VideoTranscribe/out/`（传 `-o` 可覆盖）。

## 深入阅读（按需加载）

- [references/meeting-minutes.md](references/meeting-minutes.md)：会议判定标准、转写稿校对清洗八步、说话人实名化、纪要结构、docx 排版（含长发言拆段规则）与内容选图、子代理并行模式。
- [references/video-understanding.md](references/video-understanding.md)：整段直传 / 帧列表 / 平台抽帧三通道选择、混合抽帧策略、平台实测限制（data-uri 上限、fps 注解、审核）。

## 站点能力边界

| 站点 | URL 直接转写 | 说明 |
|---|---|---|
| B站 | ✅ | 普通视频无需登录；会员视频在配置中设置 `ytdlp_cookies_browser` |
| YouTube | ✅ | 地区/年龄限制配 `ytdlp_cookies_browser` |
| 抖音 | ✅ | yt-dlp 支持 |
| 微信视频号 | ❌ | 加密取流，先本地录音后走 `audio` 子命令 |
| 视频会议/直播 | 录音 | 录屏或录音后走 `audio` / `understand` 子命令 |

> 注：本 skill 的 CLI 完全独立跨平台运行；`scripts/engine.py` 同时保留了供外部本地伴侣服务调用的 `JobManager`、`ensure_config_token` 与 `record` 管道接口。

## 代理使用要点与排障

- 转写完成后把 `.md` 路径告诉用户；长文本先给概要，不要直接刷屏贴全文。
- `yt-dlp` 报 403 / 需登录先 `pip install -U yt-dlp`；`FILE_DOWNLOAD_FAILED` 为签名 URL 过期（2 小时）或 OSS 地域/权限问题，重跑即可。
- 若报 `SERVER_ERROR` 且音频是录音笔/手机录的非标准 mp3（MPEG-2 Layer III），先转码再跑 `audio`：
  `ffmpeg -i in.mp3 -ac 1 -ar 16000 -sample_fmt s16 out.wav`
- 结果 JSON 里每句含 `speaker_id`、`begin_time/end_time`（毫秒）和词级时间戳，需要细粒度分析时读 JSON。
- 转写稿空洞（音频长、转写短）必须在存疑清单标注，不得静默。
- 云端内容审核拒帧/拒段时跳过或本地处理，禁止反复重试（见 [references/video-understanding.md](references/video-understanding.md)）。

## 费用

转写按音频时长计费（`qwen-audio-3.0-asr-flash-filetrans` 约 ¥0.00022/秒量级，53 分钟约几毛钱）；帧分析按次计费，6 帧 ≈ 一次多模态对话；视频理解按采样帧的图片 token 计费（640×360 约 114 token/帧）；OSS 临时存储默认即用即删。
