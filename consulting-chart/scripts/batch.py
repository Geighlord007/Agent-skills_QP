import html
import subprocess
import sys
from pathlib import Path

from render_png import find_browser, render as render_svg_to_png

ROOT = Path(__file__).resolve().parent.parent
EXAMPLES = ROOT / "examples"


def run_case(case, browser=None):
    rel = str(Path("examples") / case)
    r = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "pipeline.py"), "--case", rel],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if r.returncode != 0:
        return "failed", (r.stdout or "")[-400:] + (r.stderr or "")[-400:]

    svg = EXAMPLES / case / "out" / "chart.svg"
    if not svg.is_file():
        return "failed", f"未生成 SVG: {svg}"

    if browser:
        try:
            png = Path(render_svg_to_png(svg, browser=browser))
            if png.is_file():
                return "png", ""
        except subprocess.CalledProcessError as exc:
            return "svg", f"PNG 导出失败(已保留 SVG): {exc}"
    return "svg", ""


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    try:
        browser = find_browser()
    except FileNotFoundError as exc:
        browser = None
        print(f"[warn] {exc} 将仅输出 SVG。")

    cases = sorted(
        d.name
        for d in EXAMPLES.iterdir()
        if d.is_dir() and (d / "brief.json").is_file()
    )
    results = []
    for case in cases:
        if case.endswith("-gate"):
            results.append((case, "skipped", ""))
            print("SKIP", case)
            continue
        status, detail = run_case(case, browser=browser)
        results.append((case, status, detail))
        print(("OK   " if status in ("png", "svg") else "FAIL ") + case)
        if detail:
            print(detail)

    out_dir = EXAMPLES / "_batch"
    out_dir.mkdir(parents=True, exist_ok=True)
    cards = []
    for case, status, _ in results:
        if status not in ("png", "svg"):
            continue
        ext = "png" if status == "png" else "svg"
        img = f"../{case}/out/chart.{ext}"
        cards.append(
            f'<section><h2>{html.escape(case)}</h2>'
            f'<img src="{img}" alt="{html.escape(case)}"></section>'
        )
    page = (
        '<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><title>批量图表</title>'
        "<style>body{background:#F7F7F8;font-family:Arial,'Microsoft YaHei',sans-serif;margin:24px}"
        "section{background:#fff;border:1px solid #E3E3E6;border-radius:6px;padding:12px;margin:18px 0}"
        "h2{font-size:15px;margin:0 0 8px}img{width:100%;display:block}</style></head><body>"
        f"<h1>批量图表({len(cards)} 张)</h1>" + "".join(cards) + "</body></html>"
    )
    contact_path = out_dir / "contact.html"
    contact_path.write_text(page, encoding="utf-8")

    print(f"\n批量完成: {len(cards)} 张; 联系表: {contact_path}")
    print("输出清单:")
    for case, status, _ in results:
        if status in ("png", "svg"):
            ext = "png" if status == "png" else "svg"
            print(EXAMPLES / case / "out" / f"chart.{ext}")


if __name__ == "__main__":
    main()
