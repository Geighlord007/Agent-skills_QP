# 运行报告:tesla-q2-2026

## 1 页面简报

- 目的:用最新 SEC 财报判断增长质量:收入是否转化为利润与现金
- 决策:判断价格与资本开支对利润的挤压是否可持续
- 故事句:Q2 2026 营收 282.4 亿美元、同比 +26%,但毛利率 16.8%、营业利润率 1.4%、自由现金流 -10.9 亿美元;Q3 交付 486,532 辆,同比 -2.1%。
- 读者问题:
  - 收入增长由哪块业务驱动?
  - 利润率为什么下降?
  - 现金流转负的原因是什么?

## 2 校验

| 检查 | 结果 | 明细 |
|---|---|---|
| 汽车 与季度数一致 | PASS | n=5 |
| 能源 与季度数一致 | PASS | n=5 |
| 服务 与季度数一致 | PASS | n=5 |
| 各业务之和等于总营收 | PASS | 22.496, 28.095, 24.901, 22.387, 28.236 |
| 利润率与季度数一致 | PASS | n=5 |
| 自由现金流与季度数一致 | PASS | n=5 |

## 3 关系识别

- change-over-time: True
- part-to-whole: True
- deviation: True

## 4 语法选择

- 选中:growth_margin(营收增长与利润率双面板)
- 触发类型:growth_margin
- FT 词表域:change-over-time, part-to-whole, deviation
- 词表候选:annotated_narrative, combo, composition, donut, funnel, gantt, issue_tree, mekko, partition_bridge, pie, roadmap, scenario_compare, slope, small_multiples, tornado, treemap, waffle, waterfall
- FT 图型:Line, Column, Line + column, Stock price, Slope, Area chart, Fan chart (projection), Connected scatterplot, Calendar heatmap, Priestley timeline, Circle timeline, Seismogram, Stacked column, Proportional stacked bar, Pie, Donut, Treemap, Voronoi, Arc, Gridplot, Venn, Waterfall, Diverging bar, Diverging stacked bar, Spine chart, Surplus/deficit filled line
- 皮肤:house
- 外部参照:

## 5 产出

- spec.json
- chart.svg
