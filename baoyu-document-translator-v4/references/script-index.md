# 脚本清单

```
baoyu-document-translator-v4/
├── SKILL.md                          # 流程骨架
├── scripts/
│   ├── extract_v3.py                 # 合一提取器：DOCX + PPTX（v3 主入口）
│   ├── render_slides.py              # PPTX 逐页导出 JPG（Windows PowerPoint COM / 非 Win 回退 LibreOffice + PyMuPDF）
│   ├── ocr_slides.py                 # 图内文字登记（AI Studio OCR，保留带位置 JSONL；无 token 时降级跳过）
│   ├── slide_bundles.py              # 按页分组构建翻译单元
│   ├── build_dispatch.py             # 任务书生成（translate/review/visual/unify）
│   ├── api_call.py                   # 任务书 → OpenAI 兼容模型接口 → 产出文件（四角色并发，支持 --base-url / 环境变量）
│   ├── apply_patches.py              # 补丁落稿 + run_splits.json + translation.md
│   ├── merge_v3.py                   # 合并 + run 切分一步完成（v3 主入口）
│   ├── write_v3.py                   # 合一写回器：DOCX WIR/surgical 直接导入分发 + PPTX 嵌套 key（v3 主入口）
│   ├── qa_v3.py                      # 单一 QA 入口：结构/文本/格式/数字（v3 主入口）
│   ├── page_compare.py               # 逐页中英对照视图（供 DOCX 并行逐页抽查）
│   ├── extract_docx_v2.py            # DOCX 提取内核（extract_v3 调用；独立可用）
│   ├── json_to_markdown_v2.py        # keyed JSON → keyed markdown（DOCX Step 2）
│   ├── chunk_keyed.py                # marker-safe chunk splitter（DOCX Step 3）
│   ├── reconcile_consistency.py      # TOC↔headings/captions reconcile
│   ├── merge_keyed_structure_aware.py# 结构化合并内核（merge_v3 调用；独立可用）
│   ├── write_docx_surgical.py        # w:t-level write-back, preserves fields/images（write_v3 分发目标）
│   ├── write_docx_wir.py             # WIR-engine write-back (Linux only)（write_v3 分发目标）
│   ├── engine_select.py              # environment-adaptive engine decision（write_v3 直接导入）
│   ├── xlsx_translate.py             # XLSX: shared strings + sheet names only (format-safe)
│   ├── localize_cjk_en.py            # CJK→EN layout: fonts/numbering/tracking/justify/fields
│   ├── paginate_plan.py              # pagination pre-pass + bounded --repair
│   ├── toc_pages.py                  # rewrite TOC page numbers from rendered PDF
│   ├── verify_structure.py           # DOCX structure+coverage gate（qa_v3 调用）
│   ├── render_pdf.ps1                # DOCX→PDF via Word COM / LibreOffice (Step 7b)
│   ├── render_qa.py                  # rendered QA: blanks/CJK/TOC-pages/montage (Step 7b)
│   ├── build_fixture.py              # structural fixture generator (selftest)
│   └── selftest.py                   # one-command regression selftest
├── references/
│   ├── docx.md                       # DOCX：key 规则、提取范围、写回引擎
│   ├── pptx.md                       # PPTX：key 规则、形状树提取、run 写回
│   ├── translation-workflow.md       # DOCX 分块流程细则与工作产物清单（及共用 01-context / 规格单）
│   ├── qa-pack.md                    # 可选质检包、渲染 QA、CJK→EN 本地化、Troubleshooting
│   ├── script-index.md               # 本文件
│   ├── subagent-prompt-template.md   # 任务书规则、补丁格式与子代理执行模板
│   ├── schema-v2.md                  # Keyed JSON schema
│   ├── wir-integration.md            # How to use docx skill WIR engine
│   ├── cjk-en-localization-pitfalls.md  # CJK→EN localization checklist
│   ├── optimization-notes.md         # 架构演进记录与上游问题
│   └── safe-docx-evaluation.md       # Safe Docx 实测数据（留痕交付可选）
```

## Dependencies

核心 Python 依赖（全平台）：
```bash
pip install python-docx python-pptx lxml PyMuPDF Pillow requests
```

Windows 下启用 PowerPoint / Word COM 导出（`render_slides.py`、`render_pdf.ps1`）：
```bash
pip install pywin32
```

非 Windows / 无 Office 环境请安装 LibreOffice（确保 `soffice` 或 `libreoffice` 在 `PATH` 中），`render_slides.py` 将自动回退到 LibreOffice + PyMuPDF。

可选本地 OCR QA：
```bash
pip install paddleocr
```

可选 WIR 写回路径（仅 Linux 且含可导入原生扩展）需要 `docx` skill 及其 `scripts/engine/`（可通过 `DOCX_SKILLS_DIR` 环境变量指定目录）。
