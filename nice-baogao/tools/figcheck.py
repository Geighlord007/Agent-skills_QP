#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
The canvas contract for a matplotlib figure in this repository.

Why this exists
---------------
A document pins a figure's DISPLAY width at the image's original extent (capped at
16.1 cm in this library). So the size a label actually prints at is

        on-page pt = font_units * display_pt / canvas_units

`canvas_units` is the SAVED canvas, not the figure the script authored. A
`savefig(..., bbox_inches="tight")` crops to the drawn content, so the saved canvas is
whatever the widest escaping annotation made it -- and every label on the page shrinks
in proportion. Three shipped figures in this repository saved at 3 631-4 018 px against
nominal canvases of 2 370-2 760 px and printed their smallest labels at 2.5-4.0 pt.

So a chart script must:
  1. save with `bbox_inches=None`, and
  2. prove the saved PNG is exactly `figsize x dpi`, and
  3. know what its smallest label will print at.

`assert_canvas()` is the proof for (2) and exits non-zero when it fails; `check_scale()`
is the answer for (3).

Used by every chart script fixed by the legibility pass.
"""
from __future__ import annotations

MIN_ONPAGE_PT = 6.0

# `_tools/replace_figure.py` caps a drawing's display extent at `max_width_emu = 5 800 000`,
# i.e. 456.69 pt = 16.11 cm -- `_admin/DOCUMENT_STANDARD.md` section 8 requires the original
# extent capped at 16.1 cm to leave a 0.5 cm right gutter. So the width a figure is actually
# printed at is the SMALLER of its current extent and this cap, and an assertion that used the
# uncapped extent would pass a figure that prints below the floor. Three proteinmat documents
# carried 16.6 cm extents (5 976 000 EMU); they were capped on swap, and their smallest label
# prints at 6.12 pt, not the 6.31 pt the uncapped nominal implied.
MAX_DISPLAY_PT = 5_800_000 / 12_700.0        # 456.69 pt


def nominal_px(fig, dpi: int = 300) -> tuple[int, int]:
    w, h = fig.get_size_inches()
    return int(round(w * dpi)), int(round(h * dpi))


def assert_canvas(png: str, fig, dpi: int = 300) -> tuple[int, int]:
    """The saved PNG must be exactly `figsize x dpi`. Exit non-zero if it is not.

    A larger canvas is the whole defect: the document pins the display width, so an
    over-wide canvas prints every label smaller than the script asked for, silently.
    """
    from PIL import Image

    want = nominal_px(fig, dpi)
    got = Image.open(png).size
    if got != want:
        raise SystemExit(
            f"REFUSED: {png} is {got[0]}x{got[1]} px but the nominal canvas is "
            f"{want[0]}x{want[1]} px (figsize {fig.get_size_inches()[0]:g}x"
            f"{fig.get_size_inches()[1]:g} in at {dpi} dpi).\n"
            f"  The canvas moved by {got[0] / want[0]:.3f}x horizontally and "
            f"{got[1] / want[1]:.3f}x vertically, so every label prints at "
            f"{want[0] / got[0]:.3f}x its authored point size on the page.\n"
            f"  Cause is almost always savefig(bbox_inches='tight'): the content "
            f"escaped the canvas and tight grew it to fit. Re-wrap the escaping "
            f"annotation; do not let the canvas grow.")
    return got


def escapes(fig, dpi: int = 300) -> list[str]:
    """Ground truth: does anything the figure draws lie outside the nominal canvas?

    The figure is rendered a second time with `bbox_inches="tight"` and `pad_inches=0`;
    if that raster is larger than the nominal canvas, content escaped. This is the same
    test `_tools/redraw/_ws5_kit.chart_bounds()` applies, and it is the only one that
    cannot be fooled by which artists matplotlib chooses to report.
    """
    import os
    import tempfile

    from PIL import Image

    nominal = nominal_px(fig, dpi)
    # A real file, NOT a BytesIO: `_tools/work/legible/render_one.py` wraps
    # `Figure.savefig` so that every target it cannot recognise as a PNG is relocated
    # into its scratch directory, and a buffer cannot be relocated. The suffix is
    # deliberately not ".png" so that wrapper leaves `bbox_inches="tight"` alone; the
    # format is passed to Pillow explicitly, so the bytes are PNG either way.
    fd, probe = tempfile.mkstemp(suffix=".tightprobe")
    os.close(fd)
    try:
        fig.savefig(probe, format="png", dpi=dpi, bbox_inches="tight", pad_inches=0)
        with Image.open(probe) as im:
            tight = im.size
    finally:
        os.remove(probe)
    out = []
    if tight[0] > nominal[0]:
        out.append(f"tight width {tight[0]} px > nominal {nominal[0]} px")
    if tight[1] > nominal[1]:
        out.append(f"tight height {tight[1]} px > nominal {nominal[1]} px")
    return out


def all_text(fig) -> list:
    """Every drawn string, including the ones `fig.findobj(Text)` does NOT reach.

    `Axes.get_children()` does not include `ax.title`, `ax.xaxis.label` or `ax.yaxis.label`
    on matplotlib 3.10, so a title can be clipped at the canvas edge, or printed on top of
    an annotation, while every checker built on `findobj` reports clean. It caught exactly
    that on the milk-derived-components chart: the "Immunoglobulins" block overlapped the
    title by 11 px and `collide.py` said 0 collisions.
    """
    from matplotlib.text import Text

    seen, out = set(), []
    cands = list(fig.findobj(Text))
    for ax in fig.axes:
        cands += [ax.title, ax.xaxis.label, ax.yaxis.label]
        cands += list(ax.texts)
    for t in cands:
        if id(t) in seen:
            continue
        seen.add(id(t))
        try:
            if not t.get_visible():
                continue
        except Exception:  # noqa: BLE001
            continue
        out.append(t)
    return out


def escape_detail(fig, dpi: int = 300) -> list[str]:
    """Which text artists lie outside the canvas -- for diagnosis, not for the verdict."""
    fig.canvas.draw()
    r = fig.canvas.get_renderer()
    W, H = fig.canvas.get_width_height()
    out = []

    for a in all_text(fig):
        s = (a.get_text() or "").strip()
        if not s:
            continue
        try:
            bb = a.get_window_extent(r)
        except Exception:  # noqa: BLE001
            continue
        if bb.width <= 0 or bb.height <= 0:
            continue
        o = {"left": -bb.x0, "right": bb.x1 - W, "bottom": -bb.y0, "top": bb.y1 - H}
        o = {k: round(v / fig.dpi, 3) for k, v in o.items() if v > 1.0}
        if o:
            out.append(f"{o} in  {s[:60]!r}")
    return out


def _text_union(fig):
    fig.canvas.draw()
    r = fig.canvas.get_renderer()
    x0 = y0 = 1e18
    x1 = y1 = -1e18
    for a in all_text(fig):
        if not (a.get_text() or "").strip():
            continue
        try:
            bb = a.get_window_extent(r)
        except Exception:  # noqa: BLE001
            continue
        if bb.width <= 0 or bb.height <= 0:
            continue
        x0, y0 = min(x0, bb.x0), min(y0, bb.y0)
        x1, y1 = max(x1, bb.x1), max(y1, bb.y1)
    return x0, y0, x1, y1


def autofit(fig, ax, pad_in: float = 0.035, iters: int = 8, trace: bool = False,
            axes_all=None) -> list[float]:
    """Shrink/move `ax` until every drawn string lies inside the figure canvas.

    Growing the type to clear the 6 pt floor is what pushes a y-tick label past the left
    edge and a two-line title past the top -- the escapes that `bbox_inches="tight"` used
    to hide by growing the canvas. This measures the strings and takes the room back out
    of the axes, which is the only place it can come from on a fixed canvas.

    When the figure has several subplots, pass `axes_all` (a list) and the FIGURE's subplot
    parameters are tightened instead, so the panels keep their relative geometry.

    A side whose deficit does not change between two iterations is abandoned: it is an
    artist anchored to the FIGURE (a source line pinned near the edge), which no amount of
    axes shrinking can move -- and chasing it would inflate the margin until the plot
    collapsed.

    Returns the final [x0, y0, x1, y1] axes position.
    """
    prev = None
    if axes_all:
        sp = fig.subplotpars
        left, right = sp.left, sp.right
        bottom, top = sp.bottom, sp.top
        for i in range(iters):
            bx0, by0, bx1, by1 = _text_union(fig)
            W, H = fig.canvas.get_width_height()
            pad = pad_in * fig.dpi
            d = (max(0.0, pad - bx0) / fig.dpi / fig.get_figwidth(),
                 max(0.0, by1 - (H - pad)) / fig.dpi / fig.get_figheight(),
                 max(0.0, bx1 - (W - pad)) / fig.dpi / fig.get_figwidth(),
                 max(0.0, pad - by0) / fig.dpi / fig.get_figheight())
            if trace:
                print(f"   autofit[{i}] union=({bx0:.1f},{by0:.1f},{bx1:.1f},{by1:.1f}) "
                      f"canvas={W}x{H} d={tuple(round(v, 4) for v in d)}")
            if not any(d):
                break
            if prev is not None and all(abs(a - b) < 1e-4 for a, b in zip(d, prev)):
                if trace:
                    print("   autofit: deficit not shrinking -> figure-anchored, stop")
                break
            prev = d
            left, right = left + d[0], right - d[2]
            bottom, top = bottom + d[3], top - d[1]
            if right - left < 0.15 or top - bottom < 0.10:
                break
            fig.subplots_adjust(left=left, right=right, bottom=bottom, top=top)
        return [round(v, 4) for v in (left, bottom, right, top)]

    p = ax.get_position()
    x0, y0, x1, y1 = p.x0, p.y0, p.x1, p.y1
    fw, fh = fig.get_figwidth(), fig.get_figheight()
    for i in range(iters):
        bx0, by0, bx1, by1 = _text_union(fig)
        W, H = fig.canvas.get_width_height()
        pad = pad_in * fig.dpi
        d = (max(0.0, pad - bx0) / fig.dpi / fw,
             max(0.0, by1 - (H - pad)) / fig.dpi / fh,
             max(0.0, bx1 - (W - pad)) / fig.dpi / fw,
             max(0.0, pad - by0) / fig.dpi / fh)
        if trace:
            print(f"   autofit[{i}] union=({bx0:.1f},{by0:.1f},{bx1:.1f},{by1:.1f}) "
                  f"canvas={W}x{H} d={tuple(round(v, 4) for v in d)}")
        if not any(d):
            break
        if prev is not None and all(abs(a - b) < 1e-4 for a, b in zip(d, prev)):
            if trace:
                print("   autofit: deficit not shrinking -> figure-anchored, stop")
            break
        prev = d
        x0, y1 = x0 + d[0], y1 - d[1]
        x1, y0 = x1 - d[2], y0 + d[3]
        if x1 - x0 < 0.15 or y1 - y0 < 0.10:                 # refuse to collapse
            break
        ax.set_position([x0, y0, x1 - x0, y1 - y0])
    ax.set_position([x0, y0, x1 - x0, y1 - y0])
    return [round(v, 4) for v in (x0, y0, x1, y1)]


def wrap_in(fig, s: str, size: float, family: str, max_in: float,
            style: str = "normal") -> list[str]:
    """Wrap `s` to lines that MEASURE at most `max_in` inches in the real face."""
    from matplotlib.text import Text

    r = fig.canvas.get_renderer()
    words, lines, cur = s.split(), [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        t = Text(0, 0, trial, fontsize=size, family=family, style=style)
        t.set_figure(fig)
        if cur and t.get_window_extent(renderer=r).width / fig.dpi > max_in:
            lines.append(cur)
            cur = w
        else:
            cur = trial
    if cur:
        lines.append(cur)
    return lines or [""]


def assert_no_escape(fig, dpi: int = 300) -> None:
    bad = escapes(fig, dpi)
    if bad:
        raise SystemExit("REFUSED: content escapes the canvas and would be clipped:\n  "
                         + "\n  ".join(bad + escape_detail(fig, dpi)))


def onpage_pt(font_pt: float, canvas_w_px: int, display_pt: float,
              dpi: int = 300) -> float:
    """`font_units * display_pt / canvas_units` for a 300-dpi raster canvas."""
    return font_pt * display_pt / max(1.0, canvas_w_px * 72.0 / dpi)


def check_scale(png: str, smallest_font_pt: float, display_pt: float,
                dpi: int = 300) -> dict:
    from PIL import Image

    w = Image.open(png).size[0]
    pt = onpage_pt(smallest_font_pt, w, display_pt, dpi)
    return {"canvas_w_px": w, "smallest_font_pt": smallest_font_pt,
            "display_pt": round(display_pt, 2), "onpage_pt": round(pt, 2),
            "ok": pt >= MIN_ONPAGE_PT}


def check_and_report(png: str, fig, smallest_font_pt: float, display_pt: float,
                     name: str = "", dpi: int = 300) -> dict:
    """assert_canvas + assert_no_escape + the on-page reading, in one printout.

    `display_pt` is clamped to `MAX_DISPLAY_PT`: the document cannot print the figure wider
    than that whatever the script asks for, so a claim computed at a wider extent is not a
    guarantee. Pass the CURRENT extent if it is known; this only ever makes the check stricter.
    """
    size = assert_canvas(png, fig, dpi)
    assert_no_escape(fig, dpi)
    asked = display_pt
    display_pt = min(display_pt, MAX_DISPLAY_PT)
    sc = check_scale(png, smallest_font_pt, display_pt, dpi)
    note = "" if display_pt == asked else f" (capped from {asked:g} pt by the 16.11 cm rule)"
    print(f"[{name or png}] canvas {size[0]}x{size[1]} px (nominal, no escape) | "
          f"smallest label {smallest_font_pt:g} pt -> {sc['onpage_pt']} pt on page "
          f"at a {display_pt:g} pt display width{note} | "
          f"{'ok' if sc['ok'] else 'BELOW 6.0'}")
    if not sc["ok"]:
        raise SystemExit(
            f"REFUSED: {name or png} prints its smallest label at {sc['onpage_pt']} pt, "
            f"below the {MIN_ONPAGE_PT} pt floor. Raise the smallest font size in the "
            f"script to at least "
            f"{smallest_font_pt * MIN_ONPAGE_PT / max(sc['onpage_pt'], 0.01):.2f} pt.")
    return sc
