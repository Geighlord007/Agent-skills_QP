# `synbio-editorial` — the figure reproduction spec, CORE

**The file you read while drawing.**

> **What this is.** The values, the rules, the numbers, the recipes and the decision rules of the
> `synbio-editorial` house figure style. Every constant a drafter needs is here: where a figure
> needs a value, the value is on the page.
>
> **What `STYLE_REFERENCE.md` is.** The longer-form companion: the same rules with the full
> per-device detail — every chart form, every legend form, the per-hue meaning table, the
> annotation kit, table metrics. Section numbers there are that file's own; `C0.2` maps this
> file's sections to them.
>
> **Precedence.** Where this file and the drawing code disagree, the code wins. Where this file
> and the figure in front of you disagree, the figure wins — match it and report the difference.
>
> **Not in this toolkit.** The audit record of the engagement that produced this style — the
> evidence base, the measurement discipline, the per-figure findings, the verdict tables and the
> duplicate groups — is deliberately kept out and lives with that project.

## C0. How to use this file

### C0.1 Where authority sits

1. **The drawing code wins.** `tools/design/brand.py`, `tools/design/schematic.py`,
   `diagram_kit.py` and `chart_kit.py` hold the constants. Where a value here disagrees with the
   code, the code is right.
2. **A reading taken off a finished image identifies which token was used; it is never a
   measurement of the token's value.** Colour readings are bucketed and cannot resolve close
   tokens.
3. **Type size and face are requirements.** No delivered image carries a page-width reference, so
   C7's scale law and C8's assignments cannot be checked against one. They are the requirement,
   not an observation.

### C0.2 Numbering, and where everything comes from

This file's sections are **new** (`C0`–`C20`). They deliberately do **not** reuse the
reference's numbers, so no section number is defined twice across the two files. A citation of
detail there is always written in full: `STYLE_REFERENCE.md §N.M`. That file's numbering is
stable, so every reference within it resolves within it.

| This file | Further detail in |
|---|---|
| C0 | §0 |
| C1 | §4 |
| C2 | §5 (rule and decision procedure); the per-hue collision table is `STYLE_REFERENCE.md §5.2` |
| C3 | §6 |
| C4 | §7, §9 |
| C5 | §8 |
| C6 | §10 |
| C7 | §11 |
| C8 | §12 (font stacks are new — see C8.3) |
| C9 | §13 |
| C10 | §14, §15, §16, §17, §18, §19 |
| C11 | §20, §21, §22, §23, §24, §25 |
| C12 | §26 |
| C13 | §27 |
| C14 | §28 |
| C15 | §29, §30, §31, §32, §33, §34, §35, §36, §37 |
| C16 | §38, §39, §40, §41, §42, §43, §44 |
| C17 | §45, §46, §47, §48, §49, §50, §51 |
| C18 | §53, §15.1, §17.1, §18.2, §27.2, §42, §47.3 (`C18` is new; the coordinates are approximate) |
| C19 | §54, §55 |
| C20 | §52, §56 |
| Appendix | Appendix C — the forbidden list |

**The right-hand column names where the fuller detail of a device lives**, not an address in this file. A pointer to something you might want to look up is always written `STYLE_REFERENCE.md §N.M`.

### C0.3 Vocabulary

**UNRESOLVED** means two readings are live and the corpus does not settle it — reproduce the
figure in front of you, do not harmonise. **`COR-n`** is an entry in the corrections register (`STYLE_REFERENCE.md §2`) — a `COR-n` cited here is a warning that v1 stated the rule wrongly.

---

## C1. Tokens

All hexes are from `tools/design/brand.py`. **Never hard-code a hex anywhere else.**

### C1.1 Canvas and ink

| Token | Hex | Role |
|---|---|---|
| `PAPER` | `#F7F5EB` | page canvas for house figures |
| `BONE` | `#EDEADB` | secondary panel, table header band, footer |
| `TRAVERTINE` | `#F4EFE7` | financial-register canvas — assignment corrected, see C3 |
| `INK` | `#000000` | all text, all rules |
| `INK_2` | `#3A3A38` | body copy where pure black is too hard |
| `INK_MUTED` | `#6B6B66` | captions, source lines, metadata, axis tick labels — verified exactly |
| `RULE` | `#000000` | 1 px hairline; same value as `INK`, separate name |
| `RULE_SOFT` | `#D8D3C4` | faint gridline — and also a series colour, see C4.4 |

### C1.2 Accents

| Token | Hex | Code-assigned meaning |
|---|---|---|
| `MOSS` | `#9EA617` | *natural*; chart hue 1; `NATURAL = MOSS` |
| `MEADOW` | `#617D24` | *data series / positive*; chart hue 2; `POSITIVE = MEADOW` |
| `CLAY` | `#E05E3D` | *engineered / designed / animal*; `ENGINEERED = CLAY`; also `CONFIDENCE["UNVERIFIED"]` |
| `ROSE` | `#C28775` | *evidence*; chart hue 3; `EVIDENCE = ROSE`; also the negative waterfall bar |
| `SEED_BROWN` | `#D1B594` | *low emphasis, bands*; chart hue 4; `NEUTRAL = SEED_BROWN`; also `CONFIDENCE["ESTIMATED"]` |
| `LIME` | `#E0DB00` | fill only by intent — but see C2.3 |

`TEXT_SAFE_ACCENTS = (MOSS, MEADOW, CLAY)`. Clay on paper is ≈3.6:1 — large text only.

### C1.3 The JPM set

| Token | Hex | Intent | Corpus reality |
|---|---|---|---|
| `JPM_PAPER` | `#F4EFE7` (= `TRAVERTINE`) | financial canvas | see C3 |
| `JPM_INK` | `#0B2A4A` | deep navy — headings, primary series, header band | measured `#002448` |
| `JPM_SKY` | `#A6D7F0` | secondary series, fill bands | measured `#9CCCF0` / `#B1DAEE` at ≈0.88–0.9 |
| `JPM_BRONZE` | `#8F5A39` | accent, emphasis figure, benchmark line | measured `#845430`, `#805030` |
| `JPM_SLATE` | `#5A6470` | axis, labels, de-emphasised series, footnotes | **the token does not reproduce the corpus.** Measured slate centres `#3C546C`, `#304860`, `#243C54`, `#486C9C` — see `COR-24` |

**Slate rule.** Matching an existing figure → sample its slate from that figure. New work →
`#5A6470` is the token, and expect the result not to match its neighbours.

### C1.4 Semantic aliases are code

```
brand.py:      NATURAL = MOSS; ENGINEERED = CLAY
               TEXT_SAFE_ACCENTS = (MOSS, MEADOW, CLAY)
               CONFIDENCE = {VERIFIED: MEADOW, ESTIMATED: SEED_BROWN, UNVERIFIED: CLAY}
schematic.py:  ACCENTS = {natural: MOSS, engineered: CLAY, data: MEADOW,
                          evidence: ROSE, neutral: SEED_BROWN, finance: JPM_BRONZE}
chart_kit.py / diagram_kit.py:
               NATURAL = MOSS; ENGINEERED = CLAY; EVIDENCE = ROSE
               NEUTRAL = SEED_BROWN; POSITIVE = MEADOW
```

`ACCENTS["finance"]` is `JPM_BRONZE`, **not** `JPM_INK` — a financial figure that takes its
accent from `ACCENTS` starts on bronze.

`SERIES_SYNBIO = [MEADOW, MOSS, SEED_BROWN, ROSE, CLAY]` ·
`SERIES_FINANCE = [JPM_INK, JPM_BRONZE, JPM_SKY, JPM_SLATE, SEED_BROWN]` ·
`SERIES_SINGLE = [MOSS]`.

---

## C2. Choosing the accent hue

### C2.1 The rule

Pick the hue by **the role the mark plays in this figure's argument**, not by taste and not by
tick order. Where two roles collide inside one figure, the second hue must belong to a
**different semantic class** — a comparison, a tag, an alert — and never be a second colour for
the same class.

### C2.2 Role → hue

The corpus uses each hue across several roles; the fuller per-hue table is `STYLE_REFERENCE.md §5.2`. The anchors a drafter needs:

| Hue | The role it carries |
|---|---|
| `MOSS` `#9EA617` | availability / disclosed · natural variant · workflow spine · the "natural" root · a plain series fill |
| `MEADOW` `#617D24` | data series / positive · achieved value · flow path · ordinal rank (as a lightness ramp) · biological agent |
| `CLAY` `#E05E3D` | the figure's subject, the engineered thing · the subject brand or market · the largest value · a waterfall total · an increment · a reference threshold · the US regulatory pathway |
| `ROSE` `#C28775` | **chronology and process** — timeline dots, timeline leaders, and in flows the edge bar, connector, start dot and circle-with-X terminus · evidence (measured, assayed, observed) · a duration or gap band · the negative waterfall bar |
| `SEED_BROWN` `#D1B594` | neutral / low emphasis / context band · partial disclosure · a secondary series · category lanes |
| `JPM_BRONZE` | exactly one emphasised item inside an ink field — top supplier, latest round, top family, top decile, latest half-year, milestone. "Brown = the one that matters" |
| `JPM_INK` navy | the primary measured series, the total, a calculation · box outlines, body text inside boxes, axis lines in the register |
| sky blue | a secondary series · a threshold-rule colour · a bubble halo · a decrement · `UNVERIFIED` fill · a segment with no valence |
| `RULE_SOFT` `#D8D3C4` | gridline colour, **and** the third series in 187 |

The corpus is genuinely not one-to-one: two different greens coexist and are not
interchangeable (089/091 match `MEADOW` exactly; 069/064 measure ≈`#507010`, not a token), and
116 vs 117 are the same construction with two different hues for the same class. **Sample the
original; do not harmonise.** Reproducing a figure means using the hue that figure used.

### C2.3 The three exceptions

1. **`SEED_BROWN` and `LIME` may be text** (`COR-4`). The prohibition is false; what is true is
 a legibility constraint — a short, isolated, large-enough string only. The two recorded uses
 are a 4-character year and a 10-character phrase.
2. **The alert hue.** One figure uses a second accent purely to flag a number that does not
 reconcile with its neighbour: `CLAY` italic text over a group whose data is `MEADOW`. The
 alert is `CLAY`, **text only**, never a fill, **at most once per figure**, and it must be
 preserved as an exception or the next person will "correct" it away.
3. **A figure may carry no accent at all** — see C17.5.

### C2.4 The matched pair to copy

081 and 082 are the same construction — same kicker, parallel titles, same fishbone — and differ
in exactly one thing: the root node's accent band is `MOSS` in the food figure and `CLAY`
in the chemical figure. Use the pair as the reference implementation of C2.1.

---

## C3. Canvas

| Class | Canvas |
|---|---|
| house drawn figure or house chart | `PAPER #F7F5EB`, opaque |
| JPM / cosmetic register | `TRAVERTINE #F4EFE7`, opaque |
| figure placed in a DOCX where the page tone must show through | transparent (alpha 0) |
| photographic cut-out | transparent, always |
| facsimile or foreign capture | keeps its own canvas, white included |
| near-white off-family | `#F8F9F8` |

**Rules.**

1. **The canvas is chosen per DOCUMENT, not per figure's subject** (`COR-13`). A
 market/company register draws every one of its figures on its own canvas — including a
 metabolic pathway, a polymer repeat unit, a patent route and a regulatory timeline.
2. Default: house figure → `PAPER` opaque.
3. Page tone must show through → export transparent (C19).
4. Photographic cut-out → transparent.
5. Facsimile or capture → keeps its own canvas.
6. **Never tint a canvas.** The exact token hex, or transparent, or the foreign file's own
 pixels. No `PAPER` at 40 %.

**The per-document palette switch.** Scientific/process figures: `PAPER` with
`MOSS`/`MEADOW`/`SEED_BROWN`. Market/company/cosmetic/protein-materials registers:
`TRAVERTINE` with the JPM set. Regulatory BLG figures: white with a **third, undocumented
blue-grey set** — `#486C9C`, `#849CC0`, `#9CB4CC`, `#6084B4`, `#244860`, `#547890`. Either add
that set to the token table or replace it; leaving it undocumented makes a successor build a
BLG figure in `MOSS` and be wrong on every mark.

**`PAPER` vs `TRAVERTINE` is unresolved.** They differ by (3, 6, 10) RGB — 1.2–3.9 % per
channel — which is below the resolving power of the quantised method that the three disagreeing
readings used. Do **not** write "finance figures use `TRAVERTINE`" as a rule: exact corner RGB
was never run over the disputed indices. Sample the figure you are reproducing; for new work
follow rule 1. Full account: `STYLE_REFERENCE.md §6.3`.

**White is a class, not always a defect.** Opaque white is correct for three classes: facsimile
material of a filing, statement or press page; foreign captures whose chrome is the provenance;
and the generation-1 drift figures, which are right for their own generation and wrong for new
work. White **is** a defect on a newly drawn house figure.

---

## C4. Fill, alpha, hatch, fill-state

### C4.1 Flat fill only

One flat colour per fill. No gradient, bevel, shadow or texture — the hatch of C4.4 is the
only exception, and the only 3-D in the corpus is an imported render (C17.3) and a defect.

### C4.2 Ramps

A ramp is **one hue, three to four steps, monotonic in lightness**, and it means *rank* or
*type* — never *category variety*. In the corpus in at least four places (a 3-step olive tier
ramp, a lightness ramp with hollow = off-scale, three blues for three series, four blue-greys
for four step types).

### C4.3 Alpha — use the ladder, invent nothing

| Use | Value |
|---|---|
| the drawing scripts' opacity ladder | **0.14, 0.16, 0.22, 0.28, 0.35, 0.4, 0.45, 0.5, 0.55, 0.85** |
| the header rule's opacity | **0.55** |
| a column band | **0.75** |
| area fill under a line: the series hue at ≈13 % over the canvas | `MEADOW` 13.3 % → `#E3E5D1`; `MOSS` 13.5 % → `#EBEACF` |
| bubble / halo fill: the token at ≈0.9 alpha, not the token | `#B1DAEE` = `JPM_SKY #A6D7F0` at ≈0.88 over `TRAVERTINE` |

**Use a ladder value.** A reproduction that lands between two of them reads as a different
hand.

### C4.4 Hatching

 `diagram_kit.hatch(color, key="diag", pitch=5.0, width=0.9)` — a 5.0-unit tile with a
0.9-unit stroke and four registered patterns:

| key | path | reads as |
|---|---|---|
| `diag` | `M0,5 l5,-5` — one 45° line per tile, bottom-left → top-right | the default |
| `cross` | `M0,5 l5,-5 M0,0 l5,5` | cross-hatch |
| `horiz` | `M0,5 l5,0` | horizontal rules |
| `dots` | circle r = `width × 0.8` = 0.72 at the tile centre | stipple |

**Hatch is a state, not a texture.** It means placeholder / insufficient data / not evidenced ·
liability vs a filled glyph that means evidence · unverified · eliminated · a stated target not
yet built vs solid = built · a non-modelled remainder · a subtracted cost in a bridge · a
restatement marker · geological-unit separation.

**Rules.** Hatch uses the same hue as the fill it replaces. Hatch always carries a key entry or
a sentence (C10.6, C11.4). A hatched block that is not a modelled segment must say so in the
footer. Default to `diag`; where the original is mirrored, mirror it (the code cannot emit a
mirrored `diag`).

### C4.5 Hollow versus solid

Fill state is the corpus's uncertainty vocabulary, and the same contrast means different things
in different figures — specify it per element:

| Contrast | Means |
|---|---|
| hollow ring / solid dot | claimed vs observed |
| hollow circle / solid | estimated vs tabulated |
| hollow bar / solid bar | exclusive vs non-exclusive licence |
| hollow block / filled | target not yet met vs achieved |
| hollow / filled accent | base year or reported actual vs forecast year |
| hollow / filled | future or current vs past |
| outline / filled | before vs after treatment |
| solid square / vertically split half-square / hollow | disclosed / partly disclosed / not stated |
| hollow square | a category not on that column's ordinal scale |

### C4.6 Bands and zones

An uncertainty or reference band is hatched or shaded with a **dashed edge**, labelled
**above** the band, and drawn **over** the data — it visibly occludes points. A range that is
not a series is a vertical beige band for a working window or a dead period, or a pale pink
horizontal band for a duration or a gap. A homologous ceiling is a `SEED_BROWN` band with a
dashed edge, bracketed, labelled with the native value. **Overlay order:** background zones
before the marks; an uncertainty band that must occlude, after. Where a band covers points,
reproduce that — do not "fix" it.

---

## C5. Status tags

### C5.1 The three-state vocabulary

Printed inside the figure,-backed by `brand.CONFIDENCE`:

| Tag | Token | Semantics |
|---|---|---|
| `VERIFIED` | `MEADOW` | traced to a primary source; an outside filing confirmed it |
| `ESTIMATED` | `SEED_BROWN` | model / analyst estimate; a value digitised or repositioned from someone else's figure |
| `UNVERIFIED` | `CLAY` | no source, or stale; carried by an externally sourced panel |

### C5.2 Four placements, all available

1. **Prefix inside the title** — `ESTIMATED — <title>`, or a standalone tag on a timeline.
2. **Suffix inside a cell, after the value** — `85%–98% (random distribution) VERIFIED`.
3. **A count tag in the header row** — `1 VERIFIED CELL`.
4. **Suffix on a footnote line** — `UNVERIFIED at source.`

Also observed appended to an axis or segment label: `Serviceable available market 125,711 t
(ESTIMATED)`. **Form:** uppercase, letterspaced, `INK` or `INK_MUTED`, **never a colour on its
own**, always adjacent to the thing it qualifies.

### C5.3 Chips, fill key, fill-as-tag

**Chip rendering:** small square-cornered filled chips — `MEADOW` fill = `VERIFIED`,
`SEED_BROWN` fill = `ESTIMATED`, empty outline = untagged.

**The fill key:** a swatch key at the foot mapping fill colour to tag, titled
`HOW TO READ THE FILL`. The fill itself is the legend.

**Fill-as-tag on boxes:** a grey/slate box is by definition an `ESTIMATED` input, a sky box an
`UNVERIFIED` one, a white outline box untagged.

---

## C6. Geometry

### C6.1 Stroke widths

 across 400+ primitive calls:

| Width | Where it is the default |
|---|---|
| **0.8** | box borders, `line()`, `dot()` rings, `bar()` outlines, `column_icon` |
| **0.7** | header rule under the title, axis rules, major ticks |
| **0.6** | `axes.linewidth` in matplotlib, `frame()`, hairline table grids |
| **0.9** | crossed-circle X strokes, the rule under a table header, hatch strokes |
| **1.0** | `arrow()` |
| **0.5** | minor ticks on a log axis (0.45 in `log_axis`), box-plot whiskers |
| **0.54**, **0.56** | — |
| **1.4** | `lines.linewidth` — the only stroke this heavy |

**Canonical hairline at illustration scale: 0.5–0.8.** 1.4 is for chart series only; a diagram
never uses it.

### C6.2 Corners

**Zero radius.** `column_icon` passes `rx="0"` explicitly; confirmed case by case in every house diagram. Non-zero
radius is the fastest way to look imported. Rounded corners appear only in off-family figures.

### C6.3 Dashes

| Element | Pattern |
|---|---|
| a dashed box | `stroke-dasharray="3 3"` |
| a dashed arrow or line | `stroke-dasharray="4 3"` |

No other dash pattern is in the code. `2 2` or `6 4` is off-family.

### C6.4 Effects

None. No gradient, drop shadow, bevel, glow, 3-D or decorative translucency.

---

## C7. Type

### C7.1 The scale law — a REQUIREMENT, never a measurement

```
on-page pt = authored_pt × display_width_pt ÷ canvas_width_pt
```

| Constant | Value |
|---|---|
| `MIN_ONPAGE_PT` — the floor | **6.0 pt** |
| the target | **6.5 pt** (6.00–6.05 is inside the instrument's ±0.06 pt tolerance and cannot be told from a failing figure) |
| `_TYPICAL_DISPLAY_PT` | **455.0 pt** |
| the library's measured display range | 340–471 pt |
| `TARGET_CANVAS_W` | **780 units** |
| reference anchors | A4 = 595 × 842 pt; a 16.6 cm text column = 470.55 pt; a 16.11 cm figure cap = 456.69 pt; `chart_kit` asserts at **456.6929133858268 pt** |

 `onpage_pt(font_units, canvas_w=780, display_pt=455.0) = font_units × display_pt ÷
canvas_w`. `Canvas.check_scale()` fails the build when the smallest label is under the floor.

**Type size and face cannot be read from a raster.** This law and C8's assignments are
requirements. They have never been checked against the delivered figures — do not claim a
delivered figure passes.

### C7.2 The figure type ramp

 — the sizes `schematic.py` and `diagram_kit.py` emit, in **canvas units**. This is the
whole FIGURE ramp; there is no other.

| Element | Units | Face | Ink |
|---|---|---|---|
| figure title | **22** | sans | `INK` |
| kicker | **11** | mono | `MUTED`, tracking +1.6 |
| section / micro-label | **11** | mono | `MUTED`, tracking +1.4 |
| box main label | **13** | sans | `INK` |
| box sub-label | **10.5** | mono | `MUTED` |
| axis tick label · axis unit label · legend label | **10.5** | mono | `INK_MUTED` |
| table cell | **13** (default `size`) | mono for columns > 0, sans for column 0 | `INK` |
| table header | **10.66** (= `size × 0.82`) | mono | `INK_MUTED` |
| timeline year | **12** | mono | `INK` |
| timeline event label | **13** | sans | `INK` |
| timeline sub-label | **11** | serif **italic** | `MUTED` |
| free text default | **13** | serif | `INK_2` |
| wrapped block | **11.5** | sans | `INK_2` |
| note | **11.5** | serif **italic** | `MUTED` |
| caption | **13** | serif **italic** | `MUTED` |
| source line | **12.5** | mono | `MUTED` |

**Printed size at the three widths the scripts use** (`display_pt = 455`):

| Units | 780 (×0.583) | 940 (×0.484) | 560 (×0.813) | 1320 (×0.345) |
|---|---|---|---|---|
| 22 | 12.83 | 10.65 | 17.88 | 7.58 |
| 13 | 7.58 | 6.29 | 10.56 | 4.48 |
| 12.5 | 7.29 | 6.05 | 10.16 | 4.31 |
| 12 | 7.00 | 5.81 | 9.75 | 4.14 |
| 11.5 | 6.71 | 5.57 | 9.34 | 3.96 |
| 11 | 6.42 | 5.32 | 8.94 | 3.79 |
| 10.5 | **6.13** | **5.08** | 8.53 | **3.62** |

**Read the bold cells.** At **780 units every ramp size clears the 6.0 pt floor**. At 940 every
size below 12.5 fails. At 1320 nothing on the ramp is legible.

**Two knobs, not interchangeable**, both defaulting to off:

* `type_scale` multiplies the **whole ramp**, preserving the hierarchy exactly. Use when the
 figure has room.
* `min_type` raises **only the runs under the floor**. Use when a uniform raise would push a
 long label out of its box; it costs some of the size hierarchy.

### C7.3 The document type scale — not the figure's

 `brand.TYPE`, in points, for DOCX and print. Do not use it for canvas text.

| role | pt | role | pt |
|---|---|---|---|
| `display` | 30.0 | `body_lg` | 13.0 |
| `h1` | 22.0 | `caption` | 8.5 |
| `h2` | 16.0 | `kicker` | 8.0 |
| `h3` | 12.0 | `numeric` | 9.5 |
| `body` | 10.5 | — |
`LEADING_BODY = 1.52`; `MEASURE_CHARS = (66, 70)`. The conversion between the two ramps is the
scale law, not a mapping table: a figure authored at 780 units and displayed at 456.69 pt prints
a 13-unit label at 7.61 pt.

### C7.4 Italic is a semantic slot, not emphasis

* **taxonomic italics** — species names italic serif while company names stay upright in the
 same label: `Trichoderma reesei`, `Komagataella phaffii`, `Aspergillus oryzae`,
 `Kluyveromyces lactis`. **Load-bearing; omit it and a reader notices immediately.**
* **qualitative outcomes and method notes** — mono meta → sans measure title → serif-italic
 outcome.
* **the sub-label of a hub or box.**
* **a verdict** inside a timeline's assessment box.

**The deck-line device** — an italic serif line under the title, set **smaller** than the title,
carrying the takeaway, the method and basis, the basis or unit in parentheses, or the
arithmetic. Also operates as an in-figure sub-label at sub-label size.

**The "signature move" is unverified.** v1 called a serif-italic phrase ~1.24× its surrounding
sans "the single most identifiable element of the style"; none of the six inspection passes
confirmed it and one searched 47 figures without finding it. Use the deck-line device. Do not
cite 1.24× as measured. (`STYLE_REFERENCE.md §12.4`.)

### C7.5 Weight

**400 only. There is no bold anywhere in this system.** No kit emits `font-weight` except
through a `weight=` argument nobody passes. Importance is carried by the **emphasis ladder**:
size → space → one accent colour → italic, in that order.

---

## C8. Faces and font stacks

### C8.1 The three faces

| Face | Family name | Files | Role |
|---|---|---|---|
| **Newsreader** | `Newsreader` | `Newsreader-Regular.ttf`, `Newsreader-Italic.ttf` | body copy, display, captions, notes, pull-quotes |
| **Schibsted Grotesk** | `Schibsted Grotesk` | `SchibstedGrotesk-Regular.ttf`, `-Italic.ttf` | headlines, section titles, box labels, navigation |
| **DM Mono** | `DM Mono` | `DMMono-Light.ttf`, `-Regular.ttf`, `-Medium.ttf` | years, numbers, axis figures, micro-labels, source lines |

 from `brand.py` (`FONT_SERIF` / `FONT_SANS` / `FONT_MONO`) and `schematic._font_css()`.

**Two traps.** The bundled Newsreader subset is a variable-font instance declared as
**`Newsreader 16pt`**, so matplotlib resolves it by prefix match — an exact-match-only lookup
silently picks DejaVu Serif. And **glyph gaps are real**: none of the brand faces carries
U+2265 (≥), U+03B5 (ε) or U+2082 (₂). Chrome falls back per character, so SVG schematics are
fine; **matplotlib does not** — it draws a missing-glyph box and says nothing. A chart needing
one of those characters must pass a **list**: `brand.font_stack(kind)` returns
`[brand face, "DejaVu Sans", "DejaVu Serif", "DejaVu Sans Mono"]`.

### C8.2 Face per figure element

 — no face can be confirmed from a raster; this is the requirement.

| Element | Face |
|---|---|
| chart title | **sans**, larger (`smallest_pt × 1.5` in `chart_kit`) |
| serif title (finance register) | **serif** — the register uses serif titles consistently |
| kicker | **mono** |
| x/y axis title | **sans** in `chart_kit`, **mono** in `Canvas.linear_axis` — both exist; match the figure |
| tick labels · value labels | **mono** |
| box main label | **sans** |
| box sub-label | **mono** |
| category labels (company, ingredient, microorganism, rank ordinals) | **mono** — v1 wrongly excluded categories from mono |
| panel letter | **serif** mixed case (`A. …`) as part of a panel title; **sans** in-figure (`A`, `B`, `C`, `D`); **serif** lowercase parenthesised `(a)` in a boxed corner label |
| captions and notes | **serif italic** |
| source line | **mono** `INK_MUTED` |
| tags | **uppercase mono** |
| table column headers | **mono**, uppercase |
| table row labels | **sans** (column 0, lowercase) in `table()`; **mono** in the older tables |
| table cell content | **mono** for every house table |
| numerals | **mono** — *except* facsimile statements, which are **serif** |

**Face-per-column discipline**, the corpus's actual rule: **mono for every number, unit, date,
accession code and structural metadata; sans for titles, box labels and measure names; serif
italic for qualitative outcomes and method notes; serif roman for prose captions.**

### C8.3 Font stacks — Latin, CJK and mono

**Assigning a face is not enough; a stack must be declared.** That omission is why
mixed-language documents substitute unpredictably. Use these stacks verbatim and copy them
into the code:

```
Latin:       "Schibsted Grotesk", Calibri, sans-serif
CJK:         Arial
Mono:        "DM Mono", Consolas, monospace
Serif:       "Newsreader", Georgia, serif
```

**The rules.**

1. **Latin and ASCII text is set in Schibsted Grotesk, falling back to Calibri.** Calibri is the
 fallback because it is present on every Word installation the deliverables are opened in.
2. **Chinese and other CJK text is set in Arial.** A CJK run never inherits the Latin face —
 the two are chosen independently, and the CJK face is stated explicitly even when the Latin
 face is the default.
3. **The mono face keeps its existing job** — numerals, micro-labels and source lines — and
 **falls back to Consolas, then to any monospace**. `DM Mono` is a subset; Consolas is the
 Windows-present monospace that covers the glyphs it lacks.
4. The serif face falls back to Georgia. It is listed here for completeness because captions,
 notes and the deck line use it, even though the task of face assignment names only three.

**The consequence that matters for DOCX.** Word selects the East-Asian face **separately** from
the Latin face. A mixed-language run therefore needs **both** set on the run — `w:rFonts` with
`w:ascii` and `w:hAnsi` for the Latin face **and** `w:eastAsia` for the CJK face. Setting only
the Latin face is exactly what produces an arbitrary CJK substitution: Word picks a face from
its own East-Asian default rather than from the stack above, and the result varies by machine,
by locale and by whether the text was ever typed with an IME.

```xml
<w:rPr>
  <w:rFonts w:ascii="Schibsted Grotesk" w:hAnsi="Schibsted Grotesk"
            w:cs="Schibsted Grotesk" w:eastAsia="Arial"/>
</w:rPr>
```

> **Known gap — recorded, not yet fixed.** `tools/design/brand.py` holds `FONT_SERIF`,
> `FONT_SANS` and `FONT_MONO` only: there is **no CJK face constant and no fallback stack**,
> so the stacks in C8.3 exist in the specification and nowhere in the code.
> `tools/docx_brand.py` does set `w:ascii`/`w:hAnsi`/`w:cs`/`w:eastAsia` on every run, but its
> `EA_FACE` is hard-coded to **`SimSun`**, which is not the face this section assigns, and it
> too has no fallback chain. **Both files must be updated to match this section** — add a CJK
> face constant and an ordered stack to `brand.py`, change `EA_FACE` to `Arial` and drive the
> Latin face from the stack in `docx_brand.py`. **They were deliberately not changed when this
> section was written: the task was specification only.** This gap is carried in the cautions at the end of this file.

### C8.4 Ink colours for text

| Ink | Use |
|---|---|
| `INK` `#000000` | all text in the house style |
| `INK_2` `#3A3A38` | body copy where pure black is too hard — token; **UNRESOLVED** whether the measured occurrences are the token or anti-aliasing of thin serif strokes on `PAPER` |
| `INK_MUTED` `#6B6B66` | captions, source lines, metadata, caveats |
| `JPM_INK` `#0B2A4A` | **chart** titles, labels and numbers in the finance register — verified exactly |
| white knockout | text inside a filled slate or navy block |

---

## C9. Tracking

 — v1 got this wrong in both directions (`COR-26`):

| Element | Tracking | Unit |
|---|---|---|
| figure title (22 units, sans) | **−0.3** | canvas units |
| kicker (11 units, mono) | **+1.6** | canvas units |
| section / micro-label (11 units, mono) | **+1.4** | canvas units |
| body / everything else | **0** | — |

`brand.TRACKING_BODY_PT = 0.0` and `brand.TRACKING_KICKER_REM = 0.06` — the rem value
belongs to the **document** scale, not the canvas scale. `letter-spacing` scales with
`type_scale` so tracked micro-labels keep their register when the ramp is raised.

**Where letterspacing is used:** kickers · panel labels · row headers · table column headers ·
footer section labels · tags. **Never on body text** — a run-level tracking value left set on
body text is a defect, not a choice.

---

## C10. Furniture: kicker → header → title → footer → source

### C10.1 The kicker

Uppercase, letterspaced (+1.6), mono, size 11, `INK_MUTED`, **on its own line above the title**,
emitted at `(40, 46)`. It is a **path, not a label** — several refs chained with `·`
are normal, and it is where provenance-by-section is carried.

Forms in use: a `§`-section reference (`§3.2 OVERALL SCORING TABLE · WEIGHTED TOTAL OUT OF
5.0`) · two-level section + table · chained section refs · a subject breadcrumb (`MOLECULES &
DOSSIERS · INDUSTRIAL ENZYMES · FEED`) · subject · architecture · numbered section (`SECTION 2.2
— COMPARISON OF TECHNOLOGY ROUTES`) · taxonomy (`COMPANY LANDSCAPE · LISTED · PROCESS
TECHNOLOGY`) · company · model · source. A kicker may run to two lines; chained `§` refs are
the usual cause.

**The PLATFORM unit band** — a fixed three-part kicker plus a thin rule, then the title:
`PLATFORM · DOWNSTREAM PROCESSING · OSTEOPONTIN`. It functions as a section identity band, not
a caption.

**Separator by family**: `·` for scientific figures, `/` for commercial and
valuation figures, `—` for regulatory figures. All-caps, on its own line.

**Document-first order** in the cosmetic-ingredient figures: `DOCUMENT · SUBJECT · SECTION`
(`COSMETIC INGREDIENTS · PRO-XYLANE · DEVELOPMENT HISTORY`).

A status tag may be set **flush right on the kicker line**, opposite the kicker.

### C10.2 The header stack

```
[kicker]   uppercase mono micro-label        optional
[title]    sans, or serif in the finance register, sentence case
[rule]     full-width hairline, 0.7 units, INK at 0.55 opacity
```

 geometry: kicker baseline at `y = 46`. With a kicker the title moves to `y = 72` and
the rule to `y = 96`; without one, the title sits at `y = 50` and the rule at `y = 74`.
Horizontal margins are **40 units both sides**. `body_top` is the y **after** the rule, and
`frame()` defaults its top edge to `body_top − 14`.

The rule under the title is one line at `(40, y) → (w−40, y)`, `stroke-width 0.7`, `opacity
0.55` — that is the canonical form.

**Canonical choices.**

| Figure class | Use |
|---|---|
| a **drawn** diagram | kicker **required**; title recommended; the rule under the header when the figure is more than one row deep |
| a **chart** | title required; kicker optional; **no rule** under the header — charts open with a title plus a serif-italic subtitle, never a kicker |
| a **table figure** | title plus a key sentence; no kicker unless the table is numbered |

Two recorded defects to avoid: **081 lacks the hairline rule under the header that its twin 082
has** — treat 081 as defective and give it the rule; and 161's `COLUMN 1` occupies the title's
slot so the figure has no title at all, which is a structural label rather than a title.

### C10.3 Title and subtitle

* **Sentence case**, sans, `INK`, 22 canvas units, tracking −0.3, left-aligned at `x = 40`.
* **`<Subject> — <measure>`** with an em dash: `Evolva Holding — gross contribution margin by
 half-year`.
* A title may carry a count or method as a clause (`Thirteen strains, eight weighted
 dimensions`), a status prefix (`ESTIMATED — …`), or a period range (`…, FY2019–FY2024`).
* **Serif titles are the finance register's rule**, not a deviation: 059, 072, 073, 074 — all
 three finance figures among them. Sans is the default everywhere else (`COR-9`).
* **The subtitle / deck** is a serif italic line under the title carrying the takeaway, the
 method and basis, the basis or unit in parentheses, or the arithmetic. **Set smaller than the
 title** — this is the deck device (C7.4), not the unverified signature move.
* **Object sub-labels** — a mono sub-label naming the object rather than the value
 (`TABLE 2 · SUPPLIER SPECIFICATION`, `5 LAYERS`). Mono, uppercase, `INK_MUTED`.
* **Table numbering** — `TABLE N · …` lives in the kicker, not the caption. Forms in use:
 `TABLE N · …`, `TABLE 1-1`, `(Table 28)`. **`Figure N —` and `TABLE N ·` are different
 objects and do not share a slot.**
* **Punctuation.** Em dash between subject and subject-matter · en dash without spaces for year
 ranges (`FY2019–FY2024`) · `·` middle dot inside kickers and source lines · hyphen or en dash
 for data ranges, per the source · **an in-image caption's number separator is an en dash**
 (numbered with an en dash), against v1's em dash.

### C10.4 The footer stack

The foot, top to bottom. Not every figure carries every part; **where parts are present the
order is fixed.**

```
1  graphic
2  ALL-CAPS section label        (drawn figures)
3  caption, serif italic         a sentence, not numbered
4  italic serif explanatory / method note (1–3 paragraphs)
5  per-symbol or per-marker list (some figures)
6  mono source line
7  blank line
8  status / caveat line          mono, ALL-CAPS keyword + colon + sentence
9  caveat block                  numbered (i)(ii), provenance disclosures
```

**The section label** is all-caps, letterspaced (+1.4), mono, `INK_MUTED` — one of a small set
such as `DEVELOPMENT HISTORY`, `READING`, `WHY THE STRAIN IS NOT REPLICABLE`, `POSITION IN THE
PORTFOLIO`. v1 had no concept of this element.

**The italic method note** is a free-standing serif italic note under the figure, often 2–3
paragraphs, carrying method caveats. It is **distinct from the mono source line and distinct
from the caption**; it is the corpus's actual workhorse. It frequently opens with a status word
(`VERIFIED: …` / `ESTIMATED: …` / `UNVERIFIED: …`).

**The status / caveat line** is mono, ALL-CAPS keyword + colon + sentence, on its own line below
the source line, separated by a blank line. It may name third parties.

**A discrepancy note** is printed where the document's own numbers do not reconcile — `published
shares sum to 100.25%`. **Never silently normalise a total; print the discrepancy.**

**No rule between graphic and footer.** The separation is whitespace only. The one exception in
the corpus is a *header* rule between the title block and the timeline body, which is not a
footer rule.

**Length.** Notes may be longer than the figure — three-paragraph notes blocks exist. There is
no maximum; a source line overlapping the bottom bar is a spacing failure, not a length failure.

### C10.5 The source line

```
Source: <primary source>, <detail> · Retrieved <YYYY-MM-DD>
```

Mono, `INK_MUTED`, 12.5 canvas units, **always bottom-left or centred**.
`Canvas.source()` places it at `(40, h − 22)`; `chart_kit.source_line()` places it at
axes-fraction `(0.01, −0.01)` with `va="top"`. Both are bottom-left.

It often ends with a parenthetical stating what was and was not taken from the source
(`(embedded chart)`, `(segment labels and shares as printed)`).

**The provenance verbs — seven-plus forms in production. Match the form the figure needs; do
not harmonise.**

| # | Form | Example |
|---|---|---|
| a | canonical | `Source: <source> · Retrieved YYYY-MM-DD` |
| b | source + bare URL instead of a date | `Source: Li, H. et al., Foods 2023, 12, 2935 · mdpi.com/2304-8158/12/15/2935` |
| c | a house imprint instead of a source | `Source: figure reproduced in the source document (unattributed) · Anthology Desk Research` |
| d | a DOI as an extra segment | `… · doi:10.3390/antiox12091675 · Retrieved 2026-09-11` |
| e | a disclaimer-led notes block with no `Source:` prefix | `ESTIMATED - sell-side forecasts, not independently verified.` |
| f | a multi-paragraph analytical NOTES block | later paragraphs caveating the document's own inconsistencies |
| g | a per-symbol list followed by a source | — |

Plus the **redraw / translation / digitisation** family: `translated and redrawn` ·
`translated from the Chinese datasheet` · **`redrawn in English from the source schematic
<asset> (the same figure as <twin> in the original report)`** · `efficiency values read from the
source figure (no citation given in the original)` · `<org>, via Report 4 Cosmetic Ingredients
Table 7` · an external report title.

**Rule:** the verb tells the reader whether the figure is a **quotation** or a **rebuild**.
`translated and redrawn`, `regenerated in English`, `read from the source figure` and `as
tabulated in this report` are all rebuilds and must say so.

**Name the publisher verbatim** for third parties — `BITOLA CAPITAL`, `MetricsCart`, `Chenrui
Capital`, `The Insight Partners`, `Wang et al.` — for reports and data vendors as well as
filings. A per-panel source may be numbered, and multiple sources separated by semicolons. A
re-cited figure may carry a `second-hand` qualifier. **Malformed, do not copy:** a source line
whose document name is truncated (`Report 4 Cosmetic Ingredients` → `Report`).

**Completeness.** Every house figure carries a source line. The PLATFORM family
is a recorded defect to be fixed on reissue — not a precedent (`COR-27`).

**The retrieval date.** ISO format. **A reproduction re-drawing an existing figure must reuse that figure's original
retrieval date, not today's** — the date records when the source was read, not when the figure
was drawn.

### C10.6 Captions live outside the raster

**The corpus never carries `Figure N —` in the image.** That caption is a DOCX paragraph under
the image.

1. **In a DOCX, do not draw the caption into the figure.** The document prints it.
2. Where an in-image caption is genuinely needed it is **serif italic, a full sentence, and
 unnumbered** (`Ginkgo Bioworks LDaaS workflow.`).
3. If a number must appear in-image, use the corpus's **en dash** (numbered with an en dash), not v1's em
 dash, and accept that it doubles with the document's caption.
4. `Canvas.caption()` and `Canvas.source()` exist, but their own docstrings say they are rarely
 needed: the host document already prints its own `Figure N — …` paragraph under every image,
 so drawing one here duplicates it on the page.

---

## C11. Charts

### C11.1 Axis side follows orientation

| Orientation | Scale axis | Ticks | Numbers | Unit label |
|---|---|---|---|---|
| **horizontal bars, intervals, Gantt** | **TOP** | up / outward | above the line | at the right end of the axis line |
| **vertical bars, dot plots** | **BOTTOM** | outward | below the line | centred under the axis, uppercase and letterspaced in the older form |

The top axis **substitutes for a frame**. A conventional left/bottom pair on a horizontal-bar
figure loses the family resemblance.

### C11.2 Spines

| Variant |
|---|
| **left + bottom** hairline, top and right removed |
| **bottom only** — no left spine |
| **none at all** |
| left spine with ticks but no numbers; bottom spine with no ticks |

 `chart_kit.new_chart()` hides **top, right and left**, keeps only the bottom spine at
`INK`, `linewidth 0.7`, and disables the grid. `Canvas.linear_axis()` draws one horizontal rule
at `width 0.7`. **No figure in this corpus draws a frame.** Category names **float** as
right-aligned left-hand labels; y tick numbers, when present, float with no rule under them.

The bottom spine doubles as the zero rule. Where two panels meet at zero, the zero line is
**heavier than a gridline**.

### C11.3 Unit labels — the legal positions

| Position | Form |
|---|---|
| (a) inside the tick label | `50%`, `13,000` |
| (b) a small mono axis caption under or beside the axis | `million head`, `USD millions` |
| (c) inside the data label | `3 g/L`, `USD 3.9 bn` |
| (d) centred under the axis, sentence case, unit in parentheses | `Method disclosure completeness (%)` |
| (e) centred below the tick-label row | `Nominal production capacity, tonnes per year` |
| (f) rotated 90° outside the y tick numbers | `USD billion` |
| (g) a band with a middle dot and a full stop — the axis-less form | `global production capacity, 2023 · 10,000 tons` |
| (h) y unit above the top of the axis, outside the data area | `copper grade (%)` |

**Rule, resolving a genuine self-conflict in the corpus:** horizontal orientation takes
(d)/(e)/(g); vertical orientation takes (f) or (h). Pick by orientation and stay consistent
within a document. **Never a bare "Value"** — every axis title states unit and period
(`USD m, FY2023–FY2030`).

### C11.4 When an axis may go unlabelled

An axis may omit its numbers **when and only when every mark on that axis carries its own
printed value**. It may omit its line and ticks when the category label and the value label
carry everything. **It may never omit both the numbers and the value labels.**

### C11.5 Tick marks

| Form | When |
|---|---|
| short, outward, hairline, bottom axis only | a chart where a reader must locate a position on the axis |
| **no tick marks at all** | a chart whose marks carry printed values  |
| minor ticks between log decades | log axes |
| no tick on the category axis of a bar chart | bar charts |

 when ticks are drawn: `chart_kit` uses `length=3, width=0.6`; `linear_axis` uses
`tick_len=5, width=0.7` major and `0.45` at `0.55 × len` minor. **Both are canonical for their
side.** Direction is **outward**, never inward.

**Decision rule:** marks carry printed values → no ticks. A reader must locate a position →
outward hairline ticks. In doubt, follow the nearest precedent figure.

### C11.6 Gridlines

> **v1 stated this rule wrongly (`COR-1`).** It permitted faint **horizontal** `RULE_SOFT`
> lines only, and only where a reader genuinely needed to read a value. The corpus does neither.

1. **A gridline runs perpendicular to the value axis.** A horizontal-bar chart (value axis on
 top) gets **vertical** gridlines dropping from the x ticks. A vertical-bar or line chart gets
 **horizontal** gridlines at the y ticks.
2. **Colour is `RULE_SOFT #D8D3C4`**, or a knockout in the canvas colour.
3. **Weight is 0.5–0.6** — lighter than any structural rule.
4. **The trigger is the form, not a judgement about the reader:** end-labelled bar charts get
 **no grid**; time-series and positioned-value charts get gridlines at **every** tick.

**Knocked-out gridlines** — faint white rules rather than `RULE_SOFT` — are **UNVERIFIED**: the
160×160 sample is blind to 1 px rules and only one vision read reported it. If implementing,
knock the rule out of a filled element rather than drawing white on paper.

### C11.7 Value labels

> The value is printed **above or beside the mark, never on the axis**, and the **placement is
> per-row, not fixed** — it dodges the glyph it belongs to.

Mono, `INK` (or the body text colour), no leader, no padding box, no arrowhead.

| Form |
|---|
| horizontal bar |
| vertical bar |
| stacked bar |
| negative bar |
| in-bar annotation |
| per-bar annotation stack |
| multi-line category label |
| rotated data label |
| floating annotation with no bar behind it |
| two values per bar |
| two quantities in one label |
| the `total` prefix |
| trend labels |
| multi-line label blocks |

 in `chart_kit.bars()` the vertical-bar equivalent is `ha="center", va="bottom"` at the
bar's top centre. **Jitter within a categorical lane** to stop points overlapping, and
**repeat same-period events horizontally rather than stacking them**.

### C11.8 Legends and keys

> **v1 made the legend a collision fallback (`COR-19`). It is a first-class element.**

Forms: a boxless key at the top-right of the plot area · a key block bottom-left · a **swatch
row directly under the title** (small squares, no box, no border, no fill) · a framed box
top-left · a titled semi-transparent-framed legend · a right-hand legend · a top-left legend of
small colour squares with sans labels · a **boxed** legend with a border, used only where three
series collide. **Legends sit top-right or right, never below.**

 `legend()`: swatch = a filled rect **11 wide × 7.7 high** (`swatch × 0.7`), label at
`swatch + 7`, `row_gap = 18`, label 10.5 mono `INK_MUTED`, no frame.

**Where a legend is not the answer:**

* **The header as legend** — the series name is set once at the left of its row or above its
 lane, so no legend object exists at all. Preferred for lane charts.
* **Right-end series labels** in the series' own colour, replacing the legend.
 `chart_kit.lines()` reserves **30 % x-headroom** for these and enforces a minimum gap of
 **7.5 %** of the value span between adjacent end labels. **Reproduce that headroom** — it is
 why end-labelled line charts have empty space on the right.
* **The key as a sentence under the title**, with the hue named in words and no swatch:
 `bronze = Spiber`, `solid = built, hatched sky = stated target`.
* **The state-key line** — a one-line key instead of a legend: `outline = before LF treatment;
 filled = after LF treatment`.
* **An inline axis-embedded series label** — `pigs served (right axis)` printed inside the plot.
* **A key block as a first-class form**, ruled and titled at the foot: `KEY`, `LEGEND`,
 `NOTES`, `HOW TO READ THE FILL`, `SOLID BOX = PROCESS STEP / DASHED BOX = DECISION GATE`.
* **Legends that explain a MARK, not a colour** — `Dated valuation milestone`, `range /
 median`, `initial consideration / deferred / contingent`.
* **A shape key** for molecules: `square = GlcNAc`, `circle = Man`, `triangle = Gal`, with the
 line `identity is the shape`.

One unusual idiom is load-bearing: a legend may **continue below the plot, separated by a
horizontal rule, with rows for items that have no bar at all** — the figure's way of saying what
it cannot plot. The symbol is carried into the list.

### C11.9 Numerals

Mono for every numeral except facsimiles. Right-aligned in table cells, left-aligned in charts.

| Feature | Rule | Examples |
|---|---|---|
| thousands separators, always | — | `16,283.0`, `8,950`, `40,000` |
| one decimal for model-derived shares and currency | — | `44.4%`, `38.1%`, `6,879.0` |
| integers for published shares | — | `80%`, `33%` |
| trailing `.0` on tonnage | — | `12,230.0 kt` |
| currency: prefix + unit + scale | — | `USD 761.00/kg`, `USD 214.0m`, `18.8bn €`, `~USD 500/kg` |
| lowercase magnitude suffixes in prose labels, spelled out in the axis title — **not harmonised** | — | `$17.80bn` in the label vs `USD billion` in the axis |
| thresholds | `≥` `≤` `<` | `≥90%`, `≤78 °C`, `Cu < 0.5 wt%` |
| approximation | `~` | `~96% Au recovery`, `~200 days` |
| ranges | hyphen | `40-45 °C`, `pH 1.2-1.8`, `30-50 kDa` |
| en dash for currency ranges | — | `USD 16.5-17.6 bn` |
| explicit `+` / `-` on waterfall steps | — | `+55`, `+$0.18` |
| no space before `%`; **a space before other units** | — | `65.5%` vs `50 µm`, `0.7 MPa` |

> **The published-versus-model split is the corpus's only reliable provenance signal in the
> numerals themselves: integers for published shares, one decimal for model-derived ones.**

Deltas and multipliers: a signed delta above a bar (`+55`) · a percentage change with a
direction word (`–98 % from the October 2021 peak`) · a percentage change alone (`–99.6 %`) · a
multiplier (`50x`) · a ratio annotation as a multiplier (`×1.85`, and the words `single value`
where only one source exists).

**Calculation blocks:** a mono arithmetic block beneath a chart, row-labelled (`gain`, `feed`),
using `+ - × =`, aligned in columns, sitting under each panel.

**Restatement marking:** an `R` suffix on the tick (`2021 R`), a `*R*` explanation in the source
line, or a hatch over the restated part of a bar plus a callout naming it.

 `_num()` and `_tick_label()` render `%gM` at ≥ 1e6, `%gk` at ≥ 1000, `%g` below — so
`1000000` prints as `1M`, not `1,000,000`.

> **≥, ≤ and subscripts are not in the brand subsets.** A chart needing them must pass
> `brand.font_stack("mono")` as a **list**, not a single family — see C8.1.

### C11.10 Axis forms

 `linear_axis(x0, x1, y, ticks, label, tick_len=5, minor=0)`: one rule at `width 0.7`;
major ticks `5` long at `0.7`; minor `0.55 × tick_len` at `0.5`; tick labels at
`y + tick_len + 11`, size 10.5 mono `INK_MUTED`, centred; unit label at `y + tick_len + 26`.

 `log_axis(x0, x1, y, lo, hi, ticks, minor=True, label="")`: axis `0.7`; minor ticks `3`
long at `0.45`; major `5` at `0.7`; labels at `y + 16`; unit at `y + 31`.

Log axes are for price ladders and any range spanning orders of magnitude. **Name the scale in
the axis title** (`Price (USD / kg, log scale)`). Major labels take K/M suffixes rather than
full digits (`100K / 1M / 10M / 100M`), except where the source printed digits (`10 / 100 /
1,000 / 10,000 / 100,000`). A **thin space before the unit** in the older form. Log-log occurs
in one panel only.

**The dashed `$0` cap.** A bar starting at **$0 on a log axis** gets a dashed left cap instead
of a solid end, because $0 has no position on a log scale. Where log-ness is signalled only in
the unit label (`LOG SCALE`) there are no decade ticks or break marks.

**Threshold, median and reference rules** are dashed verticals at the value · two vertical rules
in `JPM_SKY` with small mono labels at the top used to colour-group the bars · a solid
burnt-orange rule plus orange text for a physiological value · dashed black horizontal
thresholds · a dashed horizontal at the control bar's height · a horizontal at the baseline in a
bridge · a dotted vertical marking a policy date · dashed verticals as lane boundaries. Colour:
`RULE_SOFT` for a background threshold, the accent for a semantic one, `JPM_SKY` for
colour-group thresholds.

**Break axis.** The corpus does not silently truncate. **When a category dwarfs the rest, the
figure is split into two panels with a shared header rather than a broken axis.** Where a break
is drawn, draw it explicitly.

**The unit band.** When a second measure is printed but not plotted it becomes a **header line
above the category column** (`mass in kilotons` over the labels while the axis is billion EUR).
That is the sanctioned workaround for the dual-axis constraint.

---

## C12. Chart forms

Use this form list.

| Form | Construction |
|---|---|
| **Waterfall / bridge** (3) | Totals grounded at zero, intermediate steps floating; **colour keyed to category, not to sign**; a hatched bar for a subtraction; explicit `+`/`-` on every step. Construction is inconsistent across the corpus — solid connectors, dashed connectors and no connectors all ship. `chart_kit.waterfall()` is the variant new work should use: bars `width 0.6`, `edgecolor` `JPM_INK` (finance) or `INK`, fill `JPM_BRONZE` for a positive delta and **`ROSE` for a negative**, signed label above, connector a `0.5`-wide `INK_MUTED` line across `±0.42` of the bar width |
| **Range / dumbbell / median rows** (3+) | **A:** a horizontal line with vertical T-caps at both ends plus a solid dot for the median exactly on the line; legend line+dot = "range", dot = "median", boxless, top-right. **B:** a hairline connector between two endpoints, filled dot = subject and hollow ring = comparator, values at both ends. **C:** range-and-median rows with opening, closing and median all printed |
| **Bars** | Flat fill, **no outline**, square corners, **sorted descending**. `chart_kit.bars()` sets `width=0.62`, `edgecolor=INK`, `linewidth=0.6` — the code draws an outline the delivered bars do not show at raster scale; **reproduce the corpus: no visible outline.** An unsorted bar chart is a recorded defect, not a convention |
| **The one-bar highlight** | Exactly **one** bar or dot takes a second hue — the subject — with the rest of the field in the primary ink. `JPM_BRONZE` for the top supplier, latest round, top family, top decile, latest half-year, peak year; brown for the subject or largest tier; a `MEADOW` bar against `SEED_BROWN` context elsewhere. **"Brown = the one that matters" is a real convention** and v1 never stated it |
| **Direct-labelled scatter** (6) | Label text in the same hue as its marker; vertical range whiskers for a price range |
| **Unit / waffle** | One small square per observation; an empty grey-outlined square = not screened; the integer count printed to the right of each row; total at the top |
| **Discrete block-array rating** | Three stacked rectangles filled = "high", two filled + one hollow = "medium" — used instead of stars, dots or a score, and the **words, not the count, name the level** |
| **Hybrid chart + aligned table** | A scatter on the left whose rows visually align with a table on the right, **with no drawn rules between them** |
| **Combo / dual axis** (2) | **v1 forbade dual axes; two ship (`COR-15`).** Permitted — but the right-hand series **must be named inline** or in a sentence key, because there is no legend room |
| **Axis-less bar geometry** | No spines, no ticks, no gridlines; **bar thickness to gap ≈ 1.5: 1**; mono value label immediately right of the bar end |
| **Bubble / halo mark** | A light disc whose **area** is proportional to the value with a small solid `JPM_INK` dot at its centre; halo in the light tint; value label right of the dot; no connecting line; category names at the left; no left spine |
| **Rank list plus staircase** | Mono ordinal + name right-aligned against a stepped diagonal; dots joined by thin grey orthogonal segments ascending bottom-left to top-right; top decile in `JPM_BRONZE`; no axes, no ticks. **Reproduce the positions** — the metric cannot be recomputed |
| **Grouped bars** (9) | Bars **inside a group touch (zero gap)**; groups separated by about a bar width; a top-left legend of small colour squares with sans labels. A three-entry legend with no label collision is legitimate (`COR-19`) |
| **Negative values** | A distinct `JPM_INK` rule at 0 %, visually **heavier than a gridline**; negatives hanging below it; labels on the far side; a shared zero rule drawn where two panels meet |
| **Area and line mechanics** | Endpoint markers (filled circles) **only at the first and last point**; y unit rotated 90°; x axis bare years with no "year" unit; CAGR as floating mono text with no leader and no box; endpoint values below the first marker and above the last; area fill at ≈13 % alpha; gridlines at every y tick. `chart_kit.lines()` uses `linewidth 1.4` — the only 1.4 stroke in the system |
| **Event plot** | Markers on a date axis, staggered vertically to stop label collision; no y-axis, no y label, no ticks, no grid |
| **Formula strip** | Boxes joined by `×` and `=` operator glyphs, each term carrying a status micro-label beneath it — a business-model identity written as a diagram |
| **Range map on a numeric axis** | Two stacked panels lettered `A`/`B`, each a horizontal numeric axis carrying range bars whose end values are printed as range text, with a right-hand description column |
| **Category lanes in a scatter** | Labelled horizontal lanes with dashed boundary rules, a count annotation per lane, an explicit `not on this axis` note for excluded cases, and dashed reference rules with annotations |
| **Faceted small multiples** | Rows × criteria, the score printed above every bar, **not a shared grouped axis**; row headers act as the legend |
| **Box plot** | Whiskers at 0.5, box hairline, no fill. Rare in the corpus |

---

## C13. Panels

**Panels are divided by whitespace only — no rule, no gap line, no border.** Do not draw a
divider.

Both layouts are used with no stated preference: **side by side**, and **stacked (A above B)**;
side-by-side with independent y-scales; and side-by-side with different orientations (grouped
vertical bars left, grouped horizontal bars right).

**The summary line between panels** carries the arithmetic that links them and sits on the
whitespace gutter.

**A panel need not be labelled.** A three-band composition (intro / grid / routes) is panels
without labels, and two logical rows connected by a direction marker are panels too.

**Panel striping is by whitespace only**, with phase labels attached to bar groups rather than
to an axis.

**Panel labels:**

| Form | Face |
|---|---|
| `PANEL A · <subject> · <section ref>` — uppercase mono, doubling as the panel's kicker | mono |
| `A. Average daily gain` — **part of the panel title**, serif mixed case | serif |
| in-figure identifiers `A`, `B`, `C`, `D` | sans |
| lowercase `(a)` in a small **paper-filled hairline box** at the top-left of a plate | serif |

Pick by context: a labelled panel in a two-panel comparison uses `A.`/`B.` as part of its title;
a composite plate uses `(a)`, `(b)` in a boxed corner label.

**Furniture across panels.**

| Case | Rule |
|---|---|
| shared header, shared source line | always |
| panels measure **different things** | **per-panel titles** |
| panels are two halves of one measure | **shared title** |
| the x-axis title | appears **once**, under the lower panel |
| notes | per-panel is permitted (`Panel A: … Panel B: …`) |

> **v1 required one shared source line (`COR-18`).** The corpus shares the source line but uses
> per-panel titles wherever the panels measure different quantities.

**Row alignment:** categories listed in the **same order** in both panels so the eye reads
across. Small multiples may carry small mono panel headers over each sub-panel.

**Density ceiling.** The corpus's densest figure packs three stacked horizontal panels, a four-row
key and a two-column source footer onto one canvas; another is a six-panel lettered composite
of roughly 45 % chart / 20 % diagram / 35 % table by area. These define the ceiling; v1's "do not
crowd" is an aspiration, not a rule (`COR-29`).

---

## C14. Uncertainty and ranges

Light shaded bands mean **a range, not a series** — a vertical beige band for a working window
or a dead period, a pale pink horizontal band for a duration or a gap.

**Overlay order.** A band meant as a background zone is drawn before the marks. A band meant as
an uncertainty zone that occludes — dashed edge, label above, drawn over the data — is drawn
after, and it visibly occludes points.

> **There is no uncertainty element in the corpus.** No error bars, no confidence bands, no
> shaded envelope, no `n=`, no whiskers (except the single box plot inside the six-panel
> composite), no dashed projection. **Every range is prose in a micro-label**: `40-45 °C`,
> `pH 1.2-1.8`, `~200 days`, `up to 96% yield`, `below USD 3.00/kg`, `30-50 kDa MWCO`.

**Rules.**

* **Do not add error bars, confidence bands, shaded envelopes, `n=` or whiskers.** Inventing
 them is off-style.
* **Do not drop the ± caveat.** Ranges live as prose micro-labels — mono, in the axis label,
 the category label, a condition box or the caveat block.
* A figure may carry **no numeric scale at all** if it declares itself schematic.

**Exclusion bands:** a tinted vertical band marking a range to avoid, with a text tag.

---

## C15. Diagrams

### C15.1 The box

**A thick accent-coloured bar flush on the LEFT INSIDE edge of a box, over a thin black hairline
border.** This is the most repeated diagram device in the corpus, and v1 had no words for it.

| Property | Value |
|---|---|
| bar width | **3 canvas units** |
| at 2400 px | 3 × (2400 ÷ 780) = **9.2 px** |
| measured on the raster | **8–10 px at a 2400 px canvas** |

> **The code constant and the raster estimate agree.** A reading taken off a finished image is
> reliable for *which device*, never for *what value*; here the code settles it.

**The bar is a stroke on one edge, not a fill.** Filling the whole box in the accent produces a
different device.

**The accent edge is on EVERY node.** v1 said one accent marks the step that matters; the corpus
applies the edge uniformly and carries emphasis by fill and label instead (`COR-22`). A figure
that accents only one box is off-family.

**Placement by orientation:** a vertical stack of boxes takes **left**; the header of a
horizontal three-stage mechanism takes **top**; container boxes take a **top band across the
whole width**; unit operations in a two-column flow take **top**; "compatible application" in a
matrix takes **left**. `accent_edge="top"` emits `<rect width="{w}" height="3">` at
the box top — the same 3-unit thickness, rotated.

**Three box classes, not interchangeable:**

| Class | Border | Fill | Edge bar |
|---|---|---|---|
| **standard** | hairline `INK` 0.8 | none / canvas | accent left or top |
| **flat block** | **none** | flat accent or neutral | none |
| **container** | hairline `INK`, dashed when optional | tinted band or none | accent top band |

v1 said boxes have thin black borders; some have **no borders at all** (`COR-7`).

**Node geometry:** rectangles for process steps, data, containers and unit operations; a
hairline circle with text inside for assembled modules joined by straight arrows. **No
start/end terminators** in the in-house figures.

**Computed and optional steps:**

| State | Border |
|---|---|
| process step | **solid** |
| decision gate · derived/computed step · optional · planned · unavailable parent · discarded or side stream | **dashed** |

A discarded or side-stream box carries **no edge bar**. Dash pattern `3 3`.

**Ink and knockout.** Navy carries body text inside boxes, all box outlines and axis lines in
the register — unrecorded exceptions to v1's "all text, all rules" in `INK`. **Slate fills carry
white knockout text.** A box may take its own border and text hue as a category code with no
legend explaining it; record it and do not "fix" it by adding a legend.

**Two-line box labels:** a small uppercase **role** line above or below a larger **name**. Use
the primitive — `label` (13 sans `INK`) plus `sub` (10.5 mono `MUTED`) at `+19` vertical
offset — and put the role in `sub` and the name in `label`.

### C15.2 Arrows

> **v1: "thin, with a small solid head." Two head forms coexist (`COR-2`).**

| Head form | Used on |
|---|---|
| **open-V chevron** | accent-coloured flow arrows and timeline leaders |
| **solid filled triangle** | arrows whose shaft is `INK`, and non-house figures |
| **no head at all** — dot-terminated | relationship connectors |

**Rule: choose the head from the shaft's colour.** Shaft in the accent hue → open-V chevron.
Shaft in `INK` → solid filled triangle. A relationship rather than a flow → dot-terminated, no
head.

**Colour: arrows take the accent, not black.** Shaft and head are the figure's accent. A
timeline's leaders may be `ROSE` open-V, and straight vertical connectors may be `ROSE` with a
small solid head.

 `Canvas.arrow()` builds the open-V head from two lines:

```
head length       9 units from the tip, along the shaft
head half-width   4.5 units perpendicular
total head width  9 units
head stroke       same width as the shaft (default shaft width = 1.0)
```

At 2400 px over 780 units that is a head **27.7 px long and 27.7 px wide** — small relative to a
box, which is what "small head" means. **Size relative to text: 9 canvas units, i.e. 0.82 × the
11-unit micro-label.** Curved arrows take their head direction from the **control point**, not
the endpoint.

**Dot-terminated connectors** are a thin line ending in a small solid dot, used for a
relationship rather than a flow. `Canvas.dot(cx, cy, r=5)` for a filled dot,
`r=5, filled=False` for a ring. The dot sits **on the object** and is a geometric anchor at a
defined point, not decoration — treat it as an anchor and place it on a named feature.

### C15.3 Connectors

**Routing:** elbow/right-angle and diagonal connectors mixed in one figure; a down-arrow from
the end of row 1 to the start of row 2 in two-row flows; straight and vertical only in one
figure; orthogonal vertical-then-horizontal segments ascending in another; L-shaped geometry
with in-flow lane labels elsewhere.

 `Canvas.chain(nodes)` places the arrow **6 units clear** of each node — horizontally
from `a.right + 6 → b.left − 6` at the vertical mid, or vertically from `a.bottom + 6 →
b.top − 6` at the horizontal centre. **That 6-unit clearance is the family's arrow gap.**

**Solid versus dashed:** solid = material or product flow; dashed = a chemical modification, an
incomplete or conditional path, or a discard/side-stream (with an open-V head). Arrow dash
pattern `4 3`.

**Flow versus relation.** A **flow** gets a head. A **relation** gets a dot. Do not put a head on
a relation.

**Spines and zone separators:** an orthogonal collection spine gathering several outputs into
one edge; dashed vertical rules separating module zones; a vertical spine with short horizontal
ticks (a tree indent); a numbered badge spine.

**Connector edge labels** sit on the line in small caps — `ACCEPTED`, `APPROVED`, `GRAS
CONFIRMED`, `INCOMPLETE`, `NEGATIVE OPINION`, `POSITIVE OPINION` — mono or small-caps sans,
`INK`, knocked out of the line if the line passes through.

### C15.4 Process and flow

**Direction:** horizontal, left to right; vertical when the process is a column.

**Boustrophedon (snaking) two-row flow** reverses direction on the second row and requires
both (1) a **horizontal rule separating the two rows** and (2) an explicit reader-instruction
marker inside the figure:

```
CONTINUED — ROW READS RIGHT TO LEFT
```

**Gates:** a decision gate is a dashed-border box and a process step a solid-border box,
declared by the key line `SOLID BOX = PROCESS STEP / DASHED BOX = DECISION GATE`. (v1's "gates
on a line" is the *timeline* gate — a different device.)

**Side-stream column:** a separate labelled column (`SIDE STREAMS`) of dashed boxes hanging off
the main vertical run, connected by dashed horizontal arrows with open-V heads, labels ending
`— discarded`.

**Containers and group outlines:** a dashed box enclosing two steps labelled `OPTIONAL`; a left
bracket spanning stacked rows; a bordered beige summary block at the foot; an accent-edged
container block for an assessment or condition list; a large faint rectangle enclosing a phase
with a phase header above it.

**Numbered step badges:** a solid accent **square** containing a white numeral, on a vertical
spine with short horizontal ticks, plus a single long arrow linking the last step of one column
to the head of the next. Other step tokens in the corpus: plain numerals beside each step;
circled numerals (foreign); a lettered particle token — circles containing `M` for a metal ion,
moss-filled when bound — used as an in-drawing legend.

**Logic nodes:** circles containing `×` for multiplication steps; rectangles for data and
process steps; no start/end terminators.

**Column scaffolds.** `COLUMN 1` / `COLUMN 2` uppercase micro-labels above a single vertical
stack, no dividing rule, separated only by a whitespace gutter. Whether this is an idiom or
leftover scaffolding is **UNRESOLVED** — treat it as an idiom and do not emit new ones.

Related: a two-column Gantt-style scaffold with task names hard-left, owners hard-right, bars on
a wide central canvas, phases grouped by whitespace plus a coloured sub-header.

**Period bands:** a horizontal band per period with the label **inside** it, split into an
upstream and a downstream leg.

**Off-flow inputs:** a co-substrate box outside the main line joined into the chain with a `+`.

### C15.5 Timelines

**Horizontal timeline — the canonical geometry.** One horizontal `INK` rule **is** the axis: no
spines, no ticks, no gridlines. A small filled `ROSE` dot on the rule marks each event. Label
blocks alternate above and below; inside a block the **mono year sits on the line nearest the
rule** and the **serif description stacks further out**. A short `ROSE` arrow runs from the block
to the dot, pointing **down** for above-labels and **up** for below-labels.

 `Canvas.timeline(x, y, w, events, label_above=True, dot_r=5)` is the primitive:

```
rule            INK, width 0.8
dot             r = 5, filled accent
above:  year    y − 17, size 12, mono, INK, centred
        label   y − 42, size 13, sans, INK, centred
        sub     y − 60, size 11, serif ITALIC, MUTED, centred
below:  year    y + 25, size 12, mono, INK, centred
        label   y + 45, size 13, sans, INK, centred
spacing         events laid out EVENLY: ex = x + w × i / (n − 1)
```

**Vertical timeline:** a vertical rule with dots on it and all labels hanging to **one** side
(dates in mono to the left, event text to the right); or a vertical timeline with a **central
spine**, events alternating left and right, year labels in coloured mono, thumbnails attached.

**Other timeline devices:** a pale peach duration band across the timeline · **solid dot = a
past event, hollow dot = the present or latest event** · a rule-with-gate — one continuous
horizontal rule with short outward ticks, phase markers as outlined boxes with a pale clay tint
**below** the rule, and the decision gate a small solid clay diamond **on** the rule with its
caption above · a full-width shaded `GO / NO-GO` band interrupting the phase sequence · a
two-column Gantt with dashed month gridlines and the scale axis on top · mono duration
micro-labels next to a gate (`90-180 DAYS`, `12-24 MONTHS`, `3-5 YEARS`) · a left-edged
assessment box at the foot carrying a verdict in italic · a milestone marker — a diamond with a
vertical drop line to its label, in `JPM_BRONZE`, with a legend entry naming the marker class.

> **Timeline positions are decorative, not proportional.** Events are spaced evenly regardless
> of date — `timeline()` spaces them `w × i / (n − 1)`. **Do not scale timeline
> positions to their dates unless the figure is explicitly a time-series chart.**

**Year-label colour:** pure cyan `#0CF0CC` (and `#24F0D8`, `#18F0D8`) marks generation-1
vertical timeline year labels. Do not confuse it with the foreign teal `#48CCC0` of another
company's corporate identity.

### C15.6 The annotation kit

| Device | Construction |
|---|---|
| **Brackets** | a thin square bracket spanning several rows with the group name set **vertically in the margin**; a thin bracket with **end ticks** over two or more elements plus a label; a bracket spanning three columns inside a table. **Rotated marginal labels are the device** |
| **Typographic brackets** | `[ ]` used as a grouping device inside a table, spanning three columns |
| **Measured callouts** | a callout with a measured bracket pointing at a specific x value (`0.33 — CICC 2103 starts at 3.00`) |
| **Folded-corner callout** | a callout box with a **folded (cut) top-right corner**, filled one step darker than the nodes, attached by a small triangular pointer, contents as label–value lines. **The folded corner needs an explicit ruling: rounded corners are forbidden (C6.2), and a folded corner is an adjacent device — permitted only on a callout, never on a node** |
| **Leader lines** | a thin accent straight or diagonal line from a small **solid square marker** to a floating label in the empty whitespace; or a hairline (~0.5 px) straight segment from the label to the exact data point with **no terminal dot and no arrowhead**; or a thin line from a text callout in empty plot space. **The most common annotation form.** The anchored and bare forms are not interchangeable — match the original |
| **Directional data arrows** | a thin accent arrow with an open-V head from a solid dot to a hollow circle, meaning "projected after change", labelled `ESTIMATED` |
| **Genealogy / bipartite** | two headed columns, thin dot-terminated connectors, dashed border = not publicly deposited, `MEADOW` = publicly purchasable parents, `CLAY` = engineered hosts plus dashed unavailable parents |
| **Fishbone / Ishikawa** | a central horizontal spine with branches alternating above and below to leaf boxes, **no arrowheads**, the root node distinguished by an accent left band |
| **Radial activity wheel** | concentric hairline circles, six radial spokes dividing the ring into sectors, accent dots exactly on the perimeter intersections, and a hub carrying a two-line label (sans line + serif italic sub-line). `Canvas.ring(cx, cy, radii, dots, dot_len)` emits one `<circle>` per `(r, opacity)` pair at `stroke-width 0.8`, then radial ticks of length `dot_len` from `radii[0]` outward, at `i × 360/dots − 90` degrees |
| **Subset annotation** | annotate three points of a long series — **first, peak, last** — in the same hue as the series |

> **v1's "building blocks worth reusing" list** — radiating concentric-hairline fans, spiral/root
> forms, ellipse clusters, circle-with-crosshair constructions — **does not appear once** in one
> batch of 47 figures. The vocabulary actually used — column, bead, vessel, molecule glyph,
> hatch band, dispersion-halo triangle — is the one to document. Keep the crosshair circle only
> because `crossed_circle()` implements it.

### C15.7 Molecules, chemistry, cross-sections, scale-free figures

**Abstract geometric residue tokens:** a square, a triangle and a pentagon standing for amino
acids chained along the assembly line; and `square = GlcNAc`, `circle = Man`, `triangle = Gal`
with the line `identity is the shape`. The combined vocabulary in use is **circles, squares,
triangles, plus signs**.

**Highlighting positions on a structure:** colour **the locant digit, the β symbol and the bond
angles** in the accent, leaving every bond black and every ring unshaded. v1 said only "hairline,
no shading"; this is the positive rule.

**Repeating units:** square brackets with a subscript *n*.

**Four-across comparison of physical principles:** each panel a small hairline sketch with
molecule glyphs in one flat hue and a sans caption below.

**Primitives inside a flow box:** a small grid/bead icon beside chromatography steps is
**UNRESOLVED** (a single read at the resolution limit) — if it is a text glyph, drop it. A 2-D
skeletal structure with hairline black bonds, wedge stereochemistry and serif names below is the
correct chemical-drawing form; a 3-D cylinder is a defect, not a convention.

**Boxed reaction-condition micro-labels:** conditions set inside thin-outlined rectangles beside
the arrow (`6000 U · 50 mM · 24.0 gBWW · >99% conversion`). A by-product is written above the
arrow; conditions may sit inside the step box. v1 required the condition as a mono micro-label;
**the box is the missing part.**

**Arrow-borne reaction and enzyme labels:** the reaction or enzyme is named on the arrow, mono or
small sans, on the canvas fill, centred on the shaft.

**Cross-section layer stack:** three stacked hairline boxes, each labelled with an uppercase mono
header plus an italic serif sub-line, mapped to right-hand text blocks by dot-anchored radial
leaders, with a boxed caveat at the bottom. Geological sections add hatch bands, a triangle for
a geochemical dispersion halo, dotted and cross-hatched zones, mineral formulas on leader lines,
and arrows for rainfall and rising groundwater.

**Positioning / continuum map:** two axes labelled at both ends, zone header bars over the
field, nodes placed along a curved dashed path, an explanatory line under each node.

**Scale-free figures.** A curve figure may carry **no numeric scale at all**, and then it must
say so. The stage-band idiom: four thin vertical rules spanning the plot height with sans stage
names at the top; one pale rectangle shading a span; item labels scattered above and below a
smooth sigmoid with **no leader lines**; label colour switching from `JPM_INK` to `JPM_BRONZE` at
the maturity boundary; no numeric scale on either axis. **Reproducing it means reproducing the
POSITIONS, not recomputing them** — the same rule applies to a rank list whose ordinals are
printed without counts, and to decorative timeline positions.

---

## C16. Tables and matrix marks

### C16.1 Rules

**Horizontal hairlines only. No vertical rules.** One rule under the title, one under the
header, one per row. The exemption class is C16.6.

 `table()`: total width = `sum(col_w)`; the rule under the header at `width 0.9`; row
rules at `width 0.45`; cell text inset **6 units** from the column start.

### C16.2 Header treatments

`BONE` fill band with a hairline rule above and below · `BONE` band plus a thick `CLAY` rule
immediately under it · band-less: uppercase letterspaced grey text with a single hairline beneath
· accent-coloured header text only · uppercase sans column headers with a light `BONE` band ·
a full-width black rule under the header with no fill · a filled tinted header band.

 `table(header_fill=…)` fills the band and sets header text at `size × 0.82` in mono
`INK_MUTED`, uppercase. **Within one document, use the first or the third treatment**; the
second marks a table whose header carries a rule the document wants read as a section boundary;
the full-rule and tinted-band treatments belong to imported or older tables.

### C16.3 Rows, alignment, units, faces

* **Row dividers are hairlines at `RULE_SOFT`-or-lighter weight** (≤1 px at a 2400 px canvas),
 one per row.
* **No zebra shading anywhere** in the house tables.
* **Row height:** `table()` defaults `row_h = 23`, `header_h = 27`, cell text at
 `size 13` — row height ÷ text size = **1.77**, inside the measured impression of 1.6–2.0× the
 text line box. **Use 23 units.**
* **Alignment:** the first/label column **left**; the value column left in some tables and
 **right-aligned** in the facsimile statements; a basis column italic; a confidence column
 centred. **Decimal alignment is never used.** `table()` places every cell at
 `col_start + 6` — left-aligned in every column; right-alignment is a facsimile convention.
* **Units live inside the cell** (`50 µm`, `0.7 MPa`), never in the column header.
* **Faces:** cell content mono; row labels lowercase; column headers uppercase. A three-way
 split also exists — column headers, count columns and figures in mono, row labels and cell
 text in serif or sans. Serif numerals appear only in a facsimile statement.

### C16.4 Matrix marks

| Mark | Means |
|---|---|
| hollow ellipse | not stated |
| half-filled ellipse | partial |
| solid ellipse | disclosed |
| solid square whose **fill lightness** encodes the level's position on that column's own ordinal scale | ordinal rank |
| hollow square | a category **not on** that column's scale |
| large tick and cross glyphs | binary attributes |
| a hexagon with internal spokes | a virus-like particle |
| infinity-loop markers | — |
| `mark_dot(r=4.2)` | a score |
| `mark_sq(s=13, half=True)` | a score; fills the **bottom half** |

 `mark_sq()` draws the square as four `0.8`-width lines. **The code's half is a
HORIZONTAL split; the figures use a VERTICAL split.** Match the original.

**Half-state glyphs split VERTICALLY**: left half black + right half `SEED_BROWN` inside one
ellipse = "partially disclosed"; a vertically split half-square in a table = "partly disclosed";
and a half-mark **scores 0.5** in the count column. v1 named "half-squares" without the axis of
the split, the two colours, the 0.5 weighting or the derived count column.

**Icon marks** — a hexagon with internal spokes, an infinity loop, tick and cross glyphs — are
drawn as hairline geometry in `INK` or the accent.

**Conditional-format cells — the exemption.** Some imported tables encode cell **value by hue**
with no key and no scale printed, using `#FCE4E4`, `#FCE4D8`, `#FCA86C`, `#FCCC9C`, `#8484C0`,
`#B4D8B4`. That is an **imported/publisher convention**, permitted only in a table declared as
imported. A **new** house table uses the marks above. If such a table must be reproduced,
**reproduce the palette exactly and declare it in the source line** — do not convert it to
marks, because the conversion invents a scale the source did not publish.

### C16.5 Empty and absent cells

| Cell state | Means |
|---|---|
| **blank** | nothing happened |
| **an empty outlined square** | **no evidence — the gap IS the finding** |
| a dashed cell + `?` | undetermined |
| a solid `CLAY` border | prohibited |
| a plain black border | lawful |
| an empty grey-outlined square | not screened |
| hollow | not stated / not yet met / off-scale |

One figure uses all four border codings at once: solid `CLAY` prohibited, dashed undetermined,
plain black lawful, `?` inside the undetermined ones.

### C16.6 Table extras and the full-grid exemption

* **Count columns** — a right-hand printed COUNT column with the total stated as `of 10` in the
 header row. Half-state weightings of 0.5 appear in it. **Derived totals are printed, not
 implied.**
* **A key embedded as a sentence under the title**, not in a box.
* **A key block under the table** carrying the three chip swatches.
* **Row emphasis** — one row enclosed by an approximately 2 px black rectangle, heavier than any
 rule in the table.
* **A tinted column** — one whole column backed by a peach panel that **bleeds to the figure's
 bottom edge** rather than sitting inset, with small uppercase column headings, a
 `1 VERIFIED CELL` count tag in the header row, and italic notes beneath explaining that the
 cells are quoted. `BONE #EDEADB` is the sanctioned panel; the observed tint is warmer than
 `BONE`.
* **A paragraph marker** — a thick vertical `CLAY` bar to the left of a closing note.

> **Full-grid tables are a declared exemption (`COR-3`).** v1 said "no vertical rules"; the
> corpus has both conventions live. A full-grid table is either an imported table or an older
> house table being reproduced, it must keep the C1 tokens for its rules, and it must be
> **declared**. A **new** house table uses C16.1. Do not adopt the grid for density reasons —
> split the table or widen the canvas instead.

**Table metrics, all:**

| Property | Value |
|---|---|
| row height | **23 units** |
| header height | **27 units** |
| cell text size | **13 units** |
| header text size | **10.66 units** (`13 × 0.82`) |
| cell inset from column start | **6 units** |
| rule under header | width **0.9** |
| row rules | width **0.45** |
| row height ÷ text size | **1.77** |

**Rule:** a matrix gets generous rows (23–30 units); a register copied from a source keeps the
source's tight padding and says so in the source line.

### C16.7 Facsimile statements

A captured financial statement reproduced as a facsimile is its own class: **pure white**
`#FFFFFF` canvas · **serif** type, not mono · **pale sky zebra rows** (`#C0E8F8` / `#D8F0F8`,
about 23 % of the image) · **right-aligned** amounts · **no vertical rules** · a hairline under
the header and above totals · a **double rule** above the final total. A cropped fragment is
reproduced as given, with the source line naming it a fragment.

**Rule: a facsimile is a quotation, not a house table.** Do not convert it to C16's
conventions — that destroys the evidence that it is a quotation. Do add a source line.

---

## C17. Photographs, kept externals, off-family

### C17.1 Transparent cut-outs

Product photographs ship as **RGBA PNGs with 20–85 % of the canvas fully transparent**, placed
**bare on the page tone**: **no white box, no frame, no caption, no source line.** A white mat
behind a cut-out is a defect.

### C17.2 Knockout annotation over a photograph

**Paper-filled, square-cornered label boxes with hairline black borders and mono text**,
connected to features by **thick white arrows** — the one place a white stroke is correct
outside a canvas fill.

### C17.3 Kept externals

A kept external is a **citation**. Four treatments exist and none is the default: a bare white
raster with no treatment · a bare raster carrying a watermark · a bare slide edge · a bare
journal table edge.

**Rules.**

1. **No hairline frame, no `BONE` mat, no inset margin by default.** Place the raster as-is.
2. **Do not scale** a bitonal plate up or down; scaling breaks the crispness.
3. **Everything else about a kept external stays foreign** — its own white canvas, its own
 header band (a foreign `#1E366A`, **not** `JPM_INK`), its browser-blue underlined links, its
 publisher's peach column bands, its IFRS footnotes.
4. **Add a source line naming it as a quotation** — the one house element it receives.
5. Where a kept external sits inside a **house plate** (a kicker, a caption and a NOTE block
 declaring provenance and product-neutrality), the plate is house and its content is not.

**Bitonal and scanned plates** are kept at native scale, with a hairline border **only if** the
plate's own edge is indistinguishable from the page; otherwise place bare. **Never
interpolate.**

**Pixel floor and twin replacement:**

1. A kept bitmap must be at least **250 px on its short side** (the corpus's smallest usable is
 250 × 188). Below that, replace it or report it.
2. **A same-figure pair is replaced, not hashed** — the **higher-resolution twin wins** and the
 lower is deleted from the document.
3. The corpus's keep-class bitmaps run **250–1268 px wide**; that is the observed usable band.

**Palette signatures — how to tell a quotation from an off-style figure on sight:** saturated
red / navy / green / lime · saturated orange / yellow / cyan · rust `#C0540C` with steel
`#246CB4` · a teal + mint corporate identity (`#48CCC0`, `#CCF0E4`, grey `#6C7884`) · Japanese
blue + teal (`#3C6CB4`, `#00A8A8`) · an opaque blue root panel · PyMOL-style
blue/purple/red/green · the default matplotlib 7-hue cycle · a foreign header band `#1E366A`.
**A figure whose palette matches one of these is a quotation unless the source line says
otherwise.**

**The 3-D exemption.** One figure carries an **unlabelled 3-D render inside a house plate**. It
is the corpus's one sanctioned 3-D, and the sanction is narrow: the render is **imported**, the
plate around it is house, and the figure's NOTE block declares its provenance and
product-neutrality. **The ban on 3-D (C6.4) applies to drawing, not to placing an imported
render.**

### C17.4 Off-family figures

| Class | What it looks like |
|---|---|
| **default matplotlib** | the 7-hue cycle, opaque white |
| **older plotting default** | neutral white canvas, amber + orange-red, saturated pure blue, **dotted gridlines on both axes**, bordered legend |
| **another tool's default** | Office/matplotlib default line chart, blurry |
| **Office / SmartArt** | rounded corners, pastel fills, 3-D cylinder, white background, no furniture |
| **vendor software** | navy / steel-blue / purple series |
| **a raw market-report page** | default palette, 24 bpp RGB, no alpha channel |
| **rounded + pastel + white canvas** | rounded rectangles, six pastel fills, solid triangle arrowheads |

**Rules.**

1. A **house** figure never uses a library default palette or a library default style.
2. A figure **copied from another tool** keeps its own styling if it is a quotation.
3. A figure that is **ours but built with defaults** is a **reissue**: rebuild it in the house
 language from its own printed values.
4. **Do not state the rule as "never within N RGB units of a matplotlib default"** — that
 formulation fails two legitimate figures: `JPM_BRONZE #8F5A39` sits **19 RGB units** from
 matplotlib's brown `#8C564B`, and a captured greyscale equation uses `#888989`, **17 units**
 from matplotlib's grey `#7F7F7F`. Both are coincidences, not palette leaks.

An off-family **drawn** figure — drawn in-house or imported and edited in a foreign visual
language — has its own rule, because v1 covered only external bitmaps: **because authorship is
undecidable from the image, do not silently normalise these to the house style and do not
silently keep them.** Apply the C20.2 test, and state the decision and its reason per figure.

### C17.5 Zero-accent figures

**Zero-accent figures exist.** v1's rule is one accent hue per figure; the corpus has
**no statement of what a figure with zero accents looks like**, and that is a fifth of the
diagram family.

The reference is a card pipeline with ordinal kickers: three bordered cards, each a small
uppercase `STEP n` kicker plus a name plus three micro-headed columns; no fill, no accent at all.

**Rule: a figure may be pure ink-and-paper, and when it is:**

1. the ink is `INK` (or `JPM_INK` in the register);
2. hierarchy is carried entirely by **size, space, letterspacing and one typographic weight of
 italic** — never by colour;
3. it still carries the full furniture of C10;
4. its source line names it as house work so it is not mistaken for a capture.

### C17.6 Bilingual stacking

Where a figure must carry two languages, the corpus **stacks** them:

```
Chinese primary line      black, the primary face for that element
English translation       immediately beneath, grey sans, one step smaller
```

**Rules.**

1. **One element per language pair.** Do not interleave languages inside a line.
2. The **primary** language is the document's language; the translation is subordinate —
 smaller, and in `INK_MUTED` or the grey of C8.4.
3. Leading between the pair is the element's own leading, not body leading.
4. **Chinese labels are also the generation-1 signature** (C20.3). A Chinese label in an
 otherwise generation-2 figure is either a bilingual pair or an unreissued generation-1
 leftover — check which before "fixing" it.

### C17.7 Build artefacts and inline glyphs

**Five empty spacer images** are 33 × 33 / 32 × 33 PNGs with **zero opaque pixels**, embedded
among product-photo slots. They are a build artefact: nothing to reproduce, and they cannot be
typed honestly against a taxonomy that assumes content — exclude them from any type tally.
**Rule: an image part with no opaque pixels is a defect. Remove the part; do not replace it with
a blank plate or a frame.**

**Eight inline icon glyphs** are hand-drawn-style arrows, roughly 50–110 px, on a transparent
background, used as **inline text icons** rather than as standalone figures. Their colour is an
off-palette orange `#EE822F` or black, the black ones carry a thin off-palette `#4772C9` fringe,
and the head is a **hand-drawn tapering head**, not the open-V of C15.2. **Rule: these are not
figures.** They get no furniture, no source line and no caption; reproduce them from the asset
rather than drawing a replacement.

---

## C18. Layout: approximate canvas coordinates

> **These numbers are approximate and are starting points, not a grid to obey.** They are
> deliberately rough, because the per-figure coordinates live in the drawing scripts that
> produced the corpus and those scripts were not available when this section was written. The
> owner's instruction was that rough is sufficient. **Adjust per figure.** None of them is a measurement of a delivered figure (C0.1).

### C18.1 The canvas convention

| Quantity | Value |
|---|---|
| authoring width | **`TARGET_CANVAS_W = 780` units** |
| height | **varies by figure** — there is no constant; increase `h` only, never `w` |
| the canvas widths the scripts actually use | 560–940 units |
| de-facto export width | **2400 px** (`save(png_width=2400)`) |
| matplotlib chart canvas | `FIG_W_IN = 7.1 in` × `DPI = 300` = **2130 px**; delivered chart widths run **2070–2940 px** |
| scale factor at 780 units | **×0.583** (at 940 → 0.484; at 560 → 0.813; at 1320 → 0.345) |

So one canvas unit is 2400 ÷ 780 ≈ **3.08 px** at the export width, and a 3-unit accent bar is
9.2 px — which is the agreement C15.1 records.

### C18.2 Safe margin band

| Edge | Keep clear |
|---|---|
| left and right | **40 units** of text margin on both sides; `x = 40` is the text origin |
| the frame primitive | `frame()` defaults to `x = 30`, `w = w − 60` — so a drawn frame sits **10 units outside** the text margin |
| top | never above the kicker baseline `y = 46` |
| bottom | never below the source-line baseline `y = h − 22`; the frame reserves `h − 70 − y`, i.e. **70 units at the foot** |

**The derivation:** the band comes from the two primitives that draw the outermost house
elements — `Canvas.__init__`, which fixes the 40-unit side margin and the header baselines, and
`Canvas.frame()`, which fixes the 30-unit frame inset and the 70-unit bottom reserve.

### C18.3 The vertical stack, and how much of the height each band takes

Top to bottom, in canvas units from `y = 0`:

| Band | Position | Height it consumes |
|---|---|---|
| **kicker band** | baseline `y = 46`, size 11 | **26 units** (46 → 72) |
| **title** | baseline `y = 72` (drawn at `y + 4`), size 22 | **24 units** (72 → 96) |
| **separator rule** | one line at `y = 96`, `(40, y) → (w−40, y)`, stroke 0.7, opacity 0.55 | ~0 units; it *is* the boundary |
| **content area** | starts at `body_top = 96` after the rule | see C18.4 |
| **footer stack** | from the bottom of the content down to `y = h` | **70 units minimum**, more when the notes are long |

**Without a kicker** the whole header shifts up: the title sits at `y = 50` and the rule at
`y = 74`, so the header consumes **74 units instead of 96**.

### C18.4 The content area

| Quantity | Value |
|---|---|
| top | `body_top`, i.e. **96 units** with a kicker, **74** without |
| first drawn element | `frame()` defaults its top edge to `body_top − 14`, so content conventionally begins **14 units below the rule** |
| bottom of the drawn frame | `h − 70` |
| usable content height | **h − 166** with a kicker, **h − 144** without |
| share of the canvas | about **76 % of the height** on a 700-unit-tall drawn figure, about **74 %** on a 650-unit one |
| horizontal span | `x = 40` to `x = w − 40`, i.e. **700 units of 780, about 90 % of the width** |

**The footer stack's own order and rough size**, from the graphic down:

| Footer element | Rough reservation |
|---|---|
| graphic | — |
| ALL-CAPS section label (11 units, +1.4 tracking) | ~18 units |
| serif-italic note (11.5 units, often 2–3 paragraphs) | ~16 units per line; a three-paragraph note can exceed the figure's own height |
| mono source line (12.5 units) | baseline at **`h − 22`**; ~18 units including its leading |
| mono status line | one blank line plus ~18 units, below the source line |
| a caption drawn in the raster (rarely correct — see C10.6) | baseline at **`h − 40`** |

A short footer therefore occupies roughly the reserved **70 units**; a full footer with a section
label, two note paragraphs and a status line occupies roughly **120–180 units**.

### C18.5 Multi-panel figures

**Panels are separated by whitespace only** (C13) — no rule, no gap line, no border, so the
division is a gutter you leave, not a line you draw.

| Layout | Division of the content area |
|---|---|
| two panels, **side by side** | split the **width**: two columns of about **48 %** each with a **~4 %** whitespace gutter between them |
| two panels, **stacked** (A above B) | split the **height** at the mid-point, with the **summary line** — if the figure carries one — on the gutter between them |
| a **three-band** composition | three horizontal bands; the corpus's example is intro / grid / routes with no band labels |
| a **2 × 2 quadrant** | split both axes at the mid-point; the header and the footer are shared |
| a **six-panel composite** | a 3 × 2 grid over the whole content area, lettered `(a)`–`(f)`; roughly 45 % chart / 20 % diagram / 35 % table by area |
| a **four-across comparison** | four equal columns, each panel a sketch with a sans caption below |

**Shared furniture does not consume content height twice:** the header is shared, and the
**x-axis title appears once, under the lower panel** (C13).

### C18.6 Typical heights for common forms

Widths are (780 units); the heights are derived by converting a delivered pixel height
at the de-facto 2400 px export width, or from the drawing libraries' own defaults.

| Form | Typical height (canvas units) | Grade and derivation |
|---|---|---|
| **a single chart** | **≈ 420–440** | — `chart_kit.new_chart(height_in=3.9, width_in=7.1)` at 300 dpi gives a 2130 × 1170 px canvas, i.e. 1: 0.549, which is ≈ 428 units at 780 wide |
| **a chart in the register, with a key and a note** | **≈ 480–560** | — |
| **a three-band diagram** | **≈ 520–620** | — |
| **a process flow, two rows (snaking)** | **≈ 620–760** | — |
| **a timeline, horizontal** | **≈ 420–560** | — |
| **a table figure** | **grows with the row count: ≈ 96 + 27 + 23 × rows + 70** — 10 rows ≈ 420, 20 rows ≈ 650 | computation from table metrics (C16.6) plus the C18.3 header and footer |
| **a tall composite or a long list** | **≈ 830–1540** | +: a 2074 × 2220 px register chart → ≈ 835 units; a 1980 × 2100 px rank list → ≈ 827; a 2400 × 3443 px portrait flow → ≈ 1119; a 2400 × 4740 px portrait flow → ≈ 1540 |

**A tall figure is authored at 780 units wide, not wider** — otherwise the height forces a width
increase and the type floor breaks. If the content needs more height, **increase `h` only** and
run `check_scale()`.

> **Again: these are starting points to be adjusted per figure, not a grid to be obeyed.** The
> exact per-figure coordinates were not available; the owner's instruction was that rough is
> sufficient. Where a number above is it is an estimate of proportion, not a
> measurement, and it must not be quoted as one.

---

## C19. Export and the scale assertion

### C19.1 The export contract

| Artifact | Requirement |
|---|---|
| **SVG** | always written, from the same canvas; `role="img"`, `viewBox="0 0 w h"` |
| **PNG** | **2400 px wide**, at a 300 dpi equivalent |
| matplotlib PNG | `figsize × dpi`, asserted exactly; `savefig.bbox = None` — **never `tight`** |
| matplotlib SVG | also written, same canvas |
| chart width | `FIG_W_IN = 7.1`, `DPI = 300` |

### C19.2 Transparency

* **A figure placed in a DOCX whose page tone must show through → export transparent.** A
 white-filled chart on a paper page is a visible rectangle.
* **A figure that will also be opened standalone or placed in HTML → export `PAPER`-filled**,
 because transparency against a browser's white shows white.
* **Export both and let the consumer choose.** `Canvas.save()` writes SVG + PNG; the rasteriser
 uses `cairosvg` with `background_color=PAPER` and falls back to headless Chrome with
 `html,body{background:PAPER}` — so **drawn figures are `PAPER`-filled by construction**. The
 transparent class is produced by a different path and must be requested.

**Do not quote a transparency ratio.** Whether a canvas is transparent is a per-figure decision (C3, C19.2); a global count is a snapshot of one sub-corpus, not a ratio to reproduce.

**Format deviations.** Two figures ship as JPEG where PNG was required. **Reproduce as PNG on
reissue, or record the exemption; do not silently emit JPEG for a new figure.**

### C19.3 The scale assertion

 — assert on **every** build, not once:

```python
# schematic.py
MIN_ONPAGE_PT   = 6.0
TARGET_CANVAS_W = 780
_TYPICAL_DISPLAY_PT = 455.0

def onpage_pt(font_units, canvas_w=780, display_pt=455.0):
    return font_units * display_pt / max(1, canvas_w)

# Canvas.check_scale() -> {"canvas_w", "smallest_font_units", "onpage_pt", "ok", "advice"}
#   ok = onpage_pt >= MIN_ONPAGE_PT
#   advice names the canvas width to re-author at, or the size to raise the smallest label to
```

```python
# chart_kit.save()  -- two assertions, both of which have caught real defects
# 1. saved PNG is EXACTLY figsize x dpi  (a bbox_inches="tight" silently grows the canvas and
#    shrinks every label in proportion)
# 2. the smallest label clears the floor at the document's display width:
onpage = pt * 456.6929133858268 / (w_in * 72.0)
#    raise AssertionError when onpage < MIN_ONPAGE_PT
```

```python
# diagram_kit.Diagram.report()  -- a layout verdict, not a boolean
# checks_run must contain {"scale", "bounds", "collisions"}.
# A verdict of "ok" is worthless if the checks never ran:
#   an earlier version printed OK while two of three checks were silently skipped
#   by a swallowed AttributeError.
```

**Three rules.**

1. **Assert; do not report.** A build that says `ok` while a label prints at 4 pt is the defect
 the assertion exists to catch.
2. **Assert that the checks RAN** — `{"scale", "bounds", "collisions"}` and
 `elements_recorded > 0`. A vacuous pass is worse than a crash.
3. **Never `bbox_inches="tight"` on a figure whose annotations overhang.** It grows the canvas
 and shrinks every label in proportion: a chart saved at 2841 px against a nominal 2220
 printed its 7.5 pt labels at **5.02 pt**, with `check_scale()` reporting `ok=True`
 throughout.

**Boundaries.** `check_scale()` measures the **authored** smallest label, not the printed one —
it is only as good as the canvas width you pass it.

---

## C20. Working rules

### C20.1 The twin rule

Before and after any figure work: **hash every placed file (SHA-256) and compare.** The corpus
**A group is the unit of work, not the placement** — hash every placed file, not only the files one pass happens to touch.

### C20.2 The two reproduction paths

**Path A — regenerate from a script in the design language.** The figure prints its own values,
so the numbers exist and the only question is style.

* **A1 reissue** — already a house build; re-emit it.
* **A2 first build** — currently a default-matplotlib or foreign-styled figure whose values are
 printed; build it in the house language for the first time.

**Path B — reproduce by placing the existing asset.**

* **B1 quotation** — a source-screenshot, photograph, or another party's artwork.
* **B2 draw-it-forward** — a house-drawn diagram whose content is text, structures or
 qualitative marks, with no data values: keep the asset now, re-derive it if the text changes.
* **B3 external render** — needs the original tool.

**Keep the asset but re-derive it if the text changes.** Thirteen drawn figures are already in
the house style and contain no data values; a script cannot regenerate them without re-typing
text, which is the spec's own quotation rule — but they are diagrams, not quotations, so the
quotation protection does not apply.

| If… | Then |
|---|---|
| a house-drawn diagram, no data values, text unchanged | **keep the asset** |
| the same figure but any text changes | **re-derive from the script**; if none exists, rebuild it in the house language and record that the text was re-typed |
| a house-drawn diagram **with** data values | **regenerate from the values** |
| a quotation of any kind | **keep**, always |

> **Report, do not normalise.** Report every external figure rather than silently rebuilding it;
> a reader who knows which figures are quotations reads the report differently. **Report per
> figure; never quote a global ratio you have not recomputed.**

### C20.3 Two generations of the style

An earlier generation of this house style exists — opaque white canvas, a single blue magnitude
ramp, Chinese labels, no source line, and LaTeX `{,}` thousands-separator artefacts inside title
strings. **Do not reproduce it; a new figure is generation 2, the style specified here.**

**Rules.** Identify an earlier-generation figure by the grep signature (the `{,}` artefact, an
opaque white canvas, the single-hue blue ramp) and **reissue** it. Its *content* may be a
quotation or may be house work; decide per figure by C20.2 — its generation does not decide
that. The `{,}` artefact is a **build defect, not a locale choice**: it comes only from a code
pipeline writing a LaTeX-formatted number into a plain string, and it must never ship.

### C20.4 What is a defect, not a style

These are things the corpus does that are **defects**. Reproduce the figure's *intent*, fix these
on reissue — and **record that you fixed them**, because a faithful reproduction of a defect is
a defect.

* no source line on a house figure (the PLATFORM family)
* a mono source line physically overlapping the bottom bar of the chart
* bars not sorted descending while their siblings are, and highlight logic that differs between
 siblings
* a dual-axis figure that does not name its right-hand series
* a hue assigned to each row that does not carry across two panels
* non-house canvas and hues with dotted gridlines on both axes (an older plotting default)
* JPEG export where PNG was required
* `{,}` LaTeX separator artefacts inside title strings
* scaffolding labels surviving into delivered artwork (`COLUMN 1` / `COLUMN 2`)
* misspellings surviving inside a figure, and broken word spaces
* a source line that reproduces a typo from the source document
* a malformed source line whose document name is truncated
* five empty spacer images with zero opaque pixels
* a row that is not in the stated order while its siblings are
* third-party content redrawn in-house without a provenance note
* a curve figure declaring its own positions unverifiable but printed as though scaled

The fuller register is `STYLE_REFERENCE.md §56`.

---

## Appendix — the forbidden list
### The forbidden list

Rewritten from v1 §10, with the corpus's own exceptions carved out. **Each entry was an actual
defect at least once.**

**Structural**

* Default matplotlib colours, 3-D bars, pie-chart gloss, dual-axis tricks — **dual axes are no
 longer forbidden (`COR-15`); a dual-axis figure must name its right-hand series**
* Gradients, drop shadows, bevels, glows, rounded corners
* A **white or transparent canvas where the page is paper** — **for a house figure**. White is
 correct for a facsimile, a foreign capture and a generation-1 figure (C3); transparent is
 correct for a photographic cut-out
* `bbox_inches="tight"` on any figure whose annotations overhang
* More than one accent hue for **the same semantic class** in one figure — **two hues are
 permitted when they are different classes** (`COR-5`, C2.1)
* **Bold** · italic used for emphasis instead of the semantic slots · any tracking on body text
* Rounded corners anywhere; a folded corner anywhere except a callout (C15.6)
* 3-D — **except** an imported render inside a house plate (C17.3)
* A figure with no source line — **the PLATFORM family is a recorded defect, not a precedent**
* Labels below **6.0 pt** on the page — the most common and most damaging defect

**Corrected entries — v1 forbade what the corpus does**

| v1 forbade | Corrected rule |
|---|---|
| vertical gridlines | permitted and required on horizontal-orientation charts (C11.6) |
| solid arrowheads only | **two forms**, chosen by shaft colour (C15.2) |
| vertical rules in tables | horizontal-only is the house rule; a full grid is a declared exemption class (C16.6) |
| `SEED_BROWN` and `LIME` as text | permitted as short isolated strings; a legibility constraint, not a prohibition (C2.3) |
| opacity | alpha **is** the mechanism for bands, area fills and halos; use the ladder (C4.3) |
| a legend whenever labels do not collide | legends are first-class; key blocks and state-key lines are forms (C11.8) |
| one shared source line per paired panel | one source line, but per-panel titles when the panels measure different things (C13) |
| `Figure N —` inside every figure | the number lives in the document; an in-image caption is an unnumbered sentence (C10.6) |
| sans headlines, always | serif titles in the finance register (C10.3) |
| a single accent hue per chart | the JPM register is a three-hue palette; a ramp is one hue at several lightnesses (C4.2) |
| score cells as marks, always print the scale | marks are the house rule; a **declared** imported table may use conditional-format colour with no key (C16.4) |
| "never within N units of a matplotlib default" | **do not state the rule this way** — `JPM_BRONZE` is 19 units from mpl brown, and a captured grey is 17 units from mpl grey (C17.4) |

### Carried cautions

1. **Font stacks are specified but not implemented.** `tools/design/brand.py` has no CJK face
   constant and no ordered fallback chain, and `tools/docx_brand.py` hard-codes `w:eastAsia` to
   `SimSun` rather than the `Arial` of C8.3. **Both must be updated to match C8.3.**
2. **The C18 coordinates are approximate proportions, not measurements** — the drawing scripts
   that would give exact per-figure geometry were not available. Do not quote a C18 number as a
   measurement, and adjust per figure.
3. **The 6.0 pt floor has never been verified against a delivered figure** — no raster carries a
   page-width reference. Absence of a violation is not compliance.
