#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
The measuring instrument: turn a 600-dpi crop of the PRINTED page into ink bands, decide
which are text, and report the smallest one in points.

1 px = 72/600 pt = 0.12 pt.

Nothing here infers a size from canvas units. The only model in the file is the final
ink-height -> nominal-font-size step (`GLYPH_MODEL`), which is stated explicitly and
calibrated empirically in REPORT.md.

Rule for TEXT vs MARK -- a band counts as text only when it can be explained as a run of
glyphs of ONE type size:

  MARK, definitely
    M1  a stroke thinner than 0.25 pt (2 px) -- no glyph stem is that thin
    M2  a long thin horizontal rule (<= 3 px tall)
    M3  a single solid compact stamp (fill ratio >= 0.78)
    M4  a single solid elongated stamp (fill ratio >= 0.55 and one axis >= 3x the other)
    M5  a member of a REPEATED STAMP family: >= 6 components of one size class on a
        regular pitch (the 36 minor-tick case)
    M6  a member of a COLLINEAR PATTERN family: >= 4 components of one size class lying
        on a straight line (dashed / dotted / ticked rules, dashed diagonals)
    M7  a sub-1.5 pt speck cluster: too small to hold a glyph's stroke and its counter

  TEXT, only if ALL hold
    T1  glyph structure: a counter (enclosed background) or a stroke <= 0.30 of the
        height; fill ratio <= 0.72
    T2  one baseline: for runs of >= 2 components, the bottoms of the tall components
        agree to within max(2 px, 0.12 x height)
    T3  one type size: tallest/shortest component <= 2.8
    T4  letter spacing: the largest gap <= 3.5 x the median gap
    T5  size: >= 16 px (1.92 pt) for an isolated single component, >= 12 px for a run

  UNSURE otherwise -- the instrument says "I cannot tell" instead of guessing.

Known failure modes are listed in REPORT.md.
"""
from __future__ import annotations

import math

import numpy as np

PT_PER_PX = 72.0 / 600.0          # 0.12 pt at 600 dpi
PX_PER_PT = 600.0 / 72.0

BG_PEAK_MIN = 0.16                # below this the crop has no dominant background
MERGE_GAP_ROWS = 2                # blank rows <= this do not split a band
CHAIN_GAP_FRAC = 1.4              # bbox gap <= this * median component width chains
CHAIN_GAP_MIN = 6
STAMP_MIN_MEMBERS = 6             # identical components on a regular pitch
PATTERN_MIN_MEMBERS = 4           # identical components on a straight line
MIN_RUN_PX = 3
SPECK_PX = 12                     # below this a shape cannot hold stroke + counter
SPECK_AREA = 25
MIN_SINGLE_GLYPH_PX = 24          # 2.88 pt.  At the 6.0 pt floor the smallest legitimate
                                  # ink of a 6 pt label is its x-height (~3.1 pt); below
                                  # 2.9 pt an isolated shape cannot be told from a mark,
                                  # so it is reported UNSURE rather than guessed.
MIN_RUN_PX_TEXT = 12

# ink-height / nominal-size, per glyph class. Calibrated in REPORT.md against Canvas
# figures whose SVG states the font size: the MODE of the glyph heights in a printed line
# is the height of the commonest glyph class, and the ratio turns it into an em.
GLYPH_MODEL = {
    "x_height": 0.52,   # the modal glyph is lowercase with no ascender or descender
    "cap_height": 0.72,  # the modal glyph is a capital, a digit, or an ascender
}


# ---------------------------------------------------------------------------
def ink_mask(gray: np.ndarray) -> tuple:
    """Threshold relative to the crop's OWN background.

    The paper tint of these figures is not white (#F4EFE7 / #F7F5EB), so a fixed
    'dark < 128' rule would eat half the palette. The background is the histogram mode;
    ink is anything at least T grey levels away from it, in either polarity, so white
    text on a dark panel is measured the same way as black text on paper.
    """
    hist = np.bincount(gray.ravel(), minlength=256).astype(np.float64)
    n = gray.size
    bg = int(hist.argmax())
    peak = hist[bg] / n
    p1, p99 = np.percentile(gray, 1.0), np.percentile(gray, 99.0)
    contrast = max(bg - p1, p99 - bg)
    T = max(30.0, 0.30 * contrast)
    ink = (gray < bg - T) | (gray > bg + T)
    return ink, {"bg": bg, "peak_frac": round(float(peak), 4),
                 "p1": float(p1), "p99": float(p99),
                 "thresh": round(float(T), 1),
                 "ink_frac": round(float(ink.mean()), 4)}


def _components(mask: np.ndarray) -> list:
    """8-connected components of a boolean band, with bbox, area and hole count."""
    from scipy import ndimage
    lab, k = ndimage.label(mask, structure=np.ones((3, 3), dtype=np.int8))
    if k == 0:
        return []
    objs = ndimage.find_objects(lab)
    areas = ndimage.sum(mask, lab, index=range(1, k + 1))
    out = []
    cross = np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]])
    for i, sl in enumerate(objs):
        if sl is None:
            continue
        ys, xs = sl
        h = ys.stop - ys.start
        w = xs.stop - xs.start
        if h < 1 or w < 1:
            continue
        area = float(areas[i])
        sub = (lab[sl] == (i + 1))
        inv = ~sub
        hlab, hk = ndimage.label(inv, structure=cross)
        border = set(hlab[0, :]) | set(hlab[-1, :]) | set(hlab[:, 0]) | set(hlab[:, -1])
        holes = sum(1 for r in range(1, hk + 1) if r not in border)
        out.append({"y0": int(ys.start), "y1": int(ys.stop - 1),
                    "x0": int(xs.start), "x1": int(xs.stop - 1),
                    "h": int(h), "w": int(w), "area": area,
                    "solid": round(area / (w * h), 4), "holes": int(holes)})
    return out


def _bands(ink: np.ndarray, merge_gap: int = MERGE_GAP_ROWS) -> list:
    rows = ink.any(axis=1)
    bands = []
    start, gap = None, 0
    for y, v in enumerate(rows):
        if v:
            if start is None:
                start = y
            gap = 0
        elif start is not None:
            gap += 1
            if gap > merge_gap:
                bands.append((start, y - gap))
                start = None
    if start is not None:
        bands.append((start, len(rows) - 1 - gap))
    return [(a, b) for a, b in bands if b - a + 1 >= MIN_RUN_PX]


def _chain(comps: list, med_w: float) -> list:
    gap_lim = max(CHAIN_GAP_MIN, CHAIN_GAP_FRAC * med_w)
    comps = sorted(comps, key=lambda c: (c["x0"], c["y0"]))
    runs, cur = [], [comps[0]]
    for c in comps[1:]:
        prev = cur[-1]
        gap = c["x0"] - max(p["x1"] for p in cur)
        vo = min(prev["y1"], c["y1"]) - max(prev["y0"], c["y0"]) + 1
        vo_frac = vo / max(1, min(prev["h"], c["h"]))
        if gap <= gap_lim and vo_frac >= 0.45:
            cur.append(c)
        else:
            runs.append(cur)
            cur = [c]
    runs.append(cur)
    return runs


def _stroke(c: dict) -> float:
    return c["area"] / max(1.0, (c["w"] + c["h"]))


# ---------------------------------------------------------------------------
def stamp_families(comps: list) -> dict:
    """Size classes repeated >= STAMP_MIN_MEMBERS times on a regular pitch: minor ticks,
    dotted rules, scatter markers. Returns {size_key: set(indices)}."""
    from collections import defaultdict
    groups = defaultdict(list)
    for i, c in enumerate(comps):
        if c["h"] < 2 or c["w"] < 1 or c["area"] > 900:
            continue
        groups[(round(c["w"]), round(c["h"]))].append(i)
    keys = sorted(groups)
    merged, used = [], set()
    for k in keys:
        if k in used:
            continue
        fam = list(groups[k])
        for k2 in keys:
            if k2 == k or k2 in used:
                continue
            if abs(k2[0] - k[0]) <= 1 and abs(k2[1] - k[1]) <= 1:
                fam += groups[k2]
                used.add(k2)
        used.add(k)
        merged.append((k, fam))
    out = {}
    for k, fam in merged:
        if len(fam) < STAMP_MIN_MEMBERS:
            continue
        xs = sorted(comps[i]["x0"] for i in fam)
        ys = sorted(comps[i]["y0"] for i in fam)
        px, py = np.diff(xs), np.diff(ys)
        reg_x = len(px) >= 2 and px.mean() > 0 and px.std() / max(1e-9, px.mean()) <= 0.15
        reg_y = len(py) >= 2 and py.mean() > 0 and py.std() / max(1e-9, py.mean()) <= 0.15
        if reg_x or reg_y:
            out[k] = set(fam)
    return out


def pattern_families(comps: list) -> set:
    """Small components of one size class lying on a straight line: dashes, dots, ticks,
    arrow heads along a leader. Returns the set of component indices."""
    from collections import defaultdict
    groups = defaultdict(list)
    for i, c in enumerate(comps):
        if c["area"] > 900 or c["h"] > 40:
            continue
        groups[(round(c["w"] / 2.0), round(c["h"] / 2.0))].append(i)
    flagged = set()
    for _k, idx in groups.items():
        if len(idx) < PATTERN_MIN_MEMBERS:
            continue
        idx = idx[:80]
        pts = [((comps[i]["x0"] + comps[i]["x1"]) / 2.0,
                (comps[i]["y0"] + comps[i]["y1"]) / 2.0) for i in idx]
        m = len(pts)
        for a in range(m):
            for b in range(a + 1, m):
                dx, dy = pts[b][0] - pts[a][0], pts[b][1] - pts[a][1]
                L = math.hypot(dx, dy)
                if L < 8:
                    continue
                nx, ny = -dy / L, dx / L
                on = [idx[t] for t in range(m)
                      if abs((pts[t][0] - pts[a][0]) * nx
                             + (pts[t][1] - pts[a][1]) * ny) <= 1.5]
                if len(on) >= PATTERN_MIN_MEMBERS:
                    flagged.update(on)
    return flagged


# ---------------------------------------------------------------------------
def classify_run(run: list, stamps: dict, pattern: set) -> tuple:
    hs = np.array([c["h"] for c in run], float)
    ws = np.array([c["w"] for c in run], float)
    solids = np.array([c["solid"] for c in run], float)
    strokes = np.array([_stroke(c) for c in run], float)
    holes = sum(c["holes"] for c in run)
    n = len(run)
    y0 = min(c["y0"] for c in run)
    y1 = max(c["y1"] for c in run)
    x0 = min(c["x0"] for c in run)
    x1 = max(c["x1"] for c in run)
    h, w = y1 - y0 + 1, x1 - x0 + 1
    med_h, med_w = float(np.median(hs)), float(np.median(ws))
    med_solid = float(np.median(solids))

    # baseline coherence: bottoms of the tall components (>= 0.6 x tallest)
    thr = 0.6 * hs.max()
    tall = [c for c in run if c["h"] >= thr]
    bottoms = np.array([c["y1"] for c in tall], float)
    base_mad = float(np.median(np.abs(bottoms - np.median(bottoms)))) if len(tall) else 0.0
    has_desc = any(c["y1"] > np.median(bottoms) + max(2, 0.10 * h)
                   for c in run) if len(tall) else False

    feat = {"n": n, "h_px": h, "w_px": w, "med_h": round(med_h, 1),
            "med_w": round(med_w, 1), "med_solid": round(med_solid, 3),
            "holes": holes, "h_ratio": round(float(hs.max() / max(1e-9, hs.min())), 2),
            "stroke_frac": round(float(np.median(strokes) / max(1e-9, med_h)), 3),
            "base_mad": round(base_mad, 2), "desc": bool(has_desc),
            "heights": [int(x) for x in hs],
            "x0": int(x0), "y0": int(y0), "x1": int(x1), "y1": int(y1)}

    fam_hits = 0
    for c in run:
        for k in stamps:
            if abs(c["w"] - k[0]) <= 1 and abs(c["h"] - k[1]) <= 1:
                fam_hits += 1
                break
    if fam_hits >= max(1, int(0.8 * n)):
        return "MARK", ("repeated identical stamp: size class repeated >= %d times on a "
                        "regular pitch" % STAMP_MIN_MEMBERS), feat
    if sum(1 for c in run if id(c) in pattern) >= max(1, int(0.8 * n)):
        return "MARK", ("collinear pattern: >= %d identical components on one straight "
                        "line -- dashes / dots / ticks" % PATTERN_MIN_MEMBERS), feat

    # definite marks
    if min(med_w, h) <= 2:
        return "MARK", "sub-0.25 pt stroke: thinner than any glyph stem at 6 pt", feat
    if h <= 3 and w >= 12:
        return "MARK", "long thin rule", feat
    if n == 1 and med_solid >= 0.78 and w / max(1, h) <= 3:
        return "MARK", "single solid compact stamp (filled dot / square)", feat
    if n == 1 and med_solid >= 0.55 and (w >= 3 * h or h >= 3 * w):
        return "MARK", "single solid elongate stamp (filled bar)", feat

    # speck gate
    if h < SPECK_PX or float(np.median([c["area"] for c in run])) < SPECK_AREA:
        return "MARK", ("sub-1.5 pt speck cluster (h=%d px = %.2f pt): too small to carry "
                        "a glyph stroke and its counter" % (h, h * PT_PER_PX)), feat

    # text tests
    if n == 1:
        if h < MIN_SINGLE_GLYPH_PX:
            return "UNSURE", ("isolated shape of %.2f pt -- too little to tell a glyph "
                              "from a mark" % (h * PT_PER_PX)), feat
        if med_solid > 0.62:
            return "MARK", "single solid shape, no counter and no thin stroke", feat
        if holes >= 1 or (feat["stroke_frac"] <= 0.26 and w >= 0.30 * h):
            return "TEXT", "isolated glyph: counter or thin stroke, not a filled stamp", feat
        return "UNSURE", "single shape, glyph-like neither by counter nor by stroke", feat
    if h < MIN_RUN_PX_TEXT:
        return "UNSURE", "run shorter than 1.44 pt -- cannot be judged", feat
    if med_solid > 0.72:
        return "MARK", "solid components (fill ratio %.2f) -- blocks, not glyphs" \
                       % med_solid, feat
    if feat["h_ratio"] > 2.8:
        return "UNSURE", "component heights vary by %.1fx -- not one type size" \
                         % feat["h_ratio"], feat
    if n >= 3 and base_mad > max(2.0, 0.12 * h):
        return "UNSURE", ("no shared baseline: component bottoms scatter by %.1f px "
                          "-- not a line of type" % base_mad), feat
    gaps = np.diff(sorted(c["x0"] for c in run))
    if n >= 3 and len(gaps) >= 2 and gaps.max() > 3.5 * max(1.0, np.median(gaps)):
        return "UNSURE", "gaps irregular: %.0f px vs median %.0f px -- not letter spacing" \
                         % (gaps.max(), np.median(gaps)), feat
    if n >= 3:
        return "TEXT", "run of %d glyph-like components on one baseline" % n, feat
    if n == 2 and min(hs) >= 8 and base_mad <= 2.0:
        return "TEXT", "two glyph-like components on one baseline", feat
    return "UNSURE", "too little structure to call", feat


# ---------------------------------------------------------------------------
def group_lines(runs: list) -> list:
    """Group runs that sit on one printed line (their vertical ranges overlap)."""
    rs = sorted(runs, key=lambda r: r["y0"])
    lines = []
    for r in rs:
        placed = False
        for ln in lines:
            a0 = min(x["y0"] for x in ln)
            a1 = max(x["y1"] for x in ln)
            ov = min(a1, r["y1"]) - max(a0, r["y0"]) + 1
            if ov >= 0.6 * min(a1 - a0 + 1, r["h_px"]):
                ln.append(r)
                placed = True
                break
        if not placed:
            lines.append([r])
    out = []
    for ln in lines:
        y0 = min(x["y0"] for x in ln)
        y1 = max(x["y1"] for x in ln)
        out.append({"y0": y0, "y1": y1, "extent_px": y1 - y0 + 1,
                    "runs": ln, "n_runs": len(ln),
                    "text_runs": [x for x in ln if x["kind"] == "TEXT"],
                    "x0": min(x["x0"] for x in ln),
                    "x1": max(x["x1"] for x in ln)})
    return out


def _line_ratio(line: dict, all_extents: list, fig_modes: list = ()) -> tuple:
    """Turn the printed line into a nominal font size, from measurements only.

    The stable quantity in a printed line is the MODE of the glyph heights: in a lowercase
    line almost every glyph has x-height, in a caps or numeric line almost every glyph has
    cap height.  Ascenders sit only ~3 % above caps, while x-height is ~72 % of caps, so a
    component at least 1.30x the mode proves the mode is x-height and not cap height.
    Brackets and slashes run taller than either and are ignored by using the mode.

    This replaced an earlier rule that divided the whole band (ascender-to-descender) by
    0.95.  That rule produced a false FAIL on an all-caps figure whose caps measure 36 px
    and whose one parenthesis measures 42 px: the band said 5.3 pt where the caps say
    6.0 pt.  The pixels were read at 1:1 to establish this, and the mode rule reproduces
    both the all-caps figure (6.0 pt) and the mixed-case synthesis figure (6.2 pt against
    6.15 pt from its own SVG)."""
    hs = sorted(line["heights"])
    if not hs:
        return None, None, None
    hmax = max(hs)
    keep = [h for h in hs if h >= max(4, 0.35 * hmax)]
    # A printed line usually mixes two glyph classes: x-height (most glyphs) and caps or
    # ascenders.  Ascenders sit only ~3 % above caps, but x-height is ~72 % of caps, so a
    # height at or below hmax/1.30 cannot be a cap or an ascender -- it is the x-height
    # class.  Taking the median of THAT class stops the two clusters from averaging into a
    # size that belongs to neither, which is what made the mode read 5.5 pt on a figure
    # whose authored label is 6.14 pt.
    lower = [h for h in keep if h <= hmax / 1.30]
    if len(lower) >= max(3, 0.20 * len(keep)):
        return GLYPH_MODEL["x_height"], "x_height", float(np.median(lower))
    buckets = {}
    for h in keep:
        buckets[h // 2] = buckets.get(h // 2, 0) + 1
    best = max(buckets.items(), key=lambda kv: (kv[1], kv[0]))[0]
    near = [h for h in keep if h // 2 == best]
    mode = float(np.median(near))
    # Uniform line: all caps/digits (cap height) or all lowercase with no ascender
    # (x-height).  cap / x-height = 0.72 / 0.52 = 1.38, so if the SAME figure also prints
    # a line whose glyph size is 1.25-1.45x this one, this line is the x-height member of
    # that type size.  Scoring the three candidate rules against the authored sizes of 71
    # Canvas figures (see pick_rule.py) chose this one: 93.0 % of figures within 20 %,
    # against 80.3 % for always assuming cap height.
    for m in fig_modes:
        if m and m != mode and 1.25 <= m / mode <= 1.45:
            return GLYPH_MODEL["x_height"], "x_height(corroborated)", mode
    return GLYPH_MODEL["cap_height"], "cap_height", mode


def _extend_line(ink: np.ndarray, x0: int, x1: int, y0: int, y1: int,
                 max_grow: int | None = None) -> tuple:
    """Grow a line's band up and down over contiguous ink in the line's own x-span.

    A run-based grouping stops at the run's component boxes; a descender can sit in a
    component that chained into an ambiguous run. The printed band of the LINE is what
    the reader sees, so it is measured from the ink itself. Growth is capped because a
    table rule crossing the x-span leaves no blank row to stop at."""
    H, _W = ink.shape
    slab = ink[:, max(0, x0):max(1, x1)]
    rows = slab.any(axis=1)
    if max_grow is None:
        max_grow = 12
    top, gap = y0, 0
    y = y0 - 1
    while y >= 0 and y >= y0 - max_grow:
        if rows[y]:
            top, gap = y, 0
        else:
            gap += 1
            if gap > 1:
                break
        y -= 1
    bot, gap = y1, 0
    y = y1 + 1
    while y < H and y <= y1 + max_grow:
        if rows[y]:
            bot, gap = y, 0
        else:
            gap += 1
            if gap > 1:
                break
        y += 1
    return int(top), int(bot)


def analyse(gray: np.ndarray) -> dict:
    """Full measurement of one crop. Everything returned is measured, not assumed."""
    H, W = gray.shape
    ink, meta = ink_mask(gray)
    result = {"size_px": [int(W), int(H)], "ink": meta, "runs": [], "lines": [],
              "photographic": meta["peak_frac"] < BG_PEAK_MIN}
    bands = _bands(ink)
    allcomps = []
    band_runs = []
    for (a, b) in bands:
        sub = ink[a:b + 1, :]
        comps = _components(sub)
        if not comps:
            continue
        for c in comps:
            c["y0"] += a
            c["y1"] += a
        allcomps.extend(comps)
        med_w = float(np.median([c["w"] for c in comps]))
        band_runs.extend(_chain(comps, med_w))
    stamps = stamp_families(allcomps)
    pattern = pattern_families(allcomps)
    result["stamp_families"] = [{"w": k[0], "h": k[1], "members": len(v)}
                                for k, v in stamps.items()]
    result["pattern_components"] = len(pattern)
    for run in band_runs:
        kind, why, feat = classify_run(run, stamps, pattern)
        feat.update({"kind": kind, "why": why, "h_pt": round(feat["h_px"] * PT_PER_PX, 3)})
        result["runs"].append(feat)
    result["runs"].sort(key=lambda r: r["h_px"])
    texts = [r for r in result["runs"] if r["kind"] == "TEXT"]
    # A line's type size comes from the heights of ALL its glyph-like components, and an
    # ascender or a descender very often lands in a run the classifier could not call
    # (mixed heights inside one word). Grouping on TEXT runs alone split such a line and
    # produced a fragment whose mode was an ascender, which read as 5.0 pt on a figure
    # whose real labels are 6.2 pt. Ambiguous runs are therefore grouped in as well, but
    # only when they are of a size that could belong to the line at all.
    if texts:
        ref = float(np.median([r["h_px"] for r in texts]))
        pool = [r for r in result["runs"]
                if r["kind"] in ("TEXT", "UNSURE") and r["h_px"] <= 3.0 * ref]
        lines = group_lines(pool)
    else:
        lines = []
    kept = []
    for ln in lines:
        if not ln["text_runs"]:
            continue
        ln["baseline"] = int(np.median([r["y1"] for r in ln["runs"]]))
        span0 = ln["y1"] - ln["y0"] + 1
        ey0, ey1 = _extend_line(ink, ln["x0"], ln["x1"], ln["y0"], ln["y1"],
                                max_grow=max(8, int(0.6 * span0)))
        ln["y0"], ln["y1"] = ey0, ey1
        ln["extent_px"] = ey1 - ey0 + 1
        ln["heights"] = [h for r in ln["runs"] for h in r["heights"]]
        ln["n_components"] = sum(r["n"] for r in ln["runs"])
        ln["n_text_components"] = sum(r["n"] for r in ln["text_runs"])
        ln["w_px"] = max(r["w_px"] for r in ln["runs"])
        # A line governed by a single dot is not evidence of text -- but a whole word whose
        # letters touch is also ONE component, and so is a lone axis digit, which is real
        # text. The run classifier has already rejected dots (min glyph size, solidity,
        # stroke), so a line carrying a TEXT run is adjudicable; the flag is kept for the
        # report so single-component lines can be audited separately.
        ln["adjudicable"] = True
        ln["single_component"] = (ln["n_components"] == 1)
        kept.append(ln)
    lines = kept
    for ln in lines:                       # pass 1: each line's own glyph size
        ratio, cls, mode = _line_ratio(ln, [], [])
        ln["mode_px"] = mode
        ln["glyph_class"] = cls
    fig_modes = [ln["mode_px"] for ln in lines if ln["mode_px"]]
    for ln in lines:                       # pass 2: cap vs x-height, figure-relative
        ratio, cls, mode = _line_ratio(ln, [], fig_modes)
        ln["ratio"] = ratio
        ln["glyph_class"] = cls
        ln["mode_px"] = round(mode, 1) if mode else None
        ln["extent_pt"] = round(ln["extent_px"] * PT_PER_PX, 3)
        ln["mode_pt"] = round(mode * PT_PER_PX, 3) if mode else None
        ln["nominal_pt"] = round(mode * PT_PER_PX / ratio, 3) if mode else None
    result["lines"] = lines
    return result


def smallest_text(result: dict) -> dict:
    """The reportable answer: smallest run we are confident is text, and the nominal size
    of the line that carries it."""
    texts = [r for r in result["runs"] if r["kind"] == "TEXT"]
    unsure = [r for r in result["runs"] if r["kind"] == "UNSURE"]
    smallest_unsure = min((r["h_pt"] for r in unsure), default=None)
    lines = result.get("lines") or []
    if not texts or not lines:
        return {"pt": None, "confidence": "no-text", "candidates": [],
                "smallest_unsure_pt": smallest_unsure, "nominal_pt": None,
                "glyph_class": None, "line_extent_pt": None,
                "note": ("no band classified as text: %d mark(s), %d ambiguous"
                         % (sum(1 for r in result["runs"] if r["kind"] == "MARK"),
                            len(unsure)))}
    eligible = [ln for ln in lines if ln.get("adjudicable") and ln.get("nominal_pt")]
    isolated = [ln for ln in lines if not ln.get("adjudicable")]
    pool = eligible or [ln for ln in lines if ln.get("nominal_pt")]
    if not pool:
        return {"pt": None, "confidence": "no-text", "candidates": [],
                "smallest_unsure_pt": smallest_unsure, "nominal_pt": None,
                "glyph_class": None, "line_extent_pt": None,
                "note": "text bands found but none could be turned into a size"}
    # the worst line is the one with the smallest estimated nominal size
    worst = min(pool, key=lambda ln: ln["nominal_pt"])
    tr = worst["text_runs"] or worst["runs"]
    hmin = min(r["h_px"] for r in tr)
    small = [r for r in tr if r["h_px"] == hmin]
    ties = [ln for ln in pool if ln["nominal_pt"] <= worst["nominal_pt"] * 1.15]
    if len(ties) == 1 and len(small) == 1:
        conf = "exact"
    else:
        conf = "range"
    return {"pt": round(worst["extent_pt"], 3), "confidence": conf,
            "nominal_pt": worst["nominal_pt"], "glyph_class": worst["glyph_class"],
            "mode_pt": worst.get("mode_pt"), "mode_px": worst.get("mode_px"),
            "line_extent_pt": worst["extent_pt"],
            "smallest_run_pt": round(hmin * PT_PER_PX, 3),
            "isolated_line_pt": (min((ln["extent_pt"] for ln in isolated), default=None)),
            "candidates": [{"h_px": r["h_px"], "h_pt": r["h_pt"], "n": r["n"],
                            "x0": r["x0"], "y0": r["y0"], "why": r["why"]}
                           for r in small],
            "range_pt": [round(min(ln["nominal_pt"] for ln in pool), 3),
                         round(max(ln["nominal_pt"] for ln in pool), 3)],
            "n_text_runs": len(texts), "n_lines": len(lines),
            "n_eligible_lines": len(eligible),
            "smallest_unsure_pt": smallest_unsure,
            "line_runs": [{"h_px": r["h_px"], "n": r["n"], "x0": r["x0"], "y0": r["y0"]}
                          for r in tr]}
