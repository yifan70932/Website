"""
Mean reversion via Bollinger band reversals.

The natural counterpart to momentum. The classic short-horizon mean
reversion finding (Jegadeesh 1990; Lehmann 1990) is that stocks that
have fallen recently tend to rebound and vice versa, on horizons of
days to weeks.

This implementation: when a stock's price closes below its lower Bollinger
band (price < SMA(20) - 2*sigma), buy it. When it closes above its upper
band, exit. Equal-weight positions across however many stocks are signaling.

ACADEMIC NOTE: Short-horizon mean reversion is one of the more durable
empirical findings in equities, but most of the gross alpha is consumed by
transaction costs in real trading. Bid-ask spreads alone can wipe out the
edge in liquid names.

REFERENCES
==========
- Jegadeesh, N. (1990). Evidence of Predictable Behavior of Security
  Returns. JF.
- Lehmann, B. (1990). Fads, Martingales, and Market Efficiency. QJE.
- Khandani & Lo (2007). What happened to the quants in August 2007?
"""

from __future__ import annotations
import pandas as pd
import numpy as np
from . import Strategy
from dataclasses import dataclass


@dataclass
class MeanReversion(Strategy):
    name: str = "mean_reversion"
    bb_window: int = 20
    bb_sigma: float = 2.0
    description: str = ("Buy when price drops below lower Bollinger band "
                        "(20-day SMA minus 2σ); exit when above upper band. "
                        "Equal-weight across signaling stocks.")

    def generate_signals(self, prices: pd.DataFrame) -> pd.DataFrame:
        sma = prices.rolling(self.bb_window).mean()
        sd = prices.rolling(self.bb_window).std()
        lower = sma - self.bb_sigma * sd
        upper = sma + self.bb_sigma * sd

        # Vectorize the per-ticker position state. We need a stateful loop
        # (entry on close < lower, exit on close > upper) so we collect into
        # NumPy arrays and assign the whole DataFrame at the end. This avoids
        # pandas' chained-assignment trap that silently no-ops on copies.
        signals = pd.DataFrame(0.0, index=prices.index, columns=prices.columns)
        position_array = np.zeros((len(prices), len(prices.columns)))

        for j, col in enumerate(prices.columns):
            in_position = False
            p_arr = prices[col].values
            lo_arr = lower[col].values
            up_arr = upper[col].values
            for i in range(self.bb_window, len(p_arr)):
                if not in_position and not np.isnan(lo_arr[i]) and p_arr[i] < lo_arr[i]:
                    in_position = True
                elif in_position and not np.isnan(up_arr[i]) and p_arr[i] > up_arr[i]:
                    in_position = False
                position_array[i, j] = 1.0 if in_position else 0.0

        signals = pd.DataFrame(position_array, index=prices.index,
                               columns=prices.columns)
        # Convert binary position flags to equal-weight allocation across active stocks
        n_active = signals.sum(axis=1)
        weights = signals.div(n_active.replace(0, np.nan), axis=0).fillna(0.0)
        return weights
