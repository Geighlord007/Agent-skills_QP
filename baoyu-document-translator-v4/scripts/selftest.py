# -*- coding: utf-8 -*-
"""Selftest (v4.3): fixture -> doc_trans extract/chunk/merge/write/qa/compare.
Asserts all 24 original structure-preservation checks + chunk-NN-runs.json + DOCX page_compare.
Usage: python selftest.py [workdir]
"""
import json
import os
import re
import subprocess
import sys
import zipfile
from pathlib import Path


def main() -> int:
    work = Path(sys.argv[1] if len(sys.argv) > 1 else "./selftest_run")
    work.mkdir(parents=True, exist_ok=True)
    skill = Path(__file__).resolve().parent
    cli = skill / "doc_trans.py"
    env = {**os.environ, "PYTHONIOENCODING": "utf-8"}

    def run(*args):
        r = subprocess.run(
            [sys.executable] + [str(a) for a in args],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            env=env,
        )
        if r.returncode not in (0, 1):
            print(r.stdout[-2000:], r.stderr[-2000:])
            raise SystemExit("FAILED: " + " ".join(map(str, args)))
        return r

    fx = work / "fixture.docx"
    run(skill / "build_fixture.py", fx)
    run(cli, "extract", fx, work / "extracted.json", "--md", work / "source.md")
    els = json.loads((work / "extracted.json").read_text(encoding="utf-8"))["elements"]
    keys = [e["key"] for e in els]
    checks = []
    checks.append(("first-page header extracted", any(k.startswith("p_headerfirst_0_") for k in keys)))
    checks.append(("textbox-or-ins run extracted", any(len(e["parts"]) == 2 and e["type"] == "paragraph" for e in els)))
    merged = [e for e in els if e["type"] == "table_cell" and e["key"].startswith("t_body_0_r0_")]
    checks.append(("h-merge dedup (row0 -> 2 physical cells)", len(merged) == 2))
    vmerge = [e for e in els if e["key"].startswith("t_body_0_r2_c2")]
    checks.append(("v-merge continuation dropped", len(vmerge) == 0))
    checks.append(("body textbox extracted", any(k == "txbx_0_p0" for k in keys)))
    checks.append(("SDT paragraph extracted", any(k == "p_sdt_0_p0" for k in keys)))
    checks.append(("hyperlink run extracted", any("hyperlinked phrase" in "".join(e["parts"]) for e in els)))
    checks.append(("multi-w:t run joined", any("First half second half in same run." == "".join(e["parts"]) for e in els)))
    ps = [e for e in els if e["key"] == "t_body_1_r0_c0"]
    checks.append(("para_splits recorded", bool(ps) and ps[0].get("para_splits") == [1, 2]))
    checks.append(("textbox tab alignment", any(
        e["key"] == "txbx_1_p0" and e["parts"] == [
            "Alpha sufficiently long textbox sentence one", "\t",
            "Beta sufficiently long textbox sentence two",
        ] for e in els)))
    checks.append(("SEQ result run excluded", any(
        "".join(e["parts"]) == "Table . Caption with field number." for e in els)))

    # New v4.3 checks: chunk --extracted emits chunk-NN-runs.json
    run(cli, "chunk", work / "source.md", work / "chunks", "4200", "--extracted", work / "extracted.json")
    checks.append(("chunk-01-runs.json emitted", (work / "chunks" / "chunk-01-runs.json").exists()))

    # Modified translation (TR: prefix) to prove write-back reaches every story
    lines = []
    for e in els:
        lines.append("<!--key:%s|runs:%d|-->" % (e["key"], e["runs"]))
        lines.append("TR: " + e["text"].replace("\n", "\nTR: ").replace("\t", "\tTR: "))
        lines.append("")
    (work / "translation.md").write_text("\n".join(lines), encoding="utf-8")

    run(cli, "merge", work / "extracted.json", work / "translation.md", work / "translated.json")
    # Force surgical on fixture test so selftest works deterministically on Windows and Linux alike
    run(cli, "write", fx, work / "output.docx", work / "translated.json", "--engine", "surgical")
    g = run(skill / "verify_structure.py", fx, work / "output.docx", work / "translated.json")
    checks.append(("structure gate PASS", g.returncode == 0))
    # Also verify unified doc_trans.py qa entry point runs cleanly (with synced md)
    md_synced = []
    tj_ok = json.loads((work / "translated.json").read_text(encoding="utf-8"))
    for e in tj_ok["elements"]:
        md_synced.append("<!--key:%s|runs:%d|-->" % (e["key"], e["runs"]))
        md_synced.append("".join(e["parts"]))
        md_synced.append("")
    (work / "translation_synced.md").write_text("\n".join(md_synced), encoding="utf-8")
    g_qa = run(cli, "qa", fx, work / "output.docx", work / "translated.json", work / "translation_synced.md")
    checks.append(("unified doc_trans qa PASS", g_qa.returncode == 0))

    # New v4.3 check: DOCX page_compare succeeds without ValueError
    cmp_res = run(cli, "compare", work / "extracted.json", work / "translated.json", work / "pages")
    checks.append(("DOCX page_compare PASS", cmp_res.returncode == 0 and (work / "pages" / "page-01.txt").exists()))

    with zipfile.ZipFile(work / "output.docx") as zf:
        outx = zf.read("word/document.xml").decode("utf-8")
    for frag, name in (
        ("TR: Textbox line one.", "textbox write-back"),
        ("TR: SDT caption line.", "SDT write-back"),
        ("hyperlinked phrase", "hyperlink run write-back"),
        ("TR: First half second half in same run.", "multi-w:t single-write"),
        ("TR: Cover Title Block Here", "cover consolidation"),
        ("TR: Line one of cell", "para_splits cell p1"),
        ("TR: Line two of cell", "para_splits cell p2"),
        ("TR: Beta sufficiently long textbox sentence two", "textbox tab write-back"),
    ):
        checks.append((name, frag in outx))

    # Gate must catch wrong text in a textbox story
    tj = json.loads((work / "translated.json").read_text(encoding="utf-8"))
    for e in tj["elements"]:
        if e["key"] == "txbx_1_p0":
            e["parts"] = ["ZZZ nonexistent textbox sentence completely different here", "\t", ""]
    (work / "trunc_tb.json").write_text(json.dumps(tj, ensure_ascii=False), encoding="utf-8")
    run(cli, "write", fx, work / "output_tb.docx", work / "trunc_tb.json", "--engine", "surgical")
    g2 = run(skill / "verify_structure.py", fx, work / "output_tb.docx", work / "translated.json")
    checks.append(("gate catches textbox wrong-text", g2.returncode == 1))

    # Node preservation
    def cnt(p, pat):
        with zipfile.ZipFile(p) as zf:
            x = zf.read("word/document.xml").decode("utf-8")
            if "word/footer1.xml" in zf.namelist():
                x += zf.read("word/footer1.xml").decode("utf-8")
        return len(re.findall(pat, x))

    for pat, name in ((r"<w:instrText", "PAGE field instrText"), (r"<w:ptab", "ptab"), (r"<w:ins", "tracked ins")):
        checks.append(("%s preserved" % name, cnt(fx, pat) == cnt(work / "output.docx", pat)))

    fail = [n for n, ok in checks if not ok]
    for n, ok in checks:
        print(("PASS " if ok else "FAIL ") + n)
    print(f"SELFTEST ({len(checks) - len(fail)}/{len(checks)}):", "OK" if not fail else f"FAILED {fail}")
    return 0 if not fail else 1


if __name__ == "__main__":
    sys.exit(main())
