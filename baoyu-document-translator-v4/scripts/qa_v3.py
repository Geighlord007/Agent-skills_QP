# -*- coding: utf-8 -*-
"""单一 QA 入口 v4.3：结构 / 文本 / 格式 / 数字 / 渲染 一次跑完，任何阻断项不过即 exit 1。

用法:
  python qa_v3.py source.docx|pptx output translated.json translation.md [--numerals whitelist.json] [--render out.pdf]
"""
import json
import re
import subprocess
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

NUM_RE = re.compile(r"\d+(?:\.\d+)?")


def norm(s):
    return re.sub(r"\s+", "", s)


def parse_blocks(md_text):
    blocks, cur, buf = {}, None, []
    for ln in md_text.split("\n"):
        m = re.match(r"<!--\s*key:([^|]+)\|", ln.strip())
        if m:
            if cur:
                blocks[cur] = "\n".join(buf)
            cur, buf = m.group(1), []
        elif cur is not None:
            buf.append(ln)
    if cur:
        blocks[cur] = "\n".join(buf)
    return blocks


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def parts_joined(e):
    parts = e.get("parts", [])
    splits = e.get("para_splits") or []
    if len(splits) <= 1:
        return "".join(parts)
    segs, prev = [], 0
    for end in splits:
        segs.append("".join(parts[prev:end]))
        prev = end
    if prev < len(parts):
        segs.append("".join(parts[prev:]))
    return "\n".join(segs)


def check_pptx_roundtrip(src_data, out_data, tr_data, problems):
    src = {e["key"]: e for e in src_data["elements"]}
    out = {e["key"]: e for e in out_data["elements"]}
    tr = {e["key"]: e for e in tr_data["elements"]}
    if set(src) != set(out):
        problems.append("key 集合与原件不一致: %s" % sorted(set(src) ^ set(out))[:10])
    for key, se in src.items():
        oe = out.get(key)
        if oe is None:
            continue
        if oe["runs"] != se["runs"]:
            problems.append("%s：run 数量 %d → %d" % (key, se["runs"], oe["runs"]))
        if oe.get("run_styles") != se.get("run_styles"):
            problems.append("%s：格式签名变化" % key)
        if oe.get("para_splits") != se.get("para_splits"):
            problems.append("%s：分段切分变化" % key)
        if key in tr and oe["parts"] != tr[key]["parts"]:
            problems.append("%s：写回文本与译文不一致" % key)


def check_numbers(src_data, tr_data, allow, problems):
    src = {e["key"]: e for e in src_data["elements"]}
    for e in tr_data["elements"]:
        if "translated_text" not in e:
            continue
        key = e["key"]
        if key not in src:
            continue
        s_nums = NUM_RE.findall(src[key]["text"])
        t_nums = NUM_RE.findall(parts_joined(e))
        if sorted(s_nums) == sorted(t_nums):
            continue
        a = allow.get(key)
        if a and sorted(s_nums) == sorted(a["src"]) and sorted(t_nums) == sorted(a["tgt"]):
            continue
        problems.append("%s：数字词元不一致 原文=%s 译文=%s" % (key, s_nums, t_nums))


def check_concat(tr_data, md_path, problems):
    blocks = parse_blocks(Path(md_path).read_text(encoding="utf-8"))
    for e in tr_data["elements"]:
        key = e["key"]
        if key in blocks and norm("\n".join(e["parts"])) != norm(blocks[key]):
            problems.append("%s：parts 拼接与译文不一致" % key)


def run_qa(src: str, out: str, tr_json: str, md: str, numerals_path=None, render_pdf=None) -> int:
    import contextlib
    import io
    import extract_docx_v2
    import extract_v3

    allow = {}
    if numerals_path:
        allow = load(numerals_path)
        allow.pop("_comment", None)

    problems = []
    tr_data = load(tr_json)
    src_path = Path(src)
    if str(src).lower().endswith(".pptx"):
        src_data = extract_v3.extract_pptx(src_path, include_notes=True)
        out_data = extract_v3.extract_pptx(Path(out), include_notes=True)
        check_pptx_roundtrip(src_data, out_data, tr_data, problems)
    else:
        with contextlib.redirect_stdout(io.StringIO()):
            src_data = extract_docx_v2.extract_docx(src_path, out_path=None)
        cjk_target = any(
            re.search(r"[\u4e00-\u9fff]", e.get("translated_text", ""))
            for e in tr_data["elements"]
        )
        cmd = [sys.executable, str(SCRIPTS / "verify_structure.py"), src, out, tr_json]
        if cjk_target:
            cmd.append("--expect-cjk")
        res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
        if res.stdout.strip():
            print(res.stdout.strip())
        if res.returncode != 0:
            problems.append("DOCX 结构门未通过")

    check_numbers(src_data, tr_data, allow, problems)
    check_concat(tr_data, md, problems)

    if render_pdf:
        res = subprocess.run(
            [sys.executable, str(SCRIPTS / "render_qa.py"), render_pdf, "--cjk-scan"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        if res.stdout.strip():
            print(res.stdout.strip())
        if res.returncode != 0:
            problems.append(f"渲染 QA 未通过（{render_pdf}）")

    if problems:
        print("QA 未通过，%d 项：" % len(problems))
        for p in problems[:60]:
            print(" -", p)
        return 1
    print("QA 全部通过。")
    return 0


def main() -> int:
    pos = []
    numerals_path = None
    render_pdf = None
    i = 1
    while i < len(sys.argv):
        a = sys.argv[i]
        if a == "--numerals" and i + 1 < len(sys.argv):
            numerals_path = sys.argv[i + 1]
            i += 2
        elif a == "--render" and i + 1 < len(sys.argv):
            render_pdf = sys.argv[i + 1]
            i += 2
        else:
            pos.append(a)
            i += 1
    if len(pos) < 4:
        raise SystemExit(
            "用法: python qa_v3.py source output translated.json translation.md "
            "[--numerals whitelist.json] [--render out.pdf]"
        )
    return run_qa(pos[0], pos[1], pos[2], pos[3], numerals_path=numerals_path, render_pdf=render_pdf)


if __name__ == "__main__":
    sys.exit(main())
