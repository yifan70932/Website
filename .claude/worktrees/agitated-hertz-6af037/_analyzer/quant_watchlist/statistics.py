"""
Statistical rigor for performance evaluation.

Single-number performance metrics (Sharpe = 1.5, max DD = -22%) can be very
misleading on small samples. This module provides:

  - Bootstrap confidence intervals for Sharpe and other ratios
  - Lo (2002) Sharpe-ratio significance test (corrects for autocorrelation)
  - Parametric (Gaussian) VaR alongside historical VaR
  - Skewness and excess kurtosis as standalone metrics
  - Information ratio and tracking error vs. a benchmark

REFERENCES
==========
- Lo, A. W. (2002). The Statistics of Sharpe Ratios. FAJ 58(4), 36-52.
- Memmel, C. (2003). Performance Hypothesis Testing with the Sharpe Ratio.
- Politis & Romano (1994). The stationary bootstrap.
"""

from __future__ import annotations
import numpy as np
import pandas as pd
from scipy import stats
from typing import Optional


# ---------- Bootstrap confidence intervals ----------

def bootstrap_sharpe_ci(returns: pd.Series,
                         rf: float = 0.045,
                         trading_days: int = 252,
                         n_resamples: int = 2000,
                         conf: float = 0.95,
                         seed: int = 42) -> dict:
    """
    Bootstrap confidence interval for the annualized Sharpe ratio.

    Resamples the daily return series with replacement, computes Sharpe on
    each resample, and returns the empirical CI.

    Note: this is the simple iid bootstrap, not the stationary bootstrap.
    The iid version ignores autocorrelation, which slightly understates
    the true uncertainty for typical financial returns. For Lo's
    autocorrelation-aware analytic CI, see lo_sharpe_significance() below.
    """
    r = returns.dropna().values
    if len(r) < 30:
        return {"point_estimate": float("nan"), "ci_low": float("nan"),
                "ci_high": float("nan"), "n_obs": len(r), "method": "bootstrap_iid"}

    rf_d = rf / trading_days
    rng = np.random.default_rng(seed)
    n = len(r)
    sharpes = np.empty(n_resamples)
    for i in range(n_resamples):
        sample = rng.choice(r, size=n, replace=True)
        excess = sample - rf_d
        s = excess.std()
        sharpes[i] = (np.sqrt(trading_days) * excess.mean() / s) if s > 0 else 0.0

    point = (np.sqrt(trading_days) * (r - rf_d).mean()
             / (r - rf_d).std()) if (r - rf_d).std() > 0 else float("nan")
    alpha = (1 - conf) / 2
    ci_low = float(np.quantile(sharpes, alpha))
    ci_high = float(np.quantile(sharpes, 1 - alpha))
    return {"point_estimate": float(point),
            "ci_low": ci_low, "ci_high": ci_high,
            "n_obs": int(n), "n_resamples": n_resamples,
            "conf": conf, "method": "bootstrap_iid",
            "sharpe_distribution": sharpes}


def lo_sharpe_significance(returns: pd.Series,
                            rf: float = 0.045,
                            trading_days: int = 252,
                            q: int = 5) -> dict:
    """
    Lo (2002) analytic standard error for the Sharpe ratio, with adjustment
    for serial correlation up to lag q.

    Under iid normal returns, SE(Sharpe) ≈ sqrt((1 + 0.5 * SR^2) / T).
    Lo's autocorrelation correction multiplies this by an η factor that
    accounts for q lags of return autocorrelation.

    Returns the t-statistic for the null hypothesis SR=0, and the p-value
    (two-sided). A statistically significant Sharpe means it's unlikely
    to be due to luck given the sample size.

    Reference: Lo (2002), "The Statistics of Sharpe Ratios," FAJ.
    """
    r = returns.dropna().values
    n = len(r)
    if n < 30:
        return {"sharpe": float("nan"), "se": float("nan"),
                "t_stat": float("nan"), "p_value": float("nan"),
                "significant_5pct": False, "n_obs": n}

    rf_d = rf / trading_days
    excess = r - rf_d
    mu_excess = excess.mean()
    sigma_excess = excess.std()
    if sigma_excess <= 0:
        return {"sharpe": 0.0, "se": float("nan"), "t_stat": 0.0,
                "p_value": 1.0, "significant_5pct": False, "n_obs": n}

    sr_daily = mu_excess / sigma_excess  # un-annualized Sharpe
    sr_annual = sr_daily * np.sqrt(trading_days)

    # Lo's eta factor for autocorrelation (lags 1..q):
    # eta^2 = 1 + 2 * sum_{k=1}^{q} (1 - k/q) * rho_k
    # where rho_k is the autocorrelation of returns at lag k.
    rhos = []
    for k in range(1, q + 1):
        if n - k < 5:
            break
        rho = float(np.corrcoef(r[:-k], r[k:])[0, 1])
        if not np.isnan(rho):
            rhos.append((k, rho))

    eta_sq = 1.0 + 2.0 * sum((1 - k / q) * rho for k, rho in rhos)
    eta_sq = max(eta_sq, 1e-6)  # guard against pathological values

    # Standard error of the daily SR estimator (Lo eq 14, simplified):
    se_daily = np.sqrt(eta_sq * (1 + 0.5 * sr_daily ** 2) / n)
    se_annual = se_daily * np.sqrt(trading_days)
    t_stat = sr_annual / se_annual if se_annual > 0 else 0.0

    # Two-sided p-value
    p_value = 2 * (1 - stats.norm.cdf(abs(t_stat)))

    return {"sharpe": float(sr_annual),
            "se": float(se_annual),
            "t_stat": float(t_stat),
            "p_value": float(p_value),
            "significant_5pct": bool(p_value < 0.05),
            "eta_sq": float(eta_sq),
            "lags_used": q,
            "n_obs": int(n)}


# ---------- Parametric VaR / CVaR ----------

def parametric_var(returns: pd.Series, conf: float = 0.95) -> float:
    """
    Gaussian-distribution-based VaR. Assumes returns are normally distributed.
    Compare to historical VaR — if the gap is large, your portfolio has
    significant non-Gaussian tail risk.
    """
    r = returns.dropna()
    if len(r) < 10:
        return float("nan")
    z = stats.norm.ppf(1 - conf)
    return float(r.mean() + z * r.std())


def parametric_cvar(returns: pd.Series, conf: float = 0.95) -> float:
    """Gaussian CVaR — the expected loss in the worst (1-conf) tail."""
    r = returns.dropna()
    if len(r) < 10:
        return float("nan")
    z = stats.norm.ppf(1 - conf)
    # E[X | X < z] = mu - sigma * phi(z) / (1 - conf), where phi is normal pdf
    return float(r.mean() - r.std() * stats.norm.pdf(z) / (1 - conf))


# ---------- Higher moments ----------

def skewness(returns: pd.Series) -> float:
    r = returns.dropna()
    return float(stats.skew(r)) if len(r) > 10 else float("nan")


def excess_kurtosis(returns: pd.Series) -> float:
    """Excess kurtosis (kurtosis minus 3). Normal distribution has 0.
    Positive = fat tails relative to normal; negative = thin tails."""
    r = returns.dropna()
    return float(stats.kurtosis(r, fisher=True)) if len(r) > 10 else float("nan")


# ---------- Active-management metrics ----------

def tracking_error(asset_returns: pd.Series, benchmark_returns: pd.Series,
                    trading_days: int = 252) -> float:
    """
    Annualized tracking error: standard deviation of (asset - benchmark).
    Measures how much an asset deviates from its benchmark in either direction.
    """
    df = pd.concat([asset_returns, benchmark_returns], axis=1).dropna()
    if len(df) < 30:
        return float("nan")
    excess = df.iloc[:, 0] - df.iloc[:, 1]
    return float(excess.std() * np.sqrt(trading_days))


def information_ratio(asset_returns: pd.Series, benchmark_returns: pd.Series,
                       trading_days: int = 252) -> float:
    """
    Information ratio: annualized excess return over benchmark divided by
    tracking error. The metric most commonly used to evaluate active
    managers — measures consistency of outperformance per unit of bet
    against the benchmark.

    IR > 0.5 is considered good; IR > 1.0 is exceptional and rare.
    """
    df = pd.concat([asset_returns, benchmark_returns], axis=1).dropna()
    if len(df) < 30:
        return float("nan")
    excess = df.iloc[:, 0] - df.iloc[:, 1]
    sd = excess.std()
    if sd <= 0:
        return float("nan")
    return float(np.sqrt(trading_days) * excess.mean() / sd)


def calmar_ratio(returns: pd.Series, trading_days: int = 252) -> float:
    """
    Calmar ratio: annualized return / |max drawdown|.
    Higher = better. Rewards strategies that don't suffer deep drawdowns.
    """
    r = returns.dropna()
    if len(r) < 30:
        return float("nan")
    ann_ret = r.mean() * trading_days
    cum = (1 + r).cumprod()
    mdd = ((cum - cum.cummax()) / cum.cummax()).min()
    if mdd >= 0:
        return float("nan")
    return float(ann_ret / abs(mdd))
