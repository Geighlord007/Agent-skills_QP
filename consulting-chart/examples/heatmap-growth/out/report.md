# 运行报告:heatmap-growth

## 1 页面简报

- 目的:区域表现复盘;四区域 × 四季度增速扫描
- 决策:把资源向 West 倾斜,Eastern 继续修复
- 故事句:West 四个季度均为正且 Q3 最高 14.2%;East 从 Q1 的 -3.1% 逐季转正到 Q4 的 2.4%。
- 读者问题:
  - 哪个区域与季度最强?
  - 哪个区域最弱?
  - East 是否在修复?

## 2 校验

| 检查 | 结果 | 明细 |
|---|---|---|
| 矩阵形状一致 | PASS | 4x4 |

## 3 关系识别

- heatmap: True

## 4 语法选择

- 选中:heatmap(热力矩阵)
- 触发类型:heatmap
- FT 词表域:correlation, spatial
- 词表候选:bubble, choropleth, flow_map, heatmap, matrix_2x2, scatter
- FT 图型:Scatterplot, Line + Column, Connected scatterplot, Bubble, XY heatmap, Basic choropleth (rate/ratio), Proportional symbol (count/magnitde), Flow map, Contour map, Equalised cartogram, Scaled cartogram (value), Dot density, Heat map
- 皮肤:house
- 外部参照:

## 5 产出

- spec.json
- chart.svg
