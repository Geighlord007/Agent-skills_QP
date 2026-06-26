#!/usr/bin/env python3
"""Generate simple SVG charts from JSON data."""

import argparse
import json
import math
from pathlib import Path


SVG_WIDTH = 800
SVG_HEIGHT = 500
MARGIN = {"top": 60, "right": 40, "bottom": 80, "left": 80}
PLOT_WIDTH = SVG_WIDTH - MARGIN["left"] - MARGIN["right"]
PLOT_HEIGHT = SVG_HEIGHT - MARGIN["top"] - MARGIN["bottom"]

COLORS = ["#003366", "#0D7377", "#D4A843", "#6B7B8D", "#C75B3F", "#7BA05B"]


def escape(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def scale_linear(values, out_min, out_max):
    vmin, vmax = min(values), max(values)
    if vmax == vmin:
        return [out_min + (out_max - out_min) / 2 for _ in values]
    return [out_min + (v - vmin) / (vmax - vmin) * (out_max - out_min) for v in values]


def wrap_text(text, max_chars=20):
    words = text.split()
    lines = []
    current = ""
    for w in words:
        if len(current) + len(w) + 1 <= max_chars:
            current = f"{current} {w}".strip()
        else:
            if current:
                lines.append(current)
            current = w
    if current:
        lines.append(current)
    return lines if lines else [text]


def svg_header(title: str) -> str:
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{SVG_WIDTH}" height="{SVG_HEIGHT}" viewBox="0 0 {SVG_WIDTH} {SVG_HEIGHT}">
  <rect width="100%" height="100%" fill="#ffffff"/>
  <text x="{SVG_WIDTH/2}" y="30" text-anchor="middle" font-family="Arial, sans-serif" font-size="18" font-weight="bold" fill="#333333">{escape(title)}</text>
'''


def svg_footer(source: str) -> str:
    s = f"Source: {source}" if source else ""
    return (
        f'  <text x="{SVG_WIDTH - 20}" y="{SVG_HEIGHT - 15}" text-anchor="end" '
        f'font-family="Arial, sans-serif" font-size="10" fill="#999999">{escape(s)}</text>\n'
        '</svg>'
    )


def draw_axes(svg: list, x_label: str = "", y_label: str = ""):
    svg.append(f'  <line x1="{MARGIN["left"]}" y1="{MARGIN["top"] + PLOT_HEIGHT}" x2="{MARGIN["left"] + PLOT_WIDTH}" y2="{MARGIN["top"] + PLOT_HEIGHT}" stroke="#333333" stroke-width="2"/>')
    svg.append(f'  <line x1="{MARGIN["left"]}" y1="{MARGIN["top"]}" x2="{MARGIN["left"]}" y2="{MARGIN["top"] + PLOT_HEIGHT}" stroke="#333333" stroke-width="2"/>')
    if x_label:
        svg.append(f'  <text x="{MARGIN["left"] + PLOT_WIDTH/2}" y="{SVG_HEIGHT - 35}" text-anchor="middle" font-family="Arial, sans-serif" font-size="12" fill="#333333">{escape(x_label)}</text>')
    if y_label:
        svg.append(f'  <text x="20" y="{MARGIN["top"] + PLOT_HEIGHT/2}" text-anchor="middle" transform="rotate(-90 20 {MARGIN["top"] + PLOT_HEIGHT/2})" font-family="Arial, sans-serif" font-size="12" fill="#333333">{escape(y_label)}</text>')


def chart_bar(data: dict, title: str, source: str) -> str:
    categories = data.get("categories", [])
    values = data.get("values", [])
    y_label = data.get("y_label", "")

    svg = [svg_header(title)]
    draw_axes(svg, x_label="", y_label=y_label)

    n = len(categories)
    bar_width = PLOT_WIDTH / (n * 1.5)
    y_positions = scale_linear(values, MARGIN["top"] + PLOT_HEIGHT, MARGIN["top"])

    for i, (cat, val, y) in enumerate(zip(categories, values, y_positions)):
        x = MARGIN["left"] + (i + 0.25) * (PLOT_WIDTH / n)
        height = MARGIN["top"] + PLOT_HEIGHT - y
        color = COLORS[i % len(COLORS)]
        svg.append(f'  <rect x="{x}" y="{y}" width="{bar_width}" height="{height}" fill="{color}"/>')
        svg.append(f'  <text x="{x + bar_width/2}" y="{y - 5}" text-anchor="middle" font-family="Arial, sans-serif" font-size="11" fill="#333333">{escape(str(val))}</text>')
        lines = wrap_text(str(cat), 12)
        for li, line in enumerate(lines):
            svg.append(f'  <text x="{x + bar_width/2}" y="{MARGIN["top"] + PLOT_HEIGHT + 18 + li*14}" text-anchor="middle" font-family="Arial, sans-serif" font-size="10" fill="#333333">{escape(line)}</text>')

    svg.append(svg_footer(source))
    return "\n".join(svg)


def chart_grouped_bar(data: dict, title: str, source: str) -> str:
    groups = data.get("groups", [])
    series = data.get("series", {})
    y_label = data.get("y_label", "")

    svg = [svg_header(title)]
    draw_axes(svg, x_label="", y_label=y_label)

    n_groups = len(groups)
    n_series = len(series)
    group_width = PLOT_WIDTH / (n_groups * 1.5)
    bar_width = group_width / (n_series + 0.5)

    all_values = [v for vals in series.values() for v in vals]
    y_positions_map = {}
    for s_name, vals in series.items():
        y_positions_map[s_name] = scale_linear(vals, MARGIN["top"] + PLOT_HEIGHT, MARGIN["top"])

    series_names = list(series.keys())
    for i, group in enumerate(groups):
        x_base = MARGIN["left"] + i * (PLOT_WIDTH / n_groups) + group_width * 0.25
        for j, s_name in enumerate(series_names):
            val = series[s_name][i]
            y = y_positions_map[s_name][i]
            height = MARGIN["top"] + PLOT_HEIGHT - y
            x = x_base + j * bar_width
            color = COLORS[j % len(COLORS)]
            svg.append(f'  <rect x="{x}" y="{y}" width="{bar_width*0.9}" height="{height}" fill="{color}"/>')
            svg.append(f'  <text x="{x + bar_width*0.45}" y="{y - 5}" text-anchor="middle" font-family="Arial, sans-serif" font-size="9" fill="#333333">{escape(str(val))}</text>')
        lines = wrap_text(str(group), 12)
        for li, line in enumerate(lines):
            svg.append(f'  <text x="{x_base + group_width/2 - bar_width/2}" y="{MARGIN["top"] + PLOT_HEIGHT + 18 + li*14}" text-anchor="middle" font-family="Arial, sans-serif" font-size="10" fill="#333333">{escape(line)}</text>')

    # Legend
    legend_x = MARGIN["left"] + PLOT_WIDTH - 140
    legend_y = MARGIN["top"] + 10
    for j, s_name in enumerate(series_names):
        color = COLORS[j % len(COLORS)]
        svg.append(f'  <rect x="{legend_x}" y="{legend_y + j*20}" width="12" height="12" fill="{color}"/>')
        svg.append(f'  <text x="{legend_x + 18}" y="{legend_y + j*20 + 10}" font-family="Arial, sans-serif" font-size="10" fill="#333333">{escape(s_name)}</text>')

    svg.append(svg_footer(source))
    return "\n".join(svg)


def chart_line(data: dict, title: str, source: str) -> str:
    x = data.get("x", [])
    y_series = data.get("series", {})
    y_label = data.get("y_label", "")

    svg = [svg_header(title)]
    draw_axes(svg, x_label="", y_label=y_label)

    all_y = [v for vals in y_series.values() for v in vals]
    y_min, y_max = min(all_y), max(all_y)
    if y_max == y_min:
        y_max += 1

    x_positions = scale_linear(list(range(len(x))), MARGIN["left"], MARGIN["left"] + PLOT_WIDTH)

    for j, (s_name, vals) in enumerate(y_series.items()):
        points = []
        for i, val in enumerate(vals):
            px = x_positions[i]
            py = MARGIN["top"] + PLOT_HEIGHT - (val - y_min) / (y_max - y_min) * PLOT_HEIGHT
            points.append((px, py))
        color = COLORS[j % len(COLORS)]
        path_d = "M " + " L ".join(f"{px},{py}" for px, py in points)
        svg.append(f'  <path d="{path_d}" fill="none" stroke="{color}" stroke-width="2"/>')
        for px, py in points:
            svg.append(f'  <circle cx="{px}" cy="{py}" r="4" fill="{color}"/>')

    # X labels
    for i, label in enumerate(x):
        px = x_positions[i]
        svg.append(f'  <text x="{px}" y="{MARGIN["top"] + PLOT_HEIGHT + 20}" text-anchor="middle" font-family="Arial, sans-serif" font-size="10" fill="#333333">{escape(str(label))}</text>')

    # Legend
    legend_x = MARGIN["left"] + PLOT_WIDTH - 140
    legend_y = MARGIN["top"] + 10
    for j, s_name in enumerate(y_series.keys()):
        color = COLORS[j % len(COLORS)]
        svg.append(f'  <rect x="{legend_x}" y="{legend_y + j*20}" width="12" height="12" fill="{color}"/>')
        svg.append(f'  <text x="{legend_x + 18}" y="{legend_y + j*20 + 10}" font-family="Arial, sans-serif" font-size="10" fill="#333333">{escape(s_name)}</text>')

    svg.append(svg_footer(source))
    return "\n".join(svg)


def chart_timeline(data: dict, title: str, source: str) -> str:
    events = sorted(data.get("events", []), key=lambda e: e.get("year", 0))

    svg = [svg_header(title)]
    draw_axes(svg, x_label="Year", y_label="")

    if not events:
        svg.append(svg_footer(source))
        return "\n".join(svg)

    years = [e["year"] for e in events]
    y_min, y_max = min(years), max(years)
    if y_max == y_min:
        y_max += 1

    # Timeline axis
    svg.append(f'  <line x1="{MARGIN["left"]}" y1="{MARGIN["top"] + PLOT_HEIGHT/2}" x2="{MARGIN["left"] + PLOT_WIDTH}" y2="{MARGIN["top"] + PLOT_HEIGHT/2}" stroke="#333333" stroke-width="2"/>')

    x_positions = scale_linear(years, MARGIN["left"], MARGIN["left"] + PLOT_WIDTH)

    for i, (event, px) in enumerate(zip(events, x_positions)):
        label = event.get("label", "")
        color = COLORS[i % len(COLORS)]
        is_top = i % 2 == 0
        y1 = MARGIN["top"] + PLOT_HEIGHT / 2
        y2 = MARGIN["top"] + 40 if is_top else MARGIN["top"] + PLOT_HEIGHT - 40
        svg.append(f'  <circle cx="{px}" cy="{y1}" r="6" fill="{color}"/>')
        svg.append(f'  <line x1="{px}" y1="{y1}" x2="{px}" y2="{y2}" stroke="{color}" stroke-width="2"/>')
        lines = wrap_text(label, 20)
        anchor = "middle"
        for li, line in enumerate(lines):
            svg.append(f'  <text x="{px}" y="{y2 + (li*14 if not is_top else -10 - li*14)}" text-anchor="{anchor}" font-family="Arial, sans-serif" font-size="10" fill="#333333">{escape(line)}</text>')
        svg.append(f'  <text x="{px}" y="{y1 + 20}" text-anchor="middle" font-family="Arial, sans-serif" font-size="10" fill="#666666">{event["year"]}</text>')

    svg.append(svg_footer(source))
    return "\n".join(svg)


CHART_FUNCS = {
    "bar": chart_bar,
    "grouped_bar": chart_grouped_bar,
    "line": chart_line,
    "timeline": chart_timeline,
}


def main():
    parser = argparse.ArgumentParser(description="Generate SVG charts")
    parser.add_argument("--type", required=True, choices=list(CHART_FUNCS.keys()))
    parser.add_argument("--data", required=True, help="JSON chart data")
    parser.add_argument("--title", default="Chart", help="Chart title")
    parser.add_argument("--source", default="", help="Source label")
    parser.add_argument("--output", required=True, type=Path, help="Output SVG path")
    args = parser.parse_args()

    data = json.loads(args.data)
    svg = CHART_FUNCS[args.type](data, args.title, args.source)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(svg, encoding="utf-8")
    print(f"Chart written to {args.output}")


if __name__ == "__main__":
    main()
