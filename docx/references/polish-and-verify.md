# Route 4 — Polish & Verify Delivered `.docx` (成品文档精修与验尸)

Use this reference when a `.docx` report has already been built (via Route 1/2/3 or externally) and needs **post-build figure legibility polish, byte-exact width widening, structural invariant checking, or serialized Word open verification**.

---

## 1. Three-Lever Figure Legibility Order (Do Least-Invasive First)

For every chart embedded in Word, printed typography obeys the Scale Law:

$$\text{on\_page\_pt} = \text{authored\_pt} \times \frac{\text{display\_pt}}{\text{canvas\_pt}}$$

Before redrawing any chart, check levers in strict order:

1. **Check the source math first** (`consulting-chart/scripts/scale_law.py <chart.svg>`):
   - Never guess legibility from a thumbnail or a single up-sampled pixel render.
   - Standard column width on A4 (2.5 cm margins) is **~453 pt (16.0 cm / 5,760,000 EMU)**; target on-page floor is **≥ 6.5 pt** (≥ 5.5 pt for minor footnotes).
2. **Lever 1 — Byte-exact widening (zero redraw, zero pixel touch)**:
   - If the chart is printed well below the column width (e.g. 280–380 pt) and only needs larger printed text, widen its `<wp:extent>` and `<a:ext>` in place:
   ```bash
   python scripts/polish/verify_counts.py capture report.docx --out baseline.json
   python scripts/polish/widen_extent.py report.docx --list
   python scripts/polish/widen_extent.py report.docx --target rId12=445pt --dry-run
   python scripts/polish/widen_extent.py report.docx --target rId12=445pt
   python scripts/polish/verify_counts.py check report.docx --baseline baseline.json
   ```
   - `widen_extent.py` atomically updates only the 4 `cx`/`cy` digits and proves every other ZIP part and XML segment is byte-identical.
3. **Lever 2 — Redraw source via `consulting-chart`**:
   - Only re-author/re-render the chart if it is already near full column width (`≥ 430 pt`) or has genuine clipping, overlap, or data-encoding defects.

---

## 2. Final Delivery Verification Sequence

Run these checks in order before handing a polished `.docx` to the user:

```bash
# 1. Structural count invariant (no accidental paragraph/table/drawing loss)
python scripts/polish/verify_counts.py check report.docx --baseline baseline.json

# 2. OOXML business rules + OpenXML XSD validation
python scripts/docx_cli.py validate report.docx

# 3. Serialized real host-app open test (Word COM on Windows, LibreOffice elsewhere)
python scripts/polish/verify_word_open.py report.docx
```

---

## 3. Eight Verification Disciplines (Hard-Won Engineering Rules)

Every automated checker can report a false clean or false alarm when fed the wrong input. Follow these eight rules whenever verifying a finished report:

1. **Validate the input, not just the formula.** Before trusting any pass/fail number, verify *what artifact* it read and *when* it was written (e.g., check file magic bytes rather than `.jpeg`/`.png` extension; never trust a grepped source constant over the actual embedded asset).
2. **Cross-check with an independent instrument.** Pair arithmetic Scale Law with visual inspection; pair raw XML counts (`verify_counts.py`) with OOXML XSD (`docx_cli.py validate`) and host-app open (`verify_word_open.py`).
3. **Inspect the artifact at 1:1 when any metric looks dramatic.** A single high-DPI render (e.g. 600 DPI up-sampling a 200 DPI Word raster) can distort pixel heuristics by ~38% and flag healthy 6.4 pt labels as "2.0 pt". Always inspect at 1:1 and check the source math before acting.
4. **State the instrument's scope explicitly.** Every verifier should state what it did *not* check (e.g., `verify_counts.py` proves XML structure did not drift; it does not check visual overlap or prose accuracy).
5. **Never accept a silent no-result.** Zero matched files, missing summary output, or silent subprocess decoding errors must exit non-zero. Always pass `encoding="utf-8", errors="replace"` to subprocesses.
6. **Serialize Word COM verification.** Never launch multiple Word COM instances in parallel across agents or threads — concurrent Word automation causes non-deterministic false corruption errors on healthy files.
7. **Prefer the conservative reading when two checks disagree**, and document the discrepancy rather than suppressing the stricter warning.
8. **Capture a baseline before surgical edits.** Always snapshot structural counts (`verify_counts.py capture`) before modifying embedded drawings or XML parts so any unintended deletion is caught immediately.
