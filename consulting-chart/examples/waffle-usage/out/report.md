# 运行报告:waffle-usage

## 1 页面简报

- 目的:使用状态盘点;用单位格展示构成
- 决策:确定试点转日常的推进目标
- 故事句:100 个受访单元中,45 个已日常使用,30 个处于试点,25 个仍在规划。
- 读者问题:
  - 日常使用占比多少?
  - 试点与规划合计多少?

## 2 校验

| 检查 | 结果 | 明细 |
|---|---|---|
| 分项非负 | PASS | n=3 |
| 总量为正 | PASS | total=100 |

## 3 关系识别

- composition: True

## 4 语法选择

- 选中:waffle(华夫格)
- 触发类型:waffle
- FT 词表域:part-to-whole
- 词表候选:combo, composition, donut, funnel, issue_tree, mekko, partition_bridge, pie, treemap, waffle, waterfall
- FT 图型:Stacked column, Proportional stacked bar, Pie, Donut, Treemap, Voronoi, Arc, Gridplot, Venn, Waterfall
- 皮肤:house
- 外部参照:

## 5 产出

- spec.json
- chart.svg
