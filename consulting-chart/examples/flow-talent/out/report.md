# 运行报告:flow-talent

## 1 页面简报

- 目的:人才流动概览;识别主要来源与目的地
- 决策:在美国与英国补充招聘预算
- 故事句:印度流向美国 120 人,中国流向美国 90 人;英国流向美国 45 人、德国流向加拿大 30 人。
- 读者问题:
  - 主要流向是哪几条?
  - 哪些目的地吸收最多?

## 2 校验

| 检查 | 结果 | 明细 |
|---|---|---|
| 流向非空 | PASS | n=6 |
| 起讫可识别 | PASS | 异常 0 条 |

## 3 关系识别

- spatial: True
- flow: True

## 4 语法选择

- 选中:flow_map(流向地图)
- 触发类型:flow_map
- FT 词表域:spatial, flow
- 词表候选:choropleth, flow_map, heatmap, network, sankey
- FT 图型:Basic choropleth (rate/ratio), Proportional symbol (count/magnitde), Flow map, Contour map, Equalised cartogram, Scaled cartogram (value), Dot density, Heat map, Sankey (aka river plot), Waterfall, Chord, Network
- 皮肤:house
- 外部参照:

## 5 产出

- spec.json
- chart.svg
