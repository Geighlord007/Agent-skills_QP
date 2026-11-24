# 运行报告:radar-coverage

## 1 页面简报

- 目的:能力盘点;对比当前、目标与同业中位
- 决策:确认 2027 年五项能力的提升目标
- 故事句:目标 2027 在成本、速度、质量、风险、扩展性五个维度均高于当前与同业中位;风险维度提升 20 分。
- 读者问题:
  - 五项能力当前与目标的差距是多少?
  - 哪些维度低于同业中位?

## 2 校验

| 检查 | 结果 | 明细 |
|---|---|---|
| 维度非空 | PASS | n=5 |
| 序列长度一致 | PASS | 逐项 |

## 3 关系识别

- magnitude: True

## 4 语法选择

- 选中:radar(雷达图)
- 触发类型:radar
- FT 词表域:magnitude
- 词表候选:bubble, lollipop, mekko, parallel_coordinates, radar, scenario_compare
- FT 图型:Column, Bar, Paired column, Paired bar, Proportional stacked bar, Proportional symbol, Isotype (pictogram), Lollipop chart, Radar chart, Parallel coordinates
- 皮肤:house
- 外部参照:

## 5 产出

- spec.json
- chart.svg
