# Safe Docx evaluation & integration notes（2026-09-22）

> 中文速读：本 skill 的写回引擎有两种（Linux/WSL2 用 WIR，原生 Windows 用 surgical）。
> 市面上的 [Safe Docx](https://github.com/usejunior/safe-docx) 提供我们缺的**留痕交付**
> （Word 原生修订痕迹 + 干净版/留痕版双输出）。实测：它能写回 92% 的段落，
> 但**不支持"跨多个 run 且与域结果相交"的段落**，且全篇 diff（`compare`）在 WPS 重结构文档上直接报错。
> 结论：**组合使用**——普通段落交给它拿留痕，域相交/脚注/页眉页脚仍用 surgical。
> 详见下文。

## 1. What Safe Docx is

A local MCP server + CLI (`@usejunior/safe-docx`, Apache-2.0, Node) that reads, searches,
edits, compares, converts and saves DOCX/ODT/Google Docs while preserving structure.
Key capabilities we do **not** have:

| Capability | Safe Docx | this skill |
|---|---|---|
| Word-native tracked changes on write (`w:ins`/`w:del`/`w:rPrChange`) | ✅ | ❌ |
| Clean + tracked dual output (`save_format=both`) | ✅ | ❌ |
| Accept/reject revisions by id or author | ✅ | ❌ |
| Comments incl. threaded replies | ✅ | ❌ |
| Footnote add/update/delete | ✅ | read/translate only |
| Document comparison → redline | ✅ (unusable on our WPS docs, see §3) | ❌ |
| Stable paragraph IDs (`_bk_*`), edit by id or by **any bookmark name** | ✅ | index-based |
| Full-document translation pipeline (extraction, chunking, terminology, QA) | ❌ | ✅ |

## 2. Measured coverage (production report, 2026-09-22)

Our extraction vs Safe Docx `read-file`:

| Area | covered by Safe Docx |
|---|---|
| table cells | 99.4% (324/326) |
| body paragraphs | 87.4% (195/223) |
| text boxes | 100% |
| headers / footers | 100% |
| footnotes | not in `read-file` — use `get-footnotes` |

## 3. A/B result (full document, 513 mapped paragraphs)

| Metric | this skill (surgical) | Safe Docx |
|---|---|---|
| paragraphs writable | all (809 elements incl. all stories) | 473 applied / 40 failed / 104 unmatched |
| **tracked changes** | ❌ none | ✅ 471 `w:ins` + 473 `w:del`, opens in Word |
| clean output | 57 pages, 0 blank, 101 CJK lines (deliberate bilingual retention) | 51 pages, 1 blank, 374 CJK lines |
| speed | seconds | 560 s for 513 sequential calls |
| whole-document `compare` | — | ❌ `OpaquePassthroughError` on WPS-heavy docs |

Hard limits observed:

- `Edit spans multiple runs and intersects a field result. This is currently unsupported
  in Safe-Docx TS.` → paragraphs crossing PAGE/SEQ/PAGEREF field results cannot be edited.
- Text matching (our text → its paragraph id) fails on headers/footers/footnotes because our
  tab/field representation differs. Its `--node-ids` accepts **arbitrary bookmark names**, so
  writing our own hidden bookmark anchors makes dispatch deterministic (see §5, item ①).
- Side effect: its path re-evaluated the header date field (Sep 22 → Sep 23) and produced one
  extra blank page.

## 4. Recommended architecture (combination, not replacement)

```
extract / translate / QA        ← keep ours (all-story coverage, terminology, gate, render QA)
        │
write-back dispatch ├─ plain paragraphs ──────→ Safe Docx replace_text  ⇒ tracked redline
                    └─ field-intersecting / footnotes / header-footer / textboxes → our surgical
deliverable = clean output (existing) + tracked output (new, client can accept/reject)
```

## 5. TODO to productionise (≈1 day, zero cost)

1. **Anchors** (2–4 h): stamp invisible bookmarks (`w:bookmarkStart`) during extraction, then
   edit by bookmark name via `--node-ids`; recovers the 104 unmatched paragraphs.
2. **Integration script** (½ day): per-paragraph `replace_text` + automatic fallback to
   surgical on failure + dual output save.
3. Keep our surgical as the permanent fallback; pin the Safe Docx version (young project — v0.19.x).

## 6. How to reproduce

```powershell
npm install -g @usejunior/safe-docx@0.19.1      # Node + npm required
$env:SAFE_DOCX_ALLOWED_ROOTS = "<workdir>"      # its own path allow-list
$env:SAFE_DOCX_AI_AUTHOR     = "AI Translator"  # revision author name

safe-docx read-file <src.docx> --format json --limit 5000 > read.json
# map our extracted/translated keys to its paragraph ids, then per-paragraph replace_text:
#   dispatchToolCall(mgr, 'replace_text', {file_path, target_paragraph_id, old_string, new_string})
#   dispatchToolCall(mgr, 'save', {file_path, save_to_local_path, tracked_save_to_local_path})
safe-docx edit <copy.docx> --replace <id> "<old>" "<new>" -o <clean.docx>   # CLI equivalent (clean only)
```

License note: Safe Docx is Apache-2.0 (its repo LICENSE text in one commit reads MIT — both
permissive, verify the repository LICENSE before redistribution).
