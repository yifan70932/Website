"""
Multi-factor scoring (QVM+L: Quality, Value, Momentum, Low Volatility).

Industry-standard factor scoring as practiced by MSCI, S&P, AQR, and modern
quant screeners. Each ticker is ranked on each factor; ranks are converted to
percentile scores; a composite score combines them with configurable weights.

FACTOR DEFINITIONS
==================

Momentum (industry convention):
  Composite of multiple lookback windows so a single anomalous month doesn't
  dominate. Following O'Shaughnessy / MSCI:
    - 12-month total return excluding the most recent month (12-1 momentum,
      Jegadeesh & Titman 1993). The 1-month skip avoids short-term reversal
      contamination (Jegadeesh 1990).
    - 6-month return
    - 3-month return
  Higher is better. Mean-rank across the three windows.

Low Volatility (the "Low" in QVM+L):
  Following the low-vol anomaly (Frazzini & Pedersen 2014, "Betting Against
  Beta"; MSCI Minimum Volatility Indexes):
    - 12-month annualized return volatility.
  Lower volatility ranks higher (factor flipped before percentile).

Quality:
  Quality is multidimensional. We use the dimensions available from yfinance:
    - Return on Equity (profitability)
    - Profit margin (profitability)
    - Debt-to-equity (safety; lower is better)
    - 12-month return stability (proxy: low downside volatility / max DD)
  Equal-weighted percentile across these.

Value:
  Lower multiples = better value:
    - P/E (trailing) — lower is better
    - P/B — lower is better
    - EV/EBITDA — lower is better (when available)
  Equal-weighted percentile across these. Note: deeply negative-earnings
  names will have undefined or nonsensical P/E; we handle that explicitly.

REFERENCES
==========
- Jegadeesh & Titman (1993). Returns to Buying Winners and Selling Losers. JF.
- Asness, Frazzini & Pedersen (2019). Quality Minus Junk. Review of
  Accounting Studies.
- Frazzini & Pedersen (2014). Betting Against Beta. JFE.
- MSCI (2024). Factor Indexing Through the Decades.
- O'Shaughnessy (2011). What Works on Wall Street, 4th ed.
"""

from __future__ import annotations
import numpy as np
import pandas as pd
from typing import Optional


def _percentile_rank(values: pd.Series, ascending: bool = True) -> pd.Series:
    """
    Convert raw values to percentile ranks in [0, 100].
    100 = best within universe; 0 = worst.

    ascending=True: higher raw value -> higher percentile (e.g. ROE).
    ascending=False: lower raw value -> higher percentile (e.g. P/E, vol).

    NaN values get NaN percentile (preserved through aggregation).
    """
    valid = values.dropna()
    if len(valid) == 0:
        return pd.Series(np.nan, index=values.index)
    if ascending:
        ranks = valid.rank(pct=True, method="average") * 100
    else:
        ranks = (1 - valid.rank(pct=True, method="average")) * 100
    return ranks.reindex(values.index)


def momentum_scores(features_dict: dict) -> pd.DataFrame:
    """
    Build a momentum DataFrame for the universe.
    Returns DataFrame indexed by ticker with columns:
      mom_12m_excl_1m, mom_6m, mom_3m, momentum_score (composite percentile)
    """
    rows = {}
    for t, f in features_dict.items():
        price = f.price.dropna()
        if len(price) < 252:
            # Not enough history for full momentum stack — try to compute what we can
            r12 = r6 = r3 = np.nan
        else:
            # 12-1 momentum: return from 252d ago to 21d ago
            r12 = float(price.iloc[-21] / price.iloc[-252] - 1) if len(price) >= 252 else np.nan
            r6 = float(price.iloc[-1] / price.iloc[-126] - 1) if len(price) >= 126 else np.nan
            r3 = float(price.iloc[-1] / price.iloc[-63] - 1) if len(price) >= 63 else np.nan
        rows[t] = {"mom_12m_excl_1m": r12, "mom_6m": r6, "mom_3m": r3}

    df = pd.DataFrame(rows).T
    # Component percentiles
    p12 = _percentile_rank(df["mom_12m_excl_1m"], ascending=True)
    p6 = _percentile_rank(df["mom_6m"], ascending=True)
    p3 = _percentile_rank(df["mom_3m"], ascending=True)
    # Composite: average of available components per ticker
    components = pd.DataFrame({"p12": p12, "p6": p6, "p3": p3})
    df["momentum_score"] = components.mean(axis=1, skipna=True)
    return df


def low_vol_scores(features_dict: dict) -> pd.DataFrame:
    """
    Build the low-volatility score. Lower 12-month annualized vol = higher score.
    """
    rows = {}
    for t, f in features_dict.items():
        lr = f.log_returns.dropna()
        if len(lr) < 252:
            v12 = float(lr.std() * np.sqrt(252)) if len(lr) > 30 else np.nan
        else:
            v12 = float(lr.iloc[-252:].std() * np.sqrt(252))
        rows[t] = {"vol_12m": v12}
    df = pd.DataFrame(rows).T
    df["lowvol_score"] = _percentile_rank(df["vol_12m"], ascending=False)
    return df


def quality_scores(features_dict: dict) -> pd.DataFrame:
    """
    Quality composite from fundamentals. Components:
      - ROE (higher = better)
      - Profit margin (higher = better)
      - Debt/Equity (lower = better)
      - Earnings stability proxy: max drawdown over lookback (less negative = better)
    """
    rows = {}
    for t, f in features_dict.items():
        fund = f.fundamentals or {}
        # yfinance keys we use; missing fields → NaN
        roe = fund.get("ROE")
        pm = fund.get("Profit margin") or fund.get("profitMargins")
        de = fund.get("Debt/Equity") or fund.get("debtToEquity")
        # Safety proxy from price series: max drawdown over the window
        price = f.price.dropna()
        mdd = float(((price - price.cummax()) / price.cummax()).min()) if len(price) else np.nan
        rows[t] = {
            "roe": float(roe) if isinstance(roe, (int, float)) and not np.isnan(roe) else np.nan,
            "profit_margin": float(pm) if isinstance(pm, (int, float)) and not np.isnan(pm) else np.nan,
            "debt_to_equity": float(de) if isinstance(de, (int, float)) and not np.isnan(de) else np.nan,
            "max_dd": mdd,
        }
    df = pd.DataFrame(rows).T

    # Component percentiles
    p_roe = _percentile_rank(df["roe"], ascending=True)
    p_pm = _percentile_rank(df["profit_margin"], ascending=True)
    p_de = _percentile_rank(df["debt_to_equity"], ascending=False)  # lower is better
    p_mdd = _percentile_rank(df["max_dd"], ascending=True)  # less negative is better

    components = pd.DataFrame({"roe": p_roe, "pm": p_pm, "de": p_de, "mdd": p_mdd})
    df["quality_score"] = components.mean(axis=1, skipna=True)
    return df


def value_scores(features_dict: dict) -> pd.DataFrame:
    """
    Value composite from fundamental multiples. Lower = better.
    Components: P/E, P/B, EV/EBITDA (where available).
    """
    rows = {}
    for t, f in features_dict.items():
        fund = f.fundamentals or {}
        pe = fund.get("P/E (trailing)") or fund.get("trailingPE")
        pb = fund.get("P/B") or fund.get("priceToBook")
        ev_ebitda = fund.get("EV/EBITDA") or fund.get("enterpriseToEbitda")

        # Filter unrealistic values: negative P/E means the company is losing money
        # and the ratio is meaningless for value comparison; treat as NaN.
        def clean(x, allow_negative=False):
            if not isinstance(x, (int, float)):
                return np.nan
            if np.isnan(x):
                return np.nan
            if not allow_negative and x <= 0:
                return np.nan
            return float(x)

        rows[t] = {
            "pe": clean(pe),
            "pb": clean(pb),
            "ev_ebitda": clean(ev_ebitda),
        }
    df = pd.DataFrame(rows).T

    p_pe = _percentile_rank(df["pe"], ascending=False)
    p_pb = _percentile_rank(df["pb"], ascending=False)
    p_ev = _percentile_rank(df["ev_ebitda"], ascending=False)
    components = pd.DataFrame({"pe": p_pe, "pb": p_pb, "ev_ebitda": p_ev})
    df["value_score"] = components.mean(axis=1, skipna=True)
    return df


def composite_qvml(features_dict: dict,
                    weights: dict = None) -> pd.DataFrame:
    """
    Build the full QVM+L composite scoring DataFrame.

    weights: dict of {factor: weight}. Default: equal weights for all four.
             Set a weight to 0 to drop that factor (e.g. weights={"value": 0,
             "momentum": 1, "quality": 1, "lowvol": 1} for QML for ETFs
             where value multiples don't apply).

    Returns DataFrame with columns:
      mom_12m_excl_1m, mom_6m, mom_3m, momentum_score,
      vol_12m, lowvol_score,
      roe, profit_margin, debt_to_equity, max_dd, quality_score,
      pe, pb, ev_ebitda, value_score,
      composite_score
    """
    if weights is None:
        weights = {"momentum": 1.0, "quality": 1.0, "value": 1.0, "lowvol": 1.0}

    mom = momentum_scores(features_dict)
    lv = low_vol_scores(features_dict)
    q = quality_scores(features_dict)
    v = value_scores(features_dict)

    df = pd.concat([mom, lv, q, v], axis=1)

    # Composite: weighted average of the four scores (NaN-safe per row).
    score_cols = {"momentum": "momentum_score", "lowvol": "lowvol_score",
                   "quality": "quality_score", "value": "value_score"}
    components = pd.DataFrame({
        name: df[col] * weights.get(name, 0.0)
        for name, col in score_cols.items()
    })
    weight_sums = pd.DataFrame({
        name: df[col].notna().astype(float) * weights.get(name, 0.0)
        for name, col in score_cols.items()
    })
    # Composite = Σ(weight·score) / Σ(weight·indicator) so missing factors don't
    # mathematically penalize a name; instead the available factors are
    # re-weighted to sum to 1 for that ticker.
    df["composite_score"] = components.sum(axis=1) / weight_sums.sum(axis=1).replace(0, np.nan)
    return df.sort_values("composite_score", ascending=False)
