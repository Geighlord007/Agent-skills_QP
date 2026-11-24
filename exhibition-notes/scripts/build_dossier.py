#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""拼装每场档案 talk_dossier.json（同时支持 Mode A 仅照片 与 Mode B 照片+录音）。

Mode B（照片 + 录音）：
  需要 --agenda + --rec-map + --photo-map + --timeline，按议程顺序汇总每场转写稿与照片。

Mode A（仅照片）：
  传 --mode a（或不传 --rec-map 时自动走 Mode A），直接按 timeline.json 的 session index 聚合照片。
  - 若提供 --agenda（用户确认后的主题列表），优先按条目的 session / sessions 字段绑定场次，
    否则按顺序对应 timeline 场次。
  - 若不提供 --agenda，则直接以 timeline.json 的各场次生成档案（id 为 session_1, session_2, ...）。

输出 talk_dossier.json：每场含 meta + transcripts[] + photos[]（含 stem / compressed / ocr_md）。
后续由子代理读取转写+OCR 提取要点，再由 make_minutes_docx.py 装配成 docx。
"""
import argparse
import datetime as dt
import json
import sys
from collections import defaultdict
from pathlib import Path

for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8", errors="replace")


def fmt_interval(start_iso, end_iso) -> str:
    if not start_iso or not end_iso:
        return ""
    st = dt.datetime.fromisoformat(start_iso).strftime("%H:%M")
    en = dt.datetime.fromisoformat(end_iso).strftime("%H:%M")
    return f"{st}–{en}"


def make_photo_item(p: dict, ocr_dir: Path) -> dict:
    stem = p.get("stem") or Path(p["file"]).stem
    return {
        "file": p["file"],
        "stem": stem,
        "exif": p.get("exif"),
        "compressed": p.get("compressed"),
        "ocr_md": str(ocr_dir / f"{stem}.md"),
    }


def build_mode_b(agenda, rec_map, photo_map, timeline, tr_dir: Path, tr_suffix: str, ocr_dir: Path):
    idx_to_record = {s["index"]: s.get("record") for s in timeline}

    photos_by_talk = defaultdict(list)
    for p in photo_map:
        rec_file = idx_to_record.get(p.get("session"))
        tid = rec_map.get(rec_file) if rec_file else None
        if not tid:
            continue
        photos_by_talk[tid].append(make_photo_item(p, ocr_dir))
    for tid in photos_by_talk:
        photos_by_talk[tid].sort(key=lambda x: x.get("exif") or "")

    tr_by_talk = defaultdict(list)
    for rec_file, tid in rec_map.items():
        stem = Path(rec_file).stem
        md = tr_dir / f"{stem}{tr_suffix}"
        tr_by_talk[tid].append(
            {
                "recording": rec_file,
                "transcript_md": str(md),
                "exists": md.exists(),
                "size": md.stat().st_size if md.exists() else 0,
            }
        )

    dossier = []
    missing_tr = []
    for entry in agenda:
        tid = entry["id"]
        recs = [rf for rf, t in rec_map.items() if t == tid]
        intervals = []
        for rf in recs:
            for s in timeline:
                if s.get("record") == rf and s.get("start"):
                    iv = fmt_interval(s.get("start"), s.get("end"))
                    if iv:
                        intervals.append(iv)
                    break
        trs = tr_by_talk.get(tid, [])
        for t in trs:
            if not t["exists"]:
                missing_tr.append((tid, t["recording"]))
        photos = photos_by_talk.get(tid, [])
        dossier.append(
            {
                "id": tid,
                "agenda_time": entry.get("time", ""),
                "recorded_time": " / ".join(intervals),
                "title": entry.get("title", ""),
                "speaker": entry.get("speaker", ""),
                "affiliation": entry.get("affiliation", ""),
                "transcripts": trs,
                "photos": photos,
                "n_photos": len(photos),
            }
        )
    return dossier, missing_tr


def build_mode_a(agenda, photo_map, timeline, ocr_dir: Path):
    photos_by_session = defaultdict(list)
    for p in photo_map:
        sess_idx = p.get("session")
        if sess_idx is None:
            continue
        photos_by_session[sess_idx].append(make_photo_item(p, ocr_dir))
    for idx in photos_by_session:
        photos_by_session[idx].sort(key=lambda x: x.get("exif") or "")

    sess_by_idx = {s["index"]: s for s in timeline}
    dossier = []

    if agenda:
        for i, entry in enumerate(agenda):
            if "sessions" in entry and isinstance(entry["sessions"], list):
                indices = entry["sessions"]
            elif "session" in entry and entry["session"] is not None:
                indices = [entry["session"]]
            elif i < len(timeline):
                indices = [timeline[i]["index"]]
            else:
                indices = []

            photos = []
            intervals = []
            for idx in indices:
                photos.extend(photos_by_session.get(idx, []))
                s = sess_by_idx.get(idx)
                if s:
                    iv = fmt_interval(s.get("start"), s.get("end"))
                    if iv:
                        intervals.append(iv)
            photos.sort(key=lambda x: x.get("exif") or "")

            dossier.append(
                {
                    "id": entry.get("id", f"session_{i + 1}"),
                    "agenda_time": entry.get("time") or " / ".join(intervals),
                    "recorded_time": "",
                    "title": entry.get("title", f"场次{i + 1}"),
                    "speaker": entry.get("speaker", ""),
                    "affiliation": entry.get("affiliation", ""),
                    "transcripts": [],
                    "photos": photos,
                    "n_photos": len(photos),
                }
            )
    else:
        for s in timeline:
            idx = s["index"]
            photos = photos_by_session.get(idx, [])
            dossier.append(
                {
                    "id": f"session_{idx + 1}",
                    "agenda_time": fmt_interval(s.get("start"), s.get("end")),
                    "recorded_time": "",
                    "title": s.get("label", f"场次{idx + 1}"),
                    "speaker": "",
                    "affiliation": "",
                    "transcripts": [],
                    "photos": photos,
                    "n_photos": len(photos),
                }
            )
    return dossier, []


def main():
    ap = argparse.ArgumentParser(description="拼装每场档案 talk_dossier.json（支持 Mode A / Mode B）")
    ap.add_argument("--mode", choices=["auto", "a", "b"], default="auto", help="模式：auto（默认，有 --rec-map 走 B 否则走 A）、a、b")
    ap.add_argument("--agenda", default="", help="agenda.json（Mode B 必需；Mode A 可选，用于填入确认后的主题结构）")
    ap.add_argument("--rec-map", default="", help="rec_to_talk.json（Mode B 必需）")
    ap.add_argument("--photo-map", required=True, help="photo_session_map.json（scan_media.py 产出）")
    ap.add_argument("--timeline", required=True, help="timeline.json（scan_media.py 产出）")
    ap.add_argument("--transcript-dir", default="record/transcript", help="转写稿目录（Mode B 使用）")
    ap.add_argument("--transcript-suffix", default="_转写.md", help="转写稿后缀（默认 _转写.md）")
    ap.add_argument("--ocr-dir", default="_work/ocr", help="OCR 结果目录（每张图 <stem>.md）")
    ap.add_argument("--out", default="_work/talk_dossier.json", help="输出路径")
    args = ap.parse_args()

    mode = args.mode
    if mode == "auto":
        mode = "b" if args.rec_map else "a"

    photo_map = json.loads(Path(args.photo_map).read_text(encoding="utf-8"))
    timeline = json.loads(Path(args.timeline).read_text(encoding="utf-8"))
    agenda = json.loads(Path(args.agenda).read_text(encoding="utf-8")) if args.agenda else None
    ocr_dir = Path(args.ocr_dir)

    if mode == "b":
        if not args.agenda or not args.rec_map:
            sys.exit("Mode B 必须同时提供 --agenda 和 --rec-map（仅照片请用 --mode a）")
        rec_map = json.loads(Path(args.rec_map).read_text(encoding="utf-8"))
        dossier, missing_tr = build_mode_b(
            agenda, rec_map, photo_map, timeline, Path(args.transcript_dir), args.transcript_suffix, ocr_dir
        )
    else:
        dossier, missing_tr = build_mode_a(agenda, photo_map, timeline, ocr_dir)

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(dossier, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"[build_dossier] 模式={mode.upper()}  写出 {out}  共 {len(dossier)} 场", flush=True)
    for d in dossier:
        print(
            f"  {d['id']:14} {d['agenda_time']:14} spk={d['speaker']}  rec={len(d['transcripts'])} photos={d['n_photos']}",
            flush=True,
        )
    if missing_tr:
        print("[build_dossier] 警告：缺失转写稿：", missing_tr, flush=True)


if __name__ == "__main__":
    main()
