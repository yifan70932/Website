"""
Data source plug-ins. Adding a new source:

    1. Create yourname_source.py inheriting from PriceSource
    2. Implement fetch_prices() and (optionally) fetch_fundamentals()
    3. Register it in DATA_SOURCES below

The CLI flag --data-source NAME picks which source to use.

Comparison of options shipped with the package:

    yfinance:  Free, no key, ~30 yrs daily data, US + intl. UNRELIABLE in
               production (Yahoo can change endpoints anytime). Fundamentals
               via .info are not point-in-time. Default.
    fred:      Federal Reserve Economic Data. Macroeconomic series only —
               yields, CPI, unemployment, etc. NOT for stock prices. No key
               needed for basic use via pandas-datareader. Use ALONGSIDE
               yfinance for risk-free rate, term spreads, etc.
    alpha_vantage: Stub showing how to add a paid provider. Free tier is
                   25 requests/day. Requires API key.

For more (FMP, Polygon, EODHD, Finnhub), see data_sources/README in the
shipped repo or the comparison panel in the dashboard.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
import pandas as pd
from typing import Optional


class PriceSource(ABC):
    """Base class for price data providers."""
    name: str = "base"
    requires_key: bool = False
    free_tier: bool = True
    description: str = ""

    @abstractmethod
    def fetch_prices(self, tickers: list[str], period: str) -> pd.DataFrame:
        """Return DataFrame with date index and one column per ticker."""
        ...

    def fetch_fundamentals(self, ticker: str) -> dict:
        """Optional. Return dict of fundamental ratios. Default: empty."""
        return {}


# Registry — populated by submodule imports
from .yfinance_source import YFinanceSource
from .fred_source import FREDSource
from .alpha_vantage_stub import AlphaVantageSource

DATA_SOURCES: dict[str, type[PriceSource]] = {
    "yfinance": YFinanceSource,
    "fred": FREDSource,
    "alpha_vantage": AlphaVantageSource,
}


def get_source(name: str) -> PriceSource:
    if name not in DATA_SOURCES:
        raise ValueError(f"Unknown data source '{name}'. "
                         f"Available: {list(DATA_SOURCES)}")
    return DATA_SOURCES[name]()
