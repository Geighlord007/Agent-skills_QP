#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Widen the display extent of the drawings that reference given relationship ids, so a
figure that is printed well below the column prints its raster type LARGER.

    on-page pt = authored_pt x display_pt / canvas_pt

Because the type inside these figures is raster, the ONLY way to raise its printed size
without touching a single drawn pixel is to give the same image more page width. Nothing
else in the package changes: not one media byte, not one label string.

This is the mirror image of `_tools/redraw/_fit_extent.py` (which only clamps DOWN, to
keep a figure inside the text column) and is modelled on it line for line. It is NOT a
figure replacement, so it is not `_tools/replace_figure.py`'s job: that tool preserves the
ORIGINAL `cx` by design (`rescale_extents()` reads `cx` and only rewrites `cy` for a new
aspect), so it can never widen anything. `replace_figure.py` remains the only tool used
for swapping image bytes.

Guarantees, all asserted before anything is written:

  1. ATOMIC. The package is rebuilt into `<docx>.tmp_widen` and moved into place with
     `os.replace`, so a crash cannot leave a half-written document.
  2. `wp:extent` AND `a:ext` AGREE after the edit, and both carry the same cx/cy; `cy` is
     scaled by the same factor as `cx` (to within the unavoidable 1-EMU rounding), so the
     aspect ratio is preserved and the figure is not distorted.
  3. EVERY OTHER ZIP PART IS BYTE-IDENTICAL before and after, the part list is unchanged,
     and the ONLY differing bytes in `word/document.xml` are the `cx`/`cy` digits inside
     the four intended attribute values. The change is proved by re-splitting both
     documents on the recorded edit spans and requiring every untouched segment to match.

Refuses to widen past 5,800,000 EMU (456.69 pt = 16.111 cm, the pipeline's own cap in
`replace_figure.rescale_extents`), and refuses to SHRINK -- that is `_fit_extent.py`.

Usage:
    python _tools/redraw/_widen_extent.py "<docx>" --target rId12=4000000 [--target ...]
                                           [--dry-run]
"""
from __future__ import annotations

import argparse
import os
import re
import shutil
import sys
import zipfile

EMU_PER_PT = 12700.0
MAX_WIDTH_EMU = 5_800_000            # 456.69 pt -- the pipeline's cap
EXTENT_RE = r'<wp:extent\s+cx="(\d+)"\s+cy="(\d+)"\s*/>'
AEXT_RE = r'<a:ext\s+cx="(\d+)"\s+cy="(\d+)"\s*/>'


def block_span(xml: str, rid: str):
    """The [start, end) span of the <w:drawing> block whose a:blip embeds `rid`."""
    spans = []
    for m in re.finditer(r'<a:blip[^>]*r:embed="%s"' % re.escape(rid), xml):
        s = xml.rfind("<w:drawing", 0, m.start())
        e = xml.find("</w:drawing>", m.start())
        if s == -1 or e == -1:
            continue
        spans.append((s, e + len("</w:drawing>")))
    return spans


def plan(xml: str, targets: dict[str, int]):
    """Work out every edit, WITHOUT applying it. Returns (edits, report, problems).

    An edit is (abs_start, abs_end, old_text, new_text) over `xml`.
    """
    edits, report, problems = [], [], []
    for rid, new_cx in targets.items():
        spans = block_span(xml, rid)
        if len(spans) != 1:
            problems.append("%s: %d drawing blocks embed this rId, expected exactly 1"
                            % (rid, len(spans)))
            continue
        s, e = spans[0]
        block = xml[s:e]
        if block.count("<wp:extent") != 1 or block.count("<a:ext ") != 1:
            problems.append("%s: block has %d wp:extent / %d a:ext, expected 1 each"
                            % (rid, block.count("<wp:extent"), block.count("<a:ext ")))
            continue
        mw = re.search(EXTENT_RE, block)
        ma = re.search(AEXT_RE, block)
        if not mw or not ma:
            problems.append("%s: wp:extent / a:ext not both present" % rid)
            continue
        cx, cy = int(mw.group(1)), int(mw.group(2))
        acx, acy = int(ma.group(1)), int(ma.group(2))
        if (cx, cy) != (acx, acy):
            problems.append("%s: wp:extent %dx%d != a:ext %dx%d BEFORE the edit"
                            % (rid, cx, cy, acx, acy))
            continue
        if new_cx > MAX_WIDTH_EMU:
            problems.append("%s: target %d EMU (%.2f pt) is past the %.2f pt cap"
                            % (rid, new_cx, new_cx / EMU_PER_PT, MAX_WIDTH_EMU / EMU_PER_PT))
            continue
        if new_cx <= cx:
            problems.append("%s: target %d EMU does not widen (current %d); "
                            "use _fit_extent.py to clamp" % (rid, new_cx, cx))
            continue
        new_cy = int(round(cy * new_cx / cx))
        # cy must carry the SAME factor: only integer rounding may differ
        if abs(new_cy * cx - new_cx * cy) > new_cx:
            problems.append("%s: cy rounding too coarse (%d*%d vs %d*%d)"
                            % (rid, new_cy, cx, new_cx, cy))
            continue
        old_w = '<wp:extent cx="%d" cy="%d"/>' % (cx, cy)
        new_w = '<wp:extent cx="%d" cy="%d"/>' % (new_cx, new_cy)
        old_a = '<a:ext cx="%d" cy="%d"/>' % (acx, acy)
        new_a = '<a:ext cx="%d" cy="%d"/>' % (new_cx, new_cy)
        if old_w not in block or old_a not in block:
            problems.append("%s: canonical extent strings not found in the block" % rid)
            continue
        # absolute spans, the wp:extent one first (it precedes a:ext in the block)
        iw = s + block.index(old_w)
        ia = s + block.index(old_a)
        if ia < iw:
            problems.append("%s: a:ext precedes wp:extent -- unexpected block layout" % rid)
            continue
        edits.append((iw, iw + len(old_w), old_w, new_w))
        edits.append((ia, ia + len(old_a), old_a, new_a))
        report.append({
            "rid": rid, "old_cx": cx, "old_cy": cy, "new_cx": new_cx, "new_cy": new_cy,
            "old_pt": round(cx / EMU_PER_PT, 3), "new_pt": round(new_cx / EMU_PER_PT, 3),
            "factor": round(new_cx / cx, 6),
            "cy_factor": round(new_cy / cy, 9),
            "aspect_before": round(cx / cy, 9), "aspect_after": round(new_cx / new_cy, 9),
        })
    return edits, report, problems


def apply_edits(xml: str, edits: list) -> tuple[str, list]:
    """Apply edits back-to-front so earlier offsets stay valid. Returns (new, spans)."""
    spans = []
    for start, end, old, new in sorted(edits, key=lambda t: -t[0]):
        assert xml[start:end] == old, "offset drift at %d" % start
        xml = xml[:start] + new + xml[end:]
        spans.append((start, start + len(new), old, new))
    return xml, sorted(spans)


def prove_only_intended_bytes(old_xml: str, new_xml: str, spans: list) -> None:
    """Split both on the edit spans and require every untouched segment to be identical."""
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
            raise AssertionError("document.xml changed OUTSIDE the intended extent "
                                 "attributes (segment %d, %d vs %d chars)"
                                 % (i, len(a), len(b)))
    assert len(o_segs) == len(n_segs)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("docx")
    ap.add_argument("--target", action="append", default=[],
                    metavar="RID=EMU", help="e.g. --target rId12=4000000")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    targets: dict[str, int] = {}
    for t in a.target:
        rid, _, val = t.partition("=")
        targets[rid.strip()] = int(val.strip())

    with zipfile.ZipFile(a.docx) as z:
        names = z.namelist()
        items = {n: z.read(n) for n in names}

    old_xml = items["word/document.xml"].decode("utf-8")
    edits, report, problems = plan(old_xml, targets)
    print("== %s" % a.docx)
    for r in report:
        print("   %-6s %8d EMU %8.3f pt  ->  %8d EMU %8.3f pt  (x%.6f)  "
              "aspect %.7f -> %.7f  cy x%.9f"
              % (r["rid"], r["old_cx"], r["old_pt"], r["new_cx"], r["new_pt"],
                 r["factor"], r["aspect_before"], r["aspect_after"], r["cy_factor"]))
    for p in problems:
        print("   !! %s" % p, file=sys.stderr)
    if problems:
        return 2
    if len(report) != len(targets):
        print("   !! planned %d of %d targets" % (len(report), len(targets)), file=sys.stderr)
        return 2
    if a.dry_run:
        print("   (dry run -- nothing written)")
        return 0

    new_xml, spans = apply_edits(old_xml, edits)
    prove_only_intended_bytes(old_xml, new_xml, spans)
    # counts must not move
    for tag in ("<wp:extent", "<a:ext ", "<w:drawing", "<a:blip"):
        assert old_xml.count(tag) == new_xml.count(tag), "%s count changed" % tag
    items["word/document.xml"] = new_xml.encode("utf-8")

    tmp = a.docx + ".tmp_widen"
    shutil.copy2(a.docx, tmp)
    try:
        with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
            for n in names:
                zout.writestr(n, items[n])
        # condition 3: every other part byte-identical, part list identical
        with zipfile.ZipFile(tmp) as z2:
            assert z2.namelist() == names, "part list changed"
            for n in names:
                if n == "word/document.xml":
                    continue
                if z2.read(n) != items[n]:
                    raise AssertionError("part %s is not byte-identical" % n)
            with zipfile.ZipFile(a.docx) as z0:
                assert z2.read("word/document.xml") != z0.read("word/document.xml"), \
                    "document.xml did not change"
        os.replace(tmp, a.docx)
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)
    print("   written (%d extents widened)" % len(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
