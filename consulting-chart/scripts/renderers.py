import math
import statistics

from chartlib import (text, mtext, rect, line, circle, polygon, dotted, arrow,
                      path, wrap, sidebar, tw, head_block)
from annotations import draw_foreground


def _svg_open(tokens):
    W = tokens["canvas"]["width"]
    H = tokens["canvas"]["height"]
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
        f'viewBox="0 0 {W} {H}" font-family="{tokens["font"]}">'
        "<style>text{font-variant-numeric:tabular-nums}</style>"
        f'<rect width="{W}" height="{H}" fill="#FFFFFF"/>'
    )


def render_waterfall(spec, tokens):
    C = tokens["colors"]
    T = tokens["type"]
    cols = spec["columns"]
    x0, x1 = 120, 952
    colw = (x1 - x0) / len(cols)
    plot_top, plot_bot = 160, 520

    def cval(c):
        return sum(s["value"] for s in c["segments"]) if "segments" in c else c["value"]

    cum = 0.0
    levels = [0.0]
    for c in cols:
        v = cval(c)
        if c["kind"] in ("start", "subtotal", "end"):
            cum = v
        else:
            cum += v
        levels.append(cum)
    vmax = max(levels + [0])
    vmin = min(levels + [0])
    pad = (vmax - vmin) * 0.06
    scale = (plot_bot - plot_top) / (vmax - vmin + 2 * pad)
    zero = plot_top + (vmax + pad) * scale

    def yv(v):
        return zero - v * scale

    def colx(i):
        return x0 + colw * (i + 0.5)

    out = _svg_open(tokens)
    out += head_block(spec, tokens)
    out += text(48, 106, spec["panel_title"], T["panel"], C["ink900"], "bold")
    out += line(48, 116, 952, 116, C["ink900"], 1)

    level_after = []
    c2 = 0.0
    for c in cols:
        v = cval(c)
        if c["kind"] in ("start", "subtotal", "end"):
            c2 = v
        else:
            c2 += v
        level_after.append(c2)

    out += line(x0 - 34, zero, x1 + 6, zero, C["base"], tokens["lines"]["base"])
    neg_shades = ["#E0393E", "#E8696D", "#F09A9D"]
    pos_shades = ["#1437B9", "#2972FF", "#7FA6F2"]
    cum = 0.0
    prev = None
    conns = []
    for i, c in enumerate(cols):
        cx = colx(i)
        bw = 38
        v = cval(c)
        if c["kind"] in ("start", "subtotal", "end"):
            if c.get("segments"):
                y = yv(0)
                for si, seg in enumerate(c["segments"]):
                    h = abs(seg["value"]) * scale
                    y -= h
                    out += rect(cx - bw / 2, y, bw, h, pos_shades[si % 3])
                    out += line(cx - bw / 2, y, cx + bw / 2, y, "#FFFFFF", 1)
                    if h >= 14:
                        fg = "#FFFFFF" if si < 2 else C["ink900"]
                        out += text(cx, y + h / 2 + 3.4, f"{seg['value']:g}", 9, fg, "bold", "middle")
            else:
                top = yv(v) if v >= 0 else zero
                bot = yv(v) if v < 0 else zero
                out += rect(cx - bw / 2, top, bw, bot - top, C["primary"])
            if c["kind"] == "end" and v < 0:
                out += text(cx, yv(v) + 18, f"{v:g}", 11, C["ink900"], "bold", "middle")
            else:
                out += text(cx, yv(v) - 8, f"{v:g}", 11, C["ink900"], "bold", "middle")
            cum = v
        else:
            before = cum
            after = cum + v
            if c.get("segments"):
                shades = neg_shades if v < 0 else pos_shades
                y = yv(before)
                for si, seg in enumerate(c["segments"]):
                    h = abs(seg["value"]) * scale
                    if v < 0:
                        top_y = y
                        y += h
                    else:
                        y -= h
                        top_y = y
                    out += rect(cx - bw / 2, top_y, bw, h, shades[si % 3])
                    out += line(cx - bw / 2, top_y, cx + bw / 2, top_y, "#FFFFFF", 1)
                    if h >= 14:
                        fg = "#FFFFFF" if si < 2 else C["ink900"]
                        out += text(cx, top_y + h / 2 + 3.4, f"{seg['value']:g}", 9, fg, "bold", "middle")
                end_y = yv(after)
                ly = end_y + 16 if v < 0 else end_y - 8
                out += text(cx, ly, f"{v:g}", 10.5, C["neg"] if v < 0 else C["pos"], "bold", "middle")
            else:
                y1, y2 = yv(before), yv(after)
                h = abs(y2 - y1)
                color = C["neg"] if v < 0 else C["pos"]
                out += rect(cx - bw / 2, min(y1, y2), bw, max(h, 3), color)
                if h >= 40:
                    out += text(cx, (y1 + y2) / 2 + 4, f"{v:g}", 11, "#FFFFFF", "bold", "middle")
                else:
                    lbl = f"{v:g}"
                    lx = cx + bw / 2 + 6
                    ly = (y1 + y2) / 2 + 3.5
                    out += rect(lx - 2, ly - 11, tw(lbl, 9.5, True) + 4, 14, "#FFFFFF")
                    out += text(lx, ly, lbl, 9.5, color, "bold")
            cum = after
        if prev is not None:
            conns.append((colx(i - 1) + 19, yv(prev), cx - 19, yv(prev)))
        prev = cum
    for xa, ya, xb, yb in conns:
        out += dotted(xa, ya, xb, yb)

    out += draw_foreground(spec.get("annotations", []),
                           {"colx": lambda i: colx(i),
                            "level_y": lambda i: yv(level_after[i]),
                            "yv": yv}, tokens)

    for i, c in enumerate(cols):
        out += mtext(colx(i), 545, c["label"], 10, C["ink700"], "normal", "middle", 1.25)
    if spec.get("show_pct", True):
        out += line(x0 - 34, 558, x1 + 6, 558, C["hair"], 1)
        out += text(48, 582, "同比 %", 10, C["ink700"])
        for i, c in enumerate(cols):
            out += text(colx(i), 582, c.get("pct", ""), 10.5, C["ink700"], "normal", "middle")

    if spec.get("note"):
        out += text(48, 620, spec["note"], T["note"], C["ink400"])
    out += sidebar(1000, 126, "关键洞察", spec.get("insights", []), 232, C)
    out += text(48, 702, spec.get("source", ""), T["note"], C["ink400"])
    return out + "</svg>"


def capsule_at(cx, cy, s, tokens, size=9.5):
    C = tokens["colors"]
    w = tw(s, size, True) + 18
    h = 20
    out = rect(cx - w / 2, cy - h / 2, w, h, "#FFFFFF", C["ink900"], 1, rx=h / 2)
    out += text(cx, cy + size * 0.36, s, size, C["ink900"], "bold", "middle")
    return out


def render_combo(spec, tokens):
    C = tokens["colors"]
    T = tokens["type"]
    years = spec["years"]
    rev = spec["revenue"]
    gp = spec["gross_profit"]
    yoy = spec.get("yoy")
    if yoy is None:
        yoy = [round((rev[i] / rev[i - 1] - 1) * 100, 1) if i else None for i in range(len(rev))]
    gpp = [int(g / r * 100 + 0.5) for g, r in zip(gp, rev)]

    x0, x1 = 150, 980
    colw = (x1 - x0) / len(years)
    plot_top, plot_bot = 200, 540
    scale = (plot_bot - plot_top) / spec.get("y_max", 70.0)
    yzero_pct = 420

    def colx(i):
        return x0 + colw * (i + 0.5)

    out = _svg_open(tokens)
    out += head_block(spec, tokens)
    out += text(48, 126, spec["panel_title"], T["panel"], C["ink900"], "bold")
    out += line(48, 136, 952, 136, C["ink900"], 1)

    out += line(x0 - 20, yzero_pct, x1 + 6, yzero_pct, "#9E9E9E", 1, "4 4")
    out += text(x1 + 12, yzero_pct + 3.5, "0%", 9, C["ink400"])

    for i, (r, g) in enumerate(zip(rev, gp)):
        cx = colx(i)
        bw = 44
        h_gp = g * scale
        y_gp = plot_bot - h_gp
        h_rest = (r - g) * scale
        out += rect(cx - bw / 2, y_gp - h_rest, bw, h_rest, C["light"])
        out += rect(cx - bw / 2, y_gp, bw, h_gp, C["primary"])
        out += text(cx, y_gp - h_rest - 8, f"{r:.1f}", 10.5, C["ink900"], "bold", "middle")
        out += text(cx, y_gp + h_gp / 2 - 1, f"{g:.1f}", 9.5, "#FFFFFF", "bold", "middle")
        out += text(cx, y_gp + h_gp / 2 + 11, f"({gpp[i]}%)", 9.5, "#FFFFFF", "normal", "middle")

    pts = []
    for i, v in enumerate(yoy):
        if v is None:
            continue
        pts.append((colx(i), yzero_pct - v * 5.5))
    d = "M" + " L".join(f"{p[0]:.2f} {p[1]:.2f}" for p in pts)
    out += f'<path d="{d}" fill="none" stroke="{C["ink900"]}" stroke-width="2" stroke-linecap="round"/>'
    for i, (px, py) in enumerate(pts):
        out += circle(px, py, 4, "#FFFFFF", C["ink900"], 1.5)
        out += text(px, py - 10, f"{yoy[i + 1]:+.1f}%", 10, C["ink900"], "normal", "middle")

    out += draw_foreground(spec.get("annotations", []),
                           {"x_of": lambda y: colx(years.index(y)),
                            "top_of": lambda y: plot_bot - rev[years.index(y)] * scale}, tokens)

    out += line(x0 - 20, plot_bot, x1 + 6, plot_bot, C["base"], tokens["lines"]["base"])
    out += mtext(48, 300, "营收\n(US$ M)", 10, C["ink700"], "bold", "start", 1.4)
    out += mtext(48, 386, "营收同比\n增速", 9.5, C["ink500"], "normal", "start", 1.35)
    out += mtext(48, 500, "毛利润\n(US$ M),%", 10, C["ink700"], "bold", "start", 1.4)
    for i, yr in enumerate(years):
        out += text(colx(i), 566, str(yr), 9.5, C["ink700"], "normal", "middle")

    out += sidebar(1000, 126, "关键洞察", spec.get("insights", []), 232, C)
    src = spec.get("source", "")
    note = spec.get("note")
    out += text(48, 702, src, T["note"], C["ink400"])
    if note:
        out += text(48 + tw(src, T["note"]) + 24, 702, "Note: " + note, T["note"], C["ink400"])
    return out + "</svg>"


def render_gantt(spec, tokens):
    C = tokens["colors"]
    T = tokens["type"]
    x0 = 300
    month_w = 136.0
    months = spec["months"]
    tasks = spec["tasks"]
    row_top = 240
    row_h = 52
    grid_top, grid_bot = 196, 552

    def gx(p):
        return x0 + (p[0] + p[1]) * month_w

    out = _svg_open(tokens)
    out += head_block(spec, tokens)

    for idx, ph in enumerate(spec["phases"]):
        pa, pb = gx(ph["start"]), gx(ph["end"])
        h = 40
        y = 140
        col = C[ph.get("color", "accent")]
        pts = [(pa, y)]
        if idx == 0:
            pts += [(pb - 14, y), (pb, y + h / 2), (pb - 14, y + h), (pa, y + h)]
        elif idx == len(spec["phases"]) - 1:
            pts += [(pb, y), (pb, y + h), (pa + 14, y + h), (pa, y + h / 2)]
        else:
            pts += [(pb - 14, y), (pb, y + h / 2), (pb - 14, y + h), (pa + 14, y + h), (pa, y + h / 2)]
        out += polygon(pts, col)
        out += text((pa + pb) / 2, y + h / 2 + 4.5, ph["label"], 12.5, "#FFFFFF", "bold", "middle")

    band_rows = spec.get("band_rows", [])
    for a, b in band_rows:
        out += rect(x0, row_top + row_h * a, 980 - x0, row_h * (b - a), C.get("group", "#EAF1FF"))

    for m in range(len(months) + 1):
        out += line(x0 + m * month_w, grid_top, x0 + m * month_w, grid_bot, "#DDDDDD", 1)
    for m, name in enumerate(months):
        out += text(x0 + m * month_w + month_w / 2, 214, name, 10.5, C["ink700"], "bold", "middle")
    for i in range(len(tasks) + 1):
        out += line(x0, row_top + i * row_h, 980, row_top + i * row_h, "#CFCFCF", 0.75)

    for i, t in enumerate(tasks):
        cy = row_top + i * row_h + row_h / 2
        out += text(48, cy + 4, t["label"], 10.5, C["ink700"])
        col = C[t.get("color", "primary")]
        bx1, bx2 = gx(t["start"]), gx(t["end"])
        out += rect(bx1, cy - 5, bx2 - bx1, 10, col, rx=5)
        out += text(1000, cy + 4, t.get("owner", ""), 10, C["ink700"])
        sx = 1150
        st = t.get("status", "todo")
        if st == "done":
            out += circle(sx, cy, 7, C["primary"])
        elif st == "doing":
            out += circle(sx, cy, 7, "#FFFFFF", C["primary"], 1.5)
            out += f'<path d="M {sx} {cy - 7} A 7 7 0 0 1 {sx} {cy + 7}" fill="none" stroke="{C["primary"]}" stroke-width="3"/>'
        else:
            out += circle(sx, cy, 7, "#FFFFFF", C["ink400"], 1.5)

    today = spec.get("today")
    if today:
        xt = gx(today)
        out += line(xt, row_top, xt, grid_bot, C["ink500"], 1.5, "6 4")
        out += text(xt, grid_bot + 22, "今天", 10, C["ink500"], "normal", "middle")

    for ms in spec.get("milestones", []):
        xm = gx(ms["at"])
        if ms.get("kind") == "go_live":
            row = ms.get("row", 4)
            cy = row_top + row * row_h + row_h / 2
            out += line(xm, grid_top, xm, grid_bot, C["neg"], 1.2, "4 3")
            out += polygon([(xm, cy - 6), (xm + 6, cy), (xm, cy + 6), (xm - 6, cy)], C["neg"])
            out += text(xm + 10, cy + 4, ms["label"], 10, C["neg"])
        else:
            row = ms.get("row", 2)
            cy = row_top + row * row_h + row_h / 2
            out += polygon([(xm, cy - 6), (xm + 6, cy), (xm, cy + 6), (xm - 6, cy)], C["primary"], "#FFFFFF", 1)
            out += text(xm - 8, cy - 8, ms["label"], 10, C["ink700"], "normal", "end")

    out += text(48, 214, "活动", 10.5, C["ink900"], "bold")
    out += text(1000, 214, "负责人", 10.5, C["ink900"], "bold")
    out += text(1150, 214, "状态", 10.5, C["ink900"], "bold", "middle")
    out += circle(1076, 605, 5, C["primary"])
    out += text(1086, 610, "完成", 9.5, C["ink500"])
    out += circle(1118, 605, 5, "#FFFFFF", C["primary"], 1.4)
    out += f'<path d="M 1118 598 A 7 7 0 0 1 1118 612" fill="none" stroke="{C["primary"]}" stroke-width="2.4"/>'
    out += text(1128, 610, "进行中", 9.5, C["ink500"])
    out += circle(1170, 605, 5, "#FFFFFF", C["ink400"], 1.4)
    out += text(1180, 610, "未开始", 9.5, C["ink500"])

    label = spec.get("status_label", "当前状态:按计划推进")
    out += text(48, 640, label, 11, C["ink900"], "bold")
    out += circle(48 + tw(label, 11, True) + 14, 636, 7, "#1E8E3E")
    out += text(48, 702, spec.get("source", ""), T["note"], C["ink400"])
    return out + "</svg>"


def render_composition(spec, tokens):
    C = tokens["colors"]
    T = tokens["type"]
    cols = spec["columns"]
    x0, x1 = 150, 900
    colw = (x1 - x0) / len(cols)
    plot_top, plot_bot = 200, 540
    ymax = max(c["total"] for c in cols) * 1.08
    scale = (plot_bot - plot_top) / ymax

    def yv(v):
        return plot_bot - v * scale

    def colx(i):
        return x0 + colw * (i + 0.5)

    # 由下到上:深→浅的单一蓝阶,避免中途回亮
    palette = ["#08152E", "#0B2E6F", "#123C8C", "#1B4FA8", "#2A63C4",
               "#3D79DB", "#5A93EA", "#7FAEF2", "#A9C8F7", "#C7D8FF"]

    def lum(hexc):
        r = int(hexc[1:3], 16) / 255
        g = int(hexc[3:5], 16) / 255
        b = int(hexc[5:7], 16) / 255
        return 0.2126 * r + 0.7152 * g + 0.0722 * b

    out = _svg_open(tokens)
    out += head_block(spec, tokens)
    out += text(48, 126, spec["panel_title"], T["panel"], C["ink900"], "bold")
    out += line(48, 136, 952, 136, C["ink900"], 1)

    first = cols[0]
    y = plot_bot
    for si, seg in enumerate(first["segments"]):
        h = seg["value"] * scale
        y -= h
        out += text(108, y + h / 2 + 3.5, seg["name"], 9.5, C["ink700"], "normal", "end")
        out += rect(114, y + h / 2 - 5, 10, 10, palette[si % len(palette)])

    for i, col in enumerate(cols):
        cx = colx(i)
        bw = 80
        y = plot_bot
        for si, seg in enumerate(col["segments"]):
            h = seg["value"] * scale
            y -= h
            color = palette[si % len(palette)]
            out += rect(cx - bw / 2, y, bw, h, color)
            out += line(cx - bw / 2, y, cx + bw / 2, y, "#FFFFFF", 1)
            if h >= 14:
                fg = "#FFFFFF" if lum(color) < 0.55 else C["ink900"]
                out += text(cx, y + h / 2 + 3.4, f"{seg['value']:.2f}", 8.8, fg, "bold", "middle")
        out += text(cx, yv(col["total"]) - 8, f"{col['total']:.2f}", 11, C["ink900"], "bold", "middle")
        out += text(cx, 566, col["label"], 9.5, C["ink700"], "normal", "middle")

    out += line(x0 - 20, plot_bot, x1 + 6, plot_bot, C["base"], tokens["lines"]["base"])
    out += sidebar(1000, 126, "关键洞察", spec.get("insights", []), 232, C)
    out += text(48, 702, spec.get("source", ""), T["note"], C["ink400"])
    return out + "</svg>"


def render_scenario_compare(spec, tokens):
    C = tokens["colors"]
    T = tokens["type"]
    metrics = spec["metrics"]
    series = spec["series"]
    x0, x1 = 120, 952
    plot_top, plot_bot = 210, 540
    vals = [v for s in series for v in s["values"]]
    ymax = max(0, max(vals)) * 1.12
    ymin = min(0, min(vals)) * 1.15
    scale = (plot_bot - plot_top) / (ymax - ymin)
    zero = plot_top + ymax * scale

    def yv(v):
        return zero - v * scale

    group_w = (x1 - x0) / len(metrics)
    n = len(series)
    bar_w = min(32, group_w / (n + 1))
    gap = (group_w - n * bar_w) / (n + 1)
    palette = [C["primary"], C["accent"], C["second"], C["light"]]

    out = _svg_open(tokens)
    out += head_block(spec, tokens)
    out += text(48, 126, spec["panel_title"], T["panel"], C["ink900"], "bold")
    out += line(48, 136, 952, 136, C["ink900"], 1)

    lx = 120
    for si, s in enumerate(series):
        out += rect(lx, 160, 12, 12, palette[si % len(palette)])
        out += text(lx + 18, 170, s["name"], 10, C["ink700"])
        lx += 18 + tw(s["name"], 10) + 24

    out += line(x0 - 20, zero, x1 + 6, zero, C["base"], tokens["lines"]["base"])

    for gi, m in enumerate(metrics):
        gx = x0 + group_w * gi
        for si, s in enumerate(series):
            v = s["values"][gi]
            bx = gx + gap + si * (bar_w + gap)
            top = yv(max(v, 0))
            bot = yv(min(v, 0))
            out += rect(bx, top, bar_w, bot - top, palette[si % len(palette)])
            ly = top - 8 if v >= 0 else bot + 16
            out += text(bx + bar_w / 2, ly, f"{v:g}", 10, C["ink900"], "bold", "middle")
        out += mtext(gx + group_w / 2, 566, m, 10, C["ink700"], "normal", "middle")

    out += sidebar(1000, 126, "关键洞察", spec.get("insights", []), 232, C)
    if spec.get("note"):
        out += text(48, 600, spec["note"], T["note"], C["ink400"])
    out += text(48, 702, spec.get("source", ""), T["note"], C["ink400"])
    return out + "</svg>"


def render_tornado(spec, tokens):
    C = tokens["colors"]
    T = tokens["type"]
    labels = spec["labels"]
    low = spec["low"]
    high = spec["high"]
    mid = spec["midpoint"]
    n = len(labels)
    effect = [abs(high[i] - low[i]) / mid for i in range(n)]
    order = sorted(range(n), key=lambda i: effect[i], reverse=True)

    row_h = 62
    top = 210
    center = 640
    maxd = max(max(abs(mid - low[i]), abs(high[i] - mid)) for i in range(n))
    scale = 300 / maxd

    out = _svg_open(tokens)
    out += head_block(spec, tokens)
    out += text(48, 126, spec["panel_title"], T["panel"], C["ink900"], "bold")
    out += line(48, 136, 952, 136, C["ink900"], 1)

    out += line(center, top - 22, center, top + row_h * n + 8, C["ink400"], 1, "4 4")
    out += text(center, top - 30, f"中点 {mid:g}", 9.5, C["ink500"], "normal", "middle")
    out += text(48, 152, "左端=较小端点,右端=较大端点;条长=相对中点的偏离", 9, C["ink500"])

    for r, i in enumerate(order):
        cy = top + r * row_h + row_h / 2
        lines = labels[i].split("\n")
        ly = cy + 4 - (len(lines) - 1) * 7
        out += mtext(48, ly, labels[i], 11, C["ink700"], lh=1.25)

        left_v, right_v = min(low[i], high[i]), max(low[i], high[i])
        wl = abs(mid - left_v) * scale
        out += rect(center - wl, cy - 10, wl, 20, C["second"])
        out += text(center - wl - 8, cy + 4, f"{left_v:g}", 11, C["ink700"], "bold", "end")

        wh = abs(right_v - mid) * scale
        out += rect(center, cy - 10, wh, 20, C["primary"])
        out += text(center + wh + 8, cy + 4, f"{right_v:g}", 11, C["ink700"], "bold", "start")

    out += sidebar(1000, 126, "关键洞察", spec.get("insights", []), 232, C, size=11)
    out += text(48, 702, spec.get("source", ""), T["note"], C["ink400"])
    return out + "</svg>"


def render_funnel(spec, tokens):
    C = tokens["colors"]
    T = tokens["type"]
    stages = spec["stages"]
    values = spec["values"]
    top = 230
    row_h = 84
    center = 560
    maxw = 520
    shades = ["#0B2E6F", "#1B4FA8", "#3D79DB", "#7FAEF2", "#A9C8F7"]

    out = _svg_open(tokens)
    out += head_block(spec, tokens)
    out += text(48, 126, spec["panel_title"], T["panel"], C["ink900"], "bold")
    out += line(48, 136, 952, 136, C["ink900"], 1)

    out += text(280, 190, "阶段", 9, C["ink500"], "normal", "end")
    out += text(848, 190, "人数", 9, C["ink500"])
    out += text(920, 190, "较上一阶段", 9, C["ink500"])

    maxv = values[0]
    for i, (s, v) in enumerate(zip(stages, values)):
        cy = top + i * row_h
        w = maxw * v / maxv
        out += rect(center - w / 2, cy - 23, w, 46, shades[i % len(shades)])
        out += text(280, cy + 4, s, 11, C["ink700"], "normal", "end")
        out += text(848, cy + 4, f"{v:,}", 11, C["ink900"], "bold")
        if i > 0:
            pct = v / values[i - 1] * 100
            out += text(920, cy + 4, f"{pct:.1f}%", 10, C["ink500"])

    overall = values[-1] / values[0] * 100
    drops = [values[i] - values[i + 1] for i in range(len(values) - 1)]
    k = drops.index(max(drops))
    out += text(48, 620,
                f"总转化 {overall:.1f}%({values[0]:,} → {values[-1]:,});"
                f"最大单步流失:{stages[k]} → {stages[k + 1]}(-{max(drops):,})。",
                9.5, C["ink500"])

    out += sidebar(1000, 126, "关键洞察", spec.get("insights", []), 232, C)
    out += text(48, 702, spec.get("source", ""), T["note"], C["ink400"])
    return out + "</svg>"


def render_matrix(spec, tokens):
    C = tokens["colors"]
    T = tokens["type"]
    items = spec["items"]
    groups = spec["groups"]
    x0, x1 = 300, 880
    y0, y1 = 200, 580
    midx, midy = (x0 + x1) / 2, (y0 + y1) / 2

    out = _svg_open(tokens)
    out += head_block(spec, tokens)
    out += text(48, 126, spec["panel_title"], T["panel"], C["ink900"], "bold")
    out += line(48, 136, 952, 136, C["ink900"], 1)

    out += rect(midx, y0, x1 - midx, midy - y0, C["band"], opacity=0.75)
    out += rect(x0, y0, midx - x0, midy - y0, "#F4F8FF")
    out += rect(midx, midy, x1 - midx, y1 - midy, "#F4F8FF")
    out += rect(x0, midy, midx - x0, y1 - midy, "#F0F0F1")

    q = spec["quadrants"]
    out += text(x0 + 8, y0 + 20, q["tl"], 10, C["ink500"], "bold")
    out += text(x1 - 8, y0 + 20, q["tr"], 10, C["ink500"], "bold", "end")
    out += text(x0 + 8, y1 - 10, q["bl"], 10, C["ink500"], "bold")
    out += text(x1 - 8, y1 - 10, q["br"], 10, C["ink500"], "bold", "end")

    out += arrow(x0, y1, x1 + 10, y1, C["ink900"], 1.2, 8)
    out += arrow(x0, y1, x0, y0 - 10, C["ink900"], 1.2, 8)
    out += text((x0 + x1) / 2, y1 + 30, spec["x_label"], 10, C["ink700"], "bold", "middle")
    yl = (y0 + y1) / 2
    out += (f'<text x="{x0 - 26:.0f}" y="{yl:.0f}" font-size="10" fill="{C["ink700"]}" '
            f'font-weight="bold" text-anchor="middle" transform="rotate(-90 {x0 - 26:.0f} {yl:.0f})">'
            f'{spec["y_label"]}</text>')

    lx = x0
    for name, color in groups.items():
        out += rect(lx, 170, 12, 12, C[color])
        out += text(lx + 18, 180, name, 10.5, C["ink700"])
        lx += 18 + tw(name, 10.5) + 24

    for it in items:
        cx = x0 + it["x"] * (x1 - x0)
        cy = y1 - it["y"] * (y1 - y0)
        out += circle(cx, cy, 9, C[groups[it["group"]]])
        if it["x"] > 0.82:
            out += text(cx - 13, cy + 4, it["name"], 11, C["ink700"], "normal", "end")
        else:
            out += text(cx + 13, cy + 4, it["name"], 11, C["ink700"], "normal", "start")

    out += sidebar(1000, 126, "关键洞察", spec.get("insights", []), 232, C)
    out += text(48, 702, spec.get("source", ""), T["note"], C["ink400"])
    return out + "</svg>"


def render_waffle_group(spec, tokens):
    C = tokens["colors"]
    T = tokens["type"]
    panels = spec["panels"]
    states = spec["states"]
    colors_map = spec.get("colors", {})
    cols = spec.get("cols", 3)
    cell = spec.get("cell", 14)
    gap = 3
    grid = 10 * (cell + gap) - gap
    pw = grid + 90
    ph = grid + 70
    x0, y0 = 48, 210
    title_below = spec.get("title_below", False)

    out = _svg_open(tokens)
    out += head_block(spec, tokens)
    out += text(48, 126, spec["panel_title"], T["panel"], C["ink900"], "bold")
    out += line(48, 136, 952, 136, C["ink900"], 1)

    lx = min(1000, x0 + cols * (pw + 20) + 30)
    ly = 220
    for s in states:
        out += rect(lx, ly - 10, 12, 12, colors_map.get(s, C["primary"]))
        out += text(lx + 18, ly, s, 10.5, C["ink700"])
        ly += 26

    for idx, p in enumerate(panels):
        r, c = idx // cols, idx % cols
        px, py = x0 + c * (pw + 20), y0 + r * (ph + 16)
        if title_below:
            if p.get("top_label"):
                out += text(px + grid / 2, py - 8, p["top_label"], 14, C["ink900"], "bold", "middle")
            grid_y = py
            out += mtext(px + grid / 2, py + grid + 22, p["title"], 11, C["ink700"], "normal", "middle", 1.25)
        else:
            out += mtext(px, py - 22, p["title"], 10.5, C["ink900"], "bold", "start", 1.25)
            grid_y = py
        cell_idx = 0
        acc = 0
        for s in states:
            v = p["parts"].get(s, 0)
            acc += v
        acc = 0
        for s in states:
            v = p["parts"].get(s, 0)
            for _ in range(round(v)):
                row, col = cell_idx // 10, cell_idx % 10
                if row < 10:
                    out += rect(px + col * (cell + gap), grid_y + row * (cell + gap),
                                cell, cell, colors_map.get(s, C["primary"]), rx=2)
                cell_idx += 1
            if spec.get("show_pct", True) and v > 0:
                mid = acc + v / 2
                row = min(9, int(mid // 10))
                out += text(px + grid + 8, grid_y + row * (cell + gap) + cell / 2 + 3.5,
                            f"{v}%", 9.5, C["ink700"])
            acc += v

    if spec.get("takeaway"):
        out += text(48, 520, spec["takeaway"], 12, C["ink700"], "bold")
    for i, (lead, body) in enumerate(spec.get("insights", [])):
        out += text(48, 552 + i * 22, f"{lead}:{body}", 10.5, C["ink700"])
    out += text(48, 702, spec.get("source", ""), 9.5, C["ink400"])
    return out + "</svg>"


def render_waffle(spec, tokens):
    C = tokens["colors"]
    T = tokens["type"]
    parts = spec["parts"]
    total = sum(p["value"] for p in parts)
    cells = spec.get("cells", 100)
    counts = [round(p["value"] / total * cells) for p in parts]
    counts[0] += cells - sum(counts)

    colors = [C["primary"], C["accent"], C["light"], C["second"]]
    cell, gap = 38, 4
    x0, y0 = 130, 210

    out = _svg_open(tokens)
    out += head_block(spec, tokens)
    out += text(48, 126, spec["panel_title"], T["panel"], C["ink900"], "bold")
    out += line(48, 136, 952, 136, C["ink900"], 1)

    idx = 0
    for r in range(10):
        for c in range(10):
            x = x0 + c * (cell + gap)
            y = y0 + r * (cell + gap)
            if idx < cells:
                ci = 0
                acc = counts[0]
                while idx >= acc and ci < len(counts) - 1:
                    ci += 1
                    acc += counts[ci]
                out += rect(x, y, cell, cell, colors[ci % len(colors)], rx=2)
            else:
                out += rect(x, y, cell, cell, "#F1F1F2", rx=2)
            idx += 1

    ly = 260
    for i, p in enumerate(parts):
        out += rect(620, ly - 12, 16, 16, colors[i % len(colors)], rx=2)
        out += text(648, ly, p["name"], 12, C["ink700"])
        out += text(648, ly + 22, f"{p['value'] / total * 100:.0f}%", 18, C["ink900"], "bold")
        ly += 78

    out += sidebar(1000, 126, "关键洞察", spec.get("insights", []), 232, C)
    out += text(48, 702, spec.get("source", ""), T["note"], C["ink400"])
    return out + "</svg>"


def render_lollipop(spec, tokens):
    C = tokens["colors"]
    T = tokens["type"]
    labels = spec["labels"]
    values = spec["values"]
    order = sorted(range(len(labels)), key=lambda i: values[i], reverse=True)
    x0, x1 = 240, 880
    top, row_h = 230, 56
    maxv = max(values)
    scale = (x1 - x0) / maxv

    out = _svg_open(tokens)
    out += head_block(spec, tokens)
    out += text(48, 126, spec["panel_title"], T["panel"], C["ink900"], "bold")
    out += line(48, 136, 952, 136, C["ink900"], 1)

    out += line(x0, top - 18, x0, top + row_h * (len(labels) - 1) + 18, C["ink400"], 1)

    for r, i in enumerate(order):
        cy = top + r * row_h
        v = values[i]
        out += text(220, cy + 4, labels[i], 11, C["ink700"], "normal", "end")
        out += line(x0, cy, x0 + v * scale, cy, C["ink400"], 1.5)
        col = C["accent"] if r == 0 else C["primary"]
        out += circle(x0 + v * scale, cy, 6, col)
        out += text(x0 + v * scale + 12, cy + 4, f"{v:g}", 11, C["ink900"], "bold")

    out += sidebar(1000, 126, "关键洞察", spec.get("insights", []), 232, C)
    out += text(48, 702, spec.get("source", ""), T["note"], C["ink400"])
    return out + "</svg>"


def render_radar(spec, tokens):
    C = tokens["colors"]
    T = tokens["type"]
    dims = spec["dimensions"]
    series = spec["series"]
    n = len(dims)
    cx, cy, r = 560, 400, 200
    colors = [C["second"], C["primary"], C["ink500"]]

    def pt(i, frac):
        a = -math.pi / 2 + i * 2 * math.pi / n
        return (cx + math.cos(a) * r * frac, cy + math.sin(a) * r * frac)

    out = _svg_open(tokens)
    out += head_block(spec, tokens)
    out += text(48, 126, spec["panel_title"], T["panel"], C["ink900"], "bold")
    out += line(48, 136, 952, 136, C["ink900"], 1)

    for k in range(1, 5):
        out += polygon([pt(i, k / 4) for i in range(n)], "none", C["hair"], 1)
        out += rect(cx + 2, cy - r * k / 4 - 8, 22, 13, "#FFFFFF")
        out += text(cx + 6, cy - r * k / 4 + 4, str(k * 25), 8.5, C["ink400"])
    for i in range(n):
        e = pt(i, 1)
        out += line(cx, cy, e[0], e[1], C["hair"], 1)
        lx, ly = pt(i, 1.16)
        cos = math.cos(-math.pi / 2 + i * 2 * math.pi / n)
        anchor = "middle" if abs(cos) < 0.35 else ("start" if cos > 0 else "end")
        out += text(lx, ly + 4, dims[i], 10.5, C["ink700"], "normal", anchor)

    for si, s in enumerate(series):
        col = colors[si % len(colors)]
        pts = [pt(i, max(0, min(100, s["values"][i])) / 100) for i in range(n)]
        if si == 1:
            out += polygon(pts, col, None, opacity=0.14)
        out += polygon(pts, "none", col, 2)
        for p in pts:
            out += circle(p[0], p[1], 3.5, col)

    lx = 120
    for si, s in enumerate(series):
        out += rect(lx, 172, 12, 12, colors[si % len(colors)])
        out += text(lx + 18, 182, s["name"], 10.5, C["ink700"])
        lx += 18 + tw(s["name"], 10.5) + 24

    out += sidebar(1000, 126, "关键洞察", spec.get("insights", []), 232, C)
    out += text(48, 702, spec.get("source", ""), T["note"], C["ink400"])
    return out + "</svg>"


def _mix_white(base, t):
    br = int(base[1:3], 16)
    bg = int(base[3:5], 16)
    bb = int(base[5:7], 16)
    r = int(255 + (br - 255) * t)
    g = int(255 + (bg - 255) * t)
    b = int(255 + (bb - 255) * t)
    return "#%02X%02X%02X" % (r, g, b)


def render_choropleth(spec, tokens):
    import maps
    C = tokens["colors"]
    T = tokens["type"]
    values = spec["values"]
    feats = maps.features()
    proj = maps.projector(feats, 120, 150, 880, 620)
    vmin, vmax = min(values.values()), max(values.values())
    edges = [round(vmin + (vmax - vmin) * k / 5) for k in range(6)]
    for k in range(1, 6):
        if edges[k] <= edges[k - 1]:
            edges[k] = edges[k - 1] + 1
    bin_colors = [_mix_white(C["primary"], 0.25 + 0.15 * k) for k in range(5)]

    def bin_of(v):
        for k in range(5):
            if v < edges[k + 1] or k == 4:
                return k

    out = _svg_open(tokens)
    out += head_block(spec, tokens)
    out += text(48, 126, spec["panel_title"], T["panel"], C["ink900"], "bold")
    out += line(48, 136, 952, 136, C["ink900"], 1)

    for f in feats:
        v = values.get(maps.iso(f))
        fill = "#E9E9E9" if v is None else bin_colors[bin_of(v)]
        d = maps.path_d(f, proj)
        if d:
            out += f'<path d="{d}" fill="{fill}" fill-rule="evenodd" stroke="#FFFFFF" stroke-width="0.6"/>'

    feat_by_iso = {maps.iso(f): f for f in feats}
    offsets = {"USA": (16, 32), "NLD": (36, -18), "CHN": (38, -14)}
    for idx, (iso, v) in enumerate(sorted(values.items(), key=lambda kv: kv[1], reverse=True)[:3]):
        f = feat_by_iso.get(iso)
        p = maps.centroid(f, proj) if f else None
        if not p:
            continue
        ox, oy = offsets.get(iso, (28, -22))
        tx, ty = p[0] + ox, p[1] + oy
        out += line(p[0], p[1], tx, ty, C["ink500"], 0.8)
        out += circle(p[0], p[1], 2, C["ink900"])
        lab = f"{iso} {v:g}%"
        out += rect(tx - 4, ty - 13, tw(lab, 10.5, True) + 8, 17, "#FFFFFF")
        out += text(tx, ty, lab, 10.5, C["ink900"], "bold")

    ly = 630
    for k in range(5):
        out += rect(260 + k * 50, ly, 30, 14, bin_colors[k])
        lab = (f"{edges[k]:.0f}–<{edges[k + 1]:.0f}" if k < 4
               else f"{edges[k]:.0f}–{edges[k + 1]:.0f}")
        out += text(260 + k * 50 + 15, ly + 34, lab, 11, C["ink500"], "normal", "middle")
    out += rect(260 + 5 * 50 + 12, ly, 30, 14, "#E9E9E9")
    out += text(260 + 5 * 50 + 12, ly + 34, "无数据", 11, C["ink500"])

    out += sidebar(1000, 126, "关键洞察", spec.get("insights", []), 232, C, size=11)
    out += text(1000, 360, "数值一览", 11.5, C["ink900"], "bold")
    ly = 386
    for iso, v in sorted(values.items(), key=lambda kv: kv[1], reverse=True):
        out += rect(1000, ly - 10, 11, 11, bin_colors[bin_of(v)])
        out += text(1017, ly, f"{iso} {v:g}", 10.5, C["ink700"])
        ly += 19
    out += text(48, 702, spec.get("source", ""), T["note"], C["ink400"])
    return out + "</svg>"


def render_flow_map(spec, tokens):
    import maps
    C = tokens["colors"]
    T = tokens["type"]
    flows = spec["flows"]
    feats = maps.features()
    proj = maps.projector(feats, 120, 150, 880, 600)
    cent = {maps.iso(f): maps.centroid(f, proj) for f in feats}

    out = _svg_open(tokens)
    out += head_block(spec, tokens)
    out += text(48, 126, spec["panel_title"], T["panel"], C["ink900"], "bold")
    out += line(48, 136, 952, 136, C["ink900"], 1)

    for f in feats:
        d = maps.path_d(f, proj)
        if d:
            out += f'<path d="{d}" fill="#E6E6E6" stroke="#FFFFFF" stroke-width="0.7"/>'

    maxv = max(x["value"] for x in flows)
    ordered = sorted(flows, key=lambda x: x["value"], reverse=True)
    palette = ["#1437B9", "#1B3FD8", "#2972FF", "#4C8DFF", "#7FA6F2", "#A9C8F7"]
    seen = {}
    for idx, fl in enumerate(ordered):
        p1 = cent.get(fl["from"])
        p2 = cent.get(fl["to"])
        if not p1 or not p2:
            continue
        k = seen.get(fl["to"], 0)
        seen[fl["to"]] = k + 1
        p2 = (p2[0] + (k - 1.5) * 18, p2[1] + (k % 2) * 10)
        mx, my = (p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2
        dx, dy = p2[0] - p1[0], p2[1] - p1[1]
        dist = math.hypot(dx, dy) or 1
        sign = 1 if idx % 2 == 0 else -1
        bend = 0.12 + 0.05 * (idx % 3)
        cxp = mx - dy / dist * dist * bend * sign
        cyp = my + dx / dist * dist * bend * sign
        col = palette[idx % len(palette)]
        out += path(f"M{p1[0]:.1f} {p1[1]:.1f} Q{cxp:.1f} {cyp:.1f} {p2[0]:.1f} {p2[1]:.1f}",
                    "none", col, 1 + 3.5 * fl["value"] / maxv, opacity=0.8)
        out += circle(p1[0], p1[1], 3, col)
        ang = math.atan2(p2[1] - cyp, p2[0] - cxp)
        b1 = (p2[0] - 11 * math.cos(ang - 0.45), p2[1] - 11 * math.sin(ang - 0.45))
        b2 = (p2[0] - 11 * math.cos(ang + 0.45), p2[1] - 11 * math.sin(ang + 0.45))
        out += polygon([p2, b1, b2], col, "#FFFFFF", 0.8)

    labeled = set()
    for fl in ordered:
        for iso in (fl["from"], fl["to"]):
            if iso in labeled:
                continue
            labeled.add(iso)
            p = cent.get(iso)
            if p:
                out += text(p[0] + 6, p[1] - 8, iso, 10, C["ink700"], "bold")

    for i, fl in enumerate(ordered):
        lx = 180 + (i % 2) * 320
        ly = 622 + (i // 2) * 25
        out += rect(lx, ly - 11, 13, 13, palette[i % len(palette)])
        out += text(lx + 20, ly, f"{fl['from']}→{fl['to']} {fl['value']:g}", 11, C["ink700"])

    out += sidebar(1000, 126, "关键洞察", spec.get("insights", []), 232, C)
    out += text(48, 702, spec.get("source", ""), T["note"], C["ink400"])
    return out + "</svg>"


def render_mekko(spec, tokens):
    C = tokens["colors"]
    T = tokens["type"]
    segs = spec["segments"]
    share_names = list(segs[0]["shares"].keys())
    colors = [C["primary"], C["second"], C["light"], C["accent"]]
    x0, x1 = 200, 900
    top, bot = 230, 520
    total_w = x1 - x0
    total_h = bot - top

    out = _svg_open(tokens)
    out += head_block(spec, tokens)
    out += text(48, 126, spec["panel_title"], T["panel"], C["ink900"], "bold")
    out += line(48, 136, 952, 136, C["ink900"], 1)

    lx = x0
    for i, name in enumerate(share_names):
        out += rect(lx, 178, 12, 12, colors[i % len(colors)])
        out += text(lx + 18, 188, name, 10.5, C["ink700"])
        lx += 18 + tw(name, 10.5) + 24

    x = x0
    for seg in segs:
        w = total_w * seg["width"] / 100
        y = bot
        for i, name in enumerate(share_names):
            v = seg["shares"][name]
            h = total_h * v / 100
            y -= h
            out += rect(x, y, w - 2, h, colors[i % len(colors)])
            if w > 60 and h > 22:
                fg = "#FFFFFF" if i == 0 else C["ink900"]
                out += text(x + (w - 2) / 2, y + h / 2 + 4, f"{v}%", 11, fg, "bold", "middle")
        out += text(x + (w - 2) / 2, 546, f"{seg['name']}({seg['width']}%)", 10.5, C["ink700"], "normal", "middle")
        x += w

    out += line(x0, bot, x1, bot, C["base"], tokens["lines"]["base"])
    out += sidebar(1000, 126, "关键洞察", spec.get("insights", []), 232, C)
    out += text(48, 702, spec.get("source", ""), T["note"], C["ink400"])
    return out + "</svg>"


def render_slope(spec, tokens):
    C = tokens["colors"]
    T = tokens["type"]
    ents = spec["entities"]
    t1, t2 = spec["t1"], spec["t2"]
    vals = [e["from"] for e in ents] + [e["to"] for e in ents]
    vmin, vmax = min(vals), max(vals)
    pad = (vmax - vmin) * 0.15 or 1
    plot_top, plot_bot = 230, 540
    x_left, x_right = 340, 740

    def yv(v):
        return plot_bot - (v - vmin + pad) / (vmax - vmin + 2 * pad) * (plot_bot - plot_top)

    deltas = [e["to"] - e["from"] for e in ents]
    hi = deltas.index(max(deltas))
    neg = [i for i, d in enumerate(deltas) if d < 0]
    lo = min(neg, key=lambda i: deltas[i]) if neg else None

    out = _svg_open(tokens)
    out += head_block(spec, tokens)
    out += text(48, 126, spec["panel_title"], T["panel"], C["ink900"], "bold")
    out += line(48, 136, 952, 136, C["ink900"], 1)

    out += line(x_left, plot_top - 12, x_left, plot_bot, C["hair"], 1)
    out += line(x_right, plot_top - 12, x_right, plot_bot, C["hair"], 1)
    out += text(x_left, 208, t1, 11, C["ink700"], "bold", "middle")
    out += text(x_right, 208, t2, 11, C["ink700"], "bold", "middle")

    placed = []
    for i, e in enumerate(ents):
        col = C["accent"] if i == hi else (C["neg"] if i == lo else C["ink500"])
        y1, y2 = yv(e["from"]), yv(e["to"])
        out += line(x_left, y1, x_right, y2, col, 2)
        out += circle(x_left, y1, 5, col)
        out += circle(x_right, y2, 5, col)
        out += text(x_left - 12, y1 + 4, f"{e['name']} {e['from']:g}", 10.5, C["ink700"], "normal", "end")
        ly = y2 + 4
        while any(abs(ly - p) < 10 for p in placed):
            ly += 10
        placed.append(ly)
        out += text(x_right + 12, ly, f"{e['to']:g}", 10.5, col, "bold")

    cap = "高亮=最大升幅;红线=下降项。" if neg else "高亮=最大升幅;其余为灰色。"
    out += text(x_left, 580, cap, 9.5, C["ink400"])
    out += sidebar(1000, 126, "关键洞察", spec.get("insights", []), 232, C)
    out += text(48, 702, spec.get("source", ""), T["note"], C["ink400"])
    return out + "</svg>"


def render_dot_strip(spec, tokens):
    C = tokens["colors"]
    T = tokens["type"]
    cats = spec["categories"]
    names = list(cats.keys())
    vals = [v for arr in cats.values() for v in arr]
    vmax = max(vals) * 1.1
    x0, x1 = 220, 900
    top, row_h = 240, 110
    scale = (x1 - x0) / vmax

    def xv(v):
        return x0 + v * scale

    out = _svg_open(tokens)
    out += head_block(spec, tokens)
    out += text(48, 126, spec["panel_title"], T["panel"], C["ink900"], "bold")
    out += line(48, 136, 952, 136, C["ink900"], 1)

    axis_y = top + row_h * (len(names) - 1) + 48
    for v in range(0, int(vmax) + 1, 10):
        out += line(xv(v), top - 24, xv(v), axis_y, "#E8E8E8", 0.8)

    for i, (name, arr) in enumerate(cats.items()):
        cy = top + i * row_h
        out += text(200, cy + 4, name, 12, C["ink700"], "normal", "end")
        out += text(200, cy + 22, f"n={len(arr)}", 10, C["ink500"], "normal", "end")
        med = statistics.median(arr)
        out += line(xv(med), cy - 18, xv(med), cy + 18, C["ink900"], 2)
        for v in sorted(arr):
            out += circle(xv(v), cy, 6, C["primary"], "#FFFFFF", 1)
        out += text(xv(med), cy + 36, f"中位 {med:g}", 10.5, C["ink500"], "normal", "middle")

    out += line(x0, axis_y, x1, axis_y, C["ink400"], 1)
    out += text(x0, axis_y + 20, "0", 11, C["ink500"], "normal", "middle")
    out += text(x1, axis_y + 20, f"{vmax:.0f}", 11, C["ink500"], "normal", "middle")
    out += text(48, 560, "每个点=一份合同;黑线=中位数。", 9.5, C["ink400"])

    out += sidebar(1000, 126, "关键洞察", spec.get("insights", []), 232, C)
    out += text(48, 702, spec.get("source", ""), T["note"], C["ink400"])
    return out + "</svg>"


def render_heatmap(spec, tokens):
    C = tokens["colors"]
    T = tokens["type"]
    rows = spec["rows"]
    cols = spec["columns"]
    values = spec["values"]
    unit = spec.get("unit", "")
    x0, y0 = 240, 220
    cw, ch = 160, 72
    vmax = max(abs(v) for row in values for v in row)
    vmin = min(v for row in values for v in row)

    def mix(base, t):
        br = int(base[1:3], 16)
        bg = int(base[3:5], 16)
        bb = int(base[5:7], 16)
        r = int(255 + (br - 255) * t)
        g = int(255 + (bg - 255) * t)
        b = int(255 + (bb - 255) * t)
        return "#%02X%02X%02X" % (r, g, b)

    out = _svg_open(tokens)
    out += head_block(spec, tokens)
    out += text(48, 126, spec["panel_title"], T["panel"], C["ink900"], "bold")
    out += line(48, 136, 952, 136, C["ink900"], 1)

    for j, c in enumerate(cols):
        out += text(x0 + j * cw + cw / 2, y0 - 14, c, 12, C["ink700"], "bold", "middle")
    for i, r in enumerate(rows):
        out += text(x0 - 12, y0 + i * ch + ch / 2 + 4, r, 12, C["ink700"], "normal", "end")

    for i, row in enumerate(values):
        for j, v in enumerate(row):
            t = 0.12 + 0.88 * abs(v) / vmax
            color = mix(C["primary"] if v >= 0 else C["neg"], t)
            x = x0 + j * cw
            y = y0 + i * ch
            out += rect(x, y, cw - 2, ch - 2, color)
            r = int(color[1:3], 16)
            g = int(color[3:5], 16)
            b = int(color[5:7], 16)
            lum = (0.2126 * r + 0.7152 * g + 0.0722 * b) / 255
            out += text(x + cw / 2 - 1, y + ch / 2 + 4, f"{v:.1f}{unit}", 12,
                        "#FFFFFF" if lum < 0.5 else C["ink900"], "bold", "middle")

    lx, ly = x0, y0 + len(rows) * ch + 30
    steps = 7
    for k in range(steps):
        v = vmin + (vmax - vmin) * k / (steps - 1)
        color = mix(C["primary"] if v >= 0 else C["neg"], 0.12 + 0.88 * abs(v) / vmax)
        out += rect(lx + k * 28, ly, 26, 14, color)
    out += text(lx, ly + 32, f"{vmin:.1f}{unit}", 10, C["ink500"])
    zero_x = lx + (0 - vmin) / (vmax - vmin) * (steps - 1) * 28 + 13
    out += text(zero_x, ly + 32, "0", 10, C["ink500"], "normal", "middle")
    out += text(lx + (steps - 1) * 28 + 26, ly + 32, f"+{vmax:.1f}{unit}", 10, C["ink500"], "normal", "end")

    out += sidebar(1000, 126, "关键洞察", spec.get("insights", []), 232, C)
    out += text(48, 702, spec.get("source", ""), T["note"], C["ink400"])
    return out + "</svg>"
