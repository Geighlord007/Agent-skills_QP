import math
import re


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def chw(ch):
    o = ord(ch)
    if o >= 0x2E80:
        return 1.0
    if ch == " ":
        return 0.30
    if ch in ".,:;|!()[]'’":
        return 0.30
    if ch in "il":
        return 0.28
    if ch in "mwMW":
        return 0.84
    if ch.isupper():
        return 0.64
    if ch.isdigit():
        return 0.56
    return 0.54


def tw(s, size, bold=False):
    w = sum(chw(c) for c in s) * size
    return w * (1.05 if bold else 1.0)


def svg_open(tokens, default_bg="#FFFFFF"):
    W = tokens["canvas"]["width"]
    H = tokens["canvas"]["height"]
    bg = tokens.get("background", default_bg)
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
        f'viewBox="0 0 {W} {H}" font-family="{tokens["font"]}">'
        "<style>text{font-variant-numeric:tabular-nums}</style>"
        f'<rect width="{W}" height="{H}" fill="{bg}"/>'
    )


def capsule(cx, cy, s, tokens, size=9.5, fill="#FFFFFF", stroke=None, fg=None):
    C = tokens["colors"]
    w = tw(s, size, True) + 18
    out = rect(cx - w / 2, cy - 10, w, 20, fill, stroke or C["ink900"], 1, rx=10)
    out += text(cx, cy + size * 0.36, s, size, fg or C["ink900"], "bold", "middle")
    return out


def text(x, y, s, size=11, fill="#333333", weight="normal", anchor="start", italic=False, font=None, ls=None):
    parts = [f'x="{x:.1f}"', f'y="{y:.1f}"', f'font-size="{size}"', f'fill="{fill}"',
             f'font-weight="{weight}"', f'text-anchor="{anchor}"']
    if italic:
        parts.append('font-style="italic"')
    if font:
        parts.append(f'font-family="{font}"')
    if ls is not None:
        parts.append(f'letter-spacing="{ls}"')
    return f'<text {" ".join(parts)}>{esc(s)}</text>'


def mtext(x, y, s, size=10.5, fill="#333333", weight="normal", anchor="start", lh=1.35, font=None):
    out = ""
    for i, line in enumerate(s.split("\n")):
        out += text(x, y + i * size * lh, line, size, fill, weight, anchor, font=font)
    return out


def head_block(spec, tokens):
    out = ""
    if spec.get("kicker"):
        out += text(48, 38, spec["kicker"], 9, tokens.get("kicker_color", tokens["colors"]["ink500"]),
                    "bold", ls=1.2)
    out += mtext(48, 62, spec["title"], tokens["type"]["title"], tokens["colors"]["ink900"], "bold",
                 lh=1.18, font=tokens.get("font_title"))
    return out


def rect(x, y, w, h, fill, stroke=None, sw=0, rx=0, opacity=None):
    if h < 0:
        y += h
        h = -h
    parts = [f'x="{x:.2f}"', f'y="{y:.2f}"', f'width="{w:.2f}"', f'height="{h:.2f}"', f'fill="{fill}"']
    if stroke:
        parts += [f'stroke="{stroke}"', f'stroke-width="{sw}"']
    if rx:
        parts.append(f'rx="{rx}"')
    if opacity is not None:
        parts.append(f'opacity="{opacity}"')
    return f'<rect {" ".join(parts)}/>'


def line(x1, y1, x2, y2, stroke="#111111", sw=1, dash=None, cap="butt"):
    parts = [f'x1="{x1:.2f}"', f'y1="{y1:.2f}"', f'x2="{x2:.2f}"', f'y2="{y2:.2f}"',
             f'stroke="{stroke}"', f'stroke-width="{sw}"', f'stroke-linecap="{cap}"']
    if dash:
        parts.append(f'stroke-dasharray="{dash}"')
    return f'<line {" ".join(parts)}/>'


def circle(cx, cy, r, fill, stroke=None, sw=0):
    parts = [f'cx="{cx:.2f}"', f'cy="{cy:.2f}"', f'r="{r}"', f'fill="{fill}"']
    if stroke:
        parts += [f'stroke="{stroke}"', f'stroke-width="{sw}"']
    return f'<circle {" ".join(parts)}/>'


def polygon(pts, fill, stroke=None, sw=1, opacity=None):
    d = " ".join(f"{p[0]:.2f},{p[1]:.2f}" for p in pts)
    parts = [f'points="{d}"', f'fill="{fill}"']
    if stroke:
        parts += [f'stroke="{stroke}"', f'stroke-width="{sw}"']
    if opacity is not None:
        parts.append(f'opacity="{opacity}"')
    return f'<polygon {" ".join(parts)}/>'


def path(d, fill="none", stroke=None, sw=1, dash=None, cap="butt", opacity=None):
    parts = [f'd="{d}"', f'fill="{fill}"']
    if stroke:
        parts += [f'stroke="{stroke}"', f'stroke-width="{sw}"', f'stroke-linecap="{cap}"']
    if dash:
        parts.append(f'stroke-dasharray="{dash}"')
    if opacity is not None:
        parts.append(f'opacity="{opacity}"')
    return f'<path {" ".join(parts)}/>'


def dotted(x1, y1, x2, y2, color="#8A8A8A"):
    return line(x1, y1, x2, y2, color, 1, "2 3")


def arrow(x1, y1, x2, y2, color="#111111", sw=1.2, head=8):
    out = line(x1, y1, x2, y2, color, sw)
    a = math.atan2(y2 - y1, x2 - x1)
    p2 = (x2 - head * math.cos(a - 0.42), y2 - head * math.sin(a - 0.42))
    p3 = (x2 - head * math.cos(a + 0.42), y2 - head * math.sin(a + 0.42))
    out += polygon([(x2, y2), p2, p3], color)
    return out


def wrap(s, size, maxw, bold=False):
    # 把连续的字母/数字/百分号当作不可分割的整体,避免把 2022 拆成 20/22
    toks = re.findall(r"[A-Za-z0-9][A-Za-z0-9.,%+\-/]*|.", s)
    lines, cur = [], ""
    for t in toks:
        if cur and tw(cur + t, size, bold) > maxw:
            lines.append(cur)
            cur = t
        else:
            cur += t
    if cur:
        lines.append(cur)
    merged = []
    for ln in lines:
        if merged and ln and ln[0] in "。,.、;:!?%)]}":
            merged[-1] += ln[0]
            ln = ln[1:]
        if ln:
            merged.append(ln)
    if len(merged) >= 2 and tw(merged[-1], size, bold) < maxw * 0.3:
        while tw(merged[-1], size, bold) < maxw * 0.5:
            prev_toks = re.findall(r"[A-Za-z0-9][A-Za-z0-9.,%+\-/]*|.", merged[-2])
            if len(prev_toks) <= 1:
                break
            merged[-1] = prev_toks[-1] + merged[-1]
            merged[-2] = "".join(prev_toks[:-1])
    # 连接词不留在行尾
    connectors = "较和与及或为在从到对按以将把被由向于"
    for i in range(len(merged) - 1):
        merged[i] = merged[i].rstrip()
        if merged[i] and merged[i][-1] in connectors:
            ch = merged[i][-1]
            merged[i] = merged[i][:-1]
            nxt = merged[i + 1]
            sep = " " if nxt[:1].isalnum() else ""
            merged[i + 1] = ch + sep + nxt
    return [ln.rstrip() for ln in merged]


def sidebar(x, top, title, items, width, colors, size=10.5):
    out = text(x, top, title, 13, colors["ink900"], "bold")
    y = top + 34
    for lead, body in items:
        out += text(x, y, lead, size, colors["ink900"], "bold")
        y += 17
        for ln in wrap(body, size - 0.5, width):
            out += text(x, y, ln, size - 0.5, colors["ink700"])
            y += 15
        y += 14
    return out


def report_head(spec, tokens):
    style = tokens.get("style", "house")
    W = tokens["canvas"]["width"]
    C = tokens["colors"]
    size = tokens["type"]["title"]
    if style == "deloitte":
        out = ""
        if spec.get("figure"):
            out += text(24, 28, spec["figure"], 13, C["ink500"], "normal", italic=True,
                        font="Georgia, 'Times New Roman', serif")
        lines = []
        for para in spec["title"].split("\n"):
            lines += wrap(para, size, W - 48, True)
        y = 58
        for ln in lines:
            out += text(24, y, ln, size, C["ink900"], "bold")
            y += size * 1.16
        if spec.get("question"):
            y += 2
            for ln in wrap("Question: " + spec["question"], 11.5, W - 48):
                out += text(24, y, ln, 11.5, C["ink700"], "normal", italic=True,
                            font="Georgia, 'Times New Roman', serif")
                y += 15
        return out, y + 6
    if style == "bcg":
        out = ""
        head = spec.get("exhibit") or spec["title"]
        out += text(8, 30, head, 22, C["second"], "bold")
        return out, 58
    if style == "mckinsey":
        out = ""
        lines = []
        for para in spec["title"].split("\n"):
            lines += wrap(para, size, W - 40, True)
        y = 38
        for ln in lines:
            out += text(16, y, ln, size, C["ink900"], "bold")
            y += size * 1.2
        return out, y + 10
    if style == "matrix":
        out = ""
        lines = []
        for para in spec["title"].split("\n"):
            lines += wrap(para, size, W - 100, True)
        y = 42
        for ln in lines:
            out += text(40, y, ln, size, C["ink900"], "bold", font=tokens.get("font_title"))
            y += size * 1.18
        return out, y + 12
    out = ""
    if spec.get("kicker"):
        out += text(48, 38, spec["kicker"], 9, tokens.get("kicker_color", C["ink500"]),
                    "bold", ls=1.2)
    out += mtext(48, 62, spec["title"], size, C["ink900"], "bold",
                 lh=1.18, font=tokens.get("font_title"))
    return out, 136


def render_partition_bridge(spec, tokens):
    from annotations import draw_background, draw_foreground
    W = tokens["canvas"]["width"]
    H = tokens["canvas"]["height"]
    C = tokens["colors"]
    T = tokens["type"]
    font = tokens["font"]
    cat_colors = tokens["category_colors"]

    cols = spec["columns"]
    n = len(cols)
    x0, x1 = 120, 920
    colw = (x1 - x0) / n
    plot_top, plot_bot = 200, 540
    ymax = max(c["level"] for c in cols) + 8
    scale = (plot_bot - plot_top) / ymax

    def yv(v):
        return plot_bot - v * scale

    def colx(i):
        return x0 + colw * (i + 0.5)

    def cidx(cid):
        for i, c in enumerate(cols):
            if c["id"] == cid:
                return i
        raise KeyError(cid)

    emph = [i for i, c in enumerate(cols) if c.get("emphasis")]
    band_left = band_right = None
    if emph:
        ei = emph[0]
        band_left, band_right = colx(ei) - 52, colx(ei) + 52

    out = svg_open(tokens)

    out += head_block(spec, tokens)
    out += text(48, 126, spec["panel_title"], T["panel"], C["ink900"], "bold")
    out += line(48, 136, 952, 136, C["ink900"], 1)

    out += draw_background(spec.get("annotations", []),
                           {"colx": lambda c: colx(cidx(c)), "yv": yv, "x0": x0, "x1": x1}, tokens)

    out += line(x0 - 20, yv(0), x1 + 20, yv(0), C["base"], tokens["lines"]["base"])

    for conn in spec.get("connectors", []):
        xa = colx(cidx(conn["from"])) + 37
        xb = band_right if conn["to"] == "band" else colx(cidx(conn["to"])) - 37
        out += dotted(xa, yv(conn["level"]), xb, yv(conn["level"]))

    for i, c in enumerate(cols):
        cx = colx(i)
        if c["kind"] == "stack":
            y = yv(c["level"])
            for seg in c["segments"]:
                h = seg["value"] * scale
                color = C[cat_colors.get(seg["name"], "second")]
                out += rect(cx - 37, y, 74, h, color)
                out += line(cx - 37, y, cx + 37, y, "#FFFFFF", 1)
                if h >= 12:
                    fg = C["ink900"] if color in (C["light"], C["second"]) else "#FFFFFF"
                    out += text(cx, y + h / 2 + 3.4, f"{seg['value']:g}", 10, fg, "bold", "middle")
                else:
                    out += text(cx + 41, y + h / 2 + 3.5, f"{seg['value']:g}", 9.5, C["ink700"])
                if i == 0:
                    out += text(108, y + h / 2 + 3.5, seg["name"], 10, C["ink700"], "normal", "end")
                y += h
            label = c.get("total", c["level"])
            if c.get("emphasis"):
                out += text(cx - 14, yv(c["level"]) - 6, f"{label:g}", 11, C["ink900"], "bold", "end")
            else:
                out += text(cx, yv(c["level"]) - 8, f"{label:g}", 11, C["ink900"], "bold", "middle")
        else:
            y1, y2 = yv(c["level"]), yv(c["base"])
            out += rect(cx - 37, y1, 74, y2 - y1, C["step"])
            out += text(cx, (y1 + y2) / 2 + 4, f"{c['value']:g}", 11.5, C["ink900"], "bold", "middle")

    for i, c in enumerate(cols):
        out += mtext(colx(i), 566, c["label"], 10, C["ink700"], "normal", "middle", 1.25)

    out += draw_foreground(spec.get("annotations", []),
                           {"colx": lambda c: colx(cidx(c)), "yv": yv}, tokens)

    out += sidebar(1000, 126, "关键洞察", spec.get("insights", []), 232, C)

    src = spec.get("source", "")
    out += text(48, 702, src, T["note"], C["ink400"])
    return out + "</svg>"
