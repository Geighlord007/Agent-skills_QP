# 运行报告:slope-adoption

## 1 页面简报

- 目的:区域采纳率复盘;看起点、终点与变化幅度
- 决策:把 West 的做法复制到 South 与 Central
- 故事句:五个区域全部上升;West +12pp 最大,South +1pp 最小。
- 读者问题:
  - 各区域起点与终点是多少?
  - 哪个区域升幅最大?

## 2 校验

| 检查 | 结果 | 明细 |
|---|---|---|
| 实体非空 | PASS | n=5 |
| 起止数值有效 | PASS | 逐项 |

## 3 关系识别

- change-over-time: True
- ranking: True

## 4 语法选择

- 选中:slope(斜率图)
- 触发类型:slope
- FT 词表域:change-over-time, ranking
- 词表候选:annotated_narrative, combo, dot_strip, gantt, lollipop, ordered_bar, partition_bridge, roadmap, slope, small_multiples, tornado, waterfall
- FT 图型:Line, Column, Line + column, Stock price, Slope, Area chart, Fan chart (projection), Connected scatterplot, Calendar heatmap, Priestley timeline, Circle timeline, Seismogram, Ordered bar, Ordered column, Ordered proportional symbol, Dot strip plot, Slope, Lollipop chart
- 皮肤:house
- 外部参照:

## 5 产出

- spec.json
- chart.svg
