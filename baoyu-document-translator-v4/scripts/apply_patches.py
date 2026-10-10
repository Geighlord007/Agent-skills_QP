import argparse
import json
import re
import sys
from pathlib import Path

MARKER_RE = re.compile(r"^<!--key:([^|]+)\|runs:(\d+)-->$")


def split_document(text):
    blocks = []
    for line in text.splitlines():
        if MARKER_RE.match(line.strip()):
            blocks.append([line, []])
        elif blocks:
            blocks[-1][1].append(line)
        elif line.strip():
            sys.exit(f"标记行之前出现正文: {line[:40]!r}")
    if not blocks:
        sys.exit("文件里没有 key 标记")
    return blocks


def main():
    ap = argparse.ArgumentParser(description="把审校/统一补丁应用到草稿，产出 run_splits.json 与 translation.md")
    ap.add_argument("groups_dir", help="groups 目录（含 draft-*.md、patches-*.json）")
    ap.add_argument("--run-splits", default="run_splits.json")
    ap.add_argument("--translation", default="translation.md")
    args = ap.parse_args()

    gdir = Path(args.groups_dir)
    drafts = sorted(gdir.glob("draft-*.md"))
    if not drafts:
        sys.exit(f"没有草稿文件: {gdir}/draft-*.md")

    docs = {df: split_document(df.read_text(encoding="utf-8")) for df in drafts}

    all_splits = {}
    applied = 0
    patch_files = sorted(gdir.glob("patches-*.json"),
                         key=lambda p: int(re.search(r"(\d+)", p.stem).group(1)))
    for pf in patch_files:
        data = json.loads(pf.read_text(encoding="utf-8"))
        for p in data.get("patches", []):
            key, text = p["key"], p["text"]
            hit = False
            for blocks in docs.values():
                for marker, body in blocks:
                    if MARKER_RE.match(marker.strip()).group(1) == key:
                        body[:] = text.splitlines()
                        hit = True
                        applied += 1
                        break
                if hit:
                    break
            if not hit:
                sys.exit(f"补丁的 key 不在任何草稿里: {key}（{pf.name}）")
        for key, parts in data.get("splits", {}).items():
            if not "".join(parts).strip():
                sys.exit(f"splits 拼接为空: {key}（{pf.name}）")
            all_splits[key] = parts
        for note in data.get("notes", []):
            print(f"[apply_patches] note({pf.name}): {note}")

    for df, blocks in docs.items():
        out_lines = []
        for marker, body in blocks:
            out_lines.append(marker)
            out_lines.extend(body)
        df.write_text("\n".join(out_lines).rstrip("\n") + "\n", encoding="utf-8")

    # 补丁改动过文本的元素，其旧切分可能失效：非空白内容不一致的切分回退合并脚本的自动切分
    final_text = {}
    for blocks in docs.values():
        for marker, body in blocks:
            key = MARKER_RE.match(marker.strip()).group(1)
            final_text[key] = "\n".join(body)
    for key in list(all_splits):
        joined = "".join(all_splits[key])
        if "".join(joined.split()) != "".join(final_text.get(key, "").split()):
            print(f"[apply_patches] 警告: {key} 的切分与补丁后的译文不一致，回退自动切分")
            del all_splits[key]

    Path(args.run_splits).write_text(
        json.dumps(all_splits, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    concat = [df.read_text(encoding="utf-8").strip("\n") for df in drafts]
    Path(args.translation).write_text("\n\n".join(concat) + "\n", encoding="utf-8")
    print(f"[apply_patches] 补丁 {applied} 条, splits {len(all_splits)} 键 -> {args.run_splits}, {args.translation}")


if __name__ == "__main__":
    main()
