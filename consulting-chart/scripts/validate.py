import json
import argparse
import sys


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def totals(data):
    cats = list(data["baseline"].keys())
    b = sum(data["baseline"].values())
    lever_sum = sum(l["delta"] for l in data["levers"])
    ins = sum(data["in_scope"].values())
    ip = sum(data["in_progress"].values())
    res = sum(data["residual"].values())
    return cats, b, lever_sum, ins, ip, res


def check(data):
    cats, b, lever_sum, ins, ip, res = totals(data)
    rows = []
    rows.append(("基线 + 驱动 = 纳入迁移(合计)", abs(b + lever_sum - ins) < 1e-6, f"{b:g} + {lever_sum:g} = {b + lever_sum:g}; 目标 {ins:g}"))
    rows.append(("迁移中 + 残余 = 纳入迁移(合计)", abs(ip + res - ins) < 1e-6, f"{ip:g} + {res:g} = {ip + res:g}; 目标 {ins:g}"))
    for c in cats:
        left = data["in_scope"][c]
        right = data["in_progress"][c] + data["residual"][c]
        rows.append((f"{c}:迁移中 + 残余 = 纳入迁移", abs(left - right) < 1e-6, f"{left:g} = {data['in_progress'][c]:g} + {data['residual'][c]:g}"))
    rows.append(("比率分母非零", ip > 0, f"分母 {ip:g}"))
    return rows, {"baseline": b, "levers": lever_sum, "in_scope": ins, "in_progress": ip, "residual": res}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    args = ap.parse_args()
    rows, t = check(load(args.data))
    ok = True
    for name, passed, detail in rows:
        print(("PASS" if passed else "FAIL"), "|", name, "|", detail)
        ok = ok and passed
    print("TOTALS", json.dumps(t, ensure_ascii=False))
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
