import pandas as pd

from .indicators import calculate_macd, calculate_rsi, calculate_sma


def _overall(signals: dict[str, str]) -> str:
    values = [signals["rsi"], signals["sma"], signals["macd"]]
    if values.count("BUY") >= 2:
        return "BUY"
    if values.count("SELL") >= 2:
        return "SELL"
    return "NEUTRAL"


def _rsi_signal(df: pd.DataFrame) -> tuple[str, float]:
    rsi = calculate_rsi(df)
    value = float(rsi.iloc[-1])
    if value < 30:
        return "BUY", value
    if value > 70:
        return "SELL", value
    return "NEUTRAL", value


def get_signal_trend(df: pd.DataFrame) -> dict[str, str]:
    """Signals based on current indicator position (bullish/bearish state).

    SMA: BUY if SMA20 > SMA50, SELL if below.
    MACD: BUY if MACD line > signal line, SELL if below.
    """
    signals: dict[str, str] = {}

    signals["rsi"], _ = _rsi_signal(df)

    sma_short, sma_long = calculate_sma(df)
    curr_short = float(sma_short.iloc[-1])
    curr_long = float(sma_long.iloc[-1])
    if curr_short > curr_long:
        signals["sma"] = "BUY"
    elif curr_short < curr_long:
        signals["sma"] = "SELL"
    else:
        signals["sma"] = "NEUTRAL"

    macd_line, signal_line = calculate_macd(df)
    curr_macd = float(macd_line.iloc[-1])
    curr_sig = float(signal_line.iloc[-1])
    if curr_macd > curr_sig:
        signals["macd"] = "BUY"
    elif curr_macd < curr_sig:
        signals["macd"] = "SELL"
    else:
        signals["macd"] = "NEUTRAL"

    signals["overall"] = _overall(signals)
    return signals


def get_signal_crossover(df: pd.DataFrame) -> dict[str, str]:
    """Signals based on crossover events (fires only on the day lines cross).

    SMA: BUY on Golden Cross (SMA20 crosses above SMA50), SELL on Death Cross.
    MACD: BUY when MACD crosses above signal line, SELL when it crosses below.
    """
    signals: dict[str, str] = {}

    signals["rsi"], _ = _rsi_signal(df)

    sma_short, sma_long = calculate_sma(df)
    prev_short = float(sma_short.iloc[-2])
    prev_long = float(sma_long.iloc[-2])
    curr_short = float(sma_short.iloc[-1])
    curr_long = float(sma_long.iloc[-1])
    if prev_short <= prev_long and curr_short > curr_long:
        signals["sma"] = "BUY"
    elif prev_short >= prev_long and curr_short < curr_long:
        signals["sma"] = "SELL"
    else:
        signals["sma"] = "NEUTRAL"

    macd_line, signal_line = calculate_macd(df)
    prev_macd = float(macd_line.iloc[-2])
    prev_sig = float(signal_line.iloc[-2])
    curr_macd = float(macd_line.iloc[-1])
    curr_sig = float(signal_line.iloc[-1])
    if prev_macd <= prev_sig and curr_macd > curr_sig:
        signals["macd"] = "BUY"
    elif prev_macd >= prev_sig and curr_macd < curr_sig:
        signals["macd"] = "SELL"
    else:
        signals["macd"] = "NEUTRAL"

    signals["overall"] = _overall(signals)
    return signals


def get_signal(df: pd.DataFrame) -> dict[str, str]:
    return get_signal_trend(df)
