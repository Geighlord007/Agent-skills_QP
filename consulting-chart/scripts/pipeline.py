import argparse
import json
import sys
from pathlib import Path

import annotations
from validate import check as check_partition
from chartlib import render_partition_bridge
from renderers import (render_waterfall, render_combo, render_gantt, render_composition,
                       render_tornado, render_scenario_compare, render_funnel, render_lollipop,
                       render_matrix, render_waffle, render_waffle_group, render_dot_strip,
                       render_heatmap, render_mekko, render_slope, render_radar,
                       render_choropleth, render_flow_map)
from renderers_extra import (render_stacked_time_series, render_bar_pill, render_line_forecast,
                             render_mosaic_compare, render_timeline_matrix, render_maturity_table,
                             render_target_dots, render_journey_stack, render_bar_future,
                             render_quadrant_matrix, render_growth_margin, render_ai_market)

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent


def load(path):
    with Path(path).open(encoding="utf-8") as f:
        return json.load(f)


def dump(path, obj):
    with Path(path).open("w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


def check_bridge(data):
    rows = []
    cum = 0.0
    for i, c in enumerate(data["columns"]):
        if "segments" in c:
            sv = sum(s["value"] for s in c["segments"])
            same = (all(s["value"] <= 0 for s in c["segments"])
                    or all(s["value"] >= 0 for s in c["segments"]))
            rows.append((f"{c['label']} 分段同号", same, f"{len(c['segments'])} 段"))
            v = sv
        else:
            v = c["value"]
        if c["kind"] == "start":
            cum = v
            rows.append((f"{c['label']} 起点", True, f"{v:g}"))
        elif c["kind"] == "delta":
            cum += v
            rows.append((f"第 {i} 步累计", True, f"{cum:g}"))
        else:
            ok = abs(cum - v) < 1e-6
            rows.append((f"{c['label']} 等于累计", ok, f"累计 {cum:g} vs 标注 {v:g}"))
            cum = v
    return rows


def check_combo(data):
    n = len(data["years"])
    rows = [
        ("年份与序列长度一致", len(data["revenue"]) == n and len(data["gross_profit"]) == n, f"n={n}"),
        ("毛利润不超过营收", all(g <= r for g, r in zip(data["gross_profit"], data["revenue"])), "逐项检查"),
    ]
    return rows


def check_gantt(data):
    rows = []
    for t in data["tasks"]:
        rows.append((f"{t['label']} 起止顺序", t["start"] <= t["end"], f"{t['start']} -> {t['end']}"))
    return rows


def check_tornado(data):
    n = len(data["labels"])
    return [
        ("标签与两序列长度一致", len(data["low"]) == n and len(data["high"]) == n, f"n={n}"),
        ("中点非零", data["midpoint"] > 0, f"mid={data['midpoint']}"),
        ("上下界不相等", all(h != l for l, h in zip(data["low"], data["high"])), "逐项"),
    ]


def check_scenarios(data):
    names = list(data["scenarios"])
    sets = [set(data["scenarios"][n].keys()) for n in names]
    rows = [("情景指标一致", all(s == sets[0] for s in sets), f"{len(names)} 个情景")]
    if {"Revenue", "COGS", "Gross Profit"} <= sets[0]:
        for n in names:
            v = data["scenarios"][n]
            rows.append((f"{n} 毛利 = 收入 - 成本",
                         abs(v["Revenue"] - v["COGS"] - v["Gross Profit"]) < 1e-6,
                         f"{v['Revenue']:g}-{v['COGS']:g}={v['Revenue'] - v['COGS']:g}"))
    if {"Gross Profit", "OPEX", "EBITDA"} <= sets[0]:
        for n in names:
            v = data["scenarios"][n]
            rows.append((f"{n} EBITDA = 毛利 - OPEX",
                         abs(v["Gross Profit"] - v["OPEX"] - v["EBITDA"]) < 1e-6,
                         f"{v['Gross Profit']:g}-{v['OPEX']:g}={v['Gross Profit'] - v['OPEX']:g}"))
    return rows


def check_funnel(data):
    n = len(data["stages"])
    return [
        ("阶段与数值长度一致", len(data["values"]) == n, f"n={n}"),
        ("逐级不增加", all(data["values"][i] >= data["values"][i + 1] for i in range(n - 1)), "逐项"),
    ]


def check_lollipop(data):
    n = len(data["labels"])
    return [
        ("标签与数值长度一致", len(data["values"]) == n, f"n={n}"),
        ("数值非负", all(v >= 0 for v in data["values"]), "逐项"),
    ]


def check_heatmap(data):
    rows = len(data["rows"])
    cols = len(data["columns"])
    ok = len(data["values"]) == rows and all(len(r) == cols for r in data["values"])
    return [("矩阵形状一致", ok, f"{rows}x{cols}")]


def check_matrix(data):
    items = data["items"]
    return [
        ("条目坐标在 0-1", all(0 <= it["x"] <= 1 and 0 <= it["y"] <= 1 for it in items), f"n={len(items)}"),
        ("分组在图例中", all(it["group"] in data["groups"] for it in items), "逐项"),
    ]


def check_waffle(data):
    total = sum(p["value"] for p in data["parts"])
    return [
        ("分项非负", all(p["value"] >= 0 for p in data["parts"]), f"n={len(data['parts'])}"),
        ("总量为正", total > 0, f"total={total:g}"),
    ]


def check_grid_panels(data):
    states = data["states"]
    rows = []
    for p in data["panels"]:
        total = sum(p["parts"].get(s, 0) for s in states)
        rows.append((f"{p.get('title', 'panel').splitlines()[0]} 合计 100",
                     abs(total - 100) < 1e-6, f"{total:g}"))
    return rows


def check_dot_strip(data):
    cats = data["categories"]
    return [
        ("每个分类至少一个值", all(len(a) > 0 for a in cats.values()), f"{len(cats)} 类"),
        ("数值非负", all(v >= 0 for a in cats.values() for v in a), "逐项"),
    ]


def check_mekko(data):
    segs = data["segments"]
    keys = set(segs[0]["shares"].keys())
    return [
        ("宽度为正", all(s["width"] > 0 for s in segs), f"{len(segs)} 列"),
        ("份额合计 100", all(abs(sum(s["shares"].values()) - 100) < 1e-6 for s in segs), "逐列"),
        ("分项一致", all(set(s["shares"].keys()) == keys for s in segs), "逐列"),
    ]


def check_slope(data):
    ents = data["entities"]
    return [
        ("实体非空", len(ents) > 0, f"n={len(ents)}"),
        ("起止数值有效", all(isinstance(e.get("from"), (int, float))
                         and isinstance(e.get("to"), (int, float)) for e in ents), "逐项"),
    ]


def check_radar(data):
    dims = data["dimensions"]
    return [
        ("维度非空", len(dims) > 0, f"n={len(dims)}"),
        ("序列长度一致", all(len(s["values"]) == len(dims) for s in data["series"]), "逐项"),
    ]


def check_choropleth(data):
    import maps
    known = {maps.iso(f) for f in maps.features()}
    vals = data["values"]
    unknown = [k for k in vals if k not in known]
    return [
        ("有数值", len(vals) > 0, f"n={len(vals)}"),
        ("国家代码可识别", not unknown, ",".join(unknown[:5]) or "全部匹配"),
    ]


def check_flow_map(data):
    import maps
    known = {maps.iso(f) for f in maps.features()}
    flows = data["flows"]
    bad = [f for f in flows if f["from"] not in known or f["to"] not in known]
    return [
        ("流向非空", len(flows) > 0, f"n={len(flows)}"),
        ("起讫可识别", not bad, f"异常 {len(bad)} 条"),
    ]


def check_sankey(data):
    nodes = set(data["nodes"])
    links = data["links"]
    bad = [l for l in links if l["from"] not in nodes or l["to"] not in nodes]
    return [
        ("节点非空", len(nodes) > 0, f"n={len(nodes)}"),
        ("连接端点存在", not bad, f"异常 {len(bad)} 条"),
    ]


def check_stacked_time_series(data):
    n = len(data["years"])
    return [("年份与序列长度一致", all(len(s["values"]) == n for s in data["series"]), f"n={n}")]


def check_bar_pill(data):
    n = len(data["years"])
    return [
        ("年份与数值一致", len(data["values"]) == n, f"n={n}"),
        ("药丸行长度一致", not data.get("pills") or len(data["pills"]) == n, f"pills={len(data.get('pills', []))}"),
    ]


def check_line_forecast(data):
    y = data["years"]
    return [
        ("年份与数值一致", len(data["values"]) == len(y), f"n={len(y)}"),
        ("预测起点在年份内", data["forecast_from"] in y, str(data["forecast_from"])),
    ]


def check_mosaic_compare(data):
    rows = []
    for c in data["columns"]:
        total = sum(c["shares"].values())
        rows.append((f"{c['title'][:10]} 合计不超过 100", 0 < total <= 100, f"{total:g}"))
    return rows


def check_timeline_matrix(data):
    y = set(data["years"])
    bad = [ev for r in data["rows"] for ev in r.get("events", []) if ev["year"] not in y]
    return [("事件年份在列内", not bad, f"异常 {len(bad)} 个")]


def check_maturity_table(data):
    n = len(data["levels"])
    return [("每行单元格数与等级一致", all(len(r["cells"]) == n for r in data["rows"]), f"{n} 级")]


def check_target_dots(data):
    rows = data["rows"]
    n = len(rows)
    rows_out = []
    for p in data["panels"]:
        xmax = p.get("x_max", data.get("x_max", 80))
        rows_out.append((f"{p['title']} 汇总条与行数一致",
                         len(p.get("bar_values", [])) == n, f"n={n}"))
        for s in p["series"]:
            rows_out.append((f"{p['title']} {s['name']} 与行数一致",
                             len(s["values"]) == n, f"n={n}"))
            rows_out.append((f"{p['title']} {s['name']} 在 0-{xmax:g}",
                             all(v is None or 0 <= v <= xmax for v in s["values"]), "逐项"))
        rows_out.append((f"{p['title']} 汇总条在 0-{xmax:g}",
                         all(0 <= v <= xmax for v in p.get("bar_values", [])), "逐项"))
    bad = [b for b in data.get("brackets", [])
           if not (0 <= b["from"] < n and 0 <= b["to"] < n and b["from"] <= b["to"])]
    rows_out.append(("括号范围有效", not bad, f"异常 {len(bad)} 个"))
    return rows_out


def check_journey_stack(data):
    stages = data["stages"]
    n = len(stages)
    rows = data["values"]
    return [
        ("每行阶段数与图例一致", all(len(r) == n for r in rows), f"{n} 个阶段"),
        ("每行合计不超过 100", all(0 < sum(r) <= 100 for r in rows),
         ", ".join(f"{sum(r):g}" for r in rows)),
        ("阶段值非负", all(v >= 0 for r in rows for v in r), "逐项"),
    ]


def check_bar_future(data):
    rows = data["rows"]
    n = len(rows)
    out = []
    for p in data["panels"]:
        out.append((f"{p['title']} 两序列与行数一致",
                    len(p["current"]) == n and len(p["future"]) == n, f"n={n}"))
        out.append((f"{p['title']} 取值在 0-100",
                    all(0 <= v <= 100 for v in p["current"] + p["future"]), "逐项"))
    return out


def check_quadrant_matrix(data):
    items = data["items"]
    return [
        ("坐标在 0-100", all(0 <= it["x"] <= 100 and 0 <= it["y"] <= 100 for it in items),
         f"n={len(items)}"),
        ("分组在图例中", all(it["group"] in data["groups"] for it in items), "逐项"),
        ("标签非空", all(it["label"].strip() for it in items), "逐项"),
    ]


def check_growth_margin(data):
    n = len(data["quarters"])
    rows = []
    for name, vals in data["segments"].items():
        rows.append((f"{name} 与季度数一致", len(vals) == n, f"n={n}"))
    totals = [sum(v[i] for v in data["segments"].values()) for i in range(n)]
    rows.append(("各业务之和等于总营收", all(abs(t - r) < 1 for t, r in zip(totals, data["revenue"])),
                 ", ".join(f"{t:g}" for t in totals)))
    rows.append(("利润率与季度数一致",
                 len(data["gross_margin"]) == n and len(data["operating_margin"]) == n, f"n={n}"))
    rows.append(("自由现金流与季度数一致", len(data["free_cash_flow"]) == n, f"n={n}"))
    return rows


def check_ai_market(data):
    q = len(data["quarters"])
    rows = [("季度非空", q > 0, f"n={q}")]
    shares = []
    for p in data["providers"]:
        rows.append((f"{p['name']} 与季度数一致", len(p["values"]) == q, f"n={q}"))
        shares.append(p["values"])
    totals = [sum(s[i] for s in shares) for i in range(q)]
    rows.append(("每季度份额合计约 100", all(99 <= t <= 101 for t in totals),
                 ", ".join(f"{t:g}" for t in totals)))
    rows.append(("价格快照含价格与份额",
                 all("price" in it and "share" in it for it in data["price_items"]), "逐项"))
    rp = data["regions"]["periods"]
    rows.append(("地区分期与份额长度一致",
                 all(len(s["values"]) == len(rp) for s in data["regions"]["series"]), f"n={len(rp)}"))
    return rows




KEY_TRIGGERS = {
    "heatmap": {"heatmap": True},
    "scenarios": {"scenarios": True},
    "funnel": {"funnel": True},
    "lollipop": {"ranking": True, "magnitude": True},
    "matrix": {"correlation": True},
    "waffle": {"composition": True},
    "grid_panels": {"composition": True},
    "dot_strip": {"distribution": True, "ranking": True},
    "mekko": {"part-to-whole": True},
    "slope": {"change-over-time": True, "ranking": True},
    "radar": {"magnitude": True},
    "choropleth": {"spatial": True},
    "flow_map": {"spatial": True, "flow": True},
    "sankey": {"flow": True},
    "stacked_time_series": {"change-over-time": True, "part-to-whole": True},
    "bar_pill": {"change-over-time": True, "deviation": True},
    "line_forecast": {"change-over-time": True},
    "mosaic_compare": {"part-to-whole": True},
    "timeline_matrix": {"change-over-time": True},
    "maturity_table": {"part-to-whole": True},
    "target_dots": {"ranking": True, "distribution": True, "deviation": True},
    "journey_stack": {"part-to-whole": True, "ranking": True},
    "bar_future": {"deviation": True, "change-over-time": True},
    "quadrant_matrix": {"correlation": True, "ranking": True},
    "growth_margin": {"change-over-time": True, "part-to-whole": True, "deviation": True},
    "ai_market_map": {"change-over-time": True, "part-to-whole": True, "correlation": True},
}

DEFAULT_FLAGS = {
    "bridge": {"sequence": True},
    "composition": {"composition": True},
    "tornado": {"ranking": True, "deviation": True},
    "partition": {"sequence": True, "composition": True, "partition": True},
    "time_series": {"time_series": True, "ratio_line": True},
    "schedule": {"schedule": True},
    **KEY_TRIGGERS,
}


def d_bridge(d):
    ok = ("columns" in d and d["columns"] and isinstance(d["columns"][0], dict)
          and "kind" in d["columns"][0])
    return {"type": "bridge", "flags": {"sequence": True}} if ok else None


def d_composition(d):
    return {"type": "composition", "flags": {"composition": True}} if "snapshots" in d else None


def d_tornado(d):
    ok = ("tornado" in d or ("labels" in d and "midpoint" in d))
    return {"type": "tornado", "flags": {"ranking": True, "deviation": True}} if ok else None


def d_partition(d):
    if not ("baseline" in d and "levers" in d and "in_scope" in d
            and "in_progress" in d and "residual" in d):
        return None
    cats = list(d["baseline"].keys())
    same = all(set(d[k].keys()) == set(cats) for k in ("in_scope", "in_progress", "residual"))
    part = same and all(abs(d["in_scope"][c] - d["in_progress"][c] - d["residual"][c]) < 1e-6 for c in cats)
    return {"type": "partition", "flags": {"sequence": True, "composition": same, "partition": part}}


def d_time_series(d):
    return ({"type": "time_series", "flags": {"time_series": True, "ratio_line": True}}
            if ("years" in d and "revenue" in d) else None)


def d_schedule(d):
    return {"type": "schedule", "flags": {"schedule": True}} if "schedule" in d else None


DETECTORS = [d_bridge, d_composition, d_tornado, d_partition, d_time_series, d_schedule]


def detect(data, brief=None):
    # 1) 优先支持显式声明 chart_type / grammar
    explicit = data.get("chart_type") or data.get("grammar")
    if not explicit and isinstance(brief, dict):
        explicit = brief.get("chart_type") or brief.get("grammar")
    if explicit:
        if explicit == "partition":
            hit = d_partition(data)
            if hit:
                return hit
        flags = dict(DEFAULT_FLAGS.get(explicit, {explicit: True}))
        return {"type": explicit, "flags": flags}

    # 2) 兼容旧版 data.json 顶层图型标记键
    for trigger, flags in KEY_TRIGGERS.items():
        if trigger in data:
            return {"type": trigger, "flags": dict(flags)}

    # 3) 数据结构指纹启发式识别 (bridge / composition / tornado / partition / time_series / schedule)
    for fn in DETECTORS:
        hit = fn(data)
        if hit:
            return hit
    raise RuntimeError("无法识别数据形态;可在 data.json 顶层指定 chart_type 或检查必需字段")


FT_BY_TYPE = {
    "partition": ["part-to-whole", "change-over-time"],
    "bridge": ["deviation", "change-over-time"],
    "time_series": ["change-over-time"],
    "schedule": ["change-over-time"],
    "composition": ["part-to-whole"],
    "tornado": ["ranking", "deviation"],
    "scenarios": ["magnitude", "deviation"],
    "funnel": ["part-to-whole"],
    "lollipop": ["ranking", "magnitude"],
    "heatmap": ["correlation", "spatial"],
    "matrix": ["correlation"],
    "waffle": ["part-to-whole"],
    "grid_panels": ["part-to-whole"],
    "dot_strip": ["ranking", "distribution"],
    "mekko": ["part-to-whole", "magnitude"],
    "slope": ["change-over-time", "ranking"],
    "radar": ["magnitude"],
    "choropleth": ["spatial"],
    "flow_map": ["spatial", "flow"],
    "sankey": ["flow"],
    "stacked_time_series": ["change-over-time", "part-to-whole"],
    "bar_pill": ["change-over-time", "deviation"],
    "line_forecast": ["change-over-time"],
    "mosaic_compare": ["part-to-whole"],
    "timeline_matrix": ["change-over-time"],
    "maturity_table": ["part-to-whole"],
    "target_dots": ["ranking", "distribution", "deviation"],
    "journey_stack": ["part-to-whole", "ranking"],
    "bar_future": ["deviation", "change-over-time"],
    "quadrant_matrix": ["correlation", "ranking"],
    "growth_margin": ["change-over-time", "part-to-whole", "deviation"],
    "ai_market_map": ["change-over-time", "part-to-whole", "correlation"],
}


def select_grammar(kind):
    domains = FT_BY_TYPE.get(kind, [])
    vocab = load(ROOT / "references" / "vocab-index.json")
    candidates = []
    ft_types = []
    for d in domains:
        entry = vocab["domains"].get(d, {})
        candidates += entry.get("candidates", [])
        ft_types += entry.get("ft_types", [])
    registry = load(ROOT / "references" / "grammar-registry.json")
    matches = [g for g in registry["grammars"]
               if g.get("trigger") == kind and set(g.get("ft_domain", [])) & set(domains)]
    if not matches:
        raise RuntimeError("注册表没有匹配的语法: " + kind)
    impl = [g for g in matches if g["status"] == "implemented"]
    if not impl:
        raise RuntimeError("匹配到 " + matches[0]["id"] + "(" + matches[0]["name"] + ") 但渲染器未实现,停止")
    if kind not in HANDLERS:
        raise RuntimeError("注册表标记已实现,但代码缺少处理器: " + kind)
    return impl[0], domains, sorted(set(candidates)), ft_types


def build_partition_spec(brief, data, t):
    cats = list(data["baseline"].keys())
    seg = lambda d: [{"name": c, "value": d[c]} for c in cats]
    cols = [
        {"id": "baseline", "kind": "stack", "label": brief["labels"]["baseline"],
         "level": t["baseline"], "total": t["baseline"], "segments": seg(data["baseline"])}
    ]
    connectors = []
    level = t["baseline"]
    prev = "baseline"
    for i, l in enumerate(data["levers"]):
        cid = f"lever{i + 1}"
        base = level + l["delta"]
        cols.append({"id": cid, "kind": "step", "label": l["label"],
                     "value": abs(l["delta"]), "base": base, "level": level})
        connectors.append({"from": prev, "to": cid, "level": level})
        prev, level = cid, base
    cols.append({"id": "in_scope", "kind": "stack", "label": brief["labels"]["in_scope"],
                 "level": t["in_scope"], "total": t["in_scope"], "segments": seg(data["in_scope"])})
    connectors.append({"from": prev, "to": "in_scope", "level": t["in_scope"]})
    cols.append({"id": "in_progress", "kind": "stack", "label": brief["labels"]["in_progress"],
                 "base": t["residual"], "level": t["in_scope"], "total": t["in_progress"],
                 "segments": seg(data["in_progress"])})
    connectors.append({"from": "in_scope", "to": "band", "level": t["in_scope"]})
    cols.append({"id": "residual", "kind": "stack", "label": brief["labels"]["residual"],
                 "level": t["residual"], "total": t["residual"], "segments": seg(data["residual"]),
                 "emphasis": True})
    connectors.append({"from": "in_progress", "to": "residual", "level": t["residual"]})
    ratio_pct = round(t["residual"] / t["in_progress"] * 100)
    return {
        "type": "partition_bridge",
        "title": brief["title"],
        "panel_title": brief["panel_title"],
        "columns": cols,
        "connectors": connectors,
        "annotations": [
            {"type": "band", "column": "residual", "pad": 52, "top": 200, "bottom": 552, "opacity": 0.6},
            {"type": "ratio", "column": "residual", "label": "To go", "text": f"{ratio_pct}%",
             "cy": 270, "arrow_to": t["residual"]}
        ],
        "insights": brief["insights"],
        "source": brief["source"]
    }


def build_composition_spec(brief, data):
    cols = []
    for label, d in data["snapshots"].items():
        segs = [{"name": k, "value": v} for k, v in d.items()]
        cols.append({"label": label, "segments": segs, "total": sum(d.values())})
    return {"type": "composition", "title": brief["title"], "panel_title": brief["panel_title"],
            "columns": cols, "insights": brief.get("insights", []), "source": brief["source"]}


def build_tornado_spec(brief, data):
    return {"type": "tornado", "title": brief["title"], "panel_title": brief["panel_title"],
            "labels": data["labels"], "low": data["low"], "high": data["high"],
            "midpoint": data["midpoint"], "insights": brief.get("insights", []),
            "source": brief["source"]}


def build_scenario_spec(brief, data):
    names = list(data["scenarios"].keys())
    metrics = list(data["scenarios"][names[0]].keys())
    series = [{"name": n, "values": [data["scenarios"][n][m] for m in metrics]} for n in names]
    return {"type": "scenario_compare", "title": brief["title"], "panel_title": brief["panel_title"],
            "metrics": metrics, "series": series, "insights": brief.get("insights", []),
            "note": brief.get("note", ""), "source": brief["source"]}


def build_funnel_spec(brief, data):
    return {"type": "funnel", "title": brief["title"], "panel_title": brief["panel_title"],
            "stages": data["stages"], "values": data["values"],
            "insights": brief.get("insights", []), "source": brief["source"]}


def build_lollipop_spec(brief, data):
    return {"type": "lollipop", "title": brief["title"], "panel_title": brief["panel_title"],
            "labels": data["labels"], "values": data["values"],
            "insights": brief.get("insights", []), "source": brief["source"]}


def build_matrix_spec(brief, data):
    return {"type": "matrix", "title": brief["title"], "panel_title": brief["panel_title"],
            "items": data["items"], "groups": data["groups"], "quadrants": data["quadrants"],
            "x_label": data["x_label"], "y_label": data["y_label"],
            "insights": brief.get("insights", []), "source": brief["source"]}


def build_waffle_spec(brief, data):
    return {"type": "waffle", "title": brief["title"], "panel_title": brief["panel_title"],
            "parts": data["parts"], "cells": data.get("cells", 100),
            "insights": brief.get("insights", []), "source": brief["source"]}


def build_grid_panels_spec(brief, data):
    return {"type": "grid_panels", "title": brief["title"], "panel_title": brief["panel_title"],
            "panels": data["panels"], "states": data["states"], "colors": data.get("colors", {}),
            "cols": data.get("cols", 3), "cell": data.get("cell", 14),
            "title_below": data.get("title_below", False),
            "show_pct": data.get("show_pct", True),
            "takeaway": brief.get("takeaway", ""),
            "insights": brief.get("insights", []), "source": brief["source"]}


def build_dot_strip_spec(brief, data):
    return {"type": "dot_strip", "title": brief["title"], "panel_title": brief["panel_title"],
            "categories": data["categories"], "unit": data.get("unit", ""),
            "insights": brief.get("insights", []), "source": brief["source"]}


def build_heatmap_spec(brief, data):
    return {"type": "heatmap", "title": brief["title"], "panel_title": brief["panel_title"],
            "rows": data["rows"], "columns": data["columns"], "values": data["values"],
            "unit": data.get("unit", ""), "insights": brief.get("insights", []),
            "source": brief["source"]}


def build_mekko_spec(brief, data):
    return {"type": "mekko", "title": brief["title"], "panel_title": brief["panel_title"],
            "segments": data["segments"], "insights": brief.get("insights", []),
            "source": brief["source"]}


def build_slope_spec(brief, data):
    return {"type": "slope", "title": brief["title"], "panel_title": brief["panel_title"],
            "t1": data["t1"], "t2": data["t2"], "entities": data["entities"],
            "insights": brief.get("insights", []), "source": brief["source"]}


def build_stacked_time_series_spec(brief, data):
    return {"type": "stacked_time_series", "title": brief["title"], "panel_title": brief["panel_title"],
            "years": data["years"], "series": data["series"], "colors": data.get("colors", {}),
            "insights": brief.get("insights", []), "source": brief["source"]}


def build_bar_pill_spec(brief, data):
    return {"type": "bar_pill", "title": brief["title"], "panel_title": brief["panel_title"],
            "years": data["years"], "values": data["values"], "labels": data.get("labels", []),
            "pills": data.get("pills", []), "badges": data.get("badges", {}),
            "callout": data.get("callout", ""), "callout_year": data.get("callout_year"),
            "insights": brief.get("insights", []), "source": brief["source"]}


def build_line_forecast_spec(brief, data):
    return {"type": "line_forecast", "title": brief["title"], "panel_title": brief["panel_title"],
            "years": data["years"], "values": data["values"], "forecast_from": data["forecast_from"],
            "brackets": data.get("brackets", []), "callout": data.get("callout", ""),
            "subtitle": data.get("subtitle", ""), "label_years": data.get("label_years", []),
            "label_positions": data.get("label_positions", {}), "badges": data.get("badges", []),
            "callout_emphasis": data.get("callout_emphasis", ""), "callout_to": data.get("callout_to"),
            "actual_label": data.get("actual_label", "Actual"),
            "forecast_label": data.get("forecast_label", "Forecast"),
            "y_max": data.get("y_max", 1400),
            "insights": brief.get("insights", []), "source": brief["source"]}


def build_mosaic_compare_spec(brief, data):
    return {"type": "mosaic_compare", "title": brief["title"], "panel_title": brief["panel_title"],
            "columns": data["columns"], "groups": data["groups"], "colors": data.get("colors", {}),
            "row_header": data.get("row_header", ""),
            "insights": brief.get("insights", []), "source": brief["source"]}


def build_timeline_matrix_spec(brief, data):
    return {"type": "timeline_matrix", "title": brief["title"], "panel_title": brief["panel_title"],
            "years": data["years"], "rows": data["rows"],
            "examples_label": data.get("examples_label", ""),
            "highlight_year": data.get("highlight_year", ""),
            "source": brief["source"]}


def build_maturity_table_spec(brief, data):
    return {"type": "maturity_table", "title": brief["title"], "panel_title": brief["panel_title"],
            "levels": data["levels"], "bands": data["bands"], "stair": data.get("stair", []),
            "transition": data.get("transition", {}),
            "rows": data["rows"], "source": brief["source"]}


def build_target_dots_spec(brief, data):
    return {"type": "target_dots", "title": brief["title"], "panel_title": brief["panel_title"],
            "rows": data["rows"], "panels": data["panels"],
            "brackets": data.get("brackets", []), "insights": brief.get("insights", []),
            "dodge": data.get("dodge", 0.65), "dot_size": data.get("dot_size", 7),
            "dot_stroke": data.get("dot_stroke", 1.6),
            "source": brief["source"]}


def build_journey_stack_spec(brief, data):
    return {"type": "journey_stack", "title": brief["title"], "panel_title": brief["panel_title"],
            "rows": data["rows"], "stages": data["stages"], "values": data["values"],
            "brackets": data.get("brackets", []), "source": brief["source"]}


def build_bar_future_spec(brief, data):
    return {"type": "bar_future", "title": brief["title"], "panel_title": brief["panel_title"],
            "rows": data["rows"], "panels": data["panels"],
            "current_label": data.get("current_label", "当前值"),
            "future_label": data.get("future_label", "未来值"),
            "brackets": data.get("brackets", []), "source": brief["source"]}


def build_quadrant_matrix_spec(brief, data):
    return {"type": "quadrant_matrix", "title": brief["title"], "panel_title": brief["panel_title"],
            "items": data["items"], "groups": data["groups"], "quadrants": data["quadrants"],
            "x_label": data["x_label"], "y_label": data["y_label"],
            "x_ticks": data.get("x_ticks", ["低", "中", "高"]),
            "y_ticks": data.get("y_ticks", ["低", "中", "高"]),
            "source": brief["source"]}


def build_growth_margin_spec(brief, data):
    return {"type": "growth_margin", "title": brief["title"], "panel_title": brief["panel_title"],
            "quarters": data["quarters"], "segments": data["segments"],
            "revenue": data["revenue"], "gross_margin": data["gross_margin"],
            "operating_margin": data["operating_margin"],
            "free_cash_flow": data["free_cash_flow"], "capex": data.get("capex", []),
            "callout": data.get("callout", ""), "source": brief["source"]}


def build_ai_market_spec(brief, data):
    return {"type": "ai_market_map", "title": brief["title"], "panel_title": brief["panel_title"],
            "quarters": data["quarters"], "providers": data["providers"],
            "price_items": data["price_items"], "price_tiers": data.get("price_tiers", []),
            "regions": data["regions"], "callout": data.get("callout", ""),
            "notes": data.get("notes", ""), "source": brief["source"]}




def build_radar_spec(brief, data):
    return {"type": "radar", "title": brief["title"], "panel_title": brief["panel_title"],
            "dimensions": data["dimensions"], "series": data["series"],
            "insights": brief.get("insights", []), "source": brief["source"]}


def build_choropleth_spec(brief, data):
    return {"type": "choropleth", "title": brief["title"], "panel_title": brief["panel_title"],
            "values": data["values"], "insights": brief.get("insights", []),
            "source": brief["source"]}


def build_flow_map_spec(brief, data):
    return {"type": "flow_map", "title": brief["title"], "panel_title": brief["panel_title"],
            "flows": data["flows"], "insights": brief.get("insights", []),
            "source": brief["source"]}


def build_waterfall_spec(brief, data):
    spec = {"type": "waterfall"}
    spec.update({k: data[k] for k in ("columns",) if k in data})
    anns = [{"type": "bracket", "from": b["from"], "to": b["to"], "text": b["text"],
             "y": b.get("at", 132), "arrow": b.get("arrow", False),
             "arrow_to": b.get("arrow_to")} for b in data.get("brackets", [])]
    spec.update({"title": brief["title"], "panel_title": brief["panel_title"],
                 "insights": brief["insights"], "source": brief["source"],
                 "note": brief.get("note", ""), "show_pct": data.get("show_pct", True),
                 "annotations": anns})
    return spec


def build_combo_spec(brief, data):
    spec = {"type": "combo"}
    spec.update({k: data[k] for k in ("years", "revenue", "gross_profit", "yoy", "y_max") if k in data})
    anns = []
    if "cagr" in data:
        c = data["cagr"]
        anns.append({"type": "trend_band", "from": c["from_year"], "to": c["to_year"],
                     "value": c["value"], "unit": "%"})
    spec.update({"title": brief["title"], "panel_title": brief["panel_title"],
                 "insights": brief["insights"], "source": brief["source"],
                 "note": brief.get("note", ""), "annotations": anns})
    return spec


def build_gantt_spec(brief, data):
    spec = {"type": "gantt"}
    spec.update({k: data[k] for k in ("months", "phases", "tasks", "band_rows", "today",
                                      "milestones", "status_label") if k in data})
    spec.update({"title": brief["title"], "source": brief["source"]})
    return spec


def check_composition(data):
    rows = []
    for snap, d in data["snapshots"].items():
        rows.append((f"{snap} 分项合计", True, f"{sum(d.values()):g}"))
    return rows, {}


def build_spec(brief, data, t, kind=None):
    kind = kind or detect(data, brief)["type"]
    if kind not in HANDLERS:
        raise RuntimeError("语法未实现: " + kind)
    spec = HANDLERS[kind]["build"](brief, data, t)
    spec["_kind"] = kind
    for key in ("figure", "question", "notes", "exhibit"):
        spec[key] = brief.get(key, "")
    return spec


def run_checks(kind, data):
    if kind not in HANDLERS:
        return [("未实现语法的数据校验", True, kind)], {}
    return HANDLERS[kind]["check"](data)


def render(spec, tokens):
    kind = spec.get("_kind")
    if kind not in HANDLERS:
        raise RuntimeError("语法未实现: " + str(kind))
    return HANDLERS[kind]["render"](spec, tokens)


HANDLERS = {
    "partition": {"check": check_partition,
                  "build": lambda b, d, t: build_partition_spec(b, d, t),
                  "render": render_partition_bridge},
    "bridge": {"check": lambda d: (check_bridge(d), {"start": d["columns"][0]["value"]}),
               "build": lambda b, d, t: build_waterfall_spec(b, d),
               "render": render_waterfall},
    "time_series": {"check": lambda d: (check_combo(d), {}),
                    "build": lambda b, d, t: build_combo_spec(b, d),
                    "render": render_combo},
    "schedule": {"check": lambda d: (check_gantt(d), {}),
                 "build": lambda b, d, t: build_gantt_spec(b, d),
                 "render": render_gantt},
    "composition": {"check": check_composition,
                    "build": lambda b, d, t: build_composition_spec(b, d),
                    "render": render_composition},
    "tornado": {"check": lambda d: (check_tornado(d), {}),
                "build": lambda b, d, t: build_tornado_spec(b, d),
                "render": render_tornado},
    "scenarios": {"check": lambda d: (check_scenarios(d), {}),
                  "build": lambda b, d, t: build_scenario_spec(b, d),
                  "render": render_scenario_compare},
    "funnel": {"check": lambda d: (check_funnel(d), {}),
               "build": lambda b, d, t: build_funnel_spec(b, d),
               "render": render_funnel},
    "lollipop": {"check": lambda d: (check_lollipop(d), {}),
                 "build": lambda b, d, t: build_lollipop_spec(b, d),
                 "render": render_lollipop},
    "matrix": {"check": lambda d: (check_matrix(d), {}),
               "build": lambda b, d, t: build_matrix_spec(b, d),
               "render": render_matrix},
    "waffle": {"check": lambda d: (check_waffle(d), {}),
               "build": lambda b, d, t: build_waffle_spec(b, d),
               "render": render_waffle},
    "grid_panels": {"check": lambda d: (check_grid_panels(d), {}),
                    "build": lambda b, d, t: build_grid_panels_spec(b, d),
                    "render": render_waffle_group},
    "dot_strip": {"check": lambda d: (check_dot_strip(d), {}),
                  "build": lambda b, d, t: build_dot_strip_spec(b, d),
                  "render": render_dot_strip},
    "heatmap": {"check": lambda d: (check_heatmap(d), {}),
                "build": lambda b, d, t: build_heatmap_spec(b, d),
                "render": render_heatmap},
    "mekko": {"check": lambda d: (check_mekko(d), {}),
              "build": lambda b, d, t: build_mekko_spec(b, d),
              "render": render_mekko},
    "slope": {"check": lambda d: (check_slope(d), {}),
              "build": lambda b, d, t: build_slope_spec(b, d),
              "render": render_slope},
    "radar": {"check": lambda d: (check_radar(d), {}),
              "build": lambda b, d, t: build_radar_spec(b, d),
              "render": render_radar},
    "choropleth": {"check": lambda d: (check_choropleth(d), {}),
                   "build": lambda b, d, t: build_choropleth_spec(b, d),
                   "render": render_choropleth},
    "flow_map": {"check": lambda d: (check_flow_map(d), {}),
                 "build": lambda b, d, t: build_flow_map_spec(b, d),
                 "render": render_flow_map},
    "stacked_time_series": {"check": lambda d: (check_stacked_time_series(d), {}),
                            "build": lambda b, d, t: build_stacked_time_series_spec(b, d),
                            "render": render_stacked_time_series},
    "bar_pill": {"check": lambda d: (check_bar_pill(d), {}),
                 "build": lambda b, d, t: build_bar_pill_spec(b, d),
                 "render": render_bar_pill},
    "line_forecast": {"check": lambda d: (check_line_forecast(d), {}),
                      "build": lambda b, d, t: build_line_forecast_spec(b, d),
                      "render": render_line_forecast},
    "mosaic_compare": {"check": lambda d: (check_mosaic_compare(d), {}),
                       "build": lambda b, d, t: build_mosaic_compare_spec(b, d),
                       "render": render_mosaic_compare},
    "timeline_matrix": {"check": lambda d: (check_timeline_matrix(d), {}),
                        "build": lambda b, d, t: build_timeline_matrix_spec(b, d),
                        "render": render_timeline_matrix},
    "maturity_table": {"check": lambda d: (check_maturity_table(d), {}),
                       "build": lambda b, d, t: build_maturity_table_spec(b, d),
                       "render": render_maturity_table},
    "target_dots": {"check": lambda d: (check_target_dots(d), {}),
                    "build": lambda b, d, t: build_target_dots_spec(b, d),
                    "render": render_target_dots},
    "journey_stack": {"check": lambda d: (check_journey_stack(d), {}),
                      "build": lambda b, d, t: build_journey_stack_spec(b, d),
                      "render": render_journey_stack},
    "bar_future": {"check": lambda d: (check_bar_future(d), {}),
                   "build": lambda b, d, t: build_bar_future_spec(b, d),
                   "render": render_bar_future},
    "quadrant_matrix": {"check": lambda d: (check_quadrant_matrix(d), {}),
                        "build": lambda b, d, t: build_quadrant_matrix_spec(b, d),
                        "render": render_quadrant_matrix},
    "growth_margin": {"check": lambda d: (check_growth_margin(d), {}),
                      "build": lambda b, d, t: build_growth_margin_spec(b, d),
                      "render": render_growth_margin},
    "ai_market_map": {"check": lambda d: (check_ai_market(d), {}),
                      "build": lambda b, d, t: build_ai_market_spec(b, d),
                      "render": render_ai_market},
}


def validate_dispatch():
    registry = load(ROOT / "references" / "grammar-registry.json")
    impl = {g["trigger"] for g in registry["grammars"] if g["status"] == "implemented"}
    code = set(HANDLERS)
    if impl != code:
        raise RuntimeError(
            "注册表与处理器不一致: registry_only=" + str(sorted(impl - code)) +
            " code_only=" + str(sorted(code - impl)))


def write_report(path, brief, rows, det, grammar, spec, t, out_files, skin, domains, candidates, ft_types):
    ref = grammar.get("reference") or grammar.get("references", {}).get("selection", "")
    lines = ["# 运行报告:" + brief["case"], ""]
    lines += ["## 1 页面简报", "", "- 目的:" + brief["purpose"], "- 决策:" + brief["decision"],
              "- 故事句:" + brief["story"], "- 读者问题:"]
    lines += ["  - " + q for q in brief["questions"]]
    lines += ["", "## 2 校验", "", "| 检查 | 结果 | 明细 |", "|---|---|---|"]
    lines += [f"| {n} | {'PASS' if p else 'FAIL'} | {d} |" for n, p, d in rows]
    lines += ["", "## 3 关系识别", ""]
    lines += [f"- {k}: {v}" for k, v in det["flags"].items()]
    lines += ["", "## 4 语法选择", "", f"- 选中:{grammar['id']}({grammar['name']})",
              f"- 触发类型:{det['type']}",
              f"- FT 词表域:{', '.join(domains)}",
              f"- 词表候选:{', '.join(candidates) if candidates else '(空)'}",
              f"- FT 图型:{', '.join(ft_types) if ft_types else '(空)'}",
              f"- 皮肤:{skin}",
              f"- 外部参照:{ref}",
              "", "## 5 产出", ""]
    lines += ["- " + f for f in out_files]
    if t:
        lines += ["", "## 6 合计", "", "```json", json.dumps(t, ensure_ascii=False, indent=2), "```"]
    lines.append("")
    Path(path).write_text("\n".join(lines), encoding="utf-8")


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    validate_dispatch()
    ap = argparse.ArgumentParser()
    ap.add_argument("--case", required=True)
    ap.add_argument("--skin", default=None)
    args = ap.parse_args()
    case_arg = Path(args.case)
    case = case_arg if case_arg.is_absolute() else ROOT / case_arg
    brief = load(case / "brief.json")
    data = load(case / "data.json")
    skin_name = args.skin or brief.get("skin", "house")
    if skin_name == "house":
        tokens = load(ROOT / "references" / "design-tokens.json")
    else:
        tokens = load(ROOT / "references" / "skins" / f"{skin_name}.json")
    if brief.get("canvas"):
        tokens["canvas"] = brief["canvas"]

    det = detect(data, brief)
    print("[1/7] 简报:", brief["story"])
    print("[2/7] 数据形态:", det["type"])

    rows, t = run_checks(det["type"], data)
    failed = [r for r in rows if not r[1]]
    for n, p, d in rows:
        print("      ", "PASS" if p else "FAIL", n, "|", d)
    if failed:
        print("[3/7] 校验失败,停止")
        sys.exit(1)
    print("[3/7] 校验通过")

    print("[4/7] 关系:", det["flags"])
    grammar, domains, candidates, ft_types = select_grammar(det["type"])
    print("[5/7] 语法:", grammar["id"], grammar["name"],
          "| FT 域:", ",".join(domains), "| 词表候选:", ",".join(candidates) or "(空)",
          "| FT 图型:", ",".join(ft_types) or "(空)")

    spec = build_spec(brief, data, t if det["type"] == "partition" else {}, kind=det["type"])
    spec["kicker"] = brief.get("kicker")
    out_dir = case / "out"
    out_dir.mkdir(parents=True, exist_ok=True)
    spec_path = out_dir / "spec.json"
    dump(spec_path, spec)
    svg_path = out_dir / "chart.svg"
    annotations.LAST_WARNINGS = []
    svg_path.write_text(render(spec, tokens), encoding="utf-8")
    if annotations.LAST_WARNINGS:
        print("[ann] 标注碰撞:", annotations.LAST_WARNINGS)
    print("[6/7] 已写:", spec_path, "|", svg_path)

    report_path = out_dir / "report.md"
    write_report(report_path, brief, rows, det, grammar, spec, t, ["spec.json", "chart.svg"],
                 skin_name, domains, candidates, ft_types)
    print("[7/7] 已写:", report_path)


if __name__ == "__main__":
    main()
