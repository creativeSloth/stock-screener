from dataclasses import dataclass


@dataclass
class Config:
    # Watchlist paths
    watchlist_dax: str = "watchlists/dax.txt"
    watchlist_us: str = "watchlists/us.txt"

    # Data settings
    period: str = "6mo"  # Lookback period
    interval: str = "1d"   # Candle interval

    # Indicators
    rsi_period: int = 14
    sma_short: int = 20
    sma_long: int = 50
