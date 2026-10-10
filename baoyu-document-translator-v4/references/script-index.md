# 脚本清单

```
baoyu-document-translator-v4/
├── SKILL.md                          # 流程骨架
├── scripts/
│   ├── extract_v3.py                 # 合一提取器：DOCX + PPTX（v3 主入口）
│   ├── render_slides.py              # PPTX 逐页导出 JPG（PowerPoint COM）
│   ├── ocr_slides.py                 # 图内文字登记（AI Studio OCR，保留带位置 JSONL）
│   ├── slide_bundles.py              # 按页分组构建翻译单元
│   ├── build_dispatch.py             # 子代理任务书生成（translate/review/visual）
│   ├── apply_patches.py              # 补丁落稿 + run_splits.json + translation.md
│   ├── merge_v3.py                   # 合并 + run 切分一步完成（v3 主入口）
│   ├── write_v3.py                   # 合一写回器：DOCX WIR/surgical 分发 + PPTX 嵌套 key（v3 主入口）
│   ├── qa_v3.py                      # 单一 QA 入口：结构/文本/格式/数字（v3 主入口）
│   ├── page_compare.py               # 逐页中英对照视图（供并行逐页抽查）
│   ├── extract_docx_v2.py            # DOCX 提取内核（extract_v3 调用；独立可用）
│   ├── json_to_markdown_v2.py        # keyed JSON → keyed markdown (Step 2)
│   ├── chunk_keyed.py                # marker-safe chunk splitter (Step 3)
│   ├── reconcile_consistency.py      # TOC↔headingscaptions reconcile (Step 3/5)
│   ├── merge_keyed_structure_aware.py# 结构化合并内核（merge_v3 调用；独立可用）
│   ├── write_docx_surgical.py        # w:t-level write-back, preserves fields/images（write_v3 分发目标）
│   ├── write_docx_wir.py             # WIR-engine write-back (Linux only)（write_v3 分发目标）
│   ├── engine_select.py              # environment-adaptive engine decision（write_v3 调用）
│   ├── xlsx_translate.py             # XLSX: shared strings + sheet names only (format-safe)
│   ├── localize_cjk_en.py            # CJK→EN layout: fonts/numbering/tracking/justify/fields
│   ├── paginate_plan.py              # pagination pre-pass + bounded --repair (Step 6)
│   ├── toc_pages.py                  # rewrite TOC page numbers from rendered PDF (Step 7)
│   ├── verify_structure.py           # DOCX structure+coverage gate（qa_v3 调用）
│   ├── render_pdf.ps1                # DOCX→PDF via Word COM / LibreOffice (Step 7b)
│   ├── render_qa.py                  # rendered QA: blanks/CJK/TOC-pages/montage (Step 7b)
│   ├── build_fixture.py              # structural fixture generator (selftest)
│   ├── selftest.py                   # one-command regression selftest
│   ├── extract_pptx_v2.py            # legacy: PPTX 顶层形状提取（组合形状子级取不到，已被 extract_v3 取代）
│   ├── markdown_to_json_v2.py        # legacy naive merge（空 run 污染，已被 merge_v3 取代）
│   ├── write_docx_v2.py              # legacy run.text write-back（破坏域/绘图，已被 write_v3 取代）
│   ├── write_pptx_v2.py              # legacy: PPTX 顶层 key 写回（嵌套形状不可写，已被 write_v3 取代）
│   └── validate_v2.py                # keyed JSON sanity (legacy, weak — see Troubleshooting)
├── references/
│   ├── docx.md                       # DOCX：key 规则、提取范围、写回引擎
│   ├── pptx.md                       # PPTX：key 规则、形状树提取、run 写回
│   ├── translation-workflow.md       # 翻译流程细则与工作产物清单
│   ├── qa-pack.md                    # 可选质检包、渲染 QA、CJK→EN 本地化、Troubleshooting
│   ├── script-index.md               # 本文件
│   ├── subagent-prompt-template.md   # parallel-chunk prompt template (v2.5：翻译+审校+逐页抽查)
│   ├── schema-v2.md                  # Keyed JSON schema
│   ├── wir-integration.md            # How to use docx skill WIR engine
│   ├── cjk-en-localization-pitfalls.md  # CJK→EN localization checklist (v2.1)
│   ├── optimization-notes.md         # v1 → v2 rationale and upstream issues
│   └── safe-docx-evaluation.md       # Safe Docx 实测数据（留痕交付可选）
```

## Dependencies

```bash
pip install python-docx python-pptx lxml PyMuPDF Pillow
```

For OCR image QA (optional):
```bash
pip install paddleocr
```

The optional WIR path (experimental, non-Windows only) additionally needs the `docx`
skill with an importable `scripts/engine/`.
