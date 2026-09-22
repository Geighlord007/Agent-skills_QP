# -*- coding: utf-8 -*-
"""Structure-aware merge of keyed translation.md back into extracted.json.

Replaces the skill's markdown_to_json_v2 split (which mis-distributes text into
empty spacer runs and misplaces TOC page numbers). This version uses the SOURCE
parts as a structural template:
  - empty runs ("")  -> stay empty (formatting spacers preserved)
  - tab runs  ("\t") -> stay "\t"
  - newline runs("\n")-> stay "\n"
  - text runs        -> receive the translated text, distributed only across
                        real text runs within each delimiter-bounded segment,
                        using punctuation-boundary-aware proportional split.

Usage: python merge_keyed.py extracted.json translation.md translated.json
"""
import sys, json, re
from pathlib import Path

MARKER_RE = re.compile(r"<!--\s*key:([^|]+)\|runs:(\d+)(?:\|type:([^\s>]+))?\|?\s*-->")
DELIMS = ("\t", "\n")


def parse_translation(md_text):
    """key -> translated text (tabs/newlines preserved; trailing separators stripped)."""
    lines = md_text.split("\n")
    result = {}
    cur_key = None
    buf = []

    def flush():
        if cur_key is None:
            return
        # strip trailing blank/whitespace-only separator lines, keep leading tabs
        while buf and buf[-1].strip() == "":
            buf.pop()
        result[cur_key] = "\n".join(buf)

    for ln in lines:
        m = MARKER_RE.match(ln.strip())
        if m:
            flush()
            cur_key = m.group(1).strip()
            buf = []
        else:
            if cur_key is not None:
                buf.append(ln)
    flush()
    return result


def find_boundary(text, pos, radius=40):
    if not text:
        return 0
    pos = max(0, min(pos, len(text)))
    punct = "\u3002\uff0c\uff1b\uff01\uff1f.,;:!? \t\n"
    for j in range(pos, min(pos + radius, len(text))):
        if text[j] in punct:
            return j + 1
    for j in range(pos, max(pos - radius, -1), -1):
        if 0 <= j < len(text) and text[j] in punct:
            return j + 1
    return pos


def distribute(text, src_lens, n):
    """Split `text` into n parts proportional to src_lens (list len n), boundary-aware."""
    if n <= 1:
        return [text]
    total = sum(src_lens)
    if total <= 0:
        src_lens = [1] * n
        total = n
    parts = []
    start = 0
    for i in range(n - 1):
        span = int(round(src_lens[i] / total * len(text)))
        end = find_boundary(text, start + span)
        end = max(start, min(end, len(text)))
        parts.append(text[start:end])
        start = end
    parts.append(text[start:])
    return parts


def source_segments(parts):
    """Split source parts into segments bounded by delimiter runs (\t or \n).
    Returns list of segments; each segment = list of (index, part) for TEXT runs,
    plus we remember delimiter positions separately."""
    segments = []       # list of list-of-indices (text runs in this segment)
    cur = []
    layout = []         # ('delim', i, ch) | ('text', i) | ('empty', i)
    for i, p in enumerate(parts):
        if p in DELIMS and p != "":
            layout.append(("delim", i, p))
            segments.append(cur)
            cur = []
        elif p == "":
            layout.append(("empty", i))
            # empty runs do NOT split segments
        else:
            layout.append(("text", i))
            cur.append(i)
    segments.append(cur)
    return segments, layout


def build_parts(src_parts, translated, para_splits=None):
    n = len(src_parts)
    out = [""] * n
    # preserve delimiters and empties first
    for i, p in enumerate(src_parts):
        if p in DELIMS and p != "":
            out[i] = p
    segments, layout = source_segments(src_parts)

    # multi-paragraph cells without \n runs: keep the translator's line breaks aligned
    # to the source paragraph boundaries (para_splits = cumulative run counts)
    if para_splits and len(para_splits) > 1 and not any(p == "\n" for p in src_parts) \
            and "\n" in translated:
        lines = translated.split("\n")
        k = len(para_splits)
        if len(lines) >= k:
            segs = lines[:k - 1] + ["\n".join(lines[k - 1:])]
        else:
            segs = lines + [""] * (k - len(lines))
        prev = 0
        for j, end in enumerate(para_splits):
            slice_idx = [i for i in range(prev, end)
                         if src_parts[i] != "" and src_parts[i] not in DELIMS]
            tseg = segs[j] if j < len(segs) else ""
            if slice_idx:
                lens = [max(len(src_parts[i]), 1) for i in slice_idx]
                pieces = distribute(tseg, lens, len(slice_idx))
                for idx, piece in zip(slice_idx, pieces):
                    out[idx] = piece
            prev = end
        return out, ""

    # split translated text by the same delimiters present in source, in order
    t_segs = re.split(r"[\t\n]", translated)

    if len(t_segs) != len(segments):
        # Mismatch: translated text has a different number of \t/\n than the source
        # structure (translator line-wrapping, or a dropped leading tab). Fall back to
        # flowing the translated text across the real text runs, but first strip any
        # delimiter the SOURCE does not have as a standalone run (so we don't inject
        # line breaks / tabs that weren't in the original). Source delimiter runs are
        # already preserved in `out`.
        src_has_tab = any(p == "\t" for p in src_parts)
        src_has_nl = any(p == "\n" for p in src_parts)
        joined = translated
        if not src_has_nl:
            joined = joined.replace("\n", " ")
        if not src_has_tab:
            # keep page-number tabs ("\t5"); degrade other tabs to spaces
            joined = re.sub(r"\t(?!\d)", " ", joined)
        joined = re.sub(r"[ ]{2,}", " ", joined).strip()
        all_text_idx = [i for i, p in enumerate(src_parts) if p != "" and p not in DELIMS]
        if all_text_idx:
            lens = [max(len(src_parts[i]), 1) for i in all_text_idx]
            pieces = distribute(joined, lens, len(all_text_idx))
            for idx, piece in zip(all_text_idx, pieces):
                out[idx] = piece
        return out, "SEG_MISMATCH(%d src vs %d trans)" % (len(segments), len(t_segs))

    warn = ""
    for seg_idx, text_run_idxs in enumerate(segments):
        tseg = t_segs[seg_idx]
        if not text_run_idxs:
            if tseg.strip():
                warn += "SEG%d_HAS_TEXT_NO_RUN;" % seg_idx
            continue
        lens = [max(len(src_parts[i]), 1) for i in text_run_idxs]
        pieces = distribute(tseg, lens, len(text_run_idxs))
        for idx, piece in zip(text_run_idxs, pieces):
            out[idx] = piece
    return out, warn


def main():
    extracted_path, md_path, out_path = sys.argv[1], sys.argv[2], sys.argv[3]
    data = json.loads(Path(extracted_path).read_text(encoding="utf-8"))
    md = Path(md_path).read_text(encoding="utf-8")
    trans = parse_translation(md)

    missing, warns = [], []
    for e in data["elements"]:
        k = e["key"]
        if k not in trans:
            missing.append(k)
            continue
        src_parts = e.get("parts", [])
        new_parts, w = build_parts(src_parts, trans[k], e.get("para_splits"))
        # enforce exact run count
        runs = e.get("runs", len(src_parts))
        if len(new_parts) != runs:
            # pad/truncate defensively to match source length
            if len(new_parts) < runs:
                new_parts += [""] * (runs - len(new_parts))
            else:
                new_parts = new_parts[:runs]
        e["parts"] = new_parts
        e["translated_text"] = trans[k]   # keep for QA
        if w:
            warns.append((k, w))

    if missing:
        print("MISSING %d keys: %s" % (len(missing), missing[:20]))
    if warns:
        print("WARNINGS %d:" % len(warns))
        for k, w in warns[:40]:
            print("  %s: %s" % (k, w))
    else:
        print("No segment warnings.")

    Path(out_path).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print("Written %s (%d elements)" % (out_path, len(data["elements"])))


if __name__ == "__main__":
    main()
