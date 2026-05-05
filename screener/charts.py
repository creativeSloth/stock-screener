import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from .indicators import calculate_macd, calculate_rsi, calculate_sma


def plot_stock(ticker: str, df: pd.DataFrame) -> None:
    """Generate and open an interactive Plotly chart for a single stock.

    Includes candlestick chart, SMA lines, RSI and MACD subplots.
    The chart is saved as an HTML file in the output/ directory
    and automatically opened in the default browser.

    Args:
        ticker: Ticker symbol used as chart title (e.g. 'SAP.DE').
        df:     DataFrame with OHLCV columns and datetime index.
    """
    # --- Calculate indicators ---
    # All three indicators are derived from the same DataFrame
    # so they share the same date index and can be plotted on the same x-axis
    sma_short, sma_long = calculate_sma(df)
    rsi: pd.Series = calculate_rsi(df)
    macd_line, signal_line = calculate_macd(df)

    # --- Create subplot layout ---
    # Three vertically stacked subplots sharing the same x-axis (date):
    #   Row 1 (60%): candlestick price chart + SMA overlay
    #   Row 2 (20%): RSI momentum oscillator
    #   Row 3 (20%): MACD trend/momentum indicator
    # shared_xaxes=True means zooming or panning on one row affects all rows
    fig = make_subplots(
        rows=3,
        cols=1,
        shared_xaxes=True,
        row_heights=[0.6, 0.2, 0.2],
        vertical_spacing=0.05,
        subplot_titles=[
            f"{ticker} — Price & Moving Averages",
            "RSI (Relative Strength Index)",
            "MACD (Moving Average Convergence Divergence)"
        ]
    )

    # --- Row 1: Candlestick chart ---
    # Each candle represents one trading day:
    #   Green candle: Close > Open → price rose during the day
    #   Red candle:   Close < Open → price fell during the day
    #   Wick (thin line): shows the High and Low of the day
    # Candlesticks give more information than a simple line chart
    # because they show intraday price range, not just the closing price
    fig.add_trace(
        go.Candlestick(
            x=df.index,
            open=df["Open"].squeeze(),
            high=df["High"].squeeze(),
            low=df["Low"].squeeze(),
            close=df["Close"].squeeze(),
            name="Price",
            increasing_line_color="green",
            decreasing_line_color="red"
        ),
        row=1, col=1
    )

    # --- Row 1: SMA overlay ---
    # The two SMA lines are plotted on top of the candlesticks
    # Their crossover generates the Golden Cross / Death Cross signals:
    #   Blue line  (SMA 20) = short-term trend, reacts faster to price changes
    #   Orange line (SMA 50) = long-term trend, smoother and slower
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=sma_short,
            name="SMA 20 (short-term)",
            line=dict(color="blue", width=1)
        ),
        row=1, col=1
    )
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=sma_long,
            name="SMA 50 (long-term)",
            line=dict(color="orange", width=1)
        ),
        row=1, col=1
    )

    # --- Row 2: RSI ---
    # RSI oscillates between 0 and 100
    # It measures how fast and how much prices have moved recently
    # The dashed horizontal lines mark the key thresholds:
    #   Above 70 (red dashed line)  → overbought → potential sell zone
    #   Below 30 (green dashed line) → oversold  → potential buy zone
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=rsi,
            name="RSI (14)",
            line=dict(color="purple", width=1)
        ),
        row=2, col=1
    )
    # Overbought threshold: if RSI crosses above this, price may be due for a pullback
    fig.add_hline(
        y=70,
        line_dash="dash",
        line_color="red",
        annotation_text="Overbought (70)",
        annotation_position="right",
        row=2, col=1  # type: ignore[arg-type]
    )
    # Oversold threshold: if RSI crosses below this, price may be due for a bounce
    fig.add_hline(
        y=30,
        line_dash="dash",
        line_color="green",
        annotation_text="Oversold (30)",
        annotation_position="right",
        row=2, col=1  # type: ignore[arg-type]
    )

    # --- Row 3: MACD ---
    # MACD shows the relationship between two EMAs (12-day and 26-day)
    # Blue line  (MACD line)   = difference between EMA_12 and EMA_26
    # Red line   (Signal line) = 9-day EMA of the MACD line (smoother)
    # When MACD crosses above signal line → bullish momentum → potential buy
    # When MACD crosses below signal line → bearish momentum → potential sell
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=macd_line,
            name="MACD line",
            line=dict(color="blue", width=1)
        ),
        row=3, col=1
    )
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=signal_line,
            name="Signal line",
            line=dict(color="red", width=1)
        ),
        row=3, col=1
    )

    # --- Layout ---
    # xaxis_rangeslider_visible=False removes the default range slider
    # that Plotly adds to candlestick charts — it clutters the layout
    # template="plotly_dark" gives a professional dark background
    # height=900 ensures all three subplots have enough vertical space
    fig.update_layout(
        title=f"{ticker} — Technical Analysis",
        xaxis_rangeslider_visible=False,
        template="plotly_dark",
        height=900,
        legend=dict(orientation="h", y=-0.1)  # legend below chart
    )

    # --- Save and open ---
    # Replace dots in ticker (e.g. SAP.DE → SAP_DE) for valid filename
    # write_html saves a self-contained HTML file — no server needed,
    # just open it in any browser
    output_path: str = f"output/{ticker.replace('.', '_')}.html"
    fig.write_html(output_path)

    # fig.show() opens the chart directly in the default browser
    fig.show()


if __name__ == "__main__":
    from data import get_stock_data

    df: pd.DataFrame = get_stock_data("SAP.DE")
    plot_stock("SAP.DE", df)
