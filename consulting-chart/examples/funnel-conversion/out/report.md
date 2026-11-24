# 运行报告:funnel-conversion

## 1 页面简报

- 目的:增长复盘;定位转化链路的主要流失
- 决策:优先修复访客到线索环节
- 故事句:1,000 访客经 320 线索、120 合格,最终成交 30;总转化 3.0%,最大单步流失在访客到线索。
- 读者问题:
  - 各阶段流失多少?
  - 哪一步的绝对流失最大?
  - 总转化率是多少?

## 2 校验

| 检查 | 结果 | 明细 |
|---|---|---|
| 阶段与数值长度一致 | PASS | n=4 |
| 逐级不增加 | PASS | 逐项 |

## 3 关系识别

- funnel: True

## 4 语法选择

- 选中:funnel(漏斗/金字塔)
- 触发类型:funnel
- FT 词表域:part-to-whole
- 词表候选:combo, composition, donut, funnel, issue_tree, mekko, partition_bridge, pie, treemap, waffle, waterfall
- FT 图型:Stacked column, Proportional stacked bar, Pie, Donut, Treemap, Voronoi, Arc, Gridplot, Venn, Waterfall
- 皮肤:house
- 外部参照:

## 5 产出

- spec.json
- chart.svg
