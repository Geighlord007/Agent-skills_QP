import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MPL = os.path.join(ROOT, "vendor", "EconomistStyle", "src", "economiststyle", "styles", "theeconomist.mplstyle")
OUT = os.path.join(ROOT, "references", "skins", "economist.json")


def parse_style(path):
    props = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or ":" not in line:
                continue
            k, v = line.split(":", 1)
            props[k.strip()] = v.strip()
    return props


def blend_white(hex_color, ratio):
    r = int(hex_color[1:3], 16)
    g = int(hex_color[3:5], 16)
    b = int(hex_color[5:7], 16)
    r = int(r + (255 - r) * ratio)
    g = int(g + (255 - g) * ratio)
    b = int(b + (255 - b) * ratio)
    return "#%02X%02X%02X" % (r, g, b)


def main():
    props = parse_style(MPL)
    colors = re.findall(r"'([0-9A-Fa-f]{6})'", props.get("axes.prop_cycle", ""))
    if len(colors) < 7:
        raise RuntimeError("prop_cycle 颜色不足: " + str(colors))
    font_stack = props.get("font.sans-serif", "Arial")
    font = font_stack + ", 'Microsoft YaHei', sans-serif"

    primary = "#" + colors[4]
    accent = "#" + colors[0]
    second = "#" + colors[2]
    light = "#" + colors[6]
    neg = "#" + colors[1]
    ink700 = "#" + props.get("axes.labelcolor", "525254").lstrip("#")

    skin = {
        "version": 1,
        "name": "economist",
        "font": font,
        "font_title": font,
        "kicker_color": neg,
        "canvas": {"width": 1280, "height": 720},
        "colors": {
            "ink900": "#121212",
            "ink700": ink700,
            "ink500": "#6B6B6B",
            "ink400": "#8F8F8F",
            "hair": "#D8D8D8",
            "base": "#111111",
            "primary": primary,
            "accent": accent,
            "second": second,
            "light": light,
            "step": "#BFBFBF",
            "pos": accent,
            "neg": neg,
            "band": blend_white(accent, 0.82),
            "black": "#0A0A0A"
        },
        "type": {"title": 28, "panel": 13, "value": 11, "label": 10.5, "note": 8.5},
        "lines": {"hair": 1, "base": 1.6, "dotted": "2 3"},
        "category_colors": {
            "Accounting": "black",
            "Customer Service": "primary",
            "Procurement": "second",
            "Sales Support": "light"
        },
        "generated_by": "scripts/import_economist_skin.py",
        "source": "vendor/EconomistStyle/src/economiststyle/styles/theeconomist.mplstyle"
    }

    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(skin, f, ensure_ascii=False, indent=2)
    print("primary", primary, "accent", accent, "second", second, "light", light, "neg", neg)


if __name__ == "__main__":
    main()
