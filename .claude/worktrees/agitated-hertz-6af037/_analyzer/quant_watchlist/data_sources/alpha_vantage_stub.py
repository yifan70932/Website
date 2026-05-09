"""
Alpha Vantage data source — STUB / TEMPLATE.

This is a minimal example showing how to add a paid data source. It is
NOT fully implemented; running it without an API key will raise an error.

To complete it:
  1. Get a free API key at https://www.alphavantage.co/support/#api-key
  2. Set environment variable: export ALPHAVANTAGE_API_KEY=your_key
  3. Install: pip install alpha-vantage
  4. Replace the stub bodies below with real calls
  5. Use it: python -m portfolio_analyzer --data-source alpha_vantage

Free tier: 25 requests/day, 5 requests/minute. Sufficient for ~5 stocks
once a day; pay $50/month for premium if you need more.

Other commercial alternatives worth knowing about (in rough order of
power vs. cost for a learning project):
  - Alpha Vantage: 25 req/day free, $50/mo premium
  - Finnhub:       60 req/min free, $10+/mo for fundamentals
  - FMP:           250 req/day free, $14+/mo for unlimited
  - Polygon.io:    5 req/min free, $30+/mo for real-time
  - EODHD:         20 req/day free, $20+/mo for unlimited
  - Tiingo:        500 req/day free for stocks, $10/mo for IEX

For real institutional work, the next tier is Bloomberg Terminal
(~$25k/yr/seat), FactSet, Refinitiv (LSEG), or S&P Capital IQ.
"""

from __future__ import annotations
import os
import pandas as pd


class AlphaVantageSource:
    name = "alpha_vantage"
    requires_key = True
    free_tier = True
    description = ("Commercial-grade data with free tier (25 req/day). "
                   "Requires API key. STUB IMPLEMENTATION — see source for "
                   "completion instructions.")

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.environ.get("ALPHAVANTAGE_API_KEY")
        if not self.api_key:
            raise RuntimeError(
                "Alpha Vantage requires an API key. Get one free at "
                "alphavantage.co/support/#api-key, then set env var "
                "ALPHAVANTAGE_API_KEY=your_key")

    def fetch_prices(self, tickers: list[str], period: str) -> pd.DataFrame:
        # Real implementation would do something like:
        #
        # from alpha_vantage.timeseries import TimeSeries
        # ts = TimeSeries(key=self.api_key, output_format="pandas")
        # frames = {}
        # for t in tickers:
        #     df, _ = ts.get_daily_adjusted(symbol=t, outputsize="full")
        #     frames[t] = df["5. adjusted close"]
        # prices = pd.DataFrame(frames).sort_index()
        # # Trim to requested period
        # ...
        # return prices
        raise NotImplementedError(
            "Alpha Vantage source is a stub. See data_sources/alpha_vantage_stub.py "
            "for completion instructions, or use --data-source yfinance.")

    def fetch_fundamentals(self, ticker: str) -> dict:
        # Real implementation would call:
        #   from alpha_vantage.fundamentaldata import FundamentalData
        #   fd = FundamentalData(key=self.api_key)
        #   overview, _ = fd.get_company_overview(ticker)
        # and translate the response to the standard dict shape.
        return {}
