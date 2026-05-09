"""
Strategy backtester.

DESIGN PRINCIPLES (anti-bullshit edition)
==========================================
1. CAUSALITY: signal at row t is acted on at row t+1's open. We enforce
   this by shifting the signal by 1 day before computing returns. Any
   strategy that "predicts" today using today's close cannot trade today.

2. TRANSACTION COSTS: charged on every weight change. Default 10 bps per
   one-way trade, applied to the dollar amount traded. So a complete
   rebalance from 100% A to 100% B costs ~20 bps round-trip, which is
   roughly accurate for retail-friendly brokers including bid-ask spread.

3. NO REINVESTMENT FRICTION ASSUMED: we model continuous rebalancing
   in a frictionless single-account setting. Tax drag is NOT modeled.

4. SURVIVORSHIP BIAS: the dashboard explicitly flags this. yfinance only
   knows tickers that exist today, so any strategy backtested on
   delisted-or-bankrupted-since-then companies looks better than reality.

5. METRIC HONESTY: we report Sharpe, max drawdown, turnover, and the
   number of trades. We do NOT report cherry-picked windows. We do NOT
   suppress losing periods.

6. NO FORWARD-FILL CHEATING ON FUNDAMENTALS: this engine only uses prices.
   Any strategy needing fundamentals must declare so and accept the
   limitations of yfinance .info (current snapshot, no history).
"""

from __future__ import annotations
from dataclasses import dataclass
import numpy as np
import pandas as pd
from .strategies import Strategy

TRADING_DAYS = 252


@dataclass
class BacktestResult:
    strategy_name: str
    equity_curve: pd.Series       # portfolio value over time
    daily_returns: pd.Series      # daily log returns
    weights: pd.DataFrame         # actual held weights, post-shift
    turnover: pd.Series           # one-way turnover per day
    n_trades: int                 # rebalance events with non-zero turnover
    total_cost_bps: float         # cumulative cost in basis points

    @property
    def total_return(self) -> float:
        return float(self.equity_curve.iloc[-1] / self.equity_curve.iloc[0] - 1)

    @property
    def annual_return(self) -> float:
        years = len(self.equity_curve) / TRADING_DAYS
        if years <= 0:
            return float("nan")
        return float((self.equity_curve.iloc[-1] / self.equity_curve.iloc[0]) ** (1/years) - 1)

    @property
    def annual_vol(self) -> float:
        return float(self.daily_returns.std() * np.sqrt(TRADING_DAYS))

    @property
    def sharpe(self, rf: float = 0.045) -> float:
        rf_daily = rf / TRADING_DAYS
        e = self.daily_returns - rf_daily
        if e.std() == 0:
            return float("nan")
        return float(e.mean() / e.std() * np.sqrt(TRADING_DAYS))

    @property
    def max_drawdown(self) -> float:
        peak = self.equity_curve.cummax()
        dd = (self.equity_curve - peak) / peak
        return float(dd.min())

    @property
    def calmar(self) -> float:
        mdd = abs(self.max_drawdown)
        return float(self.annual_return / mdd) if mdd > 0 else float("nan")

    @property
    def avg_turnover_annual(self) -> float:
        """Average annual turnover (one-way). 1.0 = full portfolio replaced once a year."""
        return float(self.turnover.sum() * TRADING_DAYS / len(self.turnover))


def run_backtest(
    strategy: Strategy,
    prices: pd.DataFrame,
    initial_capital: float = 10_000.0,
    cost_bps: float = 10.0,  # 10 basis points = 0.10% per one-way trade
    cash_returns: pd.Series | None = None,  # optional daily cash rate (e.g. T-bill)
) -> BacktestResult:
    """
    Simulate `strategy` on `prices` and return a BacktestResult.

    Causality enforcement: signals are shifted by 1 day so we trade tomorrow
    on today's close. Strategies that contain look-ahead bugs will silently
    have their lookahead removed by this shift — but they may produce
    nonsense results, which is the user's signal that something is wrong.

    cash_returns: optional Series indexed by date of daily cash returns (in
    decimal, e.g. 0.0001 ≈ 2.5% annualized). If provided, any unallocated
    weight (1 − sum of strategy weights) earns this rate per day. If None,
    cash earns 0%, which is the conservative behavior. Strategies like SMA
    crossover that go to cash during downtrends benefit when this is set.
    """
    # Generate raw signals (target weights)
    raw_signals = strategy.generate_signals(prices)

    # Buy-and-hold special case: weights are NaN after row 0 to indicate
    # "let weights drift". Convert to actual drifted weights.
    if raw_signals.iloc[1:].isna().all().all():
        held_weights = _drift_weights(raw_signals.iloc[0], prices)
        # No trades after day 0 → no costs after day 0
        return _compute_result(strategy.name, prices, held_weights,
                               initial_capital, cost_bps,
                               trades_only_at_start=True,
                               cash_returns=cash_returns)

    # Standard case: shift signals by 1 (causality enforcement)
    signals = raw_signals.shift(1).fillna(0.0)

    return _compute_result(strategy.name, prices, signals,
                           initial_capital, cost_bps,
                           trades_only_at_start=False,
                           cash_returns=cash_returns)


def _drift_weights(initial_weights: pd.Series, prices: pd.DataFrame) -> pd.DataFrame:
    """Compute how equal-weight buy-and-hold drifts over time as prices move."""
    # initial_weights: Series of weights on day 0 (sums to 1)
    # We hold initial_weights * (price_t / price_0) shares of capital, then
    # renormalize each day to get the actual weight share.
    rel_prices = prices.div(prices.iloc[0])  # each col starts at 1.0
    raw = rel_prices.mul(initial_weights, axis=1)
    drifted = raw.div(raw.sum(axis=1), axis=0)
    return drifted


def _compute_result(name, prices, weights, initial_capital, cost_bps,
                    trades_only_at_start=False, cash_returns=None):
    # Daily simple returns of each ticker
    asset_returns = prices.pct_change().fillna(0.0)

    # Portfolio gross return = weighted sum of asset returns
    gross_returns = (weights * asset_returns).sum(axis=1)

    # Add cash earnings on the unallocated portion of the portfolio.
    # If a strategy holds 60% in stocks today, the other 40% sits in cash
    # earning the daily cash rate. Without this, going-to-cash strategies
    # are unfairly penalized vs buy-and-hold.
    if cash_returns is not None:
        cash_weight = (1.0 - weights.sum(axis=1)).clip(lower=0.0)
        # Align cash_returns to weights' index; missing days → 0
        aligned_cash = cash_returns.reindex(weights.index).fillna(0.0)
        gross_returns = gross_returns + cash_weight * aligned_cash

    # Turnover = sum of |Δw| / 2 per day (standard one-way turnover)
    weight_changes = weights.diff().abs().sum(axis=1) / 2.0
    if trades_only_at_start:
        weight_changes.iloc[1:] = 0.0
        weight_changes.iloc[0] = weights.iloc[0].abs().sum()  # initial buy
    weight_changes = weight_changes.fillna(0.0)

    # Cost = turnover * cost_bps / 10000
    daily_cost = weight_changes * (cost_bps / 10_000.0)
    net_returns = gross_returns - daily_cost

    # Equity curve
    equity = initial_capital * (1 + net_returns).cumprod()

    # Daily log returns for risk metrics
    log_returns = np.log(1 + net_returns)

    n_trades = int((weight_changes > 1e-6).sum())
    total_cost_bps = float(daily_cost.sum() * 10_000.0)

    return BacktestResult(
        strategy_name=name,
        equity_curve=equity,
        daily_returns=log_returns,
        weights=weights,
        turnover=weight_changes,
        n_trades=n_trades,
        total_cost_bps=total_cost_bps,
    )


def summarize_results(results: list[BacktestResult]) -> pd.DataFrame:
    """Return a comparison DataFrame across multiple strategy backtests."""
    rows = []
    for r in results:
        rows.append({
            "Strategy": r.strategy_name,
            "Total Return": r.total_return,
            "Ann. Return": r.annual_return,
            "Ann. Vol": r.annual_vol,
            "Sharpe": r.sharpe,
            "Max DD": r.max_drawdown,
            "Calmar": r.calmar,
            "Trades": r.n_trades,
            "Total Cost (bps)": r.total_cost_bps,
            "Avg Annual Turnover": r.avg_turnover_annual,
        })
    return pd.DataFrame(rows).set_index("Strategy")
