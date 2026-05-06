import io
import json
import re
import time
from pathlib import Path

import pandas as pd
import requests
import yfinance as yf

CACHE_PATH = Path("cache/universe.json")
CACHE_TTL = 7 * 24 * 3600  # 7 days

_INDICES: dict[str, dict] = {
    "DAX": {
        "url": "https://en.wikipedia.org/wiki/DAX",
        "ticker_cols": ["Ticker", "Symbol", "Index"],
        "name_cols": ["Company", "Name"],
        "suffix": ".DE",
    },
    "MDAX": {
        "url": "https://en.wikipedia.org/wiki/MDAX",
        "ticker_cols": ["Ticker", "Symbol"],
        "name_cols": ["Name", "Company"],
        "suffix": ".DE",
    },
    "DOW": {
        "url": "https://en.wikipedia.org/wiki/Dow_Jones_Industrial_Average",
        "ticker_cols": ["Symbol", "Ticker"],
        "name_cols": ["Company", "Name"],
        "suffix": "",
    },
    "NASDAQ100": {
        "url": "https://en.wikipedia.org/wiki/Nasdaq-100",
        "ticker_cols": ["Ticker", "Symbol"],
        "name_cols": ["Company", "Security", "Name"],
        "suffix": "",
    },
    "SP500": {
        "url": "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies",
        "ticker_cols": ["Symbol", "Ticker"],
        "name_cols": ["Security", "Company", "Name"],
        "suffix": "",
    },
}


def _is_valid_ticker(value: str) -> bool:
    if not value or not isinstance(value, str):
        return False
    v = value.strip()
    if not v or v.startswith("[") or len(v) > 12 or " " in v:
        return False
    return any(c.isalpha() for c in v)


def _clean_text(value: str) -> str:
    if not value or str(value).lower() == "nan":
        return ""
    return re.sub(r"\[.*?\]", "", str(value)).strip()


_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    )
}


def _fetch_stocks(url: str, ticker_cols: list[str], name_cols: list[str], suffix: str) -> list[dict]:
    response = requests.get(url, headers=_HEADERS, timeout=15)
    response.raise_for_status()
    tables: list[pd.DataFrame] = pd.read_html(io.StringIO(response.text), flavor="lxml")
    for table in tables:
        for col in ticker_cols:
            if col not in table.columns:
                continue
            valid_mask = table[col].astype(str).apply(_is_valid_ticker)
            valid_rows = table[valid_mask]
            if len(valid_rows) < 5:
                continue

            name_col = next((c for c in name_cols if c in table.columns), None)

            stocks = []
            for _, row in valid_rows.iterrows():
                ticker = _clean_text(str(row[col]))
                if suffix and "." not in ticker:
                    ticker = ticker + suffix
                name = _clean_text(str(row[name_col])) if name_col else ""
                stocks.append({"ticker": ticker, "name": name, "wkn": "", "isin": "", "cusip": ""})

            return stocks
    raise ValueError(f"No usable ticker column ({ticker_cols}) found at {url}")


def _fetch_de_metadata(symbol: str) -> tuple[str, str]:
    """Fetch WKN and ISIN from Onvista for a German stock. Returns (wkn, isin)."""
    url = (
        f"https://api.onvista.de/api/v1/instruments/search/facet"
        f"?searchValue={symbol}&entityType=STOCK&market=xetra"
    )
    try:
        r = requests.get(url, headers=_HEADERS, timeout=10)
        if r.status_code != 200:
            return "", ""
        results = r.json().get("facets", [{}])[0].get("results", [])
        for res in results:
            if res.get("symbol", "").upper() == symbol.upper():
                return res.get("wkn", ""), res.get("isin", "")
        if results:
            return results[0].get("wkn", ""), results[0].get("isin", "")
    except Exception:
        pass
    return "", ""


def _enrich_de_metadata(stocks: list[dict]) -> None:
    """Fetch WKN + ISIN from Onvista for German stocks (in-place)."""
    for stock in stocks:
        symbol = stock["ticker"].removesuffix(".DE")
        stock["wkn"], stock["isin"] = _fetch_de_metadata(symbol)
        stock["cusip"] = ""
        time.sleep(0.1)


def _enrich_us_metadata(stocks: list[dict]) -> None:
    """Fetch ISIN from yfinance and derive CUSIP for non-German stocks (in-place)."""
    for stock in stocks:
        try:
            isin = yf.Ticker(stock["ticker"]).isin
            isin = isin if isin and isin != "-" else ""
            stock["isin"] = isin
            # US ISIN = "US" + CUSIP(9 chars) + check digit
            if isin.startswith("US") and len(isin) == 12:
                stock["cusip"] = isin[2:11]
            else:
                stock["cusip"] = ""
        except Exception:
            stock["isin"] = ""
            stock["cusip"] = ""
        time.sleep(0.05)


def _load_cache() -> dict:
    if not CACHE_PATH.exists():
        return {}
    with open(CACHE_PATH) as f:
        return json.load(f)


def _save_cache(data: dict) -> None:
    CACHE_PATH.parent.mkdir(exist_ok=True)
    with open(CACHE_PATH, "w") as f:
        json.dump(data, f, indent=2)


def load_universe(indices: list[str] | None = None) -> dict[str, list[dict]]:
    """Return stocks per index (ticker + name + wkn + isin), fetched from Wikipedia and cached for 7 days.

    Args:
        indices: Index names to load (e.g. ["DAX", "SP500"]).
                 None loads all available indices.

    Returns:
        Dict mapping index name → list of dicts with keys 'ticker', 'name', 'wkn', 'isin'.
    """
    if indices is None:
        indices = list(_INDICES.keys())

    unknown = [n for n in indices if n not in _INDICES]
    if unknown:
        raise ValueError(f"Unknown indices: {unknown}. Available: {list(_INDICES.keys())}")

    cache = _load_cache()
    now = time.time()
    result: dict[str, list[dict]] = {}
    updated = False

    for name in indices:
        entry = cache.get(name, {})
        stocks_cached = entry.get("stocks", [])
        has_metadata = bool(stocks_cached) and "cusip" in stocks_cached[0]
        if entry.get("ts", 0) + CACHE_TTL > now and has_metadata:
            result[name] = entry["stocks"]
            print(f"  {name}: {len(entry['stocks'])} stocks (cached)")
            continue

        print(f"  {name}: fetching from Wikipedia...")
        cfg = _INDICES[name]
        stocks = _fetch_stocks(cfg["url"], cfg["ticker_cols"], cfg["name_cols"], cfg["suffix"])

        if cfg["suffix"] == ".DE":
            print(f"  {name}: fetching WKN + ISIN from Onvista...")
            _enrich_de_metadata(stocks)
        else:
            print(f"  {name}: fetching ISINs from Yahoo Finance...")
            _enrich_us_metadata(stocks)

        result[name] = stocks
        cache[name] = {"ts": now, "stocks": stocks}
        updated = True
        print(f"  {name}: {len(stocks)} stocks loaded")

    if updated:
        _save_cache(cache)

    return result


def available_indices() -> list[str]:
    return list(_INDICES.keys())
