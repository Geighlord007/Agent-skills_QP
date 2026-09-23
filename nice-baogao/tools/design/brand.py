#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Brand tokens — single source of truth for a document set.

Replace these with values read off YOUR shipping artefacts:
the site's compiled CSS for colour and font stacks; a delivered file's `word/styles.xml` for what is truly in use.
computed-style probe and full-page screenshots. Evidence is preserved in
`_admin/company_research/`. Rationale and usage rules: `_admin/DESIGN_SYSTEM.md`.

Import this from every chart script, docx builder and page generator. Do not
hard-code a hex value anywhere else in the repository.
"""
from __future__ import annotations

import sys

# ---------------------------------------------------------------------------
# Colour — core
# ---------------------------------------------------------------------------
PAPER = "#F7F5EB"        # the entire page canvas
BONE = "#EDEADB"         # secondary panel / table header band / footer
TRAVERTINE = "#F4EFE7"   # financial sub-theme canvas (JPMC)
INK = "#000000"          # all text, all rules
INK_2 = "#3A3A38"        # body copy where pure black is too hard
INK_MUTED = "#6B6B66"    # captions, source lines, metadata
RULE = "#000000"         # 1px hairline
RULE_SOFT = "#D8D3C4"    # faint gridline

# ---------------------------------------------------------------------------
# Colour — accents
# Site rule: clay and lime are UI colours; moss/meadow/rose/seed-brown are
# ILLUSTRATION-ONLY (they appear in no CSS rule, only inside diagrams).
# ---------------------------------------------------------------------------
CLAY = "#E05E3D"         # text accent, alert, "engineered" semantics
LIME = "#E0DB00"         # fill only, never body text on paper
MOSS = "#9EA617"         # chart hue 1 — natural / planetary
MEADOW = "#617D24"       # chart hue 2 — data series, positive
ROSE = "#C28775"         # chart hue 3
SEED_BROWN = "#D1B594"   # chart hue 4 — low emphasis, bands

# Semantic pair from the site's own in-copy colour system
NATURAL = MOSS           # green = natural / planetary / feedstock
ENGINEERED = CLAY        # clay  = engineered / designed / animal

# Accessibility: clay on paper is ~3.6:1 -> large text only. Lime never carries text.
TEXT_SAFE_ACCENTS = (MOSS, MEADOW, CLAY)

# ---------------------------------------------------------------------------
# Colour — J.P. Morgan sub-theme (company, finance, market sizing)
# ---------------------------------------------------------------------------
JPM_PAPER = TRAVERTINE
JPM_INK = "#0B2A4A"
JPM_SKY = "#A6D7F0"
JPM_BRONZE = "#8F5A39"
JPM_SLATE = "#5A6470"

# ---------------------------------------------------------------------------
# Confidence tags (this repository's own notation)
# ---------------------------------------------------------------------------
CONFIDENCE = {
    "VERIFIED": MEADOW,      # traced to a primary source
    "ESTIMATED": SEED_BROWN,  # model / analyst estimate, assumptions stated
    "UNVERIFIED": CLAY,      # no source, or stale
}

# ---------------------------------------------------------------------------
# Typography
# ---------------------------------------------------------------------------
FONT_SERIF = "Newsreader"          # body copy, display, pull-quotes
FONT_SANS = "Schibsted Grotesk"    # headlines, section titles, nav
FONT_MONO = "DM Mono"              # micro-labels, numbers, source lines

# CJK is chosen INDEPENDENTLY of the Latin face: Word selects the East-Asian face
# separately, so a Chinese run never inherits FONT_SANS. Setting only the Latin
# face is exactly what produces an arbitrary CJK substitution.
FONT_CJK = "Arial"

# Fallback stacks. Match the specification in styles/synbio-grotesk/STYLE.md C8.3.
# A face absent from the machine falls through to the next name, so a document
# never silently renders in Word's default.
FONT_STACKS = {
    "serif": (FONT_SERIF, "Georgia", "serif"),
    "sans": (FONT_SANS, "Calibri", "sans-serif"),
    "mono": (FONT_MONO, "Consolas", "monospace"),
    "cjk": (FONT_CJK,),
}


def stack(kind: str = "sans") -> tuple:
    """The ordered fallback stack for a face kind. Use instead of a bare name."""
    return FONT_STACKS.get(kind, (FONT_SANS, "Calibri", "sans-serif"))

FONT_DIR = "_admin/company_research/site_mirror/fonts"

# Type scale, in points, for print/DOCX (portal uses rem equivalents)
TYPE = {
    "display":   30.0,
    "h1":        22.0,
    "h2":        16.0,
    "h3":        12.0,
    "body":      10.5,
    "body_lg":   13.0,
    "caption":    8.5,
    "kicker":     8.0,
    "numeric":    9.5,
}
LEADING_BODY = 1.52
TRACKING_BODY_PT = 0.0      # STANDARD letter spacing. The site's -0.5px was
                            # absolute; applied at 10.5 pt instead of 16 px it
                            # reads as visibly cramped print, so print uses 0.
TRACKING_KICKER_REM = 0.06  # uppercase mono labels
MEASURE_CHARS = (66, 70)    # body column cap

# ---------------------------------------------------------------------------
# Chart series orders
# ---------------------------------------------------------------------------
SERIES_SYNBIO = [MEADOW, MOSS, SEED_BROWN, ROSE, CLAY]
SERIES_FINANCE = [JPM_INK, JPM_BRONZE, JPM_SKY, JPM_SLATE, SEED_BROWN]
SERIES_SINGLE = [MOSS]


def font(kind: str = "sans") -> str:
    """The resolved family name for matplotlib text. Call after apply_matplotlib()."""
    r = globals().get("_RESOLVED") or {"serif": FONT_SERIF, "sans": FONT_SANS, "mono": FONT_MONO}
    return r.get(kind, r["sans"])


def font_stack(kind: str = "sans") -> list[str]:
    """Family list for matplotlib, with a fallback that HAS the glyphs.

    The brand faces are subsets: none carries U+2265 (>=), U+03B5 (epsilon) or U+2082
    (subscript 2). Chrome falls back per character so the SVG schematics are fine, but
    matplotlib does NOT -- it draws a missing-glyph box and says nothing. So a chart that
    needs a symbol outside the subset must ask for a LIST, not a single family:

        ax.set_ylabel("conversion, %", family=brand.font_stack("mono"))

    DejaVu ships with matplotlib and covers these, so the fallback costs nothing when the
    brand face already has the character.
    """
    return [font(kind), "DejaVu Sans", "DejaVu Serif", "DejaVu Sans Mono"]


def series_for(theme: str = "synbio") -> list[str]:
    """Ordered accent hues for a chart. One accent per figure is the default;
    use more only when the data genuinely has more categories."""
    return list(SERIES_FINANCE if theme == "finance" else SERIES_SYNBIO)


def paper_for(theme: str = "synbio") -> str:
    return JPM_PAPER if theme == "finance" else PAPER


def ink_for(theme: str = "synbio") -> str:
    return JPM_INK if theme == "finance" else INK


# ---------------------------------------------------------------------------
# matplotlib theme
# ---------------------------------------------------------------------------
def apply_matplotlib(theme: str = "synbio", font_path: str | None = None):
    """Return a configured matplotlib. Call once at the top of any chart script.

        from brand import apply_matplotlib
        plt = apply_matplotlib()

    The brand faces ship as WOFF2 for the web; matplotlib needs TrueType, so the
    same faces are pre-converted into `_admin/company_research/fonts_ttf/` and
    loaded here. Falls back to DejaVu only if that folder is missing.
    """
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib import font_manager

    serif, sans, mono = "DejaVu Serif", "DejaVu Sans", "DejaVu Sans Mono"
    if font_path is None:
        font_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(
            os.path.abspath(__file__)))), "_admin", "company_research", "fonts_ttf")

    def _pick(want: str, fallback: str) -> str:
        """Exact family name, else prefix match, else the DejaVu fallback.

        The bundled Newsreader subset is a variable-font instance whose family
        is declared as `Newsreader 16pt`, so an exact-match-only lookup would
        silently pick DejaVu Serif. Hence the prefix pass. A miss is reported
        loudly: a silent substitution here is invisible in the PNG and is how
        this repository previously shipped charts in the wrong typeface.
        """
        if want in names:
            return want
        for n in sorted(names):
            if n.startswith(want):
                return n
        print(f"[brand] WARNING: face {want!r} is not installed; "
              f"falling back to {fallback!r}. Charts will NOT match the brand.",
              file=sys.stderr)
        return fallback

    try:
        for f in os.listdir(font_path):
            if f.lower().endswith((".ttf", ".otf")):
                font_manager.fontManager.addfont(os.path.join(font_path, f))
        names = {f.name for f in font_manager.fontManager.ttflist}
        serif, sans, mono = (_pick(FONT_SERIF, serif), _pick(FONT_SANS, sans),
                             _pick(FONT_MONO, mono))
    except Exception as exc:                            # pragma: no cover
        print(f"[brand] WARNING: could not load brand faces from {font_path!r}: "
              f"{exc}. Charts will NOT match the brand.", file=sys.stderr)
    globals()["_RESOLVED"] = {"serif": serif, "sans": sans, "mono": mono}

    paper, ink = paper_for(theme), ink_for(theme)
    plt.rcParams.update({
        "figure.facecolor": paper,
        "axes.facecolor": paper,
        "savefig.facecolor": paper,
        # NOT "tight". bbox="tight" crops to the drawn content, so the saved canvas
        # silently differs from the nominal figsize -- and because display width is
        # pinned (the scale law is on-page pt = font_units x display_pt / canvas_units),
        # a larger canvas prints every label SMALLER than check_scale() computed. A chart
        # in this repo saved at 2841 px against a nominal 2220 and printed its 7.5 pt
        # labels at 5.02 pt, with check_scale() reporting ok=True throughout. A
        # deterministic canvas is the whole point; scripts that want trimming opt in.
        "savefig.bbox": None,
        # Map matplotlib's GENERIC family names onto the brand faces. Chart
        # scripts across this repository ask for family="monospace" / "serif" /
        # "sans-serif" (about 200 call sites). Without these lists those
        # requests resolve against matplotlib's stock list and land on DejaVu,
        # so every mono label printed the wrong face even though `font.family`
        # below looked correct. Setting them here fixes every existing script
        # at once -- prefer this over rewriting call sites.
        "font.serif": [serif, "DejaVu Serif", "serif"],
        "font.sans-serif": [sans, "DejaVu Sans", "sans-serif"],
        "font.monospace": [mono, "DejaVu Sans Mono", "monospace"],
        "font.family": "sans-serif",
        "font.size": 9,
        "text.color": ink,
        "axes.labelcolor": ink,
        "axes.edgecolor": ink,
        "axes.linewidth": 0.6,
        "axes.titlesize": 11,
        "axes.titleweight": "normal",
        "axes.titlelocation": "left",
        "axes.titlepad": 10,
        "axes.grid": False,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "xtick.color": ink,
        "ytick.color": ink,
        "xtick.labelsize": 8,
        "ytick.labelsize": 8,
        "xtick.major.size": 0,
        "ytick.major.size": 0,
        "legend.frameon": False,
        "legend.fontsize": 8,
        "lines.linewidth": 1.4,
        "lines.markersize": 3.5,
        "figure.dpi": 110,
        "savefig.dpi": 300,
        "axes.prop_cycle": matplotlib.cycler(color=series_for(theme)),
    })
    return plt


def source_line(ax, text: str, theme: str = "synbio"):
    """Every figure carries a source line in mono under the plot."""
    ax.annotate(text, xy=(0, -0.16), xycoords="axes fraction",
                fontsize=7, color=INK_MUTED, family="monospace", ha="left", va="top")


import os  # noqa: E402  (kept last so the module stays import-light)
