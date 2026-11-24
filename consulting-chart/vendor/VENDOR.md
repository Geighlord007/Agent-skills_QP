# Vendor: 外部参考来源与许可证记录

本技能**不随技能目录分发外部大型仓库克隆**(已移除原 `chart-doctor/`、`EconomistStyle/`、`The-Python-Graph-Gallery/` 工作树与嵌套 `.git/` 目录)。所有运行时所需的词表与皮肤均已提炼并固化到 `references/`,仅保留 0.8 MB 世界地图底图供地图渲染器读取。

下表记录上游仓库 URL、参考提交号与许可证,便于溯源或按需重新克隆:

| 上游项目 | 仓库 / 来源 | 参考提交 / 日期 | 许可证 | 已固化产物 / 运行时用途 |
|---|---|---|---|---|
| Financial-Times/chart-doctor | https://github.com/Financial-Times/chart-doctor | `befb9cba2184` (2024-03-12) | MIT | `references/vocab-index.json`(FT visual-vocabulary 八大问题域与候选图型,运行时参与选型) |
| nickteff/EconomistStyle | https://github.com/nickteff/EconomistStyle | `65156e64dca4` (2026-09-10) | MIT | `references/skins/economist.json`(提取自 `theeconomist.mplstyle` 的字体与蓝红配色) |
| holtzy/The-Python-Graph-Gallery | https://github.com/holtzy/The-Python-Graph-Gallery | `c5af97086340` (2026-10-14) | 0BSD | 开发期图型配方参考(如 tornado 配方位于上游 `content/posts/web-tornado-chart/index.md`),运行时不依赖 |
| Natural Earth 110m Admin 0 Countries | https://github.com/nvkelso/natural-earth-vector (`ne_110m_admin_0_countries.geojson`) | 2026-10-20 | Public Domain | `assets/geo/world-110m.geojson`(0.8 MB, 177 国),供 `scripts/maps.py` 绘制等值区域图与流向地图 |

## 按需重新获取参考仓库

如需在开发新图型时查阅上游配方或原始样式,可在技能目录之外的临时工作区执行浅克隆:

```bash
git clone --depth 1 https://github.com/Financial-Times/chart-doctor.git
git clone --depth 1 https://github.com/nickteff/EconomistStyle.git
git clone --depth 1 https://github.com/holtzy/The-Python-Graph-Gallery.git
```

引用或再分发衍生内容时请遵守上游各自的 MIT / 0BSD / Public Domain 许可条款。
