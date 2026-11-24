---
name: exhibition-notes
description: 从展会/会议现场素材生成结构化嵌图会议纪要 docx，支持「仅照片（Mode A）」和「照片+录音（Mode B）」两种模式。当用户要求处理展会记录、整理会议纪要、从现场照片/录音生成纪要 docx 时触发。不用于通用 Word 文档编辑（用 docx）、纯音频转写（用 qwen-transcribe）或通用文档解析（用 paddleocr-doc-parsing）。
---

# Exhibition Notes - 展会/会议纪要流水线

把展会/会议的**现场照片**（Mode A）或**照片 + 录音**（Mode B）按时间轴对齐，完成 OCR / ASR、子代理结构化提取与专名校正，最终装配成总-分-总、嵌图排版规范的 docx。

## 两种模式与总原则

- **Mode A · 仅照片**：素材根目录无 `record/` 音频时自动启用。按拍摄时间间隔聚类成场次，OCR 后归类整理。
- **Mode B · 照片 + 录音**：有 `record/` 音频时自动启用。用录音时间轴精确切场，ASR + OCR 双路对齐，质量最高。

**总原则（铁律）：**
1. **先扫描确认再写作**：永远先跑 `scan_media.py`，将「场次 / 时间 / 时长 / 照片数 / 疑似主题」表发给用户确认后再继续。
2. **以现场实际为准**：议程可能与现场不符（讲者换人、议题变更），以录音和照片实际内容为准并在纪要中如实加注。
3. **诚实标注覆盖边界**：末尾在 `_scope_note` 说明覆盖了哪些场次、哪些未录到，不夸大。
4. **文风平实，禁用浮夸词**：禁用「颠覆、重磅、突破、领先、引领、攻克、赋能未来、战略高地、竞争壁垒、战略物资、重担」，改用「介绍/展示/提出/探索了某方向」。

## 依赖与兄弟技能边界

- **ffprobe / ffmpeg**：读取录音时长与内嵌时间戳（需在 PATH 中，或用 `--ffprobe` 指定）。
- **Python 包**：`pip install --user python-docx Pillow requests`。
- **转写（仅 Mode B）**：委派兄弟技能 `qwen-transcribe`（`qtranscribe.py audio`，带说话人分离），本技能不重复实现 ASR。
- **OCR（三选一）**：
  1. `scripts/ocr_aistudio.py`：直连百度 AI Studio 异步 HTTP 接口（仅依赖 `requests`），**Windows 缺 MSVC Build Tools 导致 `uvx` 编译 `pyyaml` 失败时的推荐方案**，内置断点续传。
  2. 兄弟技能 `paddleocr-doc-parsing`（环境就绪时适用）。
  3. Agent 自身视觉读图（照片极少时适用）。
- **docx 生成**：本技能用 `make_minutes_docx.py` 装配固定版式的展会纪要；通用 Word 文档修改请用 `docx` 技能。

---

## Step 0 · 扫描建时间轴与压缩（Mode A/B 通用）

```powershell
python scripts/scan_media.py "<素材根目录>" --photo-dir photo --record-dir record --out _work --tz 8
```

产出 `_work/timeline.json`、`_work/photo_session_map.json`、`_work/compressed/`（压缩副本）。

- **时间口径**：照片优先 EXIF `DateTimeOriginal` → `DateTime` → 文件 `mtime`（不用会被微信/拷贝重置的文件创建时间）；录音内嵌 `creation_time` 通常为结束时间，脚本已自动统一归一化到 UTC 再加 `--tz`（避免含 `+08:00` 偏移时重复叠加），`开始 = 结束 − 时长`。
- **绝不动原图**：自动跳过 0 字节文件；压缩时先执行 `ImageOps.exif_transpose` 校正竖拍方向，再转 RGB、缩放最大边（默认 1024）存为 JPEG（同时规避 `python-docx` 嵌入 iPhone JPEG 丢关系的 bug）。后续 OCR 与嵌图一律使用 `compressed/`。
- **边界参数**：Mode A 按 `--gap`（默认 25 分钟）切场；Mode B 对落于录音区间外的照片按 `--max-photo-gap`（默认 15 分钟）吸附，超距照片置为未归属（`session: null`）供人工确认。

扫描完成后，把场次表给用户确认再进入 Mode A 或 Mode B。

---

## Mode A · 仅照片流程

1. **批量 OCR**：对 `_work/compressed/` 跑 OCR（见下文 OCR 命令），产出 `_work/ocr/<stem>.md` 与 `_manifest.json`。
2. **识别主题结构**：派**一个** subagent 读完全部 OCR 文字，直接输出建议的主题/场次结构（不要先摘要，避免丢失细节）。
3. **向用户确认结构**：确认后将主题列表整理为 `agenda.json`（可选带 `"session": 0` 或 `"sessions": [0, 1]` 绑定 `timeline.json` 的场次索引；不提供 `agenda.json` 时按 `timeline.json` 原场次生成）。
4. **拼装档案**：
   ```powershell
   python scripts/build_dossier.py --mode a `
     --photo-map "<素材根>/_work/photo_session_map.json" `
     --timeline "<素材根>/_work/timeline.json" `
     --ocr-dir "<素材根>/_work/ocr" `
     --agenda "<素材根>/_work/agenda.json" `
     --out "<素材根>/_work/talk_dossier.json"
   ```
5. **并行提取 + 汇总 + 装配 docx**：与 Mode B 的 B4 → B6 相同（无转写稿，仅基于 OCR 提取）。

---

## Mode B · 照片 + 录音流程

### B1 · 议程映射
若用户提供日程，整理两个小 JSON（无议程也可做，但人名/公司名准确率下降，建议索要）：

- `agenda.json`：
  ```json
  [
    {"id":"wujunjun","time":"09:30–09:50","title":"超分子弹性蛋白...","speaker":"吴俊俊","affiliation":"江南大学 教授"}
  ]
  ```
- `rec_to_talk.json`（多段录音可映射到同一 `id`）：
  ```json
  {"江南大学弹性蛋白.m4a":"wujunjun","华熙生物 1.m4a":"wangruiyan","华熙生物 2.m4a":"wangruiyan"}
  ```

### B2 · 转写 ∥ OCR（并行）
两者互不依赖，建议分两个终端或并行任务同时执行：

- **转写**：对 `record/` 各音频调用 `qwen-transcribe`（`qtranscribe.py audio`，默认开说话人分离；单文件 ≤2 小时为宜，超长先切段），默认产物在 `record/transcript/<stem>_转写.md`。并发调用外部脚本时用 `capture_output=True, text=False` 再 `.decode("utf-8", "replace")`，避免 Windows GBK 报错。
- **OCR**：运行 `ocr_aistudio.py`（默认跳过已有非空 `<stem>.md` 实现断点续传，传 `--force` 强制重跑）：
  ```powershell
  # PowerShell（Bash 下改用 export AISTUDIO_OCR_TOKEN="..." 或直接传 --token）
  $env:AISTUDIO_OCR_TOKEN = "<your-token>"
  python scripts/ocr_aistudio.py "<素材根>/_work/compressed" --out "<素材根>/_work/ocr" --workers 6
  ```

### B3 · 拼装每场档案
```powershell
python scripts/build_dossier.py --mode b `
  --agenda "<素材根>/_work/agenda.json" `
  --rec-map "<素材根>/_work/rec_to_talk.json" `
  --photo-map "<素材根>/_work/photo_session_map.json" `
  --timeline "<素材根>/_work/timeline.json" `
  --transcript-dir "<素材根>/record/transcript" `
  --ocr-dir "<素材根>/_work/ocr" `
  --out "<素材根>/_work/talk_dossier.json"
```

### B4 · 子代理并行提取要点（金丝雀 + 严格 JSON）
每场派一个 subagent 读该场转写稿 + 照片 OCR，**只输出一个 JSON 对象（不要解释、不要 markdown 代码围栏、正文不要带 `##` 等符号）**：

```json
{
  "speaker_note": "string|null",
  "highlights": ["核心亮点，每条≤40字，2-4条"],
  "body":       ["正文要点，平实陈述句，含具体机制/数据/产品名，3-6条"],
  "key_data":   ["数字/专利号/标准/产品代号/分子名，原样保留"],
  "corrections":{"转写错词": "正确写法"}
}
```

- **金丝雀模式**：先只跑 1 场验证 schema 与质量，再并行铺开其余场次。
- 子代理只做单场提取，不决定文档结构；主代理解析时兜底截取首个 `{...}` 块。

### B5 · 专名校正与内容核对
用**议程（人名/机构名）+ PPT OCR** 作为真理源，校正 ASR 同音错字（如华谊→华熙、PDI→PDRN、VGF→VEGF）。无法确认的标「（推测）」并列入存疑清单，绝不编造。发现讲者或议题与议程不符时，在 `speaker_note` / 正文中如实说明。

### B6 · 主代理写总览并装配 docx
主代理汇总所有场次，编写 `_title`、`_subtitle`、`_date`、`_header`、`_overview`（总体概览）、`_closing`（横向观察）、`_scope_note`（记录范围说明），连同各 `<talk_id>` 内容写入 `talk_content.json`，再生成 docx：

```powershell
python scripts/make_minutes_docx.py `
  --dossier "<素材根>/_work/talk_dossier.json" `
  --content "<素材根>/_work/talk_content.json" `
  --manifest "<素材根>/_work/ocr/_manifest.json" `
  --out "<素材根>/展会纪要_<日期>.docx"
```

- **版式与选图**：总-分-总结构、低饱和青灰 `#2F5D62`、微软雅黑 + Calibri、A4 + 页眉页码。`--manifest` 按 `stem`（忽略扩展名与大小写）取每场 OCR 字数最多的前 N 张（默认 6），再按拍摄时间排序嵌入。
- **交付校验**：用 `python-docx` 重开产出文件，确认段落数、嵌入图片数（≈ `Σmin(6, 每场照片数)`）、各场标题与 `word/media/` 图片体积正常。

---

## 常见故障速查

- **Windows 控制台 `UnicodeEncodeError`**：本技能 4 个核心脚本开头均已强制 UTF-8 `stdout/stderr`；自定义包装脚本时也务必保留同样处理。
- **`paddleocr-doc-parsing` 报错或静默失败**：缺 MSVC 编译 `pyyaml` 时改用 `scripts/ocr_aistudio.py`；若使用 `layout_caller.py`，务必检查返回 JSON 的 `ok` 字段而非仅看退出码。

## 脚本清单

| 脚本 | 作用 |
|---|---|
| `scripts/scan_media.py` | 扫描 `photo/` + `record/`，建时间轴与照片归属，EXIF 纠偏并压缩到 `compressed/`（Mode A/B 第一步） |
| `scripts/ocr_aistudio.py` | 百度 AI Studio 异步 OCR 批处理（仅需 `requests`，支持断点续传），输出 `<stem>.md` + `_manifest.json` |
| `scripts/build_dossier.py` | 拼装每场档案 `talk_dossier.json`（支持 `--mode a` / `--mode b` / `auto`） |
| `scripts/make_minutes_docx.py` | `talk_dossier.json` + `talk_content.json` → 总-分-总嵌图纪要 docx |
