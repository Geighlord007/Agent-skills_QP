"""diagram_kit — the drawn-figure API for the `synbio-editorial` style.

Consolidates six generations of drawing kits from the source corpus
(`_figlib`, `_figkit`, `figkit`, `_timeline_kit`, `_ws5_kit`, `_fig4lib`) into one
API on top of `design/schematic.py`'s `Canvas`, which already provides the core
primitives, the scale law and the SVG→PNG rasteriser.

What this module adds, and why each exists:

  axes          linear_axis / log_axis    charts need them; 5 of 6 old kits grew one
  engraving     hatch                     the "engraved plate" half of the style
  matrices      mark_dot / mark_sq        STYLE.md §8.6: score cells as MARKS, not
                                          colours, so figures survive greyscale
  tabulation    table                     tables are legitimate figures (regulatory
                                          registers, spec tables, assumption logs)
  series        legend                    direct labels are preferred; legend is the
                                          fallback when labels would collide
  furniture     furniture()               caption + source in one call, so a figure
                                          cannot ship without provenance
  QA            report()                  bounds / overflow / collision checks and a
                                          single layout verdict

Usage
-----
    import sys; sys.path.insert(0, "<skill>/tools")
    from diagram_kit import Diagram, MOODBOARD

    d = Diagram(780, 420, title="Market build-up", accent=MEADOW)
    d.linear_axis(60, 720, 330, ticks=[0, 50, 100], label="USD m, FY2025")
    d.hatch("moss", "diag")
    ...
    d.furniture("Figure 3 — Market build-up.", "Source: Company filings · Retrieved 2026-09-11")
    print(d.report())            # layout verdict
    d.save("market_buildup")     # -> .svg + .png at 300 dpi, canvas asserted

Run `python diagram_kit.py` for a self-test that draws one figure per family and
verifies the canvas contract on each.
"""
from __future__ import annotations

import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_TOOLS = os.path.abspath(os.path.join(_HERE, "..", "..", "tools"))
if _TOOLS not in sys.path:
    sys.path.insert(0, _TOOLS)

from design import brand as B                    # noqa: E402
from design.schematic import (                   # noqa: E402
    Canvas, Node, MIN_ONPAGE_PT, TARGET_CANVAS_W,
)

# Semantic accents. Assign by MEANING, never by taste -- see STYLE.md §2.
NATURAL = B.MOSS
ENGINEERED = B.CLAY
EVIDENCE = B.ROSE
NEUTRAL = B.SEED_BROWN
POSITIVE = B.MEADOW

SERIES_SYNBIO = B.SERIES_SYNBIO
SERIES_FINANCE = B.SERIES_FINANCE

MOODBOARD = {
    "paper": B.PAPER,
    "ink": B.INK,
    "muted": B.INK_MUTED,
    "natural": NATURAL,
    "engineered": ENGINEERED,
    "evidence": EVIDENCE,
    "neutral": NEUTRAL,
    "financial": {"ink": B.JPM_INK, "bronze": B.JPM_BRONZE,
                  "sky": B.JPM_SKY, "slate": B.JPM_SLATE, "paper": B.JPM_PAPER},
}


class Diagram(Canvas):
    """Canvas + the figure primitives the six source kits each grew separately."""

    # ------------------------------------------------------------------ axes
    def linear_axis(self, x0, x1, y, ticks, label="", label_anchor="start",
                    tick_len=5, minor=0):
        """Horizontal linear axis with ticks and an optional unit label.

        `label` must state units AND period (STYLE.md §6): "USD m, FY2023-FY2030",
        never a bare "Value".
        """
        self.line(x0, y, x1, y, width=0.7)
        for i in range(len(ticks) - 1):
            if minor:
                step = (ticks[i + 1] - ticks[i]) / (minor + 1)
                for k in range(1, minor + 1):
                    xv = ticks[i] + step * k
                    xp = x0 + (xv - ticks[0]) / (ticks[-1] - ticks[0]) * (x1 - x0)
                    self.line(xp, y, xp, y + tick_len * 0.55, width=0.5)
        for t in ticks:
            xp = x0 + (t - ticks[0]) / (ticks[-1] - ticks[0]) * (x1 - x0)
            self.line(xp, y, xp, y + tick_len, width=0.7)
            self.text(xp, y + tick_len + 11, self._tick_label(t), size=10.5,
                      family="mono", fill=B.INK_MUTED, anchor="middle")
        if label:
            self.text(x0 if label_anchor == "start" else (x0 + x1) / 2, y + tick_len + 26,
                      label, size=10.5, family="mono", fill=B.INK_MUTED,
                      anchor=label_anchor)
        return y

    def log_axis(self, x0, x1, y, lo, hi, ticks, minor=True, label=""):
        """Log10 horizontal axis, for price ladders spanning orders of magnitude."""
        import math

        def pos(v):
            return x0 + (math.log10(v) - math.log10(lo)) / (
                math.log10(hi) - math.log10(lo)) * (x1 - x0)

        self.line(x0, y, x1, y, width=0.7)
        if minor:
            d = 10 ** math.floor(math.log10(lo))
            while d <= hi:
                for k in range(2, 10):
                    v = d * k
                    if lo <= v <= hi:
                        self.line(pos(v), y, pos(v), y + 3, width=0.45)
                d *= 10
        for t in ticks:
            self.line(pos(t), y, pos(t), y + 5, width=0.7)
            self.text(pos(t), y + 16, self._tick_label(t), size=10.5, family="mono",
                      fill=B.INK_MUTED, anchor="middle")
        if label:
            self.text(x0, y + 31, label, size=10.5, family="mono", fill=B.INK_MUTED)
        return y

    @staticmethod
    def _tick_label(v):
        if v >= 1_000_000:
            return "%gM" % (v / 1_000_000)
        if v >= 1000:
            return "%gk" % (v / 1000)
        return "%g" % v

    # ------------------------------------------------------------- engraving
    def hatch(self, color: str, key: str = "diag", pitch: float = 5.0, width: float = 0.9):
        """Register an SVG <pattern> for engraved fills. Returns the pattern id.

        The "vintage engraving" half of STYLE.md §1: cross-hatch reads as plate work
        and costs no colour. Use it instead of a second hue.
        """
        keys = {
            "diag": "M0,%d l%d,-%d" % (pitch, pitch, pitch),
            "cross": "M0,%d l%d,-%d M0,0 l%d,%d" % (pitch, pitch, pitch, pitch, pitch),
            "horiz": "M0,%d l%d,0" % (pitch, pitch),
            "dots": None,
        }
        body = keys.get(key, keys["diag"])
        if body is None:
            inner = ('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="%s"/>'
                     % (pitch / 2, pitch / 2, width * 0.8, color))
        else:
            inner = ('<path d="%s" stroke="%s" stroke-width="%.2f" fill="none"/>'
                     % (body, color, width))
        pid = "hatch-%s-%s" % (key, color.lstrip("#"))
        pat = ('<pattern id="%s" width="%.1f" height="%.1f" patternUnits="userSpaceOnUse">'
               '%s</pattern>' % (pid, pitch, pitch, inner))
        self._defs = getattr(self, "_defs", [])
        if not any(pid in d for d in self._defs):
            self._defs.append(pat)
        return "url(#%s)" % pid

    # --------------------------------------------------------------- matrices
    def mark_dot(self, cx, cy, r=4.2, color=None, filled=True):
        """Score mark: filled circle. See mark_sq for the two-level variant."""
        self.dot(cx, cy, r=r, filled=filled, accent=color or B.INK)

    def mark_sq(self, cx, cy, s=13.0, color=None, filled=True, half=False):
        """Score mark: square, optionally half-filled for a 2-of-3 scale.

        Marks rather than colours (STYLE.md §8.6) so a weighted matrix survives
        greyscale printing and colour blindness.
        """
        color = color or B.INK
        x, y = cx - s / 2, cy - s / 2
        self.line(x, y, x + s, y, accent=color, width=0.8)
        self.line(x + s, y, x + s, y + s, accent=color, width=0.8)
        self.line(x + s, y + s, x, y + s, accent=color, width=0.8)
        self.line(x, y + s, x, y, accent=color, width=0.8)
        if filled:
            self.bar(x, y, s, s, filled=True, accent=color)
        elif half:
            self.bar(x, y + s / 2, s, s / 2, filled=True, accent=color)

    # ------------------------------------------------------------- tabulation
    def table(self, x, y, col_w, header, rows, row_h=23, header_h=27, size=13,
              header_fill=None):
        """Hairline table. Horizontal rules only -- no vertical rules, ever.

        A table is a legitimate figure (STYLE.md §8.3, §8.6): registries, notice
        grids, specification and assumption tables.
        """
        total = sum(col_w)
        cy = y
        if header_fill:
            self.bar(x, cy, total, header_h, filled=True, accent=header_fill)
        for i, h in enumerate(header):
            cx = x + sum(col_w[:i]) + 6
            self.text(cx, cy + header_h * 0.68, str(h).upper(), size=size * 0.82,
                      family="mono", fill=B.INK_MUTED)
        cy += header_h
        self.line(x, cy, x + total, cy, width=0.9)
        for r in rows:
            cy += row_h
            self.line(x, cy, x + total, cy, width=0.45)
            for i, cell in enumerate(r):
                cx = x + sum(col_w[:i]) + 6
                fam = "mono" if i > 0 else "sans"
                self.text(cx, cy - row_h * 0.32, str(cell), size=size, family=fam)
        return cy

    # ----------------------------------------------------------------- series
    def legend(self, x, y, items, size=10.5, gap=18.0, swatch=11.0, row_gap=18.0):
        """Swatch + label list. Fallback only: prefer direct labels (STYLE.md §5.4)."""
        cy = y
        for label, color in items:
            self.bar(x, cy - swatch * 0.7, swatch, swatch * 0.7, filled=True, accent=color)
            self.text(x + swatch + 7, cy, label, size=size, family="mono",
                      fill=B.INK_MUTED)
            cy += row_gap
        return cy

    # --------------------------------------------------------------- furniture
    def furniture(self, caption, source, cap_size=13, src_size=12.5):
        """Caption + source in one call, so a figure cannot ship without provenance.

        STYLE.md §9: a figure missing its source line is incomplete, however good
        it looks.
        """
        self.caption(caption, size=cap_size)
        self.source(source, size=src_size)

    # ---------------------------------------------------------------------- QA
    # Canvas keeps `self.parts` as a flat list of SVG fragments and has no geometry
    # model, so bounds checking is impossible without recording it. We record it here
    # by overriding the four emitting primitives. This was a real defect: an earlier
    # version of this method called `overflows()`/`collisions()` via getattr and
    # swallowed the AttributeError, so it reported "ok" while checking only one thing.
    def _rec(self, x0, y0, x1, y1, kind, label=""):
        self._items = getattr(self, "_items", [])
        self._items.append((float(x0), float(y0), float(x1), float(y1), kind, label))

    @staticmethod
    def _tw(s, size):
        """Estimated text width in canvas units.

        An ESTIMATE, deliberately: the face's real metrics need the font file, and
        this must work without it. Roughly right is enough to catch a label running
        off the canvas, which is what this is for. Do not use it to typeset.
        """
        return len(str(s)) * size * 0.55

    def text(self, x, y, s, size=13, family="serif", fill=None, anchor="start",
             italic=False, tracking=None, weight=None):
        super().text(x, y, s, size=size, family=family, fill=fill, anchor=anchor,
                     italic=italic, tracking=tracking, weight=weight)
        w = self._tw(s, size)
        x0 = x - w if anchor in ("middle", "end") else x
        self._rec(x0, y - size * 0.80, x0 + w, y + size * 0.25, "text", str(s))

    def line(self, x1, y1, x2, y2, accent=None, width=0.8, dashed=False):
        super().line(x1, y1, x2, y2, accent=accent, width=width, dashed=dashed)
        self._rec(min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2), "line")

    def bar(self, x, y, w, h, filled=True, accent=None, dashed=False):
        super().bar(x, y, w, h, filled=filled, accent=accent, dashed=dashed)
        self._rec(x, y, x + w, y + h, "bar")

    def dot(self, cx, cy, r=5, filled=True, accent=None):
        super().dot(cx, cy, r=r, filled=filled, accent=accent)
        self._rec(cx - r, cy - r, cx + r, cy + r, "dot")

    def svg(self) -> str:
        """Canvas.svg() has no <defs>, so hatch patterns are injected after the
        opening tag here. Without this override `hatch()` returns a url(#...) that
        refers to nothing and every hatched fill renders black."""
        base = super().svg()
        defs = getattr(self, "_defs", None)
        if defs:
            cut = base.index(">") + 1
            base = base[:cut] + "\n<defs>" + "".join(defs) + "</defs>" + base[cut:]
        return base

    def check_bounds(self, left=40.0, right=None, top=0.0, bottom=None, tol=0.6):
        """Every recorded element inside the canvas and the safe margins."""
        right = self.w - 40.0 if right is None else right
        bottom = self.h if bottom is None else bottom
        bad = []
        for x0, y0, x1, y1, kind, label in getattr(self, "_items", []):
            if x0 < left - tol:
                bad.append("%s past left margin (%.1f < %.1f) %r" % (kind, x0, left, label[:28]))
            if x1 > right + tol:
                bad.append("%s past right margin (%.1f > %.1f) %r" % (kind, x1, right, label[:28]))
            if y0 < top - tol:
                bad.append("%s above canvas (%.1f < %.1f) %r" % (kind, y0, top, label[:28]))
            if y1 > bottom + tol:
                bad.append("%s below canvas (%.1f > %.1f) %r" % (kind, y1, bottom, label[:28]))
        return bad

    def overflows(self, left=40.0, right=None, tol=0.6):
        """Alias of check_bounds, kept because the source kits called it this."""
        return self.check_bounds(left=left, right=right, tol=tol)

    def collisions(self, min_overlap=6.0):
        """Pairs of TEXT runs whose boxes overlap by more than `min_overlap`.

        Text-only on purpose: labels sit on bars and rules by design, so including
        geometry here would report a figure full of intentional overlaps as broken.
        A text-text collision is the one that reliably means a real defect -- it is
        what a font-size increase causes when a width-wrapped note re-wraps.
        """
        texts = [t for t in getattr(self, "_items", []) if t[4] == "text"]
        hits = []
        for i in range(len(texts)):
            for j in range(i + 1, len(texts)):
                a, b = texts[i], texts[j]
                ox = min(a[2], b[2]) - max(a[0], b[0])
                oy = min(a[3], b[3]) - max(a[1], b[1])
                if ox > min_overlap and oy > min_overlap:
                    hits.append("%r overlaps %r by %.1fx%.1f units"
                                % (a[5][:24], b[5][:24], ox, oy))
        return hits

    def report(self, left=40.0, right=None, name="figure", check_collisions=True):
        """Layout verdict. Every check either runs or is reported as unavailable.

        There is deliberately NO bare `except: pass` here. A verifier that can
        silently report nothing is worse than one that crashes -- that failure mode
        cost a full working session in the source engagement.
        """
        problems, warnings = [], []

        scale = self.check_scale()
        if not scale.get("ok", False):
            problems.append("scale law: smallest label prints at %s pt (floor %s)"
                            % (scale.get("onpage_pt"), MIN_ONPAGE_PT))
        ran = ["scale"]

        bounds = self.check_bounds(left=left, right=right)
        if bounds:
            problems.extend(bounds[:10])
        ran.append("bounds")

        if check_collisions:
            coll = self.collisions()
            if coll:
                warnings.extend(coll[:10])
            ran.append("collisions")

        return {"name": name, "ok": not problems, "problems": problems,
                "warnings": warnings, "scale": scale, "checks_run": ran,
                "elements_recorded": len(getattr(self, "_items", []))}


# --------------------------------------------------------------------- self-test
def _selftest():
    """Draw one figure per family and assert the canvas contract on each.

    This is not decoration: the source corpus shipped figures whose canvas assertion
    had silently never run, because a path insert sat inside the `try: import` block
    that needed it. Running the check on every build is the fix.
    """
    out = []
    d = Diagram(780, 300, title="Market build-up", accent=POSITIVE)
    d.linear_axis(60, 720, 230, ticks=[0, 25, 50, 75, 100], label="USD m, FY2025")
    d.hatch(NATURAL, "diag")
    d.mark_dot(200, 200)
    d.mark_sq(260, 200, half=True)
    d.table(60, 60, [180, 120, 120], ["Segment", "USD m", "Share"], 
            [["Whey", "42", "38%"], ["Casein", "31", "28%"]])
    d.legend(560, 80, [("Natural", NATURAL), ("Engineered", ENGINEERED)])
    d.furniture("Figure 1 - Self-test figure.", "Source: self-test - Retrieved 2026-09-18")
    out.append(d.report(name="market_buildup"))

    f = Diagram(780, 260, title="Licensing stack", accent=B.JPM_INK)
    f.linear_axis(60, 720, 200, ticks=[0, 5, 10, 15, 20], label="USD m, cumulative")
    f.mark_sq(120, 120, filled=True, color=B.JPM_BRONZE)
    f.mark_sq(180, 120, half=True, color=B.JPM_BRONZE)
    f.furniture("Figure 2 - Self-test financial figure.",
                "Source: self-test - Retrieved 2026-09-18")
    out.append(f.report(name="licensing_stack"))
    return out


if __name__ == "__main__":
    REQUIRED_CHECKS = {"scale", "bounds", "collisions"}
    verdicts = _selftest()
    bad = 0
    for v in verdicts:
        # A verdict of "ok" is worthless if the checks never ran. An earlier version
        # of this self-test printed OK while two of its three checks were silently
        # skipped by a swallowed AttributeError -- the exact defect this kit exists
        # to prevent. So assert that the checks RAN, not merely that nothing failed.
        ran = set(v.get("checks_run", []))
        missing = REQUIRED_CHECKS - ran
        vacuous = missing or v.get("elements_recorded", 0) == 0
        ok = v["ok"] and not vacuous
        if not ok:
            bad += 1
        print("%s %s  (checks: %s, elements: %d)"
              % ("OK  " if ok else "FAIL", v["name"], ",".join(sorted(ran)),
                 v.get("elements_recorded", 0)))
        if missing:
            print("       - VACUOUS: these checks did not run: %s" % ", ".join(sorted(missing)))
        if v.get("elements_recorded", 0) == 0:
            print("       - VACUOUS: no elements recorded, so bounds checks proved nothing")
        for p in v["problems"]:
            print("       ! %s" % p)
        for w in v.get("warnings", []):
            print("       ~ %s" % w)
    print("\n%d figure(s), %d failing" % (len(verdicts), bad))
    raise SystemExit(1 if bad else 0)
