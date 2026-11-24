# 运行报告:tom-bridge

## 1 页面简报

- 目的:转型项目第二阶段立项;向指导委员会汇报 FTE 缩减与迁移进度
- 决策:批准第二阶段的 34 个 FTE 范围
- 故事句:FY25 的 193 个 FTE 经三个举措压到 129 的迁移范围;其中 95 已在迁移、34 留待第二阶段;Accounting 承担了最大份额。
- 读者问题:
  - 193 怎么减到 129?每一步减了多少?
  - 129 现在分成哪两部分?两部分是否合计为 129?
  - 每个阶段各职能的人数怎么变?
  - 还剩多少?

## 2 校验

| 检查 | 结果 | 明细 |
|---|---|---|
| 基线 + 驱动 = 纳入迁移(合计) | PASS | 193 + -64 = 129; 目标 129 |
| 迁移中 + 残余 = 纳入迁移(合计) | PASS | 95 + 34 = 129; 目标 129 |
| Accounting:迁移中 + 残余 = 纳入迁移 | PASS | 66 = 45 + 21 |
| Customer Service:迁移中 + 残余 = 纳入迁移 | PASS | 31 = 23 + 8 |
| Procurement:迁移中 + 残余 = 纳入迁移 | PASS | 19 = 19 + 0 |
| Sales Support:迁移中 + 残余 = 纳入迁移 | PASS | 13 = 8 + 5 |
| 比率分母非零 | PASS | 分母 95 |

## 3 关系识别

- sequence: True
- composition: True
- partition: True

## 4 语法选择

- 选中:partition_bridge(桥接 + 分层构成 + 浮空划分)
- 触发类型:partition
- FT 词表域:part-to-whole, change-over-time
- 词表候选:annotated_narrative, combo, composition, donut, funnel, gantt, issue_tree, mekko, partition_bridge, pie, roadmap, slope, small_multiples, treemap, waffle, waterfall
- FT 图型:Stacked column, Proportional stacked bar, Pie, Donut, Treemap, Voronoi, Arc, Gridplot, Venn, Waterfall, Line, Column, Line + column, Stock price, Slope, Area chart, Fan chart (projection), Connected scatterplot, Calendar heatmap, Priestley timeline, Circle timeline, Seismogram
- 皮肤:house
- 外部参照:

## 5 产出

- spec.json
- chart.svg

## 6 合计

```json
{
  "baseline": 193,
  "levers": -64,
  "in_scope": 129,
  "in_progress": 95,
  "residual": 34
}
```
