# 逐页中英对照视图：按幻灯片切出 pages/page-NN.txt，供并行逐页抽查
# 用法: python page_compare.py extracted.json translated.json out_dir [--slides a-b]
# DOCX 按 story 分页（page-NN 对应 story 段），PPTX 按幻灯片分页
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
    ex = load(args[0])["elements"]
    tr = {e["key"]: e for e in load(args[1])["elements"]}
    out = Path(args[2])
    out.mkdir(parents=True, exist_ok=True)
    lo, hi = 0, 10 ** 9
    if "--slides" in sys.argv:
        seg = sys.argv[sys.argv.index("--slides") + 1]
        a, b = seg.split("-")
        lo, hi = int(a), int(b)

    groups = {}
    for e in ex:
        key = e["key"]
        if key.startswith("n_"):
            page = int(key.split("_")[1])
        elif re.match(r"^[stp]_", key):
            page = int(key.split("_")[1])
        else:
            page = 0
        groups.setdefault(page, []).append(e)

    written = 0
    for page in sorted(groups):
        if not (lo <= page <= hi):
            continue
        lines = ["== PAGE %d ==" % page]
        for e in groups[page]:
            key = e["key"]
            tgt = tr.get(key, {}).get("translated_text", "")
            lines.append("-- " + key)
            for ln in e["text"].split("\n"):
                lines.append("  EN | " + ln)
            for ln in tgt.split("\n"):
                lines.append("  ZH | " + ln)
        (out / ("page-%02d.txt" % page)).write_text("\n".join(lines) + "\n", encoding="utf-8")
        written += 1
    print("written %d page files -> %s" % (written, out))


if __name__ == "__main__":
    main()
