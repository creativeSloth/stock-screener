import pandas as pd

from screener.charts import plot_stock
from screener.data import get_stock_data, load_all_tickers
from screener.signals import get_signal


def run_screener() -> None:
    """Run the stock screener for all tickers in the watchlists.

    For each ticker:
        1. Download historical OHLCV data via Yahoo Finance
        2. Calculate technical signals (RSI, SMA, MACD)
        3. Print a summary to the terminal
        4. Generate and save an interactive Plotly chart

    Returns:
        None
    """
    tickers: list[str] = load_all_tickers()
    print(f"\n📈 Stock Screener — scanning {len(tickers)} tickers...\n")
    print(f"{'Ticker':<10} {'RSI':<10} {'SMA':<10} {'MACD':<10} {'Overall':<10}")
    print("-" * 50)

    for ticker in tickers:
        try:
            # Download data for this ticker
            df: pd.DataFrame = get_stock_data(ticker)

            # Calculate signals
            signals: dict[str, str] = get_signal(df)

            # Print summary row
            print(
                f"{ticker:<10} "
                f"{signals['rsi']:<10} "
                f"{signals['sma']:<10} "
                f"{signals['macd']:<10} "
                f"{signals['overall']:<10}"
            )

            # Generate and save chart
            plot_stock(ticker, df)

        except Exception as e:
            # Skip ticker on error but keep screener running
            print(f"{ticker:<10} ERROR: {e}")

    print("\n✅ Screening complete. Charts saved to output/")


if __name__ == "__main__":
    run_screener()
