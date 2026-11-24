# 运行报告:scenario-compare

## 1 页面简报

- 目的:战略情景评审;比较三种情景的收入、成本与利润
- 决策:选定进入详细测算的情景
- 故事句:Scenario 3 收入 132、EBITDA 27,均为最高;Scenario 2 的 EBITDA 与 Scenario 1 持平为 22,毛利增量被 OPEX 抵消。
- 读者问题:
  - 三种情景的收入与成本差多少?
  - 毛利率与 EBITDA 怎么变?
  - 哪个情景的增量被 OPEX 吃掉?

## 2 校验

| 检查 | 结果 | 明细 |
|---|---|---|
| 情景指标一致 | PASS | 3 个情景 |
| Scenario 1 毛利 = 收入 - 成本 | PASS | 115-56=59 |
| Scenario 2 毛利 = 收入 - 成本 | PASS | 125-60=65 |
| Scenario 3 毛利 = 收入 - 成本 | PASS | 132-64=68 |
| Scenario 1 EBITDA = 毛利 - OPEX | PASS | 59-37=22 |
| Scenario 2 EBITDA = 毛利 - OPEX | PASS | 65-43=22 |
| Scenario 3 EBITDA = 毛利 - OPEX | PASS | 68-41=27 |

## 3 关系识别

- scenarios: True

## 4 语法选择

- 选中:scenario_compare(情景对比(分组柱))
- 触发类型:scenarios
- FT 词表域:magnitude, deviation
- 词表候选:bubble, lollipop, mekko, parallel_coordinates, radar, scenario_compare, tornado, waterfall
- FT 图型:Column, Bar, Paired column, Paired bar, Proportional stacked bar, Proportional symbol, Isotype (pictogram), Lollipop chart, Radar chart, Parallel coordinates, Diverging bar, Diverging stacked bar, Spine chart, Surplus/deficit filled line
- 皮肤:house
- 外部参照:

## 5 产出

- spec.json
- chart.svg
