import pandas as pd

from config import Config
from screener.charts import plot_stock
from screener.dashboard import build_dashboard
from screener.data import get_stock_data
from screener.indicators import calculate_rsi
from screener.progress import finish_progress, init_progress, update_progress
from screener.signals import get_signal_crossover, get_signal_trend
from screener.universe import load_universe

config = Config()


def run_screener() -> None:
    print("\n📈 Stock Screener\n")
    print(f"Indices: {', '.join(config.indices)}\n")

    universe: dict[str, list[str]] = load_universe(config.indices)

    results: list[dict] = []
    total = sum(len(t) for t in universe.values())
    count = 0

    init_progress(total)

    for index_name, stocks in universe.items():
        print(f"\n── {index_name} ({len(stocks)} stocks) ──")

        for stock in stocks:
            ticker: str = stock["ticker"]
            name: str = stock.get("name", "")
            wkn: str = stock.get("wkn", "")
            isin: str = stock.get("isin", "")
            cusip: str = stock.get("cusip", "")
            count += 1
            try:
                df: pd.DataFrame = get_stock_data(ticker)
                signals_trend: dict[str, str] = get_signal_trend(df)
                signals_crossover: dict[str, str] = get_signal_crossover(df)
                rsi_value: float = float(calculate_rsi(df).iloc[-1])

                overall = signals_trend["overall"]
                marker = {"BUY": "▲", "SELL": "▼"}.get(overall, "–")
                print(f"  [{count}/{total}] {ticker:<12} {marker} {overall}")

                plot_stock(ticker, df)

                results.append({
                    "index_name": index_name,
                    "ticker": ticker,
                    "name": name,
                    "wkn": wkn,
                    "isin": isin,
                    "cusip": cusip,
                    "signals": signals_trend,
                    "signals_crossover": signals_crossover,
                    "rsi_value": rsi_value,
                })

            except Exception as e:
                print(f"  [{count}/{total}] {ticker:<12} ERROR: {e}")

            update_progress(count, total, ticker)

    print("\n✅ Generating dashboard...")
    build_dashboard(results)
    finish_progress()
    print("Done — dashboard.html")


if __name__ == "__main__":
    run_screener()
