import pandas as pd

from .indicators import calculate_macd, calculate_rsi, calculate_sma


def get_signal(df: pd.DataFrame) -> dict[str, str]:
    """Generate buy/sell/neutral signals based on technical indicators.

    Args:
        df: DataFrame with a 'Close' column.

    Returns:
        Dictionary with signal for each indicator and an overall signal.
    """
    signals: dict[str, str] = {}

    # --- RSI Signal ---
    # RSI measures momentum: how fast and how much prices are moving
    # A value below 30 means the market has sold off too aggressively
    # (oversold) → price likely to bounce back → BUY opportunity
    # A value above 70 means the market is overheated
    # (overbought) → price likely to correct → SELL signal
    rsi: pd.Series = calculate_rsi(df)
    rsi_value: float = float(rsi.iloc[-1])  # most recent RSI value

    if rsi_value < 30:
        signals["rsi"] = "BUY"
    elif rsi_value > 70:
        signals["rsi"] = "SELL"
    else:
        signals["rsi"] = "NEUTRAL"

    # --- SMA Signal ---
    # We compare yesterday's and today's SMA values to detect crossovers
    # A crossover is more reliable than a snapshot because it confirms
    # that the trend has actually changed direction, not just fluctuated
    sma_short, sma_long = calculate_sma(df)
    prev_short: float = float(sma_short.iloc[-2])  # yesterday SMA_short
    prev_long: float = float(sma_long.iloc[-2])   # yesterday SMA_long
    curr_short: float = float(sma_short.iloc[-1])  # today SMA_short
    curr_long: float = float(sma_long.iloc[-1])   # today SMA_long

    if prev_short <= prev_long and curr_short > curr_long:
        # Golden Cross: fast MA just crossed above slow MA
        # Short-term momentum is now stronger than long-term → bullish
        signals["sma"] = "BUY"
    elif prev_short >= prev_long and curr_short < curr_long:
        # Death Cross: fast MA just crossed below slow MA
        # Short-term momentum is now weaker than long-term → bearish
        signals["sma"] = "SELL"
    else:
        # No crossover detected → trend is ongoing, no new signal
        signals["sma"] = "NEUTRAL"

    # --- MACD Signal ---
    # Same crossover logic as SMA but applied to MACD and its signal line
    # MACD already captures the difference between two EMAs, so a crossover
    # here means momentum is shifting — it reacts faster than SMA crossovers
    macd_line, signal_line = calculate_macd(df)
    prev_macd: float = float(macd_line.iloc[-2])   # yesterday MACD
    prev_sig: float = float(signal_line.iloc[-2])  # yesterday signal line
    curr_macd: float = float(macd_line.iloc[-1])   # today MACD
    curr_sig: float = float(signal_line.iloc[-1])  # today signal line

    if prev_macd <= prev_sig and curr_macd > curr_sig:
        # MACD crossed above signal line → bullish momentum shift
        signals["macd"] = "BUY"
    elif prev_macd >= prev_sig and curr_macd < curr_sig:
        # MACD crossed below signal line → bearish momentum shift
        signals["macd"] = "SELL"
    else:
        signals["macd"] = "NEUTRAL"

    # --- Overall Signal ---
    # Simple majority vote: at least 2 out of 3 indicators must agree
    # This reduces false signals — one indicator alone is never reliable enough
    # RSI catches momentum extremes, SMA catches trend changes,
    # MACD catches momentum shifts → together they cover different aspects
    values: list[str] = list(signals.values())
    if values.count("BUY") >= 2:
        signals["overall"] = "BUY"
    elif values.count("SELL") >= 2:
        signals["overall"] = "SELL"
    else:
        # No consensus → stay out of the market
        signals["overall"] = "NEUTRAL"

    return signals


if __name__ == "__main__":
    from data import get_stock_data

    df: pd.DataFrame = get_stock_data("SAP.DE")
    result: dict[str, str] = get_signal(df)
    print(result)
