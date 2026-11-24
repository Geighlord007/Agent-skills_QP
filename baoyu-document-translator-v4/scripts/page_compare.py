# -*- coding: utf-8 -*-
"""逐页源文/译文对照视图：按幻灯片（PPTX）或 story（DOCX）切出 pages/page-NN.txt，供并行逐页抽查。

用法: python page_compare.py extracted.json translated.json out_dir [--slides a-b]
"""
import json
import re
import sys
from pathlib import Path


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if len(args) < 3:
        raise SystemExit("用法: python page_compare.py extracted.json translated.json out_dir [--slides a-b]")
    ex_doc = load(args[0])
    ex = ex_doc["elements"]
    file_type = ex_doc.get("file_type", "")
    tr = {e["key"]: e for e in load(args[1])["elements"]}
    out = Path(args[2])
    out.mkdir(parents=True, exist_ok=True)
    lo, hi = 0, 10 ** 9
    if "--slides" in sys.argv:
        seg = sys.argv[sys.argv.index("--slides") + 1]
        a, b = seg.split("-")
        lo, hi = int(a), int(b)

    groups = {}
    labels = {}
    story_to_page = {}
    for e in ex:
        key = e["key"]
        parts = key.split("_")
        # PPTX keys: s_<slide>_..., t_<slide>_..., n_<slide>
        if file_type != "docx" and len(parts) >= 2 and re.match(r"^[stnp]$", parts[0]) and parts[1].isdigit():
            page = int(parts[1])
            labels.setdefault(page, f"SLIDE {page}")
        else:
            # DOCX keys: group by story in encounter order (1-based)
            story = e.get("story") or "body"
            if story not in story_to_page:
                story_to_page[story] = len(story_to_page) + 1
            page = story_to_page[story]
            labels.setdefault(page, f"STORY {story}")
        groups.setdefault(page, []).append(e)

    written = 0
    for page in sorted(groups):
        if not (lo <= page <= hi):
            continue
        lines = [f"== PAGE {page} ({labels[page]}) =="]
        for e in groups[page]:
            key = e["key"]
            tgt = tr.get(key, {}).get("translated_text", "")
            lines.append("-- " + key)
            for ln in e["text"].split("\n"):
                lines.append("  SRC | " + ln)
            for ln in tgt.split("\n"):
                lines.append("  TGT | " + ln)
        (out / ("page-%02d.txt" % page)).write_text("\n".join(lines) + "\n", encoding="utf-8")
        written += 1
    print("written %d page files -> %s" % (written, out))


if __name__ == "__main__":
    main()
