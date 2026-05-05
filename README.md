# 📈 Stock Screener

A Python-based stock screening and signal tool for German and US equities — built with **yfinance**, **Pandas**, and **Plotly**.

Automatically scans a watchlist of stocks, calculates technical indicators, and visualizes buy/sell signals in an interactive browser chart.

---

## 🚀 Features

- Fetches live and historical market data via Yahoo Finance (no API key required)
- Calculates key technical indicators: RSI, Moving Averages (SMA 20/50), MACD
- Screens multiple stocks simultaneously and ranks by signal strength
- Interactive browser charts with Plotly (candlesticks, indicators, signal markers)
- Supports DAX, MDAX, S&P 500, and Nasdaq stocks

---

## 🛠️ Tech Stack

| Layer           | Technology               |
| --------------- | ------------------------ |
| Data source     | yfinance (Yahoo Finance) |
| Data processing | Pandas, NumPy            |
| Visualization   | Plotly                   |
| Language        | Python 3.10+             |

---

## 📁 Project Structure

```
stock-screener/
├── screener/
│   ├── __init__.py
│   ├── data.py          # yfinance data loader
│   ├── indicators.py    # RSI, SMA, MACD calculations
│   ├── signals.py       # Signal logic (buy/sell/neutral)
│   └── charts.py        # Plotly chart generation
├── watchlists/
│   ├── dax.txt          # German stock tickers
│   └── us.txt           # US stock tickers
├── output/              # Generated HTML charts
├── main.py              # Entry point — run the screener
├── config.py            # Configurable parameters
├── requirements.txt
└── README.md
```

---

## ⚙️ Installation

```bash
# Clone the repository
git clone https://github.com/creativeSloth/stock-screener.git
cd stock-screener

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the screener
python main.py
```

Charts open automatically in your browser. HTML files are saved to `/output`.

---

## 📊 Indicators & Signals

### RSI (Relative Strength Index)

| Value | Signal                         |
| ----- | ------------------------------ |
| < 30  | 🟢 Oversold → potential buy    |
| > 70  | 🔴 Overbought → potential sell |
| 30–70 | ⚪ Neutral                     |

### Moving Averages (SMA 20 / SMA 50)

- **Golden Cross** (SMA 20 crosses above SMA 50) → 🟢 Buy signal
- **Death Cross** (SMA 20 crosses below SMA 50) → 🔴 Sell signal

### MACD

- MACD line crosses above signal line → 🟢 Bullish momentum
- MACD line crosses below signal line → 🔴 Bearish momentum

---

## 🖥️ Example Output

```
Screening 20 stocks...

Ticker   RSI     SMA Signal    MACD Signal   Overall
------   -----   ----------    -----------   -------
SAP.DE   28.4    Golden Cross  Bullish       🟢 STRONG BUY
BAYN.DE  71.2    Neutral       Bearish       🔴 SELL
AAPL     45.8    Neutral       Bullish       ⚪ NEUTRAL
NVDA     33.1    Golden Cross  Bullish       🟢 BUY
```

---

## ⚙️ Configuration

Edit `config.py` to customize the screener:

```python
PERIOD = "6mo"          # Data lookback period
INTERVAL = "1d"         # Candle interval
RSI_PERIOD = 14         # RSI calculation window
SMA_SHORT = 20          # Short moving average
SMA_LONG = 50           # Long moving average
```

---

## ⚠️ Disclaimer

This tool is for **educational and informational purposes only**. It does not constitute financial advice. Always do your own research before making investment decisions.

---

## 🗺️ Roadmap

- [ ] Add pytest test suite
- [ ] Migrate watchlists from .txt files to SQLite database (SQLAlchemy + CRUD via CLI)
- [ ] E-mail summary (daily digest)
- [ ] Streamlit dashboard incl. watchlist management (add, delete, group tickers)
- [ ] Backtesting module
- [ ] Docker support

---

## 👤 Author

**Edgar** · [github.com/creativeSloth](https://github.com/creativeSloth)

---

## 📄 License

MIT
