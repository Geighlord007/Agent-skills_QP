import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REG = os.path.join(ROOT, "references", "grammar-registry.json")
OUT = os.path.join(ROOT, "references", "coverage.md")


def main():
    registry = json.load(open(REG, encoding="utf-8"))
    grammars = registry["grammars"]
    impl = [g for g in grammars if g["status"] == "implemented"]
    plan = [g for g in grammars if g["status"] != "implemented"]

    lines = ["# 语法覆盖清单", "",
             "> 由 `scripts/coverage.py` 生成,请勿手工修改。", "",
             f"- 总计:{len(grammars)} 条",
             f"- 已实现:{len(impl)} 条",
             f"- planned:{len(plan)} 条", "",
             "## 已实现", "",
             "| id | 名称 | trigger | FT 域 | 渲染器 |",
             "|---|---|---|---|---|"]
    for g in impl:
        lines.append(f"| `{g['id']}` | {g['name']} | `{g['trigger']}` | {', '.join(g.get('ft_domain', []))} | `{g.get('renderer', '')}` |")
    lines += ["", "## planned", "",
              "| id | 名称 | trigger | FT 域 |", "|---|---|---|---|"]
    for g in plan:
        lines.append(f"| `{g['id']}` | {g['name']} | `{g.get('trigger', '')}` | {', '.join(g.get('ft_domain', []))} |")
    with open(OUT, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print("wrote", OUT, "| implemented", len(impl), "| planned", len(plan))


if __name__ == "__main__":
    main()
