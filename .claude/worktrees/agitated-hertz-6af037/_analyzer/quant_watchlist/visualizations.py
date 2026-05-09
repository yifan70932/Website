"""
Plotly figures for the watchlist tool. Theme-aware via themes.COLORS.

Distinct from portfolio_analyzer.visualizations: focused on cross-sectional
comparison rather than portfolio-level decomposition.
"""

from __future__ import annotations
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy import stats
from scipy.cluster import hierarchy

from . import themes
from .core import TRADING_DAYS, RISK_FREE_DEFAULT


def _base():
    c = themes.COLORS
    return dict(
        paper_bgcolor=c["panel"], plot_bgcolor=c["panel"],
        font=dict(family="Inter, sans-serif", color=c["text"]),
        margin=dict(l=60, r=60, t=60, b=50),
        hovermode="closest",
    )


# ---------- Single-ticker dashboard (reused from portfolio_analyzer style) ----------

def fig_ticker_dashboard(feat):
    """Per-ticker 3-panel: price+SMA+BB, RSI, MACD."""
    c = themes.COLORS
    fig = make_subplots(rows=3, cols=1, shared_xaxes=True,
                        row_heights=[0.55, 0.22, 0.23],
                        vertical_spacing=0.04,
                        subplot_titles=(f"{feat.ticker} price, SMAs, Bollinger bands",
                                         "RSI(14)", "MACD"))
    p = feat.price
    fig.add_trace(go.Scatter(x=p.index, y=p, name="Close",
        line=dict(color=c["text_strong"], width=1.7)), row=1, col=1)
    fig.add_trace(go.Scatter(x=p.index, y=feat.sma_50, name="SMA 50",
        line=dict(color=c["accent"], width=1.2)), row=1, col=1)
    fig.add_trace(go.Scatter(x=p.index, y=feat.sma_200, name="SMA 200",
        line=dict(color=c["accent2"], width=1.2)), row=1, col=1)
    fig.add_trace(go.Scatter(x=p.index, y=feat.bb_upper, name="BB upper",
        line=dict(color=c["muted"], width=0.8, dash="dash"),
        showlegend=False), row=1, col=1)
    fig.add_trace(go.Scatter(x=p.index, y=feat.bb_lower, name="BB lower",
        line=dict(color=c["muted"], width=0.8, dash="dash"),
        fill="tonexty", fillcolor=f"rgba(118,131,144,0.05)",
        showlegend=False), row=1, col=1)
    fig.add_trace(go.Scatter(x=p.index, y=feat.rsi_14, name="RSI",
        line=dict(color=c["accent"], width=1.4),
        showlegend=False), row=2, col=1)
    fig.add_hline(y=70, line=dict(color=c["down"], width=0.8, dash="dot"), row=2, col=1)
    fig.add_hline(y=30, line=dict(color=c["up"], width=0.8, dash="dot"), row=2, col=1)
    fig.add_trace(go.Scatter(x=p.index, y=feat.macd, name="MACD",
        line=dict(color=c["accent"], width=1.4),
        showlegend=False), row=3, col=1)
    fig.add_trace(go.Scatter(x=p.index, y=feat.macd_signal, name="Signal",
        line=dict(color=c["accent2"], width=1.2),
        showlegend=False), row=3, col=1)
    fig.update_layout(**_base(), height=620, showlegend=True,
        legend=dict(orientation="h", y=1.06, x=1, xanchor="right"))
    fig.update_xaxes(gridcolor=c["grid"])
    fig.update_yaxes(gridcolor=c["grid"])
    return fig


# ---------- Cross-sectional charts (the heart of this tool) ----------

def fig_normalized_returns(prices: pd.DataFrame, base_date=None):
    """
    All tickers' cumulative total returns rebased to 100 at the start of the window.
    Lets you read relative performance at a glance.
    """
    c = themes.COLORS
    pal = themes.palette_cycle()
    if base_date is not None:
        prices = prices[prices.index >= pd.Timestamp(base_date)]
    # Rebase to 100
    rebased = prices.div(prices.iloc[0]) * 100
    fig = go.Figure()
    for i, col in enumerate(rebased.columns):
        series = rebased[col].dropna()
        last = series.iloc[-1] if len(series) else np.nan
        # Annotate end-points so you can match line to label without legend hunt
        fig.add_trace(go.Scatter(
            x=series.index, y=series, name=f"{col} ({last:.0f})",
            line=dict(color=pal[i % len(pal)], width=1.5),
            hovertemplate=f"<b>{col}</b><br>%{{x|%Y-%m-%d}}<br>%{{y:.1f}}<extra></extra>"))
    fig.add_hline(y=100, line=dict(color=c["muted"], width=1, dash="dot"))
    fig.update_layout(**_base(),
        title=dict(text="Normalized Cumulative Returns (start = 100)",
                   x=0.5, font=dict(color=c["text_strong"])),
        height=540, xaxis_title="Date",
        yaxis_title="Indexed level (start = 100)",
        legend=dict(orientation="v", y=1, x=1.02, xanchor="left", font=dict(size=10)),
        xaxis=dict(gridcolor=c["grid"]), yaxis=dict(gridcolor=c["grid"]))
    return fig


def fig_risk_return_scatter(metrics_df: pd.DataFrame, rf: float = RISK_FREE_DEFAULT):
    """
    Each ticker as a labeled dot in (annualized vol, annualized return) space.
    Adds Sharpe-ratio iso-lines so the user can read relative risk-adjusted performance.

    metrics_df must have columns: ann_return, ann_vol (decimals).
    """
    c = themes.COLORS
    fig = go.Figure()

    # Sharpe iso-lines: Return = rf + Sharpe * Vol
    max_vol = max(metrics_df["ann_vol"].max() * 1.15, 0.40)
    vol_range = np.linspace(0.0, max_vol, 50)
    for sr, label in [(0.5, "SR 0.5"), (1.0, "SR 1.0"), (1.5, "SR 1.5"), (2.0, "SR 2.0")]:
        ret_line = rf + sr * vol_range
        fig.add_trace(go.Scatter(
            x=vol_range * 100, y=ret_line * 100,
            mode="lines", line=dict(color=c["muted"], width=0.8, dash="dot"),
            showlegend=False, hoverinfo="skip"))
        # Label at right end
        fig.add_annotation(x=vol_range[-1] * 100, y=ret_line[-1] * 100,
            text=label, showarrow=False,
            font=dict(size=10, color=c["muted"]),
            xshift=20)

    # Tickers as dots
    pal = themes.palette_cycle()
    for i, t in enumerate(metrics_df.index):
        ret = metrics_df.loc[t, "ann_return"] * 100
        vol = metrics_df.loc[t, "ann_vol"] * 100
        sh = metrics_df.loc[t].get("sharpe", np.nan)
        fig.add_trace(go.Scatter(
            x=[vol], y=[ret], mode="markers+text",
            text=[t], textposition="top center",
            textfont=dict(size=11, color=c["text_strong"]),
            marker=dict(size=14, color=pal[i % len(pal)],
                        line=dict(width=1.5, color=c["panel"])),
            name=t, showlegend=False,
            hovertemplate=(f"<b>{t}</b><br>Vol: {vol:.1f}%<br>"
                           f"Return: {ret:+.1f}%<br>Sharpe: {sh:.2f}<extra></extra>")))

    # Risk-free reference
    fig.add_hline(y=rf * 100, line=dict(color=c["muted"], width=1, dash="dash"),
                  annotation_text=f"Rf = {rf*100:.1f}%",
                  annotation_font=dict(color=c["muted"], size=10))

    fig.update_layout(**_base(),
        title=dict(text="Risk vs. Return — Sharpe Iso-Lines",
                   x=0.5, font=dict(color=c["text_strong"])),
        height=540, xaxis_title="Annualized volatility (%)",
        yaxis_title="Annualized return (%)",
        xaxis=dict(gridcolor=c["grid"], zerolinecolor=c["grid"], range=[0, max_vol * 100 * 1.05]),
        yaxis=dict(gridcolor=c["grid"], zerolinecolor=c["grid"]))
    return fig


def fig_drawdown_comparison(prices: pd.DataFrame):
    """All tickers' drawdown curves on one chart."""
    c = themes.COLORS
    pal = themes.palette_cycle()
    fig = go.Figure()
    for i, col in enumerate(prices.columns):
        series = prices[col].dropna()
        if len(series) < 30:
            continue
        cummax = series.cummax()
        dd = (series - cummax) / cummax * 100
        fig.add_trace(go.Scatter(
            x=dd.index, y=dd, name=col,
            line=dict(color=pal[i % len(pal)], width=1.2),
            hovertemplate=f"<b>{col}</b><br>%{{x|%Y-%m-%d}}<br>DD: %{{y:.1f}}%<extra></extra>"))
    fig.update_layout(**_base(),
        title=dict(text="Drawdown Comparison — All Watchlist Names",
                   x=0.5, font=dict(color=c["text_strong"])),
        height=480, xaxis_title="Date",
        yaxis_title="Drawdown from running peak (%)",
        legend=dict(orientation="v", y=1, x=1.02, xanchor="left", font=dict(size=10)),
        xaxis=dict(gridcolor=c["grid"]),
        yaxis=dict(gridcolor=c["grid"]))
    return fig


def fig_correlation_clustered(log_returns: pd.DataFrame):
    """
    Correlation heatmap with hierarchical clustering applied to row/column order.
    Adjacent tickers in the matrix are the most-correlated → groups visually pop.
    """
    c = themes.COLORS
    if log_returns.shape[1] < 2:
        return go.Figure()
    corr = log_returns.corr()
    # Hierarchical clustering on 1 - corr distance
    distance = 1 - corr.values
    np.fill_diagonal(distance, 0)
    # Need a condensed distance matrix for linkage
    from scipy.spatial.distance import squareform
    # Ensure symmetry (floating-point tiny mismatches break squareform)
    distance = (distance + distance.T) / 2
    np.fill_diagonal(distance, 0)
    condensed = squareform(distance, checks=False)
    linkage = hierarchy.linkage(condensed, method="average")
    order = hierarchy.leaves_list(linkage)
    sorted_corr = corr.iloc[order, order]

    fig = go.Figure(go.Heatmap(
        z=sorted_corr.values,
        x=sorted_corr.columns, y=sorted_corr.index,
        colorscale="RdBu_r", zmid=0, zmin=-1, zmax=1,
        colorbar=dict(title=dict(text="Corr"), tickfont=dict(color=c["text"])),
        hovertemplate="<b>%{x}</b> ↔ <b>%{y}</b>: %{z:.2f}<extra></extra>"))
    # Annotations inside cells
    for i, row_t in enumerate(sorted_corr.index):
        for j, col_t in enumerate(sorted_corr.columns):
            v = sorted_corr.iloc[i, j]
            color = "white" if abs(v) > 0.55 else c["text_strong"]
            fig.add_annotation(x=col_t, y=row_t, text=f"{v:.2f}",
                                showarrow=False, font=dict(size=9, color=color))
    fig.update_layout(**_base(),
        title=dict(text="Correlation Matrix (clustered ordering)",
                   x=0.5, font=dict(color=c["text_strong"])),
        height=560 + 18 * len(corr),  # grow with universe size
        xaxis=dict(side="bottom", tickangle=-45),
        yaxis=dict(autorange="reversed"))
    return fig


def fig_factor_scores(scores_df: pd.DataFrame, top_n: int = None):
    """
    Stacked horizontal bar showing factor decomposition for each ticker.
    Each row is a ticker; bar segments are momentum/quality/value/lowvol percentiles.
    """
    c = themes.COLORS
    df = scores_df.copy()
    if top_n:
        df = df.head(top_n)
    # We want descending composite at top
    df = df.sort_values("composite_score", ascending=True)  # Plotly h-bar reads bottom-up

    factor_cols = [
        ("momentum_score", "Momentum", c["accent"]),
        ("quality_score", "Quality", c["up"]),
        ("value_score", "Value", c["warn"]),
        ("lowvol_score", "Low Vol", c["accent2"]),
    ]

    fig = go.Figure()
    for col, label, color in factor_cols:
        fig.add_trace(go.Bar(
            y=df.index, x=df[col].fillna(0),
            name=label, orientation="h",
            marker=dict(color=color, line=dict(width=0)),
            hovertemplate=f"<b>%{{y}}</b><br>{label}: %{{x:.0f}}<extra></extra>"))

    # Composite score as a marker overlay
    fig.add_trace(go.Scatter(
        y=df.index, x=df["composite_score"], mode="markers",
        name="Composite", marker=dict(color=c["text_strong"], size=10,
            symbol="diamond", line=dict(color=c["panel"], width=1.5)),
        hovertemplate="<b>%{y}</b><br>Composite: %{x:.1f}<extra></extra>"))

    fig.update_layout(**_base(),
        title=dict(text="Factor Score Breakdown (percentiles within universe)",
                   x=0.5, font=dict(color=c["text_strong"])),
        height=max(360, 28 * len(df) + 100),
        barmode="group", xaxis_title="Percentile (0 = worst, 100 = best)",
        legend=dict(orientation="h", y=1.06, x=1, xanchor="right"),
        xaxis=dict(gridcolor=c["grid"], range=[0, 105]),
        yaxis=dict(gridcolor=c["grid"]))
    return fig


def fig_return_dispersion(metrics_df: pd.DataFrame):
    """
    Box-and-whisker style: shows the dispersion of annualized returns across
    the universe with each ticker labeled. Quick way to see outliers.
    """
    c = themes.COLORS
    rets = metrics_df["ann_return"].dropna() * 100
    fig = go.Figure()
    fig.add_trace(go.Box(
        x=rets.values, name="Annualized return",
        boxpoints="all", jitter=0.5, pointpos=0,
        text=rets.index, hovertemplate="<b>%{text}</b><br>%{x:.1f}%<extra></extra>",
        marker=dict(color=c["accent"], size=7),
        line=dict(color=c["accent"]),
        fillcolor="rgba(108,182,255,0.15)"))
    fig.update_layout(**_base(),
        title=dict(text="Annualized Return Dispersion Across Watchlist",
                   x=0.5, font=dict(color=c["text_strong"])),
        height=200, xaxis_title="Annualized return (%)",
        showlegend=False,
        xaxis=dict(gridcolor=c["grid"], zerolinecolor=c["grid"]),
        yaxis=dict(showticklabels=False))
    return fig


# ---------- Re-export portfolio-style figures we still need ----------

def fig_efficient_frontier(frontier, current_position=None, alt_portfolios=None):
    """Reused — same as portfolio_analyzer; current_position optional."""
    c = themes.COLORS
    fig = go.Figure()

    if len(frontier["frontier_vols"]) > 1:
        fig.add_trace(go.Scatter(
            x=frontier["frontier_vols"] * 100,
            y=frontier["frontier_returns"] * 100,
            mode="lines", name="Efficient frontier",
            line=dict(color=c["accent"], width=3),
            hovertemplate="Vol: %{x:.1f}%<br>Return: %{y:.1f}%<extra></extra>"))

    rf_pct = frontier.get("rf", RISK_FREE_DEFAULT) * 100
    tang = frontier["tangency"]
    if tang["ann_vol"] > 0:
        slope = (tang["ann_return"] * 100 - rf_pct) / (tang["ann_vol"] * 100)
        max_x = max(frontier["frontier_vols"].max() if len(frontier["frontier_vols"]) else 0,
                    frontier["asset_vols"].max()) * 100 * 1.1
        cml_x = np.array([0, max_x])
        fig.add_trace(go.Scatter(
            x=cml_x, y=rf_pct + slope * cml_x,
            mode="lines", name="Capital market line",
            line=dict(color=c["muted"], width=1.5, dash="dot")))

    fig.add_trace(go.Scatter(
        x=frontier["asset_vols"] * 100,
        y=frontier["asset_returns"] * 100,
        mode="markers+text", name="Individual assets",
        text=frontier["tickers"], textposition="top center",
        textfont=dict(size=11, color=c["text"]),
        marker=dict(size=10, color=c["accent2"],
                    line=dict(width=1, color=c["panel"])),
        hovertemplate="<b>%{text}</b><br>Vol: %{x:.1f}%<br>Return: %{y:.1f}%<extra></extra>"))

    gmv = frontier["gmv"]
    fig.add_trace(go.Scatter(
        x=[gmv["ann_vol"] * 100], y=[gmv["ann_return"] * 100],
        mode="markers+text", name="Min variance",
        text=["GMV"], textposition="middle right",
        textfont=dict(size=11, color=c["up"]),
        marker=dict(size=14, color=c["up"], symbol="diamond",
                    line=dict(width=2, color=c["panel"]))))
    fig.add_trace(go.Scatter(
        x=[tang["ann_vol"] * 100], y=[tang["ann_return"] * 100],
        mode="markers+text", name="Max Sharpe",
        text=["Tangency"], textposition="middle right",
        textfont=dict(size=11, color=c["accent"]),
        marker=dict(size=14, color=c["accent"], symbol="star-triangle-up",
                    line=dict(width=2, color=c["panel"]))))

    for p in (alt_portfolios or []):
        fig.add_trace(go.Scatter(
            x=[p["ann_vol"] * 100], y=[p["ann_return"] * 100],
            mode="markers+text", name=p["label"],
            text=[p["label"]], textposition="top right",
            textfont=dict(size=10, color=c["muted"]),
            marker=dict(size=11, color=c["muted"], symbol="circle-open",
                        line=dict(width=2))))

    fig.update_layout(**_base(),
        title=dict(text="Long-Only Efficient Frontier of Watchlist Universe",
                   x=0.5, font=dict(color=c["text_strong"])),
        height=520, xaxis_title="Annualized volatility (%)",
        yaxis_title="Annualized return (%)",
        legend=dict(orientation="v", y=1, x=1.02, xanchor="left"),
        xaxis=dict(gridcolor=c["grid"], zerolinecolor=c["grid"]),
        yaxis=dict(gridcolor=c["grid"], zerolinecolor=c["grid"]))
    return fig


def fig_strategy_comparison(results, initial_capital):
    """Same as portfolio_analyzer version — equity curves of each strategy."""
    c = themes.COLORS
    pal = themes.palette_cycle()
    fig = go.Figure()
    for i, r in enumerate(results):
        fig.add_trace(go.Scatter(
            x=r.equity_curve.index, y=r.equity_curve,
            name=r.strategy_name,
            line=dict(width=1.8, color=pal[i % len(pal)]),
            hovertemplate=f"<b>{r.strategy_name}</b><br>%{{x|%Y-%m-%d}}<br>$%{{y:,.0f}}<extra></extra>"))
    fig.add_hline(y=initial_capital, line=dict(color=c["muted"], width=1, dash="dot"),
                  annotation_text="Starting capital",
                  annotation_font=dict(color=c["muted"]))
    fig.update_layout(**_base(),
        title=dict(text="Strategy Equity Curves (after transaction costs)",
                   x=0.5, font=dict(color=c["text_strong"])),
        height=460, xaxis_title="Date",
        yaxis_title="Portfolio value (USD)",
        legend=dict(orientation="h", y=1.08, x=1, xanchor="right"),
        xaxis=dict(gridcolor=c["grid"]), yaxis=dict(gridcolor=c["grid"]))
    return fig
