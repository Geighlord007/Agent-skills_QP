# `synbio-editorial` — the figure style, device detail

**Longer-form companion to `STYLE.md`. Every drawing rule of the style; no audit record.**

> **What this file is.** The fuller statement of the `synbio-editorial` house figure style: the
> per-device detail behind the condensed core rules of `STYLE.md` — every form, every variant,
> every decision rule, with the reasoning that makes a rule meaningful.
>
> **Which file to read.** `STYLE.md` is the file to read while drawing: it carries the tokens,
> the numbers, the rules and the recipes. Come here when the core is too terse and you need the
> full detail of a device — the chart forms, the legend forms, the per-hue meaning table, the
> annotation kit, table metrics.
>
> **Numbering.** Section numbers are this file's own and are stable. `STYLE.md` uses its own
> `C`-prefixed numbering and maps it here in its `C0.2`, so a `§N.M` citation in the core
> resolves in this file.
>
> **Precedence.** Where this document and the drawing code disagree, the code wins. Where this
> document and the figure in front of you disagree, the figure wins: match it, and report the
> difference.
>
> **Not in this toolkit.** The evidence base, the measurement discipline, the per-figure
> findings and the verdict tables are the audit record of the engagement that produced this
> style. They belong to that project, not to a reusable toolkit, and are kept in its admin
> folder.

## Table of contents

| Section | Section |
|---|---|
| [0 How to read this document](#0-how-to-read-this-document) | [29 The box](#29-the-box) |
| [2 Corrections register](#2-corrections-register--where-v1-was-wrong) | [30 Arrows](#30-arrows) |
| [4 Core tokens](#4-core-tokens) | [31 Connectors](#31-connectors) |
| [5 Hue semantics](#5-hue-semantics) | [32 Process and flow](#32-process-and-flow) |
| [6 Canvas assignment](#6-canvas-assignment) | [33 Timelines](#33-timelines) |
| [7 Fills, alpha and tints](#7-fills-alpha-and-tints) | [34 Annotation kit](#34-annotation-kit) |
| [8 Status tags and evidence marking](#8-status-tags-and-evidence-marking) | [35 Molecules and chemistry](#35-molecules-and-chemistry) |
| [9 Hatching and fill-state](#9-hatching-and-fill-state) | [36 Cross-sections and positioning maps](#36-cross-sections-and-positioning-maps) |
| [10 Geometry](#10-geometry-strokes-corners-dashes-opacity) | [37 Scale-free figures](#37-scale-free-figures) |
| [11 Type: the scale law and the ramps](#11-type-the-scale-law-and-the-ramps) | [38 Tables](#38-tables) |
| [12 Face assignment](#12-face-assignment) | [39 Matrix marks](#39-matrix-marks) |
| [13 Tracking and micro-labels](#13-tracking-and-micro-labels) | [40 Empty and absent cells](#40-empty-and-absent-cells) |
| [14 The kicker](#14-the-kicker) | [41 Table extras](#41-table-extras) |
| [15 The header stack](#15-the-header-stack) | [42 Table metrics](#42-table-metrics) |
| [16 Title and subtitle](#16-title-and-subtitle) | [43 Full-grid tables](#43-full-grid-tables) |
| [17 The footer stack](#17-the-footer-stack) | [44 Facsimile statements](#44-facsimile-statements) |
| [18 The source line](#18-the-source-line) | [45 Zero-accent figures and off-family drawings](#45-zero-accent-figures-and-off-family-drawings) |
| [19 Captions live outside the raster](#19-captions-live-outside-the-raster) | [46 Photographs](#46-photographs) |
| [20 Axes](#20-axes) | [47 Kept externals](#47-kept-externals) |
| [21 Gridlines](#21-gridlines) | [48 Build artefacts and empty slots](#48-build-artefacts-and-empty-slots) |
| [22 Value labels](#22-value-labels) | [49 Inline icon glyphs](#49-inline-icon-glyphs) |
| [23 Legends and keys](#23-legends-and-keys) | [50 Off-family figures](#50-off-family-figures) |
| [24 Axis forms](#24-axis-forms) | [51 Two generations of the house style](#51-two-generations-of-the-house-style) |
| [25 Numerals](#25-numerals) | [52 Working rules](#52-working-rules) |
| [26 Chart forms](#26-chart-forms) | [53 Canvas geometry and aspect](#53-canvas-geometry-and-aspect) |
| [27 Panels](#27-panels) | [54 Export contract](#54-export-contract) |
| [28 Uncertainty and ranges](#28-uncertainty-and-ranges) | [55 The scale assertion](#55-the-scale-assertion) |
| [56 Defect register](#56-defect-register) | [Appendix C — the forbidden list](#appendix-c--the-forbidden-list) |

## 0. How to read this document

### 0.1 The test applied to every line

> **If someone had only this document, could they draw the figure identically?**

A line that fails that test does not belong in the body. Prose about intent is compressed to the
minimum needed to make a number meaningful.

### 0.2 Where authority sits

1. **The drawing code wins.** `tools/design/brand.py`, `tools/design/schematic.py`,
   `diagram_kit.py` and `chart_kit.py` hold the constants. Where a hex or a number in this
   document disagrees with the code, the code is right.
2. **A reading taken off a finished image identifies which token was used; it is never a
   measurement of the token's value.** Colour readings are bucketed, and close tokens cannot be
   told apart that way.
3. **Type size and face are stated as requirements.** No delivered image carries a page-width
   reference, so the scale law (§11) and the face assignments (§12) have never been checked
   against a delivered figure. They are the requirement, not an observation.

### 0.3 Status vocabulary

Rules are stated as rules. Where the style genuinely leaves two readings live, the text says
**UNRESOLVED** and gives both — reproduce the figure in front of you; do not harmonise.

### 0.4 Section-numbering convention

**`§N` always means a section of THIS document.** A reference to the earlier version of the style
is written **`v1 §N`**. `v1` had sections this document does not (`v1 §9b`, `v1 §9c`, `v1 §9d`,
`v1 §8.6`, `v1 §5.1`–`v1 §5.10`); §2 states which reading is authoritative.

## 2. Corrections register — where v1 was wrong

Each entry states what the earlier version of this style said and what the rule actually is. A
`COR-n` cited anywhere in this toolkit is explained here. **The corrections are the style:** a
corrected rule is a drawing rule, and the sentence it replaces is not.

### 2.1 The four rules v1 states wrongly

**COR-1 — Gridline orientation.** v1 said "no gridlines, except faint horizontal `RULE_SOFT`
lines where a reader genuinely needs to read a value off an axis." **That was wrong in both
halves.** On horizontal-orientation charts the gridlines are faint **VERTICAL** lines dropped
from the x ticks; and horizontal gridlines appear at **every** y tick, not only where a value
must be read. Corrected rule: §21.1.

**COR-2 — Arrowheads.** v1 said arrows are "thin, with a small **solid head**". **Two head forms
coexist:** the small **open-V chevron**, which inherits the figure's accent hue, is the default
for accent-coloured flow arrows; small solid filled heads are the second form. Rule and the
choice between them: §30.1.

**COR-3 — Vertical rules in tables.** v1 said comparison tables carry "**no vertical rules**".
That is the house rule for house tables, but there is a **declared exemption class**: a table
imported as a whole is reproduced as a **full grid**, with ~0.5 px `INK` rules on all four sides
of every cell. Rule: §38.1; exemption: §43.

**COR-4 — `SEED_BROWN` and `LIME` are not fill-only.** v1 said "`LIME` and `SEED_BROWN` are
fill-only" and "never body text on paper". Both are used **as text**. What is true is a
**legibility constraint**, not a prohibition: these hues fail on paper at small sizes, so a text
use must be a short, isolated string that is large enough on the page. Rule: §5.3.

### 2.2 The rest of the register

**COR-5 — Not one accent hue per figure.** Two or more hues are in wide use, and the JPM set is
a three-hue palette, not one accent. Rules: §5.3, §7.2.

**COR-6 — "No opacity tricks" is wrong.** Alpha is the mechanism for light bands, area fills and
halos: an area fill under a line is the series hue at ≈13 %, a halo or bubble the token at ≈0.9.
Rule: §7.3.

**COR-7 — Boxes are not "thin black borders".** Borderless flat-filled blocks exist, as does
accent-only fill with zero border; the accent left-edge band is the dominant device. Rules:
§29.1, §29.4.

**COR-8 — The `Figure N —` number is never in the raster.** It is the document's caption
paragraph. Where an in-image caption exists it is either unnumbered or numbered with an **en
dash**. Rules: §17.1, §19.

**COR-9 — Serif titles exist.** The sans face is not universal: the finance register sets
**serif** titles. Rule: §16.2.

**COR-10 — The "1.24× signature move" is unverified.** Do not cite it as measured; use the
deck-line device. Rule: §12.4.

**COR-11 — Do not trust a transparency census.** Transparent and opaque-white canvases are both
correct for named classes; decide per figure. Rules: §6.5, §54.2, §54.3.

**COR-12 — Do not trust a quoted duplicate list.** Hash the files. Rule: §52.1.

**COR-13 — Canvas is chosen per document, not by subject.** `TRAVERTINE` is not a
"financial figures only" canvas: it also carries regulatory, process and licensing figures.
Rules: §6.2, §6.4.

**COR-14 — "Never default matplotlib colours" stands as a target.** Default 7-hue cycles and
older plotting defaults do occur; they are defects, not precedents. Rules: §50.1, Appendix C.

**COR-15 — Dual axes are permitted.** A figure with a second axis must **name its right-hand
series**. Rule: §26.9.

**COR-16 — 3-D is forbidden in drawing, permitted once as an imported render** inside a house
plate. Rules: §47.5, §50.1.

**COR-17 — Score cells as marks is the house rule, and the scale must be printed.** A
**declared** imported table may encode value by hue with no key. Rules: §39.5, §43.

**COR-18 — Paired panels share one source line but may carry per-panel titles** when the panels
measure different things. Rule: §27.7.

**COR-19 — Legends are first-class, not a fallback.** Use a legend, a key block or a state-key
line whether or not labels collide. Rules: §23.1, §23.7.

**COR-20 — PNG at 300 dpi is the rule.** JPEG is a recorded exemption, never a precedent. Rule:
§54.4.

**COR-21 — `ROSE` is the chronology/process accent** — timeline dots, timeline leader arrows,
and in flows the box edge bar, the connector, the start dot and the circle-with-X terminus. It is
also `EVIDENCE` in the code. Rules: §5.2, §5.3.

**COR-22 — The accent edge is on EVERY node.** Emphasis is carried by fill and label instead, and
some figures carry **no accent hue at all**. Rules: §29.2, §45.1.

**COR-23 — Opaque white is correct for named classes:** facsimiles of filings and press material,
foreign captures, and earlier-generation figures. Transparent is correct for photographic
cut-outs. Rule: §6.5.

**COR-24 — `JPM_SLATE #5A6470` does not reproduce the slate family actually used.** The delivered
slate centres on markedly darker values (`#3C546C`, `#304860`, `#243C54`, `#486C9C`);
reimplementing the token literally will not reproduce them. Rule: §4.3.

**COR-25 — Type size and face are requirements, not measurements.** Neither can be read from a
delivered image. Rules: §11.1, §12.2.

**COR-26 — Tracking is not zero everywhere.** The code emits negative tracking on the title and
positive tracking on mono micro-labels, in **canvas units**, not rem. Rule: §13.1.

**COR-27 — Not every figure carries a source line.** A house figure may carry kicker + title +
rule only. A missing source line is a **recorded defect**, not a precedent. Rules: §18.7, §56.

**COR-28 — Letterspaced uppercase is not only for kickers:** it is also applied to panel labels
and row headers. Rule: §13.2.

**COR-29 — Density maxima exist.** Three stacked panels plus a key plus a two-column source
footer fit on one canvas, and six-panel composites exist. Rule: §27.10.

## 4. Core tokens

All hexes are from `tools/design/brand.py`. Do not hard-code a hex anywhere else.

### 4.1 Canvas and ink

| Token | Hex | Role |
|---|---|---|
| `PAPER` | `#F7F5EB` | the page canvas for house figures |
| `BONE` | `#EDEADB` | secondary panel, table header band, footer |
| `TRAVERTINE` | `#F4EFE7` | financial-register canvas — but see §6.2 |
| `INK` | `#000000` | all text, all rules |
| `INK_2` | `#3A3A38` | body copy where pure black is too hard |
| `INK_MUTED` | `#6B6B66` | captions, source lines, metadata, axis tick labels |
| `RULE` | `#000000` | 1 px hairline (same value as `INK`, separate name) |
| `RULE_SOFT` | `#D8D3C4` | faint gridline — **and also a series colour**, §7.5 |

### 4.2 Accents

| Token | Hex | Code-assigned meaning |
|---|---|---|
| `MOSS` | `#9EA617` | *natural* — chart hue 1; `NATURAL = MOSS` |
| `MEADOW` | `#617D24` | *data series / positive* — chart hue 2; `POSITIVE = MEADOW` in `chart_kit`/`diagram_kit` |
| `CLAY` | `#E05E3D` | *engineered / designed / animal*; `ENGINEERED = CLAY`; also `CONFIDENCE["UNVERIFIED"]` |
| `ROSE` | `#C28775` | *evidence* — chart hue 3; `EVIDENCE = ROSE`; also the **negative** waterfall bar in `chart_kit.waterfall()` |
| `SEED_BROWN` | `#D1B594` | *low emphasis, bands* — chart hue 4; `NEUTRAL = SEED_BROWN`; also `CONFIDENCE["ESTIMATED"]` |
| `LIME` | `#E0DB00` | fill only by intent — but see **COR-4** |

`TEXT_SAFE_ACCENTS = (MOSS, MEADOW, CLAY)`. Clay on paper is ≈3.6:1 — large text
only.

### 4.3 The JPM set

| Token | Hex | Code intent | Corpus note |
|---|---|---|---|
| `JPM_PAPER` | `#F4EFE7` (= `TRAVERTINE`) | financial canvas | §6.3 |
| `JPM_INK` | `#0B2A4A` | deep navy — headings, primary series, table header band | measured `#002448`, consistent with the token |
| `JPM_SKY` | `#A6D7F0` | secondary series, fill bands | measured `#9CCCF0` / `#B1DAEE` at ≈0.88–0.9 alpha |
| `JPM_BRONZE` | `#8F5A39` | accent, emphasis figure, benchmark line | measured `#845430`–`#805030` |
| `JPM_SLATE` | `#5A6470` | axis, labels, de-emphasised series, footnotes | **does not reproduce the corpus** — see **COR-24**. Measured slate centres `#3C546C`, `#304860`, `#243C54`, `#486C9C` |

> **Rule.** If a figure must match an existing one, sample its slate from that figure. If it is
> new work, `#5A6470` is the token but expect the delivered figure not to match its
> neighbours.

### 4.4 Semantic aliases are code, not prose

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
All. **`ACCENTS["finance"]` is `JPM_BRONZE`, not `JPM_INK`** — a financial figure
that takes its accent from `ACCENTS` starts on bronze.

---

## 5. Hue semantics

### 5.1 The rule, stated so it can be applied

> Choose a hue by the **role the mark plays in this figure's argument**, not by taste, and
> not by tick order. Where two roles collide in one figure, the second hue must be a
> **different semantic class** (a comparison, a tag, an alert), never a second category of
> the same class drawn in a different colour for variety.

Where a hue has several roles, that is not a licence to pick either freely — it means the
corpus genuinely uses one hue across several roles, and a reproduction must use the same
hue the original did. §5.3 is the lookup table.

### 5.2 Observed meanings per hue — the collision table

**This table is deliberately not one-to-one.** The corpus contradicts a tidy mapping, and the
reports said so: "do not invent a tidy one-to-one mapping that the corpus contradicts."

**The green family — `MOSS` `#9EA617` and `MEADOW` `#617D24` (reports frequently cannot tell
them apart and call both "olive").** Each batch independently counted 6–7 meanings within its
own 47 figures; the union across all six is larger:

| # | meaning |
|---|---|
| 1 | availability / disclosed |
| 2 | time period (an ordered ramp with the year text coloured to match) |
| 3 | row identity |
| 4 | flow direction, carried by the **arrows as well as** the edge bars |
| 5 | natural variant / high tolerance |
| 6 | achieved titre |
| 7 | workflow spine |
| 8 | highlight the outlier against neutral context |
| 9 | ordinal rank (a lightness ramp) |
| 10 | flow path / "this is the assembly line" |
| 11 | a chemical-annotation pointer (locant digits, β symbol, bond angles) |
| 12 | plain series fill |
| 13 | root-node "natural / food" |
| 14 | biological agent — bioindicators, metal uptake, microbial oxidation |
| 15 | "compatible" in a matrix |
| 16 | the engineered subject enzyme LiP (olive, competing with `CLAY`) |
| 17 | evidence status VERIFIED / measured |
| 18 | a regulatory pathway (EU) |
| 19 | a market segment / production route |
| 20 | the natural dairy process itself |

> **Two different greens coexist and are not interchangeable.** 089 and 091 measure `MEADOW`
> `#617D24` exactly; **069 and 064 measure ≈`#507010`, a darker olive that is not a token**.
> A reissue that emits `#617D24` will not match 069's original. Separately, **177 and 178 are
> the same template with the same meaning and use different greens** (177 `MEADOW`, 178
> `MOSS`) while `SERIES_SINGLE = [MOSS]` points the other way. **UNRESOLVED**; sample the
> original.

**`CLAY` `#E05E3D` and its rust/terracotta relatives.** The union of meanings:

| # | meaning |
|---|---|
| 1 | the figure's subject / the engineered thing |
| 2 | a neutral measured series |
| 3 | a median statistic |
| 4 | a severity rating |
| 5 | a computed date |
| 6 | a legal prohibition |
| 7 | the US regulatory pathway (the EU pathway is drawn in olive instead) |
| 8 | the subject brand / market |
| 9 | the largest value |
| 10 | a waterfall total |
| 11 | an increment |
| 12 | a reference threshold |
| 13 | an alert about numbers that do not reconcile |
| 14 | a reaction arrow only (measured lighter, `#E49078`) |
| 15 | unit operations + every flow arrow |
| 16 | the proposer's own plan and the decision gate |

> **116 vs 117 are the identical construction with two different hues for the same semantic
> class** (a regulatory pathway). **UNRESOLVED** — match the figure you are reproducing,
> do not harmonise.

**`ROSE` `#C28775`.**

| meaning |
|---|
| chronology and process — timeline dots, timeline leader arrows, and in flows the box edge bar, the connector, the start dot and the circle-with-X terminus |
| evidence — measured, assayed, observed |
| a pale pink band marking a duration or a gap |
| the **negative** bar in a waterfall |
| possibly the third hue in 000/001/002, read as `#C67E6F` — ROSE or CLAY |

**`SEED_BROWN` `#D1B594`.**

| meaning |
|---|
| neutral / low emphasis / context band |
| **text** — a year and a host name |
| a domain class inside one protein (the terminal Te domain) |
| partial disclosure — a data value drawn in the neutral colour |
| a 69 %-of-pixels area wash for geological units |
| a secondary series on bars and lines |
| category lanes |

**`JPM_BRONZE` `#8F5A39` / measured `#845430`–`#805030`.**

| meaning |
|---|
| exactly one emphasised item in an ink field — top supplier, latest round, top family, top decile, highest-priced material, latest half-year, market-cap milestone |
| the **largest** category fill, i.e. not an accent at all |
| a plain series hue |
| a chemistry product colour |
| **above** the upper threshold rule (with ink between and slate below) |
| a milestone diamond + drop line |
| a **loss** (negative series) in one figure and a **profit** in others |

**`JPM_INK` navy.**

| meaning |
|---|
| the primary measured series, the total, a calculation, `INK` itself |
| **the risk the panel exists to expose** — related-party revenue |
| initial consideration (with slate as the deferred part) |
| all box outlines, all body text inside boxes, all axis lines |

**Sky blue** (`JPM_SKY` and relatives).

| meaning |
|---|
| secondary series |
| a threshold-rule colour |
| a mark fill (the halo) |
| a decrement in a waterfall |
| a key input node |
| `UNVERIFIED` fill |
| third-party revenue — "the good half" |
| a segment with no valence |
| a residual category |

**`RULE_SOFT` `#D8D3C4`** is both the gridline colour and the third data series in 187 (the
grey mass on the canvas is both, 5.5 % of pixels). §7.5.

### 5.3 Using the table

1. Identify the role the mark plays.
2. Find that role above; use the hue recorded against it.
3. If two roles collide and both are in play, the second is a **different class** — a
 comparison, a status tag, an alert — never a second colour for the same class.
4. If the role is not in the table, **sample the nearest precedent figure** rather than
 inventing an assignment.
5. `SEED_BROWN` and `LIME` **may** be text (COR-4), but only as a short isolated string that
 is large enough on the page; the two recorded uses are a 4-character year and a 10-character
 phrase.

### 5.4 The sanctioned second hue: the alert

One figure uses a second accent **only** to flag a number that does not reconcile with its
neighbour: 089 sets `CLAY` italic text over the middle group while its data is `MEADOW`. This
is a knowing exception to a single-accent reading and **must be preserved as an exception**,
or the next person will "correct" it away. Rule: the alert hue is `CLAY`, it is applied to
**text only**, it never fills a mark, and it is used at most once per figure.

### 5.5 The worked matched pair — 081 / 082

The clearest example of the semantic-hue rule in the corpus, and the one to copy when
explaining it: **081 and 082 are the same construction** — same kicker (`B-GLUCAN ·
APPLICATIONS`), parallel titles, same fishbone — and differ in exactly one thing: the root
node's accent band is **`MOSS` in the food figure** and **`CLAY` in the
chemical/pharmaceutical figure**. Use this pair as the reference implementation.

---

## 6. Canvas assignment

### 6.1 The canvases that actually appear

| class | canvas |
|---|---|
| house drawn figures and house charts | `PAPER #F7F5EB` opaque |
| the JPM/cosmetic register | `TRAVERTINE #F4EFE7` opaque |
| transparent (page tone shows through) | alpha 0 |
| photographic cut-out | transparent |
| opaque white, **inherent** | `#FFFFFF` |
| opaque white, **drift generation** | `#FFFFFF` |
| near-white, off-family | `#F8F9F8` |
| dark / photographic / saturated | — |

### 6.2 The rule

1. **Canvas is chosen per DOCUMENT, not per figure's subject** (**COR-13**). A document that
 is a market/company register draws *every* one of its figures on its own canvas — including
 a metabolic pathway, a PA66 repeat unit, a patent route, a compatibility matrix and a
 regulatory timeline.
2. **Default:** house figure → `PAPER` opaque.
3. **A figure placed in a DOCX where the page tone must show through** → export transparent
 (§54.2). This is the export path that produces a transparent class.
4. **A photographic cut-out** → transparent, always (§46.1).
5. **A facsimile or capture** → keeps its own canvas, white included (§47.1).
6. **Never tint a canvas.** The token's exact hex, or transparent, or the foreign file's own
 pixels. No `PAPER` at 40 %.

### 6.3 `PAPER` versus `TRAVERTINE` — do not pick a winner

**`PAPER #F7F5EB` and `TRAVERTINE #F4EFE7` differ by only about 1.2–3.9 % per channel**, which is
below the resolving power of a quantised dominant-colour reading; the two tokens cannot be told
apart that way. **Do not write "finance figures use `TRAVERTINE`" as a rule.** Sample the figure
you are reproducing and match it; for a new figure follow the document rule of §6.2.

### 6.4 Per-document palette switch

The palette switches at the document level:

| document class | canvas | palette |
|---|---|---|
| scientific / process house figures | `PAPER` | `MOSS` / `MEADOW` / `SEED_BROWN` |
| market / company registers, cosmetic market figures, protein-based materials | `TRAVERTINE` | the §4.3 JPM set — `JPM_INK` strokes and text, `JPM_SKY` secondary, `JPM_BRONZE` accent, a dark slate |
| regulatory BLG figures | white | a **third, undocumented blue-grey set** (`#486C9C`, `#849CC0`, `#9CB4CC`, `#6084B4`, `#244860`, `#547890`) |

The third set is in the corpus and in no token table. Either add it or replace
it; do not leave it undocumented, because a successor will otherwise build a BLG figure in
`MOSS` and be wrong on every mark.

`SERIES_SYNBIO = [MEADOW, MOSS, SEED_BROWN, ROSE, CLAY]` and
`SERIES_FINANCE = [JPM_INK, JPM_BRONZE, JPM_SKY, JPM_SLATE, SEED_BROWN]` are. Neither
admits a single-hue ramp; the corpus uses ramps anyway (§7.2).

### 6.5 White is a class, not always a defect

v1 called every white canvas a defect. **COR-23.** Three classes where white is correct:

1. **Facsimile material** — a captured filing, statement or press page. 250, 251, 252.
2. **Foreign captures** — the chrome is the provenance.
3. **The generation-1 drift figures** — 235, 236, 237, and 246. Correct **to their own
 generation**, wrong for new work (§51).

White is a **defect** on a newly drawn house figure.

---

## 7. Fills, alpha and tints

### 7.1 Flat fill

Fills are a single flat colour. No gradient, no bevel, no shadow, no texture except the hatch
of §9.1.

### 7.2 Within-family ramps are permitted

A single hue at several lightness levels encodes an **ordinal** scale, and this is
in the corpus in at least four places:

| form |
|---|
| ONE hue at three lightness levels (dark olive → pale sage) = ordinal tier rank 1 > 2 > 3 |
| one hue as a lightness ramp; hollow = off-scale |
| three blues for three series |
| four blue-greys for four step types |
| a four-step blue ramp, one blue per production organism, grey = "Withdrawn" |
| navy + slate + sky on one chart |

**Rule:** a ramp is one hue, three to four steps, monotonic in lightness, and it means *rank*
or *type* — never *category variety*.

### 7.3 Measured alpha values

| use | measured value |
|---|---|
| area fill under a line = the series hue at **≈13 % over the canvas** | `MEADOW` 13.3 % over `PAPER` → `#E3E5D1`; `MOSS` 13.5 % → `#EBEACF` |
| bubble / halo fill = the token at **≈0.9 alpha**, not the token | `#B1DAEE`, consistent with `JPM_SKY #A6D7F0` at ≈0.88 over `TRAVERTINE` |
| band / zone opacity | 0.75 (column band) |
| the opacity ladder used across the drawing scripts | **0.14, 0.16, 0.22, 0.28, 0.35, 0.4, 0.45, 0.5, 0.55, 0.85** |
| the header rule's own opacity | 0.55 |

**Use one of the eleven ladder values.** Do not invent 0.33 or 0.62 — a reproduction that
lands between two ladder values reads as a different hand.

### 7.4 Non-token tints that are in production

| tint | where | status |
|---|---|---|
| `#D0E4EB` | 170's stage band | neither is a token — add it to the table or replace it |
| `#B1DAEE` | 158's bubbles (= `JPM_SKY` at ≈0.88) | resolved above |
| `#D8D8C0` | a pale tinted band behind a whole process column, 191 | a column separator, not a token |
| `#D0D0C0`–`#E0E0D0` | a **cool sage-grey** doing three jobs: de-emphasised series (264/265), neutral bars, range bars | "closest to `SEED_BROWN` in name, but `SEED_BROWN #D1B594` is a warm tan and this is a cool sage-grey. **The spec's token cannot produce the observed colour.**" |
| `#EE822F` | six inline arrow glyphs | §49 |
| `#4772C9` | a blue fringe on the black glyphs | §49 |
| `#0CF0CC` / `#24F0D8` / `#18F0D8` | pure **cyan** year labels on a vertical timeline spine | §33.10 |
| `#3C546C`, `#304860`, `#243C54`, `#486C9C` | the slate family (COR-24) | §4.3 |
| `#FCE4E4`, `#FCE4D8`, `#FCA86C`, `#FCCC9C`, `#8484C0`, `#B4D8B4` | pastel conditional-format cells, 220/228 | §39.5 |
| `#1E366A` | an external table's header band — **not** `JPM_INK`, RGB distance 39 | §47.1 |
| `#D80000`, `#00006C`, `#006C3C`, `#9CC000`, `#FC6000`, `#FCFC00`, `#00CCFC`, `#90CCFC`, `#C0540C`, `#246CB4`, `#48CCC0`, `#CCF0E4`, `#3C6CB4`, `#00A8A8` | foreign figures' own palettes | §47.4 |

### 7.5 `RULE_SOFT` doubles as a series colour

In 187 the third series ("Rare earths") is drawn in the same `#D8D3C4` that draws the
gridlines, and together they are 5.5 % of canvas. A successor cannot tell from v1 which grey
is a gridline and which is data. **Rule:** name the grey explicitly in the figure's own key
sentence when the two coexist. Do not let a gridline and a series share a hex silently.

### 7.6 `SEED_BROWN` at two scales

| scale |
|---|
| a series hue on bars and lines |
| a **69 %-of-pixels area wash** for geological units |

Same token, a 2-orders-of-magnitude difference in coverage. Both are legitimate; the
reproduction must match the coverage, not just the hex.

---

## 8. Status tags and evidence marking

### 8.1 The three-state vocabulary

The corpus prints its own confidence inside the figure, in three states,-backed by
`brand.CONFIDENCE`:

| tag | token | semantics |
|---|---|---|
| `VERIFIED` | `MEADOW` | traced to a primary source; an outside filing confirmed the number |
| `ESTIMATED` | `SEED_BROWN` | model / analyst estimate; a value digitised or repositioned from somebody else's figure |
| `UNVERIFIED` | `CLAY` | no source, or stale; carried by an externally sourced panel |

Figures.
### 8.2 Four placements, all required to be available

| # | form |
|---|---|
| i | `ESTIMATED — H&H Group infant formula OPN volume and value`; a standalone `ESTIMATED` tag on a timeline |
| ii | `85%–98% (random distribution) VERIFIED` |
| iii | `1 VERIFIED CELL` |
| iv | `UNVERIFIED at source.` / `UNVERIFIED – …` / `… is UNVERIFIED` |

Also observed: appended to an axis or segment label — `Serviceable available market 125,711 t
(ESTIMATED)`, `Lactoferrin animal-nutrition sales forecast, 2026-2035 (ESTIMATED)`.

**Rule:** uppercase, letterspaced, `INK` or `INK_MUTED`; **never a colour on its own**; the tag
always sits adjacent to the thing it qualifies.

### 8.3 Chip rendering

Small square-cornered **filled chips**: `MEADOW` fill = `VERIFIED`, `SEED_BROWN` fill =
`ESTIMATED`, **empty outline** = untagged.

### 8.4 The fill key

A swatch key at the foot of the figure mapping **fill colour to tag** — the fill itself is the
legend. Titled `HOW TO READ THE FILL`.

### 8.5 Fill-as-tag on boxes

A grey/slate box is by definition an `ESTIMATED` input; a sky box an `UNVERIFIED` one; a white
outline box untagged.

---

## 9. Hatching and fill-state

### 9.1 Hatch is a state, not a texture

The word "hatch" appears nowhere in v1. It is the corpus's standard uncertainty mark across
five figures in four documents, and it is implemented in code.

 `diagram_kit.hatch(color, key="diag", pitch=5.0, width=0.9)` — a 5.0-unit tile,
0.9-unit stroke, four registered patterns:

| key | path | reads as |
|---|---|---|
| `diag` | `M0,5 l5,-5` — one 45° line per tile, **bottom-left → top-right** | the default |
| `cross` | `M0,5 l5,-5 M0,0 l5,5` | cross-hatch |
| `horiz` | `M0,5 l5,0` | horizontal rules |
| `dots` | a circle r = `width×0.8` = 0.72 at the tile centre | stipple |

**Both directions occur:** a dense 45° `diag` (bottom-left → top-right), and its mirror —
light lines running top-left → bottom-right **over the bar's own hue** — which the code
cannot produce. **UNRESOLVED**:
default to `diag`; where the original is mirrored, mirror it.

**Semantics of hatching — all recorded uses:**

| meaning |
|---|
| placeholder / insufficient data / not evidenced |
| liability (against a filled glyph = evidence) |
| unverified / a category not evidenced |
| eliminated |
| **stated target, not yet built** (against solid = built) |
| a **non-modelled remainder** — "stated revenue less the three named segments", with a legend entry **and** a footer paragraph |
| a subtracted cost in a bridge |
| a **restatement** marker over the restated part of a bar, with a callout naming it |
| dense diagonal / dot / cross hatch separating **geological units** |

**Rule:** hatch is same-hue-as-the-fill-it-replaces. Hatch always carries a key entry or a
sentence (§23.13). A hatched block that is *not* a modelled segment must say so in the footer.

### 9.2 Hollow vs solid

The corpus's uncertainty vocabulary is **fill state**, and it must be specified per element
because the same contrast means different things:

| contrast | means |
|---|---|
| hollow ring = claimed, solid dot = observed | claim vs observation |
| hollow circle = estimated, solid = tabulated | provenance |
| hollow bar = exclusive, solid = non-exclusive | licence exclusivity |
| hollow block = not yet met | target vs achieved |
| hollow/outline = the **base year or reported actual**, filled accent = the forecast year | time provenance |
| hollow = future/current, filled = past | time |
| outline bar = before, filled = after | treatment state |
| **solid square = disclosed, vertically split half-square = partly disclosed**, hollow = not stated | disclosure |
| hollow square = a category not on that column's ordinal scale | off-scale |

### 9.3 Bands and zones

| element | form |
|---|---|
| uncertainty / reference band | hatched or shaded, **dashed edge**, label **above** the band, drawn **over** the data — it visibly occludes points |
| a range, not a series | vertical beige band = a working window or a dead period (`no further studies`); pale pink horizontal band = a duration or a gap |
| homologous ceiling | a `SEED_BROWN` band with a dashed edge, bracketed, labelled with the native value |
| exclusion band | a tinted vertical band marking a range to avoid, tagged `pI区域（避免操作）` / `安全操作区` |

**Overlay order:** bands are drawn **before** the marks they occlude only when they are
background zones; an uncertainty band that must occlude is drawn **after**.
show the occluding case, and 6's band visibly covers points — reproduce that, do not "fix" it.

---

## 10. Geometry: strokes, corners, dashes, opacity

### 10.1 Stroke widths — the measured inventory

 across 400+ primitive calls:

| width | where it is the default |
|---|---|
| **0.8** | box borders, `line()` default, `dot()` rings, `bar()` outlines, `column_icon` |
| **0.7** | header rule under the title, axis rules, major ticks |
| **0.6** | `axes.linewidth` in matplotlib, `frame()`, hairline table grids |
| **0.9** | the crossed-circle's X strokes, table's rule under the header, hatch strokes |
| **1.0** | `arrow()` default |
| **0.5** | minor ticks on a log axis (0.45 in `log_axis`), box-plot whiskers |
| **0.54** | — |
| **0.56** | — |
| **1.4** | `lines.linewidth` in matplotlib — the only stroke this heavy |

**Canonical hairline at illustration scale: 0.5–0.8.** The heavy line is 1.4 and it is
**only** for chart series. A diagram never uses 1.4.

### 10.2 Corners

**Zero radius.** `column_icon` passes `rx="0"` explicitly, and every house diagram confirms it.
The off-family figures break it — rounded corners are the tell. Non-zero radius is the single fastest way to look imported.

### 10.3 Effects

No gradients, no drop shadows, no bevels, no glows, no 3-D, no translucency used as decoration.
The only 3-D in the corpus is an imported render and a defect.

### 10.4 Dashes

| element | pattern |
|---|---|
| a box that is dashed | `stroke-dasharray="3 3"` |
| a dashed arrow or line | `stroke-dasharray="4 3"` |

No other dash pattern is in the code. A reproduction that invents `2 2` or `6 4` is off-family.

### 10.5 Opacity

Use the §7.3 ladder. The two values with special meaning are **0.55** (the header rule) and
**0.75** (column bands).

---

## 11. Type: the scale law and the ramps

### 11.1 The scale law — a REQUIREMENT, not a measurement

> **This law is a REQUIREMENT, and it has never been verified against a delivered figure.** No
> image carries a page-width reference, so neither type size nor the 6.0 pt floor can be measured
> from one. **Absence of a violation is not compliance.**

```
on-page pt = authored_pt × display_width_pt ÷ canvas_width_pt
```

* **Floor: 6.0 pt** `MIN_ONPAGE_PT = 6.0`.
* **Target: 6.5 pt** — a figure at 6.00–6.05 is inside the measuring instrument's ±0.06 pt
 tolerance and cannot be distinguished from a failing one.
* **Typical display width: 455.0 pt** `_TYPICAL_DISPLAY_PT`. The library's measured
 range is **340–471 pt**.
* **Reference anchors:** A4 = 595 × 842 pt; a 16.6 cm text column = 470.55 pt; a 16.11 cm
 figure cap = 456.69 pt; `chart_kit` uses **456.6929133858268 pt** in its own assertion.

 `onpage_pt(font_units, canvas_w=780, display_pt=455.0) = font_units * display_pt /
canvas_w`, and `Canvas.check_scale()` fails the build when the smallest label is under the
floor.

### 11.2 The figure type ramp

 — these are the sizes `schematic.py` and `diagram_kit.py` emit, in **canvas units**.
They are the whole FIGURE ramp; there is no other.

| element | units | face | ink |
|---|---|---|---|
| Titles: figure title | **22** | sans | `INK` |
| kicker | **11** | mono | `MUTED`, tracking `+1.6` |
| section / micro-label | **11** | mono | `MUTED`, tracking `+1.4` |
| box main label | **13** | sans | `INK` |
| box sub-label | **10.5** | mono | `MUTED` |
| axis tick label | **10.5** | mono | `INK_MUTED` |
| axis unit label | **10.5** | mono | `INK_MUTED` |
| legend label | **10.5** | mono | `INK_MUTED` |
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

**The printed size of each, at the three canvas widths the scripts actually use**
(`display_pt = 455`):

| units | 780 units (×0.583) | 940 units (×0.484) | 560 units (×0.813) | 1320 units (×0.345) |
|---|---|---|---|---|
| 22 | 12.83 | 10.65 | 17.88 | 7.58 |
| 13 | 7.58 | 6.29 | 10.56 | 4.48 |
| 12.5 | 7.29 | 6.05 | 10.16 | 4.31 |
| 12 | 7.00 | 5.81 | 9.75 | 4.14 |
| 11.5 | 6.71 | 5.57 | 9.34 | 3.96 |
| 11 | 6.42 | 5.32 | 8.94 | 3.79 |
| 10.5 | **6.13** | **5.08** | 8.53 | **3.62** |

> **Read the bold cells.** At **780 units every ramp size clears the 6.0 pt floor**. At
> **940 units every size below 12.5 fails it**. At **1320 units nothing on the ramp is
> legible**. This is why `TARGET_CANVAS_W = 780` and why the same code comment says a
> 13-unit label at 1320 units prints at 4.5 pt.

**Two knobs, not interchangeable**:

* `type_scale` multiplies the **whole ramp**, preserving the hierarchy exactly. Use when the
 figure has room.
* `min_type` raises **only the runs under the floor**, leaving everything above untouched.
 Use when a uniform raise would push a long label out of its box. It costs some of the size
 hierarchy.

Both default to off, so a figure asking for neither is byte-identical to before.

### 11.3 The document type scale

 `brand.TYPE`, in **points**, for DOCX and print. This is the *document's* scale, not
the figure's — do not use it for canvas text.

| role | pt |
|---|---|
| `display` | 30.0 |
| `h1` | 22.0 |
| `h2` | 16.0 |
| `h3` | 12.0 |
| `body` | 10.5 |
| `body_lg` | 13.0 |
| `caption` | 8.5 |
| `kicker` | 8.0 |
| `numeric` | 9.5 |

`LEADING_BODY = 1.52`; `MEASURE_CHARS = (66, 70)`.

**The conversion between the two ramps** is the scale law, not a mapping table. A figure
authored at 780 units and displayed at 456.69 pt prints a 13-unit label at 7.61 pt — larger
than the document's 10.5 pt body would suggest, which is why figure labels look "big" in the
raster and small on the page.

### 11.4 Italic is a semantic slot

Italic is **not** an emphasis choice. Its slots, observed throughout:

* **taxonomic italics** — species names set in italic serif while company names stay upright
 in the same label: `Trichoderma reesei`, `Komagataella phaffii`, `Aspergillus oryzae`,
 `Kluyveromyces lactis` (the same convention appears in external plates). **Load-bearing;
 omit it and a reader notices immediately.**
* **qualitative outcomes and method notes** — serif italic (mono
 meta → sans measure title → serif-italic outcome).
* **the sub-label of a hub or box** (084 `natural source`; 069's application lists; 068's
 deck).
* **a verdict** inside a timeline's assessment box.

### 11.5 The deck-line device

Distinct from the signature move (**COR-10**): an italic serif **deck line under the title,
set SMALLER than the title** — 068 `Nitrogen in, retained and excreted, under a common feed
and under an amino-acid-supplemented low-protein feed`; 053's explanatory line. Also operates
as an in-figure sub-label at sub-label size. **This device is observed and should be
used; the 1.24× "signature move" is the unverified one (§12.4).**

### 11.6 Weight

**Weight 400 only. There is no bold anywhere in this system.**: no kit emits
`font-weight` except through a `weight=` argument nobody passes.
Importance is carried by the **emphasis ladder**: size → space → one accent colour → italic,
in that order.

---

## 12. Face assignment

### 12.1 The three faces

| Face | Family name | File | Role |
|---|---|---|---|
| **Newsreader** | `Newsreader` | `Newsreader-Regular.ttf`, `Newsreader-Italic.ttf` | body copy, display, captions, notes, pull-quotes |
| **Schibsted Grotesk** | `Schibsted Grotesk` | `SchibstedGrotesk-Regular.ttf`, `-Italic.ttf` | headlines, section titles, box labels, navigation |
| **DM Mono** | `DM Mono` | `DMMono-Light.ttf`, `-Regular.ttf`, `-Medium.ttf` | years, numbers, axis figures, micro-labels, source lines |

 from `brand.py` and `schematic._font_css()`. The bundled Newsreader subset is a
variable-font instance declared as **`Newsreader 16pt`**, so matplotlib resolves it by prefix
match — an exact-match-only lookup silently picks DejaVu Serif.

**Glyph gaps are real.** None of the brand faces carries U+2265 (≥), U+03B5 (ε) or U+2082
(₂). Chrome falls back per character so SVG schematics are fine; **matplotlib does not** — it
draws a missing-glyph box and says nothing. A chart needing one of these must pass a **list**:
`brand.font_stack(kind)` = `[brand face, "DejaVu Sans", "DejaVu Serif", "DejaVu Sans Mono"]`.

### 12.2 Face per figure element — the lookup a successor needs

v1 assigned faces to *roles in a document*. Here is the assignment to *figure elements*.
 — the corpus cannot confirm the face from a raster; this is the requirement.

| element | face |
|---|---|
| chart title | **sans**, larger (`smallest_pt × 1.5` in `chart_kit`) |
| serif title (finance register) | **serif** — 059, 072, 073, 074 |
| kicker | **mono** |
| x/y axis title | **sans** in `chart_kit`; **mono** in `Canvas.linear_axis` — both exist; match the figure |
| tick labels | **mono** |
| value labels | **mono** |
| box main label | **sans** |
| box sub-label | **mono** |
| category labels (company, ingredient, microorganism names, rank ordinals) | **mono** — v1 excluded categories from mono; that was wrong |
| panel letter | **serif** mixed case (`A. …`) in 072, 074, 087; **sans** in-figure (`A`, `B`, `C`, `D`) in 080; lowercase parenthesised `(a)` in 235, 194 |
| captions and notes | **serif italic** |
| source line | **mono** `INK_MUTED` |
| tags | **uppercase mono** |
| table column headers | **mono**, uppercase |
| table row labels | **sans** (column 0, lowercase) in `table()` |
| table cell content | **mono** for every house table |
| numerals | **mono** — *except* facsimile statements, which are **serif** |

### 12.3 Face-per-column discipline

**The rule: mono for every number, unit,
date, accession code and structural metadata; sans for titles, box labels and measure names;
serif italic for qualitative outcomes and method notes; serif roman for prose captions.**

Numbers get one decimal when model-derived and none when the source published an integer
(§25.2), and they are always in the numeral face.

### 12.4 The signature move — a claim, not a rule

An earlier version of this style described "a serif italic phrase set ~1.24× larger than its
surrounding sans" as the single most identifiable element of the style. **That has never been
confirmed: do not cite 1.24× as measured.** Use the deck-line device of §11.5, which is observed
— the same face at *subordinate* size, as a deck line and as in-figure sub-labels.

### 12.5 Ink colours for text

| ink | use |
|---|---|
| `INK` `#000000` | all text in the house style |
| `INK_2` `#3A3A38` | body copy where pure black is too hard; measured in 141 (0.24 %), 159 (0.51 %), 162 (0.64 %), 187 (0.30 %) |
| `INK_MUTED` `#6B6B66` | captions, source lines, metadata, caveats — verified exactly in the corpus |
| `JPM_INK` `#0B2A4A` | **chart** titles, labels and numbers in the finance register — verified exactly |
| white knockout | text inside a filled slate/navy block |

---

## 13. Tracking and micro-labels

### 13.1 Values

> **COR-26.** v1 said letter spacing is 0 everywhere and only uppercase mono labels may carry
> `+0.06 rem`. The code disagrees in both directions.

:

| element | tracking | unit |
|---|---|---|
| figure title (22 units, sans) | **−0.3** | canvas units |
| kicker (11 units, mono) | **+1.6** | canvas units |
| section / micro-label (11 units, mono) | **+1.4** | canvas units |
| body / everything else | **0** | — |

`brand.TRACKING_BODY_PT = 0.0` and `brand.TRACKING_KICKER_REM = 0.06` — the rem
value belongs to the **document** scale, not the canvas scale. `letter-spacing` is scaled with
`type_scale` so tracked micro-labels keep their register when the ramp is raised.

### 13.2 Where letterspacing is used

Uppercase + letterspacing is the **emphasis device for micro-labels**, and the corpus applies
it to more than kickers:

* kickers (§14)
* **panel labels** — 7, 12, 22, 40, 41
* **row headers** — 7, 12, 22, 40, 41
* table column headers
* section labels in the footer stack (§17.2)
* tags (§8.2)

**Never on body text.** A run-level tracking value left set on body text is a defect, not a
choice.

---
## 14. The kicker

### 14.1 Form

Uppercase, letterspaced (`+1.6`), mono, small, in `INK_MUTED`, **on its own line above the
title**. it is emitted at `(40, 46)` in canvas units, size 11.

### 14.2 Grammar: a middot-separated breadcrumb

The kicker is a **path**, not a label. Multiple refs chained with `·` are normal.

| form | example |
|---|---|
| `§`-section reference | `§3.2 OVERALL SCORING TABLE · WEIGHTED TOTAL OUT OF 5.0` |
| two-level section + table | `§4.3.4 TABLE 4-2 · CHASSIS TRAIT CHECKLIST AGAINST CANDIDATE CGMCC STRAINS` |
| chained section refs | `§1.4 VETO RULE (MANDATORY IN THIS REPORT) · §3.1 · §3.4 · §4.1` |
| subject breadcrumb | `MOLECULES & DOSSIERS · INDUSTRIAL ENZYMES · FEED` |
| two-level subject | `B-GLUCAN · APPLICATIONS` |
| subject · architecture | `NRPS · MODULE ARCHITECTURE` |
| subject · concept | `POLYSACCHARIDES · GLYCOSIDIC LINKAGE` |
| misspelled in the image | `SUPERXIDE DISMUTASE · APPLICATIONS` (should be SUPEROXIDE) |
| section path, three levels | `MARKETS · BIOMINING AND BIOREMEDIATION · MECHANISM` |
| numbered section | `SECTION 2.2 — COMPARISON OF TECHNOLOGY ROUTES` |
| taxonomy | `COMPANY LANDSCAPE · LISTED · PROCESS TECHNOLOGY` |
| company · model · source | `GINKGO BIOWORKS · BUSINESS MODEL · FROM THE MAY 2021 INVESTOR PRESENTATION` |
| company · subject | `GINKGO BIOWORKS · CELL ENGINEERING TOOLS` |

The kicker is where the figure's **provenance-by-section** is carried. It is not a title.

### 14.3 The PLATFORM unit band

A fixed three-part kicker naming the module, followed by a **thin horizontal rule**, then the
title. It functions as a section identity band, not a caption.

```
PLATFORM · DOWNSTREAM PROCESSING · OSTEOPONTIN
PLATFORM · DOWNSTREAM PROCESSING · LACTOFERRIN
PLATFORM · DOWNSTREAM PROCESSING · OPN
```

33 (and 24 in a `PLATFORM · DOWNSTREAM PROCESSING · OPN` variant).
**None of these four carries a source line** — see COR-27 and §18.7.

### 14.4 Separator by figure family

The separator is chosen by figure family:
| separator | family |
|---|---|
| `·` middle dot | scientific figures |
| `/` slash | commercial / valuation figures |
| `—` em dash | regulatory figures |

All-caps, mono or sans, grey, on its own line above the title.

### 14.5 Kickers that carry a section number in a table

`TABLE 1 / SECTION 1 - ANALYTICAL FRAMEWORK` —.

### 14.6 Status tag on the kicker line

A status tag set **flush right** on the kicker line: `VERIFIED` printed top-right opposite the
kicker.

### 14.7 Document-first order

In the cosmetic-ingredient figures the kicker is ordered **`DOCUMENT · SUBJECT · SECTION`**:

```
COSMETIC INGREDIENTS · PRO-XYLANE · DEVELOPMENT HISTORY
COSMETIC INGREDIENTS · SK-II PITERA™ · BRAND HISTORY
COSMETIC INGREDIENTS · P&G NICOTINAMIDE · RESEARCH AND COMMERCIALISATION
COSMETIC INGREDIENTS · NOVÉAL / L'ORÉAL
```

Document first, then subject, then section.

### 14.8 Two-line kickers

A kicker may occupy two lines. Chained `§` refs are the usual cause ().

---

## 15. The header stack

### 15.1 The three parts

```
[kicker]            uppercase mono micro-label, optional
[title]             sans (or serif in the finance register), sentence case
[rule]              full-width hairline, 0.7 units, INK at 0.55 opacity
```

 layout: kicker baseline at `y = 46`. If a kicker exists, the title moves to `y = 72`
and the rule to `y = 96`. If no kicker, the title is at `y = 50` and the rule at `y = 74`.
The horizontal margins are 40 units on both sides. `body_top` is set to the y **after** the
rule, and `frame()` defaults its top edge to `body_top − 14`.

### 15.2 The combinations that occur

| combination |
|---|
| kicker + sans title + full-width hairline rule |
| kicker + title with **no** rule |
| **kicker only, no title at all** |
| title only, no kicker |
| title + italic serif deck |
| the PLATFORM band: `PLATFORM · …` + rule + title |

### 15.3 Canonical choices, and the two defects

| figure class | use |
|---|---|
| a **drawn** diagram | kicker **required**; title recommended; rule under the header when the figure is more than one row deep |
| a **chart** | title required; kicker optional; **no rule** under the header (charts open with a title + serif-italic subtitle, never a kicker) |
| a **table figure** | title + a key sentence, no kicker unless the table is numbered |

Two recorded defects to avoid, both in matched pairs:

* **081 lacks the hairline rule under the header that 082 has.** Either 081 is defective or a
 very faint rule was misread. **Treat 081 as defective** and give it the rule.
* 161's `COLUMN 1` occupies the title's slot, so the figure has no title at all. That is a
 structural label, not a title — see §32.8.

### 15.4 The rule under the title

Full text width, ~0.5–0.7 units, `INK` at 0.55. In the code it is one line at
`(40, y) → (w−40, y)`, `stroke-width 0.7`, `opacity 0.55` — that is the canonical form.
Present in 104, 105, 116, 117, 125, 68, 77, 82, 83, 84, 86, 90; **absent in 081** (§15.3).
141 draws exactly one thin `INK` rule between the title block and the timeline body; 187 has
no header rule and lets its gridline grey do the work.

---

## 16. Title and subtitle

### 16.1 Title construction

* **Sentence case**, sans, `INK`, 22 canvas units, tracking **−0.3**, left-aligned at x = 40.
* **`<Subject> — <measure>`** with an **em dash**: `Evolva Holding — gross contribution margin
 by half-year`; `Debut Biotech — disclosed funding by round`.
* A title may carry **a count or a method as a subtitle clause**:
 * `Thirteen strains, eight weighted dimensions` (9)
 * `Milk to purified lactoferrin — nine unit operations, two rows` (33)
 * `Published OPN purification process — IMAC · HIC · IEX` (26)
* A title may carry a **status prefix** (§8.2 i): `ESTIMATED — H&H Group infant formula OPN
 volume and value`.
* A title may carry a **period range**: `Ginkgo Bioworks — revenue and operating result,
 FY2019–FY2024` (256 register).

### 16.2 Title face

> **COR-9.** v1 assigned all headlines to the sans. The corpus has **serif titles in 059, 072,
> 073, 074 — including all three finance figures.**

| face |
|---|
| sans |
| **serif** |

**Rule:** sans is the default. The **finance register uses serif titles** consistently enough
across its own figures (072, 073, 074 all three) to be a register rule rather than a
deviation.

### 16.3 The subtitle / deck

A **serif italic line under the title**, carrying one of two things:

| carries | example |
|---|---|
| the **takeaway** | `The resveratrol pure-play never reached a positive gross profit` |
| the **method and basis** | `Nominal capacity and share of a 134,000 t market (99% covered)`; `Sixty named active-ingredient specialists by ingredient family, SpecialChem 2022` |
| the **basis or unit in parentheses** | `"Casein protein composition" / "(bovine milk casein fractions)"`; `"Cosmetic raw materials by category" / "Share of the formulation system and annual volume"` |
| the **arithmetic** | "3 high, 4 medium, 2 low — the report's own distribution" |

**Set smaller than the title** — this is the deck device (§11.5), not the unverified signature
move (§12.4).

### 16.4 Object sub-labels

A mono sub-label inside the figure naming **the object** rather than the value:

```
TABLE 2 · SUPPLIER SPECIFICATION
5 LAYERS
TARGET 10-20 g/L · 10-20-fold gap from the current 1 g/L titre (Table 1)
```

Mono, uppercase, `INK_MUTED`.

### 16.5 Table numbering

`TABLE N · …` lives **in the kicker**, not in the caption. Forms in use: `TABLE N · …`,
`TABLE 1-1` (a chapter-numbered scheme), `(Table 28)` (a parenthetical cross-reference in body
text or a sub-label). **`Figure N —` and `TABLE N ·` are
different objects and do not share a slot.**

### 16.6 Punctuation

| element | convention |
|---|---|
| subject ↔ subject-matter in a title | **em dash** `—` |
| year ranges | **en dash** `–` without spaces |
| a comma before a period in a title | yes |
| separator inside kickers and source lines | `·` middle dot |
| ranges in data labels | hyphen or en dash, per the source: `USD 16.5-17.6 bn`, `40-45 °C` |
| an in-image caption's number separator | **en dash** in the corpus (numbered with an en dash) versus v1's em dash |

---

## 17. The footer stack

### 17.1 The full order

The corpus's foot, top to bottom. Not every figure carries every part; the **order is fixed**
where parts are present.

```
1  graphic
2  ALL-CAPS section label          (drawn figures)        141, 157, 159, 162
3  caption, serif italic           sentence, not numbered 256, 275, 261
4  italic serif explanatory / method note (1–3 paragraphs)
5  per-symbol or per-marker list   (some figures)         91
6  mono source line
7  blank line
8  status / caveat line            mono, ALL-CAPS keyword + colon + sentence
9  caveat block                    numbered (i)(ii), provenance disclosures
```

### 17.2 The section label

All-caps, letterspaced, one of a small set: `DEVELOPMENT HISTORY`, `READING`, `WHY THE STRAIN
IS NOT REPLICABLE`, `POSITION IN THE PORTFOLIO`. **v1 has no concept of
this element.** Mono, `INK_MUTED`, `+1.4` tracking.

### 17.3 Explanatory blocks and their headings

| heading | boxed? |
|---|---|
| `HOW TO READ THE SHADING` | unboxed |
| `KEY LIMITATION` | **boxed**, hairline border + accent left band |
| `READING` | unboxed |
| `ASSAYS` | unboxed |

Heading = uppercase mono; body = serif or italic serif.

### 17.4 The italic method note

A free-standing **serif italic** note under the figure, often 2–3 paragraphs, carrying method
caveats — **distinct from the mono source line** and **distinct from the caption**. This is the
corpus's actual workhorse and v1 only described the caption.

Frequently **opens with a status word**:
`VERIFIED: …` / `ESTIMATED: …` / `UNVERIFIED: …`.

### 17.5 The status / caveat line

Mono, ALL-CAPS keyword + colon + sentence, **on its own line below the source line, separated
by a blank line**. `ESTIMATED:` in 158, 164, 168, 170; `VERIFIED:` in 165, 175. Semantics
(§8.1): `ESTIMATED` where values were digitised or repositioned from a source figure;
`VERIFIED` where an outside filing confirmed the number. A sentence may name third parties:
`…global nominal vitamin-B3 capacity is put above 150,000 t by Across Biotech (2022)`.

### 17.6 Discrepancy note

A printed note where the document's own numbers do not reconcile: `published shares sum to
100.25%`; `the four printed shares total 99.9%`. **Never silently
normalise a total — print the discrepancy.**

### 17.7 No rule between graphic and footer

In every figure checked, the footer is separated by **whitespace only**. **Do not add a rule
between the graphic and the footer.** The one exception in the corpus is 141, which draws a
single thin `INK` rule between the title block and the timeline body — a *header* rule, not a
footer one.

### 17.8 Length

Notes may be **longer than the figure**: 073 and 074 carry three-paragraph notes blocks. There
is no maximum. §56 records 139 as a defect — a mono source line physically overlapping the
bottom bar — which is a spacing failure, not a length failure.

### 17.9 The caveat block

A separate block under or beside the source line:

* **numbered caveats** — `Two caveats: (i) … (ii) …`
* **a provenance disclosure** — `Right panel is EXTERNALLY sourced and carries no filing in
 this repository … UNVERIFIED`
* **a method note listing assumptions**
* **a long small-type note block explaining exclusions**
* **italic provenance lines**

### 17.10 Footnote reference markers

`(1)` inside a figure; `§6.2` inside a source line. Uppercase/mono per the tag
rule; the marker always resolves to something in the same document.

### 17.11 Footer metric boxes

Cost/scope figures parked at the foot of a roadmap:

```
Est. GRAS Cost: 250K - 500K
Est. NHC Cost: ¥500K-1M
Total R&D: $3-5M
```

Boxed, square corners, hairline border, mono.

---

## 18. The source line

### 18.1 The skeleton

```
Source: <primary source>, <detail> · Retrieved <YYYY-MM-DD>
```

Mono, `INK_MUTED`, 12.5 canvas units, **always bottom-left or centred**.

### 18.2 Where it sits

 `Canvas.source()` places it at `(40, h − 22)`; `chart_kit.source_line()` places it at
axes-fraction `(0.01, −0.01)` with `va="top"`. Both are bottom-left.

### 18.3 The parenthetical provenance note

The line often ends with a parenthetical stating **what was and was not taken from the
source**: `(embedded chart)`, `(segment labels and shares as printed)`..
### 18.4 The provenance verbs — the seven-plus forms

v1 fixed one form. **Seven are in production.** Match the form the figure needs; do not
harmonise.

| # | form | example |
|---|---|---|
| a | canonical | `Source: <source> · Retrieved YYYY-MM-DD` |
| b | **source + bare URL instead of a date** | `Source: Li, H. et al., Foods 2023, 12, 2935 · mdpi.com/2304-8158/12/15/2935` |
| c | **a house imprint instead of a source** | `Source: figure reproduced in the source document (unattributed) · Anthology Desk Research` |
| d | **a DOI as an extra segment** | `… · doi:10.3390/antiox12091675 · Retrieved 2026-09-11` |
| e | **a disclaimer-led notes block with no `Source:` prefix at all** | `ESTIMATED - sell-side forecasts, not independently verified.` followed by 2–3 more paragraphs |
| f | **a multi-paragraph analytical NOTES block**, later paragraphs caveating the document's own inconsistencies | — |
| g | **a per-symbol list followed by a source** | — |

Plus the **redraw / translation / digitisation** family:

| form | example |
|---|---|
| translated and redrawn | `Source: process chart supplied in OPN purification Process.docx, translated and redrawn · Retrieved 2026-09-11` |
| translated from a datasheet | `Source: supplier product specification as supplied in OPN purification Process.docx; translated from the Chinese datasheet · Retrieved 2026-09-11` |
| **redraw naming the source asset and the twin placement** | `Source: redrawn in English from the source schematic schematic3.png (the same figure as image16 in the original report), after <journal> <vol> (<year>) <page> · Retrieved <date>` |
| **digitisation** | `Source: efficiency values read from the source figure (no citation given in the original) · Retrieved 2026-09-11` |
| report-internal table | `Source: <org>, via Report 4 Cosmetic Ingredients Table 7 · Retrieved <date>` |
| external report | `Source: <external report title> · Retrieved <date>` |

**Rule:** the verb tells the reader whether the figure is a **quotation** or a **rebuild**.
`translated and redrawn`, `regenerated in English`, `read from the source figure` and
`as tabulated in this report` are all rebuilds and must say so.

### 18.5 Naming third parties

Name the publisher **verbatim**: `BITOLA CAPITAL`, `MetricsCart`, `Chenrui Capital`, `The
Insight Partners`, `Brachelente, Galli & Cervelli`, `Wang et al.`
139, 140. v1 restricted this to filings; the corpus does it for reports and data vendors too.

### 18.6 Cross-references and multi-source

| form | example |
|---|---|
| internal cross-reference | `as transcribed in Amyris analogs.docx`; `as tabulated in Glanbia_BG.docx` |
| section reference + attribution | `… Research Report §6.2 · Anthology Desk Research` |
| **per-panel sources, numbered** | `Source: panels — …`; multiple sources separated by semicolons |
| **a `second-hand` qualifier** for a re-cited figure | — |
| an archive stamp | `· Retrieved 2026-09-11` |

**Malformed, do not copy:** 161's `Source: SK-II / P&G product communications, via Report
2026-09-11` — the document name is truncated (`Report 4 Cosmetic Ingredients` → `Report`).

### 18.7 Completeness

v1: "A figure missing its source line is incomplete." **Verified absent** on house figures
**26, 27, 31, 33** (the PLATFORM family, which carries kicker + title + rule instead) and
**246**.
absent on every capture**" — is the reliable discriminator for *is this ours*, and these five
are its exceptions. **Rule:** every house figure carries a source line. The PLATFORM family and
246 are defects to be fixed on reissue, recorded in §56.

### 18.8 The retrieval date

The retrieval date is **ISO format** (`Retrieved 2026-09-11`). A reproduction run
that is re-drawing an existing figure **must reuse that figure's original retrieval date, not
today's** — the date records when the source was read, not when the figure was drawn.

---

## 19. Captions live outside the raster

> **COR-8.** v1 required a serif-italic `Figure N — …` caption inside every figure.

**The corpus never carries the number in the image.** The `Figure N —` caption is a DOCX
paragraph under the image. In-image captions, where they exist, are:

| form | example |
|---|---|
| numbered with an **en dash** | `Figure N – …` |
| **no number at all** | `Figure – Preparation, purification and activity verification…` |
| a **full sentence, no number** | `Ginkgo Bioworks LDaaS workflow.`; `Sheet 2.2 of this document: the two columns are its own "comparison of technology routes" table, quoted cell by cell.`; `The months are the proposer's plan, not a schedule commitment …`; `The comparison is the preparing team's own assessment, not a cited fact …` |
| **no in-image caption at all** — the caption is document text | — |

**Rules:**

1. In a DOCX, **do not draw the caption into the figure.** The document prints it.
2. Where an in-image caption is genuinely needed, it is **serif italic, a full sentence, and
 unnumbered**.
3. If a number must appear in-image, use the corpus's **en dash** (numbered with an en dash), not v1's
 em dash, and accept that it will double with the document's caption.
4. `Canvas.caption()` and `Canvas.source()` exist but their own docstrings say they are
 "rarely needed … the host document already prints its own `Figure N — …` paragraph under
 every image, so drawing one here duplicates it on the page."

---

## 20. Axes

### 20.1 Axis side follows orientation

| orientation | scale axis goes | ticks point | numbers sit | unit label |
|---|---|---|---|---|
| **horizontal bars, intervals, Gantt** | **TOP** | **up / outward** | **above** the line | **at the right end of the axis line** |
| **vertical bars, dot plots** | **BOTTOM** | **outward** | below the line | **centred under the axis**, uppercase and letterspaced in the batch-0 form |

The top axis **substitutes for a frame**. A successor who draws a conventional left/bottom
pair on a horizontal-bar figure loses the family resemblance.

Worked unit labels:

```
year
weighted total
homologous ceiling – native glucoamylase, 20-30 g/L
ROYALTY RATE (% OF NET SALES)
TRANSACTION VALUE, RMB, LOG SCALE
WEIGHTED TOTAL (OF 5.0)
ESTIMATED INVESTMENT, RMB MILLION
```

### 20.2 Spine policy

| variant |
|---|
| **left + bottom** hairline, top and right removed |
| **bottom only** — no left spine at all |
| **none at all** |
| left spine with ticks but **no numbers**; bottom spine with no ticks |
| no continuous bottom spine — faint **vertical rules at major ticks** with numbers beneath |

 `chart_kit.new_chart()` hides **top, right and left**, keeps only the bottom spine at
`INK`, `linewidth 0.7`, and disables the grid. `Canvas.linear_axis()` draws one horizontal
rule at `width 0.7`. **No figure in this corpus draws a frame.**

**The bottom spine doubles as the zero rule.** In the two-panel revenue/loss figure the
zero line is a **stronger rule drawn across the panel where the two panels meet** — heavier
than a gridline. See §26.14.

### 20.3 No y-spine

Category names **float** as right-aligned left-hand labels, and y tick numbers (when present)
float with no rule under them., 12(A), 16, 2 (no axis at all — the value is printed
above each bar).

### 20.4 Numbers on ticks versus floating

**UNRESOLVED in v1 and in the corpus.** Axis numbers sit **on** the ticks in 3, 5, 6, 9, 13,
15, 16 and **float with no ticks at all** in 2, 23. Both are deliberate in their own figures.
The applicable test is §20.8.

### 20.5 Unit label placement — the legal positions

| position | form |
|---|---|
| (a) **inside the tick label** | `50%`, `13,000` |
| (b) **a small mono axis caption under or beside the axis** | `million head`, `USD millions`, `protein demand, thousand tonnes per year`, `share of total whey protein` |
| (c) **inside the data label** | `3 g/L`, `USD 3.9 bn`, `USD 600-1,200/kg` |
| (d) **centred under the axis, sentence case, unit in parentheses** | `Method disclosure completeness (%)`; `market size, 2023 (USD million)`; `titre, g/L (log scale)` |
| (e) **centred below the tick-label row** | `Nominal production capacity, tonnes per year`; `Market size, USD million (bubble area proportional)`; `USD per kg (log scale)` |
| (f) **rotated 90° outside the y tick numbers** | `USD billion` |
| (g) **a band with a middle dot and a full stop** — the axis-less horizontal-bar form | `global production capacity, 2023 · 10,000 tons` |
| (h) **y unit above the top of the axis, outside the data area** | `copper grade (%)`, `USD per tonne`, `Price differential` |

> **M30 is a genuine self-conflict in the corpus:** (e) and (f) are the same job done two ways
> — 158/164/168 centre the axis title below, 177/178 rotate it. **Rule:** horizontal
> orientation takes (d)/(e)/(g); vertical orientation takes (f) or (h). Pick by orientation and
> be consistent within a document.

**Never a bare "Value".** Every axis title states unit and period: `USD m, FY2023–FY2030`.

### 20.6 Rotated y-axis unit label

Set vertically, `−90°`, far left, mono —.
### 20.7 When an axis may go unlabelled

**089** draws a y-spine, ticks and **no numbers**, because every value is printed on its bar.
**087** panel A drops ticks entirely (log labels, no ticks). **166, 167, 115, 127, 130, 131,
137–140** have no axis line and no ticks at all.

**Rule:** an axis may omit its numbers **when and only when every mark on that axis carries
its own printed value**. It may omit its line and ticks when the category label and the value
label carry everything. It may never omit both the numbers and the value labels.

### 20.8 Tick marks

| form |
|---|
| **short, outward, hairline, bottom axis only** |
| **no tick marks at all** |
| **tick labels with no ticks** |
| **minor ticks between log decades** |
| **no tick on the category axis of a bar chart** |

 when ticks are drawn: `chart_kit` uses `length=3, width=0.6`;
`linear_axis` uses `tick_len=5, width=0.7` major and `0.45`/`0.55×len` minor. **Both are
canonical for their side.** Direction is **outward**, never inward.

**Decision rule:** a chart whose marks carry printed values gets **no ticks**; a chart where a
reader must locate a position on the axis gets **outward hairline ticks**. If in doubt, follow
the nearest precedent figure.

### 20.9 Secondary labels under ticks

Deal counts beneath the year labels as `1 deal`, `2 deals`. Mono, `INK_MUTED`,
one row below the tick row.

---

## 21. Gridlines

### 21.1 The corrected rule

> **COR-1.** v1 permitted faint **horizontal** `RULE_SOFT` lines only, and only "where a
> reader genuinely needs to read a value off an axis". The corpus does neither.

**The rule:**

1. **A gridline runs perpendicular to the value axis.** A horizontal-bar chart (value axis on
 top) gets **vertical** gridlines dropping from the x ticks. A vertical-bar or line chart
 gets **horizontal** gridlines at the y ticks.
2. **Colour is `RULE_SOFT #D8D3C4`**, or a knockout in the canvas colour (§21.5).
3. **Weight is 0.5–0.6** — lighter than any structural rule.
4. The **trigger is the form, not a judgement about the reader**: end-labelled bar charts get
 **no grid**; time-series and positioned-value charts get gridlines at **every** tick.

### 21.2 Vertical gridlines

On horizontal-orientation
charts, vertical rules rise from each major x tick through the plot.

### 21.3 Dotted gridlines

Faint **dotted** horizontal gridlines on the vertical grouped-bar chart —. Dotted is
**not** `RULE_SOFT` at 10 %. Pattern: a fine dot run, `RULE_SOFT` or lighter.

### 21.4 The trigger, as actually applied

**The rule:** faint horizontal
`RULE_SOFT` rules on time-series line charts; **no grid at all** on end-labelled bar charts.

### 21.5 Knocked-out gridlines

Two reads described "faint **white** horizontal gridlines" on **235** and **237** — i.e.
gridlines knocked out in the canvas colour rather than drawn in `RULE_SOFT`. **UNVERIFIED**:
the 160×160 sample is blind to 1 px rules and only one vision read reported it. If
implementing, knock the rule out of a filled element rather than drawing white on paper.

---

## 22. Value labels

### 22.1 The general rule

> The value is printed **above or beside the mark, never on the axis**, and the **placement
> is per-row, not fixed** — it dodges the glyph it belongs to.

v1 said "direct-label the series at the end of the line or bar"; that gets the idea, not the
geometry. The geometry is below.

Mono, `INK` (or the body text colour), no leader, no padding box, no arrowhead.

### 22.2 Horizontal bars

**Value immediately to the right of the bar end**, one gap-width past the cap, vertically
centred on the bar, in `INK`. The same value is **not** repeated on the axis..
 in `chart_kit.bars()` the vertical-bar equivalent is `ha="center", va="bottom"` at
the bar's top centre.

### 22.3 Vertical bars and stacks

| form |
|---|
| vertical bar |
| stacked bar |
| negative bar |

### 22.4 In-bar mono annotation

Right-aligned **inside** the bar: `near-complete method` set inside the `MEADOW` bar. Figure
059. Mono, the ink that contrasts with the fill.

### 22.5 Per-bar annotation stack

Line 1 the metrics (`6 % CAGR · CRn high · …`), line 2 an **italic serif** application list.
Both above or below the bar, **not inside it**.

### 22.6 Jitter and horizontal repetition

* **Jitter within a categorical lane** to stop points overlapping —.
* **Repeating same-period events horizontally instead of stacking them** — 1, 6. Do not stack
 two events at the same date vertically; spread them along the lane.

### 22.7 Multi-line category labels

`"China\nswine"` and multi-line treatment labels under bars. Leading =
the axis leading, not the body leading.

### 22.8 Rotated data labels

Rotated **90°** above points or bars for a dense series.

### 22.9 Floating value annotation with no bar behind it

`+$0.18` above a step, with no mark under it.

### 22.10 Two values per bar

Both mono, the
share on a second line or a second column, consistently.

### 22.11 Two quantities in one label

`Gold · 0.5 kt 18.8bn €` — the secondary quantity rides **in the category label** while the
plotted axis carries the primary one. Separator: two spaces or a middot, as the
original.

### 22.12 The `total` prefix

On a stack, the total at the bar end is prefixed with a **lowercase** `total`:
`total 6,879.0`, `total 54,184`.

### 22.13 Trend labels with a connector glyph

A direct label carrying **opening → closing**:

```
Gross margin 61.9 % -> 60.6 %
Net margin 6.1 % -> –0.4 %
68.2 ▾ 56.8
```

The glyph in 264/265 is **some** small directional mark between the two
values; its shape is **UNRESOLVED** (two reads rendered it `□` and `▾`). Use `▾` for a fall,
`▴` for a rise, or the literal `->` where the corpus does.

### 22.14 Multi-line label blocks

Value → holding → date → event name, stacked over **four lines**:
`1,780.3m shares @ $10.00` etc. Scenario names wrapped over **three lines** plus a
parenthetical condition. Left-aligned on the mark.

---

## 23. Legends and keys

### 23.1 The forms

> **COR-19.** v1 made the legend a collision fallback. It is a first-class element.

| form | position | swatch |
|---|---|---|
| boxless key, top-right of the plot area | top-right | one swatch per glyph — line+dot = "range", dot = "median" |
| key block, **bottom-left** | bottom-left | a square swatch |
| **swatch row directly under the title** | under the title | small squares, filled navy / filled bronze / hollow outline, each followed by its label, **no box, no border, no fill** |
| two-item version of the above | top-left | — |
| framed box, top-left | top-left | small filled squares in series order, untitled |
| titled, semi-transparent-framed | — | `Production Organism` |
| right-hand legend | right | three items |
| top-left legend of small colour squares with sans labels | top-left | — |
| **boxed** legend with a border — used only where three series collide | — |
**"Legends sit top-right or right, never below."**

### 23.2 Swatch construction

 `legend()`: swatch = a filled rect **11 wide × 7.7 high** (`swatch×0.7`), label at
`swatch + 7`, `row_gap = 18`, label 10.5 mono `INK_MUTED`, no frame.

### 23.3 The top-right symbol KEY

Inline, in sans, **no box**:

```
filled dot = Vland's PE; hollow ring = the broker's own peer average
```

### 23.4 The header as legend

The series name is set once **at the left of its row** (2) or **above its lane**, so no legend object exists at all. This is the preferred form for lane charts.

### 23.5 Legend text coloured to match its swatch

The words `dot` / `ring` set in the hue they describe., `[verify]` in the
original report.

### 23.6 The legend continued as an explanatory LIST

The most unusual legend idiom in the corpus and **load-bearing**: it is how the figure says
what it **cannot** plot.

A legend that continues below the plot, **separated by a horizontal rule**, with rows for
items that have **no bar at all**:

```
not feasible – requires the bacteria-specific lanthionine modification system
546 U/mL – a different unit
not reported – possibly feasible
```

The symbol (X / circle / square) is **carried into the list**.

### 23.7 Key blocks as a first-class form

A small ruled block at the foot of the figure, titled:

| title |
|---|
| `KEY` |
| `LEGEND` |
| `NOTES` |
| `HOW TO READ THE FILL` |
| `SOLID BOX = PROCESS STEP / DASHED BOX = DECISION GATE` |

### 23.8 The state-key line

A one-line key instead of a legend:

```
outline = before LF treatment; filled = after LF treatment
filled circle = peer-reviewed (3 of 11); open circle = commercial promotion
```

136A. Sits under the plot, mono.

### 23.9 Inline axis-embedded series label

`pigs served (right axis)` printed **inside the plot** instead of a legend.

### 23.10 Boxed legend

A legend with a visible border, used only where three series collide (LiP / 2 % hydroquinone /
placebo).

### 23.11 Shape key for molecules and markers

`square = GlcNAc`, `circle = Man`, `triangle = Gal`, with the line **`identity is the shape`**.
### 23.12 Right-end series labels in the series' own colour

Series name + last value written at the right end of the line, **in the series' own colour**,
replacing the legend entirely.

 `chart_kit.lines()` reserves **30 % x-headroom** for these labels and enforces a
minimum gap of `7.5 %` of the value span between adjacent end labels, pushing colliding ones
apart. **Reproduce that headroom** — it is why end-labelled line charts have empty space on
the right.

### 23.13 The key as a sentence under the title

The hue is **named in words**, in prose, with no swatch and no legend box:

```
bronze = Spiber
sky = muconic acid intermediate
solid = built, hatched sky = stated target
```

Also: `filled = disclosed, half = partial, outline = not
stated · right column = parameter count`.

### 23.14 Legends that explain a MARK, not a colour

A legend entry may name a marker class rather than a fill: `Dated valuation milestone`;
`range / median`; `Phase Activity / Regulatory Filing Window / Key Milestone`;
`initial consideration / deferred / contingent`. This is the corpus's answer to markers
that have no colour of their own.

---

## 24. Axis forms

### 24.1 Linear

 `linear_axis(x0, x1, y, ticks, label, tick_len=5, minor=0)`: one rule at `width 0.7`;
major ticks `5` long at `0.7`; minor ticks `0.55 × tick_len` at `0.5`; tick labels at
`y + tick_len + 11`, size 10.5 mono `INK_MUTED`, centred; unit label at `y + tick_len + 26`.

### 24.2 Log axes

| feature | rule |
|---|---|
| where used | price ladders and any range spanning orders of magnitude |
| **minor ticks between decades** | yes — 168, 96, 103, 215 |
| decade ticks only, **no minor ticks** | 209, 215, 219, 222, 225 |
| **scale named in the axis title** | `Price (USD / kg, log scale)`; `titre, g/L (log scale)`; `USD per kg (log scale)` |
| **major labels with K/M suffixes, never full digits** | `100K / 1M / 10M / 100M`; `3k / 10k / 50k / 200k / 1.5M` |
| — | `10 / 100 / 1,000 / 10,000 / 100,000` — full digits where the source printed them |
| — | `0.01 / 0.1 / 1 / 10` |
| a **thin space before the unit** | `$100 M / $1 B / $10 B` |
| **log-log** | one panel only |

 `log_axis(x0, x1, y, lo, hi, ticks, minor=True, label="")`: axis `0.7`; minor ticks
`3` long at `0.45`; major `5` at `0.7`; labels at `y+16`; unit at `y+31`;
`_tick_label()` renders `%gM` above 1e6 and `%gk` above 1000.

### 24.3 The dashed `$0` cap on a log axis

A bar starting at **$0 on a log axis** gets a **dashed left cap** instead of a solid end —
because $0 has no position on a log scale. Log-ness itself is signalled **only in
the unit label** (`LOG SCALE`, `LOG SCALE, MG/L`) with **no decade ticks or break marks
drawn**. Where a log axis does carry decade labels, use §24.2.

### 24.4 Threshold, median and reference rules

| element | form |
|---|---|
| dashed vertical rule at a threshold or median | dashed vertical at the value |
| **two vertical rules in `JPM_SKY`** with small mono labels at the top of the plot, used to **colour-group the bars** — `JPM_BRONZE` above the upper rule, `JPM_INK` between, `JPM_SLATE` below | labels `200 USD/kg`, `1,200 USD/kg` |
| solid vertical **burnt-orange** rule + orange text | `the skin's resident pH 5.5` |
| dashed black horizontal threshold lines | — |
| a dashed horizontal rule at the **control bar's height**, to compare other bars against | — |
| a horizontal rule at the **baseline value** in a bridge | — |
| **dotted** vertical rule marking a **policy date** | `September 2026` |
| dashed vertical rules as **lane boundaries** | — |

Rule colour: `RULE_SOFT` for a background threshold, the accent for a semantic one, `JPM_SKY`
for the colour-group thresholds.

### 24.5 Break axis and the paired-panel share rule

v1 listed a break-axis chart; the corpus does not silently truncate. **When a category dwarfs
the rest, the figure is split into two panels with a shared header rather than a broken axis**
—. Where a break *is* drawn, draw it explicitly.

### 24.6 The unit band / second-measure header

When a **second measure is printed but not plotted**, it becomes a **header line above the
category column**: `mass in kilotons` over the labels, while the axis is billion EUR. Figure
196. This is the sanctioned workaround for the dual-axis ban.

---

## 25. Numerals

### 25.1 Formats — the most repeated detail in the corpus

Mono for every numeral (except facsimiles, §44). Right-aligned in table cells; left-aligned in
charts.

| feature | rule | examples |
|---|---|---|
| **thousands separators, always** | `16,283.0`, `8,950`, `40,000`, `7,129`, `4,360`, `13,926`, `3,739` | — |
| **one decimal for model-derived** shares and currency | `44.4%`, `38.1%`, `65.5%`, `37.1%`, `6,879.0`, `4,533.0`, `68.2 %` | — |
| **integers for published** shares | `80%`, `33%` | — |
| **trailing `.0` on tonnage** | `12,230.0 kt` | — |
| **currency: prefix + unit + scale** | `USD 761.00/kg`, `USD 214.0m`, `18.8bn €`, `~USD 500/kg`, `USD 3.9 bn`, `USD 600-1,200/kg` | — |
| **lowercase magnitude suffixes in prose labels, spelled out in the axis title — the two are NOT harmonised** | `$17.80bn` / `1,780.3m shares @ $10.00` in the label vs `USD billion` in the axis | 250, 251 |
| **thresholds with `≥` / `≤` / `<`** | `≥90%`, `≤78 °C`, `Cu < 0.5 wt%` | — |
| **approximation with `~`** | `~96% Au recovery`, `~200 days` | — |
| **hyphenated ranges** | `40-45 °C`, `pH 1.2-1.8`, `6-10 days`, `30-50 kDa` | — |
| **en dash for currency ranges** | `USD 16.5-17.6 bn` | — |
| **explicit `+` / `-` on waterfall steps** | `+55`, `+$0.18` | — |
| no space before `%`; **a space before other units** | `65.5%` vs `50 µm`, `0.7 MPa` | — |

 `_num()` renders `%gM` above 1e6, `%gk` above 1000, `%g` below.

> **`≥`, `≤` and subscripts are not in the brand subsets.** A chart needing them must pass
> `brand.font_stack("mono")` as a **list**, not a single family — §12.1.

### 25.2 The published-vs-model split, stated as a rule

> **Integers for published shares; one decimal for model-derived shares.**

This is the corpus's only reliable signal of provenance in the numerals themselves, and it is
enforced consistently across.
### 25.3 Deltas and multipliers

| form | example |
|---|---|
| a signed delta above a bar | `+55` |
| a percentage change with a direction word | `–98 % from the October 2021 peak` |
| a percentage change alone | `–99.6 %` |
| a multiplier | `50x` |
| a **ratio annotation as a multiplier** | `×1.85`, `×1.05`, `×2.77`, and the words `single value` where only one source exists |

### 25.4 Calculation blocks

A mono arithmetic block beneath a chart: row-labelled (`gain`, `feed`, …), using `+ - × =`,
**aligned in columns**, sitting under each panel.

### 25.5 Restatement marking

| element | form |
|---|---|
| an `R` suffix on the tick | `2021 R` |
| a `*R*` explanation in the source line | — |
| a hatch over the restated part of a bar, plus a callout naming it | — |

### 25.6 `_tick_label` suffix rule

: values `≥ 1e6` → `%gM`; `≥ 1000` → `%gk`; else `%g`. So `1000000` prints as `1M`, not
`1,000,000`.

---

## 26. Chart forms

The form list is **the corpus's**, not v1's. Prefer one of these to inventing a shape.

### 26.1 Waterfall / bridge
**The signature financial form**, and its construction is **inconsistent across the corpus** —
v1 named the form and gave no construction. Three variants exist:

| variant | connector |
|---|---|
| solid step connectors | solid |
| **dashed** connectors | dashed |
| **no connectors at all** | none |

Common to all three: totals grounded at zero, intermediate steps floating; **colour keyed to
category (measured / estimated / cost) rather than to sign**; a hatched bar for a subtraction;
explicit `+` / `-` on every step.

 `chart_kit.waterfall()` is the fourth variant and the one new work should use: bars
`width 0.6`, `edgecolor` = `JPM_INK` (finance) or `INK`, fill = `JPM_BRONZE` for a positive
delta and **`ROSE` for a negative**, signed value label above, connector a `0.5`-wide
`INK_MUTED` line across `±0.42` of the bar width.

### 26.2 Range / dumbbell / median rows
Two related forms; v1's form list has neither.

**Form A — the range with T-caps.** A horizontal line with **vertical T-caps at both ends**,
plus a **solid dot for the median sitting exactly on the line**. Values placed above or below
per row to avoid the glyph. Legend: line+dot = "range", dot = "median", boxless, top-right.
**Form B — the dumbbell.** A hairline connector between two endpoints; **filled dot = the
subject, hollow ring = the comparator**; values printed at **both** ends. Used on a log axis
(087 panel A) and a linear one (074 panel B).

**Form C — range-and-median rows.** Each row a horizontal line spanning a range with a filled
dot at the median; **opening, closing and median values all printed**; a `range` / `median`
marker legend. §26.18 is its 2-panel variant.

### 26.3 Bars

Flat fill, **no outline**, square corners. `chart_kit.bars()`: `width=0.62`,
`edgecolor=INK`, `linewidth=0.6` — the code draws an outline that the corpus's delivered bars
do not show at raster scale; **reproduce the corpus: no visible outline**.

**Sorted descending** — 101, 102, 110, 113, 115, 127, 130, 131, 137, 138, 140. **Exception:**
139 is **not** sorted, and that is a recorded defect (§56), not a convention.

### 26.4 The one-bar highlight

> **-adjacent and consistent across the corpus.** Exactly **one** bar or dot takes a
> second hue — the **subject** of the figure — with the rest of the field in the primary ink.

| what is highlighted | hue |
|---|---|
| top supplier | `JPM_BRONZE` |
| latest round | `JPM_BRONZE` |
| top family | `JPM_BRONZE` |
| top ten ranks | `JPM_BRONZE` |
| latest half-year | `JPM_BRONZE` |
| the one company keyed by a sentence (Spiber) | `JPM_BRONZE` |
| peak year / top family | brown |
| the subject or the largest tier | brown |
| the amino acid the section is about (methionine) | a highlighted bar |
| the one case that matters against neutral context | `MEADOW` bar on one row, `SEED_BROWN` on the rest |

**"Brown = the one that matters" is a real convention and v1 never stated it.** Note 139 breaks
it (sky blue marks the residual instead), which is a defect.

### 26.5 Direct-labelled scatter
Label text **in the same hue as its marker**; vertical range whiskers for a price range.
### 26.6 Unit / waffle chart

One small square per observation; an **empty grey-outlined square = not screened**; the integer
count printed to the right of each row; total at the top. Not in v1's form
list.

### 26.7 Discrete block-array rating

**Three stacked rectangles filled = "high"; two filled + one hollow = "medium"** — used instead
of stars, dots or a numeric score, and the **words, not the count, name the level**
("extremely high risk"). Not in v1's form list.

### 26.8 Hybrid chart + aligned table

A scatter on the left whose rows **visually align** with a table on the right, **with no drawn
rules between them**.

### 26.9 Combo and dual axis
> **COR-15.** v1 forbade dual axes. 123 (navy bars + a copper line, revenue vs volume) and 237
> (bars left, a reduction factor on a right axis in a second hue) both ship one.

**Rule:** a second axis is permitted; the right-hand series **must be named inline** (§23.9)
or in a sentence key, because there is no legend room. Bars navy + line copper in 123; 237 uses
a brick-red line on the right.

### 26.10 Axis-less bar geometry

No spines, no ticks, no gridlines. **Bar thickness to gap ≈ 1.5: 1.** Mono value label
immediately right of the bar end.

### 26.11 Bubble / halo mark

A light disc whose **area** is proportional to the value, with a **small solid `JPM_INK` dot
at its centre**; halo in the light tint (`#B1DAEE` ≈ `JPM_SKY` at 0.88); value label right of
the dot; **no connecting line**; category names on the left; **no left spine**.
Axis title: `Market size, USD million (bubble area proportional)`.

### 26.12 Rank list plus staircase

Mono ordinal + name right-aligned against a **stepped diagonal**; dots at each rank joined by
thin grey **orthogonal (vertical-then-horizontal) segments ascending bottom-left to
top-right**; top decile in `JPM_BRONZE`, the rest in `JPM_INK`; no axes, no ticks.
Reproduce the **positions** — 167 prints rank ordinals but no counts, so the metric cannot be
recomputed.

### 26.13 Grouped bars
Bars **inside a group touch (zero gap)**; groups separated by about a bar width. A **top-left
legend of small colour squares with sans labels**.

> **COR-19 instance:** 187 uses a legend with three series and **no label collision**, which
> v1 forbade. Reproduce the legend.

### 26.14 Negative values

| element |
|---|
| a **distinct `JPM_INK` rule at 0 %**, visually **heavier than a gridline** |
| negatives hanging **below** the zero line |
| labels on the **far side** of the zero line |
| a shared zero rule across two panels, drawn where they meet |

### 26.15 Area and line mechanics

| element | rule |
|---|---|
| endpoint markers (filled circles) | **only at the first and last point**, not on every vertex |
| y-axis unit | rotated 90° |
| x-axis | bare years, no "year" unit |
| CAGR | floating mono text in the plot area, **no leader line, no box** |
| endpoint values | floating mono labels — **below the first marker, above the last** |
| area fill | the series hue at ≈13 % alpha (§7.3) |
| gridlines | at every y tick |

 `chart_kit.lines()`: `linewidth 1.4` — **the only 1.4 stroke in the system.**

### 26.16 Event plot

Markers on a **date axis**, **staggered vertically** to stop label collision; **no y-axis, no
y label, no ticks, no grid**.

### 26.17 Formula strip

Boxes joined by `×` and `=` operator glyphs, each term carrying a **status micro-label beneath
it** (`Increasing` / `Decreasing` / `Likely Flat or Decreasing`) — a business-model identity
written as a diagram, and inverted for customer cost.

### 26.18 Range map on a numeric axis

Two stacked panels lettered `A` / `B`, each a **horizontal numeric axis carrying range bars**
whose end values are printed as range text (`85-90 %`, `3k-10k Da`), with a **right-hand
description column** of activity + applications. A log axis here is ticked
`3k / 10k / 50k / 200k / 1.5M`.

### 26.19 Category lanes in a scatter

Five labelled horizontal lanes with **dashed boundary rules**, a **count annotation per lane**
(`Category A early-stage chassis - 6`), an explicit **`not on this axis`** note for excluded
cases, and two dashed reference rules with annotations.

### 26.20 Faceted small multiples

3 rows × 5 criteria, score 1–5 printed above every bar, **not a shared grouped axis**.
Row headers act as the legend (§23.4).

### 26.21 Box plot

Present in the composite 219/225 — the only one in the corpus, and absent from v1's form list
entirely. Whiskers at 0.5, box hairline, no fill.

---

## 27. Panels

### 27.1 Division by whitespace only

**Panels are divided by whitespace only — no rule, no gap line, no border.**
106, 113, 115, 120, 121, 124, 126, 129, 136. Do not draw a divider.

### 27.2 Layout

Both layouts are used with **no stated preference**:

| layout |
|---|
| **side by side** |
| **stacked (A above B)** |
| side-by-side with **independent y-scales** |
| side-by-side with **different orientations** — grouped vertical bars left, grouped horizontal bars right |

### 27.3 The summary line between panels

A line carrying the arithmetic that links two panels: `3 high, 4 medium, 2 low — the report's
own distribution`. Sits **between** the panels, on the whitespace gutter.

### 27.4 Three-band composition

`intro / grid / routes` treated as panels **with no labels** —; and two logical rows
connected by a direction marker — 26, 33. Panels do not have to be labelled to be panels.

### 27.5 Stripling by whitespace

Panel and row striping is by **whitespace only**, with phase labels attached to **bar groups**
rather than to an axis.

### 27.6 Panel labels

| form | face |
|---|---|
| `PANEL A · <subject> · <section ref>` / `PANEL B · <subject>` — uppercase mono, doubling as the panel's kicker | mono |
| `A. Average daily gain` / `B. Gain efficiency (G:F)` — **part of the panel title**, serif mixed case | serif |
| in-figure panel identifiers `A`, `B`, `C`, `D` | sans |
| **lowercase letter in parentheses**, `(a)`, in a small **paper-filled hairline box** at the top-left of a plate | serif |

**Rule:** pick by context — a labelled panel in a two-panel comparison uses `A.`/`B.` as part
of its title; a composite plate uses `(a)`, `(b)` in a boxed corner label.

### 27.7 Furniture across panels

| case | rule |
|---|---|
| **shared header, shared source line** | always |
| panels measure **different things** | **per-panel titles** |
| panels are **two halves of one measure** | **shared title** |
| the x-axis title appears **once**, under the lower panel | — |
| notes | **per-panel is permitted** — `Panel A: … Panel B: …` |

> **COR-18.** v1 required "one shared source line"; the corpus shares the source line but uses
> **per-panel titles** wherever the panels measure different quantities.

### 27.8 Row alignment across paired panels

Categories listed in the **same order** in both panels so the eye reads across.
129.

### 27.9 Small-multiple headers

Small mono panel headers over each sub-panel: `Titre`, `Glycosylation`, `Process time`. Figure
96.

### 27.10 Density maximum

The corpus's densest figure: **3 stacked horizontal panels + a 4-row key + a two-column source
footer on one canvas** —. A six-panel lettered composite, roughly 45 % chart / 20 %
diagram / 35 % table by area, with heavy panel borders — 219/225. These define the ceiling; v1's
"Do not crowd" is not a rule, it is an aspiration (§2 COR-29).

### 27.11 Composite dashboards

One shared title (`PROTEIN-BASED MATERIALS` kicker + `Price, cost and market`), six lettered
panels `a`–`f` mixing a box plot, a cost flow, a log-log line, strategy matrices, a text table
and a stacked column.

---

## 28. Uncertainty and ranges

### 28.1 Bands

Light shaded bands mean **a range, not a series**: a vertical beige band = a working window
 or a dead period `no further studies` (136A); a pale pink horizontal band = a duration or
a gap. v1 gave `SEED_BROWN` the role "bands, baselines, context" and no meaning.

### 28.2 Overlay order

A band meant as a **background zone** is drawn before the marks. A band meant as an
**uncertainty zone that occludes** — a dashed edge, label above, drawn **over** the data — is
drawn after, and it **visibly occludes points**.

### 28.3 The uncertainty gap — state it, do not invent error bars

> **There is no uncertainty element in this style.** No error bars, no
> confidence bands, no shaded envelope, no `n=`, no whiskers (except the single box plot inside
> 219/225), no dashed projection. **Every range is prose in a micro-label**: `40-45 °C`,
> `pH 1.2-1.8`, `~200 days`, `up to 96% yield`, `below USD 3.00/kg`, `30-50 kDa MWCO`."

**Rule:**

* **Do not add error bars, confidence bands, shaded envelopes, `n=` or whiskers.** A successor
 inventing them would be off-style.
* **Do not drop the ± caveat.** Ranges live as **prose micro-labels** — mono, in the axis
 label, the category label, the condition box (§35.6), or the caveat block.
* A figure may carry **no numeric scale at all** if it declares itself schematic (§37).

### 28.4 Exclusion bands

A tinted vertical band marking a range to avoid, with a text tag `pI区域（避免操作）` /
`安全操作区`.

---
## 29. The box

This section is the single most consequential omission in v1. The accent edge bar is the most
repeated diagram device in the corpus — every process box
of 068, the root nodes of 081/082, the layer boxes and limitation box of 088 — and v1 contains
no words for it.

### 29.1 The accent edge bar

**A thick accent-coloured bar flush on the LEFT INSIDE edge of a box, over a thin black hairline
border.**

| property | value |
|---|---|
| bar width | **3 canvas units** |
| at 2400 px | 3 × (2400 / 780) = **9.2 px** |
| measured on the raster | **8–10 px at 2400 px canvas** |

> **The code constant and the raster estimate agree.** This is the one place in this document
> where a raster reading is confirmed by a code constant, and it is worth stating:
> readings are reliable for *which device*, never for *what value* — except here, where the code
> closes the loop.

**The bar is a stroke on one edge, not a fill.** A successor who fills the whole box in the
accent (as v1's "no more than one accent hue of fill" implies) produces a different device.

Figures: 4 (`CLAY`), 11 (`CLAY`), 14 (`MEADOW`/`CLAY`), 18 (`CLAY`/`MEADOW`), 19 (`CLAY`), 20
(`CLAY`), 26 (olive), 27 (`CLAY`), 33 (olive), 68 (all four process boxes, `MOSS`), 81/82 (root
node only), 88 (layer boxes + limitation box).
### 29.2 The accent edge is on EVERY node

> **COR-22.** v1 §8.1 said "One accent marks **the step that matters**". The corpus applies the
> accent edge **uniformly to every node** and uses **fill and label** for emphasis instead.
>A figure that accents only one box is off-family.

### 29.3 Placement varies by orientation

| orientation | edge |
|---|---|
| vertical stack of boxes | **left** |
| header of a horizontal three-stage mechanism | **top** |
| container boxes | **top band across the whole box width** |
| unit operations in a two-column flow | **top** |
| "compatible application" in a matrix | **left** |

 `Canvas.box(accent_edge="top")` emits `<rect width="{w}" height="3">` at the box top —
the same 3-unit thickness, rotated.

### 29.4 Borderless flat fills

> **COR-7.** v1 said boxes have "thin black borders".
> A/T/C module blocks are flat-filled `MEADOW`, the terminal Te domain flat-filled tan, zero
> border on any block.

**Rule:** there are three box classes, and they are not interchangeable:

| class | border | fill | edge bar |
|---|---|---|---|
| **standard** | hairline `INK` 0.8 | none / canvas | accent left or top |
| **flat block** | **none** | flat accent or neutral | none |
| **container** | hairline `INK`, dashed when optional | tinted band or none | accent top band |

### 29.5 Node geometry

| shape | used for |
|---|---|
| **rectangle** | process steps, data, containers, unit operations |
| **hairline circle with text inside** | assembled modules joined by straight arrows |
| no start/end terminators in the in-house figures | — |

### 29.6 Computed and optional steps

| state | border |
|---|---|
| process step | **solid** |
| decision gate | **dashed** |
| derived / computed step | **dashed** |
| optional | **dashed**, sometimes inside a dashed container labelled `OPTIONAL` |
| planned | **dashed** |
| unavailable parent | **dashed** |
| discarded / side stream | **dashed**, no edge bar |

 dash pattern `3 3` for boxes.

### 29.7 Ink text and knockout

* Navy is used for **body text inside boxes**, for **all box outlines**, and for axis lines —
v1 assigned `INK` to "all text, all rules"; these are
 unrecorded exceptions.
* **Slate fills carry white knockout text** —.

### 29.8 Hue as a box category code

Each box in a route diagram takes its own **border and text hue** (light blue / navy / brown)
to code a **feedstock class**, **with no legend explaining it**. Four hues in one
diagram. Record it; do not "fix" it by adding a legend, because the original has none.

### 29.9 Box fill conventions

| convention |
|---|
| unfilled white interior + hairline black outline |
| fill equal to the canvas, so the box reads as outline only |
| a **pale tinted band behind a whole process column** (`#D8D8C0`) |

### 29.10 Two-line box label hierarchy

Inside each box: a **small uppercase role line**, above or below a **larger name**:

```
biological fermentation / L-Lysine
petro-based co-monomer / Adipic acid
```

The `box()` primitive does the same job with `label` (13 sans `INK`) plus
`sub` (10.5 mono `MUTED`) at `+19` vertical offset — use the primitive, and put the **role**
in `sub` and the **name** in `label`.

---

## 30. Arrows

### 30.1 The corrected rule — two head forms coexist

> **COR-2.** v1: "thin, with a **small solid head**."

| head form | used on |
|---|---|
| **open-V chevron** | accent-coloured flow: shafts that carry the accent hue |
| **open-V chevron** | timeline leaders |
| **solid filled triangle** | 76; 191, 198, 221, 227, 229, 230; and the non-house 030 |
| **no head at all** — dot-terminated | relationship connectors |

**Rule: choose the head from the shaft's colour.**

* shaft in the **accent hue** → **open-V chevron**
* shaft in **`INK`** → **solid filled triangle**
* the connection is a **relationship, not a flow** → **dot-terminated, no head**

### 30.2 Colour

**Arrows take the accent colour, not black.** Shaft and head are the figure's accent — `MOSS`
in 68, 77, 83; `CLAY` in 27, 229, 230 (measured `#E4543C`/`#D85430` ≈ `CLAY #E05E3D`). Figures
191, 198, 221, 227, 229, 230 carry the accent on the shaft while **every box stays monochrome**.

Exceptions: 161's connectors are straight and vertical, drawn **in `ROSE`, not black**, with a
small solid head; 141's timeline leaders are `ROSE` open-V.

### 30.3 Head geometry

 `Canvas.arrow()` builds the open-V head from two lines:

```
head length       9 units from the tip, along the shaft
head half-width   4.5 units perpendicular
total head width  9 units
head stroke       same width as the shaft (default shaft width = 1.0)
```

At 2400 px / 780 units that is a head **27.7 px long and 27.7 px wide** — small relative to a
box, which is what "small head" means. Curved arrows take their head direction from the
**control point**, not the endpoint.

**Size relative to text is nowhere stated in v1; it is 9 canvas units, i.e. 0.82 × the 11-unit
micro-label.**

### 30.4 Dot-terminated connectors

**Leaders with a dot anchor and NO arrowhead**: a thin line ending in a small solid dot, used
for a **relationship** rather than a flow.

 `Canvas.dot(cx, cy, r=5)` for a filled dot, `r=5, filled=False` for a ring. The dot
sits **on the object**; the dot is a geometric anchor at a defined point, not decoration — the
088 reads could not settle this, so **treat it as an anchor** and place it on a named feature.

---

## 31. Connectors

### 31.1 Routing

| pattern |
|---|
| **elbow / right-angle** and **diagonal** connectors mixed in one figure |
| a **down-arrow from the end of row 1 to the start of row 2** (2-row flows) |
| straight and vertical only |
| **orthogonal vertical-then-horizontal segments** ascending |
| **L-shaped** connector geometry with in-flow lane labels (`GINKGO AUTOMATON`, `GINKGO SOFTWARE`) |

 `Canvas.chain(nodes)` places the arrow **6 units clear** of each node: horizontally
from `a.right + 6 → b.left − 6` at the vertical mid, or vertically from `a.bottom + 6 →
b.top − 6` at the horizontal centre. **That 6-unit clearance is the family's arrow gap.**

### 31.2 Solid versus dashed

| dash | means |
|---|---|
| **solid** | material / product flow |
| **dashed** | a chemical modification |
| **dashed** | an incomplete or conditional path |
| **dashed** with open-V head | a discard / side-stream |

 arrow dash pattern `4 3`.

### 31.3 Flow versus relation

A **flow** gets a head. A **relation** gets a dot. Do not put a head on a relation — a
successor who does will have arrowheads on the genealogy of 18 and the radial leaders of 88.

### 31.4 Spines and zone separators

| element |
|---|
| an **orthogonal collection spine** — a vertical hairline that gathers several outputs into one edge |
| **dashed vertical rules separating module zones** |
| a vertical spine with short horizontal **ticks** (a "tree" indent) |
| a **numbered badge spine** |

### 31.5 Connector edge labels

Small caps sitting **on the line**:

```
ACCEPTED · APPROVED · GRAS CONFIRMED · INCOMPLETE · NEGATIVE OPINION · POSITIVE OPINION
```

Mono or small-caps sans, `INK`, on the canvas fill (knocked out of the
line if the line passes through).

---

## 32. Process and flow

### 32.1 Direction

Horizontal flow, left to right; vertical when the process is a column.

### 32.2 Boustrophedon (snaking) two-row flow

A two-row flow that **reverses direction on the second row**, with:

1. a **horizontal rule separating the two rows**, and
2. an **explicit reader-instruction marker inside the figure**: the literal string

```
CONTINUED — ROW READS RIGHT TO LEFT
```

v1 contains neither the snaking, nor the rule, nor the marker, and it cannot be
guessed.

### 32.3 Gates

**Decision gate = dashed-border box; process step = solid-border box**, declared by a key line
`SOLID BOX = PROCESS STEP / DASHED BOX = DECISION GATE`. v1's §8.3 said
"gates on a line", which is the *timeline* gate (§33.5) — a different device.

### 32.4 Side-stream column

A separate labelled column (`SIDE STREAMS`) of **dashed boxes hanging off the main vertical
run**, connected by **dashed horizontal arrows with open-V heads**, labels ending
**`— discarded`**: `Precipitate — discarded`, `Flow-through — discarded`, `Permeate —
discarded`.

### 32.5 Containers and group outlines

| container |
|---|
| a dashed box enclosing two steps labelled `OPTIONAL` |
| a left bracket spanning stacked rows |
| a bordered beige **summary block** at the foot of a diagram |
| an **accent-edged container block** for an assessment or condition list at the foot: `ASSESSMENT OF THE BRAND'S CURRENT STATUS`, `CONDITIONS GOVERNING STAGE 1 - ACTIVATION` |
| a large faint rectangle enclosing a **phase**, with a phase header above it (`Phase 1: Establish Base Volume`; `Protein Isolation`) |

### 32.6 Numbered step badges

A solid accent **square** containing a **white numeral**, on a **vertical spine with short
horizontal ticks** (a tree indent), and a **single long arrow linking the last step of one
column to the head of the next**.; related: 20 (numbered step boxes linked by faint
vertical connectors).

Other step tokens in the corpus: **plain numerals** beside each step; **circled numerals**
①②③ (197, foreign); a **lettered particle token** — circles containing `M` for a metal ion,
moss-filled when bound — used as an in-drawing legend.

### 32.7 Logic nodes

Circles containing `×` for multiplication steps; rectangles for data and process steps; **no
start/end terminators** in the in-house figures.

### 32.8 Column scaffolds

`COLUMN 1` / `COLUMN 2` uppercase micro-labels above a single vertical stack, **no dividing
rule**, separated only by a whitespace gutter. **Whether this is an idiom or
leftover scaffolding is UNRESOLVED** — the figure reads as one continuous flow, so the labels
are structural, but they could equally be a build artefact. Treat as an idiom; do not emit new
ones.

Related: a two-column Gantt-style scaffold with **task names hard-left, owners hard-right, bars
on a wide central canvas, phases grouped by whitespace + a coloured sub-header**
(`PHASE 1 · 0-1 MONTH`).

### 32.9 Period bands

A horizontal band per period with the label **inside** it: `Yr 1 … Yr 8 …`, split into an
**upstream and a downstream leg**.

### 32.10 Off-flow inputs

A co-substrate box **outside the main line** joined into the chain with a **`+`**.
(adipic acid entering the nylon-56 route).

---

## 33. Timelines

### 33.1 Horizontal timeline — the canonical geometry

v1 gave "a single horizontal rule; events on it; labels alternating above and below". The
measurable construction:

| element | rule |
|---|---|
| the rule | one horizontal `INK` rule that **is** the axis — no spines, no ticks, no gridlines |
| event marker | a small **filled `ROSE` dot on the rule** |
| label blocks | **alternating above and below** the rule |
| inside a block | the **mono year sits on the line nearest the rule**, the **serif description stacked further out** |
| the leader | a short **`ROSE` arrow from the block to the dot**, pointing **down** for above-labels and **up** for below-labels |
| ticks | short outward ticks with the year labels below |

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

### 33.2 Vertical timeline

| variant | geometry |
|---|---|
| **vertical rule, dots on it, all labels hanging to ONE side** (no alternation) | dates in mono to the left, event text to the right, each event on a filled dot |
| **vertical timeline with a CENTRAL spine**, events alternating left/right, year label in coloured mono (cyan), thumbnail photographs attached to events | — |

v1 described only the horizontal form. **218/224 uses the cyan year labels of §33.10.**

### 33.3 Duration bands

A pale peach block across the timeline labelled `FIVE YEARS OF DATA PROTECTION`.

### 33.4 Past versus present marks

**Solid dot = a past event; hollow dot = the present / latest event.**. (Same
vocabulary as §9.2.)

### 33.5 Rule-with-gate

One continuous horizontal rule with **short outward ticks**; phase markers are **outlined boxes
with a pale clay tint sitting BELOW the rule** (not bands ON it); the **decision gate is a
small solid clay diamond sitting ON the rule** with its caption above; an `ESTIMATED` tag at
the top; caveats in italic below.

Also a **full-width shaded band across a Gantt** labelled `GO / NO-GO`, with the decision text
inside it, **interrupting the phase sequence** —.

### 33.6 Gantt

Two-column Gantt: **task names hard-left, owners hard-right, bars on a wide central canvas**,
phases grouped by whitespace plus a coloured sub-header `PHASE 1 · 0-1 MONTH`.
Dashed month gridlines; scale axis on **top** (§20.1).

### 33.7 Duration micro-labels

Mono, next to a gate: `90-180 DAYS`, `12-24 MONTHS`, `3-5 YEARS`, `18-24 MONTHS`.
117, 118.

### 33.8 Assessment box

A **left-edged assessment box at the foot of a timeline** carrying a verdict in italic. Figure
132.

### 33.9 Positions are decorative, not proportional

> **141 places `1990s`, `1999-2000` and `2000-2006` at EVEN spacing; 165 places dated
> categories evenly. A successor must be told not to scale them.**

 confirms it: `timeline()` spaces events `w × i / (n − 1)` — even, regardless of date.

**Rule: do not scale timeline positions to their dates unless the figure is explicitly a
time-series chart.**.

### 33.10 Year-label colour

Generation-1/off-palette: **pure cyan `#0CF0CC`** (and `#24F0D8`, `#18F0D8`) on the vertical
timeline spine of 218 and 224. **Do not confuse it with the foreign teal `#48CCC0` of 231** —
one is a house timeline's year label, the other is another company's corporate identity, and a
successor cannot tell them apart from v1.

### 33.11 Milestone markers

A **diamond on a roadmap with a vertical drop line to its label**, in `JPM_BRONZE`, with a
legend entry naming the marker class (`Dated valuation milestone`).

---

## 34. Annotation kit

### 34.1 Brackets

| form |
|---|
| a thin **square bracket spanning several rows**, with the group name set **vertically in the margin** (`TIER ONE`, `TIER TWO`; `GlaA fusion`) |
| a thin bracket with **end ticks** over two or more elements plus a label — `Methylotrophic yeasts` (98), `same target: tyrosinase`, `PH WINDOW`, `the 'immunity gap', 6-16 weeks of age`, `` (99) |
| a bracket spanning **three columns inside a table** |

**Rotated marginal labels are the device; v1 mentions tier structures and no drawing device.**

### 34.2 Typographic brackets

`[ ]` used as a grouping device **inside a table**, spanning three columns.

### 34.3 Measured callouts

A callout with a **measured bracket** pointing at a specific x value:
`0.33 — CICC 2103 starts at 3.00`.

### 34.4 Folded-corner callout

A callout box with a **folded (cut) top-right corner**, filled **one step darker than the
nodes**, attached to the annotated node by a **small triangular pointer**, contents as
label-value lines with `(Predicted)` qualifiers:

```
Source: / Compound: / Boiling Point: / Density: / Acidity (pKa):
```

**The folded corner needs an explicit ruling**: §10.2 forbids rounded corners, and
a folded corner is an adjacent device — it is permitted **only** on a callout, never on a node.

### 34.5 Leader lines

| form |
|---|
| a thin **accent-coloured straight or diagonal line** from a small **solid square marker** to a floating label placed in the empty whitespace to the right of the plot |
| a hairline (~0.5 px) straight segment from the label to the exact data point, **no terminal dot, no arrowhead**, used to place endpoint labels inside the plot and named-point annotations |
| a thin line from a text callout in empty plot space to the point it names |
| leader-line callouts: `Imagindairy目标 50 g/L`, `Td=70.4 °C`, `最高稳定性`, `restated for Synlogic $13.6m` |

> **This is the single most common annotation form in the corpus and v1 never mentions it.**
> Two forms exist and are not interchangeable: **with a solid square anchor** (5) and
> **bare, no anchor**. Match the original.

### 34.6 Directional data arrows

A thin accent arrow with an **open V head** from a **solid dot** to a **hollow circle**, meaning
"projected after change", labelled `ESTIMATED`.

### 34.7 Genealogy / bipartite

Two headed columns (`ENGINEERED HOST` / `PARENT STRAIN`), **thin dot-terminated connectors**,
**dashed border = not publicly deposited**, `MEADOW` = publicly purchasable parents, `CLAY` =
engineered hosts plus dashed (unavailable) parents. Also the HEK293 lineage tree and
the 2'-FL strain genealogy in the script catalogue.

### 34.8 Fishbone / Ishikawa application tree

A **central horizontal spine**, branches **alternating above and below** to leaf boxes, **no
arrowheads**, the **root node distinguished by an accent left band**. The
matched pair of §5.5.

### 34.9 Radial activity wheel

**Concentric hairline circles**, **six radial spokes** dividing the ring into sectors, **accent
dots placed exactly on the perimeter intersections**, and a **hub carrying a two-line label**
(a sans line + a serif italic sub-line). v1 listed "radiating concentric-hairline
fans" as a building block with no construction rule; this is the construction.

 `Canvas.ring(cx, cy, radii, dots, dot_len)` emits one `<circle>` per `(r, opacity)`
pair at `stroke-width 0.8`, then radial ticks of length `dot_len` from `radii[0]` outward, at
`i × 360/dots − 90` degrees.

### 34.10 Subset annotation

Annotate three points of a long series — **first, peak, last** — in the same hue as the series.
The chart analogue of "annotate the
decision point, not every event".

---

## 35. Molecules and chemistry

### 35.1 Abstract geometric residue tokens

A **square, a triangle and a pentagon** standing for amino acids, chained along the assembly
line. A symbolic vocabulary that must be written down or it cannot be reproduced.
Related: **square = GlcNAc, circle = Man, triangle = Gal, with the line `identity is the
shape`** —.

Combined vocabulary in use: **circles, squares, triangles, plus signs**.

### 35.2 Highlighting positions on a structure

Colour **the locant digit, the β symbol and the bond angles** in the accent, leaving **every
bond black and every ring unshaded**. v1 said only "hairline, no shading"; this is
the positive rule.

### 35.3 Repeating units

**Square brackets with a subscript n** marking the repeating unit of a polysaccharide. Figure
80.

### 35.4 Four-across comparison of physical principles

Each panel a small hairline sketch with **molecule glyphs (circles, squares, triangles, plus
signs) in one flat hue** and a **sans caption below**.

### 35.5 Primitives inside a flow box

A small **grid/bead icon** beside chromatography steps (26), single read at the
resolution limit — **UNRESOLVED**; if it is a text glyph, drop it. A **2-D skeletal structure**
with hairline black bonds, wedge stereochemistry and serif names below (79) is the correct
chemical-drawing form; the **3-D cylinder** of 030 is a defect, not a convention.

### 35.6 Boxed reaction-condition micro-labels

Conditions set **inside thin-outlined rectangles** beside the arrow:

```
6000 U · 50 mM · 24.0 gBWW · >99% conversion
```

A by-product is written **above the arrow** (`-H₂O`, 205); conditions
may sit **inside the step box**. v1 required the condition as a mono micro-label; the
**box** is the missing part.

### 35.7 Arrow-borne reaction and enzyme labels

The reaction or enzyme is **named on the arrow**: `L-lysine decarboxylase`, `polycondensation`.
Mono or small sans, on the canvas fill, centred on the shaft.

---

## 36. Cross-sections and positioning maps

### 36.1 Cross-section layer stack

| element |
|---|
| **three stacked hairline boxes**, each labelled with an **UPPERCASE MONO header plus an italic serif sub-line**, mapped to right-hand text blocks by **dot-anchored radial leaders**, with a **boxed caveat** at the bottom |
| hatch bands, a **triangle for a geochemical dispersion halo**, dotted and cross-hatched zones, **mineral formulas on leader lines**, arrows for rainfall and rising groundwater |
| **dense diagonal / dot / cross hatch separates geological units** |

> **v1's "building blocks worth reusing" list** (radiating concentric-hairline fans,
> spiral/root forms, ellipse clusters, circle-with-crosshair constructions) **does not appear at all.** The vocabulary actually used — column, bead, vessel, molecule
> glyph, hatch band, dispersion-halo triangle — is the one to document. Keep the crosshair
> circle only because `crossed_circle()` implements it (§29, terminus).

### 36.2 Positioning / continuum map

Two axes **labelled at both ends** (`SOLUTIONS … TOOLS`, `HIGHER … LOWER`), **zone header bars
over the field**, nodes placed along a **curved dashed path**, with an **explanatory line under
each node**. v1 covered the two labelled axes only.

---

## 37. Scale-free figures

**A curve figure may carry NO numeric scale at all**, and then it must say so.

The stage-band idiom on a scale-free curve ():

* four **thin vertical rules** spanning the plot height, with **sans stage names at the top**
 (`Emerge` / `Growth` / `Expansion` / `Maturity` / `Decline`);
* one **pale rectangle** (`#D0E4EB`) shading a span;
* item labels scattered above and below a **smooth sigmoid**, with **no leader lines**;
* **label colour switching from `JPM_INK` to `JPM_BRONZE` at the maturity boundary**;
* **no numeric scale on either axis.**

Its own caveat states the source gives no numeric stage boundaries, and the figure is
`ESTIMATED`. **Reproducing it means reproducing the POSITIONS, not recomputing them.** The
same rule applies to 167 (rank ordinals printed, no counts) and 141/159/162 (decorative
timeline positions, §33.9).

---

## 38. Tables

### 38.1 Rules

**Horizontal hairlines only. No vertical rules** — 22, 24, 38, 40, 43, 53, 86, 90, 98, 125,
250. One rule under the title, one under the header, one per row.

 `table()`: total width = `sum(col_w)`; rule under the header at `width 0.9`; row rules
at `width 0.45`; cell text inset **6 units** from the column start.

The **exemption class** is §43.

### 38.2 Header treatments — four of them, one token

| # | treatment |
|---|---|
| 1 | **`BONE` fill band with a hairline rule above AND below** |
| 2 | **`BONE` band + a thick `CLAY` rule immediately under it** |
| 3 | **band-less**: uppercase letterspaced grey text with a single hairline beneath |
| 4 | **accent-coloured header text only**, no band, no rule |
| 5 | uppercase sans column headers + a light `BONE` band behind the header row |
| 6 | a **full-width black rule under the header with no fill** |
| 7 | a **filled header band (tinted)** |
| 8 | an **olive/tan band on `PAPER`** — **UNRESOLVED**: the probe's top chroma are tans and grey with only 2.4 % chroma overall, so the vision claim is unsupported |

 `table(header_fill=…)` fills the header band and sets header text at
`size × 0.82` in mono `INK_MUTED`, uppercase.

**Rule:** within one document, use treatment 1 or 3; treatment 2 marks a table whose header
carries a rule the document wants read as a section boundary; treatments 6–7 belong to
imported/older tables.

### 38.3 Row dividers and row height

* **Row dividers are hairlines at `RULE_SOFT`-or-lighter weight (≤1 px at 2400 px canvas)**, one
 per row.
* **No zebra shading anywhere** in the house tables — except 038,
 where one pass reported alternating shading and a later, more careful pass reported uniform
 rows with hairlines only. **The later read is used**; 038 is UNRESOLVED.
* **Row height: measured impression ~1.6–2.0× the text line box.** `table()` default
 `row_h = 23`, `header_h = 27`, cell text at `size 13` → row height / text size = **1.77**,
 inside the measured range. **Use 23 units.**
* **Zebra banding exists once**, in an off-family figure — §50.

### 38.4 Alignment

| column | alignment |
|---|---|
| first / label column | **left** |
| value column | **left** in 22, 41; **right-aligned** in 250, 251; **centred** in a datasheet table (28) |
| basis column | **italic** |
| confidence column | **centred** |
| **decimal alignment is never used** | 22, 41, 28 |

 `table()` places every cell at `col_start + 6` — i.e. **left-aligned in every
column**. That is the primitive's behaviour and the house default; right-alignment is a
facsimile convention (§44).

### 38.5 Units live inside the cell

`50 µm`, `0.7 MPa`, `>110 mg/ml at 300 cm/hr*` — **never in the column header**.
38, 41, 43. v1 required explicit units in *axis* labels and said nothing about table cells.

### 38.6 Faces in tables

| element | face |
|---|---|
| **cell content** | **mono** for every house table |
| **row labels** | lowercase |
| **column headers** | UPPERCASE |
| **a three-way split**: column headers, count columns and figures = **mono**; row labels and cell text = **serif or sans** | 53, 86, 90 |
| **serif numerals in a facsimile statement** | §44 |

 `table()` uses `mono` for every column index > 0 and `sans` for column 0 — consistent
with the batch-1 split.

---

## 39. Matrix marks

### 39.1 The vocabulary, exactly

> **COR-17.** v1 §8.6 said "marks, not colours — dots, half-squares, crosses". The corpus's
> actual encodings differ from those words.

| mark | means |
|---|---|
| **hollow ellipse** | not stated |
| **half-filled ellipse** | partial |
| **solid ellipse** | disclosed |
| **solid square** whose **fill lightness** encodes the level's position on that column's **own ordinal scale** | ordinal rank |
| **hollow square** | a category **not on** that column's scale (off-scale) |
| **large tick and cross glyphs** | binary attributes |
| a **hexagon with internal spokes** | a virus-like particle |
| **infinity-loop markers** | — |
| **filled circle** | a score |
| **square, optionally half-filled for a 2-of-3 scale** | a score |

 `mark_sq()` draws the square as four `0.8`-width lines and fills the **bottom half**
when `half=True`. **The code's half is a HORIZONTAL split; the corpus uses a VERTICAL split** (§39.3). Match the original.

### 39.2 Lightness ramp

A single hue's lightness encodes an ordinal level —. §7.2.

### 39.3 Half states

**Half-state glyphs split VERTICALLY**: left half black + right half `SEED_BROWN` within one
ellipse = "partially disclosed"; a **vertically split half-square** in a table = "partly
disclosed"; and a **half-mark scores 0.5** in the count column.

v1 named "half-squares" without the axis of the split, the two colours, the 0.5 weighting, or
the derived count column. All four are above.

### 39.4 Icon marks

A **hexagon with internal spokes** (a VLP), an **infinity loop**, tick and cross glyphs. Draw as hairline geometry in `INK` or the accent.

### 39.5 Conditional-format cells — the exemption

> **COR-17.** A **declared** imported table may encode cell **value by hue** with **no key and no
> scale printed** — a deliberate exemption from the marks rule, not a precedent.

Palette: `#FCE4E4`, `#FCE4D8`, `#FCA86C`, `#FCCC9C`, `#8484C0`, `#B4D8B4`.

**Rule:** this is an **imported/publisher convention**, permitted only in a table declared as
imported (see §43). A **new** house table uses §39.1 marks. If such a table must be reproduced,
**reproduce the palette exactly and declare it** in the source line — do not convert it to
marks, because the conversion invents a scale the source did not publish.

---

## 40. Empty and absent cells

The semantics v1 lacks entirely:

| cell state | means |
|---|---|
| **blank** | nothing happened |
| **an empty outlined square** | **"no evidence — the gap IS the finding"** |
| **a dashed cell + `?`** | undetermined |
| **a solid `CLAY` border** | prohibited |
| **plain black border** | lawful |
| **an empty grey-outlined square** | not screened |
| **hollow** | not stated / not yet met / off-scale |

**Four-colour border coding** on one figure (21): solid `CLAY` = prohibited, dashed =
undetermined, plain black = lawful, `?` glyph inside the undetermined ones.

---

## 41. Table extras

### 41.1 Count columns

A **right-hand printed COUNT column**, with the total stated as **`of 10` in the header row**.

weightings of §39.3**. Derived totals are printed, not implied.

### 41.2 The key as a sentence

`filled = disclosed, half = partial, outline = not stated · right column = parameter count` —
**embedded as a sentence under the title**, not in a box.

### 41.3 Key block under the table

A block with the three chip swatches (§8.3).

### 41.4 Row emphasis

One row enclosed by a **≈2 px black rectangle** — `Dragline silk` in 228. Heavier than any
rule in the table.

### 41.5 Tinted column

One whole column backed by a **peach panel (`#F0E0D0`, 21 % of the figure)** that **bleeds to
the figure's bottom edge** rather than sitting inset; column headings in small uppercase; a
`1 VERIFIED CELL` count tag in the header row; italic notes beneath explaining that the cells
are quoted.

`BONE #EDEADB` is the sanctioned panel; the observed tint is **warmer** than `BONE` and there is
**no bleed rule in v1**. This section supplies both.

### 41.6 The paragraph marker

A **thick vertical `CLAY` bar to the left of a closing note**, as a paragraph marker.

---

## 42. Table metrics

| property | value |
|---|---|
| row height | **23 units** |
| header height | **27 units** |
| cell text size | **13 units** |
| header text size | **10.66 units** (`13 × 0.82`) |
| cell inset from column start | **6 units** |
| rule under header | width **0.9** |
| row rules | width **0.45** |
| row height ÷ text size | **1.77** |
| cell padding | **~2 px** in the 630×480 tables of 220/228 — "far below anything §6's 'generous row height' implies" |
| cell padding is a **deliberate per-type choice**: generous in the matrix (90), tight in the register table (53) | — |

**Rule:** a matrix gets generous rows (23–30 units); a register copied from a source keeps the
source's tight padding and says so in the source line.

---

## 43. Full-grid tables

> **COR-3.** v1: "no vertical rules." The corpus has both conventions live.

**The exemption class**, to be declared rather than silently drawn:

| form |
|---|
| a full vertical grid on a house table with accent-coloured header text |
| **full-grid hairlines** — ~0.5 px `INK` rules on **all four sides of every cell**, plus pastel conditional-format fills |

**Rules for the exemption:**

1. A full-grid table must be **declared** — it is either an imported table (§47) or an older
 house table being reproduced.
2. It must keep the §4 tokens for its rules; a full grid in a foreign hue is a §50 figure.
3. A **new** house table uses §38.1. Do not adopt the grid for density reasons; split the table
 or widen the canvas instead.

---

## 44. Facsimile statements

facsimile,-measured.

| property | value |
|---|---|
| canvas | **pure white** `#FFFFFF` |
| type | **serif** (a book face), **not mono** — the opposite of v1's "DM Mono for all numerals" |
| zebra rows | **pale sky tint**, `#C0E8F8` / `#D8F0F8`, ~23 % of the image |
| amounts | **right-aligned** |
| vertical rules | **none** |
| rules above totals | a hairline under the header and above totals |
| the final total | a **double rule** above it |

251 is additionally a **cropped fragment** of the same statement; **there is no convention in
v1 for a partial statement** — reproduce the crop as given, with the source line naming it a
fragment.

**Rule:** a facsimile is a **quotation**, not a house table. Do not convert it to §38
conventions; that destroys the evidence that it is a quotation. Do add a source line.

---

## 45. Zero-accent figures and off-family drawings

### 45.1 Zero accent

**Nine figures use no accent hue at all**: 241, 247, 256, 262, 278, and 252–254, 257, 258, 270,
274 as non-figures. §2's rule is "one accent hue per figure"; **the corpus has no statement of
what a figure with ZERO accents looks like**, and that is a fifth of the diagram family here.

The reference: **262 — a card pipeline with ordinal kickers.** Three bordered cards, each a
small uppercase `STEP n` kicker + a name + three micro-headed columns; **no fill, no accent at
all**.

**Rule:** a figure may be pure ink-and-paper, and when it is:

1. the ink is `INK` (or `JPM_INK` in the register);
2. hierarchy is carried entirely by **size, space, letterspacing and one typographic weight of
 italic** — never by colour;
3. it still carries the full furniture (§14–§18);
4. its source line names it as house work so it is not mistaken for a capture.

> **COR-22, second instance.** 262 directly contradicts v1 §8.1's "One accent marks the step
> that matters", because there is no accent to mark anything.

### 45.2 Off-family **drawn** figures — the gap v1 leaves

v1 §9d covers external **bitmaps**. It has **no rule for an off-family DRAWN figure** — one
that was drawn in-house (or imported and edited) in a foreign visual language.

| what it is | verdict |
|---|---|
| rounded rectangles, six pastel fills with darker borders, solid triangle arrowheads, bold italic orange durations, ovals for start/end — the PowerPoint/Visio default language. No logo, seal, watermark or source line, so **authorship is undecidable from the image** | rebuild |
| an illustrated two-column comparison with pastel fills and red section headers; no chrome, no branding | keep-adjacent; `fits_family=no` |
| Office blue `#1F4E79`, grey rounded nodes, folded-corner callout, **no source line**; content is recoverable | rebuild |
| ROUNDED-corner boxes filled solid slate blue with white text, dashed borders for optional steps, white canvas | rebuild |
| PowerPoint/SmartArt, 3-D cylinder, pastel blue fills, rounded corners, no furniture | defect instance, not a style reference |

**Rule:** because authorship is undecidable, **do not silently normalise these to the house
style and do not silently keep them.** Apply the §52.3 test: if the *data or content* is
recoverable and the figure is in-house or plausibly in-house, **rebuild**; if it is another
party's artwork, **keep and report** (§47). State which decision was made and why, per figure,
in the work list.

### 45.3 Bilingual stacking

Where a figure must carry two languages, the corpus stacks them:

```
Chinese primary line      black, the primary face for that element
English translation       immediately beneath, grey sans, one step smaller
```

This is
also **why 19 is KEEP rather than rebuild**: the second language is the content, and retyping
it risks introducing an error into a quotation.

**Rules:**

1. **One element per language pair.** Do not interleave languages inside a line.
2. The **primary** language is the document's language; the translation is subordinate —
 smaller, and in `INK_MUTED` or the grey of §12.5.
3. Leading between the pair is the element's own leading, not body leading.
4. **Chinese labels are also the generation-1 signature (§51).** A Chinese label in an
 otherwise generation-2 figure is either a bilingual pair (this section) or an unreissued
 generation-1 leftover — check which before "fixing" it.

---

## 46. Photographs

### 46.1 Transparent cut-outs

Product photographs ship as **RGBA PNGs with 20–85 % of the canvas fully transparent**, placed
**bare on the page tone**: **no white box, no frame, no caption, no source line**. Figures
143–.
v1 said photographs must be kept and never said how they are presented. **This is how.** A
white mat behind a cut-out is a defect.

### 46.2 Knockout annotation over a photograph

**Paper-filled, square-cornered label boxes with hairline black borders and mono text**,
connected to features by **thick white arrows**. The white arrow is the one place a
white stroke is correct outside a canvas fill.

---

## 47. Kept externals

### 47.1 Framing and the mat rule

A kept external is a **citation**. Four treatments exist in the corpus and v1 picks none:

| treatment |
|---|
| bare white raster, no treatment |
| bare raster **carrying a watermark** |
| bare slide edge |
| bare journal table edge |

**Rule:**

1. **No hairline frame, no `BONE` mat, no inset margin by default.** Place the raster as-is.
2. **Do not scale** a bitonal plate up or down; scaling breaks the crispness (§47.2).
3. **Everything else about a kept external stays foreign** — including its own white canvas,
 its own header band (`#1E366A` in 172/173, **not** `JPM_INK`; RGB distance 39), its
 browser-blue underlined links, its publisher's peach column bands, its IFRS footnotes.
4. **Add a source line naming it as a quotation** — that is the one house element it receives.
5. Where a kept external sits inside a **house plate** (241: a kicker + caption + a NOTE block
 declaring provenance and product-neutrality), the plate is house and its content is not.

### 47.2 Bitonal and scanned plates

049–052 and 060–063 are **1-bit indexed** (pure black/white, no greys); 054–058 are 8-bit
indexed scans. On a paper page they read as **hard white plates**.

**Rule:** keep them at native scale, with a hairline border **only if** the plate's own edge is
indistinguishable from the page (a blue-white rectangle on cream); otherwise place bare. Never
interpolate.

### 47.3 Pixel floor and the twin-replacement rule

| case |
|---|
| cannot carry a 6 pt label |
| a 630×480 px table with six numeric columns |
| the same figure at two resolutions |

v1 set a **point** floor and no **pixel** floor. **Rule:**

1. A kept bitmap must be at least **250 px on its short side** (the corpus's smallest usable is
 250×188). Below that, replace it or report it.
2. **A same-figure pair is replaced, not hashed**: the **higher-resolution twin wins** and the
 lower is deleted from the document.
3. The corpus's KEEP-class bitmaps run **250–1268 px wide**; that is the observed usable band.

### 47.4 Palette signatures

Without a list, "foreign" and "off-style" cannot be told apart on sight. The signatures:

| signature |
|---|
| saturated red / navy / green / lime |
| saturated orange / yellow / cyan |
| rust `#C0540C` + steel `#246CB4` |
| teal + mint corporate identity (`#48CCC0`, `#CCF0E4`, grey `#6C7884`) |
| Japanese blue + teal (`#3C6CB4`, `#00A8A8`) |
| an opaque blue root panel |
| PyMOL-style blue/purple/red/green |
| default matplotlib 7-hue cycle |
| a foreign header band `#1E366A` |

**Rule:** a figure whose palette matches one of these is a **quotation** unless the source line
says otherwise.

### 47.5 The 3-D render exemption

241 carries an **unlabelled 3-D render inside a house plate**. This is the one sanctioned 3-D
in the corpus, and the sanction is narrow: the render is **imported**, the plate around it is
house, and the figure's NOTE block declares its provenance and product-neutrality.
**§10.3's ban on 3-D applies to drawing, not to placing an imported render.**

---

## 48. Build artefacts and empty slots

**Five empty spacer images** — 148, 151, 152, 154, 163 — are 33×33 / 32×33 PNGs with **zero
opaque pixels**, embedded among product-photo slots (pages 7, 8, 14 of their documents).

They are a **build artefact**: nothing to reproduce, and they cannot be typed honestly against
a taxonomy that assumes content (they were recorded as `source-screenshot` purely to keep the
schema valid — **exclude them from any type tally**).

**Rule:** an image part with no opaque pixels is a defect. Remove the part; do not replace it
with a blank plate or a frame. `151 = 152` are byte-identical, so a fix hits both.

---

## 49. Inline icon glyphs

Eight images are **hand-drawn-style arrows, ~50–110 px, on a transparent background**,
used as **inline text icons** rather than as standalone figures.

| property | value |
|---|---|
| colour | **off-palette orange `#EE822F`** (up, down, curved) or **black** |
| fringe | the black glyphs carry a thin off-palette **`#4772C9`** blue fringe |
| size | ~50–110 px |
| duplicates | `179 = 182 = 185` (orange up-arrow, three copies); `181 = 184` (black curved arrow) |
| head form | a **hand-drawn tapering head**, not the §30 open-V — the curved one in 181/184 is drawn by hand |

**Rule:** these are **not figures**. They are inline icons in running text. Do not give them
furniture, a source line or a caption. Reproduce them from the asset, not by drawing a
replacement.

---

## 50. Off-family figures

### 50.1 The classes

| class | what it looks like |
|---|---|
| **default matplotlib** | the 7-hue cycle, opaque white |
| **older plotting default** | neutral white canvas, amber + orange-red, saturated pure blue, **dotted gridlines on both axes**, bordered legend |
| **another tool's default** | Office/matplotlib default line chart, blurry, 465×276 |
| **Office / SmartArt** | rounded corners, pastel fills, 3-D cylinder, white background, no furniture |
| **vendor software** | navy/steel-blue/purple series |
| **a raw market-report page** | default palette, 24 bpp RGB, no alpha channel |
| **rounded + pastel + white canvas** | rounded rectangles, six pastel fills, solid triangle arrowheads |

### 50.2 The rule

> **COR-14.** v1 said "Never default matplotlib colours. Ever." The corpus violates this in at
> least nine figures.

**Rules:**

1. A **house** figure never uses a library default palette or a library default style.
2. A figure **copied from another tool** keeps its own styling if it is a quotation (§47).
3. A figure that is **ours but built with defaults** is
 a **reissue**: rebuild it in the house language from its own printed values.
4. **Do not state the rule as "never within N RGB units of a matplotlib default"** — that
 formulation fails two legitimate figures: `JPM_BRONZE #8F5A39` sits **19 RGB units** from
 matplotlib's brown `#8C564B`, and the greyscale equation fragment
 169 uses `#888989`, **17 units** from matplotlib's grey `#7F7F7F`. Both are coincidences, not
 palette leaks (the bronze is the documented JPM token; the equation is a captured render).

---

## 51. Two generations of the house style

An earlier generation of this house style exists — opaque white canvas, a single blue magnitude
ramp, Chinese labels and no source line, with LaTeX `{,}` thousands-separator artefacts inside
its title strings. **Do not reproduce it; the current style is the one specified in this
document.** Such a figure is identified by the `{,}` grep signature, an opaque white canvas and
the single-hue blue ramp, and it is **reissued into the current style**, not merely kept. The
`{,}` artefact is a **build defect, not a locale choice** — it comes only from a code pipeline
writing a LaTeX-formatted number into a plain string. **Never let it ship.**

## 52. Working rules

### 52.1 The twin rule

Before and after any figure work: **hash every placed file (SHA-256) and compare.** Duplicate
groups cross document and batch boundaries, so a hash run restricted to one document misses
them. **A group is the unit of work, not the placement.**

### 52.2 Keep-the-asset-but-re-derive-it

Thirteen drawn figures are
**already in the house style** and contain **no data values**. A script cannot regenerate them
without re-typing text — which is the spec's own "text as an image → keep" rule. But they are
**diagrams, not quotations**, so §47 does not protect them the way it protects a patent page.

**The rule:**

| if… | then |
|---|---|
| a house-drawn diagram, no data values, text unchanged | **keep the asset** |
| the same figure, but any text changes | **re-derive from the script**; if no script exists, rebuild it in the house language and record that the text was re-typed |
| a house-drawn diagram **with** data values | **regenerate from the values** (§52.3) |
| a quotation of any kind | **keep**, always (§47) |

### 52.3 The two reproduction paths

Two paths, chosen by whether the figure's values are recoverable:

**Path A — regenerate from a script in the design language.** The figure prints its own data
values, so the numbers exist and the only question is style. Two sub-cases:

* **A1 reissue** — already a house build; re-emit it.
* **A2 first build** — currently a default-matplotlib or foreign-styled figure whose values are
 printed; build it in the house language for the first time.

**Path B — reproduce by placing the existing asset.** Sub-cases:

* **B1 quotation** — a source-screenshot, photograph, or another party's artwork.
* **B2 draw-it-forward** — a house-drawn diagram whose content is text, structures or
 qualitative marks, with no data values: keep the asset now, re-derive it if the text changes
 (§52.2).
* **B3 external render** — needs the original tool (70, 75 need PyMOL/ChimeraX).

### 52.4 Report, do not normalise

**Report every external figure rather than silently rebuilding it.** The count matters: a
reader who knows which figures are quotations reads the report differently. **Report per figure;
do not quote a global ratio you have not
recomputed.**

---

## 53. Canvas geometry and aspect

| property | value |
|---|---|
| authoring width | **`TARGET_CANVAS_W = 780` units** |
| figure sizes in the scripts | **560–940 units** |
| derived factors | 780 → 0.583; 940 → 0.484; 1320 → 0.345; 560 → 0.813 |
| export width | **2400 px** |
| matplotlib chart widths | `FIG_W_IN = 7.1 in` × `DPI = 300` = **2130 px** |

### 53.1 Aspect ratios far from landscape

| size | ratio |
|---|---|
| 2400 × 4740 | 1: 1.98 |
| 2074 × 2220 | ≈1: 1.07 |
| 1980 × 2100 | ≈1: 1.06 |
| 2400 × 3443 | ≈1: 1.43 |
| long lists and flows | — |

**v1's scale law is stated per figure WIDTH and says nothing about stacking long lists or
flows** — where the on-page width shrinks and the type floor becomes the binding constraint.
**Rule:** a tall figure must be authored **at 780 units wide** (not wider) so that the height
does not force a width increase; if the content needs more height, increase `h` only, and check
`check_scale()`.

### 53.2 Canvas margins

: horizontal margin **40 units** on both sides; header content starts at `y = 46`;
`frame()` defaults to `x = 30`, `w = w − 60`, `y = body_top − 14`, `h = h − 70 − y`.

---

## 54. Export contract

### 54.1 The contract

| artifact | requirement |
|---|---|
| **SVG** | always written, from the same canvas; `role="img"`, `viewBox="0 0 w h"` |
| **PNG** | **2400 px wide**, at 300 dpi equivalent |
| matplotlib PNG | `figsize × dpi`, asserted exactly; `savefig.bbox = None` — **never `tight`** |
| matplotlib SVG | also written, same canvas |
| chart width | `FIG_W_IN = 7.1`, `DPI = 300` |

### 54.2 Transparency

* **For a figure placed in a DOCX whose page tone must show through → export transparent.**
 A white-filled chart on a paper page is a visible rectangle.
* **For a figure that will also be opened standalone or placed in HTML → export
 `PAPER`-filled**, because transparency against a browser's white shows white.
* **Export both and let the consumer choose.** `Canvas.save()` writes SVG + PNG; the rasteriser
 uses `cairosvg` with `background_color=PAPER`, and falls back to headless Chrome with
 `html,body{background:PAPER}` — so **drawn figures are `PAPER`-filled by construction**.
 The transparent class (§6.1) is produced by a different path and must be requested.

### 54.3 Do not quote a transparency ratio

Whether a canvas is transparent is decided **per figure**, not from a census: a global count of
transparent figures describes neither a rule nor a target. Use the rules in §54.2 and §6.2, and
recompute a count if one is needed.

### 54.4 Format deviations

| deviation |
|---|
| ships as **JPEG** (2400×3443) while every other drawn figure in its batch is PNG |
| JPEG |

> **COR-20.** v1 requires PNG at 300 dpi. JPEG is a recorded exemption/defect. **Reproduce as
> PNG on reissue**, or record the exemption; do not silently emit JPEG for a new figure.

---

## 55. The scale assertion

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

**Three rules:**

1. **Assert; do not report.** A build that says `ok` while a label prints at 4 pt is the defect
 the assertion exists to catch.
2. **Assert that the checks RAN.** `{"scale", "bounds", "collisions"}` and
 `elements_recorded > 0`. A vacuous pass is worse than a crash.
3. **Never `bbox_inches="tight"` on a figure whose annotations overhang.** It grows the canvas
 and shrinks every label in proportion. A real instance: a chart saved at 2841 px against a
 nominal 2220 printed its 7.5 pt labels at **5.02 pt**, with `check_scale()` reporting
 `ok=True` throughout.

**Boundaries:**

* `check_scale()` measures the **authored** smallest label, not the printed one; it is only as
 good as the canvas width you pass it.
* `CENSUS.md` tags roughly half the population `FAIL` / `PASS`. **If `FAIL` is the scale-law
 check, that is an independent evidence stream for this work and must be reconciled with the
 figure-level findings** — it has not been, and nothing in this document depends on it.

---

## 56. Defect register

These are **things the corpus does that are defects, not style.** Reproduce the figure's
*intent*, and fix these on reissue — but **record that you fixed them**, because a faithful
reproduction of a defect is a defect.

| # | defect |
|---|---|
| 1 | **No source line on a house figure** |
| 2 | A mono source line **physically overlaps** the bottom bar of the chart |
| 3 | Bars **not sorted descending** while their siblings are; the highlight logic also differs (sky blue marks the residual in one figure, a segment in another) |
| 4 | A **dual-axis figure that does not name its right-hand series** — dual axes are permitted (§26.9); the missing label is the defect |
| 5 | **Vertical gridlines** where v1 forbade them — now permitted (§21.1) |
| 6 | The hue assigned to each row **looks arbitrary and does not carry across the two panels** (brown is "No antibiotic" on the left and "Probiotics" on the right) |
| 7 | **Non-house canvas and hues** (neutral white, amber + orange-red; saturated pure blue) with dotted gridlines on both axes — an older plotting default |
| 8 | **JPEG export** where PNG was required |
| 9 | **`{,}` LaTeX separator artefacts inside title strings** (`100{,}000-200{,}000 L`, `870{,}000 t`) |
| 10 | **Scaffolding labels survive into delivered artwork** (`COLUMN 1` / `COLUMN 2`) — decide whether it is an idiom; do not emit new ones |
| 11 | A **misspelling survives inside a figure**: `Chemical and Pharamaceutical Industry` |
| 12 | A misspelling in a kicker: `SUPERXIDE DISMUTASE` where it should be `SUPEROXIDE` |
| 13 | A **broken word space**: `All onnia` |
| 14 | A source line **reproduces a typo from the source document**: `Bussiness Model` |
| 15 | A **malformed source line**: the document name is truncated (`Report 4 Cosmetic Ingredients` → `Report`) |
| 16 | **Five empty spacer images** with zero opaque pixels |
| 17 | `state = NO_DISK_FILE` recorded for four files that exist and are legible |
| 18 | **A row is not in the stated order** in a table while its siblings are |
| 19 | **Third-party content redrawn in-house without a provenance note** |
| 20 | **A curve figure declaring its own positions are unverifiable** but printed as though scaled |

---
## Appendix C — the forbidden list

Rewritten from v1 §10, with the corpus's own exceptions carved out. Each entry was an actual
defect at least once.

**Structural**

* Default matplotlib colours, 3-D bars, pie-chart gloss, dual-axis tricks (**dual axes are no
 longer forbidden — see COR-15 / §26.9; a dual-axis figure must name its right-hand series**)
* Gradients, drop shadows, bevels, glows, rounded corners
* A **white or transparent canvas where the page is paper** — **for a house figure**. White is
 correct for a facsimile, a foreign capture and a generation-1 figure (§6.5); transparent is
 correct for a photographic cut-out (§46.1).
* `bbox_inches="tight"` on any figure whose annotations overhang — it grows the canvas and
 shrinks every label in proportion
* More than one accent hue for **the same semantic class** in one figure (**two hues are
 permitted when they are different classes** — COR-5, §5.3)
* **Bold** · italic used for emphasis instead of the semantic slots of §11.4 · any tracking on
 body text
* Rounded corners anywhere; a folded corner anywhere except a callout (§34.4)
* 3-D — **except** an imported render inside a house plate (§47.5)
* A figure with no source line (**the PLATFORM family and 246 are recorded defects, not
 precedents** — §18.7)
* Labels below 6.0 pt on the page — the most common and most damaging defect

**Corrected entries — v1 forbade what the corpus does**

| v1 forbade | corrected |
|---|---|
| vertical gridlines | permitted and required on horizontal-orientation charts (§21.1) |
| solid arrowheads only | **two forms**, chosen by shaft colour (§30.1) |
| vertical rules in tables | horizontal-only is the house rule; a full grid is a declared exemption class (§43) |
| `SEED_BROWN` and `LIME` as text | permitted as short isolated strings; a legibility constraint, not a prohibition (§5.3, COR-4) |
| opacity | alpha **is** the mechanism for bands, area fills and halos; use the eleven-value ladder (§7.3) |
| a legend whenever labels do not collide | legends are first-class; key blocks and state-key lines are forms (§23) |
| one shared source line per paired panel | one source line, but per-panel titles when the panels measure different things (§27.7) |
| `Figure N —` inside every figure | the number lives in the document; an in-image caption is an unnumbered sentence (§19) |
| sans headlines, always | serif titles in the finance register (§16.2) |
| a single accent hue per chart | the JPM register is a three-hue palette; a ramp is one hue at several lightnesses (§7.2) |
| score cells as marks, always print the scale | marks are the house rule; a **declared** imported table may use conditional-format colour with no key (§39.5, §43) |
| "never within N units of a matplotlib default" | **do not state the rule this way** — `JPM_BRONZE` is 19 units from mpl brown and the captured 169 is 17 units from mpl grey (§50.2 rule 4) |

---
