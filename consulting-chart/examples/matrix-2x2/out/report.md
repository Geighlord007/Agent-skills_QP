# 运行报告:matrix-2x2

## 1 页面简报

- 目的:杠杆优先级排序;按影响与可行性分区
- 决策:确定先执行与单独立项的杠杆
- 故事句:Prompt caching 与 Batch API 落在 Quick Wins;GPU utilization 影响最大但可行性低,属于 Big Bets。
- 读者问题:
  - 哪些杠杆可以先做?
  - 哪些需要单独立项?
  - 三类杠杆各自分布在哪?

## 2 校验

| 检查 | 结果 | 明细 |
|---|---|---|
| 条目坐标在 0-1 | PASS | n=9 |
| 分组在图例中 | PASS | 逐项 |

## 3 关系识别

- correlation: True

## 4 语法选择

- 选中:matrix_2x2(2×2 矩阵)
- 触发类型:matrix
- FT 词表域:correlation
- 词表候选:bubble, heatmap, matrix_2x2, scatter
- FT 图型:Scatterplot, Line + Column, Connected scatterplot, Bubble, XY heatmap
- 皮肤:house
- 外部参照:

## 5 产出

- spec.json
- chart.svg
