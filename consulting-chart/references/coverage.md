# 语法覆盖清单

> 由 `scripts/coverage.py` 生成,请勿手工修改。

- 总计:48 条
- 已实现:31 条
- planned:17 条

## 已实现

| id | 名称 | trigger | FT 域 | 渲染器 |
|---|---|---|---|---|
| `partition_bridge` | 桥接 + 分层构成 + 浮空划分 | `partition` | part-to-whole, change-over-time | `chartlib.render_partition_bridge` |
| `waterfall` | 顺序桥接(含小计、分段与方差括线) | `bridge` | deviation, change-over-time, part-to-whole | `renderers.render_waterfall` |
| `combo` | 堆叠柱 + 同比折线 + 趋势带 | `time_series` | change-over-time, part-to-whole | `renderers.render_combo` |
| `gantt` | 阶段甘特/路线图 | `schedule` | change-over-time | `renderers.render_gantt` |
| `composition` | 分层构成柱(多时点) | `composition` | part-to-whole | `renderers.render_composition` |
| `tornado` | 龙卷风/双向排序条 | `tornado` | ranking, deviation | `renderers.render_tornado` |
| `scenario_compare` | 情景对比(分组柱) | `scenarios` | magnitude, deviation | `renderers.render_scenario_compare` |
| `dot_strip` | 点带图 | `dot_strip` | ranking, distribution | `renderers.render_dot_strip` |
| `slope` | 斜率图 | `slope` | ranking, change-over-time | `renderers.render_slope` |
| `lollipop` | 棒棒糖图 | `lollipop` | ranking, magnitude | `renderers.render_lollipop` |
| `heatmap` | 热力矩阵 | `heatmap` | correlation, spatial | `renderers.render_heatmap` |
| `matrix_2x2` | 2×2 矩阵 | `matrix` | correlation | `renderers.render_matrix` |
| `waffle` | 华夫格 | `waffle` | part-to-whole | `renderers.render_waffle` |
| `waffle_group` | 华夫小倍数(多面板) | `grid_panels` | part-to-whole | `renderers.render_waffle_group` |
| `mekko` | 马赛克/变宽堆叠柱 | `mekko` | part-to-whole, magnitude | `renderers.render_mekko` |
| `funnel` | 漏斗/金字塔 | `funnel` | part-to-whole | `renderers.render_funnel` |
| `radar` | 雷达图 | `radar` | magnitude | `renderers.render_radar` |
| `choropleth` | 等值区域图 | `choropleth` | spatial | `renderers.render_choropleth` |
| `flow_map` | 流向地图 | `flow_map` | spatial, flow | `renderers.render_flow_map` |
| `stacked_time_series` | 堆叠时序(含累计增速) | `stacked_time_series` | change-over-time, part-to-whole | `renderers_extra.render_stacked_time_series` |
| `bar_pill` | 柱 + 第二指标药丸行 | `bar_pill` | change-over-time, deviation | `renderers_extra.render_bar_pill` |
| `line_forecast` | 预测折线(实绩/预测分界) | `line_forecast` | change-over-time | `renderers_extra.render_line_forecast` |
| `mosaic_compare` | 马赛克对比(等宽两列) | `mosaic_compare` | part-to-whole | `renderers_extra.render_mosaic_compare` |
| `timeline_matrix` | 事件时间线矩阵 | `timeline_matrix` | change-over-time | `renderers_extra.render_timeline_matrix` |
| `maturity_table` | 成熟度阶梯表 | `maturity_table` | part-to-whole | `renderers_extra.render_maturity_table` |
| `target_dots` | 汇总条与子组点阵 | `target_dots` | ranking, distribution, deviation | `renderers_extra.render_target_dots` |
| `journey_stack` | 采用阶段堆叠条(变长) | `journey_stack` | part-to-whole, ranking | `renderers_extra.render_journey_stack` |
| `bar_future` | 现状条与未来刻度 | `bar_future` | deviation, change-over-time | `renderers_extra.render_bar_future` |
| `quadrant_matrix` | 影响-可行性矩阵 | `quadrant_matrix` | correlation, ranking | `renderers_extra.render_quadrant_matrix` |
| `growth_margin` | 营收增长与利润率双面板 | `growth_margin` | change-over-time, part-to-whole, deviation | `renderers_extra.render_growth_margin` |
| `ai_market_map` | AI 市场三面板(份额/价格/地区) | `ai_market_map` | change-over-time, part-to-whole, correlation | `renderers_extra.render_ai_market` |

## planned

| id | 名称 | trigger | FT 域 |
|---|---|---|---|
| `ordered_bar` | 排序条形 | `ranking` | ranking |
| `histogram` | 直方图 | `distribution` | distribution |
| `boxplot` | 箱线图 | `boxplot` | distribution |
| `violin` | 小提琴图 | `violin` | distribution |
| `population_pyramid` | 人口金字塔 | `pyramid` | distribution |
| `scatter` | 散点图 | `scatter` | correlation |
| `bubble` | 气泡图 | `bubble` | correlation, magnitude |
| `pie` | 饼图 | `pie` | part-to-whole |
| `donut` | 环形图 | `donut` | part-to-whole |
| `treemap` | 树图 | `treemap` | part-to-whole |
| `sankey` | 桑基图 | `sankey` | flow |
| `network` | 网络图 | `network` | flow |
| `parallel_coordinates` | 平行坐标 | `parallel` | magnitude |
| `small_multiples` | 小倍数图 | `small_multiples` | change-over-time |
| `issue_tree` | 议题树 | `issue_tree` | part-to-whole |
| `roadmap` | 转型路线图 | `roadmap` | change-over-time |
| `annotated_narrative` | 叙事标注图 | `narrative` | change-over-time |
