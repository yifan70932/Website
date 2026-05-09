"""
Mean-variance optimization (Markowitz 1952) and the efficient frontier.

THEORY
======
Given N assets with expected returns μ and covariance matrix Σ, the set of
portfolios that minimize variance for any given target return forms a curve
in (volatility, return) space called the *efficient frontier*. Two special
portfolios on this frontier:

  - Global minimum variance portfolio (GMV): the leftmost point on the
    frontier; the lowest-volatility allocation possible from these assets.
  - Tangency portfolio: the portfolio that maximizes Sharpe ratio
    (rf, point) - drawn as a line from the risk-free rate, the tangent to
    the frontier touches at this point.

Modern Portfolio Theory's headline claim is that a rational investor should
hold the tangency portfolio (in some leverage ratio combined with cash),
regardless of risk preferences. In practice, mean-variance optimization is
notoriously sensitive to estimation error in μ — small changes in expected
returns produce huge swings in optimal weights (Michaud 1989, "The Markowitz
Optimization Enigma"). This is why practitioners use shrinkage (Ledoit-Wolf
2003), Black-Litterman, or constraints to stabilize the result.

For this educational tool: we use historical sample mean and covariance.
Constraints: long-only, weights in [0, 1] summing to 1. This matches what a
retail investor without short-sale or leverage access can actually hold.

REFERENCES
==========
- Markowitz, H. (1952). Portfolio Selection. JF.
- Sharpe, W. (1964). Capital Asset Prices. JF.
- Michaud, R. (1989). The Markowitz Optimization Enigma. FAJ.
- Ledoit, O. & Wolf, M. (2003). Honey, I Shrunk the Sample Covariance Matrix. JPM.
"""

from __future__ import annotations
import numpy as np
import pandas as pd
from scipy.optimize import minimize
from typing import Optional


def _annualize(returns_df: pd.DataFrame, trading_days: int = 252):
    """Return annualized mean vector and covariance matrix."""
    mu = returns_df.mean().values * trading_days
    sigma = returns_df.cov().values * trading_days
    return mu, sigma


def portfolio_stats(weights: np.ndarray, mu: np.ndarray, sigma: np.ndarray,
                    rf: float = 0.045):
    """Return (annualized return, annualized vol, Sharpe) for given weights."""
    ret = float(weights @ mu)
    vol = float(np.sqrt(weights @ sigma @ weights))
    sharpe = (ret - rf) / vol if vol > 0 else float("nan")
    return ret, vol, sharpe


def min_variance_portfolio(returns_df: pd.DataFrame,
                            trading_days: int = 252) -> dict:
    """
    Solve for the global minimum variance portfolio (GMV).

    min_w   w' Σ w
    s.t.    sum(w) = 1
            0 <= w_i <= 1   (long-only)

    Returns dict with weights, ann_return, ann_vol, sharpe, tickers.
    """
    mu, sigma = _annualize(returns_df, trading_days)
    n = len(mu)
    if n == 1:
        return {"tickers": list(returns_df.columns), "weights": np.array([1.0]),
                "ann_return": float(mu[0]), "ann_vol": float(np.sqrt(sigma[0, 0])),
                "sharpe": float("nan"), "label": "Min variance"}

    x0 = np.full(n, 1.0 / n)
    bounds = [(0.0, 1.0)] * n
    constraints = [{"type": "eq", "fun": lambda w: w.sum() - 1.0}]

    def objective(w):
        return float(w @ sigma @ w)

    result = minimize(objective, x0, method="SLSQP", bounds=bounds,
                      constraints=constraints, options={"ftol": 1e-10, "maxiter": 200})

    w = result.x if result.success else x0
    w = np.clip(w, 0, 1)
    w = w / w.sum()  # normalize after clipping
    ret, vol, sh = portfolio_stats(w, mu, sigma)
    return {"tickers": list(returns_df.columns), "weights": w,
            "ann_return": ret, "ann_vol": vol, "sharpe": sh,
            "label": "Min variance"}


def max_sharpe_portfolio(returns_df: pd.DataFrame, rf: float = 0.045,
                          trading_days: int = 252) -> dict:
    """
    Solve for the tangency portfolio (max Sharpe ratio).

    max_w   (w'μ - rf) / sqrt(w'Σw)

    Implemented as min of negative Sharpe.
    """
    mu, sigma = _annualize(returns_df, trading_days)
    n = len(mu)
    if n == 1:
        return {"tickers": list(returns_df.columns), "weights": np.array([1.0]),
                "ann_return": float(mu[0]), "ann_vol": float(np.sqrt(sigma[0, 0])),
                "sharpe": (mu[0] - rf) / np.sqrt(sigma[0, 0]) if sigma[0, 0] > 0 else float("nan"),
                "label": "Max Sharpe"}

    x0 = np.full(n, 1.0 / n)
    bounds = [(0.0, 1.0)] * n
    constraints = [{"type": "eq", "fun": lambda w: w.sum() - 1.0}]

    def neg_sharpe(w):
        ret = w @ mu
        vol = np.sqrt(w @ sigma @ w)
        if vol <= 0:
            return 1e6
        return -(ret - rf) / vol

    result = minimize(neg_sharpe, x0, method="SLSQP", bounds=bounds,
                      constraints=constraints, options={"ftol": 1e-10, "maxiter": 300})

    w = result.x if result.success else x0
    w = np.clip(w, 0, 1)
    w = w / w.sum()
    ret, vol, sh = portfolio_stats(w, mu, sigma, rf)
    return {"tickers": list(returns_df.columns), "weights": w,
            "ann_return": ret, "ann_vol": vol, "sharpe": sh,
            "label": "Max Sharpe (tangency)"}


def efficient_frontier(returns_df: pd.DataFrame, n_points: int = 30,
                        rf: float = 0.045, trading_days: int = 252) -> dict:
    """
    Compute the long-only efficient frontier.

    Sweeps target returns from min asset return to max asset return,
    solving min-variance for each. Returns arrays for plotting.

    Also includes the GMV portfolio, max-Sharpe portfolio, and the
    individual assets as reference points.
    """
    mu, sigma = _annualize(returns_df, trading_days)
    n = len(mu)
    tickers = list(returns_df.columns)

    if n < 2:
        return {"frontier_returns": np.array([mu[0]]),
                "frontier_vols": np.array([np.sqrt(sigma[0, 0])]),
                "tickers": tickers, "asset_returns": mu,
                "asset_vols": np.sqrt(np.diag(sigma)),
                "gmv": min_variance_portfolio(returns_df, trading_days),
                "tangency": max_sharpe_portfolio(returns_df, rf, trading_days)}

    target_returns = np.linspace(mu.min() * 1.02, mu.max() * 0.98, n_points)
    frontier_vols = []
    frontier_rets = []
    frontier_weights = []

    for tgt in target_returns:
        x0 = np.full(n, 1.0 / n)
        bounds = [(0.0, 1.0)] * n
        constraints = [
            {"type": "eq", "fun": lambda w: w.sum() - 1.0},
            {"type": "eq", "fun": lambda w, t=tgt: w @ mu - t},
        ]
        result = minimize(lambda w: w @ sigma @ w, x0, method="SLSQP",
                          bounds=bounds, constraints=constraints,
                          options={"ftol": 1e-10, "maxiter": 200})
        if result.success:
            w = np.clip(result.x, 0, 1)
            w = w / w.sum()
            ret, vol, _ = portfolio_stats(w, mu, sigma)
            frontier_rets.append(ret)
            frontier_vols.append(vol)
            frontier_weights.append(w)

    return {
        "frontier_returns": np.array(frontier_rets),
        "frontier_vols": np.array(frontier_vols),
        "frontier_weights": frontier_weights,
        "tickers": tickers,
        "asset_returns": mu,
        "asset_vols": np.sqrt(np.diag(sigma)),
        "gmv": min_variance_portfolio(returns_df, trading_days),
        "tangency": max_sharpe_portfolio(returns_df, rf, trading_days),
        "rf": rf,
    }


def current_portfolio_position(weights: np.ndarray, returns_df: pd.DataFrame,
                                rf: float = 0.045,
                                trading_days: int = 252) -> dict:
    """
    Compute the (return, vol, Sharpe) of the user's *current* portfolio,
    so we can plot it on the same axes as the efficient frontier and show
    them how far from optimal their actual allocation is.
    """
    mu, sigma = _annualize(returns_df, trading_days)
    ret, vol, sh = portfolio_stats(weights, mu, sigma, rf)
    return {"ann_return": ret, "ann_vol": vol, "sharpe": sh,
            "weights": weights, "tickers": list(returns_df.columns),
            "label": "Your portfolio"}


def risk_parity_weights(returns_df: pd.DataFrame,
                         trading_days: int = 252,
                         max_iter: int = 100) -> dict:
    """
    Compute risk parity weights (a.k.a. equal risk contribution).

    Each asset contributes equally to portfolio variance. Solved iteratively
    using the Spinu (2013) closed-form for diagonal Σ as a starting point,
    then refined.

    For a learning tool we use the simple inverse-volatility approximation,
    which is exact when assets are uncorrelated and a good starting point
    otherwise. This is what's commonly called "naive risk parity."

    Reference: Maillard, Roncalli & Teïletche (2010). The Properties of
    Equally Weighted Risk Contribution Portfolios. JPM 36(4), 60-70.
    """
    mu, sigma = _annualize(returns_df, trading_days)
    n = len(mu)
    vols = np.sqrt(np.diag(sigma))

    # Inverse-volatility weights (naive risk parity)
    inv_vol = 1.0 / vols
    w = inv_vol / inv_vol.sum()

    # Refinement: Newton-style iteration toward equal risk contribution.
    # Risk contribution of asset i: RC_i = w_i * (Σw)_i / sqrt(w'Σw)
    for _ in range(max_iter):
        port_vol = np.sqrt(w @ sigma @ w)
        if port_vol < 1e-12:
            break
        marginal = sigma @ w / port_vol
        risk_contrib = w * marginal
        target = port_vol / n  # equal target
        # Update: scale weights inversely to current risk contribution
        if np.allclose(risk_contrib, target, rtol=1e-4):
            break
        w_new = w * (target / np.maximum(risk_contrib, 1e-12)) ** 0.5
        w_new = np.clip(w_new, 1e-6, 1.0)
        w_new = w_new / w_new.sum()
        if np.allclose(w_new, w, rtol=1e-6):
            w = w_new
            break
        w = w_new

    ret, vol, sh = portfolio_stats(w, mu, sigma)
    return {"tickers": list(returns_df.columns), "weights": w,
            "ann_return": ret, "ann_vol": vol, "sharpe": sh,
            "label": "Risk parity"}


def equal_weight_portfolio(returns_df: pd.DataFrame,
                            trading_days: int = 252) -> dict:
    """The 1/N portfolio. DeMiguel, Garlappi & Uppal (2009) showed this is
    surprisingly hard to beat out-of-sample, due to estimation error in
    optimization-based approaches."""
    mu, sigma = _annualize(returns_df, trading_days)
    n = len(mu)
    w = np.full(n, 1.0 / n)
    ret, vol, sh = portfolio_stats(w, mu, sigma)
    return {"tickers": list(returns_df.columns), "weights": w,
            "ann_return": ret, "ann_vol": vol, "sharpe": sh,
            "label": "Equal weight (1/N)"}
