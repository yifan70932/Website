"""
FRED (Federal Reserve Economic Data) source.

Use this for MACRO data — yields, inflation, unemployment, GDP — not stocks.
The script uses FRED automatically (when --use-fred is set) to fetch the
risk-free rate (3-mo T-bill), which makes Sharpe ratios more accurate than
the hardcoded 4.5% default.

For comprehensive use, get a free API key at https://fred.stlouisfed.org/docs/api/
and pass FRED_API_KEY in env (the fredapi package will pick it up).
For basic series, pandas-datareader works without a key.

Common FRED series codes:
    DGS3MO     — 3-month Treasury yield (risk-free rate proxy)
    DGS10      — 10-year Treasury yield
    T10Y2Y     — Term spread (10y - 2y), recession indicator when negative
    UNRATE     — Unemployment rate
    CPIAUCSL   — CPI (inflation)
    VIXCLS     — VIX volatility index
    DFF        — Fed funds rate
    BAMLH0A0HYM2 — High-yield credit spread
"""

from __future__ import annotations
import pandas as pd
from typing import Optional


class FREDSource:
    name = "fred"
    requires_key = False  # Basic use; key recommended for heavy use
    free_tier = True
    description = ("Federal Reserve Economic Data. Macro time series only "
                   "(yields, CPI, unemployment, etc). Not for stock prices. "
                   "Use alongside yfinance for risk-free rate, term spreads, "
                   "and macroeconomic context.")

    def fetch_prices(self, tickers: list[str], period: str) -> pd.DataFrame:
        """
        For FRED, 'tickers' are series codes like 'DGS3MO', 'CPIAUCSL'.
        Returned values are levels (yields in percent, indexes raw).
        """
        try:
            from pandas_datareader import data as pdr
        except Exception as e:
            raise RuntimeError(
                "FRED source requires pandas-datareader. "
                "pip install pandas-datareader") from e

        end = pd.Timestamp.today()
        period_days = {"1mo": 30, "3mo": 90, "6mo": 180, "1y": 365,
                       "2y": 730, "5y": 1825, "10y": 3650,
                       "max": 7300}.get(period, 730)
        start = end - pd.Timedelta(days=int(period_days))

        out = {}
        for code in tickers:
            try:
                series = pdr.DataReader(code, "fred", start, end)
                # pandas-datareader returns DataFrame with one column = code
                out[code] = series.iloc[:, 0]
            except Exception as e:
                print(f"  ! FRED fetch failed for {code}: {e}")
        if not out:
            return pd.DataFrame()
        return pd.DataFrame(out).ffill()

    @staticmethod
    def fetch_risk_free_rate(period: str = "1y") -> Optional[float]:
        """
        Returns the latest 3-month T-bill yield as a decimal (e.g., 0.045 for 4.5%).
        If the fetch fails, returns None and caller should fall back to a default.
        """
        try:
            from pandas_datareader import data as pdr
        except Exception:
            return None
        try:
            end = pd.Timestamp.today()
            start = end - pd.Timedelta(days=30)
            df = pdr.DataReader("DGS3MO", "fred", start, end)
            latest = df.iloc[:, 0].dropna()
            if len(latest) == 0:
                return None
            return float(latest.iloc[-1]) / 100.0  # FRED reports as percent
        except Exception:
            return None

    @staticmethod
    def fetch_daily_cash_returns(period: str = "2y") -> Optional[pd.Series]:
        """
        Returns a Series of DAILY cash returns over the given lookback,
        indexed by date. Used by the backtester to credit unallocated
        weight at the historical risk-free rate rather than 0%.

        Source: DGS3MO (3-month Treasury yield) is used as a proxy for
        cash returns because (a) it's free and reliable from FRED,
        (b) high-yield savings rates closely track the Fed Funds rate,
        which closely tracks the 3-mo T-bill, so DGS3MO is a defensible
        proxy for "cash earning current yield." A few-basis-point spread
        between actual bank APYs and T-bill yields won't change conclusions
        for a typical retail portfolio.

        Returns None if the fetch fails; caller should pass None to backtest
        (which makes cash earn 0% — conservative).
        """
        try:
            from pandas_datareader import data as pdr
        except Exception:
            return None
        try:
            end = pd.Timestamp.today()
            period_days = {"1mo": 30, "3mo": 90, "6mo": 180, "1y": 365,
                           "2y": 730, "5y": 1825, "10y": 3650,
                           "max": 7300}.get(period, 730)
            start = end - pd.Timedelta(days=int(period_days * 1.2))
            df = pdr.DataReader("DGS3MO", "fred", start, end)
            yields_pct = df.iloc[:, 0].dropna()
            # Yield is annualized in percent; convert to daily decimal.
            # 252 trading days/year is the standard finance convention.
            daily = (yields_pct / 100.0) / 252.0
            daily.index = pd.to_datetime(daily.index)
            return daily
        except Exception as e:
            print(f"  ! FRED daily cash rate fetch failed: {e}")
            return None
