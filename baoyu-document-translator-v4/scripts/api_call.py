import argparse
import base64
import json
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import requests

DEFAULT_KEY_FILE = Path.home() / ".agents" / "keys" / "mimo.key"
URL = "https://api.xiaomimimo.com/v1/chat/completions"


def build_images(img_dir, pages):
    content = []
    for p in pages:
        fp = Path(img_dir) / f"slide-{p:02d}.jpg"
        if not fp.is_file():
            sys.exit(f"页面图不存在: {fp}")
        b64 = base64.b64encode(fp.read_bytes()).decode()
        content.append({"type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{b64}"}})
    return content


def call_model(model, text, images, key, temperature):
    body = {"model": model, "temperature": temperature,
            "messages": [{"role": "user", "content": [{"type": "text", "text": text}] + images}]}
    last = None
    for attempt in range(3):
        try:
            r = requests.post(URL, headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
                              json=body, timeout=600)
            break
        except requests.RequestException as e:
            last = e
            time.sleep(3 * (attempt + 1))
    else:
        sys.exit(f"接口网络错误（已重试 3 次）: {type(last).__name__}: {last}")
    if r.status_code != 200:
        sys.exit(f"接口错误 {r.status_code}: {r.text[:300]}")
    j = r.json()
    return j["choices"][0]["message"]["content"], j.get("usage", {})


def strip_fence(text):
    t = text.strip()
    if t.startswith("```"):
        t = re.sub(r"^```[a-zA-Z]*\n", "", t)
        t = re.sub(r"\n```$", "", t)
    return t.strip() + "\n"


def sanitize_markdown(text):
    # 丢弃模型混入的工具调用片段：只保留第一个 key 标记到最后一个块内容之间的文本
    t = strip_fence(text)
    first = t.find("<!--key:")
    if first < 0:
        sys.exit(f"输出里没有 key 标记: {t[:200]}")
    t = t[first:]
    lines = t.splitlines()
    clean = []
    for line in lines:
        if "antml:" in line or "paramet" in line:
            continue
        clean.append(line)
    return "\n".join(clean).rstrip("\n") + "\n"


def extract_json(text):
    t = strip_fence(text)
    m = re.search(r"\{.*\}", t, re.S)
    if not m:
        sys.exit(f"输出里没有 JSON: {t[:200]}")
    return json.loads(m.group(0))


def one_task(role, model, key, gdir, item, images_dir):
    gi = item["group"]
    pages = item["pages"]
    if role == "translate":
        book = (gdir / f"dispatch-tr-{gi:02d}.md").read_text(encoding="utf-8")
        imgs = build_images(images_dir, pages) if images_dir else []
        out = gdir / f"draft-{gi:02d}.md"
        content, usage = call_model(model, book, imgs, key, 0.2)
        out.write_text(sanitize_markdown(content), encoding="utf-8")
    elif role == "review":
        book = (gdir / f"dispatch-rv-{gi:02d}.md").read_text(encoding="utf-8")
        out = gdir / f"patches-{gi:02d}.json"
        content, usage = call_model(model, book, [], key, 0.1)
        data = extract_json(content)
        out.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    elif role == "visual":
        book = (gdir / f"dispatch-vs-{gi:02d}.md").read_text(encoding="utf-8")
        imgs = build_images(images_dir, pages)
        out = gdir / f"issues-{gi:02d}.json"
        content, usage = call_model(model, book, imgs, key, 0.1)
        data = extract_json(content)
        out.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    else:
        sys.exit(f"未知角色: {role}")
    return gi, len(pages), usage


def one_unify(model, key, gdir):
    book = (gdir / "dispatch-unify.md").read_text(encoding="utf-8")
    out = gdir / "patches-99.json"
    content, usage = call_model(model, book, [], key, 0.1)
    data = extract_json(content)
    out.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return "unify", 0, usage


def main():
    ap = argparse.ArgumentParser(description="任务书 → 模型接口 → 产出文件（不走子代理）")
    ap.add_argument("role", choices=["translate", "review", "unify", "visual"])
    ap.add_argument("groups_dir")
    ap.add_argument("--group", default="0", help="只跑指定组，逗号分隔（0=全部）")
    ap.add_argument("--images", default="", help="页面图目录（translate=源图，visual=输出图）")
    ap.add_argument("--key-file", default=str(DEFAULT_KEY_FILE))
    ap.add_argument("--model", default="mimo-v2.6-pro", help="模型（默认 mimo-v2.6-pro，支持图像）")
    ap.add_argument("--workers", type=int, default=6)
    args = ap.parse_args()

    key = Path(args.key_file).read_text(encoding="utf-8").strip()
    gdir = Path(args.groups_dir)
    index = json.loads((gdir / "_index.json").read_text(encoding="utf-8"))
    if args.group != "0":
        wanted = {int(x) for x in args.group.split(",")}
        index = [i for i in index if i["group"] in wanted]
        if not index:
            sys.exit(f"没有组 {args.group}")
    if args.role == "visual" and not args.images:
        sys.exit("visual 需要 --images")

    t0 = time.time()
    total = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
    tasks = []
    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        if args.role == "unify":
            tasks.append(ex.submit(one_unify, args.model, key, gdir))
        else:
            for item in index:
                tasks.append(ex.submit(one_task, args.role, args.model, key,
                                       gdir, item, args.images))
        for fut in as_completed(tasks):
            gi, pages, usage = fut.result()
            total = {k: total.get(k, 0) + usage.get(k, 0) for k in total}
            print(f"[api_call] {args.role} 组 {gi}: 页 {pages}  "
                  f"tokens in={usage.get('prompt_tokens', 0)} out={usage.get('completion_tokens', 0)}")
    print(f"[api_call] {args.role} 完成 {time.time() - t0:.0f}s  "
          f"合计 tokens: in={total['prompt_tokens']} out={total['completion_tokens']} "
          f"total={total['total_tokens']}")


if __name__ == "__main__":
    main()
