---
name: video-transcribe
description: "视频/直播/在线会议转写、会议纪要与素材收集：B站、YouTube、抖音链接不播放直接转写（yt-dlp 下载音频→百炼 Qwen ASR，说话人分离、中英混合、时间戳），微信视频号/会议/直播用录音转写；会议文件出校对版转写 + 会议纪要 docx（带内容选图的关键画面截图）；视频理解用 qwen3.8 整段直传或自适应抽帧精控，支持内容问答与详细分镜描述；素材收集模式按镜头切分抽帧、Qwen-VL 边界框检测抠出 logo/软件截图/图表并按转写稿时间轴归档成素材包 zip；结果可自动 SMTP 发邮箱。配套同名 Chrome 扩展。Use when 用户要 转写视频/转写链接/B站视频转文字/YouTube字幕/抖音转写/会议记录/会议纪要/直播转写/视频号转写/看懂这个视频/总结视频内容/视频问答/收集视频素材/抠视频里的logo/视频封面文案/插图挑选，或要求转写完发邮箱。"
version: 1.3.0
tags: ["asr", "transcription", "video", "meeting-minutes", "qwen", "dashscope", "oss", "yt-dlp", "vlm", "video-understanding", "asset-harvest", "email", "语音转写", "视频转写", "会议纪要", "素材收集", "画面分析", "视频理解"]
platforms: ["windows", "linux", "macos"]
---

# VideoTranscribe 视频转写与会议纪要

视频链接 / 本地音频 / 本地视频 → 转写稿（Markdown + SRT）→ 会议纪要 docx / 画面分析报告
→ 可选自动发邮箱。音频转写引擎与 [[qwen-asr-transcribe]] 同源；纪要方法论见
[references/meeting-minutes.md](references/meeting-minutes.md)；视频理解路由与平台限制见
[references/video-understanding.md](references/video-understanding.md)。

## 何时使用

- "转写这个 B站/YouTube/抖音视频"、"把这个链接转成文字"、"视频字幕"
- "整理我的会议录像"、"出会议纪要"、"这个会议讲了什么" → 会议管线（校对版转写 + 纪要 docx 带截图）
- "这个视频讲了什么/详细说说视频内容/视频问答" → understand 视频理解
- 微信视频号/直播/在线会议 → 录音转写（URL 模式不可用时兜底）
- "收集视频素材/抠 logo/选插图" → 素材收集模式

不适合：需要实时流式字幕的场景。

## 工作流：先出方案，用户确认后再执行

单文件简单指令（"转写这个链接"）直接执行。**批量整理任务必须分两阶段**：
ASR、校对、纪要、docx 属于重处理，开始前必须拿到用户对方案的确认。

1. **盘点与判定**（本地、低成本）：列媒体文件清单与时长/分辨率；已有转写/帧等中间产物先复用；
   按 references/meeting-minutes.md 第一节做类型判定（会议 / 语音记录 / 游戏与录屏 / 碎片），
   判定依据写入产出物。
2. **出方案**：逐文件列处理计划——类型、产出物（纪要 docx / 校对版 / 内容说明）、输出命名、
   抽帧策略（自适应，见 references/video-understanding.md）、docx 嵌图数量——等用户确认。
3. **确认后执行**：转写 → 校对清洗与纪要（meeting-minutes.md 第二、三节）→ docx 装配
   （第四节）→ 总览索引。原文件永不删除。

## 依赖

- Python 3.10+（标准库可跑；`oss2` 可选；`python-docx` + `Pillow` 仅 docx 装配需要）
- `yt-dlp`（URL 模式）；`ffmpeg`（抽帧/自适应抽帧必需）
- 凭据 `~/.config/video-transcribe/config.json`；存在 `~/.config/qwen-asr/env` 时自动继承
  DASHSCOPE_API_KEY 与 OSS 四件套。首次缺配置向用户索取后 `config` 子命令核对。

## 用法

```bash
# 转写：链接 / 本地音频（默认说话人分离，可自动发邮件）
python {baseDir}/scripts/vtranscribe.py url "https://www.bilibili.com/video/BVxxxx"
python {baseDir}/scripts/vtranscribe.py audio "录音.m4a"

# 会议管线：转写之后，纪要产出按 references/meeting-minutes.md 执行
#   校对清洗 → <会议名>_校对版.md + <会议名>_会议纪要.md → make_meeting_docx.py 装配 docx
python {baseDir}/scripts/make_meeting_docx.py --config meetings.json \
  --minutes-dir <纪要目录> --out-dir <输出目录>

# 视频理解：整段直传（≤2h/≤2GB）/ 自适应抽帧精控
python {baseDir}/scripts/vtranscribe.py understand 录像.mp4
python {baseDir}/scripts/vtranscribe.py understand 录像.mp4 --mode frames --max-frames 16

# 素材收集：场景抽帧 → Qwen-VL bbox 检测 → 抠图归档
python {baseDir}/scripts/vtranscribe.py url "<链接>" --assets

# 截图/帧分析、SMTP 测试、体检
python {baseDir}/scripts/vtranscribe.py analyze 帧1.png 帧2.png --transcript 转写.md
python {baseDir}/scripts/vtranscribe.py email-test
python {baseDir}/scripts/vtranscribe.py status
```

输出落在 `~/VideoTranscribe/out/`；素材收集产出 `assets/` + `素材索引.md` + zip。

## 深入阅读（按需加载）

- [references/meeting-minutes.md](references/meeting-minutes.md)：会议判定标准、转写稿校对清洗
  八步、说话人实名化、纪要结构、docx 排版与内容选图、子代理并行模式。
- [references/video-understanding.md](references/video-understanding.md)：整段直传/帧列表/
  平台抽帧三通道选择、自适应抽帧策略、平台实测限制（data-uri 上限、fps 注解、审核）。

## Chrome 扩展（同一引擎）

本 skill 的 CLI 不依赖任何扩展与服务，可独立运行。另有同名「视频转写助手」Chrome 扩展与
本地伴侣服务（`server/companion.py`，随扩展分发、不在本仓库内）复用同一个 `scripts/engine.py`：
扩展负责浏览器侧提示与截帧，伴侣服务承载任务队列；二者与 CLI 共享配置与引擎，互不干扰。

## 站点能力边界

| 站点 | URL 直接转写 | 说明 |
|---|---|---|
| B站 | ✅ | 普通视频无需登录；会员视频配 cookie |
| YouTube | ✅ | 地区/年龄限制配 cookie |
| 抖音 | ✅ | yt-dlp 支持 |
| 微信视频号 | ❌ | 加密取流，用扩展「录制声音」或本地录音 |
| 视频会议/直播 | 录音 | 扩展 tabCapture 录网页声音后转写 |

## 代理使用要点

- yt-dlp 报 403/需登录先 `pip install -U yt-dlp`；`FILE_DOWNLOAD_FAILED` 是签名 URL 过期，重跑即可。
- 转写稿空洞（音频长、转写短）在纪要存疑清单标注，不得静默。
- 云端内容审核拒帧/拒段时跳过或本地处理，禁止反复重试（见 references/video-understanding.md）。
- 校对清洗、说话人实名化、docx 排版规范与 [[qwen-asr-transcribe]] 保持一致。

## 费用

转写按音频时长计费（qwen-audio-3.0-asr-flash-filetrans 约 ¥0.00022/秒量级）；帧分析按次
计费，6 帧 ≈ 一次多模态对话；视频理解按采样帧的图片 token 计费（640×360 实测约 114
token/帧）；OSS 临时存储即用即删。
