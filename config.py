from dataclasses import dataclass, field


@dataclass
class Config:
    # Indices to scan — available: DAX, MDAX, DOW, NASDAQ100, SP500
    indices: list[str] = field(
        default_factory=lambda: [
            "DAX"])

    # Data settings
    period: str = "6mo"  # Lookback period
    interval: str = "1d"   # Candle interval

    # Indicators
    rsi_period: int = 14
    sma_short: int = 20
    sma_long: int = 50
