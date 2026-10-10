# 单一 QA 入口 v3：结构 / 文本 / 格式 / 数字 一次跑完，任何阻断项不过即 exit 1
# 用法: python qa_v3.py source.docx|pptx output translated.json translation.md [--numerals whitelist.json] [--render out.pdf]
# 检查项:
#   1 结构与文本（阻断）— PPTX: 回抽比对（文本、run 数量、分段切分、格式签名、key 集合）
#                        DOCX: verify_structure.py（结构节点计数 + 译文覆盖）
#   2 数字保真（阻断）— 已翻译元素的数字词元与原文一致；书写形式转换记入白名单后放行
#   3 拼接一致（阻断）— 元素 parts 拼接与译文一致（去空白比对）
#   4 渲染检查（可选）— 导出 PDF 后空白页与残留源语言扫描
import json
import re
import subprocess
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
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
    # 按段落结构拼接 parts：段内 run 直接相连（与源文本 text 的拼法一致），
    # 段间补换行，避免跨段数字词元粘连
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


def check_pptx_roundtrip(src_json, out_json, tr_json, problems):
    src = {e["key"]: e for e in load(src_json)["elements"]}
    out = {e["key"]: e for e in load(out_json)["elements"]}
    tr = {e["key"]: e for e in load(tr_json)["elements"]}
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


def check_numbers(src_json, tr_json, allow, problems):
    src = {e["key"]: e for e in load(src_json)["elements"]}
    for e in load(tr_json)["elements"]:
        if "translated_text" not in e:
            continue
        key = e["key"]
        s_nums = NUM_RE.findall(src[key]["text"])
        t_nums = NUM_RE.findall(parts_joined(e))
        if sorted(s_nums) == sorted(t_nums):
            continue
        a = allow.get(key)
        if a and sorted(s_nums) == sorted(a["src"]) and sorted(t_nums) == sorted(a["tgt"]):
            continue
        problems.append("%s：数字词元不一致 原文=%s 译文=%s" % (key, s_nums, t_nums))


def check_concat(tr_json, md_path, problems):
    blocks = parse_blocks(Path(md_path).read_text(encoding="utf-8"))
    for e in load(tr_json)["elements"]:
        key = e["key"]
        if key in blocks and norm("\n".join(e["parts"])) != norm(blocks[key]):
            problems.append("%s：parts 拼接与译文不一致" % key)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if len(args) < 4:
        raise SystemExit("用法: python qa_v3.py source output translated.json translation.md "
                         "[--numerals whitelist.json] [--render out.pdf]")
    src, out, tr_json, md = args[0], args[1], args[2], args[3]
    allow = {}
    if "--numerals" in sys.argv:
        allow = load(sys.argv[sys.argv.index("--numerals") + 1])
        allow.pop("_comment", None)

    problems = []
    tmp = Path(tr_json).parent
    src_ex = tmp / "qa_src_extract.json"
    subprocess.run([sys.executable, str(SCRIPTS / "extract_v3.py"), src, str(src_ex)],
                   check=True, capture_output=True)
    if str(src).lower().endswith(".pptx"):
        out_ex = tmp / "qa_out_extract.json"
        subprocess.run([sys.executable, str(SCRIPTS / "extract_v3.py"), out, str(out_ex)],
                       check=True, capture_output=True)
        check_pptx_roundtrip(str(src_ex), str(out_ex), tr_json, problems)
    else:
        # 目标语言含 CJK 时 CJK 残留扫描属预期，改用 --expect-cjk 门（否则 EN→CJK 会被误报）
        cjk_target = any(re.search(r"[一-鿿]", e.get("translated_text", ""))
                         for e in load(tr_json)["elements"])
        cmd = [sys.executable, str(SCRIPTS / "verify_structure.py"), src, out, tr_json]
        if cjk_target:
            cmd.append("--expect-cjk")
        res = subprocess.run(cmd, capture_output=True, text=True)
        print(res.stdout.strip())
        if res.returncode != 0:
            problems.append("DOCX 结构门未通过")

    check_numbers(str(src_ex), tr_json, allow, problems)
    check_concat(tr_json, md, problems)

    if "--render" in sys.argv:
        pdf = sys.argv[sys.argv.index("--render") + 1]
        res = subprocess.run([sys.executable, str(SCRIPTS / "render_qa.py"), pdf, "--cjk-scan"],
                             capture_output=True, text=True)
        print(res.stdout.strip())

    if problems:
        print("QA 未通过，%d 项：" % len(problems))
        for p in problems[:60]:
            print(" -", p)
        return 1
    print("QA 全部通过。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
