# 展会纪要生成 · 详细工作流

本文是 `SKILL.md` 的操作细则。两种模式：**A 仅照片** / **B 照片+录音**（有 `record/` 即 B）。

## 0. 扫描建时间轴（必做，第一步）

```bash
python scripts/scan_media.py <素材根> --photo-dir photo --record-dir record --out _work --tz 8
```

- 产出 `_work/timeline.json`、`_work/photo_session_map.json`、`_work/compressed/`。
- 自动识别模式；打印每场「时间 / 录音时长 / 照片数」。
- **把这张表给用户确认后再继续。** 不确认不写。

时间字段铁律：
- 照片 = EXIF `DateTimeOriginal`（回退修改时间），**不用文件创建时间**。
- 录音"媒体创建日期" = 内嵌 `creation_time` = **结束时间**，常为 **UTC** → 本地结束 = +`--tz`，开始 = 结束 − 时长。文件名常≈开始时间，可交叉验证。
- 0 字节文件自动剔除；照片压缩到 `compressed/`（PIL RGB / 1024px / q60），**不改原图**，且顺带修复 python-docx 的 JPEG 嵌入 bug。

## A. 仅照片

1. OCR `compressed/`（`ocr_aistudio.py` 或 paddleocr 技能或视觉）→ `_work/ocr/<stem>.md`。
2. 一个 subagent 读全部 OCR 文字 → **直接输出主题结构**（不先写摘要）。
3. 主题结构给用户确认。
4. subagent 按主代理给的框架并行整理各场内容（严格 JSON，见 SKILL.md 契约）。
5. 主代理汇总：总结在前，各场在后。
6. `make_minutes_docx.py` 装配 + 校验。

## B. 照片 + 录音

### B1 对齐 + 议程
- 时间轴已由 scan_media 给出。
- 有议程 → 主代理写 `agenda.json`（每场 id/time/title/speaker/affiliation）+ `rec_to_talk.json`（录音文件名→talk id；同一场多段录音映射同一 id）。
- 无议程 → 主题留待转写+OCR 后识别（公司名/人名会不准，尽量要议程）。

### B2 转写 ∥ OCR
- 转写：每个音频调 `qwen-asr-transcribe` 技能（说话人分离）。并发驱动时 `subprocess.run(..., capture_output=True, text=False)` 再 `.decode("utf-8","replace")`，**别用 text=True**（Windows GBK 线程报错）。产物 `record/transcript/<stem>_转写.md`。
- OCR：`AISTUDIO_OCR_TOKEN=xx python scripts/ocr_aistudio.py <根>/_work/compressed --out <根>/_work/ocr --workers 6`。产物 `_work/ocr/<stem>.md` + `_manifest.json`。
- 两路并行。

### B3 拼档案
```bash
python scripts/build_dossier.py --agenda agenda.json --rec-map rec_to_talk.json \
  --photo-map <根>/_work/photo_session_map.json --timeline <根>/_work/timeline.json \
  --transcript-dir <根>/record/transcript --ocr-dir <根>/_work/ocr --out <根>/_work/talk_dossier.json
```

### B4 子代理提取（金丝雀先行）
- 每场一个 subagent，读其转写 + 该场照片 OCR，输出严格 JSON（highlights/body/key_data/corrections/speaker_note，无围栏）。
- **先跑 1 场**验证 schema 与质量，再并行铺开其余。

### B5 专名校正 + 内容核对
- 词典 = 议程（公司/人名）+ PPT OCR。逐场校正 ASR 同音错字；拿不准标"（推测）"进存疑清单，不编造。
- 比对议程与实际：讲者换人、环节内容与标题不符等，以实际为准并加注。

### B6 总览 + 装配 + 校验
- 主代理亲自写 `_overview` / `_closing` / `_scope_note` 填入 `talk_content.json`。
- ```bash
  python scripts/make_minutes_docx.py --dossier <根>/_work/talk_dossier.json \
    --content <根>/_work/talk_content.json --manifest <根>/_work/ocr/_manifest.json --out <根>/展会纪要.docx
  ```
- 校验：python-docx 重开，查段落数、嵌入图数（≈ Σmin(6, 每场照片数)）、各场标题与关键短语、`word/media/` 图片数与体积。

## 已知坑速查

1. 时间字段：照片用 EXIF；录音媒体创建日期=结束+UTC，+tz，开始=结束−时长。
2. 空文件剔除。
3. 嵌图用 `compressed/` 副本（PIL RGB 重存），规避 python-docx JPEG bug。
4. OCR：uvx 在缺 MSVC 的 Windows 上编译 pyyaml 失败 → 用 `ocr_aistudio.py`/pip 入口/视觉；`layout_caller` 成败看 JSON `ok` 字段别看退出码。
5. Windows GBK：脚本开头强制 UTF-8 stdout；调外部脚本用 bytes+utf-8 decode。
6. 子代理严约束 JSON + 金丝雀先跑 1 场；解析兜底取首个 `{...}`。
7. 专名校正靠议程+OCR 词典，不确定标"（推测）"。
8. 议程≠实际，以素材为准并加注。
9. 子代理不决定文档结构，主代理汇总。
10. 正文不带 `##` 等 markdown 符号。

禁用词：颠覆/重磅/突破/领先/引领/攻克/赋能未来/战略高地/竞争壁垒/战略物资/重担。
