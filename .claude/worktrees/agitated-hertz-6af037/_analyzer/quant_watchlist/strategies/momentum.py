"""
12-1 Momentum: hold the top-half of tickers by past 12-month return,
skipping the most recent month (the standard academic specification).

LOGIC:
  Once a month:
    For each ticker, compute return over the past 252 trading days,
    EXCLUDING the most recent 21 days (Jegadeesh-Titman 12-1 convention).
    Rank tickers; hold the top half equal-weighted.

EVIDENCE:
  Momentum is one of the most robust documented anomalies in finance:
    Jegadeesh & Titman (1993): original cross-sectional momentum paper
    Carhart (1997): added momentum as a 4th Fama-French factor
    Asness, Moskowitz & Pedersen (2013): momentum exists across asset
      classes and countries

  HOWEVER: momentum has periodic catastrophic crashes (Daniel & Moskowitz
  2016 show momentum can lose >50% in months around market reversals like
  2009). It also doesn't work consistently on small portfolios; the
  cross-sectional ranking needs a wider universe (typically 100+ stocks).
  Backtesting on your 5-stock portfolio is essentially data-mining.

  References:
    Jegadeesh & Titman (1993) — Journal of Finance
    Carhart (1997) — Journal of Finance
    Asness, Moskowitz & Pedersen (2013) — Journal of Finance
    Daniel & Moskowitz (2016) — Journal of Financial Economics, "Momentum crashes"
"""

from __future__ import annotations
import pandas as pd
import numpy as np
from . import Strategy
from dataclasses import dataclass, field


@dataclass
class Momentum(Strategy):
    name: str = "momentum"
    description: str = ("Top-half by 12-1 month total return, monthly "
                        "rebalance, equal-weighted within the top half.")
    rebalance_freq: str = "M"
    params: dict = field(default_factory=lambda: {
        "lookback": 252,  # 12 months of trading days
        "skip": 21,       # skip last 1 month (the "12-1" convention)
        "top_frac": 0.5,  # top half
    })

    def generate_signals(self, prices: pd.DataFrame) -> pd.DataFrame:
        lookback = self.params.get("lookback", 252)
        skip = self.params.get("skip", 21)
        top_frac = self.params.get("top_frac", 0.5)
        n_tickers = len(prices.columns)
        n_top = max(1, int(round(n_tickers * top_frac)))

        # 12-1 momentum: return from t-lookback to t-skip
        # i.e., price at t-skip / price at t-lookback - 1
        ret_12_1 = prices.shift(skip) / prices.shift(lookback) - 1.0

        # Build weights: NaN everywhere except rebalance dates, then ffill.
        # Using NaN (not 0) as the "no signal today" marker means ffill
        # propagates the LAST REBALANCE'S FULL WEIGHT VECTOR forward —
        # which is what "hold between rebalances" actually means.
        weights = pd.DataFrame(np.nan, index=prices.index, columns=prices.columns)
        rebalance_dates = prices.resample("ME").last().index
        for date in rebalance_dates:
            if date not in ret_12_1.index:
                avail = ret_12_1.index[ret_12_1.index <= date]
                if len(avail) == 0:
                    continue
                date = avail[-1]
            today_returns = ret_12_1.loc[date]
            if today_returns.dropna().empty:
                continue
            top = today_returns.nlargest(n_top).index
            w = pd.Series(0.0, index=prices.columns)
            w[top] = 1.0 / len(top)
            weights.loc[date] = w  # sets ALL columns (winners = 1/n_top, losers = 0)

        # Forward-fill per-column so each row reflects the most recent full
        # weight vector. Any leading NaN (before first rebalance) → 0 (cash).
        weights = weights.ffill().fillna(0.0)
        return weights
