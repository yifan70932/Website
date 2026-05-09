"""
Trading strategy plug-ins.

ADDING A NEW STRATEGY
=====================
1. Create a new file in this directory, e.g. my_strategy.py
2. Inherit from Strategy and implement generate_signals()
3. Register it in STRATEGIES below

A strategy converts price history into a target weight series for each
ticker. The backtester simulates trading those weights forward, charging
transaction costs on each rebalance.

THE INTERFACE
=============
generate_signals(prices) -> DataFrame
  Input:  DataFrame indexed by date, one column per ticker = adjusted close
  Output: DataFrame with same index/columns; values are TARGET WEIGHTS
          (0.0 to 1.0). Each row should sum to <= 1.0; any leftover is cash.

The signal at row t is the position you HOLD entering trading day t+1.
This is the standard convention to avoid look-ahead bias: you cannot
trade on information you don't yet have.

CRITICAL — AVOIDING COMMON BIASES
==================================
1. NO LOOK-AHEAD: Compute signal[t] using ONLY prices.iloc[:t+1]. Never
   peek at prices.iloc[t+1] or later. The backtester verifies this by
   shifting the signal series by 1 day before applying.

2. NO SURVIVORSHIP FIX: yfinance only knows about tickers that exist
   today. A momentum strategy backtested on the S&P 500 misses companies
   that went bankrupt — biasing returns upward. The dashboard flags this.

3. TRANSACTION COSTS: The backtester charges a configurable basis-point
   cost on every rebalance. Default is 10 bps (0.10%) per trade, which is
   roughly realistic for retail brokers including spread.

4. PARAMETER OVERFIT: If you tune your strategy's parameters until the
   backtest looks great, you've fit to noise. Always (a) split data into
   train/test, (b) report both, and (c) prefer simple parameters.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
import pandas as pd


@dataclass
class Strategy(ABC):
    """Base class. Override generate_signals."""
    name: str = "base"
    description: str = ""
    rebalance_freq: str = "M"  # 'D'=daily, 'W'=weekly, 'M'=monthly
    params: dict = field(default_factory=dict)

    @abstractmethod
    def generate_signals(self, prices: pd.DataFrame) -> pd.DataFrame:
        """
        Return target weights per ticker per day.
        Must be causal: signal[t] depends only on prices[:t+1].
        """
        ...


from .buy_and_hold import BuyAndHold
from .sma_crossover import SMACrossover
from .momentum import Momentum
from .equal_weight import EqualWeight
from .risk_parity import RiskParity
from .mean_reversion import MeanReversion

STRATEGIES: dict[str, type[Strategy]] = {
    "buy_and_hold": BuyAndHold,
    "equal_weight": EqualWeight,
    "risk_parity": RiskParity,
    "sma_crossover": SMACrossover,
    "momentum": Momentum,
    "mean_reversion": MeanReversion,
}


def get_strategy(name: str, **kwargs) -> Strategy:
    if name not in STRATEGIES:
        raise ValueError(f"Unknown strategy '{name}'. Available: {list(STRATEGIES)}")
    return STRATEGIES[name](**kwargs)
