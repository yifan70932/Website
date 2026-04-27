"""HTML report assembly for the watchlist tool."""

from __future__ import annotations
from datetime import datetime
import numpy as np
import pandas as pd

from . import themes
from .core import (TRADING_DAYS, BENCHMARK, RISK_FREE_DEFAULT,
                   sharpe, sortino, max_drawdown, max_drawdown_duration,
                   beta, var_95, cvar_95,
                   momentum_window, volatility_window, correlation_to_benchmark)
from .visualizations import (
    fig_ticker_dashboard, fig_normalized_returns, fig_risk_return_scatter,
    fig_drawdown_comparison, fig_correlation_clustered, fig_factor_scores,
    fig_return_dispersion, fig_efficient_frontier, fig_strategy_comparison,
)
from .literature import LITERATURE


# ---------- Plain-language explanations ----------

EXPLANATIONS = {
    "summary": (
        "<strong>What this is:</strong> A condensed read of the dispersion across "
        "your watchlist over the lookback window — best/worst performer, most/least "
        "volatile name, and how clustered the universe is in correlation terms.<br><br>"
        "<strong>What it isn't:</strong> Stock picks. The summary describes statistical "
        "properties of recent returns, not predictions about future performance."
    ),
    "screener": (
        "<strong>The headline section.</strong> Sortable cross-sectional metrics for every "
        "ticker in the universe over the lookback window. Click a column header to sort "
        "by it.<br><br>"
        "<strong>Annualized return / volatility / Sharpe</strong> are computed from daily "
        "log returns. <strong>Sortino</strong> only penalizes downside deviation. "
        "<strong>Calmar</strong> is annual return ÷ |max DD| — rewards consistency. "
        "<strong>Beta</strong> is regression slope vs SPY. <strong>Corr SPY</strong> is "
        "correlation with market. <strong>VaR/CVaR-95</strong> are historical 5%-tail "
        "measures of single-day loss.<br><br>"
        "<strong>Reading caveat:</strong> These are descriptive, not predictive. A name "
        "with high recent Sharpe is not necessarily a good prospect — it might just be "
        "lucky, near a high, or have benefited from a regime that's about to end."
    ),
    "factor_scores": (
        "<strong>What you're looking at:</strong> The Quality / Value / Momentum / Low-Vol "
        "(QVM+L) framework as practiced by MSCI, S&amp;P, AQR, and modern multi-factor screeners. "
        "Each factor is computed for each ticker, then converted to a percentile rank within "
        "the watchlist universe. The diamond marker is the equal-weighted composite of the "
        "four factors.<br><br>"
        "<strong>How each factor is built:</strong><br>"
        "<strong>Momentum</strong> — composite of 12-month-excluding-most-recent-month "
        "(Jegadeesh &amp; Titman 1993), 6-month, and 3-month price returns. Higher = better.<br>"
        "<strong>Low Volatility</strong> — 12-month annualized return volatility. "
        "Lower = better (Frazzini &amp; Pedersen 2014).<br>"
        "<strong>Quality</strong> — composite of ROE, profit margin, debt/equity, and "
        "max-drawdown stability (Asness, Frazzini &amp; Pedersen 2019).<br>"
        "<strong>Value</strong> — composite of P/E, P/B, EV/EBITDA. Lower multiples = better.<br><br>"
        "<strong>Important caveats:</strong> (1) ETFs lack standalone fundamentals, so their "
        "Quality and Value scores are unreliable — focus on Momentum and Low-Vol for them. "
        "(2) Factor returns are cyclical (MSCI 2024); momentum has crashed badly in 2009 and "
        "elsewhere. (3) Composite scores rank within <em>this</em> universe, not the broader "
        "market — a 90 here just means &quot;best of these 18,&quot; not a strong absolute signal. "
        "(4) Single-sample-period rankings are noisy estimates."
    ),
    "normalized_returns": (
        "<strong>The chart:</strong> Each name's cumulative total return rebased to 100 at "
        "the start of the lookback window. End-of-line values let you read the relative "
        "performance ranking directly. A line at 130 means &quot;up 30% over the window.&quot;<br><br>"
        "Watch for: the spread between best and worst performer (dispersion), whether the "
        "leaders changed mid-period (regime), and how the ETFs (smooth, low-amplitude lines) "
        "compare to single names (jagged, high-amplitude)."
    ),
    "risk_return": (
        "<strong>The chart:</strong> Each ticker's annualized volatility (x) vs. annualized "
        "return (y) over the window. Dotted lines are <em>iso-Sharpe</em> contours — "
        "any name on the same iso-line earned the same Sharpe ratio.<br><br>"
        "<strong>Reading the chart:</strong> Names <em>above</em> the SR=1.0 line earned "
        "more than 1× their volatility in excess return — generally considered the threshold "
        "for &quot;good&quot; risk-adjusted performance over a multi-year window. Names below "
        "SR=0.5 earned mediocre risk-adjusted returns.<br><br>"
        "<strong>Important:</strong> A point above SR=2 over a 2-year window is rarely "
        "sustained out-of-sample. Mean reversion in factor performance is well documented "
        "(MSCI 2024)."
    ),
    "drawdown": (
        "<strong>The chart:</strong> Underwater curves for every name. A line at -30% "
        "means the price was 30% below its running peak on that date.<br><br>"
        "<strong>Worth noting:</strong> Drawdowns matter more than volatility in practice. "
        "A 50% drawdown requires a 100% recovery to break even. Single names can spend "
        "years underwater; broad ETFs typically recover faster. The deepest and "
        "longest-duration drawdown line should not be confused with the most volatile name "
        "— these are different things, and high vol with low drawdown happens when "
        "volatility is symmetric (frequent up-days as well as down-days)."
    ),
    "correlation": (
        "<strong>The chart:</strong> Correlation matrix of daily log returns, with rows "
        "and columns reordered via hierarchical clustering so that highly-correlated "
        "names appear adjacent.<br><br>"
        "<strong>What to look for:</strong> Square-shaped clusters of red along the "
        "diagonal indicate groups that move together — likely a sector or factor exposure. "
        "Names that are correlated with everything (whole row red) provide little "
        "diversification. Names that have a row of mostly-near-zero values are the most "
        "diversifying additions.<br><br>"
        "<strong>Caveat:</strong> Correlations are unstable across regimes. The 2020 "
        "stress period saw correlations spike toward +1 across most equity sectors — "
        "exactly when diversification was most needed."
    ),
    "optimization": (
        "<strong>The chart:</strong> The long-only mean-variance efficient frontier "
        "(Markowitz 1952) computed across your full watchlist. Each gray dot is one "
        "ticker; the green diamond is the global-minimum-variance combination; the blue "
        "triangle is the maximum-Sharpe (tangency) combination. Equal-weight and risk-parity "
        "reference portfolios are also shown.<br><br>"
        "<strong>The capital market line</strong> (dotted) connects the risk-free rate "
        "to the tangency portfolio. Combining cash with tangency gives you any point along "
        "this line. Anything below it is dominated.<br><br>"
        "<strong>Important warning:</strong> Mean-variance optimization is notoriously "
        "fragile. Small changes in expected return inputs produce large swings in optimal "
        "weights (Michaud 1989). Tangency weights are <em>diagnostic</em>, not "
        "<em>actionable</em> — they show you what the in-sample data implies, but "
        "out-of-sample performance is typically much worse than the chart suggests "
        "(DeMiguel, Garlappi &amp; Uppal 2009)."
    ),
    "strategies": (
        "<strong>What you're looking at:</strong> A backtest comparing six rule-based "
        "strategies on the watchlist universe. Each curve shows what $10,000 grew to "
        "under each strategy with realistic 10 bp transaction costs.<br><br>"
        "<strong>Strategies:</strong> "
        "<strong>Buy &amp; Hold</strong> equal-weights all names on day 0 and never "
        "rebalances. <strong>Equal Weight</strong> rebalances back to 1/N monthly. "
        "<strong>Risk Parity</strong> weights inversely to volatility "
        "(Maillard et al. 2010). <strong>SMA Crossover</strong> holds names where "
        "50-day SMA &gt; 200-day. <strong>Momentum 12-1</strong> holds the top half by "
        "12-1 trailing return (Jegadeesh &amp; Titman 1993). <strong>Mean Reversion</strong> "
        "buys Bollinger-band-low names, exits at the high.<br><br>"
        "<strong>What to learn:</strong> If buy-and-hold beats the rule-based strategies "
        "(it usually does on a small US-equity universe like this one), that's empirical "
        "support for what Bogle, Fama-French, and SPIVA have argued for decades — costs "
        "and turnover destroy most rule-based edges in liquid US equities."
    ),
    "strategy_caveats": (
        "<strong>Read this before drawing conclusions.</strong> The biggest biases that "
        "make most retail backtests misleading:<br><br>"
        "<strong>1. Survivorship bias (NOT fixed).</strong> yfinance only knows "
        "currently-listed tickers. Backtesting on today's universe misses companies that "
        "went bankrupt, merged out, or got delisted — all of which biases historical "
        "returns upward.<br><br>"
        "<strong>2. Tiny universe.</strong> Cross-sectional strategies (momentum, "
        "low-vol screening) work properly on universes of 100-500+ names. With 18 names "
        "you're at the edge of usefulness; results are noisy.<br><br>"
        "<strong>3. Single time period.</strong> The result you see is one realization "
        "of history. The same strategy run on a different period (1970-1985 vs. "
        "2010-2025) often produces very different results. Watch the entire MSCI factor "
        "report (2024) — they document <em>10 years</em> of underperformance for some "
        "factor styles vs. the cap-weighted index.<br><br>"
        "<strong>4. Look-ahead bias (FIXED).</strong> The backtester shifts strategy "
        "signals by 1 day before applying them, so you trade on yesterday's close, not "
        "tomorrow's information.<br><br>"
        "<strong>5. Transaction costs (partially modeled).</strong> 10 bps round-trip "
        "captures commissions and a typical bid-ask spread for liquid US equities. It "
        "doesn't model market impact, taxes, or short-borrow costs.<br><br>"
        "<strong>6. Multiple-testing.</strong> Try 50 strategies and one will look "
        "great by chance. Harvey, Liu &amp; Zhu (2016) argue t&gt;3.0 is the right "
        "threshold for &quot;real&quot; signal under realistic multiple-testing assumptions."
    ),
    "news": (
        "<strong>What it is:</strong> Recent ticker news from Yahoo Finance RSS, sorted "
        "newest-first across the entire watchlist (not grouped per-ticker). The ticker "
        "tag in front of each headline tells you which name it concerns.<br><br>"
        "<strong>How to read it:</strong> Markets typically price in publicly known "
        "information quickly (Fama 1970), so a headline you see in the morning has often "
        "already moved the price. Use this section for context — earnings, regulatory "
        "developments, executive changes — rather than as a basis for buy/sell decisions. "
        "For anything that matters financially, read the actual SEC filings via "
        "<code>sec.gov/edgar</code>."
    ),
    "ticker_dashboards": (
        "<strong>Per-ticker drilldown.</strong> Click any name to expand its full "
        "technical chart: price with 50/200-day SMAs and Bollinger bands, RSI(14), MACD.<br><br>"
        "<strong>Honest warning:</strong> Technical indicators in liquid US equities have "
        "weak out-of-sample predictive power. RSI &gt; 70 doesn't reliably mean &quot;will "
        "sell off&quot;; SMA crossovers don't reliably mean &quot;will trend.&quot; Use "
        "these as descriptive context, not as buy/sell triggers (Bajgrowicz &amp; Scaillet 2012)."
    ),
}


# ---------- CSS ----------

def make_css():
    c = themes.COLORS
    return f"""<style>
  :root {{
    --bg:{c['bg']}; --panel:{c['panel']}; --panel-alt:{c['panel_alt']};
    --text:{c['text']}; --text-strong:{c['text_strong']}; --muted:{c['muted']};
    --border:{c['border']}; --accent:{c['accent']}; --accent2:{c['accent2']};
    --up:{c['up']}; --down:{c['down']}; --warn:{c['warn']};
    --code-bg:{c['code_bg']};
  }}
  * {{ box-sizing:border-box; }}
  body {{ margin:0; padding:32px 24px; background:var(--bg); color:var(--text);
    font-family:'Inter',-apple-system,BlinkMacSystemFont,sans-serif; line-height:1.55; }}
  .container {{ max-width:1700px; margin:0 auto; }}
  .explain, .caveats {{ max-width:1100px; }}
  header {{ background:{c['header_grad']}; color:white; padding:36px 32px;
    border-radius:16px; margin-bottom:24px; box-shadow:0 8px 24px rgba(0,0,0,0.30); }}
  header h1 {{ margin:0 0 6px; font-size:28px; font-weight:700; color:white; }}
  header p {{ margin:0; opacity:0.92; font-size:14px; color:white; }}
  nav {{ background:var(--panel); padding:14px 22px; border-radius:10px;
    margin-bottom:20px; border:1px solid var(--border); display:flex;
    flex-wrap:wrap; gap:8px; font-size:13px; position:sticky; top:8px;
    z-index:50; backdrop-filter:blur(8px); }}
  nav a {{ color:var(--accent); text-decoration:none; padding:6px 12px;
    border-radius:6px; transition:background 0.15s; }}
  nav a:hover {{ background:var(--panel-alt); }}
  .panel {{ background:var(--panel); border-radius:12px; padding:24px;
    margin-bottom:20px; border:1px solid var(--border);
    box-shadow:0 1px 3px rgba(0,0,0,0.15); scroll-margin-top:80px; }}
  .panel h2 {{ margin:0 0 16px; font-size:18px; font-weight:600;
    color:var(--text-strong); padding-bottom:12px; border-bottom:1px solid var(--border); }}
  .panel h3 {{ font-size:15px; margin:18px 0 10px; color:var(--text-strong); }}
  .grid-2 {{ display:grid; grid-template-columns:1fr 1fr; gap:20px; }}
  @media (max-width:900px) {{ .grid-2 {{ grid-template-columns:1fr; }} }}
  .explain {{ background:var(--panel-alt); border-left:3px solid var(--accent);
    padding:14px 18px; border-radius:6px; margin:14px 0; font-size:13.5px;
    color:var(--text); line-height:1.75; }}
  .explain em {{ color:var(--accent2); font-style:italic; }}
  .explain strong {{ color:var(--text-strong); }}
  .caveats {{ background:var(--panel-alt); border-left:3px solid var(--warn);
    padding:14px 18px; border-radius:6px; margin:14px 0; font-size:13px;
    color:var(--text); line-height:1.75; }}
  .caveats strong {{ color:var(--warn); }}
  table {{ width:100%; border-collapse:collapse; font-size:13px; }}
  th, td {{ text-align:right; padding:8px 10px;
           border-bottom:1px solid var(--border); color:var(--text); }}
  th:first-child, td:first-child {{ text-align:left; font-weight:500; }}
  th {{ background:var(--panel-alt); font-weight:600; color:var(--muted);
    text-transform:uppercase; font-size:11px; letter-spacing:0.04em;
    cursor:pointer; user-select:none; }}
  th:hover {{ color:var(--text-strong); }}
  th.sorted-asc::after {{ content:" ▲"; color:var(--accent); }}
  th.sorted-desc::after {{ content:" ▼"; color:var(--accent); }}
  tr:hover td {{ background:var(--panel-alt); }}
  .pos {{ color:var(--up); font-weight:500; }}
  .neg {{ color:var(--down); font-weight:500; }}
  .flag {{ display:inline-block; padding:4px 10px; margin:3px 4px 3px 0;
    border-radius:999px; font-size:12px; font-weight:500; }}
  .flag.up {{ background:rgba(87,171,90,0.18); color:var(--up); }}
  .flag.down {{ background:rgba(229,83,75,0.18); color:var(--down); }}
  .flag.neutral {{ background:var(--panel-alt); color:var(--muted); }}
  details {{ margin-bottom:10px; }}
  details summary {{ cursor:pointer; padding:14px 18px; background:var(--panel-alt);
    border-radius:8px; font-weight:600; font-size:14px; user-select:none;
    border:1px solid var(--border); color:var(--text-strong); }}
  details summary:hover {{ background:var(--border); }}
  details[open] summary {{ border-bottom-left-radius:0; border-bottom-right-radius:0; }}
  details .body {{ padding:16px; border:1px solid var(--border); border-top:none;
    border-bottom-left-radius:8px; border-bottom-right-radius:8px; background:var(--panel); }}
  .disclaimer {{ background:rgba(218,170,63,0.15); border-left:4px solid var(--warn);
    padding:16px 20px; border-radius:8px; margin-bottom:24px; font-size:13px; color:var(--text); }}
  .disclaimer strong {{ color:var(--warn); }}
  .lit-section {{ margin-bottom:22px; }}
  .lit-section h3 {{ color:var(--accent2); margin-bottom:6px; font-size:14px; }}
  .lit-section .topic-summary {{ font-size:13px; color:var(--muted);
    margin-bottom:12px; font-style:italic; }}
  .lit-paper {{ padding:12px 14px; margin-bottom:8px; background:var(--panel-alt);
    border-left:3px solid var(--accent); border-radius:6px; font-size:13px; }}
  .lit-paper .cite {{ font-style:italic; color:var(--text); }}
  .lit-paper .note {{ color:var(--muted); margin-top:4px; font-size:12px; }}
  .lit-paper a {{ color:var(--accent); text-decoration:none; font-size:12px; }}
  .small-note {{ font-size:11px; color:var(--muted); margin-top:6px; font-style:italic; }}
  .stat-grid {{ display:grid; grid-template-columns:repeat(auto-fit, minmax(180px, 1fr));
    gap:12px; margin:14px 0; }}
  .stat-card {{ padding:14px 16px; background:var(--panel-alt);
    border-radius:8px; border:1px solid var(--border); }}
  .stat-card .label {{ font-size:11px; color:var(--muted);
    text-transform:uppercase; letter-spacing:0.05em; }}
  .stat-card .value {{ font-size:22px; font-weight:700; margin-top:4px; color:var(--text-strong); }}
  code {{ font-family:'SF Mono',Monaco,monospace; font-size:12.5px;
    background:var(--code-bg); color:var(--text-strong); padding:2px 6px;
    border-radius:4px; border:1px solid var(--border); }}
  pre {{ background:var(--code-bg); padding:12px 16px; border-radius:8px;
    border:1px solid var(--border); overflow-x:auto; }}
  pre code {{ border:none; padding:0; background:transparent; }}
  footer {{ text-align:center; color:var(--muted); font-size:12px; padding:24px 0; }}

  /* News feed (flat, chronological) */
  .news-feed {{ }}
  .news-row {{ display:flex; gap:14px; padding:11px 0;
    border-bottom:1px solid var(--border); align-items:flex-start; }}
  .news-row:last-child {{ border-bottom:none; }}
  .news-ticker {{ display:inline-block; min-width:54px; padding:3px 8px;
    background:rgba(108,182,255,0.12); color:var(--accent); border-radius:4px;
    font-family:'SF Mono',Monaco,monospace; font-size:11px; font-weight:600;
    text-align:center; flex-shrink:0; }}
  .news-content {{ flex-grow:1; }}
  .news-title {{ display:block; color:var(--text-strong); text-decoration:none;
    font-weight:500; font-size:14px; line-height:1.45; }}
  .news-title:hover {{ color:var(--accent); }}
  .news-row .meta {{ display:inline-block; color:var(--muted); font-size:11px;
    margin-top:3px; }}
  .news-summary {{ font-size:12.5px; color:var(--text); margin-top:5px;
    line-height:1.55; }}

  /* Summary card */
  .summary-card {{ background:linear-gradient(135deg, rgba(108,182,255,0.08) 0%,
    rgba(220,189,251,0.08) 100%); border:1px solid var(--border);
    border-left:4px solid var(--accent2); border-radius:12px;
    padding:22px 26px; margin-bottom:20px; font-size:14px; line-height:1.7; }}
  .summary-card p {{ margin:0; color:var(--text); }}
  .summary-card strong {{ color:var(--text-strong); font-weight:600; }}
  .summary-card em {{ color:var(--muted); font-style:italic; font-size:12px;
    display:block; margin-top:10px; }}

  @media (max-width:600px) {{
    body {{ padding:12px 10px; }}
    header {{ padding:20px 16px; border-radius:10px; margin-bottom:14px; }}
    header h1 {{ font-size:20px; }}
    header p {{ font-size:12px; }}
    nav {{ padding:10px 12px; font-size:11px; gap:4px;
      border-radius:8px; margin-bottom:14px; top:4px; }}
    nav a {{ padding:4px 8px; }}
    .panel {{ padding:14px 14px; border-radius:8px; margin-bottom:14px; }}
    .panel h2 {{ font-size:15px; }}
    .panel table {{ font-size:11px; }}
    .panel > table {{ display:block; overflow-x:auto; }}
    .stat-grid {{ grid-template-columns:repeat(2, 1fr); gap:8px; }}
    .stat-card .value {{ font-size:17px; }}
    details summary {{ padding:10px 12px; font-size:12px; }}
    details .body {{ padding:10px 12px; }}
  }}
</style>"""


# ---------- Sortable table JS ----------

SORTABLE_JS = """
<script>
(function() {
  document.querySelectorAll('table.sortable').forEach(table => {
    const headers = table.querySelectorAll('th');
    headers.forEach((h, i) => {
      h.addEventListener('click', () => {
        const tbody = table.querySelector('tbody');
        const rows = Array.from(tbody.querySelectorAll('tr'));
        const ascending = !h.classList.contains('sorted-asc');
        // Clear sort indicators on all headers
        headers.forEach(x => x.classList.remove('sorted-asc', 'sorted-desc'));
        h.classList.add(ascending ? 'sorted-asc' : 'sorted-desc');
        // Detect numeric vs string by sampling first row
        rows.sort((a, b) => {
          const av = a.cells[i].dataset.sortValue ?? a.cells[i].textContent.trim();
          const bv = b.cells[i].dataset.sortValue ?? b.cells[i].textContent.trim();
          const an = parseFloat(av);
          const bn = parseFloat(bv);
          if (!isNaN(an) && !isNaN(bn)) {
            return ascending ? an - bn : bn - an;
          }
          return ascending ? av.localeCompare(bv) : bv.localeCompare(av);
        });
        rows.forEach(r => tbody.appendChild(r));
      });
    });
  });
})();
</script>
"""


# ---------- Formatters ----------

def fmt_pct(x, d=2):
    if pd.isna(x): return "—"
    cls = "pos" if x > 0 else ("neg" if x < 0 else "")
    return f'<span class="{cls}">{x:+.{d}f}%</span>'

def fmt_num(x, d=2):
    return "—" if pd.isna(x) else f"{x:.{d}f}"

def fmt_score(x):
    if pd.isna(x): return "—"
    # Color the percentile: red (poor) → yellow → green (excellent)
    if x >= 70: cls = "pos"
    elif x <= 30: cls = "neg"
    else: cls = ""
    return f'<span class="{cls}">{x:.0f}</span>'

def explain(key):
    return f'<div class="explain">{EXPLANATIONS[key]}</div>'


# ---------- Section builders ----------

def build_summary(metrics_df: pd.DataFrame, log_returns: pd.DataFrame,
                   period: str, n_tickers: int) -> str:
    """Cross-sectional summary text — what stands out across the universe."""
    parts = [f"Watchlist contains <strong>{n_tickers}</strong> tickers; "
             f"lookback window: <strong>{period}</strong>."]

    rets = metrics_df["ann_return"].dropna()
    if len(rets) >= 2:
        best_t = rets.idxmax(); best_v = rets.max() * 100
        worst_t = rets.idxmin(); worst_v = rets.min() * 100
        parts.append(
            f"Top performer: <strong>{best_t}</strong> (+{best_v:.0f}% annualized); "
            f"laggard: <strong>{worst_t}</strong> ({worst_v:+.0f}%); "
            f"return spread of <strong>{best_v - worst_v:.0f}pp</strong> across the universe."
        )

    vols = metrics_df["ann_vol"].dropna() * 100
    if len(vols) >= 2:
        most_vol = vols.idxmax(); calmest = vols.idxmin()
        parts.append(
            f"Most volatile: <strong>{most_vol}</strong> ({vols.max():.0f}% annualized vol); "
            f"calmest: <strong>{calmest}</strong> ({vols.min():.0f}%)."
        )

    sharpes = metrics_df["sharpe"].dropna()
    if len(sharpes) >= 2:
        best_sh = sharpes.idxmax()
        parts.append(
            f"Best risk-adjusted return: <strong>{best_sh}</strong> "
            f"(Sharpe {sharpes.max():.2f})."
        )

    if log_returns.shape[1] >= 2:
        corr = log_returns.corr().values
        upper = corr[np.triu_indices_from(corr, k=1)]
        avg_corr = upper.mean()
        max_corr = upper.max()
        if avg_corr > 0.65:
            corr_msg = "high — most names in this universe move together (limited diversification across the watchlist)"
        elif avg_corr > 0.45:
            corr_msg = "moderate — partial diversification structure"
        else:
            corr_msg = "low — meaningful diversification possible"
        parts.append(
            f"Average pairwise correlation: <strong>{avg_corr:.2f}</strong> ({corr_msg}); "
            f"highest pair correlation: {max_corr:.2f}."
        )

    parts.append("<em>This is a descriptive snapshot of the lookback window; "
                 "past performance does not predict future returns.</em>")
    return "<p>" + " ".join(parts) + "</p>"


def build_screener_table(metrics_df: pd.DataFrame, names: dict = None) -> str:
    """Cross-sectional screener — sortable table of all tickers."""
    rows = []
    for t in metrics_df.index:
        row = metrics_df.loc[t]
        name = (names or {}).get(t, "")
        ticker_cell = f"<strong>{t}</strong>"
        if name:
            ticker_cell += f"<br><span style='font-size:11px;color:var(--muted);'>{name}</span>"

        def cell(val, formatter, sort_val=None):
            text = formatter(val) if not pd.isna(val) else "—"
            sv = sort_val if sort_val is not None else (val if not pd.isna(val) else -999999)
            return f'<td data-sort-value="{sv}">{text}</td>'

        rows.append(
            f"<tr><td data-sort-value='{t}'>{ticker_cell}</td>" +
            cell(row.get("ann_return", np.nan) * 100,
                 lambda v: fmt_pct(v, 1)) +
            cell(row.get("ann_vol", np.nan) * 100,
                 lambda v: f"{v:.1f}%") +
            cell(row.get("sharpe", np.nan), fmt_num) +
            cell(row.get("sortino", np.nan), fmt_num) +
            cell(row.get("calmar", np.nan), fmt_num) +
            cell(row.get("max_dd", np.nan) * 100,
                 lambda v: fmt_pct(v, 1)) +
            cell(row.get("max_dd_duration", np.nan),
                 lambda v: f"{int(v)}d" if not pd.isna(v) else "—",
                 sort_val=row.get("max_dd_duration", -1)) +
            cell(row.get("beta", np.nan), fmt_num) +
            cell(row.get("corr_spy", np.nan), fmt_num) +
            cell(row.get("var_95", np.nan) * 100,
                 lambda v: fmt_pct(v, 2)) +
            cell(row.get("cvar_95", np.nan) * 100,
                 lambda v: fmt_pct(v, 2)) +
            "</tr>"
        )
    return f"""<table class="sortable"><thead><tr>
        <th>Ticker</th><th>Ann Ret</th><th>Ann Vol</th>
        <th>Sharpe</th><th>Sortino</th><th>Calmar</th>
        <th>Max DD</th><th>DD Days</th><th>Beta</th><th>Corr SPY</th>
        <th>VaR95</th><th>CVaR95</th></tr></thead>
        <tbody>{"".join(rows)}</tbody></table>
        <p class="small-note">Click any column header to sort. DD Days = longest
        peak-to-recovery duration in trading days. Beta and Corr SPY are
        relative to the SPY ETF (S&amp;P 500) over the same window.</p>"""


def build_factor_score_table(scores_df: pd.DataFrame, names: dict = None) -> str:
    """Detailed factor breakdown table — companion to the bar chart."""
    rows = []
    for t in scores_df.index:
        row = scores_df.loc[t]
        name = (names or {}).get(t, "")
        ticker_cell = f"<strong>{t}</strong>"
        if name:
            ticker_cell += f"<br><span style='font-size:11px;color:var(--muted);'>{name}</span>"

        # Composite gets prominent display
        composite = row.get("composite_score", np.nan)
        comp_cell = (f'<td data-sort-value="{composite if not pd.isna(composite) else -999}" '
                     f'style="font-weight:700;">{fmt_score(composite)}</td>')

        def score_cell(s):
            sv = s if not pd.isna(s) else -999
            return f'<td data-sort-value="{sv}">{fmt_score(s)}</td>'

        rows.append(
            f"<tr><td data-sort-value='{t}'>{ticker_cell}</td>" +
            comp_cell +
            score_cell(row.get("momentum_score", np.nan)) +
            score_cell(row.get("quality_score", np.nan)) +
            score_cell(row.get("value_score", np.nan)) +
            score_cell(row.get("lowvol_score", np.nan)) +
            f"<td>{fmt_pct(row.get('mom_12m_excl_1m', np.nan) * 100, 1)}</td>"
            f"<td>{fmt_pct(row.get('mom_6m', np.nan) * 100, 1)}</td>"
            f"<td>{fmt_pct(row.get('mom_3m', np.nan) * 100, 1)}</td>"
            f"<td>{fmt_num(row.get('vol_12m', np.nan) * 100, 1)}%</td>"
            f"<td>{fmt_num(row.get('pe', np.nan), 1)}</td>"
            f"<td>{fmt_num(row.get('pb', np.nan), 1)}</td>"
            f"<td>{fmt_num(row.get('roe', np.nan) * 100 if not pd.isna(row.get('roe', np.nan)) else np.nan, 1)}%</td>"
            "</tr>"
        )
    return f"""<table class="sortable"><thead><tr>
        <th>Ticker</th><th>Composite</th>
        <th>Momentum</th><th>Quality</th><th>Value</th><th>Low Vol</th>
        <th>Mom 12-1</th><th>Mom 6m</th><th>Mom 3m</th>
        <th>Vol 12m</th><th>P/E</th><th>P/B</th><th>ROE</th>
        </tr></thead>
        <tbody>{"".join(rows)}</tbody></table>
        <p class="small-note">All score columns are percentile ranks (0-100) within
        the watchlist universe. Higher = better. The four right-side columns are the
        underlying raw values. Click any header to sort.</p>"""


def build_news_feed(feed: list) -> str:
    """Flat chronological news feed."""
    if not feed:
        return '<p class="small-note">News disabled or unavailable for any ticker.</p>'
    from .news import format_published
    rows = []
    for a in feed[:80]:  # cap to keep page from getting huge
        when = format_published(a.get("published"))
        meta = []
        if when:
            meta.append(when)
        if a.get("source") and a["source"] != "Yahoo Finance":
            meta.append(a["source"])
        meta_html = (f'<span class="meta">{" · ".join(meta)}</span>'
                     if meta else "")
        summary_html = (f'<div class="news-summary">{a["summary"]}</div>'
                        if a.get("summary") else "")
        rows.append(f"""<div class="news-row">
          <span class="news-ticker">{a['ticker']}</span>
          <div class="news-content">
            <a class="news-title" href="{a['link']}" target="_blank" rel="noopener">{a['title']}</a>
            {meta_html}
            {summary_html}
          </div>
        </div>""")
    return f'<div class="news-feed">{"".join(rows)}</div>'


def build_ticker_dashboards(features_dict: dict) -> str:
    """Per-ticker collapsible technical dashboards."""
    blocks = []
    for t, f in features_dict.items():
        if f.price.empty:
            continue
        fig_html = fig_ticker_dashboard(f).to_html(
            include_plotlyjs=False, full_html=False,
            div_id=f"chart_{t}", config={"displayModeBar": False, "responsive": True})
        title = (f"{t} — {f.company_name} — ${f.price.iloc[-1]:.2f}"
                 if f.company_name
                 else f"{t} — ${f.price.iloc[-1]:.2f}")
        blocks.append(f"""<details><summary>{title}</summary>
          <div class="body">{fig_html}</div>
        </details>""")
    return "".join(blocks)


def build_optimization_section(frontier, alt_portfolios=None):
    """Efficient frontier + reference portfolio cards. No 'your portfolio' marker
    since this tool is universe-level, not holdings-level."""
    fig_html = fig_efficient_frontier(frontier, current_position=None,
                                       alt_portfolios=alt_portfolios).to_html(
        include_plotlyjs=False, full_html=False,
        config={"displayModeBar": False, "responsive": True})
    gmv = frontier["gmv"]
    tang = frontier["tangency"]
    cards = [
        ("Min variance (GMV)", gmv["ann_return"], gmv["ann_vol"], gmv["sharpe"], "var(--up)"),
        ("Max Sharpe (tangency)", tang["ann_return"], tang["ann_vol"], tang["sharpe"], "var(--accent)"),
    ]
    for p in (alt_portfolios or []):
        cards.append((p["label"], p["ann_return"], p["ann_vol"], p["sharpe"], "var(--muted)"))

    card_html = ""
    for label, r, v, sh, color in cards:
        card_html += f"""<div class="stat-card" style="border-left:3px solid {color};">
          <div class="label">{label}</div>
          <div style="font-size:13px;color:var(--muted);margin-top:6px;">
            Return: <strong style="color:var(--text-strong);">{r*100:+.1f}%</strong> ·
            Vol: <strong style="color:var(--text-strong);">{v*100:.1f}%</strong> ·
            Sharpe: <strong style="color:var(--text-strong);">{sh:.2f}</strong>
          </div></div>"""

    # Tangency weight breakdown
    tickers = frontier["tickers"]
    tang_w = tang["weights"]
    rows = []
    nonzero = [(tickers[i], tang_w[i]) for i in range(len(tickers)) if tang_w[i] > 0.005]
    nonzero.sort(key=lambda x: -x[1])
    for t, w in nonzero:
        rows.append(f"<tr><td><strong>{t}</strong></td><td>{w*100:.1f}%</td></tr>")
    if not rows:
        rows = ["<tr><td>—</td><td>0%</td></tr>"]
    weight_table = f"""<table><thead><tr><th>Ticker</th>
        <th>Tangency weight</th></tr></thead>
        <tbody>{"".join(rows)}</tbody></table>"""

    return f"""{fig_html}
    <h3>Reference portfolios</h3>
    <div class="stat-grid">{card_html}</div>
    <h3>Tangency portfolio composition</h3>
    {weight_table}
    <p class="small-note">Tangency weights are sample-period optimal. Out-of-sample
    performance is typically substantially worse (DeMiguel/Garlappi/Uppal 2009).
    Use as diagnostic, not as a target allocation.</p>"""


def build_strategy_section(backtest_results, initial_capital):
    if not backtest_results:
        return '<p class="small-note">Strategy backtest disabled. Run with <code>--backtest</code>.</p>'
    from .visualizations import fig_strategy_comparison
    eq_html = fig_strategy_comparison(backtest_results, initial_capital).to_html(
        include_plotlyjs=False, full_html=False,
        config={"displayModeBar": False, "responsive": True})
    rows = []
    for r in backtest_results:
        rows.append(f"<tr><td><strong>{r.strategy_name}</strong></td>"
                    f"<td>{fmt_pct(r.total_return*100, 1)}</td>"
                    f"<td>{fmt_pct(r.annual_return*100, 1)}</td>"
                    f"<td>{fmt_num(r.annual_vol*100, 1)}%</td>"
                    f"<td>{fmt_num(r.sharpe)}</td>"
                    f"<td>{fmt_pct(r.max_drawdown*100, 1)}</td>"
                    f"<td>{fmt_num(r.calmar)}</td>"
                    f"<td>{r.n_trades}</td></tr>")
    table = f"""<table><thead><tr>
        <th>Strategy</th><th>Total Ret</th><th>Ann Ret</th><th>Ann Vol</th>
        <th>Sharpe</th><th>Max DD</th><th>Calmar</th><th># Trades</th>
        </tr></thead><tbody>{"".join(rows)}</tbody></table>"""
    return f"""{eq_html}
    <h3>Strategy performance comparison</h3>
    {table}"""


def build_literature_section() -> str:
    blocks = []
    for topic_key, topic in LITERATURE.items():
        papers_html = "".join(f"""<div class="lit-paper">
            <div class="cite">{p['cite']}</div>
            <div class="note">{p['note']}</div>
            <a href="{p['url']}" target="_blank" rel="noopener">→ Original paper</a>
          </div>""" for p in topic["papers"])
        blocks.append(f"""<div class="lit-section">
          <h3>{topic['section_title']}</h3>
          <div class="topic-summary">{topic['what_it_covers']}</div>
          {papers_html}</div>""")
    return "".join(blocks)


# ---------- Main report assembly ----------

def build_html_report(tickers, features_dict, prices, bench_returns, period,
                      metrics_df, scores_df,
                      log_returns,
                      frontier=None, alt_portfolios=None,
                      backtest_results=None, initial_capital=10_000.0,
                      news_feed=None, names=None):
    """
    Top-level assembly. Different signature from portfolio_analyzer because
    this is a universe report — no holdings, no risk decomp, no Monte Carlo.
    """
    # Generate the textual summary
    summary_html = build_summary(metrics_df, log_returns, period, len(tickers))

    # Render charts
    norm_html = fig_normalized_returns(prices[tickers]).to_html(
        include_plotlyjs=False, full_html=False,
        config={"displayModeBar": False, "responsive": True})
    rr_html = fig_risk_return_scatter(metrics_df).to_html(
        include_plotlyjs=False, full_html=False,
        config={"displayModeBar": False, "responsive": True})
    dd_html = fig_drawdown_comparison(prices[tickers]).to_html(
        include_plotlyjs=False, full_html=False,
        config={"displayModeBar": False, "responsive": True})
    corr_html = fig_correlation_clustered(log_returns[tickers]).to_html(
        include_plotlyjs=False, full_html=False,
        config={"displayModeBar": False, "responsive": True})
    factor_chart_html = fig_factor_scores(scores_df).to_html(
        include_plotlyjs=False, full_html=False,
        config={"displayModeBar": False, "responsive": True})
    dispersion_html = fig_return_dispersion(metrics_df).to_html(
        include_plotlyjs=False, full_html=False,
        config={"displayModeBar": False, "responsive": True})

    screener_html = build_screener_table(metrics_df, names)
    factor_table_html = build_factor_score_table(scores_df, names)
    ticker_blocks = build_ticker_dashboards(features_dict)
    news_html = build_news_feed(news_feed) if news_feed is not None else \
        '<p class="small-note">News fetch disabled. Run without <code>--no-news</code> to include.</p>'
    opt_html = (build_optimization_section(frontier, alt_portfolios)
                if frontier is not None
                else '<p class="small-note">Mean-variance optimization disabled.</p>')
    strat_html = build_strategy_section(backtest_results or [], initial_capital)
    lit_html = build_literature_section()

    nav = """<nav>
      <a href="#summary">Summary</a>
      <a href="#screener">Screener</a>
      <a href="#factors">Factor Scores</a>
      <a href="#performance">Performance</a>
      <a href="#riskreturn">Risk/Return</a>
      <a href="#drawdowns">Drawdowns</a>
      <a href="#correlation">Correlation</a>
      <a href="#optimization">Optimization</a>
      <a href="#strategies">Strategies</a>
      <a href="#tickers">Per-Ticker</a>
      <a href="#news">News</a>
      <a href="#literature">Literature</a>
    </nav>"""

    return f"""<!DOCTYPE html>
<html lang="en"><head>
<meta charset="utf-8">
<title>Watchlist Analysis — {datetime.now().strftime("%Y-%m-%d")}</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
{make_css()}
</head><body><div class="container">

<header>
  <h1>Quantitative Watchlist Analysis</h1>
  <p>Generated {datetime.now().strftime("%B %d, %Y at %H:%M")} ·
     Lookback: {period} · {len(tickers)} tickers · Benchmark: {BENCHMARK}</p>
</header>

<div class="disclaimer">
  <strong>For learning, not for trading.</strong> Cross-sectional metrics, factor
  scores, and backtests are descriptive of the lookback window. Past performance
  does not predict future returns. Single-period rankings are noisy estimates
  subject to multiple-testing concerns (Harvey, Liu &amp; Zhu 2016).
</div>

{nav}

<div class="panel" id="summary">
  <h2>📋 Cross-Sectional Summary</h2>
  <div class="summary-card">{summary_html}</div>
  {explain('summary')}
</div>

<div class="panel" id="screener">
  <h2>🔍 Cross-Sectional Screener</h2>
  {explain('screener')}
  {screener_html}
  {dispersion_html}
</div>

<div class="panel" id="factors">
  <h2>📊 Factor Scores (QVM+L)</h2>
  {explain('factor_scores')}
  {factor_chart_html}
  <h3>Factor score detail</h3>
  {factor_table_html}
</div>

<div class="panel" id="performance">
  <h2>Normalized Cumulative Performance</h2>
  {norm_html}
  {explain('normalized_returns')}
</div>

<div class="panel" id="riskreturn">
  <h2>Risk vs. Return</h2>
  {rr_html}
  {explain('risk_return')}
</div>

<div class="panel" id="drawdowns">
  <h2>Drawdown Comparison</h2>
  {dd_html}
  {explain('drawdown')}
</div>

<div class="panel" id="correlation">
  <h2>Correlation Structure</h2>
  {corr_html}
  {explain('correlation')}
</div>

<div class="panel" id="optimization">
  <h2>📐 Mean-Variance Optimization</h2>
  {explain('optimization')}
  {opt_html}
</div>

<div class="panel" id="strategies">
  <h2>Strategy Backtest</h2>
  {explain('strategies')}
  {strat_html}
  <h3>⚠️ Methodology Caveats</h3>
  <div class="caveats">{EXPLANATIONS['strategy_caveats']}</div>
</div>

<div class="panel" id="tickers">
  <h2>Per-Ticker Technical Dashboards</h2>
  {explain('ticker_dashboards')}
  <p class="small-note" style="margin-top:14px;">Click any ticker to expand.</p>
  {ticker_blocks}
</div>

<div class="panel" id="news">
  <h2>📰 Watchlist News Feed</h2>
  {explain('news')}
  {news_html}
</div>

<div class="panel" id="literature">
  <h2>Academic Literature</h2>
  <p class="small-note">Curated foundational and contemporary papers organized
  around the methods this report uses.</p>
  {lit_html}
</div>

<footer>
  Generated by quant_watchlist v1 · Educational use only · Not investment advice
</footer>

{SORTABLE_JS}
</div></body></html>
"""
