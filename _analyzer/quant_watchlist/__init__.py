"""
Quant Watchlist Analyzer v1
============================

A cross-sectional quantitative analysis tool for a watchlist of stocks/ETFs.
Different from a portfolio analyzer — this answers the questions:

  - Across these candidates, which look attractive on momentum/value/quality/low-vol?
  - How are they correlated? Which are duplicative; which are diversifying?
  - What's the relative-performance picture?
  - What does the long-only efficient frontier across this universe look like?
  - Which factor exposures dominate?
  - Where do single-name backtests of standard factor strategies land?

Usage:
    python -m quant_watchlist                            # default watchlist
    python -m quant_watchlist --tickers VOO QQQ NVDA TSLA
    python -m quant_watchlist --period 5y --backtest

The default watchlist contains broadly-traded large-cap US equities and a
few ETFs spanning indices, sectors, and international exposures.
"""

__version__ = "1.0.0"
