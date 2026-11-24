# 运行报告:tornado-sensitivity

## 1 页面简报

- 目的:敏感性分析;找出对结果影响最大的变量
- 决策:优先校验影响最大的两个变量
- 故事句:Variable 6 的区间 4–36 偏离最大,Variable 1 的 19.5–20.5 几乎无影响。
- 读者问题:
  - 哪些变量影响最大?
  - 各变量的区间是多少?

## 2 校验

| 检查 | 结果 | 明细 |
|---|---|---|
| 标签与两序列长度一致 | PASS | n=6 |
| 中点非零 | PASS | mid=20 |
| 上下界不相等 | PASS | 逐项 |

## 3 关系识别

- ranking: True
- deviation: True

## 4 语法选择

- 选中:tornado(龙卷风/双向排序条)
- 触发类型:tornado
- FT 词表域:ranking, deviation
- 词表候选:dot_strip, lollipop, ordered_bar, scenario_compare, slope, tornado, waterfall
- FT 图型:Ordered bar, Ordered column, Ordered proportional symbol, Dot strip plot, Slope, Lollipop chart, Diverging bar, Diverging stacked bar, Spine chart, Surplus/deficit filled line
- 皮肤:house
- 外部参照:vendor/The-Python-Graph-Gallery/content/posts/web-tornado-chart/index.md

## 5 产出

- spec.json
- chart.svg
