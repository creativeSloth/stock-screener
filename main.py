import pandas as pd

from config import Config
from screener.charts import plot_stock
from screener.dashboard import build_dashboard
from screener.data import get_stock_data
from screener.indicators import calculate_rsi
from screener.signals import get_signal
from screener.universe import load_universe

config = Config()


def run_screener() -> None:
    print("\n📈 Stock Screener\n")
    print(f"Indices: {', '.join(config.indices)}\n")

    universe: dict[str, list[str]] = load_universe(config.indices)

    results: list[dict] = []

    for index_name, tickers in universe.items():
        print(f"\n── {index_name} ({len(tickers)} stocks) ──")

        for ticker in tickers:
            try:
                df: pd.DataFrame = get_stock_data(ticker)
                signals: dict[str, str] = get_signal(df)
                rsi_value: float = float(calculate_rsi(df).iloc[-1])

                overall = signals["overall"]
                marker = {"BUY": "▲", "SELL": "▼"}.get(overall, "–")
                print(f"  {ticker:<12} {marker} {overall}")

                plot_stock(ticker, df)

                results.append({
                    "index_name": index_name,
                    "ticker": ticker,
                    "signals": signals,
                    "rsi_value": rsi_value,
                })

            except Exception as e:
                print(f"  {ticker:<12} ERROR: {e}")

    print("\n✅ Generating dashboard...")
    build_dashboard(results)
    print("Dashboard saved to output/dashboard.html")


if __name__ == "__main__":
    run_screener()
