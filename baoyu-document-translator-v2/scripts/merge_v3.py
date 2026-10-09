# 合并 + run 切分一步到位 v3：keyed markdown → 最终 translated.json
# 用法: python merge_v3.py extracted.json translation.md translated.json [run_splits.json]
# run_splits.json 为可选的精确切分覆盖（key -> parts 列表），格式与合并结果的 parts 相同；
# 提供时其切分优先生效，未覆盖的元素沿用合并脚本的自动切分。
import json
import re
import sys
from pathlib import Path

from merge_keyed_structure_aware import build_parts, parse_translation


def norm(s):
    return re.sub(r"\s+", "", s)


def load_run_splits(path):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    data.pop("_comment", None)
    return data


def main():
    if len(sys.argv) < 4:
        raise SystemExit("用法: python merge_v3.py extracted.json translation.md translated.json [run_splits.json]")
    extracted_path, md_path, out_path = map(Path, sys.argv[1:4])
    splits_path = Path(sys.argv[4]) if len(sys.argv) > 4 else None

    data = json.loads(extracted_path.read_text(encoding="utf-8"))
    trans = parse_translation(md_path.read_text(encoding="utf-8"))
    splits = load_run_splits(splits_path) if splits_path else {}

    unknown = [k for k in splits if k not in {e["key"] for e in data["elements"]}]
    if unknown:
        raise SystemExit("run_splits.json 含未知 key: %s" % unknown)

    missing, warns = [], []
    for e in data["elements"]:
        key = e["key"]
        src_parts = e.get("parts", [])
        if key in trans:
            new_parts, w = build_parts(src_parts, trans[key], e.get("para_splits"))
            runs = e.get("runs", len(src_parts))
            if len(new_parts) < runs:
                new_parts += [""] * (runs - len(new_parts))
            else:
                new_parts = new_parts[:runs]
            e["parts"] = new_parts
            e["translated_text"] = trans[key]
            if w:
                warns.append((key, w))
        else:
            missing.append(key)   # 未翻译 key 保持原文
        if key in splits:
            parts = list(splits[key])
            if len(parts) != e["runs"]:
                raise SystemExit("%s：切分数量 %d 与 run 数量 %d 不一致" % (key, len(parts), e["runs"]))
            e["parts"] = parts

    # 自检：精确切分元素的 parts 拼接与译文一致（去空白比对）
    for key, parts in splits.items():
        if key in trans and norm("".join(parts)) != norm(trans[key]):
            raise SystemExit("%s：切分拼接与译文不一致\n  拼接=%r\n  译文=%r" % (key, "".join(parts), trans[key]))

    if missing:
        print("未翻译 key %d 个（保持原文）: %s%s" % (
            len(missing), ", ".join(missing[:20]), " …" if len(missing) > 20 else ""))
    for key, w in warns[:40]:
        print("切分警告 %s: %s" % (key, w))

    out_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print("Written %s (%d elements, 精确切分 %d 个)" % (out_path, len(data["elements"]), len(splits)))


if __name__ == "__main__":
    main()
