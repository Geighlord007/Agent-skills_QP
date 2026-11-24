# 运行报告:cashflow-waterfall

## 1 页面简报

- 目的:财务评审;解释经营现金流与自由现金流之间的差额来源
- 决策:确认维护性资本开支与增长性资本开支的预算安排
- 故事句:EBITDA 250 经营运资本与一次性项目后形成经营性现金流 176,再扣除 280 的增长性资本开支,最终自由现金流为 -153。
- 读者问题:
  - 起点到终点每一步减了多少?
  - 经营性现金流小计是否对得上?
  - 最大的一项缺口来自哪里?
  - 各项目同比变化是多少?

## 2 校验

| 检查 | 结果 | 明细 |
|---|---|---|
| EBITDA 起点 | PASS | 250 |
| 第 1 步累计 | PASS | 205 |
| 第 2 步累计 | PASS | 220 |
| 第 3 步累计 | PASS | 180 |
| 第 4 步累计 | PASS | 168 |
| 第 5 步累计 | PASS | 176 |
| 经营性现金流 等于累计 | PASS | 累计 176 vs 标注 176 |
| 第 7 步累计 | PASS | 146 |
| 第 8 步累计 | PASS | -134 |
| 第 9 步累计 | PASS | -149 |
| 第 10 步累计 | PASS | -171 |
| 第 11 步累计 | PASS | -153 |
| 自由现金流 等于累计 | PASS | 累计 -153 vs 标注 -153 |

## 3 关系识别

- sequence: True

## 4 语法选择

- 选中:waterfall(顺序桥接(含小计、分段与方差括线))
- 触发类型:bridge
- FT 词表域:deviation, change-over-time
- 词表候选:annotated_narrative, combo, gantt, partition_bridge, roadmap, scenario_compare, slope, small_multiples, tornado, waterfall
- FT 图型:Diverging bar, Diverging stacked bar, Spine chart, Surplus/deficit filled line, Line, Column, Line + column, Stock price, Slope, Area chart, Fan chart (projection), Connected scatterplot, Calendar heatmap, Priestley timeline, Circle timeline, Seismogram
- 皮肤:house
- 外部参照:

## 5 产出

- spec.json
- chart.svg

## 6 合计

```json
{
  "start": 250
}
```
