"""
Risk parity (naive / inverse-volatility version).

Each asset receives a weight inversely proportional to its volatility,
so each asset contributes roughly equally to portfolio variance. This is
exactly equal-risk-contribution when assets are uncorrelated; for typical
correlated portfolios it's a close approximation that requires no
optimization.

Risk parity has been popularized by Bridgewater (All Weather, 1996) and
AQR (since the 2000s). The intuition: a 60/40 stock/bond portfolio has
roughly 90% of its risk from the stock sleeve, so it's not actually
balanced in any meaningful sense — risk parity fixes that.

REFERENCES
==========
- Maillard, Roncalli, Teïletche (2010). The Properties of Equally Weighted
  Risk Contribution Portfolios. JPM 36(4).
- Asness, Frazzini & Pedersen (2012). Leverage Aversion and Risk Parity. FAJ.
"""

from __future__ import annotations
import pandas as pd
import numpy as np
from . import Strategy
from dataclasses import dataclass


@dataclass
class RiskParity(Strategy):
    name: str = "risk_parity"
    rebalance_days: int = 21
    vol_lookback: int = 60  # days of history for vol estimate
    description: str = ("Inverse-volatility weighting: each asset gets weight "
                        "1/σ, normalized to sum to 1. Rebalanced monthly. "
                        "Approximates equal risk contribution.")

    def generate_signals(self, prices: pd.DataFrame) -> pd.DataFrame:
        log_returns = np.log(prices / prices.shift(1))
        n = len(prices.columns)
        weights = pd.DataFrame(0.0, index=prices.index, columns=prices.columns)

        for i, date in enumerate(prices.index):
            if i < self.vol_lookback:
                # Not enough history yet — use equal weight as warmup
                weights.iloc[i] = 1.0 / n
                continue
            if i % self.rebalance_days != 0:
                weights.iloc[i] = np.nan  # drift between rebalances
                continue
            # Estimate vol from recent window
            window = log_returns.iloc[i - self.vol_lookback : i]
            vols = window.std().values
            # Guard against zero or nan
            vols = np.where((vols > 0) & np.isfinite(vols), vols, vols[np.isfinite(vols) & (vols > 0)].mean() if np.any(np.isfinite(vols) & (vols > 0)) else 1e-4)
            inv_vol = 1.0 / vols
            w = inv_vol / inv_vol.sum()
            weights.iloc[i] = w
        return weights.ffill().fillna(1.0 / n)
