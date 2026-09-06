---
name: exhibition-notes
description: 从展会/会议素材生成结构化会议纪要 docx，支持「仅照片」和「照片+录音」两种模式。当用户说"帮我处理展会记录"、"整理会议纪要"、"从照片/录音生成 docx"、"展会纪要"、"会议记录转纪要"时触发。完整流程：扫描建时间轴 → 确认场次 → OCR +（有录音时）ASR 转写 → 子代理并行提取要点 → 专名校正 → 装配 docx（嵌入压缩照片）。
---

# Exhibition Notes - 展会/会议纪要 Skill

把展会/会议的**照片**，或**照片 + 录音**，整理成一份结构化、嵌图的会议纪要 docx。

## 两种模式（自动识别）

- **Mode A · 仅照片**：只有照片文件夹。按照片拍摄时间聚类成场次，OCR 后归纳成纪要。
- **Mode B · 照片 + 录音**：同时有照片和录音。用录音时间轴精确切场，ASR 转写 + OCR 双路对齐，每场由「转写 + 该场 PPT 文字」共同还原，质量最高。

判断方式：素材根目录下有 `record/`（含音频）即 Mode B，否则 Mode A。**第一步永远先跑 `scan_media.py` 扫描**，它会告诉你检测到哪种模式、各场时间与照片数。

## 总原则（最重要）

1. **先扫描建时间轴 → 给用户确认场次划分 → 再开始写。** 不确认不写。把「场次 / 时间 / 录音长度 / 照片数 / 疑似主题」的表给用户点头后再往下。
2. **以素材实际内容为准，不硬套议程。** 议程可能和现场不符（讲者临时换人、某时段实际是圆桌而非白皮书发布）。发现差异就在纪要里如实注明，不假装没看见。
3. **诚实标注边界。** 纪要末尾写明覆盖了哪些场次、哪些没录到（未录的演讲、其他场馆），不夸大覆盖范围。
4. **平实，不浮夸。** 禁用词见文末。是"介绍了/展示了某方向"，不是"该公司引领/突破/重磅/颠覆"。

## 依赖

- **ffprobe / ffmpeg**：读录音时长与内嵌时间戳。
- **Python 包**：`python-docx`、`Pillow`、`requests`（`pip install --user python-docx Pillow requests`）。
- **转写（仅 Mode B）**：用兄弟技能 **`qwen-asr-transcribe`**（阿里云百炼 qwen-audio，带说话人分离）。本技能不重复实现 ASR，直接调用它。
- **OCR**（三选一）：① 兄弟技能 `paddleocr-doc-parsing`；② 本技能自带 `scripts/ocr_aistudio.py`（直连百度 AI Studio 异步接口，**绕过 uvx/MSVC 坑**，推荐 Windows 用）；③ agent 自身视觉读图。

---

## Step 0 · 扫描与时间轴（两种模式都做）

```bash
python scripts/scan_media.py <素材根目录> --photo-dir photo --record-dir record --out _work --tz 8
```

产出 `_work/timeline.json`、`_work/photo_session_map.json`、`_work/compressed/`（压缩图）。

### 时间字段约定（踩过坑，务必遵守）

- **照片时间**：优先 EXIF `DateTimeOriginal`，回退 `DateTime`，再回退文件修改时间。脚本已按此顺序取。**不要用文件系统"创建时间"**——复制/微信传输会把它重置成拷贝时刻。
- **录音时间**：文件详细信息里的"媒体创建日期"= 内嵌 `creation_time`，对很多录音笔而言它是**结束时间**，且常为 **UTC**。所以 `本地结束 = creation_time + 时区偏移`，`开始 = 结束 − 时长`。用 `--tz` 指定偏移（中国 +8）。录音**文件名往往≈开始时间**，可用来交叉验证。
- **空文件剔除**：0 字节 / 损坏文件直接跳过（脚本已处理）。
- **压缩到独立目录，绝不动原图**：PIL 转 RGB + 最大边 `--max-dim`（默认 1024）+ 质量 `--quality`（默认 60）。这一步**同时规避 python-docx 嵌入 iPhone JPEG 丢失关系的 bug**——后面 OCR 和嵌图都用 `compressed/` 里的副本。
- **Mode A 聚类**：无录音时，按 `--gap`（默认 25 分钟）的时间间隔把照片切成场次。

扫描完，把场次表给用户确认，再进入下一步。

---

## Mode A · 仅照片 流程

1. **OCR**：对 `compressed/` 批量 OCR（见 Step「OCR」），每张图得到一段 markdown 文字。
2. **识别主题结构**：派**一个** subagent 读完全部 OCR 文字，**直接输出识别出的主题结构**（不要先写摘要，避免信息损失）。
3. **向用户确认主题结构**：把结构给用户看，**确认后才写**。
4. **并行整理各家/各场详细内容**：subagent 按主代理给的框架整理（见「子代理 JSON 契约」）。
5. **主代理汇总撰写**：主代理负责组装，不让 subagent 决定文档结构。总结在前，各场在后。
6. **装配 docx**：`make_minutes_docx.py`（见 Step「docx 输出」）。

---

## Mode B · 照片 + 录音 流程

### B1 · 时间轴对齐 + 议程映射
- `scan_media.py` 已给出每场（每个录音）的起止与归属照片。
- 若用户提供了**日程/议程**，主代理据此准备两个小 JSON：
  - `agenda.json`：`[{"id":"wujunjun","time":"09:30–09:50","title":"...","speaker":"吴俊俊","affiliation":"江南大学 教授"}, ...]`
  - `rec_to_talk.json`：`{"<录音文件名>":"<talk id>", ...}`（据时间轴把每个录音对上议程的一场；同一场被录成多段的，多个文件名映射到同一 id）
- 没有议程也能做：场次主题留待转写+OCR 后从内容识别，但**公司名/人名会不准**，强烈建议要一份议程。

### B2 · 转写 ∥ OCR（并行）
- **转写**：对 `record/` 每个音频调用 `qwen-asr-transcribe` 技能（开说话人分离）。多文件用并发驱动（ThreadPoolExecutor + subprocess，**capture_output 用 bytes 再 utf-8 decode**，避免 Windows GBK 线程报错）。单文件 ≤2 小时适合 diarization；超长先按时间切段。产物在 `record/transcript/<stem>_转写.md`。
- **OCR**：对 `compressed/` 跑 `ocr_aistudio.py`（或 paddleocr 技能 / 视觉），产物在 `_work/ocr/<stem>.md` + `_manifest.json`（含每张字数）。
- 两者互不依赖，**并行跑**省时间。

```bash
# OCR（AI Studio 异步接口，token 走环境变量或 --token）
AISTUDIO_OCR_TOKEN=xxxx python scripts/ocr_aistudio.py <素材根>/_work/compressed --out <素材根>/_work/ocr --workers 6
```

### B3 · 拼装每场档案
```bash
python scripts/build_dossier.py \
  --agenda agenda.json --rec-map rec_to_talk.json \
  --photo-map <素材根>/_work/photo_session_map.json \
  --timeline <素材根>/_work/timeline.json \
  --transcript-dir <素材根>/record/transcript \
  --ocr-dir <素材根>/_work/ocr \
  --out <素材根>/_work/talk_dossier.json
```
每场档案含：议程 meta + 该场转写稿路径 + 该场照片（compressed/ocr_md 路径）。

### B4 · 子代理并行提取要点（严格 JSON）
- 对每一场派一个 subagent：读它的转写稿 + 该场照片的 OCR 文字，输出**严格 JSON**（见「子代理 JSON 契约」）。
- **金丝雀模式**：先只跑 1 场，确认 schema 与内容质量没问题，再并行铺开其余场次。避免 11 个一起跑结果格式不对要返工。
- 子代理只做"提取"，**不决定文档结构**；结构由主代理定。

### B5 · 专名校正 + 内容核对
- **专名校正**：用**议程（公司名/人名）+ PPT OCR 文字**当词典，校正转写里的同音错字（华谊→华熙、PDI→PDRN、VGF→VEGF、真白印→珍白因、花胶酸→王浆酸、吴浩→吴昊…）。无法确认的标"（推测）"列入存疑清单，**不瞎猜**。
- **内容核对**：比对议程与实际录音/照片。常见差异——讲者换人（议程写 A，现场是 B 代讲）、某时段内容与议程标题不符。以实际为准，在纪要里加注说明。

### B6 · 主代理写总览/观察/范围 + 装配 docx
- 主代理据所有场的提取结果，亲自写 `_overview`（总体概览）、`_closing`（横向观察）、`_scope_note`（记录范围说明），填入 `talk_content.json`。
- ```bash
  python scripts/make_minutes_docx.py \
    --dossier <素材根>/_work/talk_dossier.json \
    --content <素材根>/_work/talk_content.json \
    --manifest <素材根>/_work/ocr/_manifest.json \
    --out <素材根>/展会纪要_<日期>.docx
  ```
- **校验**：用 python-docx 重开 docx，确认段落数、嵌入图片数（应≈ Σmin(6, 每场照片数)）、各场标题与关键短语都在、`word/media/` 里图片文件数与体积合理。

---

## 子代理 JSON 契约

子代理**只输出一个 JSON 对象**，不要任何解释、不要 markdown 代码围栏：

```json
{
  "speaker_note": "string|null",
  "highlights": ["核心亮点，每条≤40字，2-4条"],
  "body":       ["正文要点，普通陈述句，含具体机制/数据/产品名，3-6条"],
  "key_data":   ["数字/专利号/标准/产品代号/分子名，原样保留"],
  "corrections":{"转写错词": "正确写法"}
}
```

- `speaker_note`：转写/OCR 能确认或修正讲者姓名时填，否则 `null`。
- 语言平实，禁用浮夸词（见文末）；专有名词以议程和 PPT(OCR) 写法为准。
- 某项无内容用 `[]` 或 `{}`。

## 议程的作用与格式

议程是 Mode B 的"骨架 + 校正词典"，决定场次命名、讲者实名化、专名校正。主代理从用户给的日程（docx/文本/图片）整理成：

`agenda.json`
```json
[
  {"id":"wujunjun","time":"09:30–09:50","title":"超分子弹性蛋白...","speaker":"吴俊俊","affiliation":"江南大学 教授"},
  {"id":"wangruiyan","time":"09:50–10:10","title":"...","speaker":"王瑞妍","affiliation":"华熙生物 副总裁"}
]
```
`rec_to_talk.json`
```json
{
  "江南大学弹性蛋白.m4a":"wujunjun",
  "华熙生物 1.m4a":"wangruiyan", "华熙生物 2.m4a":"wangruiyan", "华熙生物 3.m4a":"wangruiyan",
  "2026年09月04日 10点10分.m4a":"gulihao"
}
```

---

## docx 输出标准

**结构（总-分-总）：**
```
标题 / 副标题 / 日期
总体概览（_overview，跨场共性趋势，编号或分段）
各场记录（按议程时间）
  ├─ HH:MM–HH:MM  演讲标题
  │   ├─ 讲者 · 机构（斜体）
  │   ├─ 核心亮点（• 条目）
  │   ├─ 正文要点
  │   ├─ 关键数据 / 专利
  │   └─ 嵌入照片 ≤6 张
  └─ ...
横向观察（_closing）
记录范围说明（_scope_note）
```

**排版：** 低饱和配色（默认青灰 `#2F5D62`）、微软雅黑 + Calibri、页眉页脚 + 页码、A4。`make_minutes_docx.py` 已内置。

**照片选择：** 每场按 OCR 文字量（`_manifest.json` 的 chars）取信息最丰富的 top N（默认 6），再按拍摄时间排序展示——优先嵌数据页/结构图，跳过近空白页。

**语言风格：** 平实，不浮夸；层次清晰，每点一意。

---

## 已知坑（血泪总结）

1. **时间字段别搞错**：照片用 EXIF 不用文件创建时间；录音"媒体创建日期"= 结束时间且常为 UTC，开始 = 结束 − 时长，+时区偏移。详见 Step 0。
2. **空文件先剔除**：0 字节照片会让 PIL/OCR 报错，扫描时跳过。
3. **python-docx 嵌入 iPhone JPEG 丢关系**：必须先用 PIL `convert('RGB').save(jpeg)` 重存再嵌。`scan_media.py` 的压缩步骤已顺带解决——**始终嵌 `compressed/` 的副本**。
4. **OCR 通路 — uvx/MSVC 坑**：`paddleocr-doc-parsing` 的 MCP 服务器用 `uvx` 冷启动时，在缺 Microsoft Visual C++ Build Tools 的 Windows 上会因源码编译 pyyaml 失败。**改用 `ocr_aistudio.py`（只需 requests）或 pip 装好的入口或 agent 视觉**。另外 `layout_caller.py` 失败时退出码可能被管道吞掉看似成功，**必须读返回 JSON 的 `ok` 字段**判断成败。
5. **Windows 控制台 GBK**：脚本打印 CJK / `•` / 替换字符 `\ufffd` 会 `UnicodeEncodeError` 崩溃（曾让整个批处理在打印阶段挂掉，但实际工作已完成）。**所有脚本开头强制 UTF-8 stdout**：
   ```python
   import io, sys
   if sys.platform == "win32":
       sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
       sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
   ```
   调外部脚本（如 transcribe.py）时用 `capture_output=True, text=False` 再 `.decode("utf-8","replace")`，别用 `text=True`。
6. **子代理输出要严约束**：明确要求"只输出 JSON、无围栏"，否则个别子代理会加前言导致解析失败；主代理解析时兜底取第一个 `{...}` 块。先跑 1 场金丝雀验证 schema。
7. **专名校正要有词典**：ASR 必错小众品牌/人名/专利号。用议程 + PPT OCR 当真理源逐场校正；拿不准的标"（推测）"进存疑清单，绝不编造。
8. **议程 ≠ 实际**：讲者可能换人、环节内容可能与标题不符。以录音/照片实际内容为准并加注，不硬套议程。
9. **subagent 别让它决定结构**：子代理只提取/整理单场内容，文档结构与汇总由主代理负责。
10. **markdown 污染**：子代理正文不要带 `##` 等符号；docx 装配层也只做纯文本段落。

**禁用词**：颠覆、重磅、突破、领先、引领、攻克、赋能未来、战略高地、竞争壁垒、战略物资、重担。用"介绍/展示/提出/探索了某方向"替代。

---

## 脚本清单

| 脚本 | 作用 |
|---|---|
| `scripts/scan_media.py` | 扫描 photo/+record/，建时间轴 + 照片↔场次映射，压缩照片到 compressed/（Mode A/B 通用，第一步必跑） |
| `scripts/ocr_aistudio.py` | 百度 AI Studio 异步 OCR 批处理（绕过 uvx/MSVC 坑），输出 ocr/<stem>.md + _manifest.json |
| `scripts/build_dossier.py` | 议程 + 录音↔场次 + 照片↔场次 → talk_dossier.json（Mode B） |
| `scripts/make_minutes_docx.py` | talk_dossier.json + talk_content.json → 纪要 docx（总-分-总、嵌图、页眉页脚页码） |
| `scripts/compress_images.py` | （旧）单独压缩大图，已被 scan_media.py 的压缩步骤取代 |
| `scripts/make_docx.py` | （旧）简易公司章节 docx 生成器 |

**典型 Mode B 命令链：**
```bash
ROOT=/path/to/展会素材
python scripts/scan_media.py $ROOT --tz 8                       # 1. 扫描+时间轴+压缩 → 给用户确认
# （用户确认场次；主代理准备 agenda.json + rec_to_talk.json）
AISTUDIO_OCR_TOKEN=xx python scripts/ocr_aistudio.py $ROOT/_work/compressed --out $ROOT/_work/ocr &  # 2a. OCR
# 2b. 同时对每个录音调用 qwen-asr-transcribe 技能（并发）
python scripts/build_dossier.py --agenda agenda.json --rec-map rec_to_talk.json \
       --photo-map $ROOT/_work/photo_session_map.json --timeline $ROOT/_work/timeline.json \
       --transcript-dir $ROOT/record/transcript --ocr-dir $ROOT/_work/ocr --out $ROOT/_work/talk_dossier.json  # 3. 拼档案
# 4. 子代理并行提取（先金丝雀 1 场）→ 主代理写 talk_content.json（含 _overview/_closing/_scope_note）
python scripts/make_minutes_docx.py --dossier $ROOT/_work/talk_dossier.json \
       --content $ROOT/_work/talk_content.json --manifest $ROOT/_work/ocr/_manifest.json \
       --out $ROOT/展会纪要.docx                                  # 5. 装配 docx + 校验
```
