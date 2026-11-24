# 运行报告:launch-gantt

## 1 页面简报

- 目的:发布前周会;检查各工作流与里程碑状态
- 决策:确认 10 月上线窗口是否保持
- 故事句:六个工作流中两个已完成、两个进行中、两个未开始;代码冻结与上线两个里程碑保持在计划内。
- 读者问题:
  - 各工作流的时间范围是什么?
  - 今天处于哪个阶段?
  - 哪些任务已完成、在办、未开始?
  - 关键里程碑是否落在计划内?

## 2 校验

| 检查 | 结果 | 明细 |
|---|---|---|
| 需求评审 起止顺序 | PASS | [0, 0.05] -> [0, 0.95] |
| 产品设计 起止顺序 | PASS | [0, 0.55] -> [1, 0.45] |
| 平台开发 起止顺序 | PASS | [1, 0.55] -> [3, 0.1] |
| 集成与测试 起止顺序 | PASS | [1, 0.75] -> [3, 0.2] |
| 发布就绪 起止顺序 | PASS | [3, 0.3] -> [3, 0.65] |
| 采用与优化 起止顺序 | PASS | [3, 0.7] -> [4, 0.75] |

## 3 关系识别

- schedule: True

## 4 语法选择

- 选中:gantt(阶段甘特/路线图)
- 触发类型:schedule
- FT 词表域:change-over-time
- 词表候选:annotated_narrative, combo, gantt, partition_bridge, roadmap, slope, small_multiples, waterfall
- FT 图型:Line, Column, Line + column, Stock price, Slope, Area chart, Fan chart (projection), Connected scatterplot, Calendar heatmap, Priestley timeline, Circle timeline, Seismogram
- 皮肤:house
- 外部参照:

## 5 产出

- spec.json
- chart.svg
