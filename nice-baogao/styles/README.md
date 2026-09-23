# Styles

A **style** is a complete, self-contained visual contract for figures: palette, typography,
geometry, chart conventions, and per-category rules. Every style is swappable — the
workflow in `SKILL.md` does not change, only the look.

**Pick one style per document set and use it everywhere.** Mixing two styles inside one
report is the defect this system exists to prevent.

## Available

| Style | Register | Use for |
|---|---|---|
| [`synbio-editorial`](synbio-editorial/STYLE.md) | Engraved technical — hairline drawing over modern geometric construction; one accent hue by meaning | Technical and commercial research reports: scientific mechanisms, market analyses, regulatory pathways, financial models, timelines, matrices. The style the source corpus was built in. |
| `_template` | — | Not a style. The skeleton for authoring a new one. |

## How to choose

Ask the user once, at the start, and record the answer in the set's `_admin/`:

```
Which figure style?
  a) synbio-editorial  — the house style; engraved technical, restrained
  b) a new style       — describe it, and I will author it from _template/
```

If the user offers no preference, **use `synbio-editorial`** — it is the one with a
full catalogue, a working toolkit and a proven corpus behind it.

If the user describes something else ("make it look like a McKinsey deck", "flat and
modern, no engraving", "dark background"), **do not approximate it inside
`synbio-editorial`.** Author a new style from `_template/` and keep both. Approximating
produces a third, undocumented look that nobody can reproduce.

## Census the population before you catalogue it

**A style is only as complete as its catalogue, and a catalogue built from script names
is not a census.** This was a real failure: the first CATALOG.md was assembled from the
~91 names in the drawing-script directory and read as though it covered the corpus. The
corpus actually holds **281 displayed figures in five classes**, and only two of those
classes come from a script at all:

| class | count | comes from a script? |
|---|---|---|
| drawn diagrams | 127 | yes |
| matplotlib charts | 97 | yes |
| external / extracted bitmaps | 50 | **no** |
| orphans (referenced by nothing) | 5 | **no** |
| charts with no source | 2 | **no** |

So a third of the population was invisible to a catalogue that looked complete.

**Do this first, every time:**

1. Enumerate every figure **actually displayed in the documents** — resolve every
   
:embed / 
:id / svg:svgBlip reference, and count them.
2. Classify each one: drawn / chart / external bitmap / photograph / orphan.
3. For each class, ask *which part of the style covers this?* If the answer is "nothing",
   the style has a gap — not the figure.
4. Write the counts into the style's catalogue so a successor sees the coverage, not just
   the entries.

census_figures.py does steps 1–2 against a measured population; adapt its two input
paths to your set. And note the general shape of the error, because it recurs:
**"the things I made" is not "the things the reader sees."**

### Classify by what a figure IS, not by what produced it

**A trap I walked into three times.** The census in this folder classes figures by
producer x provenance - matplotlib / itmap x has-a-source / has-none. That is a
proxy, and it misleads:

* producer: matplotlib does **not** mean "it is a chart". Inspecting the 97
  matplotlib-produced figures at full resolution found **diagrams** among them (a
  geological cross-section, process schematics) and **7 tables** (text in a grid).
* producer: bitmap does not mean "it is a diagram". Ordinary bar charts sit there.

producer records the **rendering tool**. It tells you whether a figure can be
re-rendered - genuinely useful - but it cannot tell you which part of the style covers it,
which is the only question a catalogue exists to answer.

**Class by figure type, keep the producer as a second column:**

| type | covered by |
|---|---|
| data chart (bar / line / scatter / stacked) | the style's chart section |
| diagram / schematic / process flow | the style's per-category conventions |
| table-as-figure | the style's table rules |
| photograph / micrograph | keep as is |
| screenshot of a source document | keep as is (see the external-figure test) |

**Judge type at full resolution.** The same survey that produced this correction first
reported three forms "missing from the style" - a heatmap, a dual-axis chart and area
charts - and all three were refuted at full size: they are a geological cross-section
diagram, a plain horizontal bar, and a stacked horizontal bar. **A 240 px thumbnail hides
the absence of axis numbers, and it invents forms that are not there.** If you cannot read
the axis values in the image, you are looking at the wrong image.

## What a style must define

A style is a folder containing exactly four things:

```
<style-name>/
  STYLE.md            REQUIRED. The rules you draw by: tokens, colour meaning, canvas,
                      fills, status tags, geometry, type and font stacks, tracking,
                      furniture, axes, chart rules and forms, panels, uncertainty,
                      diagrams, tables, layout coordinates, export contract, and the
                      forbidden list. Self-contained -- no value is deferred elsewhere.
  STYLE_REFERENCE.md  optional. The same rules at greater depth, plus the longer device
                      detail. Load a section when you need more than the core gives.
  chart_kit.py        matplotlib: theme, series palettes, chart conventions as callables.
  diagram_kit.py      the drawn-figure API: primitives, layout QA, save/export.
```

Only `STYLE.md` is required. A style without it is not swappable, because a successor
cannot apply it without guessing.

### Load only the section you need

`STYLE.md` is a manual, not an essay — it is sectioned so a drawing session pays for the
sections it opens, not for the whole file. Measured on the reference style:

| drawing | open | cost |
|---|---|---|
| a table | tokens, canvas, fills, geometry, tables | ~6,000 tokens |
| a diagram or flow | the above plus furniture and diagrams | ~15,000 tokens |
| a chart | the above plus chart rules, forms, panels | ~16,000 tokens |
| everything | the whole core | ~30,000 tokens |

The full core plus the reference is ~73,000 tokens — **do not load both to draw one
figure.** Read the table of contents, open what the figure needs.

### What must NOT go in a style folder

**Audit records.** A style is what to draw; an audit is what was found in one particular
corpus (which figures used which device, which are off-family, which are byte-identical
duplicates). The second is a project record and belongs with that project — it is
worthless for the next document set and it inflates the spec.

The reference style's audit record lives at
`Desk Research/_admin/FIGURE_AUDIT_RECORD.md`, deliberately outside the toolkit. When you
run an inspection like that, put its output with the documents, not here.

### The non-negotiable parts

Every style must define these, whatever its look. They are not aesthetic choices:

| Must define | Why |
|---|---|
| **A type-size floor and target**, in printed points | Legibility is not a style preference. 6.0 pt floor, 6.5 pt target, measured on the page. |
| **The scale law** `on-page pt = authored × display ÷ canvas` | The same arithmetic governs every style. Ignore it and labels shrink silently. |
| **A caption and source format** | Every figure carries its provenance. |
| **An export rule** (vector + raster, and at what dpi) | |
| **A forbidden list** | A style is defined as much by what it refuses. |

### The parts that are yours to invent

Palette and its semantics; faces and their roles; stroke weight; whether fills are flat,
hatched or absent; the drawing idiom (engraved, flat, isometric, blueprint, hand-drawn);
chart forms; how importance is expressed.

## Authoring a new style

1. Copy `_template/` to `styles/<your-style-name>/`.
2. Write `STYLE.md` first, and write **numbers**, not adjectives. "Hairline 0.5–0.8 px"
   is a style; "clean and modern" is a conversation.
3. Name the **semantic** meaning of each accent before choosing the hex. A palette
   assigned by meaning reproduces itself across 100 figures; one assigned by taste does
   not.
4. Declare the floor, target and export rules — inherit the defaults if you agree with
   them, but state them.
5. Write the **forbidden list**. It is the fastest way for a successor to stay inside
   the style.
6. Build `chart_kit.py` and `diagram_kit.py` **from working figures**, not in the
   abstract. Draw three real figures first; the API will tell you what it needs.
7. Add `CATALOG.md` as you go, with one row per figure. It becomes the precedent library.
8. Verify against the page: render, measure the smallest printed label, and confirm it
   clears the floor. A style that looks right on screen and prints at 4 pt has failed.

## Porting an existing set to a style

Changing a document set's style is a **figure-layer rewrite**, not a re-render:

* Every figure must be re-drawn or re-rendered through the new style's kits.
* **Do not restyle by recolouring a finished raster.** Recolouring a PNG produces flat,
  wrong-looking output because the original had its own background, antialiasing and
  stroke weight baked in.
* Figures with no source script cannot be restyled at all — **measure and report them
  rather than faking a conversion.** See `../reference/SCHEMATICS.md`.
* Counts must not change: same figures, same positions, same captions.
