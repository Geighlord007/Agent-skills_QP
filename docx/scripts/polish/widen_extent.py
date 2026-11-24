#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
widen_extent.py — Byte-exact atomic width adjustment for embedded drawings in .docx.

For raster/SVG-exported figures embedded in Word, on-page typography follows:
    on_page_pt = authored_pt * (display_pt / canvas_pt)

When a figure is printed narrower than the page column, widening its `<wp:extent>`
and `<a:ext>` proportionally raises on-page text size WITHOUT touching a single
image pixel or any other byte in the .docx package.

Guarantees asserted before any write:
  1. ATOMIC: Rebuilt into a temp file and swapped via `os.replace`.
  2. SYNCED ASPECT: `<wp:extent>` and `<a:ext>` carry identical (cx, cy), with
     `cy` scaled by the exact same factor (within 1 EMU rounding).
  3. BYTE-EXACT PROOF: Every other ZIP part is byte-identical, part order is
     unchanged, and every untouched character span in `word/document.xml` is
     verified identical before committing.

Usage:
  python scripts/polish/widen_extent.py <doc.docx> --list
  python scripts/polish/widen_extent.py <doc.docx> --target rId12=5200000 --dry-run
  python scripts/polish/widen_extent.py <doc.docx> --target rId12=5200000
  python scripts/polish/widen_extent.py <doc.docx> --target rId12=4200000 --allow-shrink
"""
from __future__ import annotations

import argparse
import os
import re
import shutil
import sys
import xml.etree.ElementTree as ET
import zipfile

for _s in (sys.stdout, sys.stderr):
    if hasattr(_s, "reconfigure"):
        _s.reconfigure(encoding="utf-8", errors="replace")

EMU_PER_PT = 12700.0
EMU_PER_CM = 360000.0
DEFAULT_MAX_WIDTH_EMU = 5_800_000  # 456.69 pt (~16.11 cm, standard A4 column cap)

EXTENT_RE = r'<wp:extent\s+cx="(\d+)"\s+cy="(\d+)"\s*/>'
AEXT_RE = r'<a:ext\s+cx="(\d+)"\s+cy="(\d+)"\s*/>'
BLIP_RE = r'<a:blip[^>]*r:embed="([^"]+)"'


def parse_rels(rels_bytes: bytes | None) -> dict[str, str]:
    if not rels_bytes:
        return {}
    mapping: dict[str, str] = {}
    try:
        root = ET.fromstring(rels_bytes)
        for rel in root:
            rid = rel.attrib.get("Id")
            target = rel.attrib.get("Target")
            if rid and target:
                mapping[rid] = target
    except ET.ParseError:
        pass
    return mapping


def block_spans(xml: str, rid: str) -> list[tuple[int, int]]:
    """Return [start, end) spans of every <w:drawing> block whose a:blip embeds `rid`."""
    spans: list[tuple[int, int]] = []
    for m in re.finditer(r'<a:blip[^>]*r:embed="%s"' % re.escape(rid), xml):
        s = xml.rfind("<w:drawing", 0, m.start())
        e = xml.find("</w:drawing>", m.start())
        if s == -1 or e == -1:
            continue
        spans.append((s, e + len("</w:drawing>")))
    return spans


def list_drawings(xml: str, rels: dict[str, str]) -> list[dict]:
    rows: list[dict] = []
    seen_spans: set[tuple[int, int]] = set()
    for m in re.finditer(BLIP_RE, xml):
        rid = m.group(1)
        s = xml.rfind("<w:drawing", 0, m.start())
        e = xml.find("</w:drawing>", m.start())
        if s == -1 or e == -1:
            continue
        span = (s, e + len("</w:drawing>"))
        if span in seen_spans:
            continue
        seen_spans.add(span)
        block = xml[span[0]:span[1]]
        mw = re.search(EXTENT_RE, block)
        ma = re.search(AEXT_RE, block)
        cx = int(mw.group(1)) if mw else None
        cy = int(mw.group(2)) if mw else None
        acx = int(ma.group(1)) if ma else None
        acy = int(ma.group(2)) if ma else None
        rows.append({
            "rid": rid,
            "target": rels.get(rid, "?"),
            "cx_emu": cx,
            "cy_emu": cy,
            "width_pt": round(cx / EMU_PER_PT, 2) if cx else None,
            "height_pt": round(cy / EMU_PER_PT, 2) if cy else None,
            "width_cm": round(cx / EMU_PER_CM, 2) if cx else None,
            "synced": (cx, cy) == (acx, acy) if (cx and acx) else False,
        })
    return rows


def plan(
    xml: str,
    targets: dict[str, int],
    max_width_emu: int = DEFAULT_MAX_WIDTH_EMU,
    allow_shrink: bool = False,
):
    """Compute edits without mutating XML. Returns (edits, report, problems)."""
    edits, report, problems = [], [], []
    for rid, new_cx in targets.items():
        spans = block_spans(xml, rid)
        if len(spans) != 1:
            problems.append(
                f"{rid}: {len(spans)} drawing blocks embed this rId, expected exactly 1"
            )
            continue
        s, e = spans[0]
        block = xml[s:e]
        if block.count("<wp:extent") != 1 or block.count("<a:ext ") != 1:
            problems.append(
                f"{rid}: block has {block.count('<wp:extent')} wp:extent / "
                f"{block.count('<a:ext ')} a:ext, expected 1 each"
            )
            continue
        mw = re.search(EXTENT_RE, block)
        ma = re.search(AEXT_RE, block)
        if not mw or not ma:
            problems.append(f"{rid}: wp:extent / a:ext not both present")
            continue
        cx, cy = int(mw.group(1)), int(mw.group(2))
        acx, acy = int(ma.group(1)), int(ma.group(2))
        if (cx, cy) != (acx, acy):
            problems.append(
                f"{rid}: wp:extent {cx}x{cy} != a:ext {acx}x{acy} BEFORE the edit"
            )
            continue
        if new_cx <= 0:
            problems.append(f"{rid}: target width must be > 0 (got {new_cx})")
            continue
        if new_cx > max_width_emu:
            problems.append(
                f"{rid}: target {new_cx} EMU ({new_cx / EMU_PER_PT:.2f} pt) exceeds cap "
                f"{max_width_emu} EMU ({max_width_emu / EMU_PER_PT:.2f} pt)"
            )
            continue
        if not allow_shrink and new_cx <= cx:
            problems.append(
                f"{rid}: target {new_cx} EMU does not widen current {cx} EMU "
                "(pass --allow-shrink to clamp down)"
            )
            continue
        if new_cx == cx:
            problems.append(f"{rid}: target {new_cx} EMU equals current width {cx} EMU")
            continue
        new_cy = int(round(cy * new_cx / cx))
        if abs(new_cy * cx - new_cx * cy) > max(cx, new_cx):
            problems.append(f"{rid}: cy rounding too coarse ({new_cy}*{cx} vs {new_cx}*{cy})")
            continue

        old_w = mw.group(0)
        new_w = f'<wp:extent cx="{new_cx}" cy="{new_cy}"/>'
        old_a = ma.group(0)
        new_a = f'<a:ext cx="{new_cx}" cy="{new_cy}"/>'

        iw = s + mw.start()
        ia = s + ma.start()
        if ia < iw:
            problems.append(f"{rid}: a:ext precedes wp:extent -- unexpected block layout")
            continue

        edits.append((iw, iw + len(old_w), old_w, new_w))
        edits.append((ia, ia + len(old_a), old_a, new_a))
        report.append({
            "rid": rid,
            "old_cx": cx,
            "old_cy": cy,
            "new_cx": new_cx,
            "new_cy": new_cy,
            "old_pt": round(cx / EMU_PER_PT, 3),
            "new_pt": round(new_cx / EMU_PER_PT, 3),
            "factor": round(new_cx / cx, 6),
            "cy_factor": round(new_cy / cy, 9),
            "aspect_before": round(cx / cy, 9),
            "aspect_after": round(new_cx / new_cy, 9),
        })
    return edits, report, problems


def apply_edits(xml: str, edits: list) -> tuple[str, list]:
    """Apply edits back-to-front so earlier offsets remain exact."""
    spans = []
    for start, end, old, new in sorted(edits, key=lambda t: -t[0]):
        assert xml[start:end] == old, f"offset drift at {start}"
        xml = xml[:start] + new + xml[end:]
        spans.append((start, start + len(new), old, new))
    return xml, sorted(spans)


def prove_only_intended_bytes(old_xml: str, new_xml: str, spans: list) -> None:
    """Require every untouched character segment of document.xml to be identical."""
    o_segs, n_segs = [], []
    pos_o = pos_n = 0
    for s, e, old, new in spans:
        o_segs.append(old_xml[pos_o:s])
        n_segs.append(new_xml[pos_n:s])
        pos_o, pos_n = s + len(old), e
    o_segs.append(old_xml[pos_o:])
    n_segs.append(new_xml[pos_n:])
    for i, (a, b) in enumerate(zip(o_segs, n_segs)):
        if a != b:
            raise AssertionError(
                f"document.xml changed OUTSIDE intended extent attributes "
                f"(segment {i}, {len(a)} vs {len(b)} chars)"
            )
    assert len(o_segs) == len(n_segs)


def parse_width_value(raw: str) -> int:
    s = raw.strip().lower()
    if s.endswith("pt"):
        return int(round(float(s[:-2]) * EMU_PER_PT))
    if s.endswith("cm"):
        return int(round(float(s[:-2]) * EMU_PER_CM))
    return int(s)


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Byte-exact width adjustment for embedded drawings in a .docx package."
    )
    ap.add_argument("docx", help="Path to target .docx file")
    ap.add_argument("--list", action="store_true", help="List all embedded drawings and exit")
    ap.add_argument(
        "--target",
        action="append",
        default=[],
        metavar="RID=WIDTH",
        help="Target width in EMU (e.g. rId12=5200000) or pt/cm (e.g. rId12=420pt, rId12=15cm)",
    )
    ap.add_argument(
        "--max-width-emu",
        type=int,
        default=DEFAULT_MAX_WIDTH_EMU,
        help=f"Maximum allowed display width in EMU (default: {DEFAULT_MAX_WIDTH_EMU})",
    )
    ap.add_argument(
        "--allow-shrink",
        action="store_true",
        help="Allow shrinking width as well as widening",
    )
    ap.add_argument("--dry-run", action="store_true", help="Plan and verify without writing")
    args = ap.parse_args()

    if not os.path.isfile(args.docx):
        print(f"ERROR: file not found: {args.docx}", file=sys.stderr)
        return 2

    with zipfile.ZipFile(args.docx, "r") as z:
        names = z.namelist()
        items = {n: z.read(n) for n in names}

    if "word/document.xml" not in items:
        print("ERROR: invalid .docx (missing word/document.xml)", file=sys.stderr)
        return 2

    old_xml = items["word/document.xml"].decode("utf-8")
    rels = parse_rels(items.get("word/_rels/document.xml.rels"))

    if args.list:
        rows = list_drawings(old_xml, rels)
        print(f"== {args.docx} ({len(rows)} embedded drawings)")
        for r in rows:
            sync_mark = "OK" if r["synced"] else "DESYNC"
            print(
                f"   {r['rid']:<7} {r['target']:<26} "
                f"{str(r['cx_emu']):>9} EMU ({str(r['width_pt']):>6} pt / {str(r['width_cm']):>5} cm) "
                f"H={str(r['height_pt']):>6} pt [{sync_mark}]"
            )
        return 0

    if not args.target:
        print("ERROR: specify --list or at least one --target RID=WIDTH", file=sys.stderr)
        return 2

    targets: dict[str, int] = {}
    for t in args.target:
        if "=" not in t:
            print(f"ERROR: invalid --target '{t}', expected RID=WIDTH", file=sys.stderr)
            return 2
        rid, _, val = t.partition("=")
        targets[rid.strip()] = parse_width_value(val)

    edits, report, problems = plan(
        old_xml,
        targets,
        max_width_emu=args.max_width_emu,
        allow_shrink=args.allow_shrink,
    )
    print(f"== {args.docx}")
    for r in report:
        print(
            f"   {r['rid']:<6} {r['old_cx']:>8d} EMU {r['old_pt']:>7.2f} pt -> "
            f"{r['new_cx']:>8d} EMU {r['new_pt']:>7.2f} pt (x{r['factor']:.4f})  "
            f"aspect {r['aspect_before']:.6f} -> {r['aspect_after']:.6f}"
        )
    for p in problems:
        print(f"   !! {p}", file=sys.stderr)
    if problems or len(report) != len(targets):
        return 2
    if args.dry_run:
        print("   (dry run -- nothing written)")
        return 0

    new_xml, spans = apply_edits(old_xml, edits)
    prove_only_intended_bytes(old_xml, new_xml, spans)
    for tag in ("<wp:extent", "<a:ext ", "<w:drawing", "<a:blip"):
        assert old_xml.count(tag) == new_xml.count(tag), f"{tag} count changed"
    items["word/document.xml"] = new_xml.encode("utf-8")

    tmp = args.docx + ".tmp_widen"
    shutil.copy2(args.docx, tmp)
    try:
        with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
            for n in names:
                zout.writestr(n, items[n])
        with zipfile.ZipFile(tmp, "r") as z2:
            assert z2.namelist() == names, "part list changed"
            for n in names:
                if n == "word/document.xml":
                    continue
                if z2.read(n) != items[n]:
                    raise AssertionError(f"part {n} is not byte-identical")
            with zipfile.ZipFile(args.docx, "r") as z0:
                assert z2.read("word/document.xml") != z0.read("word/document.xml"), (
                    "document.xml did not change"
                )
        os.replace(tmp, args.docx)
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)

    print(f"   written ({len(report)} extents updated, all other bytes proven identical)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
