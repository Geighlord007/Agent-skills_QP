<!--
  合成生物行业周简报 · HTML 模板 v2（PAPER-INK EDITORIAL v1.0）
  填写规则：
  1) {{...}} 为占位符；结构与 class 不改（设计契约）
  2) 条形图宽度 = 数值 ÷ 该图最大值 × 100%（取整）；恰好一根 .subj（CLAY）= 编辑判断的主角
  3) 双语堆叠：中文行 + 紧随灰色英文行，一行内不中英混排
  4) 每条目必带 source 行；空栏目写「本期无」
  5) 写完后运行 node scripts/embed-images.mjs 本文件内联封面图
-->
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{{ISSUE_TITLE}}</title>
<style>
  /* 打包字体（latin 子集；生成后由 embed 脚本内联为 data URI。CJK 走系统栈不内嵌） */
  @font-face { font-family:"Newsreader"; font-style:normal; font-weight:400; src:url("assets/fonts/Newsreader-Regular.woff2") format("woff2"); }
  @font-face { font-family:"Newsreader"; font-style:italic; font-weight:400; src:url("assets/fonts/Newsreader-Italic.woff2") format("woff2"); }
  @font-face { font-family:"Schibsted Grotesk"; font-style:normal; font-weight:400; src:url("assets/fonts/SchibstedGrotesk-Regular.woff2") format("woff2"); }
  @font-face { font-family:"DM Mono"; font-style:normal; font-weight:400; src:url("assets/fonts/DMMono-Regular.woff2") format("woff2"); }
  :root {
    --paper:#F7F5EB; --bone:#EDEADB; --ink:#000000; --ink2:#3A3A38; --muted:#6B6B66;
    --rule:#000000; --rule-soft:#D8D3C4;
    --moss:#9EA617; --meadow:#617D24; --clay:#E05E3D; --rose:#C28775; --seed:#D1B594;
    --jpm-ink:#0B2A4A; --jpm-bronze:#8F5A39;
    --serif:"Newsreader","Georgia","Times New Roman","Songti SC","SimSun",serif;
    --sans:"Schibsted Grotesk","Segoe UI","Helvetica Neue","PingFang SC","Microsoft YaHei",sans-serif;
    --mono:"DM Mono","Consolas","SFMono-Regular",monospace;
  }
  * { box-sizing:border-box; margin:0; padding:0; border-radius:0 !important; font-weight:400; }
  body { background:var(--paper); color:var(--ink); font-family:var(--serif); line-height:1.8; padding:48px 20px; }
  .wrap { max-width:780px; margin:0 auto; }
  a { color:var(--ink); text-decoration:underline; text-underline-offset:2px; }

  /* ── 报头 ── */
  .kicker { font-family:var(--mono); font-size:11.5px; letter-spacing:.14em; text-transform:uppercase; color:var(--muted); margin-bottom:14px; }
  h1 { font-family:var(--serif); font-size:34px; line-height:1.3; letter-spacing:-.01em; }
  .title-en { font-family:var(--serif); font-style:italic; font-size:15px; color:var(--muted); margin-top:6px; }
  .headrule { border:none; border-top:1px solid var(--rule); opacity:.55; margin:18px 0; }
  .deck { font-family:var(--serif); font-style:italic; font-size:15.5px; color:var(--ink2); margin-bottom:8px; }
  .deck-en { font-family:var(--serif); font-style:italic; font-size:13px; color:var(--muted); margin-bottom:26px; }

  /* ── 封面图 ── */
  .cover-box { border:1px solid var(--ink); border-top:3px solid var(--clay); margin-bottom:8px; }
  .cover-box img { width:100%; display:block; }
  .cover-cap { font-family:var(--serif); font-style:italic; font-size:12.5px; color:var(--muted); margin:0 0 26px; }

  /* ── 英文摘要 ── */
  .abstract { background:var(--bone); padding:18px 22px; margin-bottom:28px; }
  .abstract .fl { margin-bottom:8px; }
  .abstract p { font-family:var(--serif); font-style:italic; font-size:13.5px; color:var(--ink2); line-height:1.75; }

  /* ── 微标签 ── */
  .fl { font-family:var(--mono); font-size:11.5px; letter-spacing:.14em; text-transform:uppercase; color:var(--muted); }

  /* ── KPI 带 ── */
  .kpis { display:flex; flex-wrap:wrap; background:var(--bone); margin-bottom:8px; }
  .kpi { flex:1 1 140px; padding:16px 18px; border-left:1px solid var(--rule-soft); }
  .kpi:first-child { border-left:none; }
  .kpi .n { font-family:var(--mono); font-size:30px; line-height:1.1; }
  .kpi .t { font-family:var(--mono); font-size:10.5px; letter-spacing:.12em; text-transform:uppercase; color:var(--muted); margin-top:6px; }
  .kpi .t-en { font-family:var(--serif); font-style:italic; font-size:11px; color:var(--muted); margin-top:2px; }
  .kpi-note { font-family:var(--serif); font-style:italic; font-size:12.5px; color:var(--muted); margin-bottom:30px; }

  /* ── 栏目 ── */
  section { margin-bottom:34px; }
  h2 { font-family:var(--serif); font-size:22px; margin:2px 0 2px; }
  .sec-en { font-family:var(--serif); font-style:italic; font-size:13px; color:var(--muted); margin-bottom:10px; }
  .sec-rule { border:none; border-top:1px solid var(--rule); opacity:.55; margin:0 0 16px; }

  /* ── 条目盒（左强调条） ── */
  .item { border:1px solid var(--ink); border-left:3px solid var(--muted); padding:16px 18px 14px; margin-bottom:14px; }
  .item.key { border-left-color:var(--clay); }
  .item.watch { border-left-color:var(--meadow); }
  .item.brief { border-left-color:var(--seed); }
  .chips { margin-bottom:8px; }
  .chip { display:inline-block; font-family:var(--mono); font-size:10px; letter-spacing:.12em; text-transform:uppercase; padding:2px 8px; margin-right:6px; color:var(--paper); background:var(--muted); }
  .chip.key { background:var(--clay); }
  .chip.watch { background:var(--meadow); }
  .chip.brief { background:var(--muted); }
  .chip.wl { background:var(--jpm-bronze); }
  .chip.reg { background:var(--jpm-ink); }
  .claim { font-family:var(--sans); font-size:16px; line-height:1.6; margin-bottom:4px; }
  .deck-en { font-family:var(--serif); font-style:italic; font-size:13px; color:var(--muted); line-height:1.6; margin-bottom:10px; }
  .field { margin-bottom:8px; font-family:var(--sans); font-size:14.5px; line-height:1.75; color:var(--ink2); }
  .field .fl { display:block; margin-bottom:2px; }
  .src { font-family:var(--mono); font-size:12px; color:var(--muted); margin-top:10px; }
  .item ul.plain { list-style:none; }
  .item ul.plain li { padding:7px 0; border-bottom:1px dashed var(--rule-soft); font-family:var(--sans); font-size:14px; line-height:1.7; }
  .item ul.plain li:last-child { border-bottom:none; }

  /* ── 图表 ── */
  .chart-conc { font-family:var(--serif); font-size:15.5px; margin:14px 0 2px; }
  .chart-conc-en { font-family:var(--serif); font-style:italic; font-size:12.5px; color:var(--muted); margin-bottom:10px; }
  .chart .row { display:flex; align-items:center; gap:10px; margin:7px 0; }
  .chart .label { width:132px; flex:none; text-align:right; font-family:var(--mono); font-size:11.5px; color:var(--muted); }
  .chart .barwrap { flex:1; display:flex; align-items:center; }
  .chart .bar { height:22px; background:var(--meadow); flex:none; }
  .chart .bar.subj { background:var(--clay); }
  .chart .val { margin-left:8px; font-family:var(--mono); font-size:12.5px; color:var(--ink); }
  .chart-note { font-family:var(--serif); font-style:italic; font-size:12px; color:var(--muted); margin-top:8px; }

  /* ── 表格 ── */
  table { width:100%; border-collapse:collapse; margin:10px 0 6px; }
  th { background:var(--bone); font-family:var(--mono); font-size:10.5px; letter-spacing:.1em; text-transform:uppercase; color:var(--muted); font-weight:400; text-align:left; padding:8px; border-bottom:1px solid var(--ink); }
  td { font-family:var(--mono); font-size:12px; padding:9px 8px; border-bottom:1px solid var(--rule-soft); vertical-align:top; line-height:1.6; }
  td.sans { font-family:var(--sans); font-size:13px; }

  /* ── 页脚 ── */
  .notes { font-family:var(--serif); font-style:italic; font-size:13px; color:var(--ink2); line-height:1.8; }
  .src-line { font-family:var(--mono); font-size:12px; color:var(--muted); margin-top:14px; }
  .status-line { font-family:var(--mono); font-size:11.5px; letter-spacing:.08em; text-transform:uppercase; color:var(--muted); margin-top:10px; }
  @media print { body { background:#fff; padding:0; } .item, section { break-inside:avoid; } }
</style>
</head>
<body>
<div class="wrap">

  <header>
    <div class="kicker">{{KICKER}}</div>
    <h1>{{TITLE_CN}}</h1>
    <div class="title-en">{{TITLE_EN}}</div>
    <hr class="headrule">
    <p class="deck">{{DECK_ONELINER}}</p>
    <p class="deck-en">{{DECK_ONELINER_EN}}</p>
    <div class="cover-box"><img data-embed src="{{COVER_SRC}}" alt=""></div>
    <p class="cover-cap">{{COVER_CAPTION_EN}} — generated illustration (Seedream).</p>
  </header>

  <div class="abstract">
    <div class="fl">ENGLISH ABSTRACT</div>
    <p>{{ENGLISH_ABSTRACT}}</p>
  </div>

  <div class="fl">本期速览 · THIS ISSUE</div>
  <div class="kpis">
    <div class="kpi"><div class="n">{{KPI_1_N}}</div><div class="t">{{KPI_1_T}}</div><div class="t-en">{{KPI_1_EN}}</div></div>
    <div class="kpi"><div class="n">{{KPI_2_N}}</div><div class="t">{{KPI_2_T}}</div><div class="t-en">{{KPI_2_EN}}</div></div>
    <div class="kpi"><div class="n">{{KPI_3_N}}</div><div class="t">{{KPI_3_T}}</div><div class="t-en">{{KPI_3_EN}}</div></div>
    <div class="kpi"><div class="n">{{KPI_4_N}}</div><div class="t">{{KPI_4_T}}</div><div class="t-en">{{KPI_4_EN}}</div></div>
    <div class="kpi"><div class="n">{{KPI_5_N}}</div><div class="t">{{KPI_5_T}}</div><div class="t-en">{{KPI_5_EN}}</div></div>
  </div>
  <p class="kpi-note">{{KPI_NOTE}}</p>

  <section>
    <div class="kicker">{{S0_KICKER}}</div>
    <h2>{{S0_TITLE_CN}}</h2>
    <div class="sec-en">{{S0_TITLE_EN}}</div>
    <hr class="sec-rule">
    <p class="chart-conc">{{CH1_CONCLUSION_CN}}</p>
    <p class="chart-conc-en">{{CH1_CONCLUSION_EN}}</p>
    <div class="chart">{{CH1_ROWS}}</div>
    <p class="chart-note">{{CH1_NOTE}}</p>
  </section>

  <section>
    <div class="kicker">01 · FUNDING &amp; CAPITAL</div>
    <h2>融资动态</h2>
    <div class="sec-en">Funding rounds, grants and fund closes</div>
    <hr class="sec-rule">
    {{FUNDING_ITEMS}}
  </section>

  <section>
    <div class="kicker">02 · COMPANY &amp; COMMERCIAL</div>
    <h2>公司与商业化</h2>
    <div class="sec-en">Partnerships, capacity and go-to-market</div>
    <hr class="sec-rule">
    {{COMPANY_ITEMS}}
  </section>

  <section>
    <div class="kicker">03 · TECHNOLOGY &amp; R&amp;D</div>
    <h2>技术与研发</h2>
    <div class="sec-en">Technology signals worth watching</div>
    <hr class="sec-rule">
    {{TECH_ITEMS}}
  </section>

  <section>
    <div class="kicker">04 · REGULATORY</div>
    <h2>法规与监管</h2>
    <div class="sec-en">GRAS weekly filings, FDA letters and other lines</div>
    <hr class="sec-rule">
    <div class="fl">4.1 本周新增 GRAS 申报 · NEW GRAS FILINGS</div>
    <table>
      <tr><th>GRN</th><th>物质 · SUBSTANCE</th><th>申请人 · NOTIFIER</th><th>拟议用途 · INTENDED USE</th><th>状态</th><th>相关性</th></tr>
      {{GRAS_ROWS}}
    </table>
    <p class="chart-note">{{GRAS_BASELINE}}</p>
    <p class="chart-conc">{{CH2_CONCLUSION_CN}}</p>
    <p class="chart-conc-en">{{CH2_CONCLUSION_EN}}</p>
    <div class="chart">{{CH2_ROWS}}</div>
    <div class="field" style="margin-top:14px"><span class="fl">本期洞察 · INSIGHT</span>{{GRAS_INSIGHT}}</div>
    <div class="fl" style="margin-top:14px">4.2 FDA 回函 · NO-QUESTIONS LETTERS</div>
    {{GRAS_LETTERS}}
    <div class="fl" style="margin-top:14px">4.3 其他法规线 · OTHER LINES</div>
    {{REG_OTHER}}
  </section>

  <section>
    <div class="kicker">05 · VIEWPOINT</div>
    <h2>观点与延伸</h2>
    <div class="sec-en">Commentary and further reading</div>
    <hr class="sec-rule">
    {{VIEWPOINT_ITEMS}}
  </section>

  <footer>
    <p class="notes">{{METHOD_NOTES}}</p>
    <p class="src-line">{{SOURCE_LINE}}</p>
    <p class="status-line">{{STATUS_LINE}}</p>
  </footer>

</div>
</body>
</html>
