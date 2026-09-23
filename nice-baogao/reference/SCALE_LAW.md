# The scale law

## The formula

```
on-page pt = authored_pt × display_width_pt ÷ canvas_width_pt
```

A figure prints at its **native extent** — the size implied by the image's own pixel
dimensions and embedded dpi — unless the document explicitly caps it. So:

* a canvas **wider** than the display width shrinks every label in proportion;
* a canvas **narrower** than the display width enlarges every label.

This is why "the author set the font to 6.6 pt" and "the reader sees 5.9 pt" are both true.

## Unit anchors

Make every number checkable by hand:

| | pt | mm | note |
|---|---|---|---|
| 1 pt | 1 | 0.3528 | 1/72 in |
| A4 width | 595.276 | 210 | |
| A4 height | 841.890 | 297 | |
| body text | 10–11 | 3.5–3.9 | comfortable print |
| newspaper body | 9–10 | | |
| **floor** | **6.0** | **2.12** | ~1.5 mm capitals, ~1.1 mm x-height |
| **target** | **6.5** | **2.29** | floor × 1.08 |
| 16.6 cm column | 470.551 | 166 | widest a figure may sit at |
| 16.11 cm cap | 456.693 | 161.1 | the standard's figure cap |
| 1 pt in EMU | 12,700 | | for `wp:extent` / `a:ext` edits |

## Worked examples (all real, all verified two ways)

**1. A figure authored wider than it prints.** A chart built on a 7.1 in canvas
(511.2 pt at 300 dpi) displayed in a 456.69 pt column:

```
scale = 456.69 / 511.2 = 0.8934
authored 6.6 pt  →  6.6 × 0.8934 = 5.90 pt     # below a 6.0 floor
authored 6.85 pt →  6.85 × 0.8934 = 6.12 pt    # passes
```

**2. The cheapest fix is often the display width, not the type.** Same figure, canvas
untouched — widen the display from 456.69 to 470.55 pt (the full column):

```
470.55 / 456.69 = 1.0303   →  +3.03 % on every label
```

**3. And when the figure sits far below the cap, the headroom is large.** A figure
displayed at 368.0 pt has `456.69 / 368.0 = 1.241` available — a ×1.24 lift with no
re-rendering, no clipping, no text change and no collision risk.

**4. A Canvas figure whose design units are points.** A script declaring
`TARGET_CANVAS_W = 940` units with a smallest label of 12.5, displayed at 368.0 pt:

```
12.5 × 368.0 / 940 = 4.89 pt
```

Hand-computed and matched against the instrument's 4.88 — which is the cross-check that
validates the instrument.

**5. Where the multiplicand, not the arithmetic, is wrong.** `6.6 × 0.8934 = 5.896`
agreed with a pixel reading of `5.891`, and that agreement was treated as proof. The
authored value was stale — the script had been re-rendered and the true size was 6.85.
**A correct multiplication by a stale factor yields a confident wrong answer.** Always
resolve the authored size from the built figure, never from a grep of the source.

## Choosing a target

The instrument has a demonstrated figure-level spread of **±0.06 pt**. A figure at
6.00–6.05 is therefore inside the noise of a 6.0 floor and **cannot be distinguished from
a failing one**. Target the floor × 1.08 (6.0 → 6.5), which is about 8× the tolerance.

**A floor met by 0.05 pt is not met.** State the target, and reject "it passes" when the
margin is inside the instrument's error.

## Verifying a size two ways

Never accept one route. Compute both and reconcile:

1. **Arithmetic** — `authored × display ÷ canvas`. Shares no code with any pixel
   measurement and assumes no glyph ratio.
2. **Pixels** — render the page, crop the figure's rectangle, invert the smallest text
   line. Ground truth for what the reader sees, but it carries the dpi hazard below.

Agreement within a fraction of a point validates both. Disagreement means one input is
wrong, and the arithmetic route is the criterion — but **read the disputed band at 1:1
before acting**, because the pixel route's most common failure is calling non-text "text".
