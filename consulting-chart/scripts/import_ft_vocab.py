import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
README = os.path.join(ROOT, "vendor", "chart-doctor", "visual-vocabulary", "README.md")
OUT = os.path.join(ROOT, "references", "vocab-index.json")

DOMAIN_MAP = {
    "Deviation": "deviation",
    "Correlation": "correlation",
    "Ranking": "ranking",
    "Distribution": "distribution",
    "Change over Time": "change-over-time",
    "Part-to-whole": "part-to-whole",
    "Magnitude": "magnitude",
    "Spatial": "spatial",
    "Flow": "flow",
}


def main():
    with open(README, encoding="utf-8") as f:
        lines = f.read().splitlines()

    found = {k: [] for k in DOMAIN_MAP.values()}
    current = None
    for line in lines:
        m = re.match(r"^### (.+?)\s*$", line)
        if m:
            current = DOMAIN_MAP.get(m.group(1))
            continue
        m = re.match(r"^#### (.+?)\s*$", line)
        if m and current:
            found[current].append(m.group(1))

    idx = json.load(open(OUT, encoding="utf-8"))
    registry = json.load(open(os.path.join(ROOT, "references", "grammar-registry.json"), encoding="utf-8"))
    for key, types in found.items():
        if key not in idx["domains"]:
            idx["domains"][key] = {"question": "", "candidates": []}
        idx["domains"][key]["ft_types"] = types
        ids = [g["id"] for g in registry["grammars"] if key in g.get("ft_domain", [])]
        idx["domains"][key]["candidates"] = sorted(set(idx["domains"][key].get("candidates", []) + ids))
    idx["source"] = "Financial Times visual-vocabulary (vendor/chart-doctor/visual-vocabulary/README.md)"
    idx["generated_by"] = "scripts/import_ft_vocab.py"

    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(idx, f, ensure_ascii=False, indent=2)

    for k in sorted(idx["domains"]):
        print(k, "->", len(idx["domains"][k].get("ft_types", [])), "types")


if __name__ == "__main__":
    main()
