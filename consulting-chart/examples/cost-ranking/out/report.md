# 运行报告:cost-ranking

## 1 页面简报

- 目的:成本结构复盘;找出最大的单项
- 决策:优先谈判材料与销售费用
- 故事句:六项成本合计 105,材料 40 占 38%,销售 18 次之,物流 8 最小。
- 读者问题:
  - 哪几项最大?
  - 前两项合计占比多少?

## 2 校验

| 检查 | 结果 | 明细 |
|---|---|---|
| 标签与数值长度一致 | PASS | n=6 |
| 数值非负 | PASS | 逐项 |

## 3 关系识别

- ranking: True
- magnitude: True

## 4 语法选择

- 选中:lollipop(棒棒糖图)
- 触发类型:lollipop
- FT 词表域:ranking, magnitude
- 词表候选:bubble, dot_strip, lollipop, mekko, ordered_bar, parallel_coordinates, radar, scenario_compare, slope, tornado
- FT 图型:Ordered bar, Ordered column, Ordered proportional symbol, Dot strip plot, Slope, Lollipop chart, Column, Bar, Paired column, Paired bar, Proportional stacked bar, Proportional symbol, Isotype (pictogram), Lollipop chart, Radar chart, Parallel coordinates
- 皮肤:house
- 外部参照:

## 5 产出

- spec.json
- chart.svg
