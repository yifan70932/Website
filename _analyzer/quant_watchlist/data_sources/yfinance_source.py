"""yfinance source — the default. Free but unofficial."""

from __future__ import annotations
import pandas as pd
import warnings


class YFinanceSource:
    name = "yfinance"
    requires_key = False
    free_tier = True
    description = ("Free, no API key. Unofficial scraper of Yahoo Finance. "
                   "~30 years of daily data, US + international. May break "
                   "without warning when Yahoo changes their site.")

    def fetch_prices(self, tickers: list[str], period: str) -> pd.DataFrame:
        import yfinance as yf
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            raw = yf.download(tickers, period=period, auto_adjust=True,
                              progress=False, group_by="ticker")
        if isinstance(raw.columns, pd.MultiIndex):
            prices = pd.concat(
                {t: raw[t]["Close"] for t in tickers
                 if t in raw.columns.levels[0]}, axis=1)
        else:
            prices = raw[["Close"]].rename(columns={"Close": tickers[0]})
        return prices.dropna(how="all").ffill()

    def fetch_fundamentals(self, ticker: str) -> dict:
        import yfinance as yf
        try:
            info = yf.Ticker(ticker).info
        except Exception as e:
            return {"_error": str(e)}
        keys = [
            ("trailingPE", "P/E (trailing)"),
            ("forwardPE", "P/E (forward)"),
            ("priceToBook", "P/B"),
            ("priceToSalesTrailing12Months", "P/S"),
            ("pegRatio", "PEG"),
            ("returnOnEquity", "ROE"),
            ("returnOnAssets", "ROA"),
            ("profitMargins", "Profit margin"),
            ("operatingMargins", "Operating margin"),
            ("grossMargins", "Gross margin"),
            ("debtToEquity", "Debt/Equity"),
            ("currentRatio", "Current ratio"),
            ("quickRatio", "Quick ratio"),
            ("dividendYield", "Dividend yield"),
            ("payoutRatio", "Payout ratio"),
            ("beta", "Beta (yfinance)"),
            ("marketCap", "Market cap"),
            ("enterpriseValue", "Enterprise value"),
            ("enterpriseToEbitda", "EV/EBITDA"),
            ("freeCashflow", "Free cash flow"),
            ("sector", "Sector"),
            ("industry", "Industry"),
            ("country", "Country"),
            ("longBusinessSummary", "_summary"),
        ]
        return {label: info.get(k) for k, label in keys
                if info.get(k) is not None}
