#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Catch the silent label-text change that a font-size bump causes.

THE TRAP. A caption, source line or note whose lines are chosen by MEASURED WIDTH
(`_fit`, `fig_wrap`, `textwrap`-by-metrics) is wrapped at the size it is measured at. Raise
that size and the line breaks move: the words are the same but the DRAWN STRINGS are not,
so `no label text may change` is violated even though nothing looks different. Looking at
the picture will never catch it -- only diffing the text actually drawn will.

WHAT THIS DOES. Render one figure twice with a module-level constant set to two values, read
the drawn strings from the live figure object (`fig.findobj(Text)` -- not the image, not the
SVG, which bakes glyphs to paths), and diff the multisets. Exits non-zero if they differ.

    python facediff.py <script.py> <callable> --attr SMALL --old 7.5 --new 7.6
    python facediff.py _tools/work/ws06_charts.py chart_c1 --attr MIN_PT --old 7.5 --new 7.75
    python facediff.py _tools/redraw/ws5_v1_broker_forecasts.py build \
                       --attr SMALL --old 7.5 --new 7.6 --also WRAP_PT=7.5

`--also NAME=VALUE` pins a second constant in BOTH runs (use it for the wrap size).

FIX WHEN IT FIRES: pin the wrap size to the value the shipped note was wrapped at, and draw
at the raised size. `_tools/design/schematic.py` and `_tools/work/ws06_charts.py` both expose
that split (`type_scale`/`min_type`; `size`/`wrap_size`).
"""
from __future__ import annotations

import argparse
import collections
import importlib.util
import os
import sys

ROOT = os.environ.get("DOCSET_ROOT") or os.path.abspath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))


def load(path: str, tag: str):
    spec = importlib.util.spec_from_file_location(tag, path)
    m = importlib.util.module_from_spec(spec)
    sys.modules[tag] = m
    spec.loader.exec_module(m)
    return m


def render_strings(script: str, callable_name: str, attr: str, value: float,
                   also: dict, tag: str, outdir: str):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.text as mtext

    m = load(os.path.join(ROOT, script), tag)
    for name, val in list(also.items()) + [(attr, value)]:
        if not hasattr(m, name):
            return None, None, "module has no attribute %r" % name
        setattr(m, name, float(val))
    # keep the render off the delivered tree
    for guess in ("OUT",):
        if hasattr(m, guess):
            setattr(m, guess, os.path.join(outdir, os.path.basename(str(getattr(m, guess)))))
    for guess in ("CELL_FIG", "NRPS_FIG", "ENZ_FIG"):
        if hasattr(m, guess):
            setattr(m, guess, outdir)
    before = set(plt.get_fignums())
    grabbed = []
    real_close = plt.close

    def grab(f=None):
        """Many figure scripts call plt.close(fig) before returning; capture instead."""
        if f is not None:
            grabbed.append(f)
        else:
            real_close()

    plt.close = grab
    try:
        getattr(m, callable_name)()
    finally:
        plt.close = real_close
    if grabbed:
        fig = grabbed[-1]
    else:
        new = [n for n in plt.get_fignums() if n not in before] or plt.get_fignums()
        if not new:
            return None, None, "the script produced no figure object to inspect"
        fig = plt.figure(new[-1])
    texts = [t.get_text() for t in fig.findobj(mtext.Text) if t.get_text()]
    plt.close(fig)
    return collections.Counter(texts), texts, None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("script")
    ap.add_argument("callable")
    ap.add_argument("--attr", required=True)
    ap.add_argument("--old", type=float, required=True)
    ap.add_argument("--new", type=float, required=True)
    ap.add_argument("--also", action="append", default=[], metavar="NAME=VALUE")
    a = ap.parse_args()
    also = {}
    for kv in a.also:
        k, _, v = kv.partition("=")
        also[k.strip()] = float(v)

    outdir = os.path.join(ROOT, "_tools", "work", "legiblefix", "facediff_out")
    os.makedirs(outdir, exist_ok=True)
    co, lo, err = render_strings(a.script, a.callable, a.attr, a.old, also, "fd_old", outdir)
    if err:
        print("ERROR(old): %s" % err)
        return 2
    cn, ln, err = render_strings(a.script, a.callable, a.attr, a.new, also, "fd_new", outdir)
    if err:
        print("ERROR(new): %s" % err)
        return 2

    print("%s::%s   %s %s -> %s   pinned: %s"
          % (a.script, a.callable, a.attr, a.old, a.new, also or "none"))
    print("   drawn strings: %d -> %d" % (len(lo), len(ln)))
    if co == cn:
        print("   MULTISETS IDENTICAL -- no drawn string changed")
        return 0
    print("   *** DRAWN STRINGS CHANGED -- this violates 'no label text may change' ***")
    for tag, diff in (("only in OLD", co - cn), ("only in NEW", cn - co)):
        for s, n in diff.items():
            print("   %s x%d: %r" % (tag, n, s if len(s) < 200 else s[:200] + "..."))
    wrapped_o = sorted(s for s in lo if "\n" in s)
    wrapped_n = sorted(s for s in ln if "\n" in s)
    if wrapped_o != wrapped_n:
        print("   -> a WRAPPED block re-broke its lines. Pin the wrap size "
              "(see the docstring).")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
