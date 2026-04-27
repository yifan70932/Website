"""
News fetcher for the watchlist tool.

Same RSS-based approach as portfolio_analyzer.news (Yahoo Finance RSS,
chosen over yfinance.Ticker.news because of that method's known instability
since March 2024). The differences from the portfolio version:

1. Output is flattened into a single chronological feed across all tickers,
   not grouped per-ticker. With 18+ names, per-ticker collapsibles become
   noise. A single feed with ticker tags is the dashboard convention used
   by Bloomberg, Reuters, Eikon for watchlist views.

2. Lower per-ticker article cap (default 2) since the flat feed gets long.
"""

from __future__ import annotations
import time
import re
import xml.etree.ElementTree as ET
from datetime import datetime
from email.utils import parsedate_to_datetime
from typing import Optional

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

YAHOO_RSS_URL = ("https://feeds.finance.yahoo.com/rss/2.0/headline"
                 "?s={ticker}&region=US&lang=en-US")
USER_AGENT = "quant_watchlist/1.0 (educational use)"
TIMEOUT = 10


def _strip_html(text: str) -> str:
    if not text:
        return ""
    clean = re.sub(r"<[^>]+>", "", text)
    clean = (clean.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
                  .replace("&quot;", '"').replace("&#39;", "'").replace("&apos;", "'")
                  .replace("&nbsp;", " "))
    return re.sub(r"\s+", " ", clean).strip()


def _parse_pubdate(text):
    if not text:
        return None
    try:
        return parsedate_to_datetime(text)
    except Exception:
        return None


def fetch_ticker_news(ticker: str, limit: int = 2) -> list[dict]:
    if not HAS_REQUESTS:
        return []
    url = YAHOO_RSS_URL.format(ticker=ticker)
    try:
        r = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=TIMEOUT)
        if r.status_code != 200:
            return []
        try:
            root = ET.fromstring(r.content)
        except ET.ParseError:
            return []
    except Exception:
        return []

    items = root.findall(".//item")
    out = []
    for item in items[:limit]:
        title = (item.findtext("title") or "").strip()
        link = (item.findtext("link") or "").strip()
        raw = item.findtext("description") or ""
        summary = _strip_html(raw)
        if len(summary) > 240:
            summary = summary[:240] + "…"
        pub = _parse_pubdate(item.findtext("pubDate"))
        if not title or not link:
            continue
        src_elem = item.find("source")
        source = (src_elem.text if src_elem is not None and src_elem.text
                  else "Yahoo Finance")
        out.append({
            "title": title, "link": link, "summary": summary,
            "published": pub, "source": source.strip(),
            "ticker": ticker.upper(),
        })
    return out


def fetch_news_feed(tickers: list[str], per_ticker: int = 2,
                     throttle_sec: float = 1.0) -> list[dict]:
    """
    Fetch news for the entire watchlist and merge into one chronological
    list, sorted newest first.
    """
    feed = []
    for i, t in enumerate(tickers):
        articles = fetch_ticker_news(t, limit=per_ticker)
        feed.extend(articles)
        if i < len(tickers) - 1 and throttle_sec > 0:
            time.sleep(throttle_sec)
    # Sort by published date (most recent first); items without dates last
    feed.sort(key=lambda a: a.get("published") or datetime.min,
               reverse=True)
    return feed


def format_published(dt) -> str:
    if dt is None:
        return ""
    now = datetime.now(dt.tzinfo) if dt.tzinfo else datetime.now()
    delta = now - dt
    secs = delta.total_seconds()
    if secs < 0:
        return "just now"
    if secs < 3600:
        m = int(secs / 60)
        return f"{m}m ago" if m > 0 else "just now"
    if secs < 86400:
        return f"{int(secs / 3600)}h ago"
    days = int(secs / 86400)
    if days < 30:
        return f"{days}d ago"
    return dt.strftime("%b %d, %Y")
