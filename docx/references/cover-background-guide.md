# Cover & Page Background Guide (Playwright + SVG)

Generate bespoke A4 cover, back-cover, and subtle body backgrounds as crisp 2x PNGs (`1588×2246` px from a `794×1123` CSS viewport) using inline SVG rendered via headless Chromium (`playwright`).

> **Design rule:** Never reuse a canned background verbatim. Pick a style family below, adapt the palette to your document's 3-tier low-saturation scheme (Primary / Dark / Light), and keep the center text zone clean so cover typography has strong contrast and feels like its own visual space.

---

## 1. Standard Render Harness (Cross-Platform Python)

```python
from pathlib import Path
from playwright.sync_api import sync_playwright

PAGE_W, PAGE_H = 794, 1123  # A4 at 96 DPI; device_scale_factor=2 -> 1588x2246 px

GRAIN_FILTER = (
    '<filter id="grain">'
    '<feTurbulence type="fractalNoise" baseFrequency="0.55" numOctaves="3" stitchTiles="stitch" result="n"/>'
    '<feColorMatrix type="saturate" values="0" in="n" result="m"/>'
    '<feBlend in="SourceGraphic" in2="m" mode="multiply"/>'
    '</filter>'
)

def wrap_svg(bg_hex: str, body_svg: str, defs: str = "", grain_opacity: float = 0.04) -> str:
    return (
        f'<!DOCTYPE html><html><head><meta charset="utf-8">'
        f'<style>*{{margin:0;padding:0}}body{{width:{PAGE_W}px;height:{PAGE_H}px;background:{bg_hex}}}</style>'
        f'</head><body>'
        f'<svg width="{PAGE_W}" height="{PAGE_H}" xmlns="http://www.w3.org/2000/svg">'
        f'<defs>{GRAIN_FILTER}{defs}</defs>'
        f'<rect width="100%" height="100%" fill="{bg_hex}"/>'
        f'{body_svg}'
        f'<rect width="100%" height="100%" filter="url(#grain)" opacity="{grain_opacity}"/>'
        f'</svg></body></html>'
    )

def render_backgrounds(templates: dict[str, str], out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": PAGE_W, "height": PAGE_H}, device_scale_factor=2)
        for filename, html in templates.items():
            page.set_content(html)
            page.screenshot(path=str(out_dir / filename), type="png")
        browser.close()
```

---

## 2. Six Visual Archetypes & SVG Techniques

| Archetype | Best For | Palette Example | Core SVG Technique |
|-----------|----------|-----------------|--------------------|
| **Morandi Curves** | Consulting, ESG, healthcare, calm reports | Warm paper `#f5f2ed` + sage `#7C9885` / slate `#8B9DC3` / sand `#B4A992` | Layered cubic Bézier `<path d="M... C... S...">` ribbons (`opacity` 0.04–0.18) + soft rotated `<ellipse>` blobs in upper-right and lower-right corners. |
| **Formal Double Frame** | Legal, institutional, academic, government | Ivory `#faf9f5` + navy `#1e2a4a` + muted gold `#b8975a` | Outer (`stroke-width="2"`) + inner (`stroke-width="0.5"`, inset `7px`) `<rect>` border with gold L-bracket `<path>` corners and small `<polygon>` diamonds. |
| **Ink Wash (水墨)** | Cultural, humanities, CJK monographs | Rice paper `#f7f5f0` + ink `#3a3a3a` + wash `#8a8a7a` + seal red `#B83A2A` | `<feTurbulence baseFrequency="0.01–0.025">` piped into `<feDisplacementMap scale="22–45">` on translucent `<ellipse>` and quadratic `<path>` strokes, plus a tiny vermilion seal `<rect>`. |
| **Swiss Grid** | Technical specs, engineering, finance | Off-white `#fafaf8` + hairlines `#c0c0bc` + charcoal `#1a1a1a` + 1 accent `#c8372d` | Staggered partial grid `<line>` elements (`stroke-width` 0.3–1.0) in upper-right, crosshair registration `<circle>` + `<line>`, and a single crisp accent rule on the left. |
| **Geometric Arcs** | Modern corporate, SaaS, strategy decks | Cool tint `#f7f8fa` + navy `#1a3550` + teal `#0a6b6e` + copper `#a0714a` | Concentric SVG arc commands (`M x1 y1 A r r 0 largeArc 1 x2 y2`) with contrasting thick translucent (`stroke-width="38"`, `opacity="0.07"`) and thin crisp (`1.5px`) strokes anchored to opposite corners. |
| **Warm Gradient Ribbons** | Annual reports, lifestyle, executive summaries | Warm white `#faf8f5` + earth `#8b6f4e` + mist `#5a7a8a` + gold `#a08050` | `<linearGradient>` fills (`stop-opacity` 0.06–0.28) inside gentle wave-edged top/bottom `<path>` bands plus a full-page vertical wash. |

---

## 3. Cover / Body / Back-Cover Composition Rules

- **Safe text zone:** Keep `x ∈ [90, 704]`, `y ∈ [260, 820]` free of high-contrast shapes so titles, subtitles, and metadata remain effortlessly readable.
- **Opacity discipline:** Decorative fills should stay between `0.03` and `0.15`; thin accent rules can go up to `0.35–0.55`.
- **Cohesive 3-page set:**
  - `cover_bg.png`: Strongest visual anchor (top/bottom or diagonal corner framing).
  - `body_bg.png`: Whisper-quiet echo (hairline top/bottom rules or tiny corner tint at `opacity ≤ 0.04`).
  - `backcover_bg.png`: Mirrored or simplified echo of the cover with a subtle centered divider.
- **Cleanup:** Generate background PNGs into a temporary directory (e.g., `tempfile.gettempdir()`), embed them into the `.docx`, and do not leave stray PNGs in the final output folder.
