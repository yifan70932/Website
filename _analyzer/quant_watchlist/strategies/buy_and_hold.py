"""
Buy-and-hold: equal-weighted, never rebalance after initial buy.

This is THE benchmark to beat. The single most robust empirical finding in
finance is that simple low-cost buy-and-hold of a diversified index usually
beats active strategies after costs (Bogle 2014; Fama & French 2010; SPIVA).

If your fancy strategy doesn't beat buy-and-hold over a long horizon, your
fancy strategy is just adding cost and risk for no benefit.
"""

from __future__ import annotations
import pandas as pd
import numpy as np
from . import Strategy
from dataclasses import dataclass


@dataclass
class BuyAndHold(Strategy):
    name: str = "buy_and_hold"
    description: str = ("Equal-weight all tickers at day 0, never rebalance. "
                        "The benchmark to beat — usually unbeatable by simple rules.")

    def generate_signals(self, prices: pd.DataFrame) -> pd.DataFrame:
        """All weight allocated equally on day 0; held forever."""
        n = len(prices.columns)
        weights = pd.DataFrame(0.0, index=prices.index, columns=prices.columns)
        # Set initial weights on first row only; backtester will treat
        # "buy and hold" as a one-time allocation that drifts with prices.
        weights.iloc[0] = 1.0 / n
        # For daily rebalancing back to equal weight, fill all rows. But true
        # B&H lets winners run. We model true B&H: weights are NaN after row 0
        # to signal "don't rebalance"; backtester interprets this.
        weights.iloc[1:] = np.nan
        return weights
