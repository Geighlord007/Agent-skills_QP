"""chart_kit — the matplotlib side of the `synbio-editorial` style.

`design/brand.py` already owns the tokens, the faces and `apply_matplotlib()`.
This module adds the **chart conventions** from STYLE.md §5 as callables, so a chart
script does not have to remember them:

  * paper canvas, no frame, no gridlines (except faint horizontals)
  * direct-label series rather than a legend
  * DM Mono for every numeral
  * a source line under every figure
  * one accent hue, chosen by meaning

Usage
-----
    import sys; sys.path.insert(0, "<skill>/tools")
    sys.path.insert(0, "<this folder>")
    import chart_kit as K

    fig, ax = K.new_chart("Market build-up", kicker="SECTION 3.1")
    K.bars(ax, ["Whey", "Casein"], [42, 31], accent=K.POSITIVE, direct_labels=True)
    K.finish(fig, ax, caption="Figure 3 - Protein market build-up.",
             source="Source: Company filings - Retrieved 2026-09-11")
    K.save(fig, "market_buildup")      # asserts canvas == figsize x dpi, floor >= 6.0 pt

Run `python chart_kit.py` for a self-test that renders one chart per register and
asserts the canvas contract.
"""
from __future__ import annotations

import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_TOOLS = os.path.abspath(os.path.join(_HERE, "..", "..", "tools"))
for _p in (_TOOLS, _HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from design import brand as B                     # noqa: E402
from design.schematic import (                    # noqa: E402
    MIN_ONPAGE_PT, TARGET_CANVAS_W,
)

NATURAL = B.MOSS
ENGINEERED = B.CLAY
EVIDENCE = B.ROSE
NEUTRAL = B.SEED_BROWN
POSITIVE = B.MEADOW

SERIES_SYNBIO = B.SERIES_SYNBIO
SERIES_FINANCE = B.SERIES_FINANCE

# The published figure width used by every chart in the source corpus.
# Changing this changes the printed size of every label: see the scale law.
FIG_W_IN = 7.1
DPI = 300


def new_chart(title="", kicker="", height_in=3.9, theme="synbio", width_in=FIG_W_IN,
              smallest_pt=6.6):
    """A themed figure and axes, already stripped to the house style.

    Returns `(fig, ax)`. `smallest_pt` is the size of the smallest label you intend to
    draw; it is used by `save()` to assert the printed floor.
    """
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    B.apply_matplotlib(theme=theme)
    fig, ax = plt.subplots(figsize=(width_in, height_in))
    fig.patch.set_facecolor(B.paper_for(theme))
    ax.set_facecolor(B.paper_for(theme))

    # STYLE.md §5.2 / §5.3 -- no frame, no gridlines
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(B.INK)
    ax.spines["bottom"].set_linewidth(0.7)
    ax.grid(False)
    ax.tick_params(colors=B.INK_MUTED, labelsize=smallest_pt, length=3, width=0.6)
    for lbl in ax.get_xticklabels() + ax.get_yticklabels():
        lbl.set_fontfamily(B.font("mono"))
        lbl.set_fontsize(smallest_pt)

    if title:
        ax.set_title(title, fontsize=smallest_pt * 1.5, color=B.INK,
                     fontfamily=B.font("sans"), loc="left", pad=12)
    if kicker:
        ax.text(0, 1.16, kicker.upper(), transform=ax.transAxes, fontsize=smallest_pt * 0.85,
                color=B.INK_MUTED, fontfamily=B.font("mono"))
    fig._style_smallest_pt = smallest_pt           # noqa: SLF001  (carried to save())
    fig._style_theme = theme                       # noqa: SLF001
    return fig, ax


def bars(ax, labels, values, accent=None, direct_labels=True, series=None, **kw):
    """Vertical bars, one accent unless `series` gives a palette by meaning."""
    colors = series or [accent or POSITIVE] * len(labels)
    bars_ = ax.bar(labels, values, color=colors, width=0.62,
                   edgecolor=B.INK, linewidth=0.6, **kw)
    if direct_labels:
        for rect, v in zip(bars_, values):
            ax.annotate(_num(v), (rect.get_x() + rect.get_width() / 2, rect.get_height()),
                        ha="center", va="bottom", fontsize=ax.xaxis.get_ticklabels()[0]
                        .get_fontsize() if ax.xaxis.get_ticklabels() else 6.6,
                        fontfamily=B.font("mono"), color=B.INK)
    return bars_


def lines(ax, x, series, direct_labels=True, palette=None, **kw):
    """Line series with DIRECT LABELS at the right end (STYLE.md §5.4).

    `series` is a dict {label: values}. A legend is only used if two end labels would
    collide.
    """
    palette = palette or ([B.JPM_INK, B.JPM_BRONZE, B.JPM_SKY, B.JPM_SLATE]
                          if getattr(ax.figure, "_style_theme", "synbio") == "finance"
                          else SERIES_SYNBIO)
    ends = []
    for i, (label, vals) in enumerate(series.items()):
        color = palette[i % len(palette)]
        ax.plot(x, vals, color=color, linewidth=1.4, label=label, **kw)
        ends.append((vals[-1], label, color))
    if direct_labels:
        # generous x headroom so end labels fit inside the canvas
        x0, x1 = ax.get_xlim()
        ax.set_xlim(x0, x0 + (x1 - x0) * 1.30)
        # ends entries are (value, label, color) -- index, do not unpack blindly
        span = max(e[0] for e in ends) - min(e[0] for e in ends) or 1
        min_gap = span * 0.075
        ends.sort(key=lambda t: t[0])
        placed = []
        for v, label, color in ends:
            y = v
            while placed and abs(y - placed[-1]) < min_gap:
                y = placed[-1] + min_gap
            placed.append(y)
            ax.annotate(label, (x[-1], y), xytext=(6, 0), textcoords="offset points",
                        va="center", fontsize=ax.figure._style_smallest_pt,  # noqa: SLF001
                        fontfamily=B.font("sans"), color=color)
    return ax


def waterfall(ax, labels, deltas, start=0.0, accent=None):
    """The signature FINANCIAL form (STYLE.md §6): value build-ups.

    `deltas` alternate contributions; the running total is drawn as a full column.
    """
    accent = accent or B.JPM_BRONZE
    base = B.JPM_INK if getattr(ax.figure, "_style_theme", "synbio") == "finance" else B.INK
    run = start
    for i, (lab, d) in enumerate(zip(labels, deltas)):
        bottom = min(run, run + d)
        ax.bar(i, abs(d), bottom=bottom, width=0.6, color=accent if d >= 0 else B.ROSE,
               edgecolor=base, linewidth=0.6)
        ax.annotate(_num(d, signed=True), (i, max(run, run + d)), ha="center", va="bottom",
                    fontsize=ax.figure._style_smallest_pt,  # noqa: SLF001
                    fontfamily=B.font("mono"), color=B.INK)
        run += d
        ax.plot([i - 0.42, i + 0.42], [run, run], color=B.INK_MUTED, linewidth=0.5)
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels)
    return ax


def source_line(ax, text):
    """The mandatory source line (STYLE.md §5.7 / §9)."""
    ax.figure.text(0.01, -0.01, text, fontsize=ax.figure._style_smallest_pt * 0.9,  # noqa: SLF001
                   color=B.INK_MUTED, fontfamily=B.font("mono"), ha="left", va="top")


def finish(fig, ax, caption=None, source=None, tight_layout=True):
    """Apply layout, then the mandatory furniture."""
    if tight_layout:
        fig.tight_layout()
    if source:
        source_line(ax, source)
    if caption:
        fig.text(0.01, -0.055, caption, fontsize=fig._style_smallest_pt * 1.08,  # noqa: SLF001
                 color=B.INK, fontfamily=B.font("serif"), style="italic", ha="left",
                 va="top")
    return fig


def save(fig, stem, dpi=DPI):
    """Save PNG at `dpi` and SVG, asserting the canvas contract.

    Two assertions, both of which have caught real defects:
      1. the saved PNG is EXACTLY `figsize x dpi` -- a `bbox_inches="tight"` anywhere
         silently grows the canvas and shrinks every label in proportion;
      2. the smallest label clears the printed floor at the document's display width.
    """
    from PIL import Image

    png, svg = stem + ".png", stem + ".svg"
    fig.savefig(png, dpi=dpi, bbox_inches=None, facecolor=fig.get_facecolor())
    fig.savefig(svg, bbox_inches=None, facecolor=fig.get_facecolor())

    w_in, h_in = fig.get_size_inches()
    want = (int(round(w_in * dpi)), int(round(h_in * dpi)))
    got = Image.open(png).size
    if got != want:
        raise AssertionError(
            "canvas contract: saved %dx%d px but figsize x dpi = %dx%d. "
            "Something is using bbox_inches='tight'." % (got[0], got[1], want[0], want[1]))

    pt = fig._style_smallest_pt                    # noqa: SLF001
    # displayed at the document's cap (456.69 pt), canvas = full figure width
    onpage = pt * 456.6929133858268 / (w_in * 72.0)
    verdict = {"png": png, "svg": svg, "px": got, "canvas_pt": round(w_in * 72, 1),
               "smallest_onpage_pt": round(onpage, 3), "floor": MIN_ONPAGE_PT,
               "ok": onpage >= MIN_ONPAGE_PT}
    if not verdict["ok"]:
        raise AssertionError(
            "scale law: smallest label prints at %.2f pt (floor %.1f). Raise the "
            "authored size or narrow the canvas."
            % (onpage, MIN_ONPAGE_PT))
    return verdict


def _num(v, signed=False):
    if signed:
        return ("+" if v >= 0 else "") + ("%g" % v)
    if abs(v) >= 1e6:
        return "%gM" % (v / 1e6)
    if abs(v) >= 1e3:
        return "%gk" % (v / 1e3)
    return "%g" % v


def _selftest():
    out = []
    import matplotlib.pyplot as plt

    # 7.3 pt on a 7.1 in canvas => 7.3 x 456.69 / 511.2 = 6.52 pt on page: clears the floor.
    # (6.6 pt would give 5.90 pt -- the exact defect found in three real figures.)
    SMALL = 7.3

    fig, ax = new_chart("Segment stack", kicker="Section 3.2", smallest_pt=SMALL)
    bars(ax, ["Whey", "Casein", "Plant"], [42, 31, 18], accent=POSITIVE)
    finish(fig, ax, caption="Figure 1 - Self-test bars.",
           source="Source: self-test - Retrieved 2026-09-18")
    out.append(save(fig, "_selftest_bars"))
    plt.close(fig)

    fig, ax = new_chart("Value bridge", smallest_pt=SMALL, theme="finance")
    waterfall(ax, ["Base", "Volume", "Price", "Mix"], [100, 18, -6, 9])
    finish(fig, ax, caption="Figure 2 - Self-test waterfall.",
           source="Source: self-test - Retrieved 2026-09-18")
    out.append(save(fig, "_selftest_waterfall"))
    plt.close(fig)

    fig, ax = new_chart("Forecast paths", smallest_pt=SMALL)
    lines(ax, [2024, 2025, 2026, 2027], {"Base": [10, 14, 19, 26], "Upside": [10, 16, 24, 35]})
    finish(fig, ax, caption="Figure 3 - Self-test lines.",
           source="Source: self-test - Retrieved 2026-09-18")
    out.append(save(fig, "_selftest_lines"))
    plt.close(fig)
    return out


def _selftest_rejection():
    """Assert the guard FIRES when it should.

    A check that has never been seen to fail is not evidence. This drives the exact
    combination that broke three figures in the source corpus -- 6.6 pt of type on a
    7.1 in canvas, i.e. 5.90 pt on the page -- and requires the build to refuse it.
    """
    import matplotlib.pyplot as plt

    fig, ax = new_chart("Deliberately too small", smallest_pt=6.6)
    bars(ax, ["A", "B"], [1, 2], direct_labels=False)
    try:
        save(fig, "_selftest_should_fail")
        return False, "save() accepted a 5.90 pt label -- the floor guard is NOT working"
    except AssertionError as exc:
        fired = "5.9" in str(exc) or "6.0" in str(exc)
        return fired, str(exc)
    finally:
        plt.close(fig)


if __name__ == "__main__":
    STEMS = ("_selftest_bars", "_selftest_waterfall", "_selftest_lines",
             "_selftest_should_fail")
    bad = 0
    try:
        for v in _selftest():
            ok = v["ok"]
            if not ok:
                bad += 1
            print("%s %-22s %sx%s px  smallest %s pt" % (
                "OK  " if ok else "FAIL", os.path.basename(v["png"]),
                v["px"][0], v["px"][1], v["smallest_onpage_pt"]))

        fired, msg = _selftest_rejection()
        print("%s %-22s %s" % ("OK  " if fired else "FAIL", "floor guard fires", msg[:72]))
        if not fired:
            bad += 1
    finally:
        # Cleanup in `finally`: an earlier version cleaned up only on the success
        # path, so the first crash left rendered leftovers in the style folder.
        for stem in STEMS:
            for ext in (".png", ".svg"):
                try:
                    os.remove(stem + ext)
                except OSError:
                    pass
    print("\n3 chart(s) + 1 rejection test, %d failing" % bad)
    raise SystemExit(1 if bad else 0)
