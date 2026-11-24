# 运行报告:gdp-stacked

## 1 页面简报

- 目的:城市经济体量对比;验证组合语法是否会被触发
- 决策:无(覆盖度测试用例)
- 故事句:九个城市的 GDP 在四年间此消彼长,总量从 948 增至 1,055。
- 读者问题:
  - 各城市占比如何?
  - 总量怎么变?

## 2 校验

| 检查 | 结果 | 明细 |
|---|---|---|
| 2022 分项合计 | PASS | 948.21 |
| 2023 分项合计 | PASS | 977.2 |
| 2024 分项合计 | PASS | 995.07 |
| 2025 分项合计 | PASS | 1054.98 |

## 3 关系识别

- composition: True

## 4 语法选择

- 选中:composition(分层构成柱(多时点))
- 触发类型:composition
- FT 词表域:part-to-whole
- 词表候选:combo, composition, donut, funnel, issue_tree, mekko, partition_bridge, pie, treemap, waffle, waterfall
- FT 图型:Stacked column, Proportional stacked bar, Pie, Donut, Treemap, Voronoi, Arc, Gridplot, Venn, Waterfall
- 皮肤:house
- 外部参照:

## 5 产出

- spec.json
- chart.svg
