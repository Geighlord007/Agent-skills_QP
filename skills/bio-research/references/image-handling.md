# Image and Chart Handling

Charts are optional and generated only in **standard** or **deep** mode when real data supports them. Quick mode never generates charts.

## When to add a chart

Use a chart when:
- A comparison table has 4+ rows and a visual pattern helps interpretation.
- A timeline has 5+ events.
- Quantitative trends (yield, market size, dose-response) have 3+ data points.

Do not add a chart when:
- Data is sparse or inferred.
- The chart would duplicate a simple table.
- No reliable numbers are available.

## Chart types

| Type | Use case | Data format |
|------|----------|-------------|
| bar | Comparisons across categories | `{categories: [...], values: [...]}` |
| grouped_bar | Multi-scenario comparison | `{groups: [...], series: {name: [...]}}` |
| line | Trends over time | `{x: [...], y: [...]}` |
| timeline | Patent / regulatory / company events | `{events: [{year, label, source_id}]}` |
| mechanism | Simplified pathway diagram | Use text + arrows in markdown; SVG only if data exists |

## Generation workflow

1. Prepare JSON data in the report directory.
2. Run `python scripts/chart_generator.py --type <type> --data '<json>' --output output/charts/<name>.svg`.
3. Read the SVG file and base64-encode it.
4. Embed as HTML:
   ```html
   <div class="exhibit-label">Exhibit N: Title</div>
   <div class="chart-container">
     <img src="data:image/svg+xml;base64,{BASE64}" alt="Title" style="max-width:100%; height:auto;" />
   </div>
   <p class="chart-source">Source: [N]</p>
   ```
5. Reference the exhibit in the surrounding prose.

## No synthetic data

Every number in a chart must come from a cited source. Do not fill gaps with illustrative values.

## Error handling

If chart generation fails:
- Log the failure in `progress.md`.
- Insert an HTML comment: `<!-- Chart generation failed: reason -->`.
- Continue report assembly without the chart.
- Note the missing chart in `eval/quality_evaluation.md`.
