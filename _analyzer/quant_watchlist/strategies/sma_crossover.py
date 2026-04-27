"""
Simple Moving Average crossover: a textbook trend-following rule.

LOGIC:
  For each ticker:
    Compute fast_sma (default 50-day) and slow_sma (default 200-day).
    HOLD when fast_sma > slow_sma (uptrend, "golden cross")
    OUT (cash) when fast_sma < slow_sma (downtrend, "death cross")
  Equal weight across all currently-held tickers.

EVIDENCE:
  This is one of the oldest and most-tested technical rules. Brock,
  Lakonishok & LeBaron (1992) found it profitable on the DJIA 1897-1986.
  Sullivan, Timmermann & White (1999) showed those results don't survive
  data-snooping correction. Modern out-of-sample tests (Bajgrowicz &
  Scaillet 2012) find no consistent edge after costs in liquid US equities.

  Conclusion: the strategy is included as an instructive example of how
  technical rules look on paper vs. in honest backtests. Expect to roughly
  match buy-and-hold gross of fees, and underperform after costs.

  References (all in the dashboard literature library):
    Brock, Lakonishok & LeBaron (1992) — original DJIA test
    Sullivan, Timmermann & White (1999) — data-snooping correction
    Bajgrowicz & Scaillet (2012) — out-of-sample failure
"""

from __future__ import annotations
import pandas as pd
import numpy as np
from . import Strategy
from dataclasses import dataclass, field


@dataclass
class SMACrossover(Strategy):
    name: str = "sma_crossover"
    description: str = ("Hold ticker when 50-day SMA above 200-day SMA, "
                        "else cash. Equal-weight across held tickers.")
    rebalance_freq: str = "D"
    params: dict = field(default_factory=lambda: {"fast": 50, "slow": 200})

    def generate_signals(self, prices: pd.DataFrame) -> pd.DataFrame:
        fast = self.params.get("fast", 50)
        slow = self.params.get("slow", 200)

        # Causal moving averages: rolling().mean() at row t uses rows [t-w+1, t]
        sma_fast = prices.rolling(fast, min_periods=fast).mean()
        sma_slow = prices.rolling(slow, min_periods=slow).mean()

        # Boolean: is each ticker in an uptrend today?
        in_trend = (sma_fast > sma_slow).fillna(False)

        # Equal weight across tickers currently in trend.
        # If 0 tickers in trend, we hold cash (weights all 0).
        n_in = in_trend.sum(axis=1).replace(0, np.nan)
        weights = in_trend.div(n_in, axis=0).fillna(0.0)
        return weights
