import argparse
import json
import sys
from pathlib import Path


def is_emphasis(style, majority_sz=None):
    if not isinstance(style, dict):
        return False
    color = style.get("color")
    colored = color not in (None, "", "000000", "auto")
    if style.get("b") or style.get("i") or style.get("u") or colored:
        return True
    sz = style.get("sz")
    return majority_sz is not None and sz is not None and sz != majority_sz


def main():
    ap = argparse.ArgumentParser(description="按页分组构建翻译单元（keyed 块 + run 元信息）")
    ap.add_argument("extracted", help="extract_v3.py 产出的 extracted.json")
    ap.add_argument("--out", default="groups", help="输出目录（默认 groups）")
    ap.add_argument("--per-group", type=int, default=3, help="每组页数（默认 3）")
    args = ap.parse_args()

    data = json.loads(Path(args.extracted).read_text(encoding="utf-8"))
    if data.get("file_type") != "pptx":
        sys.exit(f"只支持 PPTX 提取结果，当前 file_type={data.get('file_type')!r}")
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    by_page = {}
    for e in data["elements"]:
        by_page.setdefault(e.get("slide", 0) + 1, []).append(e)
    pages = sorted(by_page)
    if not pages:
        sys.exit("extracted.json 里没有元素")

    groups = [pages[i:i + args.per_group] for i in range(0, len(pages), args.per_group)]
    index = []
    for gi, grp in enumerate(groups, 1):
        blocks, meta = [], []
        for p in grp:
            for e in by_page[p]:
                runs = e.get("runs", 1)
                styles = e.get("run_styles") or []
                szs = [s.get("sz") for s in styles if isinstance(s, dict) and s.get("sz") is not None]
                majority_sz = max(set(szs), key=szs.count) if szs else None
                em = [i for i, s in enumerate(styles) if is_emphasis(s, majority_sz)]
                blocks.append(f"<!--key:{e['key']}|runs:{runs}-->\n{e['text']}")
                m = {"key": e["key"], "page": p, "runs": runs}
                if em:
                    m["em_runs"] = em
                if runs > 1 and e.get("parts"):
                    m["run_texts"] = e["parts"]
                if e.get("para_splits"):
                    m["para_splits"] = e["para_splits"]
                meta.append(m)
        (out / f"src-{gi:02d}.md").write_text("\n\n".join(blocks) + "\n", encoding="utf-8")
        (out / f"meta-{gi:02d}.json").write_text(
            json.dumps(meta, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        index.append({"group": gi, "pages": grp, "elements": len(meta),
                      "src": f"src-{gi:02d}.md", "meta": f"meta-{gi:02d}.json"})
        print(f"[slide_bundles] 组 {gi:02d}: 页 {grp} 元素 {len(meta)}")
    (out / "_index.json").write_text(json.dumps(index, ensure_ascii=False, indent=1) + "\n",
                                     encoding="utf-8")
    print(f"[slide_bundles] 共 {len(groups)} 组 -> {out}")


if __name__ == "__main__":
    main()
