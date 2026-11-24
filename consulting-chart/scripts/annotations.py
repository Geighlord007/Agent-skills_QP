from chartlib import text, rect, line, circle, polygon, arrow, tw

LAST_WARNINGS = []


def _box(x, y, s, size, anchor):
    w = tw(s, size)
    if anchor == "middle":
        x0 = x - w / 2
    elif anchor == "end":
        x0 = x - w
    else:
        x0 = x
    return (x0, y - size * 0.9, x0 + w, y + size * 0.3)


def _overlap(a, b):
    return not (a[2] <= b[0] or b[2] <= a[0] or a[3] <= b[1] or b[3] <= a[1])


def _capsule(cx, cy, s, tokens, size=9.5, fill=None, stroke=None, fg=None):
    C = tokens["colors"]
    w = tw(s, size, True) + 18
    h = 20
    out = rect(cx - w / 2, cy - h / 2, w, h, fill or "#FFFFFF", stroke or C["ink900"], 1, rx=h / 2)
    out += text(cx, cy + size * 0.36, s, size, fg or C["ink900"], "bold", "middle")
    return out


def draw_background(anns, ctx, tokens):
    C = tokens["colors"]
    out = ""
    for a in anns:
        if a["type"] == "band":
            cx = ctx["colx"](a["column"])
            pad = a.get("pad", 52)
            out += rect(cx - pad, a["top"], 2 * pad, a["bottom"] - a["top"],
                        C["band"], opacity=a.get("opacity", 0.6))
        elif a["type"] == "reference_line":
            y = ctx["yv"](a["value"])
            out += line(ctx["x0"], y, ctx["x1"], y, C["ink400"], 1, "4 4")
    return out


def draw_foreground(anns, ctx, tokens):
    C = tokens["colors"]
    out = ""
    boxes = []
    for a in anns:
        if a["type"] == "ratio":
            cx = ctx["colx"](a["column"])
            cy = a["cy"]
            r = a.get("r", 42)
            out += circle(cx, cy, r, "#FFFFFF", C["ink900"], 1.5)
            out += text(cx, cy - 4, a["label"], 9.5, C["ink500"], "normal", "middle")
            out += text(cx, cy + 16, a["text"], 15, C["ink900"], "bold", "middle")
            out += arrow(cx, cy + r + 2, cx, ctx["yv"](a["arrow_to"]) - 14, C["ink900"], 1.2, 8)
            boxes.append((_box(cx, cy - 4, a["label"], 9.5, "middle"), a.get("id", "ratio.label")))
            boxes.append((_box(cx, cy + 16, a["text"], 15, "middle"), a.get("id", "ratio.text")))
        elif a["type"] == "bracket":
            xi, xj = ctx["colx"](a["from"]), ctx["colx"](a["to"])
            xa, xb = xi - 18, xj + 24
            y = a["y"]
            out += line(xa, y, xb, y, C["ink900"], 1)
            out += line(xa, y, xa, ctx["level_y"](a["from"]), C["ink500"], 0.8)
            if a.get("arrow"):
                out += arrow(xb, y, xb, ctx["yv"](a["arrow_to"]) + 2, C["ink900"], 1.1, 7)
            else:
                out += line(xb, y, xb, ctx["level_y"](a["to"]), C["ink500"], 0.8)
            out += _capsule((xa + xb) / 2, y, a["text"], tokens, 10.5)
            boxes.append((_box((xa + xb) / 2, y, a["text"], 10.5, "middle"), a.get("id", "bracket")))
        elif a["type"] == "capsule":
            x, y = a["x"], a["y"]
            out += _capsule(x, y, a["text"], tokens, a.get("size", 9.5),
                            a.get("fill"), a.get("stroke"), a.get("fg"))
            boxes.append((_box(x, y, a["text"], a.get("size", 9.5), "middle"), a.get("id", "capsule")))
        elif a["type"] == "callout":
            x, y = a["x"], a["y"]
            out += circle(x, y, a.get("r", 26), "#FFFFFF", C["ink900"], 1.5)
            out += text(x, y + 4, a["text"], a.get("size", 12), C["ink900"], "bold", "middle")
            if "arrow_to" in a:
                out += arrow(x, y + a.get("r", 26) + 2, a["arrow_x"], ctx["yv"](a["arrow_to"]) - 10,
                             C["ink900"], 1.1, 7)
            boxes.append((_box(x, y, a["text"], a.get("size", 12), "middle"), a.get("id", "callout")))
        elif a["type"] == "trend_band":
            xa = ctx["x_of"](a["from"])
            xb = ctx["x_of"](a["to"])
            ya = ctx["top_of"](a["from"])
            yb = ctx["top_of"](a["to"])
            out += polygon([(xa + 4, ya - 60), (xb, yb - 60), (xb, yb - 80), (xa + 4, ya - 80)],
                           C["band"], opacity=0.9)
            out += arrow(xa + 10, ya - 70, xb - 4, yb - 70, C["ink900"], 1.2, 8)
            lab = f"{a['from']}–{a['to']} CAGR +{a['value']}{a.get('unit', '')}"
            out += rect(xa + 2, ya - 106, tw(lab, 9.5, True) + 10, 18, "#FFFFFF")
            out += text(xa + 7, ya - 93, lab, 9.5, C["ink700"], "bold")
            boxes.append((_box(xa + 7, ya - 93, lab, 9.5, "start"), a.get("id", "trend_band")))

    warns = []
    for i in range(len(boxes)):
        for j in range(i + 1, len(boxes)):
            if _overlap(boxes[i][0], boxes[j][0]):
                warns.append((boxes[i][1], boxes[j][1]))
    global LAST_WARNINGS
    LAST_WARNINGS = warns
    return out
