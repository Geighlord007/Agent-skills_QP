import math

from chartlib import (text, mtext, rect, line, circle, polygon, path, dotted, arrow,
                      wrap, sidebar, tw, head_block, report_head)


def _open(tokens):
    W = tokens["canvas"]["width"]
    H = tokens["canvas"]["height"]
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
        f'viewBox="0 0 {W} {H}" font-family="{tokens["font"]}">'
        "<style>text{font-variant-numeric:tabular-nums}</style>"
        f'<rect width="{W}" height="{H}" fill="{tokens.get("background", "#FFFFFF")}"/>'
    )


def _cap(cx, cy, s, tokens, size=9.5, fill="#FFFFFF", stroke=None, fg=None):
    C = tokens["colors"]
    w = tw(s, size, True) + 18
    out = rect(cx - w / 2, cy - 10, w, 20, fill, stroke or C["ink900"], 1, rx=10)
    out += text(cx, cy + size * 0.36, s, size, fg or C["ink900"], "bold", "middle")
    return out


def render_stacked_time_series(spec, tokens):
    C = tokens["colors"]
    T = tokens["type"]
    years = spec["years"]
    series = spec["series"]
    colors_map = spec.get("colors", {})
    palette = [C["primary"], C["black"], C["second"], C["light"]]
    x0, x1 = 150, 900
    top, bot = 230, 540
    totals = [sum(s["values"][i] for s in series) for i in range(len(years))]
    scale = (bot - top) / (max(totals) * 1.12)
    colw = (x1 - x0) / len(years)
    bw = min(44, colw * 0.62)
    n = len(series)

    out = _open(tokens)
    out += head_block(spec, tokens)
    out += text(48, 126, spec["panel_title"], T["panel"], C["ink900"], "bold")
    out += line(48, 136, 952, 136, C["ink900"], 1)

    lx = x0
    for si, s in enumerate(series):
        col = C.get(colors_map.get(s["name"], ""), palette[si % len(palette)])
        out += rect(lx, 180, 12, 12, col)
        out += text(lx + 18, 190, s["name"], 10.5, C["ink700"])
        lx += 18 + tw(s["name"], 10.5) + 24

    for i, yr in enumerate(years):
        cx = x0 + colw * (i + 0.5)
        y = bot
        for si, s in enumerate(series):
            v = s["values"][i]
            h = v * scale
            y -= h
            col = C.get(colors_map.get(s["name"], ""), palette[si % len(palette)])
            out += rect(cx - bw / 2, y, bw, h, col)
            if h >= 18:
                fg = C["ink900"] if col == C["light"] else "#FFFFFF"
                out += text(cx, y + h / 2 + 3.5, f"{v:g}", 9.5, fg, "bold", "middle")
        out += text(cx, y - 8, f"{totals[i]:g}", 10.5, C["ink900"], "bold", "middle")
        out += text(cx, 566, str(yr), 9.5, C["ink700"], "normal", "middle")

    out += line(x0 - 20, bot, x1 + 6, bot, C["base"], 1.6)
    cagr = (totals[-1] / totals[0]) ** (1 / (len(years) - 1)) - 1
    xa, xb = x0 + colw * 0.5, x0 + colw * (len(years) - 0.5)
    ya, yb = bot - totals[0] * scale - 34, bot - totals[-1] * scale - 34
    out += arrow(xa, ya, xb, yb, C["ink900"], 1.2, 8)
    out += _cap((xa + xb) / 2, (ya + yb) / 2 - 12, f"+{cagr * 100:.1f}% p.a.", tokens)

    out += sidebar(1000, 126, "关键洞察", spec.get("insights", []), 232, C)
    out += text(48, 702, spec.get("source", ""), T["note"], C["ink400"])
    return out + "</svg>"


def render_bar_pill(spec, tokens):
    C = tokens["colors"]
    T = tokens["type"]
    years = spec["years"]
    values = spec["values"]
    labels = spec.get("labels", [f"{v:g}" for v in values])
    pills = spec.get("pills", [])
    badges = spec.get("badges", {})
    x0, x1 = 150, 900
    top, bot = 250, 540
    scale = (bot - top) / (max(values) * 1.15)
    colw = (x1 - x0) / len(years)
    bw = min(46, colw * 0.62)

    out = _open(tokens)
    out += head_block(spec, tokens)
    out += text(48, 126, spec["panel_title"], T["panel"], C["ink900"], "bold")
    out += line(48, 136, 952, 136, C["ink900"], 1)

    for i, yr in enumerate(years):
        cx = x0 + colw * (i + 0.5)
        h = values[i] * scale
        out += rect(cx - bw / 2, bot - h, bw, h, C["primary"])
        out += text(cx, bot - h - 8, labels[i], 10, C["ink900"], "bold", "middle")
        out += text(cx, 566, str(yr), 9.5, C["ink700"], "normal", "middle")
        if str(yr) in badges:
            out += _cap(cx, bot - h - 34, badges[str(yr)], tokens, 9, C["step"], None, C["ink900"])

    out += line(x0 - 20, bot, x1 + 6, bot, C["base"], 1.6)
    out += text(48, 616, "渗透率", 10, C["ink700"], "bold")
    for i, p in enumerate(pills):
        cx = x0 + colw * (i + 0.5)
        out += rect(cx - 28, 596, 56, 24, C["band"], rx=12)
        out += text(cx, 612, p, 9.5, C["ink900"], "bold", "middle")

    callout = spec.get("callout", "")
    if callout:
        lines = []
        for para in callout.split("\n"):
            lines += wrap(para, 9.5, 250)
        ch = len(lines) * 14 + 18
        out += rect(620, 150, 300, ch, "#FFFFFF", C["ink500"], 1, 6)
        for k, ln in enumerate(lines):
            out += text(634, 168 + k * 14, ln, 9.5, C["ink700"])
        tgt = x0 + colw * (years.index(int(spec.get("callout_year", years[-2]))) + 0.5)
        out += line(620, 150 + ch / 2, tgt, bot - values[years.index(int(spec.get("callout_year", years[-2])))] * scale - 6,
                    C["ink500"], 0.8)

    out += sidebar(1000, 126, "关键洞察", spec.get("insights", []), 232, C)
    out += text(48, 702, spec.get("source", ""), T["note"], C["ink400"])
    return out + "</svg>"


def render_line_forecast(spec, tokens):
    if tokens.get("style") == "bcg":
        return render_line_bcg(spec, tokens)
    C = tokens["colors"]
    T = tokens["type"]
    years = spec["years"]
    values = spec["values"]
    ffrom = spec["forecast_from"]
    x0, x1 = 150, 900
    top, bot = 220, 540
    vmax = max(values) * 1.1
    ymin, ymax = min(years), max(years)

    def xv(y):
        return x0 + (y - ymin) / (ymax - ymin) * (x1 - x0)

    def yv(v):
        return bot - v / vmax * (bot - top)

    out = _open(tokens)
    out += head_block(spec, tokens)
    out += text(48, 126, spec["panel_title"], T["panel"], C["ink900"], "bold")
    out += line(48, 136, 952, 136, C["ink900"], 1)

    for tv in (0, 350, 700, 1050, 1400):
        out += line(x0, yv(tv), x1, yv(tv), "#E8E8E8", 0.8)
        out += text(x0 - 10, yv(tv) + 4, f"{tv:,}", 9, C["ink500"], "normal", "end")

    pts = [(xv(y), yv(v)) for y, v in zip(years, values)]
    actual = [(x, y) for (x, y), yr in zip(pts, years) if yr <= ffrom]
    fore = [(x, y) for (x, y), yr in zip(pts, years) if yr >= ffrom]
    out += path("M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in actual), "none", C["primary"], 2)
    out += path("M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in fore), "none", C["primary"], 2, "5 4")
    for x, y in pts:
        out += circle(x, y, 4, C["primary"], "#FFFFFF", 1.2)

    for y, v in [(2010, 1220), (2015, 393), (2020, 140), (2021, 132), (2022, 135), (2030, 100), (2036, 45)]:
        if y in years:
            i = years.index(y)
            above = values[i] < 500
            out += text(xv(y), yv(values[i]) + (-10 if above else 18), f"{values[i]:g}", 9.5, C["ink900"], "bold", "middle")

    for br in spec.get("brackets", []):
        xa, xb = xv(br["from"]), xv(br["to"])
        yy = br.get("y", 170)
        out += line(xa, yy, xb, yy, C["ink900"], 1)
        out += line(xa, yy, xa, yy + 6, C["ink900"], 1)
        out += line(xb, yy, xb, yy + 6, C["ink900"], 1)
        out += _cap((xa + xb) / 2, yy, br["text"], tokens)

    out += line(x0, 600, x1, 600, C["ink400"], 1)
    out += text(x0, 620, "Actual", 9.5, C["ink700"], "bold")
    out += text(x1, 620, "Forecast", 9.5, C["ink700"], "bold", "end")
    xf = xv(ffrom)
    out += line(x0, 600, xf - 8, 600, C["ink400"], 1.5)
    out += line(xf + 8, 600, x1, 600, C["ink400"], 1.5, "5 4")
    out += circle(x0, 600, 3, C["primary"])
    out += circle(x1, 600, 3, C["primary"])

    callout = spec.get("callout", "")
    if callout:
        lines = wrap(callout, 9.5, 250)
        ch = len(lines) * 14 + 18
        out += rect(640, 150, 290, ch, "#FFFFFF", C["ink500"], 1, 6)
        for k, ln in enumerate(lines):
            out += text(654, 168 + k * 14, ln, 9.5, C["ink700"])
        out += line(640, 150 + ch / 2, xv(ffrom), yv(135) - 8, C["ink500"], 0.8)

    out += sidebar(1000, 126, "关键洞察", spec.get("insights", []), 232, C)
    out += text(48, 702, spec.get("source", ""), T["note"], C["ink400"])
    return out + "</svg>"


def render_line_bcg(spec, tokens):
    C = tokens["colors"]
    W = tokens["canvas"]["width"]
    H = tokens["canvas"]["height"]
    years = spec["years"]
    values = spec["values"]
    ffrom = spec["forecast_from"]
    x0, x1 = 100, W - 60
    y0, y1 = 140, H - 95
    ymax = spec.get("y_max", 1400)
    out = _open(tokens)
    head, hy = report_head(spec, tokens)
    out += head
    out += text(48, 92, spec.get("subtitle", ""), 13, C["primary"])

    def xv(y):
        return x0 + (y - min(years)) / (max(years) - min(years)) * (x1 - x0)

    def yv(v):
        return y1 - v / ymax * (y1 - y0)

    v = 0
    while v <= ymax:
        out += text(x0 - 8, yv(v) + 3, f"{v:,}", 9, C["ink700"], "normal", "end")
        v += 200
    out += line(x0, y1, x1, y1, C["ink400"], 0.8)
    out += line(x0, y0, x0, y1, C["ink400"], 0.8)
    for yr in range(int(min(years)), int(max(years)) + 1, 2):
        out += text(xv(yr), y1 + 16, str(yr), 9, C["ink700"], "normal", "middle")
        out += line(xv(yr), y1, xv(yr), y1 + 4, C["ink400"], 0.8)

    pts = [(xv(y), yv(v)) for y, v in zip(years, values)]
    actual = [(x, y) for (x, y), yr in zip(pts, years) if yr <= ffrom]
    fore = [(x, y) for (x, y), yr in zip(pts, years) if yr >= ffrom]
    out += path("M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in actual), "none", C["primary"], 1.6)
    out += path("M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in fore), "none", C["primary"], 1.6)
    for x, y in pts:
        out += circle(x, y, 2.6, C["primary"])

    for yr in spec.get("label_years", []):
        if yr not in years:
            continue
        i = years.index(yr)
        above = spec.get("label_positions", {}).get(str(yr), "above") == "above"
        label = f"{values[i]:,}"
        lw = tw(label, 11, True)
        ly = yv(values[i]) + (-9 if above else 17)
        out += rect(xv(yr) - lw / 2 - 3, ly - 11, lw + 6, 14, tokens.get("background", "#FFFFFF"))
        out += text(xv(yr), ly, label, 11, C["ink900"], "bold", "middle")

    for b in spec.get("badges", []):
        xa, xb = xv(b["from"]), xv(b["to"])
        by = b.get("y", 140)
        out += line(xa, by, xb, by, C["ink500"], 0.8)
        out += line(xa, by - 5, xa, by + 5, C["ink500"], 0.8)
        out += line(xb, by - 5, xb, by + 5, C["ink500"], 0.8)
        label = b["label"]
        w = tw(label, 12, True) + 26
        out += rect((xa + xb) / 2 - w / 2, by - 11, w, 22, C["primary"], rx=11)
        out += text((xa + xb) / 2, by + 4, label, 12, "#FFFFFF", "bold", "middle")

    callout = spec.get("callout", "")
    if callout:
        bx, by = W * 0.55, H * 0.28
        lines = wrap(callout, 10.5, W * 0.30)
        em = spec.get("callout_emphasis", "")
        elines = wrap(em, 10.5, W * 0.30) if em else []
        bw = max(max([tw(ln, 10.5) for ln in lines + elines] + [0]) + 26, 230)
        bh = (len(lines) + len(elines)) * 15 + 22
        out += rect(bx, by, bw, bh, "#FFFFFF", C["primary"], 1, 2)
        yy = by + 18
        for ln in lines:
            out += text(bx + 12, yy, ln, 10.5, C["ink700"])
            yy += 15
        for ln in elines:
            out += text(bx + 12, yy, ln, 10.5, C["ink900"], "bold")
            yy += 15
        out += line(bx, by + bh, xv(ffrom) - 10, yv(spec.get("callout_to", values[years.index(ffrom)])) - 7,
                    C["ink400"], 0.8)

    ay = H - 18
    out += line(xv(min(years)), ay, xv(ffrom), ay, C["primary"], 1.2)
    out += circle(xv(min(years)), ay, 2.5, C["primary"])
    out += circle(xv(ffrom), ay, 2.5, C["primary"])
    out += text((xv(min(years)) + xv(ffrom)) / 2, ay - 8, spec.get("actual_label", "Actual"),
                12, C["primary"], "bold", "middle")
    out += line(xv(ffrom), ay, xv(max(years)), ay, C["primary"], 1.2)
    out += circle(xv(max(years)), ay, 2.5, C["primary"])
    out += text((xv(ffrom) + xv(max(years))) / 2, ay - 8, spec.get("forecast_label", "Forecast"),
                12, C["primary"], "bold", "middle")
    return out + "</svg>"


def render_mosaic_compare(spec, tokens):
    C = tokens["colors"]
    T = tokens["type"]
    W = tokens["canvas"]["width"]
    H = tokens["canvas"]["height"]
    cols = spec["columns"]
    groups = spec["groups"]
    colors = spec.get("colors", {})
    head, hy = report_head(spec, tokens)
    out = _open(tokens) + head

    left = 16
    plot_left = 0.32 * W
    plot_right = W - 18
    plot_w = plot_right - plot_left
    gap = 0.18 * plot_w if len(cols) > 1 else 0
    total_n = sum(c.get("n", 1) for c in cols)
    widths = [c.get("n", 1) / total_n * (plot_w - gap * (len(cols) - 1)) for c in cols]
    xs = []
    x = plot_left
    for w in widths:
        xs.append(x)
        x += w + gap

    top = hy + 110
    bot = H - 128
    col_top = top + 34

    for j, col in enumerate(cols):
        cx = xs[j] + widths[j] / 2
        headline = col.get("title", "")
        lines = []
        for para in headline.split("\n"):
            lines += wrap(para, 17, widths[j] + 30, True)
        for k, ln in enumerate(lines):
            out += text(cx, top - 4 - (len(lines) - 1 - k) * 20, ln, 17, C["ink900"], "bold", "middle")
        sub = col.get("subtitle", "")
        if sub:
            out += text(cx, top + 14, sub, 11.5, C["ink700"], "normal", "middle")

    if spec.get("row_header"):
        for k, ln in enumerate(wrap(spec["row_header"], 12, plot_left - 34, True)):
            out += text(left, top - 66 + k * 16, ln, 12, C["ink900"], "bold")

    for j, col in enumerate(cols):
        total = sum(col["shares"].values())
        y = col_top
        for g in groups:
            v = col["shares"].get(g, 0)
            h = v / total * (bot - col_top)
            colr = colors.get(g, C["primary"])
            out += rect(xs[j], y, widths[j], h, colr)
            out += text(xs[j] + widths[j] / 2, y + h / 2 + 6, f"{v:g}", 20, "#FFFFFF", "bold", "middle")
            y += h
        out += text(xs[j] + widths[j] / 2, bot + 30, f"{col['n']:,}", 24, C["ink900"], "bold", "middle")
        out += text(xs[j] + widths[j] / 2, bot + 54, "total respondents", 12, C["ink500"], "normal", "middle")

    if len(cols) >= 2:
        for j in range(1, len(cols)):
            ya = col_top
            yb = col_top
            for g in groups[:-1]:
                ya += cols[j - 1]["shares"].get(g, 0) / sum(cols[j - 1]["shares"].values()) * (bot - col_top)
                yb += cols[j]["shares"].get(g, 0) / sum(cols[j]["shares"].values()) * (bot - col_top)
                out += dotted(xs[j - 1] + widths[j - 1], ya, xs[j], yb)

    total = sum(cols[0]["shares"].values())
    y = col_top
    for g in groups:
        v = cols[0]["shares"].get(g, 0)
        h = v / total * (bot - col_top)
        lines = wrap(g, 13, plot_left - 34, True)
        y0 = y + h / 2 - (len(lines) - 1) * 15 / 2 + 4
        for k, ln in enumerate(lines):
            out += text(left, y0 + k * 15, ln, 13, C["ink700"], "normal")
        y += h

    if spec.get("source"):
        out += text(left, H - 12, spec["source"], T["note"], C["ink400"])
    return out + "</svg>"


def render_timeline_matrix(spec, tokens):
    if tokens.get("style") == "bcg":
        return render_timeline_bcg(spec, tokens)
    C = tokens["colors"]
    T = tokens["type"]
    years = spec["years"]
    rows = spec["rows"]
    x0, x1 = 300, 850
    cw = (x1 - x0) / len(years)
    y0 = 200
    row_h = 46

    out = _open(tokens)
    out += head_block(spec, tokens)
    out += text(48, 126, spec["panel_title"], T["panel"], C["ink900"], "bold")
    out += line(48, 136, 952, 136, C["ink900"], 1)

    for j, yr in enumerate(years):
        xa = x0 + j * cw
        pts = [(xa, 160), (xa + cw - 12, 160), (xa + cw, 180), (xa + cw - 12, 200), (xa, 200), (xa + 12, 180)]
        out += polygon(pts, C["primary"])
        out += text(xa + cw / 2, 184, yr, 10, "#FFFFFF", "bold", "middle")

    groups = []
    for r in rows:
        g = r.get("group", "PV")
        if not groups or groups[-1][0] != g:
            groups.append([g, 0, 0])
        groups[-1][2] += 1
    idx = 0
    for g, start, count in [(g[0], sum(x[2] for x in groups[:i]), g[2]) for i, g in enumerate(groups)]:
        ya = y0 + start * row_h
        out += line(96, ya + 4, 96, ya + count * row_h - 4, C["ink400"], 2)
        out += f'<text x="80" y="{ya + count * row_h / 2:.0f}" font-size="11" fill="{C["ink700"]}" font-weight="bold" text-anchor="middle" transform="rotate(-90 80 {ya + count * row_h / 2:.0f})">{g}</text>'

    for i, r in enumerate(rows):
        y = y0 + i * row_h
        out += text(280, y + row_h / 2 + 4, r["name"], 10.5, C["ink700"], "bold", "end")
        for ev in r.get("events", []):
            if ev["year"] not in years:
                continue
            cx = x0 + years.index(ev["year"]) * cw + cw / 2
            label = ev["label"]
            lw = tw(label, 8.5, True) + 12
            out += rect(cx - lw / 2, y + 12, lw, 22, C["band"], rx=11)
            out += text(cx, y + 27, label, 8.5, C["ink900"], "bold", "middle")
        if r.get("note"):
            out += mtext(880, y + 16, r["note"], 8.5, C["ink700"], "normal", "start", 1.3)

    out += text(48, 702, spec.get("source", ""), T["note"], C["ink400"])
    return out + "</svg>"


def _car_icon(x, y, color, window):
    out = polygon([(x, y + 7), (x + 4, y + 3), (x + 12, y + 1), (x + 26, y + 1),
                   (x + 32, y + 7), (x + 37, y + 7), (x + 37, y + 13), (x, y + 13)], color)
    out += polygon([(x + 8, y + 1), (x + 12, y - 5), (x + 24, y - 5), (x + 30, y + 1)], color)
    out += polygon([(x + 10, y), (x + 13, y - 4), (x + 23, y - 4), (x + 28, y)], window)
    out += circle(x + 9, y + 14, 3.5, "#1A1A1A")
    out += circle(x + 29, y + 14, 3.5, "#1A1A1A")
    out += circle(x + 9, y + 14, 1.3, "#FFFFFF")
    out += circle(x + 29, y + 14, 1.3, "#FFFFFF")
    return out


def render_timeline_bcg(spec, tokens):
    C = tokens["colors"]
    W = tokens["canvas"]["width"]
    H = tokens["canvas"]["height"]
    years = spec["years"]
    rows = spec["rows"]
    out = _open(tokens)
    head, hy = report_head(spec, tokens)
    out += head

    if spec.get("examples_label"):
        out += rect(W - 170, 104, 150, 30, C["primary"], rx=1)
        out += text(W - 95, 124, spec["examples_label"], 12, "#FFFFFF", "bold", "middle")

    x0, x1 = 200, 800
    cw = (x1 - x0) / len(years)
    ytop = 150
    for j, yr in enumerate(years):
        x = x0 + j * cw
        pts = [(x, ytop), (x + cw - 10, ytop), (x + cw, ytop + 16),
               (x + cw - 10, ytop + 32), (x, ytop + 32), (x + 10, ytop + 16)]
        out += polygon(pts, C["second"])
        out += text(x + cw / 2, ytop + 21, str(yr), 11, "#FFFFFF", "bold", "middle")

    row_top = 190
    row_h = min(60, (H - 120 - row_top) / len(rows))
    for i, r in enumerate(rows):
        y = row_top + i * row_h
        cv = r.get("group") == "CV"
        cell = C.get("cv_fill", C["light"]) if cv else C["light"]
        accent = C.get("cv_line", C["primary"]) if cv else C["primary"]
        brand_ink = "#1F4E79" if cv else C["second"]
        out += rect(80, y, W - 120, row_h, C["row"] if i % 2 == 0 else C["panel"])
        out += rect(80, y, 4, row_h, accent)
        out += rect(80, y, 110, row_h, cell)
        out += text(135, y + row_h / 2 + 6, r["name"], 20, brand_ink, "bold", "middle")

    for j, yr in enumerate(years):
        x = x0 + j * cw
        out += line(x, row_top, x, row_top + row_h * len(rows), "#C8C9CB", 0.8, "2 3")

    for i, r in enumerate(rows):
        y = row_top + i * row_h
        for ev in r.get("events", []):
            if ev["year"] not in years:
                continue
            cx = x0 + years.index(ev["year"]) * cw + cw / 2
            lw = tw(ev["label"], 11, True)
            out += rect(cx - 42, y + row_h / 2 - 18, 56 + lw, 32, "#E8F6EE", rx=16)
            out += _car_icon(cx - 34, y + row_h / 2 - 8, C["primary"], "#E6F7EE")
            out += text(cx + 8, y + row_h / 2 + 4, ev["label"], 11, C["primary"], "bold")
        if r.get("note"):
            blocks = []
            for para in r["note"].split("\n"):
                blocks.append(wrap(para, 10.5, W - 870))
            total = sum(len(b) for b in blocks) + 2 * (len(blocks) - 1)
            yy = y + row_h / 2 - total * 12.5 / 2 + 13
            for block in blocks:
                for k, ln in enumerate(block):
                    if k == 0:
                        out += text(832, yy, "•", 10.5, C["second"])
                    out += text(842, yy, ln, 10.5, C["ink700"])
                    yy += 12.5
                yy += 2

    groups = []
    for r in rows:
        g = r.get("group", "PV")
        if not groups or groups[-1][0] != g:
            groups.append([g, 0, 0])
        groups[-1][2] += 1
    idx = 0
    for g, _, count in groups:
        cv = g == "CV"
        accent = C.get("cv_line", C["primary"]) if cv else C["primary"]
        brand_ink = "#1F4E79" if cv else C["second"]
        ya = row_top + idx * row_h + 4
        yb = row_top + (idx + count) * row_h - 4
        out += line(58, ya, 58, yb, accent, 2)
        out += circle(58, ya, 2.5, accent)
        out += circle(58, yb, 2.5, accent)
        out += text(20, (ya + yb) / 2 + 5, g, 16, brand_ink, "bold")
        idx += count

    src = spec.get("source", "")
    if src.startswith("Source:"):
        out += text(80, H - 16, "Source:", 12.5, C["ink700"], "bold")
        out += text(80 + tw("Source:", 12.5, True) + 4, H - 16, src[7:].strip(), 12.5, C["ink700"])
    else:
        out += text(80, H - 16, src, 12.5, C["ink700"])
    return out + "</svg>"


def _driver_icon(x, y, color):
    out = circle(x, y - 18, 8, color)
    out += polygon([(x - 12, y - 28), (x + 12, y - 28), (x + 8, y - 22), (x - 8, y - 22)], color)
    out += path(f"M{x - 14} {y + 8} Q{x} {y - 8} {x + 14} {y + 8} L{x + 10} {y + 20} L{x - 10} {y + 20} Z", color)
    out += rect(x - 6, y - 2, 12, 14, "#FFFFFF")
    return out


def _gear_icon(x, y, color):
    out = ""
    for k in range(8):
        import math
        a = k * math.pi / 4
        out += line(x + math.cos(a) * 13, y + math.sin(a) * 13,
                    x + math.cos(a) * 20, y + math.sin(a) * 20, color, 4)
    out += circle(x, y, 14, color)
    out += circle(x, y, 6, "#ECECEE")
    return out


def render_maturity_table(spec, tokens):
    if tokens.get("style") == "bcg":
        return render_maturity_bcg(spec, tokens)
    return render_maturity_table_house(spec, tokens)


def render_maturity_bcg(spec, tokens):
    C = tokens["colors"]
    W = tokens["canvas"]["width"]
    H = tokens["canvas"]["height"]
    levels = spec["levels"]
    rows = spec["rows"]
    n = len(levels)
    x0, x1 = 210, W - 19
    cw = (x1 - x0) / n
    out = _open(tokens)
    head, hy = report_head(spec, tokens)
    out += head

    band = spec.get("bands", [])
    split = [l["id"] for l in levels].index(band[1]["from"]) if len(band) > 1 else 3
    xm = x0 + split * cw
    if band:
        pts1 = [(x0, 88), (xm - 12, 88), (xm + 8, 113), (xm - 12, 138), (x0, 138)]
        out += polygon(pts1, "#939598")
        out += text((x0 + xm - 12) / 2, 118, band[0]["label"], 16, "#FFFFFF", "bold", "middle")
        pts2 = [(xm + 8, 88), (x1, 88), (x1, 138), (xm + 8, 138), (xm - 12, 113)]
        out += polygon(pts2, C["primary"])
        out += text((xm + 8 + x1) / 2, 118, band[1]["label"], 16, "#FFFFFF", "bold", "middle")

    for i, lv in enumerate(levels):
        cx = x0 + i * cw
        out += rect(cx + 2, 150, cw - 4, 30, "#FFFFFF", C["ink400"], 0.8, 2)
        label = lv["id"] + (" (" + lv["tag"] + ")" if lv.get("tag") else "")
        out += text(cx + cw / 2, 170, label, 12, C["second"], "bold", "middle")

    top = 190
    for i in range(1, n):
        for ya, yb in ((190, 270), (500, 540), (550, 620)):
            out += line(x0 + i * cw, ya, x0 + i * cw, yb, "#C8C9CB", 0.8, "2 3")

    def cell(i):
        return x0 + i * cw

    left = x0 - 16
    defs = next((r for r in rows if r.get("kind") == "definition"), None)
    if defs:
        out += text(left, 204, defs["label"], 12, C["second"], "bold", "end")
        for i, cell_data in enumerate(defs["cells"]):
            cx = cell(i) + 8
            title = cell_data.get("title", "") if isinstance(cell_data, dict) else ""
            body = cell_data.get("text", "") if isinstance(cell_data, dict) else str(cell_data)
            y = 204
            if title:
                out += text(cx, y, title, 11, C["second"], "bold")
                y += 16
            for para in body.split("\n"):
                for k, ln in enumerate(wrap(para, 10, cw - 22)):
                    if k == 0:
                        out += text(cx, y, "•", 10, C["primary"])
                    out += text(cx + 10, y, ln, 10, C["ink700"])
                    y += 13
                y += 1

    tr = spec.get("transition", {})
    ty0, ty1 = 330, 480
    cuts = [2 * cw, 3 * cw, 4 * cw]
    bands = [(ty0, ty0 + 50), (ty0 + 50, ty0 + 100), (ty0 + 100, ty1)]
    for (ya, yb), cut in zip(bands, cuts):
        out += rect(x0, ya, cut, yb - ya, "#939598")
        out += rect(x0 + cut, ya, x1 - (x0 + cut), yb - ya, C["light"])
    out += _driver_icon(x0 + 100, 392, C["second"])
    out += text(x0 + 100, 425, tr.get("driver", "驾驶员"), 11.5, C["ink900"], "bold", "middle")
    out += _gear_icon(x1 - 95, 392, C["second"])
    out += text(x1 - 95, 425, tr.get("system", "系统"), 11.5, C["ink900"], "bold", "middle")
    out += text(left, 358, tr.get("execute", "执行驾驶行为"), 12, C["second"], "bold", "end")
    out += text(left, 408, tr.get("supervise", "监督驾驶环境"), 12, C["second"], "bold", "end")
    out += text(left, 458, tr.get("emergency", "紧急接管"), 12, C["second"], "bold", "end")

    usage = next((r for r in rows if r.get("kind") == "usage"), None)
    if usage:
        out += text(left, 522, usage["label"], 12, C["second"], "bold", "end")
        for i, txt in enumerate(usage["cells"]):
            out += text(cell(i) + 8, 522, str(txt), 9.5, C["ink700"])

    ex = next((r for r in rows if r.get("kind") == "examples"), None)
    if ex:
        out += text(left, 566, ex["label"], 12, C["second"], "bold", "end")
        for i, txt in enumerate(ex["cells"]):
            cx = cell(i) + 8
            y = 566
            for para in str(txt).split("\n"):
                for k, ln in enumerate(wrap(para, 11.5, cw - 22)):
                    if k == 0:
                        out += text(cx, y, "•", 11.5, C["primary"])
                    out += text(cx + 11, y, ln, 11.5, C["ink700"])
                    y += 16
                y += 1

    out += line(x0, 540, x1, 540, "#C8C9CB", 0.8)
    out += line(x0, 544, x1, 544, "#C8C9CB", 0.8)
    out += text(8, 700, spec.get("source", ""), 10.5, C["ink500"])
    return out + "</svg>"


def render_maturity_table_house(spec, tokens):
    C = tokens["colors"]
    T = tokens["type"]
    levels = spec["levels"]
    bands = spec["bands"]
    rows = spec["rows"]
    x0, x1 = 200, 1220
    cw = (x1 - x0) / len(levels)
    left = 48

    out = _open(tokens)
    out += head_block(spec, tokens)
    out += text(48, 126, spec["panel_title"], T["panel"], C["ink900"], "bold")
    out += line(48, 136, 952, 136, C["ink900"], 1)

    for b in bands:
        i = [l["id"] for l in levels].index(b["from"])
        j = [l["id"] for l in levels].index(b["to"])
        out += rect(x0 + i * cw, 160, (j - i + 1) * cw - 4, 30, C.get(b.get("color", "primary"), C["primary"]))
        out += text(x0 + (i + (j - i + 1) / 2) * cw, 180, b["label"], 10.5, "#FFFFFF", "bold", "middle")

    for i, lv in enumerate(levels):
        out += text(x0 + i * cw + cw / 2, 212, lv["id"], 11, C["ink900"], "bold", "middle")
        out += text(x0 + i * cw + cw / 2, 228, lv.get("name", ""), 9, C["ink700"], "normal", "middle")

    for st in spec.get("stair", []):
        i = [l["id"] for l in levels].index(st["from"])
        j = [l["id"] for l in levels].index(st["to"])
        out += rect(x0 + i * cw, 240, (j - i + 1) * cw - 2, 26, st.get("color", C["step"]))
        out += text(x0 + (i + (j - i + 1) / 2) * cw, 257, st["label"], 9.5, C["ink900"], "bold", "middle")

    y = 292
    for row in rows:
        h = row.get("height", 110)
        out += text(left, y + 14, row["label"], 9.5, C["ink900"], "bold")
        out += line(left, y + h - 6, x1, y + h - 6, C["hair"], 1)
        for i, cell in enumerate(row["cells"]):
            lines = []
            for para in str(cell).split("\n"):
                lines += wrap(para, 8.3, cw - 16)
            for k, ln in enumerate(lines[:9]):
                out += text(x0 + i * cw + 8, y + 14 + k * 12, ln, 8.3, C["ink700"])
        y += h

    out += text(48, 702, spec.get("source", ""), T["note"], C["ink400"])
    return out + "</svg>"


def _color(C, key):
    return C.get(key, key)


def _ink_on(hexcolor, C):
    h = hexcolor.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    lum = (0.2126 * r + 0.7152 * g + 0.0722 * b) / 255
    return C["ink900"] if lum > 0.5 else "#FFFFFF"


def _chip_row(items, x0, x1, y0, tokens, size=9.5):
    C = tokens["colors"]
    placed = []
    out = ""
    for x, label, color in sorted(items, key=lambda t: t[0]):
        w = tw(label, size, True) + 16
        left = min(max(x - w / 2, x0), x1 - w)
        yy = y0
        for lv in range(2):
            yy = y0 + lv * 19
            if not any(abs(yy - b) < 18 and not (left + w + 4 < a or left > bb + 4)
                       for a, bb, b in placed):
                break
        while any(abs(yy - b) < 18 and not (left + w + 4 < a or left > bb + 4)
                  for a, bb, b in placed) and left + w + 6 < x1:
            left += 6
        placed.append((left, left + w, yy))
        fill = _color(C, color)
        out += rect(left, yy - 9, w, 18, fill, rx=2)
        out += text(left + w / 2, yy + size * 0.36, label, size, _ink_on(fill, C), "bold", "middle")
    return out


def _row_lines(label, size, maxw):
    lines = []
    for para in str(label).split("\n"):
        lines += wrap(para, size, maxw, True)
    return lines


def render_quadrant_matrix_ref(spec, tokens):
    C = tokens["colors"]
    W = tokens["canvas"]["width"]
    H = tokens["canvas"]["height"]
    items = spec["items"]
    groups = spec["groups"]
    quads = spec["quadrants"]
    head, hy = report_head(spec, tokens)
    out = _open(tokens) + head
    x0, x1 = 200, W - 70
    y0, y1 = hy + 40, H - 190
    xm, ym = (x0 + x1) / 2, (y0 + y1) / 2

    cells = [
        (x0, y0, xm, ym, quads["top_left"], "start", "top", C["band"]),
        (xm, y0, x1, ym, quads["top_right"], "end", "top", C.get("teal_tint", C["band"])),
        (x0, ym, xm, y1, quads["bottom_left"], "start", "bottom", C["step"]),
        (xm, ym, x1, y1, quads["bottom_right"], "end", "bottom", C["light"]),
    ]
    for xa, ya, xb, yb, q, anchor, corner, fill in cells:
        out += rect(xa, ya, xb - xa, yb - ya, fill)
        tx = xa + 20 if anchor == "start" else xb - 20
        ty = ya + 34 if corner == "top" else yb - 20
        out += text(tx, ty, q["label"], 14, C["ink900"], "bold", anchor)

    out += line(xm, y0, xm, y1, "#FFFFFF", 2)
    out += line(x0, ym, x1, ym, "#FFFFFF", 2)
    out += rect(x0, y0, x1 - x0, y1 - y0, "none", C["ink900"], 1)

    def xv(v):
        return x0 + v / 100 * (x1 - x0)

    def yv(v):
        return y1 - v / 100 * (y1 - y0)

    xt = spec.get("x_ticks", ["低", "中", "高"])
    yt = spec.get("y_ticks", ["低", "中", "高"])
    for k, lab in enumerate(xt):
        out += text(xv((k + 0.5) / len(xt) * 100), y1 + 26, lab, 12, C["ink700"], "normal", "middle")
    for k, lab in enumerate(yt):
        out += text(x0 - 22, yv((k + 0.5) / len(yt) * 100) + 4, lab, 12, C["ink700"], "normal", "end")

    ay = y1 + 58
    out += arrow(x0, ay, x1, ay, C["ink900"], 1.6, 14)
    out += arrow(x1, ay, x0, ay, C["ink900"], 1.6, 14)
    out += rect((x0 + x1) / 2 - 46, ay - 11, 92, 24, "#FFFFFF")
    out += text((x0 + x1) / 2, ay + 7, spec["x_label"], 12, C["ink900"], "bold", "middle")
    ax = x0 - 62
    out += arrow(ax, y1, ax, y0, C["ink900"], 1.6, 14)
    out += arrow(ax, y0, ax, y1, C["ink900"], 1.6, 14)
    out += rect(ax - 12, (y0 + y1) / 2 - 42, 24, 84, "#FFFFFF")
    out += f'<text x="{ax - 2}" y="{(y0 + y1) / 2 + 4}" font-size="12" fill="{C["ink900"]}" font-weight="bold" text-anchor="middle" transform="rotate(-90 {ax - 2} {(y0 + y1) / 2 + 4})">{spec["y_label"]}</text>'

    for it in items:
        cx, cy = xv(it["x"]), yv(it["y"])
        color = _color(C, groups[it["group"]])
        out += circle(cx, cy, 9, color)
        lines = wrap(it["label"], 10, 160)
        pos = it.get("pos", "right")
        if pos == "left":
            tx, anchor = cx - 15, "end"
            ty = cy - (len(lines) - 1) * 13 / 2 + 4
        elif pos == "above":
            tx, anchor = cx, "middle"
            ty = cy - 18 - (len(lines) - 1) * 13
        elif pos == "below":
            tx, anchor = cx, "middle"
            ty = cy + 24
        else:
            tx, anchor = cx + 15, "start"
            ty = cy - (len(lines) - 1) * 13 / 2 + 4
        for k, ln in enumerate(lines):
            out += text(tx, ty + k * 13, ln, 10, color, "normal", anchor)

    lx = W * 0.36
    for name, color in groups.items():
        out += circle(lx, H - 34, 7, _color(C, color))
        out += text(lx + 13, H - 30, name, 11, C["ink700"])
        lx += 13 + tw(name, 11) + 36

    if spec.get("source"):
        out += text(20, H - 10, spec["source"], 10.5, C["ink400"])
    return out + "</svg>"


def render_target_dots(spec, tokens):
    if tokens.get("style") == "deloitte":
        return render_target_dots_deloitte(spec, tokens)
    C = tokens["colors"]
    T = tokens["type"]
    rows = spec["rows"]
    panels = spec["panels"]
    n = len(rows)
    two = len(panels) > 1
    if two:
        panel_left, panel_right, gap = 205, 960, 44
        pw = (panel_right - panel_left - gap * (len(panels) - 1)) / len(panels)
        bounds = [(panel_left + i * (pw + gap), panel_left + i * (pw + gap) + pw)
                  for i in range(len(panels))]
        label_x = 190
        bracket_x = None
    else:
        bounds = [(225, 850)]
        pw = 625
        label_x = 210
        bracket_x = 880

    top, bot = 272, 540
    row_h = (bot - top) / (n - 1) if n > 1 else 0
    centers = [top + i * row_h for i in range(n)]
    bar_h = min(22, row_h * 0.48)
    dash = 5.2 if two else 5.6

    out = _open(tokens)
    out += head_block(spec, tokens)
    out += text(48, 126, spec["panel_title"], T["panel"], C["ink900"], "bold")
    out += line(48, 136, 952, 136, C["ink900"], 1)

    for pi, p in enumerate(panels):
        x0, x1 = bounds[pi]
        xmax = p.get("x_max", spec.get("x_max", 80))
        step = p.get("x_step", spec.get("x_step", 10))
        out += text(x0, 166, p["title"], 12, C["ink900"], "bold")

        v = 0
        while v <= xmax + 1e-9:
            x = x0 + v / xmax * (x1 - x0)
            out += text(x, 192, f"{v:g}%", 9, C["ink500"], "normal", "middle")
            out += line(x, 258, x, 548, "#E8E8E8", 0.8)
            v += step
        out += line(x0, 258, x0, 548, C["ink400"], 1)

        legend_fill = p.get("bar_fill", "none")
        out += rect(x0, 207, 18, 10, "#FFFFFF" if legend_fill == "none" else _color(C, legend_fill),
                    C["ink900"], 1)
        out += text(x0 + 24, 216, p.get("bar_label", "整体"), 9.5, C["ink700"])

        bar_vals = p.get("bar_values", [])
        for i in range(n):
            cy = centers[i]
            if i < len(bar_vals):
                xe = x0 + bar_vals[i] / xmax * (x1 - x0)
                out += rect(x0, cy - bar_h / 2, xe - x0, bar_h,
                            "#FFFFFF" if legend_fill == "none" else _color(C, legend_fill),
                            C["ink900"], 1 if legend_fill == "none" else 0)
            dots = []
            for s in p.get("series", []):
                v = s["values"][i]
                if v is None:
                    continue
                dots.append([x0 + v / xmax * (x1 - x0), _color(C, s["color"])])
            dots.sort(key=lambda d: d[0])
            ys = [cy] * len(dots)
            k = 0
            while k < len(dots):
                j = k + 1
                while j < len(dots) and dots[j][0] - dots[j - 1][0] < dash * 1.6:
                    j += 1
                if j - k > 1:
                    d = spec.get("dodge", 0.65)
                    offs = [0, -dash * d, dash * d, -dash * 2 * d, dash * 2 * d]
                    for m in range(k, j):
                        ys[m] = cy + offs[min(m - k, len(offs) - 1)]
                k = j
            for (xv, color), yy in zip(dots, ys):
                out += circle(xv, yy, dash, color, "#FFFFFF", 1.4)

        if p.get("series"):
            items = []
            for s in p["series"]:
                first = next((v for v in s["values"] if v is not None), None)
                if first is None:
                    continue
                xv = x0 + first / xmax * (x1 - x0)
                items.append((xv, s["name"], s["color"]))
            out += _chip_row(items, x0, x1, 230, tokens)

    for i, name in enumerate(rows):
        lines = _row_lines(name, 10.5, 150)
        cy = centers[i]
        y0 = cy - (len(lines) - 1) * 10.5 * 1.2 / 2 + 3.5
        for k, ln in enumerate(lines):
            out += text(label_x, y0 + k * 10.5 * 1.2, ln, 10.5, C["ink900"], "bold", "end")

    if bracket_x:
        for br in spec.get("brackets", []):
            ya, yb = centers[br["from"]], centers[br["to"]]
            out += line(bracket_x, ya, bracket_x, yb, C["ink500"], 2)
            out += line(bracket_x - 4, ya, bracket_x + 4, ya, C["ink500"], 2)
            out += line(bracket_x - 4, yb, bracket_x + 4, yb, C["ink500"], 2)
            lines = wrap(br["text"], 9.5, 330)
            ty = (ya + yb) / 2 - (len(lines) - 1) * 13 / 2 + 3
            for k, ln in enumerate(lines):
                out += text(bracket_x + 14, ty + k * 13, ln, 9.5, C["ink700"])
    elif spec.get("insights"):
        out += sidebar(1000, 166, "关键洞察", spec["insights"], 232, C)

    out += text(48, 702, spec.get("source", ""), T["note"], C["ink400"])
    return out + "</svg>"


def render_target_dots_deloitte(spec, tokens):
    C = tokens["colors"]
    W = tokens["canvas"]["width"]
    H = tokens["canvas"]["height"]
    rows = spec["rows"]
    panels = spec["panels"]
    n = len(rows)
    two = len(panels) > 1
    head, hy = report_head(spec, tokens)
    out = _open(tokens) + head

    if two:
        label_x = 22
        plot_l, plot_r = 0.16 * W, W - 24
        gap = 0.035 * W
        pw = (plot_r - plot_l - gap * (len(panels) - 1)) / len(panels)
        bounds = [(plot_l + i * (pw + gap), plot_l + i * (pw + gap) + pw)
                  for i in range(len(panels))]
    else:
        label_x = 22
        bounds = [(0.175 * W, 0.815 * W)]
        pw = bounds[0][1] - bounds[0][0]

    top = hy + (200 if n <= 5 else (160 if two else 122))
    bot = H - (264 if n <= 5 else 150)
    row_h = (bot - top) / (n - 1) if n > 1 else 0
    bar_h = min(38, row_h * 0.46)
    dash = spec.get("dot_size", 7)
    dstroke = spec.get("dot_stroke", 1.6)

    for pi, p in enumerate(panels):
        x0, x1 = bounds[pi]
        xmax = p.get("x_max", spec.get("x_max", 80))
        step = p.get("x_step", spec.get("x_step", 10))
        out += text(x0, top - 124, p["title"], 12, C["ink900"], "bold")

        legend_fill = p.get("bar_fill", "none")
        out += circle(x0 + 7, top - 96, 6, "#FFFFFF" if legend_fill == "none" else _color(C, legend_fill),
                      C["ink900"], 1)
        out += text(x0 + 20, top - 92, p.get("bar_label", "整体"), 10, C["ink700"])

        v = 0
        while v <= xmax + 1e-9:
            x = x0 + v / xmax * (x1 - x0)
            out += text(x, top - 78, f"{v:g}%", 10, C["ink700"], "normal", "middle")
            out += line(x, top - 14, x, bot + 12, "#D8D8D8", 0.9)
            v += step
        out += line(x0, top - 14, x0, bot + 12, C["ink900"], 1.2)

        bar_vals = p.get("bar_values", [])
        for i in range(n):
            cy = top + i * row_h
            if i < len(bar_vals):
                xe = x0 + bar_vals[i] / xmax * (x1 - x0)
                out += rect(x0, cy - bar_h / 2, xe - x0, bar_h,
                            "#FFFFFF" if legend_fill == "none" else _color(C, legend_fill),
                            C["ink900"], 1 if legend_fill == "none" else 0)
            dots = []
            for s in p.get("series", []):
                val = s["values"][i]
                if val is None:
                    continue
                dots.append([x0 + val / xmax * (x1 - x0), _color(C, s["color"])])
            dots.sort(key=lambda d: d[0])
            ys = [cy] * len(dots)
            k = 0
            while k < len(dots):
                j = k + 1
                while j < len(dots) and dots[j][0] - dots[j - 1][0] < dash * 1.6:
                    j += 1
                if j - k > 1:
                    d = spec.get("dodge", 0.65)
                    offs = [0, -dash * d, dash * d, -dash * 2 * d, dash * 2 * d]
                    for m in range(k, j):
                        ys[m] = cy + offs[min(m - k, len(offs) - 1)]
                k = j
            for (xv, color), yy in zip(dots, ys):
                out += circle(xv, yy, dash, color, "#FFFFFF", dstroke) if dstroke else circle(xv, yy, dash, color)

        if p.get("series"):
            items = []
            for s in p["series"]:
                first = next((v for v in s["values"] if v is not None), None)
                if first is None:
                    continue
                items.append((x0 + first / xmax * (x1 - x0), s["name"], s["color"]))
            out += _chip_row(items, x0, x1, top - 58, tokens, size=10)

    for i, name in enumerate(rows):
        lines = _row_lines(name, 11.5, (bounds[0][0] - label_x - 16) if not two else (bounds[0][0] - label_x - 22))
        cy = top + i * row_h
        y0 = cy - (len(lines) - 1) * 11.5 * 1.2 / 2 + 4
        for k, ln in enumerate(lines):
            out += text(label_x, y0 + k * 11.5 * 1.2, ln, 11.5, C["ink900"], "bold")

    if not two:
        bx = 0.845 * W
        for br in spec.get("brackets", []):
            ya, yb = top + br["from"] * row_h, top + br["to"] * row_h
            out += line(bx, ya, bx, yb, C["ink500"], 2.2)
            out += line(bx - 5, ya, bx + 5, ya, C["ink500"], 2.2)
            out += line(bx - 5, yb, bx + 5, yb, C["ink500"], 2.2)
            lines = wrap(br["text"], 10, W - bx - 30)
            ty = (ya + yb) / 2 - (len(lines) - 1) * 14 / 2 + 4
            for k, ln in enumerate(lines):
                out += text(bx + 14, ty + k * 14, ln, 10, C["ink700"])

    if spec.get("notes"):
        ny = H - (190 if n <= 5 else 60)
        out += text(20, ny, "Notes: " + spec["notes"], 9.5, C["ink500"])
    if spec.get("source"):
        sy = H - (44 if n <= 5 else 24)
        out += text(20, sy, spec["source"], 9.5, C["ink400"])
    return out + "</svg>"


def render_journey_stack(spec, tokens):
    if tokens.get("style") == "deloitte":
        return render_journey_stack_deloitte(spec, tokens)
    C = tokens["colors"]
    T = tokens["type"]
    rows = spec["rows"]
    stages = spec["stages"]
    values = spec["values"]
    n = len(rows)
    x0, x1 = 200, 880
    top, bot = 232, 600
    row_h = (bot - top) / n
    bar_h = min(24, row_h * 0.62)
    scale = (x1 - x0) / 100

    out = _open(tokens)
    out += head_block(spec, tokens)
    out += text(48, 126, spec["panel_title"], T["panel"], C["ink900"], "bold")
    out += line(48, 136, 952, 136, C["ink900"], 1)

    lx = x0
    for st in stages:
        fill = _color(C, st["color"])
        out += rect(lx, 184, 12, 12, fill,
                    _color(C, st["stroke_color"]) if st.get("stroke_color") else None,
                    1 if st.get("stroke_color") else 0)
        out += text(lx + 18, 194, st["name"], 10.5, C["ink700"])
        lx += 18 + tw(st["name"], 10.5) + 26

    for i, row in enumerate(rows):
        cy = top + row_h * (i + 0.5)
        lines = _row_lines(row, 10.5, 170)
        y0 = cy - (len(lines) - 1) * 10.5 * 1.2 / 2 + 3.5
        for k, ln in enumerate(lines):
            out += text(x0 - 14, y0 + k * 10.5 * 1.2, ln, 10.5, C["ink900"], "bold", "end")
        x = x0
        for j, st in enumerate(stages):
            v = values[i][j]
            if v <= 0:
                continue
            w = v * scale
            fill = _color(C, st["color"])
            stroke = _color(C, st["stroke_color"]) if st.get("stroke_color") else None
            out += rect(x, cy - bar_h / 2, w, bar_h, fill, stroke, 1 if stroke else 0)
            if w >= 18:
                out += text(x + w / 2, cy + 3.5, f"{v:g}%", 9.5,
                            st.get("fg", "#FFFFFF"), "bold", "middle")
            x += w

    out += line(x0, 612, x1, 612, C["ink400"], 1)
    out += text(x0, 630, "0", 9, C["ink500"], "normal", "middle")
    out += text(x1, 630, "100%", 9, C["ink500"], "normal", "middle")

    for br in spec.get("brackets", []):
        ya = top + row_h * (br["from"] + 0.5)
        yb = top + row_h * (br["to"] + 0.5)
        bx = 900
        out += line(bx, ya, bx, yb, C["ink500"], 2)
        out += line(bx - 4, ya, bx + 4, ya, C["ink500"], 2)
        out += line(bx - 4, yb, bx + 4, yb, C["ink500"], 2)
        lines = wrap(br["text"], 9.5, 340)
        ty = (ya + yb) / 2 - (len(lines) - 1) * 13 / 2 + 3
        for k, ln in enumerate(lines):
            out += text(bx + 14, ty + k * 13, ln, 9.5, C["ink700"])

    out += text(48, 702, spec.get("source", ""), T["note"], C["ink400"])
    return out + "</svg>"


def render_journey_stack_deloitte(spec, tokens):
    C = tokens["colors"]
    W = tokens["canvas"]["width"]
    H = tokens["canvas"]["height"]
    rows = spec["rows"]
    stages = spec["stages"]
    values = spec["values"]
    n = len(rows)
    head, hy = report_head(spec, tokens)
    out = _open(tokens) + head
    x0, x1 = 190, 0.74 * W
    top, bot = hy + 100, H - 150
    row_h = (bot - top) / n
    bar_h = min(28, row_h * 0.62)
    scale = (x1 - x0) / 100

    lx = x0
    for st in stages:
        fill = _color(C, st["color"])
        out += rect(lx, top - 54, 16, 16, fill,
                    _color(C, st["stroke_color"]) if st.get("stroke_color") else None,
                    1 if st.get("stroke_color") else 0)
        out += text(lx + 24, top - 41, st["name"], 11.5, C["ink700"])
        lx += 24 + tw(st["name"], 11.5) + 26

    for i, row in enumerate(rows):
        cy = top + row_h * (i + 0.5)
        lines = _row_lines(row, 11.5, 170)
        y0 = cy - (len(lines) - 1) * 11.5 * 1.2 / 2 + 4
        for k, ln in enumerate(lines):
            out += text(x0 - 16, y0 + k * 11.5 * 1.2, ln, 11.5, C["ink900"], "bold", "end")
        x = x0
        for j, st in enumerate(stages):
            v = values[i][j]
            if v <= 0:
                continue
            w = v * scale
            fill = _color(C, st["color"])
            stroke = _color(C, st["stroke_color"]) if st.get("stroke_color") else None
            out += rect(x, cy - bar_h / 2, w, bar_h, fill, stroke, 1 if stroke else 0)
            if w >= 18:
                out += text(x + w / 2, cy + 4, f"{v:g}%", 11, st.get("fg", "#FFFFFF"), "bold", "middle")
            x += w

    out += line(x0, bot + 16, x1, bot + 16, C["ink400"], 1)
    out += text(x0, bot + 36, "0", 10, C["ink500"], "normal", "middle")
    out += text(x1, bot + 36, "100%", 10, C["ink500"], "normal", "middle")

    bx = 0.77 * W
    for br in spec.get("brackets", []):
        ya = top + row_h * (br["from"] + 0.5)
        yb = top + row_h * (br["to"] + 0.5)
        out += line(bx, ya, bx, yb, C["ink500"], 2.2)
        out += line(bx - 5, ya, bx + 5, ya, C["ink500"], 2.2)
        out += line(bx - 5, yb, bx + 5, yb, C["ink500"], 2.2)
        lines = wrap(br["text"], 10, W - bx - 26)
        ty = (ya + yb) / 2 - (len(lines) - 1) * 14 / 2 + 4
        for k, ln in enumerate(lines):
            out += text(bx + 14, ty + k * 14, ln, 10, C["ink700"])

    if spec.get("notes"):
        ny = H - (190 if n <= 5 else 60)
        out += text(20, ny, "Notes: " + spec["notes"], 9.5, C["ink500"])
    if spec.get("source"):
        sy = H - (44 if n <= 5 else 24)
        out += text(20, sy, spec["source"], 9.5, C["ink400"])
    return out + "</svg>"


def render_bar_future(spec, tokens):
    if tokens.get("style") == "deloitte":
        return render_bar_future_deloitte(spec, tokens)
    C = tokens["colors"]
    T = tokens["type"]
    rows = spec["rows"]
    panels = spec["panels"]
    n = len(rows)
    bounds = [(240, 570), (690, 1020)]
    label_x = 220
    top, bot = 258, 570
    row_h = (bot - top) / (n - 1) if n > 1 else 0
    bar_h = min(24, row_h * 0.42)

    out = _open(tokens)
    out += head_block(spec, tokens)
    out += text(48, 126, spec["panel_title"], T["panel"], C["ink900"], "bold")
    out += line(48, 136, 952, 136, C["ink900"], 1)

    out += circle(240, 190, 5, C["ink900"])
    out += text(252, 194, spec.get("current_label", "当前值"), 10.5, C["ink700"])
    out += line(400, 182, 400, 198, C["ink900"], 2.5)
    out += text(410, 194, spec.get("future_label", "未来值"), 10.5, C["ink700"])

    for pi, p in enumerate(panels):
        x0, x1 = bounds[pi]
        color = _color(C, p["color"])
        out += text(x0, 170, p["title"], 12, C["ink900"], "bold")
        v = 0
        while v <= 100 + 1e-9:
            x = x0 + v / 100 * (x1 - x0)
            out += text(x, 216, f"{v:g}%", 9, C["ink500"], "normal", "middle")
            out += line(x, 228, x, 582, "#E8E8E8", 0.8)
            v += 20
        out += line(x0, 228, x0, 582, C["ink400"], 1)

        for i in range(n):
            cy = top + i * row_h
            cur = p["current"][i]
            fut = p["future"][i]
            xe = x0 + cur / 100 * (x1 - x0)
            xf = x0 + fut / 100 * (x1 - x0)
            out += rect(x0, cy - bar_h / 2, xe - x0, bar_h, color)
            if xe - x0 >= 30:
                out += text(xe - 7, cy + 3.5, f"{cur:g}%", 9.5, "#FFFFFF", "bold", "end")
            else:
                out += text(xe, cy + bar_h / 2 + 12, f"{cur:g}%", 9, color, "bold", "middle")
            out += line(xe, cy, xf, cy, C["ink400"], 0.8)
            out += line(xf, cy - bar_h / 2, xf, cy + bar_h / 2, color, 2.5)
            lw = tw(f"{fut:g}%", 9.5, True)
            if xf + 7 + lw <= x1:
                out += text(xf + 7, cy + 3.5, f"{fut:g}%", 9.5, C["ink900"], "bold")
            else:
                out += text(xf - 7, cy + 3.5, f"{fut:g}%", 9.5, C["ink900"], "bold", "end")

    for i, name in enumerate(rows):
        lines = _row_lines(name, 10.5, 190)
        cy = top + i * row_h
        y0 = cy - (len(lines) - 1) * 10.5 * 1.2 / 2 + 3.5
        for k, ln in enumerate(lines):
            out += text(label_x, y0 + k * 10.5 * 1.2, ln, 10.5, C["ink700"], "normal", "end")

    bx = 1040
    for br in spec.get("brackets", []):
        ya = top + br["from"] * row_h - 10
        yb = top + br["to"] * row_h + 10
        out += line(bx, ya, bx, yb, C["ink500"], 2)
        out += line(bx - 4, ya, bx + 4, ya, C["ink500"], 2)
        out += line(bx - 4, yb, bx + 4, yb, C["ink500"], 2)
        lines = wrap(br["text"], 9.5, 200)
        ty = (ya + yb) / 2 - (len(lines) - 1) * 13 / 2 + 3
        for k, ln in enumerate(lines):
            out += text(bx + 14, ty + k * 13, ln, 9.5, C["ink700"])

    out += text(48, 702, spec.get("source", ""), T["note"], C["ink400"])
    return out + "</svg>"


def render_bar_future_deloitte(spec, tokens):
    C = tokens["colors"]
    W = tokens["canvas"]["width"]
    H = tokens["canvas"]["height"]
    rows = spec["rows"]
    panels = spec["panels"]
    n = len(rows)
    head, hy = report_head(spec, tokens)
    out = _open(tokens) + head
    bounds = [(0.18 * W, 0.48 * W), (0.53 * W, 0.83 * W)]
    label_x = 0.16 * W
    top, bot = hy + 220, H - 260
    row_h = (bot - top) / (n - 1) if n > 1 else 0
    bar_h = min(40, row_h * 0.46)

    out += circle(0.18 * W, top - 80, 6, C["ink900"])
    out += text(0.18 * W + 14, top - 76, spec.get("current_label", "当前值"), 11.5, C["ink700"])
    out += line(0.18 * W + 250, top - 88, 0.18 * W + 250, top - 68, C["ink900"], 2.8)
    out += text(0.18 * W + 260, top - 76, spec.get("future_label", "未来值"), 11.5, C["ink700"])

    for pi, p in enumerate(panels):
        x0, x1 = bounds[pi]
        color = _color(C, p["color"])
        out += text(x0, top - 52, p["title"], 12.5, C["ink900"], "bold")
        v = 0
        while v <= 100 + 1e-9:
            x = x0 + v / 100 * (x1 - x0)
            out += text(x, top - 26, f"{v:g}%", 10, C["ink700"], "normal", "middle")
            out += line(x, top - 14, x, bot + 14, "#D8D8D8", 0.9)
            v += 20
        out += line(x0, top - 14, x0, bot + 14, C["ink900"], 1.2)

        for i in range(n):
            cy = top + i * row_h
            cur = p["current"][i]
            fut = p["future"][i]
            xe = x0 + cur / 100 * (x1 - x0)
            xf = x0 + fut / 100 * (x1 - x0)
            out += rect(x0, cy - bar_h / 2, xe - x0, bar_h, color)
            if xe - x0 >= 34:
                out += text(xe - 8, cy + 4, f"{cur:g}%", 11, "#FFFFFF", "bold", "end")
            else:
                out += text(xe, cy + bar_h / 2 + 14, f"{cur:g}%", 10, color, "bold", "middle")
            out += line(xe, cy, xf, cy, C["ink400"], 0.9)
            out += line(xf, cy - bar_h / 2, xf, cy + bar_h / 2, color, 2.8)
            lw = tw(f"{fut:g}%", 11, True)
            if xf + 8 + lw <= x1:
                out += text(xf + 8, cy + 4, f"{fut:g}%", 11, C["ink900"], "bold")
            else:
                out += text(xf, cy + bar_h / 2 + 14, f"{fut:g}%", 11, C["ink900"], "bold", "middle")

    for i, name in enumerate(rows):
        lines = _row_lines(name, 11.5, label_x - 20)
        cy = top + i * row_h
        y0 = cy - (len(lines) - 1) * 11.5 * 1.2 / 2 + 4
        for k, ln in enumerate(lines):
            out += text(label_x, y0 + k * 11.5 * 1.2, ln, 11.5, C["ink700"], "normal", "end")

    bx = 0.855 * W
    for br in spec.get("brackets", []):
        ya = top + br["from"] * row_h - 12
        yb = top + br["to"] * row_h + 12
        out += line(bx, ya, bx, yb, C["ink500"], 2.2)
        out += line(bx - 5, ya, bx + 5, ya, C["ink500"], 2.2)
        out += line(bx - 5, yb, bx + 5, yb, C["ink500"], 2.2)
        lines = wrap(br["text"], 9.5, W - bx - 24)
        ty = (ya + yb) / 2 - (len(lines) - 1) * 13 / 2 + 4
        for k, ln in enumerate(lines):
            out += text(bx + 14, ty + k * 13, ln, 9.5, C["ink700"])

    if spec.get("notes"):
        out += text(20, H - 110, "Notes: " + spec["notes"], 9.5, C["ink500"])
    if spec.get("source"):
        out += text(20, H - 60, spec["source"], 9.5, C["ink400"])
    return out + "</svg>"


def render_quadrant_matrix(spec, tokens):
    if tokens.get("style") == "matrix":
        return render_quadrant_matrix_ref(spec, tokens)
    C = tokens["colors"]
    T = tokens["type"]
    items = spec["items"]
    groups = spec["groups"]
    quads = spec["quadrants"]
    x0, x1 = 200, 900
    y0, y1 = 170, 588
    xm, ym = (x0 + x1) / 2, (y0 + y1) / 2
    tint = {"green": "#EAF6E3", "teal": "#E4F4F2", "gray": "#F0F0F0", "lime": "#E8F7E5"}

    out = _open(tokens)
    out += head_block(spec, tokens)

    cells = [
        (x0, y0, xm, ym, quads["top_left"], "start", "top"),
        (xm, y0, x1, ym, quads["top_right"], "end", "top"),
        (x0, ym, xm, y1, quads["bottom_left"], "start", "bottom"),
        (xm, ym, x1, y1, quads["bottom_right"], "end", "bottom"),
    ]
    for xa, ya, xb, yb, q, anchor, corner in cells:
        out += rect(xa, ya, xb - xa, yb - ya, tint.get(q.get("tone", "gray"), tint["gray"]))
        tx = xa + 16 if anchor == "start" else xb - 16
        ty = ya + 26 if corner == "top" else yb - 16
        out += text(tx, ty, q["label"], 12.5, C["ink900"], "bold", anchor)

    out += line(xm, y0, xm, y1, "#FFFFFF", 2)
    out += line(x0, ym, x1, ym, "#FFFFFF", 2)
    out += rect(x0, y0, x1 - x0, y1 - y0, "none", C["ink900"], 1)

    def xv(v):
        return x0 + v / 100 * (x1 - x0)

    def yv(v):
        return y1 - v / 100 * (y1 - y0)

    xt = spec.get("x_ticks", ["低", "中", "高"])
    yt = spec.get("y_ticks", ["低", "中", "高"])
    for k, lab in enumerate(xt):
        out += text(xv((k + 0.5) / len(xt) * 100), 614, lab, 11, C["ink700"], "normal", "middle")
    for k, lab in enumerate(yt):
        out += text(184, yv((k + 0.5) / len(yt) * 100) + 4, lab, 11, C["ink700"], "normal", "end")

    arrow(x0, 640, x1, 640, C["ink900"], 1.2, 9)
    arrow(x1, 640, x0, 640, C["ink900"], 1.2, 9)
    out += rect(510, 629, 80, 22, "#FFFFFF")
    out += text(550, 646, spec["x_label"], 11, C["ink900"], "bold", "middle")
    arrow(150, y1, 150, y0, C["ink900"], 1.2, 9)
    arrow(150, y0, 150, y1, C["ink900"], 1.2, 9)
    out += rect(88, 350, 24, 80, "#FFFFFF")
    out += f'<text x="108" y="390" font-size="11" fill="{C["ink900"]}" font-weight="bold" text-anchor="middle" transform="rotate(-90 108 390)">{spec["y_label"]}</text>'

    for it in items:
        cx, cy = xv(it["x"]), yv(it["y"])
        color = _color(C, groups[it["group"]])
        out += circle(cx, cy, 9, color)
        lines = wrap(it["label"], 9.5, 150)
        pos = it.get("pos", "right")
        if pos == "left":
            tx, anchor = cx - 15, "end"
            ty = cy - (len(lines) - 1) * 12 / 2 + 3.5
        elif pos == "above":
            tx, anchor = cx, "middle"
            ty = cy - 16 - (len(lines) - 1) * 12
        elif pos == "below":
            tx, anchor = cx, "middle"
            ty = cy + 22
        else:
            tx, anchor = cx + 15, "start"
            ty = cy - (len(lines) - 1) * 12 / 2 + 3.5
        for k, ln in enumerate(lines):
            out += text(tx, ty + k * 12, ln, 9.5, color, "normal", anchor)

    lx = 470
    for name, color in groups.items():
        out += circle(lx, 684, 7, _color(C, color))
        out += text(lx + 12, 688, name, 10, C["ink700"])
        lx += 12 + tw(name, 10) + 34

    out += text(48, 704, spec.get("source", ""), T["note"], C["ink400"])
    return out + "</svg>"


def render_growth_margin(spec, tokens):
    C = tokens["colors"]
    T = tokens["type"]
    W = tokens["canvas"]["width"]
    H = tokens["canvas"]["height"]
    q = spec["quarters"]
    rev = spec["revenue"]
    segs = spec["segments"]
    gm = spec["gross_margin"]
    om = spec["operating_margin"]
    fcf = spec["free_cash_flow"]
    out = _open(tokens)
    out += head_block(spec, tokens)
    out += text(48, 126, spec["panel_title"], T["panel"], C["ink900"], "bold")
    out += line(48, 136, W - 48, 136, C["ink900"], 1)

    x0, x1 = 95, 690
    top, bot = 235, 610
    ymax = max(rev) * 1.14
    for v in range(0, int(ymax) + 1, 10):
        y = bot - v / ymax * (bot - top)
        out += line(x0, y, x1, y, "#E8E8E8", 0.8)
        out += text(x0 - 10, y + 3, f"{v}", 9, C["ink500"], "normal", "end")
    out += text(48, 250, "十亿美元", 9, C["ink500"])

    out += text(x0, 215, "营收结构(十亿美元)", 11, C["ink900"], "bold")
    lx = x0
    seg_colors = {"汽车": C["primary"], "能源": C["pos"], "服务": C["second"]}
    for name in segs:
        out += rect(lx, 182, 12, 12, seg_colors.get(name, C["primary"]))
        out += text(lx + 18, 192, name, 10.5, C["ink700"])
        lx += 18 + tw(name, 10.5) + 24

    colw = (x1 - x0) / len(q)
    bw = min(66, colw * 0.58)
    for i, qq in enumerate(q):
        cx = x0 + colw * (i + 0.5)
        y = bot
        for name in segs:
            v = segs[name][i]
            h = v / ymax * (bot - top)
            y -= h
            color = seg_colors.get(name, C["primary"])
            out += rect(cx - bw / 2, y, bw, h, color)
            if h >= 20:
                fg = C["ink900"] if color in (C["second"], C["light"]) else "#FFFFFF"
                out += text(cx, y + h / 2 + 4, f"{v:.1f}", 9.5, fg, "bold", "middle")
        out += text(cx, y - 9, f"{rev[i]:.1f}", 10.5, C["ink900"], "bold", "middle")
        out += text(cx, bot + 24, qq, 9.5, C["ink700"], "normal", "middle")

    xa, xb = 760, W - 45
    mtop, mbot = 235, 430
    out += text(xa, 215, "毛利率与营业利润率(%)", 11, C["ink900"], "bold")
    out += line(xa + 150, 185, xa + 165, 185, C["primary"], 2.5)
    out += text(xa + 172, 189, "毛利率", 9.5, C["ink700"])
    out += line(xa + 235, 185, xa + 250, 185, C["neg"], 2.5)
    out += text(xa + 257, 189, "营业利润率", 9.5, C["ink700"])
    for v in range(0, 26, 5):
        y = mbot - v / 25 * (mbot - mtop)
        out += line(xa, y, xb, y, "#E8E8E8", 0.8)
        out += text(xa - 8, y + 3, f"{v}", 9, C["ink500"], "normal", "end")
    for name, vals, color, dy in (("gross", gm, C["primary"], -8), ("op", om, C["neg"], 15)):
        pts = []
        for i, v in enumerate(vals):
            px = xa + (xb - xa) * (i + 0.5) / len(q)
            py = mbot - v / 25 * (mbot - mtop)
            pts.append((px, py))
        out += path("M" + " L".join(f"{p[0]:.1f} {p[1]:.1f}" for p in pts), "none", color, 2)
        for i, (px, py) in enumerate(pts):
            out += circle(px, py, 4, color, "#FFFFFF", 1)
            out += text(px, py + dy, f"{vals[i]:.1f}", 9, color, "bold", "middle")

    ftop, fbot = 495, 600
    out += text(xa, 475, "自由现金流(十亿美元)", 11, C["ink900"], "bold")
    fmin, fmax = -2, 5
    zero = fbot - (0 - fmin) / (fmax - fmin) * (fbot - ftop)
    out += line(xa, zero, xb, zero, C["ink400"], 1)
    out += text(xa - 8, zero + 3, "0", 9, C["ink500"], "normal", "end")
    fw = min(54, (xb - xa) / len(q) * 0.5)
    for i, v in enumerate(fcf):
        cx = xa + (xb - xa) * (i + 0.5) / len(q)
        h = abs(v) / (fmax - fmin) * (fbot - ftop)
        color = C["pos"] if v >= 0 else C["neg"]
        if v >= 0:
            out += rect(cx - fw / 2, zero - h, fw, h, color)
            out += text(cx, zero - h - 6, f"{v:.1f}", 9, C["ink900"], "bold", "middle")
        else:
            out += rect(cx - fw / 2, zero, fw, h, color)
            out += text(cx, zero + h + 12, f"{v:.1f}", 9, C["ink900"], "bold", "middle")
        out += text(cx, fbot + 18, q[i], 9, C["ink700"], "normal", "middle")

    callout = spec.get("callout", "")
    if callout:
        out += rect(48, 650, W - 96, 58, "#FFFFFF", C["ink400"], 1, 4)
        out += text(62, 672, "最新经营信号", 10, C["ink900"], "bold")
        for k, ln in enumerate(wrap(callout, 11, W - 160)):
            out += text(150, 671 + k * 16, ln, 11, C["ink700"])

    if spec.get("source"):
        out += text(48, 790, spec["source"], T["note"], C["ink400"])
    out += text(48, 810, "Q3 2026 财报尚未披露;交付为 2026-10-02 公告数据。", 8.5, C["ink400"])
    return out + "</svg>"


def render_ai_market(spec, tokens):
    C = tokens["colors"]
    T = tokens["type"]
    W = tokens["canvas"]["width"]
    H = tokens["canvas"]["height"]
    quarters = spec["quarters"]
    providers = spec["providers"]
    out = _open(tokens)
    out += head_block(spec, tokens)
    out += text(48, 126, spec["panel_title"], T["panel"], C["ink900"], "bold")
    out += line(48, 136, W - 48, 136, C["ink900"], 1)

    stats = [
        ("Anthropic", "42% → 5%", "#C15F3C"),
        ("DeepSeek", "7% → 24%", "#5B5BD6"),
        ("中国开源合计", "11% → 46%", "#2A9D8F"),
        ("亚洲调用占比", "13% → 58%", "#1B3FD8"),
    ]
    for i, (label, val, color) in enumerate(stats):
        bx = 48 + i * (W - 96 + 12) / 4
        bw = (W - 96 - 36) / 4
        out += rect(bx, 155, bw, 52, "#F7F7F7")
        out += rect(bx, 155, 4, 52, color)
        out += text(bx + 16, 177, val, 18, C["ink900"], "bold")
        out += text(bx + 16, 195, label, 9.5, C["ink500"])

    x0, x1 = 90, W - 50
    top, bot = 285, 555
    out += text(48, 235, "Provider token 份额(%)", 11, C["ink900"], "bold")
    lx = 90
    for p in providers:
        out += rect(lx, 253, 11, 11, p["color"])
        out += text(lx + 15, 262, p["name"], 9.5, C["ink700"])
        lx += 15 + tw(p["name"], 9.5) + 24
    for v in range(0, 101, 25):
        y = bot - v / 100 * (bot - top)
        out += line(x0, y, x1, y, "#E8E8E8", 0.8)
        out += text(x0 - 8, y + 3, f"{v}", 9, C["ink500"], "normal", "end")
    out += text(x0 - 46, top - 12, "份额(%)", 9, C["ink500"])
    colw = (x1 - x0) / len(quarters)
    bw = min(100, colw * 0.58)
    for i, qq in enumerate(quarters):
        cx = x0 + colw * (i + 0.5)
        y = bot
        for p in providers:
            v = p["values"][i]
            h = v / 100 * (bot - top)
            y -= h
            out += rect(cx - bw / 2, y, bw, h, p["color"])
            if h >= 12:
                fg = C["ink900"] if p["color"] in ("#D9D9D9",) else "#FFFFFF"
                out += text(cx, y + h / 2 + 3, f"{v:g}", 8.2, fg, "bold", "middle")
        out += text(cx, bot + 22, qq, 9.5, C["ink700"], "normal", "middle")

    # price vs volume
    bx0, bx1 = 90, 620
    btop, bbot = 650, 850
    out += text(48, 615, "2026 Q3:价格带与调用量", 11, C["ink900"], "bold")
    tiers = spec.get("price_tiers", [])
    bounds = [0.05, 1, 5, 25]
    tints = ["#F7F7F7", "#F0F0F0", "#E8E8E8"]
    for i in range(3):
        xa = bx0 + (math.log10(bounds[i]) - math.log10(0.05)) / (math.log10(25) - math.log10(0.05)) * (bx1 - bx0)
        xb = bx0 + (math.log10(bounds[i + 1]) - math.log10(0.05)) / (math.log10(25) - math.log10(0.05)) * (bx1 - bx0)
        out += rect(xa, btop, xb - xa, bbot - btop, tints[i])
        if i < len(tiers):
            out += text((xa + xb) / 2, btop + 14, tiers[i]["label"], 9, C["ink500"], "normal", "middle")

    def px(v):
        return bx0 + (math.log10(v) - math.log10(0.05)) / (math.log10(25) - math.log10(0.05)) * (bx1 - bx0)

    for v in range(0, 31, 10):
        y = bbot - v / 30 * (bbot - btop)
        out += line(bx0, y, bx1, y, "#D8D8D8", 0.6)
        out += text(bx0 - 8, y + 3, f"{v}", 9, C["ink500"], "normal", "end")
    out += text(bx0 - 44, btop - 12, "份额(%)", 9, C["ink500"])
    for pv in (0.1, 1, 10):
        out += text(px(pv), bbot + 20, f"{pv:g}", 8.5, C["ink500"], "normal", "middle")
    out += text(bx1 - 4, btop - 12, "气泡=份额", 8.5, C["ink400"], "normal", "end")
    for it in sorted(spec["price_items"], key=lambda x: -x["share"]):
        cx, cy = px(max(it["price"], 0.05)), bbot - it["share"] / 30 * (bbot - btop)
        r = 6 + math.sqrt(it["share"]) * 4
        out += circle(cx, cy, r, it["color"], "#FFFFFF", 2)
        pos = it.get("pos", "right")
        if pos == "left":
            out += text(cx - r - 5, cy + 3, it["name"], 9.5, it["color"], "bold", "end")
        elif pos == "above":
            out += text(cx, cy - r - 6, it["name"], 9.5, it["color"], "bold", "middle")
        elif pos == "below":
            out += text(cx, cy + r + 12, it["name"], 9.5, it["color"], "bold", "middle")
        else:
            out += text(cx + r + 5, cy + 3, it["name"], 9.5, it["color"], "bold")
    out += text(bx0, bbot + 36, "blended 价格(美元/百万 token,对数轴)", 9, C["ink500"])

    # region mix
    cx0, cx1 = 740, W - 50
    ctop, cbot = 675, 850
    out += text(700, 615, "OpenRouter 调用量的地区构成(%)", 11, C["ink900"], "bold")
    lx = 740
    for s in spec["regions"]["series"]:
        out += rect(lx, 636, 10, 10, s["color"])
        out += text(lx + 14, 645, s["name"], 9.5, C["ink700"])
        lx += 14 + tw(s["name"], 9.5) + 18
    periods = spec["regions"]["periods"]
    n = len(periods)
    colw = (cx1 - cx0) / n
    bw = min(90, colw * 0.48)
    for i, period in enumerate(periods):
        cx = cx0 + colw * (i + 0.5)
        y = cbot
        for s in spec["regions"]["series"]:
            v = s["values"][i]
            h = v / 100 * (cbot - ctop)
            y -= h
            out += rect(cx - bw / 2, y, bw, h, s["color"])
            if h >= 12:
                fg = C["ink900"] if s["color"] in ("#D9D9D9", "#7FA6F2") else "#FFFFFF"
                out += text(cx, y + h / 2 + 3, f"{v:g}", 8.2, fg, "bold", "middle")
        out += text(cx, cbot + 18, period, 9.5, C["ink700"], "normal", "middle")
    for v in (0, 50, 100):
        y = cbot - v / 100 * (cbot - ctop)
        out += line(cx0, y, cx1, y, "#E8E8E8", 0.8)
        out += text(cx0 - 8, y + 3, f"{v}", 9, C["ink500"], "normal", "end")

    if spec.get("notes"):
        yy = 910
        for ln in wrap(spec["notes"], 9, W - 96):
            out += text(48, yy, ln, 9, C["ink500"])
            yy += 12
    if spec.get("source"):
        out += text(48, H - 18, spec["source"], 8.5, C["ink400"])
    return out + "</svg>"
