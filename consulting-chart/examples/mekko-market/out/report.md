# 运行报告:mekko-market

## 1 页面简报

- 目的:成本杠杆的市场结构;同时看规模与领导者占比
- 决策:优先在 Cloud 与 Edge 推进领导者方案
- 故事句:Cloud 占 45% 规模且领导者份额 70%;On-prem 规模 30% 但领导者仅 35%;Edge 规模 25%、领导者 55%。
- 读者问题:
  - 各部署形态的规模占比是多少?
  - 各形态内部领导者占比多少?

## 2 校验

| 检查 | 结果 | 明细 |
|---|---|---|
| 宽度为正 | PASS | 3 列 |
| 份额合计 100 | PASS | 逐列 |
| 分项一致 | PASS | 逐列 |

## 3 关系识别

- part-to-whole: True

## 4 语法选择

- 选中:mekko(马赛克/变宽堆叠柱)
- 触发类型:mekko
- FT 词表域:part-to-whole, magnitude
- 词表候选:bubble, combo, composition, donut, funnel, issue_tree, lollipop, mekko, parallel_coordinates, partition_bridge, pie, radar, scenario_compare, treemap, waffle, waterfall
- FT 图型:Stacked column, Proportional stacked bar, Pie, Donut, Treemap, Voronoi, Arc, Gridplot, Venn, Waterfall, Column, Bar, Paired column, Paired bar, Proportional stacked bar, Proportional symbol, Isotype (pictogram), Lollipop chart, Radar chart, Parallel coordinates
- 皮肤:house
- 外部参照:

## 5 产出

- spec.json
- chart.svg
