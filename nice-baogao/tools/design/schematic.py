#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Schematic drawing kit — the brand's diagram language as reusable SVG primitives.

The house style, taken from the company's own SVGs: fine hairline strokes (0.5–0.8 px at
illustration scale), flat geometry, ONE accent hue per figure, no gradients, no shadows,
no rounded corners. Vintage-engraving restraint plus modern thin construction.

Everything returns SVG fragments, so a figure is composed and then written out once.

    from design.schematic import Canvas, BRAND
    c = Canvas(1200, 520, title="Downstream purification route")
    a = c.box(40, 120, 200, 90, "Capture", "Protein A")
    b = c.box(320, 120, 200, 90, "HIC", "Butyl")
    c.arrow(a.right, a.mid, b.left, b.mid)
    c.caption("Figure 6 — Flow diagram of the published OPN purification process.")
    c.source("Source: <where it came from> · <DOCSET_TITLE>")
    c.save("_admin/_redraw/opn_flow")

Then swap it into the document:
    python _tools/replace_figure.py <docx> <sha16> _admin/_redraw/opn_flow.png
"""
from __future__ import annotations

import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from design import brand as B  # noqa: E402

PAPER, INK, INK2, MUTED = B.PAPER, B.INK, B.INK_2, B.INK_MUTED
RULE = B.RULE_SOFT


class Node:
    """A placed box, so arrows can attach to real edges instead of guessed coordinates."""

    def __init__(self, x, y, w, h):
        self.x, self.y, self.w, self.h = x, y, w, h

    @property
    def left(self):
        return self.x

    @property
    def right(self):
        return self.x + self.w

    @property
    def top(self):
        return self.y

    @property
    def bottom(self):
        return self.y + self.h

    @property
    def mid(self):
        return self.y + self.h / 2

    @property
    def cx(self):
        return self.x + self.w / 2

    @property
    def cy(self):
        return self.y + self.h / 2


# The documents pin a figure's DISPLAY width at the original image's extent, measured at
# 340-471 pt across this library. On-page label size is therefore
#       font_units * display_pt / canvas_units
# With a 1320-unit canvas a 13-unit label prints at 4.5 pt, which is illegible. At 780
# units the same label lands at 7.6 pt and the smallest primitive default (10.5) clears
# 6 pt — matching the 6-8 pt text measured in the original documents.
#
#   canvas 780 units  ->  factor 0.583   (author here)
#   canvas 940 units  ->  factor 0.484
#   canvas 1320 units ->  factor 0.345   (illegible)
TARGET_CANVAS_W = 780
MIN_ONPAGE_PT = 6.0
_TYPICAL_DISPLAY_PT = 455.0


def onpage_pt(font_units: float, canvas_w: int = TARGET_CANVAS_W,
              display_pt: float = _TYPICAL_DISPLAY_PT) -> float:
    """What a label of `font_units` will actually measure on the page."""
    return font_units * display_pt / max(1, canvas_w)


class Canvas:
    """One figure. Accent hue is chosen once and used throughout.

    Author at `TARGET_CANVAS_W` (780) units wide unless the figure genuinely needs more
    room. `check_scale()` warns if the smallest label would print below `MIN_ONPAGE_PT`.

    PRINT LEGIBILITY -- `type_scale` and `min_type`.

    A figure's display width is pinned by its extent in the host document, so the printed
    size of a label is `font_units * display_pt / canvas_units` and nothing here can change
    that ratio: the ONLY way to print a label larger is to author it larger. Two knobs do
    that, and they are not interchangeable:

      * `type_scale` multiplies the WHOLE type ramp, so the label / sub-label hierarchy is
        preserved exactly and every printed size grows by the same factor. This is the
        right knob when the figure has room for it.
      * `min_type` raises only the runs that would otherwise print under the floor, leaving
        everything already above it untouched. Use it when a uniform raise would push a
        long label out of its box -- it costs some of the size hierarchy, and buys the
        floor without moving any geometry.

    `letter-spacing` is scaled with `type_scale` so the tracked micro-labels keep their
    register. Both default to off, so a figure that does not ask for them is written
    byte-identically to before.
    """

    def __init__(self, w: int, h: int, title: str = "", accent: str = B.MOSS,
                 kicker: str = "", type_scale: float = 1.0, min_type: float | None = None):
        self.w, self.h = w, h
        self.accent = accent
        self.type_scale = float(type_scale)
        self.min_type = None if min_type is None else float(min_type)
        self.parts: list[str] = []
        self._min_font = 99.0
        self._head = h
        self.parts.append(f'<rect width="{w}" height="{h}" fill="{PAPER}"/>')
        y = 46
        if kicker:
            self.parts.append(self.text_fragment(40, y, kicker.upper(), size=11, family="mono",
                                        fill=MUTED, tracking=1.6))
            y += 26
        if title:
            self.parts.append(self.text_fragment(40, y + 4, title, size=22, family="sans", fill=INK,
                                        tracking=-0.3))
            y += 24
            self.parts.append(f'<line x1="40" y1="{y}" x2="{w-40}" y2="{y}" '
                              f'stroke="{INK}" stroke-width="0.7" opacity="0.55"/>')
            y += 26
        self.body_top = y

    def type_size(self, size: float) -> float:
        """The authored size a run is actually emitted at (see `type_scale`/`min_type`).

        An integral result is returned as an int so that a figure which asks for neither
        knob is written byte-identically to before (`font-size="11"`, not `"11.0"`). The
        rendered pixels are the same either way, but the SVG is not, and a re-render that
        cannot reproduce the shipped file is not a safe re-render.
        """
        s = float(size) * self.type_scale
        if self.min_type is not None:
            s = max(s, self.min_type)
        return int(s) if s == int(s) else s

    def type_tracking(self, tracking):
        if tracking is None:
            return None
        t = tracking * self.type_scale
        return int(t) if t == int(t) else t

    # ---------------------------------------------------------------- text
    def text_fragment(self, x, y, s, size=13, family="serif", fill=None, anchor="start",
             italic=False, tracking=None, weight=None):
        size = self.type_size(size)
        tracking = self.type_tracking(tracking)
        self._min_font = min(self._min_font, float(size))
        fam = {"serif": B.FONT_SERIF, "sans": B.FONT_SANS, "mono": B.FONT_MONO}[family]
        fill = fill or INK2
        style = f' font-style="italic"' if italic else ""
        tr = f' letter-spacing="{tracking}"' if tracking else ""
        wt = f' font-weight="{weight}"' if weight else ""
        s = (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))
        return (f'<text x="{x}" y="{y}" font-family="{fam}" font-size="{size}" '
                f'fill="{fill}" text-anchor="{anchor}"{style}{tr}{wt}>{s}</text>')

    def text(self, x, y, s, size=13, family="serif", fill=None, anchor="start",
             italic=False, tracking=None, weight=None):
        """Append a text run. This is the one you want; `text_fragment` returns a string
        instead, which is only useful when composing a group by hand."""
        self.parts.append(self.text_fragment(x, y, s, size, family, fill, anchor,
                                             italic, tracking, weight))

    def lines(self, x, y, rows, size=12, family="serif", fill=None, leading=16):
        """Append several lines of text."""
        for i, r in enumerate(rows):
            self.text(x, y + i * leading, r, size=size, family=family, fill=fill)

    # ---------------------------------------------------------------- shapes
    def box(self, x, y, w, h, label="", sub="", accent_edge="left", dashed=False,
            label_size=13, mono_sub=True) -> Node:
        dash = ' stroke-dasharray="3 3"' if dashed else ""
        self.parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="none" '
                          f'stroke="{INK}" stroke-width="0.8"{dash}/>')
        if accent_edge == "left":
            self.parts.append(f'<rect x="{x}" y="{y}" width="3" height="{h}" '
                              f'fill="{self.accent}"/>')
        elif accent_edge == "top":
            self.parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="3" '
                              f'fill="{self.accent}"/>')
        ty = y + (h / 2 + 5 if not sub else h / 2 - 5)
        if label:
            self.parts.append(self.text_fragment(x + 14, ty, label, size=label_size,
                                        family="sans", fill=INK))
        if sub:
            self.parts.append(self.text_fragment(x + 14, ty + 19, sub,
                                        size=10.5, family="mono" if mono_sub else "serif",
                                        fill=MUTED))
        return Node(x, y, w, h)

    def arrow(self, x1, y1, x2, y2, accent=None, curve=0.0, width=1.0, dashed=False):
        accent = accent or self.accent
        dash = ' stroke-dasharray="4 3"' if dashed else ""
        if abs(curve) < 1e-6:
            self.parts.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
                              f'stroke="{accent}" stroke-width="{width}"{dash}/>')
        else:
            dx, dy = x2 - x1, y2 - y1
            nx, ny = -dy, dx
            L = math.hypot(dx, dy) or 1
            mx, my = (x1 + x2) / 2 + nx / L * curve, (y1 + y2) / 2 + ny / L * curve
            self.parts.append(f'<path d="M{x1} {y1} Q{mx} {my} {x2} {y2}" fill="none" '
                              f'stroke="{accent}" stroke-width="{width}"{dash}/>')
            # arrowhead direction from the control point
            x2, y2, x1, y1 = x2, y2, mx, my
        ang = math.atan2(y2 - y1, x2 - x1)
        for s in (+1, -1):
            ax = x2 - 9 * math.cos(ang) + s * 4.5 * math.sin(ang)
            ay = y2 - 9 * math.sin(ang) - s * 4.5 * math.cos(ang)
            self.parts.append(f'<line x1="{x2}" y1="{y2}" x2="{ax:.1f}" y2="{ay:.1f}" '
                              f'stroke="{accent}" stroke-width="{width}"/>')

    def chain(self, nodes: list[Node], gap_label: str = "", curve=0.0, width=1.0):
        """Arrow every consecutive pair, left-to-right or top-to-bottom."""
        for a, b in zip(nodes, nodes[1:]):
            if abs(a.cy - b.cy) < abs(a.cx - b.cx):     # horizontal neighbours
                self.arrow(a.right + 6, a.mid, b.left - 6, b.mid, curve=curve, width=width)
            else:                                        # vertical neighbours
                self.arrow(a.cx, a.bottom + 6, b.cx, b.top - 6, curve=curve, width=width)

    def line(self, x1, y1, x2, y2, accent=None, width=0.8, dashed=False):
        """A plain hairline. Structural only — never decoration."""
        accent = accent or INK
        dash = ' stroke-dasharray="4 3"' if dashed else ""
        self.parts.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
                          f'stroke="{accent}" stroke-width="{width}"{dash}/>')

    def dot(self, cx, cy, r=5, filled=True, accent=None):
        """A node marker: a solid accent dot, or a hairline ring."""
        accent = accent or self.accent
        if filled:
            self.parts.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{accent}"/>')
        else:
            self.parts.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" '
                              f'stroke="{accent}" stroke-width="0.8"/>')

    def bar(self, x, y, w, h, filled=True, accent=None, dashed=False):
        """A flat column. `y` is the TOP of the bar; filled bars are one accent hue,
        outlined bars are hairlines. No 3-D, no gradient, no value label baked in."""
        accent = accent or self.accent
        if filled:
            self.parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" '
                              f'fill="{accent}"/>')
        else:
            dash = ' stroke-dasharray="3 3"' if dashed else ""
            self.parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" '
                              f'fill="none" stroke="{accent}" stroke-width="0.8"{dash}/>')

    def crossed_circle(self, cx, cy, r=13, accent=None):
        """The flowchart terminator: a hairline ring with an X through it."""
        accent = accent or self.accent
        self.dot(cx, cy, r, filled=False, accent=accent)
        d = r * 0.62
        self.line(cx - d, cy - d, cx + d, cy + d, accent=accent, width=0.9)
        self.line(cx - d, cy + d, cx + d, cy - d, accent=accent, width=0.9)

    def wrapped(self, cx, y, s, wrap=38, size=11.5, line_h=15.5, family="sans",
                fill=None, anchor="middle", italic=False):
        """Wrap `s` to <= `wrap` characters and set it from baseline `y` down.

        Returns the number of lines, so a caller can stack blocks precisely.
        """
        import textwrap as _tw
        rows = _tw.wrap(s, wrap) or [""]
        for j, r in enumerate(rows):
            self.text(cx, y + j * line_h, r, size=size, family=family, fill=fill,
                      anchor=anchor, italic=italic)
        return len(rows)

    def ring(self, cx, cy, radii, dots=0, dot_len=0):
        for i, (r, op) in enumerate(radii):
            self.parts.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" '
                              f'stroke="{self.accent}" stroke-width="0.8" opacity="{op}"/>')
        if dots:
            for i in range(dots):
                a = math.radians(i * (360 / dots) - 90)
                self.parts.append(
                    f'<line x1="{cx + (radii[0][0]) * math.cos(a):.1f}" '
                    f'y1="{cy + (radii[0][0]) * math.sin(a):.1f}" '
                    f'x2="{cx + (radii[0][0] + dot_len) * math.cos(a):.1f}" '
                    f'y2="{cy + (radii[0][0] + dot_len) * math.sin(a):.1f}" '
                    f'stroke="{self.accent}" stroke-width="0.8"/>')

    def column_icon(self, x, y, w=34, h=84, bands=3):
        """A chromatography column: the recurring object in this literature."""
        self.parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="0" '
                          f'fill="none" stroke="{INK}" stroke-width="0.8"/>')
        step = h / (bands + 1)
        for i in range(1, bands + 1):
            yy = y + i * step
            self.parts.append(f'<line x1="{x}" y1="{yy:.1f}" x2="{x + w}" y2="{yy:.1f}" '
                              f'stroke="{self.accent}" stroke-width="0.8" opacity="0.75"/>')
        return Node(x, y, w, h)

    def timeline(self, x, y, w, events: list[tuple], label_above=True, dot_r=5):
        """events = [(year, label, sub), ...] laid out evenly on one hairline."""
        self.parts.append(f'<line x1="{x}" y1="{y}" x2="{x + w}" y2="{y}" '
                          f'stroke="{INK}" stroke-width="0.8"/>')
        n = max(1, len(events) - 1)
        for i, ev in enumerate(events):
            year, label = ev[0], ev[1]
            sub = ev[2] if len(ev) > 2 else ""
            ex = x + w * i / n
            self.parts.append(f'<circle cx="{ex:.1f}" cy="{y}" r="{dot_r}" '
                              f'fill="{self.accent}"/>')
            if label_above:
                self.parts.append(self.text_fragment(ex, y - 17, str(year), size=12, family="mono",
                                            fill=INK, anchor="middle"))
                self.parts.append(self.text_fragment(ex, y - 42, label, size=13, family="sans",
                                            fill=INK, anchor="middle"))
                if sub:
                    self.parts.append(self.text_fragment(ex, y - 60, sub, size=11,
                                                         family="serif", fill=MUTED,
                                                         anchor="middle", italic=True))
            else:
                self.parts.append(self.text_fragment(ex, y + 25, str(year), size=12, family="mono",
                                            fill=INK, anchor="middle"))
                self.parts.append(self.text_fragment(ex, y + 45, label, size=13, family="sans",
                                            fill=INK, anchor="middle"))

    def label(self, x, y, s, size=11):
        """A small mono section label, the brand's uppercase micro-label."""
        self.parts.append(self.text_fragment(x, y, s.upper(), size=size, family="mono",
                                    fill=MUTED, tracking=1.4))

    def note(self, x, y, s, size=11.5, width=None):
        self.parts.append(self.text_fragment(x, y, s, size=size, family="serif", fill=MUTED,
                                             italic=True))

    # ---------------------------------------------------------------- furniture
    def caption(self, s, size=13):
        """Rarely needed. The host document already prints its own `Figure N — ...`
        paragraph under every image, so drawing one here duplicates it on the page.
        Only use it when the document prints no caption of its own."""
        self.parts.append(self.text_fragment(40, self.h - 40, s, size=size, family="serif",
                                    fill=MUTED, italic=True))

    def source(self, s, size=12.5):
        """Rarely needed, for the same reason as `caption`."""
        self.parts.append(self.text_fragment(40, self.h - 22, s, size=size, family="mono",
                                    fill=MUTED))

    def frame(self, x=30, y=None, w=None, h=None):
        y = y if y is not None else self.body_top - 14
        w = w or self.w - 60
        h = h or (self.h - 70 - y)
        self.parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="none" '
                          f'stroke="{RULE}" stroke-width="0.6"/>')

    # ---------------------------------------------------------------- output
    def svg(self) -> str:
        return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.w} {self.h}" '
                f'width="{self.w}" height="{self.h}" role="img">\n'
                + "\n".join(self.parts) + "\n</svg>")

    def check_scale(self) -> dict:
        """Will the smallest label be legible on the page? Call before shipping."""
        pt = onpage_pt(self._min_font, self.w)
        return {"canvas_w": self.w, "smallest_font_units": self._min_font,
                "onpage_pt": round(pt, 2), "ok": pt >= MIN_ONPAGE_PT,
                "advice": "" if pt >= MIN_ONPAGE_PT else
                f"re-author at ~{TARGET_CANVAS_W} units wide, or raise the smallest "
                f"label from {self._min_font:g} to "
                f"{self._min_font * MIN_ONPAGE_PT / max(pt, 0.01):.0f}"}

    def save(self, stem: str, png_width: int = 2400) -> dict:
        """Write <stem>.svg and <stem>.png at 300 dpi equivalent."""
        chk = self.check_scale()
        if not chk["ok"]:
            import warnings
            warnings.warn(f"{os.path.basename(stem)}: smallest label prints at "
                          f'{chk["onpage_pt"]} pt (min {MIN_ONPAGE_PT}). {chk["advice"]}')
        os.makedirs(os.path.dirname(os.path.abspath(stem)), exist_ok=True)
        svg_path = stem + ".svg"
        with open(svg_path, "w", encoding="utf-8") as fh:
            fh.write(self.svg())
        png_path = stem + ".png"
        try:
            import cairosvg  # optional
            cairosvg.svg2png(url=svg_path, write_to=png_path,
                             output_width=png_width, background_color=PAPER)
        except Exception:
            # no cairosvg: rasterise with the browser, which we already depend on
            _rasterise(svg_path, png_path, self.w, self.h, png_width)
        return {"svg": svg_path, "png": png_path}


_FONT_CSS: str | None = None


def _font_css() -> str:
    """@font-face rules for the three brand faces, base64-embedded.

    Chrome only sees system-installed fonts, and Schibsted Grotesk / DM Mono /
    Newsreader are NOT installed on this machine — without this the whole figure
    silently falls back to Times and Courier. Encoded once, cached for the run.
    """
    global _FONT_CSS
    if _FONT_CSS is not None:
        return _FONT_CSS
    import base64

    faces = [("SchibstedGrotesk-Regular.ttf", B.FONT_SANS, "normal", 400),
             ("SchibstedGrotesk-Italic.ttf", B.FONT_SANS, "italic", 400),
             ("Newsreader-Regular.ttf", B.FONT_SERIF, "normal", 400),
             ("Newsreader-Italic.ttf", B.FONT_SERIF, "italic", 400),
             ("DMMono-Light.ttf", B.FONT_MONO, "normal", 300),
             ("DMMono-Regular.ttf", B.FONT_MONO, "normal", 400),
             ("DMMono-Medium.ttf", B.FONT_MONO, "normal", 500)]
    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    fdir = os.path.join(root, "_admin", "company_research", "fonts_ttf")
    out = []
    for fname, family, style, weight in faces:
        path = os.path.join(fdir, fname)
        if not os.path.exists(path):
            continue
        with open(path, "rb") as fh:
            b64 = base64.b64encode(fh.read()).decode("ascii")
        out.append(f"@font-face{{font-family:'{family}';font-style:{style};"
                   f"font-weight:{weight};src:url(data:font/ttf;base64,{b64}) "
                   f"format('truetype');}}")
    _FONT_CSS = "".join(out)
    return _FONT_CSS


def _rasterise(svg_path: str, png_path: str, w: int, h: int, png_width: int):
    """Headless-Chrome rasterisation via the bundled edge/chrome binary."""
    import subprocess
    import tempfile

    scale = png_width / w
    wrapper = tempfile.NamedTemporaryFile("w", suffix=".html", delete=False,
                                         encoding="utf-8")
    svg = open(svg_path, encoding="utf-8").read()
    try:
        font_css = _font_css()
    except Exception:  # noqa: BLE001 — a missing font dir must never break a render
        font_css = ""
    wrapper.write(f'<!DOCTYPE html><html><head><meta charset="utf-8"><style>'
                  f'{font_css}'
                  f'html,body{{margin:0;padding:0;background:{PAPER}}}'
                  f'svg{{display:block;width:{w*scale}px;height:{h*scale}px}}</style>'
                  f'</head><body>{svg}</body></html>')
    wrapper.close()
    for exe in (r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
                r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"):
        if not os.path.exists(exe):
            continue
        subprocess.run([exe, "--headless=new", "--disable-gpu", "--no-sandbox",
                        "--hide-scrollbars", "--force-device-scale-factor=1",
                        f"--window-size={int(w*scale)},{int(h*scale)}",
                        f"--screenshot={os.path.abspath(png_path)}",
                        "file:///" + wrapper.name.replace("\\", "/")],
                       capture_output=True, timeout=120)
        if os.path.exists(png_path):
            break
    try:
        os.unlink(wrapper.name)
    except OSError:
        pass


# common palettes, so every redraw picks a deliberate accent
ACCENTS = {"natural": B.MOSS, "engineered": B.CLAY, "data": B.MEADOW,
           "evidence": B.ROSE, "neutral": B.SEED_BROWN, "finance": B.JPM_BRONZE}
