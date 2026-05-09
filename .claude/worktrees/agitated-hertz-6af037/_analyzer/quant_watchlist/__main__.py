"""CLI entry: python -m quant_watchlist [...]"""

from __future__ import annotations
import argparse
import time
import webbrowser
import warnings

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore", category=FutureWarning)

from . import themes
from .core import (DEFAULT_WATCHLIST, BENCHMARK, OUTPUT_DIR, RISK_FREE_DEFAULT,
                   TRADING_DAYS,
                   load_watchlist, save_watchlist, apply_cli_changes,
                   compute_features, sharpe, sortino, max_drawdown,
                   max_drawdown_duration, beta, var_95, cvar_95,
                   correlation_to_benchmark)
from .data_sources import get_source, DATA_SOURCES
from .strategies import STRATEGIES, get_strategy
from .backtester import run_backtest
from .factor_scores import composite_qvml
from .statistics import calmar_ratio
from .report import build_html_report


def parse_args():
    p = argparse.ArgumentParser(
        prog="quant_watchlist",
        description="Quantitative watchlist analyzer (cross-sectional screening + factor scoring)",
    )
    p.add_argument("--tickers", nargs="+", metavar="TICKER",
                   help="Replace watchlist entirely (e.g. --tickers VOO QQQ NVDA TSLA)")
    p.add_argument("--add", nargs="+", metavar="TICKER",
                   help="Add tickers to current watchlist")
    p.add_argument("--remove", nargs="+", metavar="TICKER",
                   help="Remove tickers from watchlist")
    p.add_argument("--reset", action="store_true",
                   help="Reset to default watchlist")
    p.add_argument("--period", default="2y",
                   help="Lookback (1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, max)")
    p.add_argument("--no-open", action="store_true")
    p.add_argument("--no-fundamentals", action="store_true",
                   help="Skip fundamentals fetch (faster; Quality/Value scores will be sparse)")
    p.add_argument("--no-news", action="store_true")
    p.add_argument("--no-optimization", action="store_true")
    p.add_argument("--light", action="store_true", help="Light theme")
    p.add_argument("--data-source", default="yfinance",
                   choices=list(DATA_SOURCES))
    p.add_argument("--backtest", action="store_true",
                   help="Run strategy backtest across all 6 strategies")
    p.add_argument("--initial-capital", type=float, default=10_000.0)
    p.add_argument("--cost-bps", type=float, default=10.0)
    return p.parse_args()


def fetch_company_names(tickers: list[str]) -> dict:
    """Best-effort name fetch — used for display labels."""
    names = {}
    try:
        import yfinance as yf
        for t in tickers:
            try:
                info = yf.Ticker(t).info
                name = info.get("longName") or info.get("shortName")
                if name:
                    names[t] = name
            except Exception:
                pass
    except ImportError:
        pass
    return names


def main():
    args = parse_args()
    themes.set_theme("light" if args.light else "dimmed")
    print(f"Theme: {'light' if args.light else 'GitHub Dark Dimmed'}")

    tickers = list(DEFAULT_WATCHLIST) if args.reset else load_watchlist()
    tickers = apply_cli_changes(tickers, args)
    if not tickers:
        print("Empty watchlist — add tickers with --add or --tickers.")
        return
    save_watchlist(tickers)
    print(f"Watchlist ({len(tickers)}): {tickers}")

    # Fetch prices
    source = get_source(args.data_source)
    print(f"Data source: {source.name}")
    print(f"Fetching {args.period} of price data for {len(tickers) + 1} symbols...")
    prices = source.fetch_prices(tickers + [BENCHMARK], args.period)
    if prices.empty:
        print("Price fetch failed.")
        return
    bench_returns = (np.log(prices[BENCHMARK] / prices[BENCHMARK].shift(1))
                     if BENCHMARK in prices.columns else pd.Series(dtype=float))
    print(f"  {len(prices)} days "
          f"({prices.index[0].date()} to {prices.index[-1].date()})")

    # Fetch company names for labels
    print("Fetching company names...")
    names = fetch_company_names(tickers)
    print(f"  Got {len(names)} names")

    # Build features
    features = {}
    log_returns_full = np.log(prices / prices.shift(1)).dropna()
    valid_tickers = [t for t in tickers if t in prices.columns]
    for t in valid_tickers:
        features[t] = compute_features(t, prices[t].dropna(),
                                        company_name=names.get(t))

    # Fundamentals
    if not args.no_fundamentals:
        print("Fetching fundamentals (may take a moment)...")
        for t in valid_tickers:
            features[t].fundamentals = source.fetch_fundamentals(t)

    # ---------- Cross-sectional metrics ----------
    print("Computing cross-sectional metrics...")
    metrics_rows = {}
    for t in valid_tickers:
        f = features[t]
        lr = f.log_returns.dropna()
        ar = lr.mean() * TRADING_DAYS
        av = lr.std() * np.sqrt(TRADING_DAYS)
        metrics_rows[t] = {
            "ann_return": ar,
            "ann_vol": av,
            "sharpe": sharpe(lr),
            "sortino": sortino(lr),
            "calmar": calmar_ratio(lr, TRADING_DAYS),
            "max_dd": max_drawdown(f.price),
            "max_dd_duration": max_drawdown_duration(f.price),
            "beta": beta(lr, bench_returns) if len(bench_returns) else np.nan,
            "corr_spy": correlation_to_benchmark(lr, bench_returns) if len(bench_returns) else np.nan,
            "var_95": var_95(lr),
            "cvar_95": cvar_95(lr),
        }
    metrics_df = pd.DataFrame(metrics_rows).T
    print(f"  {len(metrics_df)} tickers; "
          f"return range {metrics_df['ann_return'].min()*100:+.0f}% to "
          f"{metrics_df['ann_return'].max()*100:+.0f}%")

    # ---------- Factor scoring ----------
    print("Computing QVM+L factor scores...")
    scores_df = composite_qvml(features)
    top3 = scores_df.head(3).index.tolist()
    bot3 = scores_df.tail(3).index.tolist()
    print(f"  Top 3 by composite: {top3}")
    print(f"  Bottom 3 by composite: {bot3}")

    # ---------- Mean-variance optimization ----------
    frontier = None
    alt_portfolios = None
    if not args.no_optimization and len(valid_tickers) >= 2:
        try:
            from .optimization import (efficient_frontier, equal_weight_portfolio,
                                        risk_parity_weights)
            print("Computing efficient frontier...")
            held_returns = log_returns_full[valid_tickers]
            frontier = efficient_frontier(held_returns, n_points=30,
                                           rf=RISK_FREE_DEFAULT)
            ew = equal_weight_portfolio(held_returns)
            rp = risk_parity_weights(held_returns)
            alt_portfolios = [ew, rp]
            print(f"  GMV vol={frontier['gmv']['ann_vol']*100:.1f}%; "
                  f"Tangency Sharpe={frontier['tangency']['sharpe']:.2f}")
        except Exception as e:
            print(f"  ! Optimization failed: {e}")

    # ---------- Strategy backtest ----------
    backtest_results = []
    if args.backtest and len(valid_tickers) >= 2:
        print(f"Backtesting {len(STRATEGIES)} strategies...")
        # Naive cash baseline for going-to-cash strategies
        cash_returns = pd.Series(RISK_FREE_DEFAULT / TRADING_DAYS,
                                 index=prices.index)
        held_prices = prices[valid_tickers]
        for sname in STRATEGIES:
            try:
                strat = get_strategy(sname)
                result = run_backtest(strat, held_prices,
                                       initial_capital=args.initial_capital,
                                       cost_bps=args.cost_bps,
                                       cash_returns=cash_returns)
                backtest_results.append(result)
                print(f"  {sname:18s} ann_ret={result.annual_return*100:+6.1f}%  "
                      f"sharpe={result.sharpe:5.2f}  trades={result.n_trades:3d}")
            except Exception as e:
                print(f"  ! {sname} failed: {e}")

    # ---------- News ----------
    news_feed = None
    if not args.no_news:
        print("Fetching news from Yahoo Finance RSS...")
        from .news import fetch_news_feed
        news_feed = fetch_news_feed(valid_tickers, per_ticker=2)
        print(f"  {len(news_feed)} articles in feed")

    # ---------- Assemble report ----------
    print("Assembling HTML report...")
    html = build_html_report(
        valid_tickers, features, prices, bench_returns, args.period,
        metrics_df, scores_df, log_returns_full,
        frontier=frontier, alt_portfolios=alt_portfolios,
        backtest_results=backtest_results,
        initial_capital=args.initial_capital,
        news_feed=news_feed, names=names,
    )
    out_path = OUTPUT_DIR / "report.html"
    out_path.write_text(html, encoding="utf-8")
    print(f"\n✓ Report: {out_path.resolve()}")
    if not args.no_open:
        webbrowser.open(out_path.resolve().as_uri())


if __name__ == "__main__":
    main()
