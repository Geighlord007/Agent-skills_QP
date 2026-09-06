---
name: company-bg-info
description: Use when the user asks for a background-info / BG-info / company-profile Word document on a potential partner or customer (e.g., “写一个 [公司] 的 BG info” / “参考 Glanbia_BG.docx 的格式”). Generates a single .docx summarising who the company is, why they are strategically relevant, what they sell, how they are organised, recent M&A, and how a partnership could look — with inline hyperlinks and a Sources section.
---

# Partner Company Background Info (BG Info) Skill

Use this skill when the user asks for a **background-info / BG-info / company-profile Word document** on a potential partner or customer (e.g., “写一个 [公司] 的 BG info” / “参考 Glanbia_BG.docx 的格式”).

The deliverable is a single `.docx` that summarises who the company is, why they are strategically relevant, what they sell, how they are organised, recent M&A, and how a partnership could look — with **inline hyperlinks and a Sources section**.

---

## 1. Output structure (follow this order)

1. **Document title** — “[Company] BG info”
2. **Main heading** — “[Company]”
3. **Company overview** — 1–2 paragraphs: HQ, revenue, market position, listed status, division structure.
4. **Strategic context** — 1 short paragraph on why this company is relevant to the user’s platform/technology; include a key investor-slide or chart image if available.
5. **Operating divisions / business segments** — 4-column table: Division, Description, Key brands/products, Recent revenue/EBITDA.
6. **Selected ingredient/product brands** — Subsections by category with short, factual brand descriptions.
7. **Key financials** — 3-column table: Metric, Year-1, Year-2 / guidance.
8. **Alternative proteins / precision fermentation / relevant technology layout** — Fact block or table covering:
   - Public statements (CMD/AR slides, CEO/CSO quotes)
   - Internal initiatives / business units
   - Partnerships, JVs and licensing deals
   - Investments / venture bets
   - M&A deals in the space
   If none, state clearly: “No public internal platform announced; strategic interest signalled by X.”
9. **Recent M&A / transactions** — 4-column table: Year, Target/asset, Transaction amount, Description.
10. **Innovation & partnership landscape** — Concise subsections:
    - Open innovation / R&D facilities and customer-collaboration model
    - Relevant product line (e.g., Bioferrin)
    - Stance on precision fermentation / synthetic biology
    - Proposed collaboration hook (one paragraph)
11. **Sources** — Bulleted list of all URLs used, rendered as blue hyperlinks.

---

## 2. Visual format (matching Glanbia_BG.docx)

- **Font:** Schibsted Grotesk for all text.
- **Title:** 14 pt, bold, dark grey `#333333`.
- **Main company heading:** 18 pt, bold, dark grey `#333333`.
- **Body:** 10 pt, dark grey `#333333`, 1.5 line spacing.
- **Section headings:** 10 pt, **bold**, olive green `#617D24`. Use Word styles `Heading 1` and `Heading 2`; do not make them dramatically larger than body text.
- **Tables:** `Table Grid` style, header row shaded `#E5E5E5`, 9 pt text, vertically centred.
- **Images:** centre-aligned, width ~5.5 in, italic caption in 8 pt `#666666`.
- **Hyperlinks:** blue `#0563C1`, underlined, in-line where a claim is made; collect the same URLs again in the Sources section.

Full format specification: `references/format-spec.md`

---

## 3. Data-collection workflow

1. **Ask / confirm target** and any existing materials (reports, source folders, URLs).
2. **Search the web** for:
   - Latest annual report and CMD/Investor Day deck
   - Revenue, EBITDA, EPS, ROCE targets
   - Division / segment structure and brands
   - Recent acquisitions, divestitures and investments (including VC/CVC if any)
   - Any internal initiatives, partnerships, JVs or investments in **precision fermentation, alternative proteins, synthetic biology or related technology**
   - Leadership quotes on innovation, open collaboration, or relevant technology
   - Relevant product pages (e.g., lactoferrin, whey proteins, premix)
3. **Use previously collected sources** in the user’s `output/sources/` folder (PDFs, images, text extracts).
4. **Extract key slide as image** if an investor deck is available: use `scripts/extract_pdf_page.py` to render the relevant page to PNG and insert it.
5. **Write the docx** with `scripts/generate_bg_doc.py` (JSON → DOCX) or python-docx directly.
6. **Validate** the JSON with `scripts/validate_bg_json.py` before generation.
7. **Verify** the file opens and that external hyperlinks are present.

Data-collection checklist: `references/data-collection-checklist.md`
JSON schema: `references/json-schema.md`

---

## 4. Code templates

### 4.1 JSON-driven generation (recommended)

Populate a JSON file following `references/json-schema.md`, then run:

```bash
python scripts/validate_bg_json.py --input data.json
python scripts/generate_bg_doc.py --input data.json --output /home/adam18294/output/Company_BG_info.docx
```

### 4.2 PDF page extraction

```bash
python scripts/extract_pdf_page.py --input report.pdf --page 5 --output /tmp/slide.png --dpi 200
```

### 4.3 Inline python-docx template

If the JSON pipeline is too rigid, use the inline python-docx template from the original SKILL.md (Section 4) as a starting point.

---

## 5. Image handling

- If the company has an investor PDF, locate the most relevant page and render it:

```bash
python scripts/extract_pdf_page.py --input investor-deck.pdf --page 3 --output /tmp/key-slide.png --dpi 200
```

- Insert into the Word doc with a caption.
- Also insert the company logo if available (top-right, ~1.2 in wide).

---

## 6. Sources discipline

- Every factual claim that came from a specific webpage or document should be hyperlinked inline **or** appear in the Sources section.
- Typical sources to include:
  - Annual report / CMD deck download page
  - Investor relations results page
  - Company “Our Journey” / M&A history page
  - Product-page URLs for key brands
  - Leadership / innovation quotes page
- If a URL is long or repetitive, use a short label in the Sources section and hyperlink it.

---

## 7. Quality checks before finishing

- [ ] Document opens without corruption.
- [ ] All tables have a shaded header row and 9 pt text.
- [ ] Section headings are 10 pt bold green, not oversized.
- [ ] At least one relevant image/chart is inserted.
- [ ] No unnecessary analytical commentary; the doc presents facts, tables, and a one-paragraph proposed hook.
- [ ] An “Alternative proteins / precision fermentation / relevant technology layout” section is included (even if the conclusion is “none publicly announced”).
- [ ] Investments / venture activity are captured if they exist.
- [ ] File is saved under `output/` with naming convention `[Company]_BG_info.docx`.

---

## 8. Notes

- If the user provides an existing reference `.docx` and says “match this format exactly”, prefer the **WIR engine** in the `docx` skill to read and clone that document rather than building from scratch.
- If the user’s existing report is long (e.g., a full strategic intelligence report), distill it into the shorter BG-info structure above; do not paste the whole report.
- **Keep analysis minimal.** BG Info is a fact pack: who the company is, what they sell, what they have done, and a one-paragraph collaboration hook. Avoid long strategic essays or competitor profiles.
- Always use the **same language** as the user’s request for the skill response, but default to English for the document unless the user asks otherwise.
