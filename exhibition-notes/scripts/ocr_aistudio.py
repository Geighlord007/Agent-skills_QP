#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""批量 OCR：调用百度 AI Studio 异步任务接口（PaddleOCR-VL 等），绕过 uvx/MSVC 坑。

适用边界：
  - 本脚本直连 AI Studio 异步 OCR HTTP 接口（仅依赖 requests），用于在 Windows 缺少
    Microsoft Visual C++ Build Tools 导致 paddleocr-doc-parsing 的 uvx 冷启动编译 pyyaml
    失败时作为轻量替代方案。
  - 若环境已就绪，也可直接使用兄弟技能 paddleocr-doc-parsing 或 agent 视觉读图。

特性：
  - 默认支持断点续传：若 <out>/<stem>.md 已存在且非空则跳过，避免重跑浪费额度；
    传 --force 可强制重新识别。

配置（环境变量或命令行参数，参数优先）：
  AISTUDIO_OCR_URL    任务接口，默认 https://paddleocr.aistudio-app.com/api/v2/ocr/jobs
  AISTUDIO_OCR_TOKEN  访问令牌
  AISTUDIO_OCR_MODEL  模型名，默认 PaddleOCR-VL-1.6

用法：
  python scripts/ocr_aistudio.py <compressed_dir> [--out ocr] [--workers 6] [--limit 0] [--force]
输出：
  <out>/<stem>.md       每张图的 markdown 文字（layoutParsingResults[].markdown.text）
  <out>/_manifest.json  [{file,stem,ok,chars,skipped,error}]
"""
import argparse
import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8", errors="replace")

import requests  # pip install requests

DEFAULT_URL = "https://paddleocr.aistudio-app.com/api/v2/ocr/jobs"
OPT_PAYLOAD = {"useDocOrientationClassify": False, "useDocUnwarping": False, "useChartRecognition": False}


def ocr_one(fp: Path, out_dir: Path, url: str, token: str, model: str, retries: int = 3) -> dict:
    stem = fp.stem
    info = {"file": fp.name, "stem": stem, "ok": False, "chars": 0, "skipped": False, "error": None}
    headers = {"Authorization": f"bearer {token}"}
    last = None
    for attempt in range(retries):
        try:
            data = {"model": model, "optionalPayload": json.dumps(OPT_PAYLOAD)}
            with open(fp, "rb") as f:
                r = requests.post(url, headers=headers, data=data, files={"file": f}, timeout=120)
            if r.status_code != 200:
                last = f"submit HTTP {r.status_code}: {r.text[:200]}"
                time.sleep(2 * (attempt + 1))
                continue
            jid = r.json()["data"]["jobId"]
            jsonl_url = ""
            for _ in range(200):
                g = requests.get(f"{url}/{jid}", headers=headers, timeout=60)
                if g.status_code != 200:
                    last = f"poll HTTP {g.status_code}"
                    time.sleep(3)
                    continue
                d = g.json().get("data", {})
                st = d.get("state")
                if st == "done":
                    jsonl_url = d["resultUrl"]["jsonUrl"]
                    break
                if st == "failed":
                    last = f"job failed: {d.get('errorMsg')}"
                    break
                time.sleep(3)
            if not jsonl_url:
                last = last or "poll timeout"
                time.sleep(2 * (attempt + 1))
                continue
            jr = requests.get(jsonl_url, timeout=60)
            jr.raise_for_status()
            parts = []
            for line in jr.text.strip().split("\n"):
                line = line.strip()
                if not line:
                    continue
                for lp in json.loads(line).get("result", {}).get("layoutParsingResults", []):
                    parts.append(lp.get("markdown", {}).get("text", ""))
            md = "\n\n".join(p for p in parts if p.strip())
            (out_dir / f"{stem}.md").write_text(md, encoding="utf-8")
            info.update(ok=True, chars=len(md), skipped=False, error=None)
            return info
        except Exception as e:
            last = f"{type(e).__name__}: {str(e)[:160]}"
            time.sleep(2 * (attempt + 1))
    info["error"] = last
    return info


def main():
    ap = argparse.ArgumentParser(description="AI Studio 异步 OCR 批处理（支持断点续传）")
    ap.add_argument("comp_dir", help="压缩图片目录（scan_media.py 产出的 compressed/）")
    ap.add_argument("--out", default="ocr", help="输出目录（默认 ocr，相对 comp_dir 的父目录）")
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--limit", type=int, default=0, help="只处理前 N 张（0=全部，用于试跑）")
    ap.add_argument("--force", action="store_true", help="忽略已有非空 <stem>.md，强制重新 OCR")
    ap.add_argument("--url", default=os.getenv("AISTUDIO_OCR_URL", DEFAULT_URL))
    ap.add_argument("--token", default=os.getenv("AISTUDIO_OCR_TOKEN", ""))
    ap.add_argument("--model", default=os.getenv("AISTUDIO_OCR_MODEL", "PaddleOCR-VL-1.6"))
    args = ap.parse_args()

    comp = Path(args.comp_dir).expanduser().resolve()
    out_dir = Path(args.out)
    if not out_dir.is_absolute():
        out_dir = comp.parent / args.out
    out_dir.mkdir(parents=True, exist_ok=True)

    files = sorted(p for p in comp.glob("*.jpg") if p.is_file() and p.stat().st_size > 0)
    if args.limit > 0:
        files = files[: args.limit]

    results = []
    todo = []
    for fp in files:
        md_path = out_dir / f"{fp.stem}.md"
        if not args.force and md_path.is_file() and md_path.stat().st_size > 0:
            text = md_path.read_text(encoding="utf-8", errors="replace")
            if text.strip():
                results.append(
                    {
                        "file": fp.name,
                        "stem": fp.stem,
                        "ok": True,
                        "chars": len(text),
                        "skipped": True,
                        "error": None,
                    }
                )
                continue
        todo.append(fp)

    if todo and not args.token:
        sys.exit("缺少 token：设置环境变量 AISTUDIO_OCR_TOKEN 或用 --token 传入")

    print(
        f"[ocr] 共 {len(files)} 张（跳过已有 {len(results)} 张，待识别 {len(todo)} 张）, "
        f"{args.workers} 并发, model={args.model} -> {out_dir}",
        flush=True,
    )

    t0 = time.time()
    if todo:
        with ThreadPoolExecutor(max_workers=args.workers) as ex:
            futs = {ex.submit(ocr_one, fp, out_dir, args.url, args.token, args.model): fp for fp in todo}
            done = 0
            for fut in as_completed(futs):
                done += 1
                info = fut.result()
                results.append(info)
                tag = "OK " if info["ok"] else "FAIL"
                print(
                    f"  [{done}/{len(todo)}] {tag} {info['file']}  chars={info['chars']}"
                    + (f"  err={info['error']}" if info["error"] else ""),
                    flush=True,
                )

    results.sort(key=lambda r: r["file"])
    (out_dir / "_manifest.json").write_text(json.dumps(results, ensure_ascii=False, indent=1), encoding="utf-8")
    ok = sum(1 for r in results if r["ok"])
    print(f"[ocr] 完成 {time.time() - t0:.0f}s: {ok}/{len(results)} ok（含跳过 {sum(1 for r in results if r.get('skipped'))}）", flush=True)
    sys.exit(0 if ok == len(results) else 4)


if __name__ == "__main__":
    main()
