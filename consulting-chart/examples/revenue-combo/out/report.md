# 运行报告:revenue-combo

## 1 页面简报

- 目的:十年财务回顾与展望;解释营收平台期与盈利改善
- 决策:确认 2031 年前的营收与毛利目标
- 故事句:营收在 2025 年触底 48.2 后回升,2030 年达到 63.5;毛利润同步改善,2030 年达到 13.4(21%)。
- 读者问题:
  - 营收的长期趋势如何?
  - 毛利润与毛利率怎么变?
  - 2025–2031 的复合增速是多少?
  - 同比增速在哪些年份为负?

## 2 校验

| 检查 | 结果 | 明细 |
|---|---|---|
| 年份与序列长度一致 | PASS | n=11 |
| 毛利润不超过营收 | PASS | 逐项检查 |

## 3 关系识别

- time_series: True
- ratio_line: True

## 4 语法选择

- 选中:combo(堆叠柱 + 同比折线 + 趋势带)
- 触发类型:time_series
- FT 词表域:change-over-time
- 词表候选:annotated_narrative, combo, gantt, partition_bridge, roadmap, slope, small_multiples, waterfall
- FT 图型:Line, Column, Line + column, Stock price, Slope, Area chart, Fan chart (projection), Connected scatterplot, Calendar heatmap, Priestley timeline, Circle timeline, Seismogram
- 皮肤:house
- 外部参照:

## 5 产出

- spec.json
- chart.svg
