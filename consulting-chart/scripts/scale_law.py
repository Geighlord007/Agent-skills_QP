#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""scale_law.py — Pure-arithmetic on-page legibility guard (absorbed from nice-baogao).

Formula:
    on_page_pt = authored_pt * display_width_pt / canvas_width_pt

Replaces 1,252 lines of brittle pixel-ink CV measurement with a deterministic 15-line
arithmetic gate run directly on authored SVG before shipping.

Default anchors:
  - A4 Word full figure cap: 16.11 cm = 456.69 pt (16:9 PPT slide = 960 pt / 720 pt)
  - Hard legibility floor: 6.0 pt | Recommended target: 6.5 pt (floor * 1.08)

Usage:
  python scripts/scale_law.py chart.svg [--display-pt 456.69] [--target 6.5] [--floor 6.0]
"""
import argparse
import re
import sys
from pathlib import Path
from xml.etree import ElementTree as ET

if sys.platform == "win32":
    for _s in (sys.stdout, sys.stderr):
        if hasattr(_s, "reconfigure"):
            _s.reconfigure(encoding="utf-8", errors="replace")

FONT_RE = re.compile(r"font-size\s*:\s*([0-9]+(?:\.[0-9]+)?)\s*(px|pt)?", re.I)


def on_page_pt(authored_pt: float, canvas_width_pt: float, display_width_pt: float) -> float:
    return authored_pt * display_width_pt / canvas_width_pt


def parse_svg_metrics(svg_path: Path):
    root = ET.fromstring(svg_path.read_text(encoding="utf-8", errors="replace"))
    vb = root.get("viewBox", "").strip()
    canvas_w = None
    if vb:
        parts = re.split(r"[\s,]+", vb)
        if len(parts) == 4:
            canvas_w = float(parts[2])
    if canvas_w is None:
        w_attr = root.get("width", "")
        m = re.match(r"([0-9]+(?:\.[0-9]+)?)", w_attr)
        canvas_w = float(m.group(1)) if m else 960.0

    sizes = []
    for elem in root.iter():
        tag = elem.tag.rsplit("}", 1)[-1]
        if tag not in ("text", "tspan"):
            continue
        txt = "".join(elem.itertext()).strip()
        if not txt:
            continue
        fs = elem.get("font-size")
        val = None
        if fs:
            m = re.match(r"([0-9]+(?:\.[0-9]+)?)", fs.strip())
            if m:
                val = float(m.group(1))
        if val is None and elem.get("style"):
            m = FONT_RE.search(elem.get("style", ""))
            if m:
                val = float(m.group(1))
        if val is not None and val > 0:
            sizes.append((val, txt[:40]))
    return canvas_w, sizes


def main() -> int:
    ap = argparse.ArgumentParser(description="Verify SVG on-page font legibility via Scale Law arithmetic.")
    ap.add_argument("svg", help="Input SVG file")
    ap.add_argument("--display-pt", type=float, default=456.69, help="Target display width in pt (Word A4 cap=456.69, PPT=720)")
    ap.add_argument("--floor", type=float, default=6.0, help="Hard failure floor in pt (default: 6.0)")
    ap.add_argument("--target", type=float, default=6.5, help="Warning target in pt (default: 6.5)")
    args = ap.parse_args()

    canvas_w, sizes = parse_svg_metrics(Path(args.svg))
    if not sizes:
        print(f"[scale_law] No sized text elements found in {args.svg} (canvas_w={canvas_w})")
        return 0

    scale = args.display_pt / canvas_w
    ranked = sorted((on_page_pt(sz, canvas_w, args.display_pt), sz, txt) for sz, txt in sizes)
    min_pt, min_auth, min_txt = ranked[0]
    status = "FAIL" if min_pt < args.floor else ("WARN" if min_pt < args.target else "PASS")
    print(f"[scale_law] {status} | canvas={canvas_w:.1f} -> display={args.display_pt:.2f}pt (scale={scale:.3f})")
    print(f"  smallest label: authored={min_auth:.1f} -> on-page={min_pt:.2f}pt | sample={min_txt!r}")
    if status != "PASS":
        needed = args.target / scale
        print(f"  fix lever: raise smallest font-size to >= {needed:.1f} (or narrow canvas / widen display extent)")
    return 1 if status == "FAIL" else 0


if __name__ == "__main__":
    sys.exit(main())
