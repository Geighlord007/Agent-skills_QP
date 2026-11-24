# 运行报告:ai-market-2025-2026

## 1 页面简报

- 目的:判断模型调用量正在向哪些价格带、厂商与地区迁移
- 决策:确定模型采购与路由策略:是否为低价开源模型保留多供应商通道
- 故事句:Anthropic 的 token 份额从 42% 降到 5%,DeepSeek 从 7% 升到 24%,中国开源合计从 11% 升到 46%;亚洲调用占比从 13% 升到 58%;2026 Q3 的最大调用量集中在每百万 token 1 美元以下的低价带。
- 读者问题:
  - 哪家厂商的调用量份额变化最大?
  - 价格带与调用量是什么关系?
  - 地区结构如何变化?

## 2 校验

| 检查 | 结果 | 明细 |
|---|---|---|
| 季度非空 | PASS | n=7 |
| Anthropic 与季度数一致 | PASS | n=7 |
| OpenAI 与季度数一致 | PASS | n=7 |
| Google 与季度数一致 | PASS | n=7 |
| DeepSeek 与季度数一致 | PASS | n=7 |
| 中国开源其他 与季度数一致 | PASS | n=7 |
| xAI 与季度数一致 | PASS | n=7 |
| 其他 与季度数一致 | PASS | n=7 |
| 每季度份额合计约 100 | PASS | 100, 100, 100, 100, 100, 100, 100 |
| 价格快照含价格与份额 | PASS | 逐项 |
| 地区分期与份额长度一致 | PASS | n=3 |

## 3 关系识别

- change-over-time: True
- part-to-whole: True
- correlation: True

## 4 语法选择

- 选中:ai_market_map(AI 市场三面板(份额/价格/地区))
- 触发类型:ai_market_map
- FT 词表域:change-over-time, part-to-whole, correlation
- 词表候选:annotated_narrative, bubble, combo, composition, donut, funnel, gantt, heatmap, issue_tree, matrix_2x2, mekko, partition_bridge, pie, roadmap, scatter, slope, small_multiples, treemap, waffle, waterfall
- FT 图型:Line, Column, Line + column, Stock price, Slope, Area chart, Fan chart (projection), Connected scatterplot, Calendar heatmap, Priestley timeline, Circle timeline, Seismogram, Stacked column, Proportional stacked bar, Pie, Donut, Treemap, Voronoi, Arc, Gridplot, Venn, Waterfall, Scatterplot, Line + Column, Connected scatterplot, Bubble, XY heatmap
- 皮肤:house
- 外部参照:

## 5 产出

- spec.json
- chart.svg
