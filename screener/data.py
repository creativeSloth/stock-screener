import pandas as pd
import yfinance as yf

from config import INTERVAL, PERIOD, WATCHLIST_DAX, WATCHLIST_US


def load_watchlist(filepath: str) -> list[str]:
    """Load ticker symbols from a plain-text watchlist file.

    Args:
        filepath: Path to the watchlist file (one ticker per line).

    Returns:
        List of ticker symbols as strings.
    """
    tickers: list[str] = [line.strip()
                          for line in open(filepath) if line.strip()]
    return tickers


def get_stock_data(ticker: str) -> pd.DataFrame:
    """Download historical OHLCV data for a single ticker via Yahoo Finance.

    Args:
        ticker: Yahoo Finance ticker symbol (e.g. 'SAP.DE', 'AAPL').

    Returns:
        DataFrame with columns: Open, High, Low, Close, Volume.
    """
    df: pd.DataFrame | None = yf.download(
        ticker, period=PERIOD, interval=INTERVAL, auto_adjust=True
    )
    if df is None:
        raise ValueError(f"No data returned for ticker: {ticker}")
    return df


def load_all_tickers() -> list[str]:
    """Load and combine all tickers from DAX and US watchlists.

    Returns:
        Combined list of ticker symbols.
    """
    dax: list[str] = load_watchlist(WATCHLIST_DAX)
    us: list[str] = load_watchlist(WATCHLIST_US)
    combined: list[str] = dax + us
    return combined


if __name__ == "__main__":
    tickers: list[str] = load_all_tickers()
    print(f"Loaded {len(tickers)} tickers: {tickers}\n")

    df: pd.DataFrame = get_stock_data("SAP.DE")
    print(df.tail(5))
