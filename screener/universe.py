import io
import json
import time
from pathlib import Path

import pandas as pd
import requests

CACHE_PATH = Path("cache/universe.json")
CACHE_TTL = 7 * 24 * 3600  # 7 days

# Wikipedia source config per index
_INDICES: dict[str, dict] = {
    "DAX": {
        "url": "https://en.wikipedia.org/wiki/DAX",
        "ticker_cols": ["Ticker", "Symbol", "Index"],
        "suffix": ".DE",
    },
    "MDAX": {
        "url": "https://en.wikipedia.org/wiki/MDAX",
        "ticker_cols": ["Ticker", "Symbol"],
        "suffix": ".DE",
    },
    "DOW": {
        "url": "https://en.wikipedia.org/wiki/Dow_Jones_Industrial_Average",
        "ticker_cols": ["Symbol", "Ticker"],
        "suffix": "",
    },
    "NASDAQ100": {
        "url": "https://en.wikipedia.org/wiki/Nasdaq-100",
        "ticker_cols": ["Ticker", "Symbol"],
        "suffix": "",
    },
    "SP500": {
        "url": "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies",
        "ticker_cols": ["Symbol", "Ticker"],
        "suffix": "",
    },
}


def _is_valid_ticker(value: str) -> bool:
    if not value or not isinstance(value, str):
        return False
    v = value.strip()
    # Reject Wikipedia footnotes, headers, empty strings
    if not v or v.startswith("[") or len(v) > 12 or " " in v:
        return False
    # Must contain at least one letter
    return any(c.isalpha() for c in v)


_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    )
}


def _fetch_tickers(url: str, ticker_cols: list[str], suffix: str) -> list[str]:
    response = requests.get(url, headers=_HEADERS, timeout=15)
    response.raise_for_status()
    tables: list[pd.DataFrame] = pd.read_html(io.StringIO(response.text), flavor="lxml")
    for table in tables:
        for col in ticker_cols:
            if col in table.columns:
                raw = table[col].dropna().astype(str).tolist()
                tickers = [t.strip() for t in raw if _is_valid_ticker(t)]
                if len(tickers) < 5:
                    continue
                if suffix:
                    # Only append suffix if ticker has no exchange suffix yet
                    tickers = [
                        t if "." in t else t + suffix
                        for t in tickers
                    ]
                return tickers
    raise ValueError(f"No usable ticker column ({ticker_cols}) found at {url}")


def _load_cache() -> dict:
    if not CACHE_PATH.exists():
        return {}
    with open(CACHE_PATH) as f:
        return json.load(f)


def _save_cache(data: dict) -> None:
    CACHE_PATH.parent.mkdir(exist_ok=True)
    with open(CACHE_PATH, "w") as f:
        json.dump(data, f, indent=2)


def load_universe(indices: list[str] | None = None) -> dict[str, list[str]]:
    """Return tickers per index, fetched from Wikipedia and cached for 7 days.

    Args:
        indices: Index names to load (e.g. ["DAX", "SP500"]).
                 None loads all available indices.

    Returns:
        Dict mapping index name → list of yfinance-compatible ticker symbols.
    """
    if indices is None:
        indices = list(_INDICES.keys())

    unknown = [n for n in indices if n not in _INDICES]
    if unknown:
        raise ValueError(f"Unknown indices: {unknown}. Available: {list(_INDICES.keys())}")

    cache = _load_cache()
    now = time.time()
    result: dict[str, list[str]] = {}
    updated = False

    for name in indices:
        entry = cache.get(name, {})
        if entry.get("ts", 0) + CACHE_TTL > now:
            result[name] = entry["tickers"]
            print(f"  {name}: {len(entry['tickers'])} tickers (cached)")
            continue

        print(f"  {name}: fetching from Wikipedia...")
        cfg = _INDICES[name]
        tickers = _fetch_tickers(cfg["url"], cfg["ticker_cols"], cfg["suffix"])
        result[name] = tickers
        cache[name] = {"ts": now, "tickers": tickers}
        updated = True
        print(f"  {name}: {len(tickers)} tickers loaded")

    if updated:
        _save_cache(cache)

    return result


def available_indices() -> list[str]:
    return list(_INDICES.keys())
