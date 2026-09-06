#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""批量 OCR：调用百度 AI Studio 异步任务接口（PaddleOCR-VL 等），绕过 uvx/MSVC 坑。

为什么有这个脚本：paddleocr-doc-parsing 技能的 MCP 服务器用 `uvx` 冷启动时，
在缺少 Microsoft Visual C++ Build Tools 的 Windows 上会因源码编译 pyyaml 而失败。
本脚本直接用 http(s) 调 AI Studio 的异步 OCR 任务接口（只需 requests），
不依赖 paddlepaddle/uvx/本地推理，跨机器更稳。

也可改用 paddleocr-doc-parsing 技能，或用 agent 自身视觉读图——三者择一即可。

配置（环境变量或命令行参数，参数优先）：
  AISTUDIO_OCR_URL    任务接口，形如 https://paddleocr.aistudio-app.com/api/v2/ocr/jobs
  AISTUDIO_OCR_TOKEN  访问令牌
  AISTUDIO_OCR_MODEL  模型名，如 PaddleOCR-VL-1.6

用法：
  python ocr_aistudio.py <compressed_dir> [--out ocr] [--workers 6] [--limit 0]
输出：
  <out>/<stem>.md     每张图的 markdown 文字（layoutParsingResults[].markdown.text）
  <out>/_manifest.json [{file,stem,ok,chars,error}]
"""
import argparse
import io
import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

import requests  # pip install requests

DEFAULT_URL = "https://paddleocr.aistudio-app.com/api/v2/ocr/jobs"
OPT_PAYLOAD = {"useDocOrientationClassify": False, "useDocUnwarping": False, "useChartRecognition": False}


def ocr_one(fp: Path, out_dir: Path, url: str, token: str, model: str, retries: int = 3) -> dict:
    stem = fp.stem
    info = {"file": fp.name, "stem": stem, "ok": False, "chars": 0, "error": None}
    headers = {"Authorization": f"bearer {token}"}
    last = None
    for attempt in range(retries):
        try:
            data = {"model": model, "optionalPayload": json.dumps(OPT_PAYLOAD)}
            with open(fp, "rb") as f:
                r = requests.post(url, headers=headers, data=data, files={"file": f}, timeout=120)
            if r.status_code != 200:
                last = f"submit HTTP {r.status_code}: {r.text[:200]}"
                time.sleep(2 * (attempt + 1)); continue
            jid = r.json()["data"]["jobId"]
            jsonl_url = ""
            for _ in range(200):
                g = requests.get(f"{url}/{jid}", headers=headers, timeout=60)
                if g.status_code != 200:
                    last = f"poll HTTP {g.status_code}"; time.sleep(3); continue
                d = g.json().get("data", {})
                st = d.get("state")
                if st == "done":
                    jsonl_url = d["resultUrl"]["jsonUrl"]; break
                if st == "failed":
                    last = f"job failed: {d.get('errorMsg')}"; break
                time.sleep(3)
            if not jsonl_url:
                last = last or "poll timeout"
                time.sleep(2 * (attempt + 1)); continue
            jr = requests.get(jsonl_url, timeout=60); jr.raise_for_status()
            parts = []
            for line in jr.text.strip().split("\n"):
                line = line.strip()
                if not line:
                    continue
                for lp in json.loads(line).get("result", {}).get("layoutParsingResults", []):
                    parts.append(lp.get("markdown", {}).get("text", ""))
            md = "\n\n".join(p for p in parts if p.strip())
            (out_dir / f"{stem}.md").write_text(md, encoding="utf-8")
            info.update(ok=True, chars=len(md), error=None)
            return info
        except Exception as e:
            last = f"{type(e).__name__}: {str(e)[:160]}"
            time.sleep(2 * (attempt + 1))
    info["error"] = last
    return info


def main():
    ap = argparse.ArgumentParser(description="AI Studio 异步 OCR 批处理")
    ap.add_argument("comp_dir", help="压缩图片目录（scan_media.py 产出的 compressed/）")
    ap.add_argument("--out", default="ocr", help="输出目录（默认 ocr，相对 comp_dir 的父目录）")
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--limit", type=int, default=0, help="只处理前 N 张（0=全部，用于试跑）")
    ap.add_argument("--url", default=os.getenv("AISTUDIO_OCR_URL", DEFAULT_URL))
    ap.add_argument("--token", default=os.getenv("AISTUDIO_OCR_TOKEN", ""))
    ap.add_argument("--model", default=os.getenv("AISTUDIO_OCR_MODEL", "PaddleOCR-VL-1.6"))
    args = ap.parse_args()

    if not args.token:
        sys.exit("缺少 token：设置环境变量 AISTUDIO_OCR_TOKEN 或用 --token 传入")

    comp = Path(args.comp_dir).expanduser().resolve()
    out_dir = Path(args.out)
    if not out_dir.is_absolute():
        out_dir = comp.parent / args.out
    out_dir.mkdir(parents=True, exist_ok=True)

    files = sorted(p for p in comp.glob("*.jpg") if p.stat().st_size > 0)
    if args.limit > 0:
        files = files[: args.limit]
    print(f"[ocr] {len(files)} 张, {args.workers} 并发, model={args.model} -> {out_dir}", flush=True)

    results = []
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        futs = {ex.submit(ocr_one, fp, out_dir, args.url, args.token, args.model): fp for fp in files}
        done = 0
        for fut in as_completed(futs):
            done += 1
            info = fut.result()
            results.append(info)
            tag = "OK " if info["ok"] else "FAIL"
            print(f"  [{done}/{len(files)}] {tag} {info['file']}  chars={info['chars']}"
                  + (f"  err={info['error']}" if info["error"] else ""), flush=True)

    (out_dir / "_manifest.json").write_text(json.dumps(results, ensure_ascii=False, indent=1), encoding="utf-8")
    ok = sum(1 for r in results if r["ok"])
    print(f"[ocr] 完成 {time.time()-t0:.0f}s: {ok}/{len(results)} ok", flush=True)
    sys.exit(0 if ok == len(results) else 4)


if __name__ == "__main__":
    main()
