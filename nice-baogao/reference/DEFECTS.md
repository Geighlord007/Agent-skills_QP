# Instrument defects, and the meta-lesson

Every instrument in this method's history reported **clean or damning while the artefact
was fine or the input was stale**. Nine instances. In every single one, **the arithmetic was
sound and the input was wrong.**

Read this before trusting any "clean" — including your own.

## The nine

| # | instrument | what it could not see |
|---|---|---|
| 1 | a canvas-unit scale checker | canvas overflow. It guarded type *size* only; three figures had their last line off the bottom of their own canvas while it reported `ok`. |
| 2 | `fig.findobj(Text)` | does not reach `ax.title` on matplotlib 3.10, so a clipped title or one printed over an annotation passes. |
| 3 | a 1 px overflow tolerance | a clip inside the tolerance: a y-tick label lost its leading characters 17 px off the canvas while the tool printed the truncated string as if complete. |
| 4 | a text screen | scored 36 identical minor log-axis tick marks as a text label, and a 200-dpi photograph with no text as a "0.0 pt defect". |
| 5 | a shipped-image checker | a script re-run *after* a swap leaves the document holding the older image while the measurement refers to the new one. |
| 6 | `figcheck.escapes()` | compares the raster's **size** with the nominal size, so it cannot see ink hanging off the **left** while there is slack on the right. Called three figures clean while ink was being cut. |
| 7 | **me, reading a filename** | `image2.jpeg` held PNG bytes and reproduced byte-identically from its redraw script. Reading the extension instead of the bytes produced a wrong diagnosis, and an argument built on it. |
| 8 | **me, grepping a source file** | found `6.6` where the built figure resolves to `6.85`, because a later commit had re-rendered it. This **inverted a published conclusion**. |
| 9 | **me, amplifying a dramatic number** | repeated another agent's pixel-route reading of "2.0 pt" as "the worst figure in the corpus" and ranked it first for repair. The figure was at **6.424 pt all along** — its own script's docstring said so. |

## The failure modes named, so you can watch for them

**The wrong quantity.** A comparison that is arithmetically perfect but applied to something
other than what you care about: raster size instead of ink extent, canvas units instead of
printed points, a filename instead of a format, a source constant instead of a resolved
value. **This is the majority of the nine.**

**The up-sampling render.** Word exports embedded figures as rasters at roughly 200 dpi. A
600 dpi page render therefore up-samples ~3×; the thresholded ink mask splits connected
lines differently and the classifier flips glyph class from x-height (÷0.52) to cap height
(÷0.72) — a **38 % swing**. Measured on one fixed rectangle:

| page dpi | 150 | 200 | 300 | 400 | **600** | 900 |
|---|---|---|---|---|---|---|
| reported pt | 6.46 | 6.23 | 6.46 | 6.23 | **4.50** | 4.56 |

A single-resolution measurement **cannot detect its own up-sampling**, and this one looked
entirely plausible. Always sweep the dpi and confirm stability first.

**Non-text reported as text.** Line art, a dense dotted legend, a dashed diagonal rule,
a 1-px speck, a *fragment of a larger label* whose x-height was mistaken for a cap height.
The pixel route has produced all of these. **Read the band at 1:1 before believing a
dramatic number** — and when a figure is claimed to be far below the floor, check the
source's own declared size first, because a figure at 6.4 pt cannot be at 2.0 pt.

**The stale input.** A value read once and reused after the artefact changed. Grep a
source, read a memo, quote a filename, cache a baseline — all of these go stale silently.
**Resolve at the moment of use.**

**The silent no-result.** A verification tool that cannot read its own subprocess output
prints "no summary line" and **reports nothing** rather than failing. A verifier that can
silently report no result is worse than one that crashes. Treat a missing summary as a
failure, and pass an explicit `encoding=` to every subprocess call.

**The concurrency artifact.** A repo-wide Word sweep run while other agents drive Word
returned **0, then 1, then 3** failures with a *different* document each time. A genuinely
corrupt package fails consistently. This produced a plausible wrong answer naming real
documents — worse than no answer, because it looks like a finding.

## The discipline that comes out of it

1. **Validate the input, not the formula.** Before trusting a number, ask what it was read
   *from* and when.
2. **Cross-check with an instrument that shares no code.** Arithmetic against pixels;
   python-docx against raw XML; two independent counts.
3. **Read the artefact, at 1:1, when the number is dramatic** — in either direction.
4. **State the instrument's own scope.** Print what you did not check.
5. **Prefer the conservative reading when two routes disagree**, and say so.
6. **When you were wrong, correct it in writing** and leave the correction where the wrong
   claim was made. Three of the nine were caught by someone else, and two of those were me
   being caught by a subagent reading the bytes I had only read the name of.
