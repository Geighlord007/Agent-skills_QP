# 运行报告:choropleth-ai

## 1 页面简报

- 目的:全球采纳率概览;识别领先与落后市场
- 决策:优先在美国、新加坡与北欧加深投入
- 故事句:美国 42%、荷兰 40%、中国 38% 领先;墨西哥 21%、南非 22% 仍在 20% 出头。
- 读者问题:
  - 哪些国家采纳率最高?
  - 哪些国家仍在 20% 附近?

## 2 校验

| 检查 | 结果 | 明细 |
|---|---|---|
| 有数值 | PASS | n=14 |
| 国家代码可识别 | PASS | 全部匹配 |

## 3 关系识别

- spatial: True

## 4 语法选择

- 选中:choropleth(等值区域图)
- 触发类型:choropleth
- FT 词表域:spatial
- 词表候选:choropleth, flow_map, heatmap
- FT 图型:Basic choropleth (rate/ratio), Proportional symbol (count/magnitde), Flow map, Contour map, Equalised cartogram, Scaled cartogram (value), Dot density, Heat map
- 皮肤:house
- 外部参照:

## 5 产出

- spec.json
- chart.svg
