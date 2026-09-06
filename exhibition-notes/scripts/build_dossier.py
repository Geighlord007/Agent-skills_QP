#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把「议程 + 录音↔场次映射 + 照片↔场次映射」拼成每场档案 talk_dossier.json。

输入：
  --agenda       agenda.json   [{id,time,title,speaker,affiliation}, ...]   （主代理从用户给的日程整理）
  --rec-map      rec_to_talk.json  {"<录音文件名>": "<talk id>", ...}        （主代理据时间轴对齐后给出）
  --photo-map    photo_session_map.json   （scan_media.py 产出）
  --timeline     timeline.json            （scan_media.py 产出，用于 session index → 录音文件名）
  --transcript-dir  转写稿目录（默认 record/transcript）
  --transcript-suffix  转写稿后缀（默认 _转写.md，qwen-asr-transcribe 技能的命名）
  --ocr-dir      OCR 结果目录（默认 _work/ocr，每张图 <stem>.md）
  --out          talk_dossier.json

输出 talk_dossier.json：按议程顺序，每场含 meta + transcripts[] + photos[]（带 compressed/ocr_md 路径）。
后续由子代理读取每场的转写+OCR 提取要点，再由 make_minutes_docx.py 装配成 docx。
"""
import argparse
import io
import json
import sys
import datetime as dt
from collections import defaultdict
from pathlib import Path

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")


def main():
    ap = argparse.ArgumentParser(description="拼装每场档案 talk_dossier.json")
    ap.add_argument("--agenda", required=True, help="agenda.json")
    ap.add_argument("--rec-map", required=True, help="rec_to_talk.json")
    ap.add_argument("--photo-map", required=True, help="photo_session_map.json")
    ap.add_argument("--timeline", required=True, help="timeline.json")
    ap.add_argument("--transcript-dir", default="record/transcript")
    ap.add_argument("--transcript-suffix", default="_转写.md")
    ap.add_argument("--ocr-dir", default="_work/ocr")
    ap.add_argument("--tz", type=float, default=8.0, help="录音内嵌 UTC 的本地时区偏移（默认 +8）")
    ap.add_argument("--ffprobe", default="ffprobe")
    ap.add_argument("--out", default="_work/talk_dossier.json")
    args = ap.parse_args()

    agenda = json.loads(Path(args.agenda).read_text(encoding="utf-8"))
    rec_map = json.loads(Path(args.rec_map).read_text(encoding="utf-8"))
    photo_map = json.loads(Path(args.photo_map).read_text(encoding="utf-8"))
    timeline = json.loads(Path(args.timeline).read_text(encoding="utf-8"))

    # session index -> 录音文件名
    idx_to_record = {s["index"]: s.get("record") for s in timeline}
    # 录音文件名 -> talk id
    # 照片按 talk 聚合
    photos_by_talk = defaultdict(list)
    for p in photo_map:
        rec_file = idx_to_record.get(p.get("session"))
        tid = rec_map.get(rec_file) if rec_file else None
        if not tid:
            continue
        photos_by_talk[tid].append({
            "file": p["file"], "exif": p.get("exif"),
            "compressed": p.get("compressed"),
            "ocr_md": str(Path(args.ocr_dir) / f"{p['stem']}.md"),
        })
    for tid in photos_by_talk:
        photos_by_talk[tid].sort(key=lambda x: x.get("exif") or "")

    # 转写稿按 talk 聚合
    tr_by_talk = defaultdict(list)
    tr_dir = Path(args.transcript_dir)
    for rec_file, tid in rec_map.items():
        stem = Path(rec_file).stem
        md = tr_dir / f"{stem}{args.transcript_suffix}"
        tr_by_talk[tid].append({
            "recording": rec_file, "transcript_md": str(md),
            "exists": md.exists(), "size": md.stat().st_size if md.exists() else 0,
        })

    dossier = []
    missing_tr = []
    for entry in agenda:
        tid = entry["id"]
        recs = [rf for rf, t in rec_map.items() if t == tid]
        intervals = []
        for rf in recs:
            # 从 timeline 里取该录音的 start/end（若有）
            for s in timeline:
                if s.get("record") == rf and s.get("start"):
                    st = dt.datetime.fromisoformat(s["start"]).strftime("%H:%M")
                    en = dt.datetime.fromisoformat(s["end"]).strftime("%H:%M")
                    intervals.append(f"{st}–{en}")
                    break
        trs = tr_by_talk.get(tid, [])
        for t in trs:
            if not t["exists"]:
                missing_tr.append((tid, t["recording"]))
        dossier.append({
            "id": tid,
            "agenda_time": entry.get("time", ""),
            "recorded_time": " / ".join(intervals),
            "title": entry.get("title", ""),
            "speaker": entry.get("speaker", ""),
            "affiliation": entry.get("affiliation", ""),
            "transcripts": trs,
            "photos": photos_by_talk.get(tid, []),
            "n_photos": len(photos_by_talk.get(tid, [])),
        })

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(dossier, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"[build_dossier] 写出 {out}  共 {len(dossier)} 场", flush=True)
    for d in dossier:
        print(f"  {d['id']:14} {d['agenda_time']:14} spk={d['speaker']}  rec={len(d['transcripts'])} photos={d['n_photos']}", flush=True)
    if missing_tr:
        print("[build_dossier] ⚠️ 缺失转写稿：", missing_tr, flush=True)


if __name__ == "__main__":
    main()
