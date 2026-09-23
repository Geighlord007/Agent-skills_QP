# `synbio-editorial` — the figure style

A house style for figures in technical and commercial research reports: scientific
mechanisms, market analyses, regulatory pathways, financial models, timelines and
matrices — all recognisably one family.

Every number in this document is measured from real production figures, not invented.

---

## 1. Design intent

**Vintage botanical / scientific engraving, overlaid with modern thin geometric
construction.**

The tension is the whole point. Two visual languages sit on one page:

* **Hairline ink drawing** — fine strokes, flat fills, single hues. Reads as engraved
  plate: precise, unhurried, slightly old.
* **Modern geometric construction** — circles, right-angle connectors, dot grids, thin
  curved arrows. Reads as technical drawing: engineered, contemporary.

Neither dominates. A figure that is *only* engraved looks antique; *only* geometric looks
like a software diagram. The house style is the overlap.

**Corollary worth stating:** the style is quiet. It never competes with the text. If a
figure is the first thing a reader notices on a page, it is too loud.

---

## 2. Colour

### Core tokens

| Token | Hex | Role |
|---|---|---|
| `PAPER` | `#F7F5EB` | the entire canvas. Never white, never transparent in print |
| `BONE` | `#EDEADB` | secondary panel, table header band, footer |
| `TRAVERTINE` | `#F4EFE7` | financial sub-theme canvas (within 1 % of PAPER — a sub-theme, not a new look) |
| `INK` | `#000000` | all text, all rules |
| `INK_MUTED` | `#6B6B66` | captions, source lines, metadata |
| `RULE_SOFT` | `#D8D3C4` | faint gridline, at 10 % when it must recede |

### Accent hues — assigned by meaning, not by taste

This is the rule that makes a corpus of 100 figures feel authored rather than assembled.

| Accent | Hex | Means |
|---|---|---|
| `MOSS` | `#9EA617` | **natural** — feedstock, plant, planetary, biological baseline. Chart hue 1 |
| `MEADOW` | `#617D24` | **data series / positive** — growth, verified quantity |
| `CLAY` | `#E05E3D` | **engineered** — designed, synthetic, animal-derived, alert, the figure's subject |
| `ROSE` | `#C28775` | **evidence** — measured, assayed, observed |
| `SEED_BROWN` | `#D1B594` | **neutral / low emphasis** — bands, baselines, context |
| `LIME` | `#E0DB00` | **fill only.** Never body text on paper — unreadable at small sizes |

**Semantic aliases** exist so scripts read as intent: `NATURAL = MOSS`,
`ENGINEERED = CLAY`.

### Rules

* **One accent hue per figure.** A second appears only as a genuinely different
  semantic category, never as decoration.
* Text-safe accents are `MOSS`, `MEADOW`, `CLAY`. `LIME` and `SEED_BROWN` are fill-only.
* Never default matplotlib colours. Ever.
* Fills are **flat and single-hue**. No gradients, no opacity tricks beyond a light
  band.

---

## 3. Typography

Three faces, three jobs. Mixing them wrongly is the fastest way to look generic.

| Face | Role |
|---|---|
| **Newsreader** (serif) | body copy, display, captions, notes, pull-quotes |
| **Schibsted Grotesk** (sans) | headlines, section titles, box labels, navigation |
| **DM Mono** | years, numbers, axis figures, micro-labels, source lines |

### The signature move — copy this exactly

A **serif italic phrase set ~1.24× larger than its surrounding sans**. It is the single
most identifiable element of the style, and it costs nothing.

### Weight and tracking

* **Weight 400 only.** There is no bold anywhere in this system.
* Importance is carried by the **emphasis ladder**: size → space → one accent colour →
  italic. In that order. Never by weight.
* **Letter spacing is 0 (standard) everywhere.** Uppercase mono micro-labels may carry
  `+0.06 rem`; nothing else. A run-level tracking value left set on body text is a
  defect, not a choice.

### Micro-label convention

Uppercase, letterspaced, mono, small: `SECTION 2.2 — COMPARISON OF TECHNOLOGY ROUTES`.
Used for kickers and panel labels, never for sentences.

---

## 4. Geometry

| | |
|---|---|
| **Stroke widths** | measured from production SVG: `0.5`, `0.57`, `0.79` → **treat 0.5–0.8 px as the canonical hairline** at illustration scale |
| **Corners** | **zero radius.** No rounded corners, anywhere |
| **Effects** | no gradients, no drop shadows, no bevels, no glows, no 3-D |
| **Arrows** | thin, with a small solid head. Curved only when the flow genuinely curves |
| **Whitespace** | **part of the drawing.** Do not crowd. A figure with no breathing room is wrong even if every element fits |

### Building blocks worth reusing

From the same visual family: radiating concentric-hairline fans, spiral/root forms,
ellipse clusters, circle-with-crosshair constructions, thin curved arrow connectors.

---

## 5. Chart rules (matplotlib)

1. **Canvas** = `PAPER`. In DOCX/HTML the figure sits on the page tone, so a white chart
   background is a visible defect. **Read §9b before implementing this** — the corpus
   achieves it by exporting embedded charts *transparent*, not by filling them.
2. **No chart frame.** No box around the plot area.
3. **No gridlines**, except faint horizontal `RULE_SOFT` lines at 10 % where a reader
   genuinely needs to read a value off an axis.
4. **Direct-label the series** at the end of the line or bar. Use a legend only when
   labels would collide.
5. **One accent hue per chart**, by semantic meaning. `SEED_BROWN` and greys for
   secondary series.
6. **DM Mono for all numerals** — data labels, axis figures, source line.
7. **Source line under every figure**: `Source: <primary source> · Retrieved <YYYY-MM-DD>`,
   mono, `INK_MUTED`.
8. **Caption** in serif italic, numbered `Figure N —` / `Table N —`.
9. **Export SVG** for HTML, **PNG at 300 dpi** for DOCX.
10. **Never**: default matplotlib colours, 3-D bars, pie-chart gloss, dual-axis tricks.

Series palettes are defined, not improvised:

```
SERIES_SYNBIO  = [MEADOW, MOSS, SEED_BROWN, ROSE, CLAY]
SERIES_FINANCE = [JPM_INK, JPM_BRONZE, JPM_SKY, JPM_SLATE, SEED_BROWN]
SERIES_SINGLE  = [MOSS]
```

---

## 6. Financial sub-theme (J.P. Morgan register)

Applies to company landscapes, financial models, valuations, market sizing and any
investment-return figure. **Same typography, same hairlines, same zero-radius
discipline** — only the accent set changes. That is what makes it a sub-theme rather
than a second style.

| Token | Hex | Role |
|---|---|---|
| `JPM_PAPER` | `#F4EFE7` | canvas (JPMC travertine) |
| `JPM_INK` | `#0B2A4A` | deep navy — headings, primary series, table header band |
| `JPM_SKY` | `#A6D7F0` | secondary series, fill bands |
| `JPM_BRONZE` | `#8F5A39` | accent, emphasis figure, benchmark line |
| `JPM_SLATE` | `#5A6470` | axis, labels, de-emphasised series, footnotes |

Conventions:

* **Waterfall / bridge** for any value build-up. This is the signature financial form.
* **Comparison tables in mono**, generous row height, no vertical rules.
* **Explicit units and periods in every axis label.** `USD m, FY2023–FY2030` — never a
  bare "Value".
* **Source line names the filing**: `Source: Glanbia plc Annual Report 2025, p.42`.
* JPMC's own rule applies: **typography in black, white or bronze only.**

---

## 7. The scale law — every figure, no exceptions

```
on-page pt = authored_pt × display_width_pt ÷ canvas_width_pt
```

* **Floor: 6.0 pt.** ≈ 2.1 mm em, ≈ 1.5 mm capitals — the smallest legible print size.
* **Target: 6.5 pt** (floor × 1.08). A figure at 6.00–6.05 is inside the measuring
  instrument's ±0.06 pt tolerance and **cannot be distinguished from a failing one**.
  A floor met by 0.05 pt is not met.
* Reference anchors: A4 = 595 × 842 pt · 16.6 cm text column = 470.55 pt ·
  16.11 cm figure cap = 456.69 pt.
* **Assert it on every build.** `Canvas.check_scale()` fails the build rather than
  reporting `ok` while a label prints at 4 pt.

---

## 8. Per-category conventions

The six families, and what each should reach for.

### 8.1 Scientific / process
Mechanisms, pathways, reaction routes, purification flows, strain genealogy.
* Horizontal flow, left to right; vertical when the process is a column.
* One accent marks **the step that matters** — usually the engineered or novel one.
* Molecules and structures: hairline, no shading, labelled with mono where possible.
* Include the reaction condition (`pH 7.4`, `50 °C`) as a mono micro-label.
* Purification: show what is removed as well as what is kept.

### 8.2 Market / commercial
Market build-ups, price ladders, competitive positioning, application maps.
* **Build-ups read bottom-up**, contributions stacked, total labelled once.
* Price ladders: a horizontal log axis where the range is wide, linear otherwise.
* Always name the **basis** (per kg, per tonne, retail vs bulk) in the axis label —
  a price without its basis is not information.
* Competitive maps: two axes only, and label both ends of each.

### 8.3 Regulatory / compliance
Authorisation pathways, notice grids, risk registers, due-diligence checklists.
* Pathways as **gates on a line**, with the decision at each gate named.
* Notice grids and registers as **tables in mono** with hairlines — a table is a
  legitimate figure.
* Distinguish *required* from *recommended* typographically, not by colour alone.
* Date everything; a regulatory figure without dates is not usable.

### 8.4 Financial
See §6. Waterfalls for build-ups, comparison tables for statements, footprint charts
for segmentation.

### 8.5 Timeline / roadmap
* A single horizontal rule; events on it; **labels alternating above and below** to
  double the usable density without crowding.
* Past solid, planned dashed.
* Years in mono.
* Annotate the **decision point**, not every event.

### 8.6 Matrix / scorecard
* Weighted tables, veto cascades, tier structures, specification tables.
* **Score cells as marks, not colours** — dots, half-squares, crosses — so the figure
  survives greyscale printing and colour blindness.
* Always print the weights and the scale.

---

## 9. Furniture — every figure carries all three

1. **Caption**: serif italic, `Figure N — …`
2. **Source line**: mono, `Source: <primary source> · Retrieved <YYYY-MM-DD>`
3. **Kicker** (optional): uppercase mono micro-label at the top

A figure missing its source line is incomplete, regardless of how good it looks.

---

## 9b. How the canvas is actually exported — measured, not assumed

**This is the rule the implementation uses, and the spec above states it wrongly if you
read "canvas = PAPER" literally.** Measured across the 80 delivered figures:

| | count | why |
|---|---|---|
| **transparent PNG** (`savefig(transparent=True, facecolor="none")`) | 18 | embedded in DOCX — the **page tone shows through**, which is what §5.1 actually wants |
| **PAPER-filled PNG/SVG** (`facecolor=PAPER`) | 62 | standalone files for HTML, and every drawn (non-chart) figure |
| opaque white | **0** | — |

So the correct rule is:

* **For a chart that will be embedded in a DOCX → export transparent.** A white-filled
  chart on a paper page is a visible rectangle; a transparent one sits on the page.
* **For a chart or drawing that will also be opened standalone or placed in HTML →
  export PAPER-filled**, because transparency against a browser's white shows white.
* **Export both** (`chartkit`-style `save()`) and let the consumer choose. That is what
  the corpus does, and it is better than either option alone.

**Measurement trap, recorded because it caught me twice.** A transparent PNG read with
`PIL.Image.convert("RGB")` is flattened against **white**, so a correct transparent figure
measures as an opaque white one. Check `im.mode` and sample the **alpha** channel, or the
"defect" you find will be your own instrument. (The first attempt also pasted figures onto
white cells to build a contact sheet — which is the same mistake with an extra step.)

---

## 9c. Chart forms in use

§5 gives the rules; these are the actual forms the corpus uses. Prefer one of these to
inventing a new shape.

| form | use | notes |
|---|---|---|
| **Horizontal bar, end-labelled** | rankings, comparisons, segment splits | the workhorse. No axis needed when the label carries the value |
| **Vertical bar** | few categories, short labels | |
| **Line / trend** | anything over time | direct-label the series at the right end; never a legend unless labels collide |
| **Stacked column** | composition over time | one accent + neutrals; never more than one accent hue |
| **Scatter** | many observations, two variables | the corpus has one with ~100 labelled points — **this needs a bigger canvas and careful label sizing, and is the form most likely to breach the floor** |
| **Waterfall / bridge** | value build-ups (financial) | the signature financial form |
| **Break-axis chart** | a category far larger than the rest | draw the break explicitly; do not silently truncate |
| **Paired panels** | two related series side by side | keep one shared header and one shared source line, or it reads as two figures |
| **Boxed flow / process** | chemical and process routes | boxes + thin arrows; thin black borders; **no more than one accent hue of fill** |
| **Timeline** | dated events | one rule, events alternating above/below |

Two implementations exist in the corpus and both follow this style: the drawn figures go
through `diagram_kit.py`; charts go through `chart_kit.py`. Older scripts used
`slice04/chartkit_a.py` and `cosmetic/figures.py` — read them if you need a precedent, but
build new work on the two kits in this folder.

---

## 9d. Figures that came from somewhere else

Not every figure in a set was drawn in-house. The corpus contains screenshots of published
papers and patent filings, photographs, and charts exported from other people's tools.
**The style doc must say what to do with them, because a successor will otherwise either
redraw them badly or leave them inconsistent.**

### The decidable test

Do **not** classify by "is it a chart?" — that gets it wrong. Two figures can both be line
charts, and one is rebuildable while the other is not. Classify by:

> **Are the DATA VALUES present in the image?**

| if the image shows… | then | example from the corpus |
|---|---|---|
| **values printed on it** — axis numbers, data labels, percentages, a table of figures | **REBUILDABLE.** Rebuild it in the style from those numbers, and keep the original source line | a market-share pie chart with every percentage labelled |
| **shape only** — a curve, a chromatogram, a spectrum, a trend with no labels | **MUST KEEP.** The data does not exist in a recoverable form; redrawing means inventing it | an HPLC chromatogram whose y-axis has no numbers |
| **document chrome** — patent margins, "SUBSTITUTE SHEET", journal columns, screenshot borders | **MUST KEEP.** That chrome *is* the provenance; removing it destroys the evidence that this is a quotation | a WO patent figure |
| **a photograph or micrograph** | **MUST KEEP.** Nothing to redraw | product shots, microscopy |
| **text in another language, as an image** | **MUST KEEP.** Retyping risks introducing errors into a quotation | a captured table in Chinese |

**The test is deliberately about information, not about aesthetics.** A figure can look
crude and still be rebuildable (a labelled bar chart); it can look crisp and still be
irreplaceable (a clean unlabelled chromatogram).

### A trap when you survey them

**Judge at full resolution, not on a contact sheet.** A thumbnail pass over these figures
classified 19 as "rebuildable charts"; reading them at full size reversed two of the first
three I checked — a chromatogram and a patent figure both looked like ordinary line charts
at 240 px wide, and neither is rebuildable. Small images hide the absence of axis numbers.
If you cannot read the numbers in the image you are looking at, you are looking at the
wrong image.

### Duplicate embeddings

Measured in this corpus: **5 pairs of byte-identical images** embedded twice
(`002=006`, `012=021`, `013=022`, `014=023`, `015=024`). This is not necessarily a defect —
the same figure may legitimately appear in two documents — but it means **counting
placements over-counts distinct figures**, and it means a fix applied to one copy must be
applied to its twin. Check by hash before and after any figure work.

### Report, don't normalise

**Report every external figure rather than silently rebuilding it.** The count matters: a
reader who knows which figures are quotations reads the report differently. In the source
corpus this class was 50 of 281 displayed figures — around a fifth.


---

## 10. The forbidden list

Extracted from a corpus of ~100 figures and the defects found in them. Each of these
was an actual defect at least once.

* Default matplotlib colours · 3-D bars · pie-chart gloss · dual axes
* Gradients, drop shadows, bevels, glows, rounded corners
* A white or transparent canvas where the page is paper
* `bbox_inches="tight"` on any figure whose annotations overhang — it grows the canvas
  and silently shrinks every label in proportion
* More than one accent hue per figure
* Bold · italic used for emphasis instead of the ladder · any tracking on body text
* Crowding: a figure where whitespace was sacrificed to fit one more element
* A figure with no source line
* Labels below 6.0 pt on the page — **the most common and most damaging defect**, and
  the one most easily missed because the source script looked correct
