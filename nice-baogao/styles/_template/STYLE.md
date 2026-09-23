# `<your-style-name>` — figure style

> Copy this folder to `styles/<your-style-name>/` and fill it in.
> Every section below is required. Delete the guidance and keep the numbers.

## 1. Design intent

One paragraph, in the form *"X overlaid with Y"* — the tension that makes the style
recognisable. Then one sentence on how loud it should be.

*Why it matters:* without a stated intent, every later judgement call is taste, and two
people applying the style will produce two different looks.

## 2. Colour

### Core tokens

| Token | Hex | Role |
|---|---|---|
| `PAPER` | | the canvas |
| `INK` | | all text and rules |
| `INK_MUTED` | | captions, sources, metadata |
| `RULE_SOFT` | | faint gridlines |

### Accents — assign by MEANING, not by taste

| Accent | Hex | Means |
|---|---|---|
| | | |

A palette assigned by meaning reproduces itself across 100 figures. One assigned by
taste does not. State which hues are text-safe and which are fill-only.

## 3. Typography

| Face | Role |
|---|---|
| | |

Then state, explicitly:

* **Weight** — how many weights exist, and how importance is expressed if there is no
  bold. (An emphasis ladder: size → space → one accent → italic.)
* **Letter spacing** — the standard value, and the single exception if any.
* **Micro-label convention** — case, tracking, face.

## 4. Geometry

Stroke weights (name real numbers) · corner radius · what effects are forbidden ·
how arrows are drawn · how much whitespace is required.

## 5. Chart rules

State at minimum: canvas colour · frame yes/no · gridlines (and at what weight) ·
labels direct or legend · numerals in which face · source-line format · export formats
and dpi · the explicit never-list.

Define the **series palettes** as named lists so charts cannot improvise.

## 6. Sub-theme (optional)

If part of the corpus needs a different register, define it here — and say why it is a
sub-theme rather than a separate style (usually: same typography and geometry, only the
accents change).

## 7. The scale law

Required, unchanged in every style:

```
on-page pt = authored_pt × display_width_pt ÷ canvas_width_pt
```

State your **floor** and your **target**. (Defaults: floor 6.0 pt, target 6.5 pt. The
target exceeds the floor because the measuring instrument has a ±0.06 pt spread, so a
figure at 6.00–6.05 is undecidable.)

## 8. Per-category conventions

One subsection per family you need. For each: the form to reach for, what must be
labelled, and what is commonly got wrong.

Suggested families: scientific/process · market/commercial · regulatory/compliance ·
financial · timeline/roadmap · matrix/scorecard.

## 9. Furniture

What every figure carries. Default: caption (face, format, numbering), source line
(face, format, retrieval date), optional kicker.

## 10. The forbidden list

The fastest way for a successor to stay inside the style. Write it from the defects you
actually hit, not from general taste.
