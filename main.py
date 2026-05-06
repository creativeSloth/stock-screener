import pandas as pd

from config import Config
from screener.charts import plot_stock
from screener.data import get_stock_data
from screener.signals import get_signal
from screener.universe import load_universe

config = Config()


def run_screener() -> None:
    print("\n📈 Stock Screener\n")
    print(f"Indices: {', '.join(config.indices)}\n")

    universe: dict[str, list[str]] = load_universe(config.indices)

    for index_name, tickers in universe.items():
        print(f"\n── {index_name} ({len(tickers)} stocks) ──")
        print(f"{'Ticker':<12} {'RSI':<10} {'SMA':<10} {'MACD':<10} {'Overall':<10}")
        print("-" * 55)

        for ticker in tickers:
            try:
                df: pd.DataFrame = get_stock_data(ticker)
                signals: dict[str, str] = get_signal(df)
                print(
                    f"{ticker:<12} "
                    f"{signals['rsi']:<10} "
                    f"{signals['sma']:<10} "
                    f"{signals['macd']:<10} "
                    f"{signals['overall']:<10}"
                )
                plot_stock(ticker, df)
            except Exception as e:
                print(f"{ticker:<12} ERROR: {e}")

    print("\n✅ Screening complete. Charts saved to output/")


if __name__ == "__main__":
    run_screener()
