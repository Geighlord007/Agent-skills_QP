# video-transcribe

[ZCode/Agent Skills](https://agentskills.io) 格式的视频转写与理解 skill：把视频链接、本地音频、
本地视频整理成转写稿、会议纪要 docx（带关键画面截图）、画面分析报告与素材包。

## 能力

- **转写**：B站 / YouTube / 抖音链接不播放直接转写（yt-dlp 下载音频 → 百炼 Qwen ASR，
  说话人分离、中英混合、句级时间戳）；微信视频号/会议/直播走录音兜底。
- **会议纪要**：ASR 原稿 → 结构冻结式校对清洗（专名统一、去冗、删幻听、说话人实名化）
  → 会议纪要（议题分节 + 结论行动项 + 存疑清单）→ 带关键画面截图的 docx。
- **视频理解**：qwen3.8 整段直传（≤2h/≤2GB）或自适应抽帧（一半均匀覆盖 + 一半场景切换点）
  帧列表精控，支持内容问答与秒级分镜描述。
- **素材收集**：镜头切分抽帧 → Qwen-VL 边界框检测 → 抠出 logo/截图/图表 → 按转写稿时间轴
  归档成素材包 zip。

## 安装

复制到 agent 的 skills 目录（如 `~/.agents/skills/video-transcribe`），依赖：

- Python 3.10+（标准库可跑核心；`oss2`、`python-docx`、`Pillow` 按需）
- `yt-dlp`（URL 模式）、`ffmpeg`（抽帧必需）
- 阿里云百炼 `DASHSCOPE_API_KEY`（视频理解/纪要需要 qwen3.8 访问权限）与 OSS 四件套
  （转写文件中转），写入 `~/.config/video-transcribe/config.json` 或
  `~/.config/qwen-asr/env`

## 使用

```bash
# 转写链接 / 本地音频
python scripts/vtranscribe.py url "https://www.bilibili.com/video/BVxxxx"
python scripts/vtranscribe.py audio "录音.m4a"

# 视频理解（整段直传 / 自适应抽帧）
python scripts/vtranscribe.py understand 录像.mp4

# 会议纪要 docx 装配（纪要 md 由 agent 按校对流程产出）
python scripts/make_meeting_docx.py --config meetings.json \
  --minutes-dir <纪要目录> --out-dir <输出目录>

# 素材收集 / 状态体检
python scripts/vtranscribe.py url "<链接>" --assets
python scripts/vtranscribe.py status
```

agent 侧的完整工作流（含"先出方案、用户确认后执行"的批量整理流程）见
[SKILL.md](SKILL.md)；会议纪要方法论见
[references/meeting-minutes.md](references/meeting-minutes.md)；
视频理解路由与平台实测限制见
[references/video-understanding.md](references/video-understanding.md)。

## 文件结构

```
video-transcribe/
├── SKILL.md                          # agent 入口：路由、工作流、快速用法
├── references/
│   ├── meeting-minutes.md            # 会议判定、校对清洗八步、纪要结构、docx 规范
│   └── video-understanding.md        # 三通道选择、混合抽帧、平台实测限制
└── scripts/
    ├── engine.py                     # 共享引擎：ASR/OSS/抽帧/去重/视频理解/自适应策略
    ├── vtranscribe.py                # CLI：url / audio / analyze / understand / status
    └── make_meeting_docx.py          # 会议纪要 md → 带截图 docx
```

## 平台与费用

视频理解走阿里云百炼（qwen3.8-flash 默认）；转写按音频时长计费
（qwen-audio-3.0-asr-flash-filetrans 约 ¥0.00022/秒量级）；帧分析按图片 token 计费。
云端审核会拒绝部分敏感画面——跳过或本地处理，不要反复重试（详见 references）。
