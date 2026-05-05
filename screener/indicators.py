import pandas as pd

from config import Config

config: Config = Config()


def calculate_rsi(df: pd.DataFrame) -> pd.Series:
    """Calculate the Relative Strength Index (RSI) for a given DataFrame.

    Args:
        df: DataFrame with a 'Close' column.

    Returns:
        Pandas Series with RSI values (0–100).
    """
    # Extract closing prices as 1D Series
    close: pd.Series = pd.Series(df["Close"].squeeze())

    # Day-over-day price change: delta = Close(t) - Close(t-1)
    delta: pd.Series = close.diff()

    # Separate gains (positive deltas) and losses (positive absolute values of negative deltas)
    # clip(lower=0) sets all negative values to 0
    gain: pd.Series = delta.clip(lower=0)
    loss: pd.Series = (-delta).clip(lower=0)

    # Exponentially weighted average of gains and losses over rsi_period (default: 14 days)
    # ewm reacts faster to recent price changes than a simple rolling mean
    # adjust=False: recursive calculation as per Wilder's original RSI formula
    avg_gain: pd.Series = gain.ewm(
        span=config.rsi_period, adjust=False
    ).mean()
    avg_loss: pd.Series = loss.ewm(
        span=config.rsi_period, adjust=False
    ).mean()

    # RS = average gain / average loss
    rs: pd.Series = avg_gain / avg_loss

    # RSI formula: RSI = 100 - (100 / (1 + RS))
    # RSI < 30 → oversold, RSI > 70 → overbought
    rsi: pd.Series = 100 - (100 / (1 + rs))
    return rsi


def calculate_sma(df: pd.DataFrame) -> tuple[pd.Series, pd.Series]:
    """Calculate short and long Simple Moving Averages.

    Args:
        df: DataFrame with a 'Close' column.

    Returns:
        Tuple of (SMA_short, SMA_long) as Pandas Series.
    """
    close: pd.Series = pd.Series(df["Close"].squeeze())

    # SMA = arithmetic mean of closing prices over the last N days
    # All days are equally weighted (unlike EWM)
    # Golden Cross: SMA_short crosses above SMA_long → bullish signal
    # Death Cross:  SMA_short crosses below SMA_long → bearish signal
    sma_short: pd.Series = close.rolling(window=config.sma_short).mean()
    sma_long: pd.Series = close.rolling(window=config.sma_long).mean()
    return sma_short, sma_long


def calculate_macd(df: pd.DataFrame) -> tuple[pd.Series, pd.Series]:
    """Calculate MACD line and signal line.

    Args:
        df: DataFrame with a 'Close' column.

    Returns:
        Tuple of (macd_line, signal_line) as Pandas Series.
    """
    close: pd.Series = pd.Series(df["Close"].squeeze())

    # EMA_12 reacts faster to price changes, EMA_26 is slower
    ema_12: pd.Series = close.ewm(span=12, adjust=False).mean()
    ema_26: pd.Series = close.ewm(span=26, adjust=False).mean()

    # MACD line = difference between fast and slow EMA
    # Positive MACD → short-term momentum above long-term → bullish
    # Negative MACD → short-term momentum below long-term → bearish
    macd_line: pd.Series = ema_12 - ema_26

    # Signal line = 9-day EMA of MACD line
    # MACD crosses above signal line → buy signal
    # MACD crosses below signal line → sell signal
    signal_line: pd.Series = macd_line.ewm(span=9, adjust=False).mean()
    return macd_line, signal_line
