#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""扫描展会素材文件夹，建立时间轴 + 照片↔场次映射，并压缩照片。

支持两种模式（自动识别）：
  Mode B（照片 + 录音）：有 record/ 音频时，用「录音结束时间 = 媒体创建日期」还原每场起止，
                        再把每张照片按拍摄时间落入对应场次。
  Mode A（仅照片）：无录音时，按照片拍摄时间的间隔聚类成场次。

关键约定（踩过坑）：
  - 照片时间优先取 EXIF DateTimeOriginal，回退 DateTime，再回退文件修改时间。
  - 录音内嵌 creation_time 通常是 UTC，且对很多录音笔而言它是【结束】时间；
    开始时间 = 结束 − 时长。用 --tz 指定本地时区偏移（默认 +8）。
  - 0 字节 / 损坏文件直接剔除。
  - 照片压缩到独立目录（绝不改原图）：PIL 转 RGB + 最大边 --max-dim + 质量 --quality，
    这一步同时规避 python-docx 嵌入 iPhone JPEG 丢失关系的 bug。

输出（写入 --out 目录）：
  timeline.json          场次列表 [{index,label,start,end,record,n_photos}]
  photo_session_map.json 照片列表 [{file,stem,exif,compressed,compressed_bytes,session}]
  compressed/            压缩后的照片（供 OCR 与 docx 嵌入）
"""
import argparse
import datetime as dt
import io
import json
import os
import subprocess
import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

IMG_EXT = {".jpg", ".jpeg", ".png", ".webp"}
AUD_EXT = {".m4a", ".mp3", ".wav", ".aac", ".flac", ".ogg"}


def find_ffprobe(arg):
    if arg:
        return arg
    import shutil
    return shutil.which("ffprobe") or "ffprobe"


def photo_time(path: Path):
    """返回 (local_datetime, source_label)。优先 EXIF，回退 mtime。"""
    try:
        from PIL import Image
        im = Image.open(path)
        ex = im._getexif() or {}
        for tag in (36867, 306):  # DateTimeOriginal, DateTime
            v = ex.get(tag)
            if v:
                try:
                    return dt.datetime.strptime(v, "%Y:%m:%d %H:%M:%S"), "EXIF"
                except ValueError:
                    pass
    except Exception:
        pass
    return dt.datetime.fromtimestamp(path.stat().st_mtime), "mtime"


def compress(src: Path, dst: Path, max_dim: int, quality: int) -> int:
    from PIL import Image
    im = Image.open(src).convert("RGB")
    w, h = im.size
    m = max(w, h)
    if m > max_dim:
        im = im.resize((round(w * max_dim / m), round(h * max_dim / m)), Image.LANCZOS)
    dst.parent.mkdir(parents=True, exist_ok=True)
    im.save(dst, "JPEG", quality=quality, optimize=True)
    return dst.stat().st_size


def probe_audio(ffprobe: str, path: Path):
    """返回 (duration_s, creation_time_utc_iso_or_None)。"""
    try:
        r = subprocess.run(
            [ffprobe, "-v", "quiet", "-print_format", "json", "-show_format", "-show_streams", str(path)],
            capture_output=True, timeout=60,
        )
        d = json.loads(r.stdout.decode("utf-8", "replace"))
    except Exception as e:
        raise RuntimeError(f"ffprobe 失败 {path.name}: {e}")
    fmt = d.get("format", {})
    dur = float(fmt.get("duration", 0))
    tags = {k.lower(): v for k, v in fmt.get("tags", {}).items()}
    for s in d.get("streams", []):
        for k, v in s.get("tags", {}).items():
            tags.setdefault(k.lower(), v)
    ct = tags.get("creation_time") or tags.get("date")
    return dur, ct


def parse_utc(iso: str) -> dt.datetime:
    return dt.datetime.fromisoformat(iso.replace("Z", "+00:00")).replace(tzinfo=None)


def main():
    ap = argparse.ArgumentParser(description="扫描展会素材，建时间轴 + 照片↔场次映射 + 压缩照片")
    ap.add_argument("root", help="展会素材根目录（含 photo/ 和/或 record/）")
    ap.add_argument("--photo-dir", default="photo", help="照片子目录名（默认 photo）")
    ap.add_argument("--record-dir", default="record", help="录音子目录名（默认 record）")
    ap.add_argument("--out", default="_work", help="输出目录（在 root 下，默认 _work）")
    ap.add_argument("--tz", type=float, default=8.0, help="录音内嵌 UTC 时间的本地时区偏移小时数（默认 +8）")
    ap.add_argument("--max-dim", type=int, default=1024, help="压缩后最大边像素（默认 1024）")
    ap.add_argument("--quality", type=int, default=60, help="压缩 JPEG 质量（默认 60）")
    ap.add_argument("--gap", type=float, default=25.0, help="仅照片模式下，超过此分钟数的间隔切为新场次（默认 25）")
    ap.add_argument("--ffprobe", default="", help="ffprobe 路径（默认从 PATH 找）")
    args = ap.parse_args()

    root = Path(args.root).expanduser().resolve()
    photo_dir = root / args.photo_dir
    record_dir = root / args.record_dir
    out = root / args.out
    comp = out / "compressed"
    out.mkdir(parents=True, exist_ok=True)
    ffprobe = find_ffprobe(args.ffprobe)

    # ---- 录音 ----
    records = []
    if record_dir.is_dir():
        for f in sorted(record_dir.iterdir()):
            if f.suffix.lower() in AUD_EXT and f.stat().st_size > 0:
                dur, ct = probe_audio(ffprobe, f)
                rec = {"file": f.name, "stem": f.stem, "dur_s": round(dur, 1)}
                if ct:
                    end_loc = (parse_utc(ct) + dt.timedelta(hours=args.tz))
                    start_loc = end_loc - dt.timedelta(seconds=dur)
                    rec["start"] = start_loc.isoformat()
                    rec["end"] = end_loc.isoformat()
                    rec["time_source"] = "embedded_creation_time(=end)"
                else:
                    rec["start"] = None
                    rec["end"] = None
                    rec["time_source"] = "none(需人工提供开始时间)"
                records.append(rec)
    mode = "B" if records else "A"
    print(f"[scan_media] 模式={mode}  录音={len(records)}  照片目录={'有' if photo_dir.is_dir() else '无'}", flush=True)

    # ---- 照片 + 压缩 ----
    photos = []
    if photo_dir.is_dir():
        for f in sorted(photo_dir.iterdir()):
            if f.suffix.lower() in IMG_EXT and f.stat().st_size > 0:
                t, src = photo_time(f)
                dst = comp / (f.stem + ".jpg")
                try:
                    nb = compress(f, dst, args.max_dim, args.quality)
                except Exception as e:
                    print(f"  [warn] 压缩失败 {f.name}: {e}", flush=True)
                    continue
                photos.append({
                    "file": f.name, "stem": f.stem,
                    "exif": t.isoformat(), "time_source": src,
                    "compressed": str(dst), "compressed_bytes": nb,
                    "session": None,
                })
    print(f"[scan_media] 有效照片={len(photos)}  已压缩到 {comp}", flush=True)

    # ---- 场次划分 + 照片归属 ----
    sessions = []
    if mode == "B":
        for i, rec in enumerate(records):
            sessions.append({
                "index": i, "label": rec["stem"], "record": rec["file"],
                "start": rec["start"], "end": rec["end"], "dur_s": rec["dur_s"],
            })
        def in_interval(t, s, e):
            if not s or not e:
                return False
            return dt.datetime.fromisoformat(s) <= t <= dt.datetime.fromisoformat(e)

        for p in photos:
            t = dt.datetime.fromisoformat(p["exif"])
            idx = None
            for sess in sessions:
                if in_interval(t, sess["start"], sess["end"]):
                    idx = sess["index"]; break
            if idx is None:
                def dist(sess):
                    pts = [dt.datetime.fromisoformat(x) for x in (sess["start"], sess["end"]) if x]
                    return min(abs((t - x).total_seconds()) for x in pts) if pts else 1e18
                idx = min(sessions, key=dist)["index"] if sessions else None
            p["session"] = idx
    else:
        # Mode A：按时间间隔聚类
        ordered = sorted(photos, key=lambda p: p["exif"])
        gap = dt.timedelta(minutes=args.gap)
        cur_idx = -1
        last_t = None
        for p in ordered:
            t = dt.datetime.fromisoformat(p["exif"])
            if cur_idx < 0 or (last_t and (t - last_t) > gap):
                cur_idx += 1
                sessions.append({"index": cur_idx, "label": f"场次{cur_idx + 1}", "record": None,
                                 "start": t.isoformat(), "end": t.isoformat()})
            else:
                sessions[cur_idx]["end"] = t.isoformat()
            p["session"] = cur_idx
            last_t = t

    # 回填每场照片数
    for sess in sessions:
        sess["n_photos"] = sum(1 for p in photos if p["session"] == sess["index"])

    (out / "timeline.json").write_text(json.dumps(sessions, ensure_ascii=False, indent=1), encoding="utf-8")
    (out / "photo_session_map.json").write_text(json.dumps(photos, ensure_ascii=False, indent=1), encoding="utf-8")

    print("\n[scan_media] 场次时间轴：", flush=True)
    for s in sessions:
        st = (dt.datetime.fromisoformat(s["start"]).strftime("%H:%M") if s["start"] else "??:??")
        en = (dt.datetime.fromisoformat(s["end"]).strftime("%H:%M") if s["end"] else "??:??")
        print(f"  [{s['index']}] {st}-{en}  {s['label']}  photos={s['n_photos']}", flush=True)
    unassigned = sum(1 for p in photos if p["session"] is None)
    print(f"[scan_media] 未归属照片={unassigned}  输出: {out/'timeline.json'}, {out/'photo_session_map.json'}", flush=True)


if __name__ == "__main__":
    main()
