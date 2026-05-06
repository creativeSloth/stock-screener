import pandas as pd
import yfinance as yf

from config import Config

config: Config = Config()


def get_stock_data(tickers: str | list[str]) -> pd.DataFrame:
    """Download historical OHLCV data for one or more tickers via Yahoo Finance.

    Args:
        tickers: Yahoo Finance ticker symbol or list of symbols
                (e.g. 'SAP.DE' or ['SAP.DE', 'AAPL']).

    Returns:
        DataFrame with columns: Open, High, Low, Close, Volume.
    """
    df: pd.DataFrame | None = yf.download(
        tickers,
        period=config.period,
        interval=config.interval,
        auto_adjust=True
    )
    if df is None:
        raise ValueError(f"No data returned for tickers: {tickers}")
    return df


if __name__ == "__main__":
    df: pd.DataFrame = get_stock_data("SAP.DE")
    print(df.tail(5))
