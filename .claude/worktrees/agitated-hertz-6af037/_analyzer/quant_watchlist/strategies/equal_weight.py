"""
Equal-weight rebalanced (1/N).

DeMiguel, Garlappi & Uppal (2009, RFS) showed that the naive 1/N portfolio
is surprisingly hard to beat out-of-sample by sample-based mean-variance
optimization, because estimation error in expected returns is so severe.

This is the natural counterpart to buy-and-hold: same equal-weight starting
point, but rebalanced periodically back to equal weights so winners are
trimmed and losers added to (a small "rebalancing premium" comes from this).
"""

from __future__ import annotations
import pandas as pd
import numpy as np
from . import Strategy
from dataclasses import dataclass, field


@dataclass
class EqualWeight(Strategy):
    name: str = "equal_weight"
    rebalance_days: int = 21  # roughly monthly
    description: str = ("Equal-weight all holdings, rebalanced monthly. "
                        "DeMiguel/Garlappi/Uppal (2009) show this is hard "
                        "to beat out-of-sample due to estimation error.")

    def generate_signals(self, prices: pd.DataFrame) -> pd.DataFrame:
        n = len(prices.columns)
        target = 1.0 / n
        weights = pd.DataFrame(0.0, index=prices.index, columns=prices.columns)
        # On rebalance days, set weights back to 1/N. Between rebalances,
        # weights drift with prices.
        for i, date in enumerate(prices.index):
            if i % self.rebalance_days == 0:
                weights.iloc[i] = target
            else:
                weights.iloc[i] = np.nan  # let backtester carry forward / drift
        # Forward-fill NaN with previous explicit row's drifted weights
        # The backtester's signal-shift logic + ffill handles this; we just
        # need to make sure the rebalance days have explicit values.
        return weights.ffill()
