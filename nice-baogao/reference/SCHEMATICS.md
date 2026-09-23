# Redrawing schematics to a house style

The source engagement redrew **129 figures** with **491 outputs**, plus a separate legibility
pass over 275 figures. This is a large workstream and it is a *drawing* problem, not a
measurement problem.

## Write the brief down, and write the house style into it

A `SCHEMATIC_REDRAW_BRIEF.md` given to every agent, covering: **why** the redraw is
happening; **the house diagram style** (stated concretely enough to reproduce — box and rule
weights, corner treatment, label placement, arrow form, the accent used for emphasis, the
paper tone); **"use the toolkit, do not hand-write SVG"**; **what to preserve and what to
drop**; the per-figure procedure; and the hard rules.

Two sections earn their place by saving a day each:

* **"Three things that will cost you a day if nobody tells you."** Every engagement
  accumulates these. Write them down the moment you learn them.
* **"Defects found in the documents while working."** Whoever redraws a figure is reading its
  source document closely. Require them to report what looks wrong. This is how the
  highest-value content corrections were found.

## Use a toolkit, never hand-written SVG

Hand-written SVG cannot hold a shared style, cannot be re-rendered when the standard changes,
and cannot be checked. Build a small Canvas toolkit — boxes, arrows, chains, rings, columns,
timelines, labels, notes, captions, source lines, frames — and a `check` that asserts the
canvas contract on every build.

Then a redraw is a *script*, and the whole library can be re-rendered when the type scale or
an accent colour changes. In the source engagement that is exactly what happened, repeatedly.

**Put the toolkit under shared ownership and treat it as an engine.** Defects found in it
must be fixed once, centrally, and the fix recorded — the same bug will otherwise be
rediscovered by several workstreams in parallel.

## Preserve vs drop

Preserve: every label string, the meaning of every relationship, the data values, the
citation and source line.

Drop or normalise: inconsistent stroke weights, ad-hoc colours, decorative gradients,
shadows, clip art, mixed label casing, and any element that carries no information.

**Never change a word.** If a label does not fit, the fix is geometry — widen a box, rebalance
column widths, move a label off a collision — not a shorter word. Require the drawn-string
multiset to be proven identical before and after (see `RULEBOOK.md` rule 1: raising a font
size re-wraps width-measured notes and silently changes line breaks).

## The procedure per figure

1. Find the **generator**. Do not assume: check that re-running it reproduces the shipped
   bytes. If nothing reproduces them, you have found either a stale figure or an untraceable
   one — report it rather than substituting a drawing of your own.
2. Read the source document around the figure to know what it is asserting.
3. Rebuild on the toolkit at the house style.
4. Assert the canvas contract and the type floor (see `SCALE_LAW.md`).
5. Diff the drawn-string multiset against the original.
6. Render the page and **look at it** at 1:1.

## What to leave alone, and when to refuse

State the refusal criteria up front, because an agent under pressure to "finish" will
otherwise fake something:

* **No editable source exists** (the image is only inside the package, or carries no
  generator anywhere) → measure and report. Redrawing substitutes a *different* drawing for
  the one the author chose.
* **A JPEG or a scanned bitmap** → same. There is nothing to re-render.
* **The shipped bytes do not match any script** → the source is stale or the figure was
  edited by hand. Report it; re-running the script would silently swap a differently
  proportioned drawing into a delivered document.
* **The label cannot fit without a word change** → stop and escalate. Do not shorten.

"Left alone (and why)" is a required report section. A redraw pass that reports only its
successes is hiding the interesting half.

## The trap worth repeating

A figure's own `figcheck`-style helpers may be **silently disabled**: if a script puts
`sys.path.insert` *inside* its own `try: import <checker>` block, the import can never
resolve, the `ImportError` is swallowed, and the canvas assertion never runs — while the
script looks like it is checking. Move the path setup to module scope and assert that the
check actually fires on a build.

Similarly, an escape test that compares the raster's **size** with the nominal size cannot
see content hanging off one edge while there is slack on the other. Measure escapes on an
explicit margin box. See `reference/DEFECTS.md`.
