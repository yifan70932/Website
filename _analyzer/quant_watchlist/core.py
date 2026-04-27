"""
Core domain logic for the watchlist analyzer.

Different from the portfolio version:
- No holdings/weights/cash. The universe is just a list of tickers.
- Metrics are computed per-ticker for cross-sectional ranking.
- Adds momentum windows (3m, 6m, 12m), volatility windows (1m, 3m, 12m),
  drawdown duration, return-to-drawdown, etc.
"""

from __future__ import annotations
import json
import warnings
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd
from scipy import stats

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

TRADING_DAYS = 252
RISK_FREE_DEFAULT = 0.045

OUTPUT_DIR = Path("./watchlist_output")
OUTPUT_DIR.mkdir(exist_ok=True)
WATCHLIST_FILE = OUTPUT_DIR / "watchlist.json"

# Default watchlist — well-known US equities + ETFs.
# Curated to span market-cap, sector, and asset-type exposures so the
# correlation, factor, and clustering analyses produce meaningful structure.
DEFAULT_WATCHLIST = [
    # Broad-market index ETFs (note overlap among VOO, VTI, QQQ — itself instructive)
    "VOO",   # S&P 500
    "VTI",   # Total US market
    "QQQ",   # Nasdaq-100
    "VXUS",  # International ex-US
    "VHT",   # US healthcare sector
    # Tech mega-caps
    "AAPL", "MSFT", "GOOG", "AMZN", "META", "NVDA",
    # Tech-adjacent / consumer-tech
    "NFLX", "TSLA",
    # Industrials / cyclicals
    "GE",    # General Electric (post-spinoff aerospace+power)
    "DAL",   # Delta — airlines, very cyclical
    # Discretionary / staples
    "DIS", "MCD",
    # Single semis name (more vol than NVDA, useful as factor outlier)
    "MU",
]

BENCHMARK = "SPY"  # use SPY as benchmark since it tracks the same index VOO does
# but is the historical industry standard for benchmarking purposes


# ---------- Watchlist persistence ----------

def load_watchlist() -> list[str]:
    if WATCHLIST_FILE.exists():
        try:
            data = json.loads(WATCHLIST_FILE.read_text())
            if isinstance(data, list):
                return [t.upper().strip() for t in data]
        except Exception:
            pass
    return list(DEFAULT_WATCHLIST)


def save_watchlist(tickers: list[str]) -> None:
    WATCHLIST_FILE.write_text(json.dumps(tickers, indent=2))


def apply_cli_changes(tickers: list[str], args) -> list[str]:
    """Apply --tickers, --add, --remove flags."""
    if args.tickers:
        tickers = [t.upper().strip() for t in args.tickers]
    if args.add:
        for t in args.add:
            tu = t.upper().strip()
            if tu not in tickers:
                tickers.append(tu)
    if args.remove:
        removed = {t.upper().strip() for t in args.remove}
        tickers = [t for t in tickers if t not in removed]
    return tickers


# ---------- Per-ticker feature engineering ----------

@dataclass
class TickerFeatures:
    ticker: str
    price: pd.Series
    log_returns: pd.Series
    sma_50: pd.Series
    sma_200: pd.Series
    bb_upper: pd.Series
    bb_lower: pd.Series
    bb_mid: pd.Series
    rsi_14: pd.Series
    macd: pd.Series
    macd_signal: pd.Series
    drawdown: pd.Series
    fundamentals: dict = field(default_factory=dict)
    company_name: Optional[str] = None


def rsi(s: pd.Series, w: int = 14) -> pd.Series:
    d = s.diff()
    g = d.clip(lower=0); l = -d.clip(upper=0)
    ag = g.ewm(alpha=1/w, adjust=False).mean()
    al = l.ewm(alpha=1/w, adjust=False).mean()
    return 100 - (100 / (1 + ag / al))


def macd_calc(s, fast=12, slow=26, signal=9):
    ef = s.ewm(span=fast, adjust=False).mean()
    es = s.ewm(span=slow, adjust=False).mean()
    line = ef - es
    return line, line.ewm(span=signal, adjust=False).mean()


def bollinger(s, w=20, n=2.0):
    mid = s.rolling(w).mean()
    sd = s.rolling(w).std()
    return mid + n*sd, mid, mid - n*sd


def compute_features(ticker: str, price: pd.Series,
                      company_name: Optional[str] = None) -> TickerFeatures:
    log_ret = np.log(price / price.shift(1))
    upper, mid, lower = bollinger(price)
    macd_line, signal_line = macd_calc(price)
    drawdown = (price - price.cummax()) / price.cummax()
    return TickerFeatures(
        ticker=ticker, price=price, log_returns=log_ret,
        sma_50=price.rolling(50).mean(),
        sma_200=price.rolling(200).mean(),
        bb_upper=upper, bb_mid=mid, bb_lower=lower,
        rsi_14=rsi(price), macd=macd_line, macd_signal=signal_line,
        drawdown=drawdown, company_name=company_name,
    )


# ---------- Cross-sectional metrics ----------

def sharpe(lr, rf=RISK_FREE_DEFAULT):
    rf_d = rf / TRADING_DAYS
    e = lr.dropna() - rf_d
    return np.sqrt(TRADING_DAYS) * e.mean() / e.std() if e.std() > 0 else np.nan


def sortino(lr, rf=RISK_FREE_DEFAULT):
    rf_d = rf / TRADING_DAYS
    e = lr.dropna() - rf_d
    d = e[e < 0]
    return np.sqrt(TRADING_DAYS) * e.mean() / d.std() if len(d) > 5 and d.std() > 0 else np.nan


def max_drawdown(price: pd.Series) -> float:
    return ((price - price.cummax()) / price.cummax()).min()


def max_drawdown_duration(price: pd.Series) -> int:
    """Longest peak-to-recovery period in trading days (a drawdown that
    hasn't recovered counts up to today)."""
    cummax = price.cummax()
    in_dd = price < cummax
    if not in_dd.any():
        return 0
    # Length of each drawdown spell
    spells = (in_dd != in_dd.shift()).cumsum()
    spell_lengths = in_dd.groupby(spells).sum()
    return int(spell_lengths.max())


def beta(asset: pd.Series, bench: pd.Series) -> float:
    df = pd.concat([asset, bench], axis=1).dropna()
    if len(df) < 30:
        return np.nan
    cov = df.cov().iloc[0, 1]
    var = df.iloc[:, 1].var()
    return cov / var if var > 0 else np.nan


def var_95(lr): return float(np.quantile(lr.dropna(), 0.05))


def cvar_95(lr):
    s = lr.dropna()
    th = np.quantile(s, 0.05)
    return float(s[s <= th].mean())


def momentum_window(price: pd.Series, days: int) -> float:
    """Total return over the last `days` trading days."""
    if len(price) < days + 1:
        return np.nan
    return float(price.iloc[-1] / price.iloc[-days - 1] - 1.0)


def volatility_window(log_returns: pd.Series, days: int) -> float:
    """Annualized volatility over the last `days` trading days."""
    if len(log_returns) < days:
        return np.nan
    return float(log_returns.iloc[-days:].std() * np.sqrt(TRADING_DAYS))


def correlation_to_benchmark(asset_returns: pd.Series,
                              bench_returns: pd.Series) -> float:
    df = pd.concat([asset_returns, bench_returns], axis=1).dropna()
    if len(df) < 30:
        return np.nan
    return float(df.corr().iloc[0, 1])
