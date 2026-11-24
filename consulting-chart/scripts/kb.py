#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""kb.py — Knowledge Base Runtime & Read-Write Flywheel for consulting-chart.

Zero vector DB, zero external service. Operates on the compact git-synced hot index
`kb/recipes.jsonl` (<50 KB) + thumbnails/snippets inside `kb/` (plus optional local
`vendor/zerox-thinkcell` example thumbnails).

Subcommands:
  query         Fast deterministic recipe retrieval (Top-K compact JSON, <1.5 KB)
  lookbook      Build a visual HTML contact sheet for 1C designer-style selection
  ingest-image  Distill a new report chart PNG into a 600px thumbnail + recipe card (2B)
  harvest       Harvest a user-approved Tier-3 SVG script + PNG into kb/ and track promotion
  stats         Summarize recipe counts by tier/backend and list Tier-3 -> Tier-2 candidates
"""
import argparse
import base64
import html
import json
import re
import shutil
import sys
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parent.parent
KB_DIR = SKILL_ROOT / "kb"
RECIPES_FILE = KB_DIR / "recipes.jsonl"
THUMBS_DIR = KB_DIR / "thumbnails"
SNIPPETS_DIR = KB_DIR / "snippets"
PROMOTE_THRESHOLD = 3

if sys.platform == "win32":
    for _s in (sys.stdout, sys.stderr):
        if hasattr(_s, "reconfigure"):
            _s.reconfigure(encoding="utf-8", errors="replace")


def load_recipes() -> list:
    if not RECIPES_FILE.exists():
        return []
    out = []
    for line in RECIPES_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            out.append(json.loads(line))
    return out


def save_recipes(recipes: list):
    KB_DIR.mkdir(parents=True, exist_ok=True)
    RECIPES_FILE.write_text(
        "\n".join(json.dumps(r, ensure_ascii=False) for r in recipes) + "\n",
        encoding="utf-8",
    )


def _tokenize(text: str) -> set:
    text = (text or "").lower()
    words = set(re.findall(r"[a-z0-9_-]{2,}", text))
    # Add Chinese 2-char bigrams for crisp CJK intent matching without jieba
    cjk = re.findall(r"[\u4e00-\u9fff]+", text)
    for seg in cjk:
        words.add(seg)
        for i in range(len(seg) - 1):
            words.add(seg[i : i + 2])
    return words


def score_recipe(r: dict, rel: str, intent: str, fmt: str, tier_filter: int | None) -> float:
    if tier_filter is not None and r.get("tier") != tier_filter:
        return -1.0
    score = 0.0
    rel_l = (rel or "").strip().lower()
    if rel_l:
        rels = [x.lower() for x in r.get("relationships", [])]
        if rel_l in rels:
            score += 5.0
        elif any(rel_l in x or x in rel_l for x in rels):
            score += 3.0

    q_toks = _tokenize(intent)
    if q_toks:
        hay = " ".join([
            r.get("id", ""),
            r.get("title", ""),
            r.get("source", ""),
            " ".join(r.get("intent_tags", [])),
            (r.get("skeleton") or {}).get("signature_move", ""),
        ])
        h_toks = _tokenize(hay)
        overlap = q_toks & h_toks
        score += len(overlap) * 1.4

    # Format-aware routing bias
    fmt_l = (fmt or "").lower()
    if fmt_l in ("pptx", "html", "editable"):
        if r.get("backend") == "zerox_thinkcell":
            score += 4.0
    elif fmt_l in ("docx", "pdf", "svg", "static"):
        if r.get("backend") in ("native_svg", "composed_svg"):
            score += 1.5

    # Mild reward for proven recipes
    score += min(r.get("use_count", 1), 5) * 0.25
    return round(score, 2)


def cmd_query(args) -> int:
    recipes = load_recipes()
    scored = []
    for r in recipes:
        sc = score_recipe(r, args.rel, args.intent, args.format, args.tier)
        if sc > 0:
            scored.append((sc, r))
    scored.sort(key=lambda x: (-x[0], x[1]["tier"], x[1]["id"]))
    top = []
    for sc, r in scored[: args.top]:
        top.append({
            "score": sc,
            "id": r["id"],
            "tier": r["tier"],
            "backend": r["backend"],
            "title": r["title"],
            "source": r.get("source", ""),
            "signature_move": (r.get("skeleton") or {}).get("signature_move", ""),
            "annotations": (r.get("skeleton") or {}).get("annotations", []),
            "skins": r.get("compatible_skins", []),
            "thumb": r.get("thumb", ""),
            "snippet": r.get("snippet", ""),
        })
    print(json.dumps({"query": {"rel": args.rel, "intent": args.intent, "format": args.format}, "hits": top}, ensure_ascii=False, indent=2))
    return 0


def _resolve_thumb(rel_path: str) -> Path | None:
    if not rel_path:
        return None
    p = SKILL_ROOT / rel_path
    if p.exists():
        return p
    # Fallback: check local Desktop zerox path if vendor junction not yet created
    if rel_path.startswith("vendor/zerox-thinkcell/"):
        sub = rel_path[len("vendor/zerox-thinkcell/"):]
        alt = Path.home() / "Desktop" / "zerox-skills-main" / "zerox-skills-main" / "zerox-thinkcell-charts" / sub
        if alt.exists():
            return alt
    return None


def cmd_lookbook(args) -> int:
    recipes = {r["id"]: r for r in load_recipes()}
    ids = [x.strip() for x in args.ids.split(",") if x.strip()]
    picked = [recipes[i] for i in ids if i in recipes]
    if not picked:
        print(f"No matching recipe IDs found in {RECIPES_FILE}", file=sys.stderr)
        return 1

    cards_html = []
    for idx, r in enumerate(picked, 1):
        thumb_path = _resolve_thumb(r.get("thumb", ""))
        if thumb_path and thumb_path.exists():
            b64 = base64.b64encode(thumb_path.read_bytes()).decode("ascii")
            img_block = f'<img src="data:image/png;base64,{b64}" alt="{html.escape(r["id"])}">'
        else:
            anns = ", ".join((r.get("skeleton") or {}).get("annotations", []))
            img_block = (
                f'<div class="placeholder"><b>Tier {r["tier"]} · {html.escape(r["backend"])}</b>'
                f'<span>标注构件：{html.escape(anns or "标准直标")}</span>'
                f'<small>（待入库缩略图：{html.escape(r.get("thumb") or "无")}）</small></div>'
            )
        sig = (r.get("skeleton") or {}).get("signature_move", "")
        skins = " · ".join(r.get("compatible_skins", []))
        cards_html.append(f"""
        <div class="card">
          <div class="head"><span class="num">#{idx}</span><code>{html.escape(r['id'])}</code><span class="tier">Tier {r['tier']}</span></div>
          <div class="media">{img_block}</div>
          <h3>{html.escape(r['title'])}</h3>
          <p class="sig">{html.escape(sig)}</p>
          <div class="meta">出处：{html.escape(r.get('source', ''))}<br>适用皮肤：{html.escape(skins)}</div>
        </div>""")

    out_html = f"""<!DOCTYPE html><html lang="zh-CN"><head><meta charset="utf-8">
<title>Chart Lookbook — 方向选型画册</title>
<style>
body{{margin:0;padding:24px;background:#f5f6f8;font-family:"PingFang SC","Microsoft YaHei",system-ui,sans-serif;color:#111827}}
h1{{margin:0 0 6px;font-size:18px}} .sub{{color:#6b7280;font-size:13px;margin-bottom:18px}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:16px}}
.card{{background:#fff;border:1px solid #e5e7eb;border-radius:12px;padding:16px;display:flex;flex-direction:column;gap:8px}}
.head{{display:flex;align-items:center;gap:8px}} .num{{background:#111827;color:#fff;font-weight:700;padding:2px 8px;border-radius:99px;font-size:12px}}
.tier{{margin-left:auto;background:#eff6ff;color:#1d4ed8;padding:2px 8px;border-radius:99px;font-size:11px;font-weight:700}}
.media img{{width:100%;height:200px;object-fit:contain;background:#f8fafc;border:1px solid #eef0f4;border-radius:8px}}
.placeholder{{height:200px;background:#f8fafc;border:1px dashed #cbd5e1;border-radius:8px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:6px;padding:14px;text-align:center;color:#475569;font-size:12.5px}}
h3{{margin:4px 0 0;font-size:15px}} .sig{{margin:0;font-size:13px;color:#374151;line-height:1.5}}
.meta{{margin-top:auto;padding-top:8px;border-top:1px solid #f1f5f9;font-size:11.5px;color:#6b7280}}
</style></head><body>
<h1>图表方向选型画册（1C Lookbook）</h1>
<div class="sub">回复编号与偏好皮肤即可，例如：「用 #2 骨架 + Economist 皮肤，右侧加结论卡」</div>
<div class="grid">{"".join(cards_html)}</div>
</body></html>"""
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(out_html, encoding="utf-8")
    print(f"Lookbook written ({len(picked)} cards) -> {out}")
    return 0


def _save_thumbnail(src_img: Path, recipe_id: str, max_w: int = 600) -> str:
    THUMBS_DIR.mkdir(parents=True, exist_ok=True)
    dst = THUMBS_DIR / f"{recipe_id}.png"
    try:
        from PIL import Image, ImageOps
        with Image.open(src_img) as im:
            im = ImageOps.exif_transpose(im)
            if im.width > max_w:
                ratio = max_w / im.width
                im = im.resize((max_w, max(1, int(im.height * ratio))), Image.LANCZOS)
            im.save(dst, format="PNG", optimize=True)
    except Exception:
        shutil.copy2(src_img, dst)
    return f"kb/thumbnails/{recipe_id}.png"


def cmd_ingest_image(args) -> int:
    src = Path(args.image)
    if not src.exists():
        print(f"Image not found: {src}", file=sys.stderr)
        return 1
    thumb_rel = _save_thumbnail(src, args.id)
    recipes = load_recipes()
    entry = {
        "id": args.id,
        "title": args.title,
        "source": args.source,
        "tier": 3,
        "backend": "composed_svg",
        "relationships": [x.strip() for x in args.rel.split(",") if x.strip()],
        "intent_tags": [x.strip() for x in args.intent.split(",") if x.strip()],
        "skeleton": {
            "signature_move": args.signature,
            "annotations": [x.strip() for x in (args.annotations or "").split(",") if x.strip()],
        },
        "compatible_skins": [x.strip() for x in args.skins.split(",") if x.strip()],
        "thumb": thumb_rel,
        "snippet": "",
        "use_count": 1,
    }
    recipes = [r for r in recipes if r["id"] != args.id] + [entry]
    save_recipes(recipes)
    print(f"Ingested recipe `{args.id}` (thumb={thumb_rel}) into {RECIPES_FILE}")
    return 0


def cmd_harvest(args) -> int:
    script_src = Path(args.script)
    img_src = Path(args.image)
    if not script_src.exists() or not img_src.exists():
        print("Both --script and --image must exist.", file=sys.stderr)
        return 1
    SNIPPETS_DIR.mkdir(parents=True, exist_ok=True)
    snip_dst = SNIPPETS_DIR / f"{args.id}{script_src.suffix}"
    shutil.copy2(script_src, snip_dst)
    thumb_rel = _save_thumbnail(img_src, args.id)

    recipes = load_recipes()
    existing = next((r for r in recipes if r["id"] == args.id), None)
    if existing:
        existing["use_count"] = int(existing.get("use_count", 1)) + 1
        existing["thumb"] = thumb_rel
        existing["snippet"] = f"kb/snippets/{snip_dst.name}"
        cnt = existing["use_count"]
    else:
        entry = {
            "id": args.id,
            "title": args.title or args.id,
            "source": args.source or "local harvested Tier-3 chart",
            "tier": 3,
            "backend": "composed_svg",
            "relationships": [x.strip() for x in (args.rel or "magnitude").split(",") if x.strip()],
            "intent_tags": [x.strip() for x in (args.intent or args.title or args.id).split(",") if x.strip()],
            "skeleton": {"signature_move": args.signature or "本地沉淀自定义组合图", "annotations": []},
            "compatible_skins": ["house", "mckinsey", "bcg", "economist"],
            "thumb": thumb_rel,
            "snippet": f"kb/snippets/{snip_dst.name}",
            "use_count": 1,
        }
        recipes.append(entry)
        cnt = 1
    save_recipes(recipes)
    print(f"Harvested `{args.id}` (use_count={cnt}, snippet={snip_dst.name}, thumb={thumb_rel})")
    if cnt >= PROMOTE_THRESHOLD:
        print(f"[PROMOTE] `{args.id}` reached use_count={cnt} (>= {PROMOTE_THRESHOLD}) — consider promoting to Tier-2 registered renderer!")
    return 0


def cmd_stats(_args) -> int:
    recipes = load_recipes()
    by_tier = {1: 0, 2: 0, 3: 0}
    promote = []
    for r in recipes:
        by_tier[r.get("tier", 3)] = by_tier.get(r.get("tier", 3), 0) + 1
        if r.get("tier") == 3 and r.get("use_count", 0) >= PROMOTE_THRESHOLD:
            promote.append(r["id"])
    print(json.dumps({
        "recipes_file": str(RECIPES_FILE),
        "total_recipes": len(recipes),
        "by_tier": {"tier1_zerox": by_tier[1], "tier2_native_svg": by_tier[2], "tier3_motifs": by_tier[3]},
        "promote_candidates": promote,
    }, ensure_ascii=False, indent=2))
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Chart Knowledge Base CLI (query / lookbook / ingest-image / harvest / stats)")
    sp = ap.add_subparsers(dest="cmd", required=True)

    p = sp.add_parser("query", help="Deterministic Top-K recipe retrieval")
    p.add_argument("--rel", default="", help="Relationship / FT domain (e.g. partition, deviation, change-over-time, ranking)")
    p.add_argument("--intent", default="", help="One-line story or chart intent")
    p.add_argument("--format", default="docx", choices=("docx", "pdf", "svg", "pptx", "html", "any"))
    p.add_argument("--tier", type=int, default=None, choices=(1, 2, 3))
    p.add_argument("--top", type=int, default=3)
    p.set_defaults(fn=cmd_query)

    p = sp.add_parser("lookbook", help="Generate visual HTML contact sheet for selected recipe IDs")
    p.add_argument("--ids", required=True, help="Comma-separated recipe IDs")
    p.add_argument("--out", required=True, help="Output HTML path")
    p.set_defaults(fn=cmd_lookbook)

    p = sp.add_parser("ingest-image", help="Ingest a new report/Economist chart image into kb/")
    p.add_argument("image")
    p.add_argument("--id", required=True)
    p.add_argument("--title", required=True)
    p.add_argument("--source", required=True)
    p.add_argument("--rel", required=True, help="Comma-separated relationships")
    p.add_argument("--intent", required=True, help="Comma-separated intent tags")
    p.add_argument("--signature", required=True, help="One-line visual mechanism")
    p.add_argument("--annotations", default="")
    p.add_argument("--skins", default="mckinsey,bcg,economist")
    p.set_defaults(fn=cmd_ingest_image)

    p = sp.add_parser("harvest", help="Harvest an approved Tier-3 chart script + PNG back into kb/")
    p.add_argument("script")
    p.add_argument("image")
    p.add_argument("--id", required=True)
    p.add_argument("--title", default="")
    p.add_argument("--source", default="")
    p.add_argument("--rel", default="")
    p.add_argument("--intent", default="")
    p.add_argument("--signature", default="")
    p.set_defaults(fn=cmd_harvest)

    p = sp.add_parser("stats", help="Show knowledge base index statistics")
    p.set_defaults(fn=cmd_stats)

    args = ap.parse_args()
    return int(args.fn(args))


if __name__ == "__main__":
    sys.exit(main())
