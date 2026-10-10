import argparse
import json
import sys
from pathlib import Path

TRANSLATE_RULES = """# 翻译任务书（组 {gi}，页 {pages}）

你是专业译者。一次读入本文件与页面图后直接产出译文。

硬性规则：
1. 每个 `<!--key:...|runs:N-->` 标记行原样保留，放在对应译文块之前；块数与顺序与源块一致；块之间空一行。
2. 译文以完整自然的目标语言句子为先；禁止为对上 run 数量而扭曲语序或截断词组。
3. 下方规格（术语表、缩写释义、数字写法、保留英文清单、语域）逐条遵守；同一概念全篇同一译法。
4. 数值不得改动；书写形式按规格处理（如 million/billion 换算为 万/亿），转换后的写法直接写进译文。
5. 空源块：保留标记行，正文留空。表格单元格按片段翻译，保留内部换行。
6. 译文是纯文本：禁止 markdown 强调符号与转义符（**、*、__、_、`、>），强调含义由措辞承载。
7. 标记为 `em_runs` 的 run 承载源文强调短语，译文用相应措辞自然突出；`para_splits` 决定换行归属，行不跨段。
8. 页面图只作语境参考：图内文字（含 OCR 登记）不回写，翻译范围只有标记块。
9. 产出文件只含标记块本身，开头与结尾禁止附带任何报告、统计、说明文字。
10. 产出文件：{draft}（UTF-8；经接口调用时由脚本写入同名文件，直接回复正文即可）。

"""

REVIEW_RULES = """# 审校任务书（组 {gi}，页 {pages}）

你是独立审校（未参与本组翻译）。对照内嵌的源块与译文块，只查语义与表达：

1. 语域贴合页面语境；2. 缩写按释义展开或保留；3. 保留英文清单逐项核对（清单里的项保留英文原样）；
4. 术语与术语表一致；5. 数值未被改动；6. 翻译腔、语义走样、标题折行整体理解后重排。

产出写入 {patches}（严格 JSON，不要 markdown 外壳）：
{{"patches": [{{"key": "…", "text": "整块修订后译文"}}], "splits": {{"key": ["part1", "part2"]}}, "notes": ["…"]}}

splits 只写含强调（`em_runs` 非空）或分段（`para_splits` 非空）的多 run 元素，规则：
强调 run 承载对应强调短语译文；换行不跨段；数值词元完整落在单个 part；
parts 拼接与修订后译文逐字一致（仅空白差异）；数组长度必须等于该元素的 runs 数量。
补丁改动了多 run 元素时必须在同一个补丁文件里给出该 key 的新 splits。
没有问题就写 {{"patches": [], "splits": {{}}, "notes": []}}。回复只报修订条数与争议点。

"""

VISUAL_RULES = """# 终稿视觉核对（组 {gi}，页 {pages}）

对照本组输出页面图与该页译文块，检查：可编辑文本漏译、误译、文字溢出或重叠、明显截断、
数字与专名错误。图内文字（图片里烘焙的字）保留源语言属于既定政策，不算问题。

产出写入 {issues}（严格 JSON）：
{{"issues": [{{"page": N, "key": "…或 null", "kind": "漏译|误译|溢出|重叠|截断|数字", "detail": "…"}}]}}
没有问题就写 {{"issues": []}}。回复只报检查页号与问题条数。

"""


UNIFY_RULES = """# 跨组统一任务书

通读各组译文块，做全篇用词统一：同一概念同一译法；缩写展开形式一致；数字书写形式一致；
保留英文清单全篇一致。只输出需要修改的条目。

产出（严格 JSON，不要 markdown 外壳）：
{{"patches": [{{"key": "…", "text": "整块统一后的译文"}}], "splits": {{"key": ["part1", "part2"]}}, "notes": ["…"]}}

补丁改动了多 run 元素时必须在同一个文件里给出该 key 的新 splits（强调 run 承载强调短语译文、
换行不跨段、数值词元完整落单 part、parts 拼接与统一后译文逐字一致、数组长度等于 runs 数量）。
没有需要统一的写 {{"patches": [], "splits": {{}}, "notes": []}}。

"""


def read(path):
    return Path(path).read_text(encoding="utf-8")


def ocr_for_page(ocr_dir, page):
    if not ocr_dir:
        return None
    p = Path(ocr_dir) / f"slide-{page:02d}.md"
    return p.read_text(encoding="utf-8").strip() if p.is_file() else None


def main():
    ap = argparse.ArgumentParser(description="组装子代理任务书（内容随任务书下发，子代理零查找）")
    ap.add_argument("role", choices=["translate", "review", "visual", "unify"])
    ap.add_argument("groups_dir")
    ap.add_argument("--context", required=True, help="01-context.md（规格）")
    ap.add_argument("--ocr-dir", default="", help="页面 OCR 目录（可选）")
    ap.add_argument("--images", default="", help="visual 角色的输出页面图目录")
    ap.add_argument("--group", type=int, default=0, help="只生成指定组（0=全部）")
    args = ap.parse_args()

    gdir = Path(args.groups_dir)
    index = json.loads(read(gdir / "_index.json"))
    if args.group:
        index = [item for item in index if item["group"] == args.group]
        if not index:
            sys.exit(f"没有组 {args.group}")
    context = read(args.context).strip()

    if args.role == "unify":
        drafts = []
        for df in sorted(gdir.glob("draft-*.md")):
            drafts.append(f"## {df.name}\n" + read(df).strip())
        if not drafts:
            sys.exit("没有草稿可统一")
        out = gdir / "dispatch-unify.md"
        out.write_text(UNIFY_RULES + "## 规格（全文理解产物）\n" + context
                       + "\n\n" + "\n\n".join(drafts) + "\n", encoding="utf-8")
        print(f"[build_dispatch] {out.name}: {out.stat().st_size} 字节")
        return

    prefix = {"translate": "dispatch-tr", "review": "dispatch-rv", "visual": "dispatch-vs"}[args.role]

    for item in index:
        gi = item["group"]
        pages = item["pages"]
        src = read(gdir / item["src"]).strip()
        meta = read(gdir / item["meta"]).strip()
        draft_path = gdir / f"draft-{gi:02d}.md"

        if args.role == "translate":
            head = TRANSLATE_RULES.format(gi=gi, pages=pages, draft=draft_path.name)
        elif args.role == "review":
            if not draft_path.is_file():
                sys.exit(f"缺草稿: {draft_path}")
            head = REVIEW_RULES.format(gi=gi, pages=pages, patches=f"patches-{gi:02d}.json")
        else:
            if not args.images:
                sys.exit("visual 角色需要 --images")
            if not draft_path.is_file():
                sys.exit(f"缺草稿: {draft_path}")
            head = VISUAL_RULES.format(gi=gi, pages=pages, issues=f"issues-{gi:02d}.json")

        parts = [head]
        if args.role == "translate":
            img_root = Path(args.images).resolve() if args.images else Path(".")
            images = [str(img_root / f"slide-{p:02d}.jpg") for p in pages]
            parts.append("## 页面图（与本任务书并行读入，仅供语境）\n" + "\n".join(images))
        if args.role == "visual":
            img_root = Path(args.images).resolve()
            images = [str(img_root / f"slide-{p:02d}.jpg") for p in pages]
            parts.append("## 输出页面图（与本任务书并行读入）\n" + "\n".join(images))
        parts.append("## 规格（全文理解产物，逐条遵守）\n" + context)
        if args.role == "review" or args.role == "visual":
            parts.append("## 译文块（" + draft_path.name + "）\n" + read(draft_path).strip())
        parts.append("## 源块\n" + src)
        parts.append("## run 元信息（JSON）\n" + meta)
        if args.role == "translate" and args.ocr_dir:
            ocr_lines = []
            for p in pages:
                t = ocr_for_page(args.ocr_dir, p)
                if t:
                    ocr_lines.append(f"### 页 {p} 图内文字（OCR，仅语境）\n{t}")
            if ocr_lines:
                parts.append("\n\n".join(ocr_lines))

        out = gdir / f"{prefix}-{gi:02d}.md"
        out.write_text("\n\n".join(parts) + "\n", encoding="utf-8")
        print(f"[build_dispatch] {out.name}: {out.stat().st_size} 字节")

    print(f"[build_dispatch] {args.role} 任务书 {len(index)} 份 -> {gdir}")


if __name__ == "__main__":
    main()
