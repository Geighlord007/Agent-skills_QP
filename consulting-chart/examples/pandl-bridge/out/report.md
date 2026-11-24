# 运行报告:pandl-bridge

## 1 页面简报

- 目的:把情景测算的收入、成本与费用拆成可核查的桥接
- 决策:确认成本与费用的主要驱动项
- 故事句:收入 132 扣除 COGS 64(材料 40、人工 16、物流 8)得到毛利 68,再扣除 OPEX 41(销售 18、研发 12、管理 11),EBITDA 为 27。
- 读者问题:
  - 收入到 EBITDA 每一步扣了多少?
  - COGS 与 OPEX 内部各占多少?
  - 最大的单项扣减是什么?

## 2 校验

| 检查 | 结果 | 明细 |
|---|---|---|
| Revenue 起点 | PASS | 132 |
| COGS 分段同号 | PASS | 3 段 |
| 第 1 步累计 | PASS | 68 |
| Gross Profit 等于累计 | PASS | 累计 68 vs 标注 68 |
| OPEX 分段同号 | PASS | 3 段 |
| 第 3 步累计 | PASS | 27 |
| EBITDA 等于累计 | PASS | 累计 27 vs 标注 27 |

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
  "start": 132
}
```
