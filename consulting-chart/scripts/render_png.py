import os
import re
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

BROWSER_CANDIDATES = (
    "msedge",
    "microsoft-edge",
    "microsoft-edge-stable",
    "google-chrome",
    "google-chrome-stable",
    "chromium",
    "chromium-browser",
    "chrome",
)

PLATFORM_FALLBACKS = {
    "win32": (
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    ),
    "darwin": (
        "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Chromium.app/Contents/MacOS/Chromium",
    ),
}


def find_browser():
    """Locate a headless-capable Chromium/Edge executable across platforms."""
    env_override = os.environ.get("CONSULTING_CHART_BROWSER")
    if env_override:
        p = Path(env_override)
        if p.is_file():
            return str(p)
        raise FileNotFoundError(
            f"CONSULTING_CHART_BROWSER 指定的浏览器不存在: {env_override}"
        )

    for name in BROWSER_CANDIDATES:
        found = shutil.which(name)
        if found:
            return found

    for fallback in PLATFORM_FALLBACKS.get(sys.platform, ()):
        if Path(fallback).is_file():
            return fallback

    raise FileNotFoundError(
        "未找到可用的无头浏览器 (Edge / Chrome / Chromium)。"
        "请安装任一 Chromium 系浏览器,或通过环境变量 CONSULTING_CHART_BROWSER 指定可执行文件路径。"
    )


def _parse_dim(raw):
    if raw is None:
        return None
    m = re.match(r"\s*([0-9]+(?:\.[0-9]+)?)", str(raw))
    return int(round(float(m.group(1)))) if m else None


def svg_dimensions(svg_path):
    """Read width and height from an SVG file, falling back to viewBox."""
    root = ET.parse(svg_path).getroot()
    w = _parse_dim(root.get("width"))
    h = _parse_dim(root.get("height"))
    if w and h:
        return w, h
    vb = root.get("viewBox") or root.get("viewbox")
    if vb:
        parts = re.split(r"[\s,]+", vb.strip())
        if len(parts) == 4:
            vw, vh = _parse_dim(parts[2]), _parse_dim(parts[3])
            if vw and vh:
                return vw, vh
    return 1280, 720


def render(svg_path, browser=None):
    """Render an SVG file to a same-stem PNG using headless Chromium/Edge."""
    svg = Path(svg_path).resolve()
    if not svg.is_file():
        raise FileNotFoundError(f"SVG 文件不存在: {svg}")
    png = svg.with_suffix(".png")
    w, h = svg_dimensions(svg)
    exe = browser or find_browser()
    url = svg.as_uri()
    cmd = [
        exe,
        "--headless=new",
        "--disable-gpu",
        "--no-first-run",
        "--no-default-browser-check",
        "--hide-scrollbars",
        f"--window-size={w},{h}",
        f"--screenshot={png}",
        url,
    ]
    subprocess.run(cmd, check=True)
    return str(png)


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if len(sys.argv) < 2:
        print("用法: python scripts/render_png.py <chart.svg> [more.svg ...]", file=sys.stderr)
        sys.exit(2)
    for path in sys.argv[1:]:
        print(render(path))
