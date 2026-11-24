# 运行报告:dot-strip-approval

## 1 页面简报

- 目的:流程效率复盘;比较三个部门的审批周期分布
- 决策:优先压缩 Finance 的长尾合同
- 故事句:Finance 的审批周期中位数 29 天,比 Ops 的 14 天长一倍;Sales 的跨度最大(12–31 天)。
- 读者问题:
  - 各部门的中位周期是多少?
  - 哪个部门的分布最分散?

## 2 校验

| 检查 | 结果 | 明细 |
|---|---|---|
| 每个分类至少一个值 | PASS | 3 类 |
| 数值非负 | PASS | 逐项 |

## 3 关系识别

- distribution: True
- ranking: True

## 4 语法选择

- 选中:dot_strip(点带图)
- 触发类型:dot_strip
- FT 词表域:ranking, distribution
- 词表候选:boxplot, dot_strip, histogram, lollipop, ordered_bar, population_pyramid, slope, tornado, violin
- FT 图型:Ordered bar, Ordered column, Ordered proportional symbol, Dot strip plot, Slope, Lollipop chart, Histogram, Boxplot, Violin plot, Population pyramid, Dot strip plot, Dot plot, Barcode plot, Cumulative curve
- 皮肤:house
- 外部参照:

## 5 产出

- spec.json
- chart.svg
