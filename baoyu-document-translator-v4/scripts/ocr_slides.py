# 页面图内文字 OCR（百度 AI Studio 异步接口）。
# 调用方式沿用 exhibition-notes 技能的 scripts/ocr_aistudio.py；此处额外保留原始
# JSONL（含版面位置信息），供"图内文字带位置登记"使用。
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

import requests

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
            (out_dir / f"{stem}.raw.jsonl").write_text(jr.text, encoding="utf-8")
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
    ap = argparse.ArgumentParser(description="页面图 OCR（AI Studio 异步接口，保留原始 JSONL）")
    ap.add_argument("images_dir", help="页面图目录（*.jpg）")
    ap.add_argument("--out", default="ocr", help="输出目录（默认 images_dir/ocr）")
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--limit", type=int, default=0, help="只处理前 N 张（0=全部）")
    ap.add_argument("--url", default=os.getenv("AISTUDIO_OCR_URL", DEFAULT_URL))
    ap.add_argument("--token", default=os.getenv("AISTUDIO_OCR_TOKEN", ""))
    ap.add_argument("--token-file", default=str(Path.home() / ".agents" / "keys" / "aistudio.key"),
                    help="token 文件（环境变量优先）")
    ap.add_argument("--model", default=os.getenv("AISTUDIO_OCR_MODEL", "PaddleOCR-VL-1.6"))
    args = ap.parse_args()

    token = args.token
    if not token and Path(args.token_file).is_file():
        token = Path(args.token_file).read_text(encoding="utf-8").strip()
    if not token:
        sys.exit("缺少 token：设置 AISTUDIO_OCR_TOKEN、--token，或写入 ~/.agents/keys/aistudio.key")

    src = Path(args.images_dir).resolve()
    if not src.is_dir():
        sys.exit(f"目录不存在: {src}")
    out_dir = Path(args.out)
    if not out_dir.is_absolute():
        out_dir = src / args.out
    out_dir.mkdir(parents=True, exist_ok=True)

    files = sorted(p for p in src.glob("*.jpg") if p.stat().st_size > 0)
    if args.limit > 0:
        files = files[: args.limit]
    if not files:
        sys.exit(f"目录里没有 jpg: {src}")
    print(f"[ocr_slides] {len(files)} 张, {args.workers} 并发, model={args.model} -> {out_dir}", flush=True)

    results = []
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        futs = {ex.submit(ocr_one, fp, out_dir, args.url, token, args.model): fp for fp in files}
        done = 0
        for fut in as_completed(futs):
            done += 1
            info = fut.result()
            results.append(info)
            tag = "OK " if info["ok"] else "FAIL"
            print(f"  [{done}/{len(files)}] {tag} {info['file']}  chars={info['chars']}"
                  + (f"  err={info['error']}" if info["error"] else ""), flush=True)

    (out_dir / "_manifest.json").write_text(
        json.dumps(results, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    ok = sum(1 for r in results if r["ok"])
    print(f"[ocr_slides] 完成 {time.time() - t0:.0f}s: {ok}/{len(results)} ok")
    if ok != len(results):
        sys.exit(4)


if __name__ == "__main__":
    main()
