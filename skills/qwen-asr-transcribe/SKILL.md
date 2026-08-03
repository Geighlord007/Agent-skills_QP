---
name: qwen-asr-transcribe
description: "用阿里云百炼 Qwen ASR 转写会议/长音频：本地文件自动上传 OSS 生成签名 URL，调用 qwen-audio-3.0-asr-flash-filetrans 异步转写，支持说话人分离、中英混合、句级时间戳，输出 Markdown 纪要 + SRT 字幕，并含 LLM 校对清洗流程（专名统一、去语气词、删幻听重复）。Use when the user wants to transcribe 录音/会议/访谈/播客 audio files (mp3/wav/m4a), especially multi-speaker meetings (区分说话人/会议纪要/语音转文字/校对转写稿)."
version: 1.2.0
tags: ["asr", "transcription", "qwen", "dashscope", "aliyun", "oss", "diarization", "meeting", "语音转写", "会议纪要"]
platforms: ["linux", "macos"]
---

# Qwen ASR 会议转写

把本地长音频转成带说话人标注的转写稿。单文件 ≤2GB / ≤12 小时（开说话人分离建议 ≤2 小时、单声道）。

## 何时使用

- "转写这个录音 / 会议 / 访谈"、"语音转文字"、"会议纪要"、"区分说话人"
- 多人会议需要 `说话人N` 标注 + 时间戳
- 中英混合音频

不适合：需要实时流式转写的场景。

## 依赖

- Python 包：`oss2`（`pip install --user oss2`）
- 凭据配置文件 `~/.config/qwen-asr/env`（权限 600，每行 `KEY=VALUE`）：

```
DASHSCOPE_API_KEY=sk-...
DASHSCOPE_WORKSPACE_ID=llm-xxxx        # 可选，工作空间级 key 建议填
OSS_ACCESS_KEY_ID=...
OSS_ACCESS_KEY_SECRET=...
OSS_BUCKET=...
OSS_ENDPOINT=https://oss-cn-beijing.aliyuncs.com   # 可选
```

环境变量优先于配置文件。首次使用若缺配置，向用户索取后写入该文件。

## 用法

```bash
python3 {baseDir}/scripts/transcribe.py <音频文件> [-o 输出目录] [--no-diarize] [--language-hints zh,en] [--keep-oss]
```

- 默认输出到 `<音频目录>/transcript/`：`原名_转写.md`、`原名_转写.srt`、`原名_transcription.json`
- 默认开说话人分离；转写完自动删除 OSS 上的临时音频（`--keep-oss` 保留）
- 53 分钟音频实测云端约 2 分钟完成；脚本前台运行即可，长音频可加 `&` 或后台任务

## 代理使用要点

- 转写完成后把 `.md` 路径告诉用户；长文本不要直接贴全文，先给概要
- 用户若反馈专名识别错误多，可在转写后加一道 LLM 校对（见下节）
- 若任务报 `FILE_DOWNLOAD_FAILED`：签名 URL 失效（2 小时）或 OSS 地域/权限不对，重新跑即可（脚本每次新签名）
- 若报 `SERVER_ERROR` 且音频是录音笔/手机录的非标准 mp3（MPEG-2 Layer III），先转码：
  `ffmpeg -i in.mp3 -ac 1 -ar 16000 -sample_fmt s16 out.wav`
- 结果 JSON 里每句含 `speaker_id`、`begin_time/end_time`（毫秒）和词级时间戳，需要更细粒度分析时读 JSON

## 校对清洗（推荐的标准后续步骤）

ASR 原稿常见四类问题：专名拼错（小众品牌/人名最突出）、语气词和口吃、大小写混乱、偶发整句重复幻听。用户要求"校对/清洗/ polish 稿子"时，按以下流程做 LLM 校对（长稿可派子代理执行）：

1. **结构冻结**：`**[HH:MM:SS] 说话人N：**` 块的时间戳、编号、顺序一律不动，逐块处理，完工后用 diff 校验块序列与源稿一致。
2. **输出新文件**：`<原名>_校对版.md`，保留原稿不覆盖。
3. **专名统一**：先把议程/背景信息（主办方、嘉宾、品牌）列成对照表再逐块替换。同稿异拼是典型信号（如一个品牌出现 prada/Proto/Protuc 三种写法）。无法确认的专名**保留原文**，在校对报告中列为存疑项，不瞎猜。
4. **去冗**：删孤立 uh/um/er、修口吃重复（the the 等），保留口语风格和原意，不改写句子。
5. **修标点大小写**：英文里的中文句号「。」改回 `.`，句首大写，i→I，品牌按官方大小写（PepsiCo、GLP-1、Euromonitor 等）。
6. **删幻听**：整句/整段原文重复的（模型 artifact）删到只剩一遍，保持上下文连贯。
7. **说话人实名化**（多人会议必做）：ASR 只给 `说话人N` 编号，要从内容识别真实身份——优先自我介绍（"my name is..."）、主持人串场提名、互相称呼。确认后把所有 `说话人N：**` 标签替换为 `姓名 (机构)：**`，并在文件头部元信息加人名对照表。无法确认的保留角色名（如「主持人」）或原编号，不要瞎编姓名；纯属发音猜测的姓要列入存疑清单。
8. **收尾报告**：改动统计、专名对照表、存疑清单（用户按现场记忆核对）。

也可在校对后追加：中文要点总结、按嘉宾分段的观点提炼——需用户明确要求再做。

## 导出 docx 的排版要点

用户要 Word 版转写稿时（用 docx skill 的 C# 工具链生成，禁止 pandoc）：

- 每个发言块的第一段：加粗 + 主色的 `[时间] 姓名：` 标签 + 正文
- **长发言块必须拆段**：在句末标点（. ! ?）+ 空格 + 大写字母处切句，贪心组段每段约 2–4 句 / 250–350 字符，绝不切断句子；延续段不加标签、左缩进 ~360 twips 表示归属。整轮发言一段到底的排版用户明确反馈过难读
- 短块（1–2 句）保持单段
- 页眉页脚 + 页码；低饱和配色；文件按主题命名，不留 v1/v2 迭代垃圾

## 费用

按音频时长计费（qwen-audio-3.0-asr-flash-filetrans 约 ¥0.00022/秒量级，以百炼定价页为准），53 分钟约几毛钱；OSS 存储几分钱且默认即用即删。
