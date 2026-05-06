# 📈 Stock Screener

A Python-based stock screening and signal tool for German and US equities — built with **yfinance**, **Pandas**, and **Plotly**.

Automatically fetches index constituents from Wikipedia, calculates technical indicators, and presents buy/sell signals in a single interactive dashboard.

---

## 🚀 Features

- Fetches live index constituents (DAX, MDAX, Dow Jones, NASDAQ 100, S&P 500) from Wikipedia — no manual watchlists required
- 7-day local cache to avoid repeated Wikipedia requests
- Downloads historical market data via Yahoo Finance (no API key required)
- Calculates key technical indicators: RSI, Moving Averages (SMA 20/50), MACD
- Single HTML dashboard with color-coded signals per index — no more one-tab-per-stock
- Dashboard shows company name and WKN (derived from ISIN via yfinance, German stocks only)
- Click any row in the dashboard to load its full interactive chart inline

---

## 🛠️ Tech Stack

| Layer           | Technology               |
| --------------- | ------------------------ |
| Index universe  | Wikipedia + requests     |
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
│   ├── universe.py      # Wikipedia scraper + 7-day cache
│   ├── data.py          # yfinance data loader
│   ├── indicators.py    # RSI, SMA, MACD calculations
│   ├── signals.py       # Signal logic — trend position & crossover
│   ├── charts.py        # Plotly chart generation (per stock)
│   ├── dashboard.py     # Single-page HTML dashboard with method switcher
│   └── progress.py      # Browser progress page (auto-refreshes while running)
├── cache/               # Auto-generated universe cache (gitignored)
├── output/              # Generated HTML files (gitignored)
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

The dashboard opens automatically in your browser at `output/dashboard.html`.

---

## ⚙️ Configuration

Edit `config.py` to customize the screener:

```python
@dataclass
class Config:
    # Indices to scan — available: DAX, MDAX, DOW, NASDAQ100, SP500
    indices: list[str] = ["DAX"]

    period: str = "6mo"   # Data lookback period
    interval: str = "1d"  # Candle interval
    rsi_period: int = 14  # RSI calculation window
    sma_short: int = 20   # Short moving average
    sma_long: int = 50    # Long moving average
```

---

## 📊 Indicators & Signals

### RSI (Relative Strength Index)

Applies to both signal methods.

| Value | Signal                         |
| ----- | ------------------------------ |
| < 30  | 🟢 Oversold → potential buy    |
| > 70  | 🔴 Overbought → potential sell |
| 30–70 | ⚪ Neutral                     |

> Source: Wilder, J.W. Jr. (1978). _New Concepts in Technical Trading Systems_. Trend Research.

---

### Signal Methods (switchable in the dashboard)

The dashboard offers a dropdown to switch between two calculation methods for SMA and MACD signals:

#### Trend Position (default)

Evaluates the **current state** of each indicator — whether the market is in a bullish or bearish phase right now.

| Indicator | BUY                     | SELL                    |
| --------- | ----------------------- | ----------------------- |
| SMA       | SMA 20 > SMA 50         | SMA 20 < SMA 50         |
| MACD      | MACD line > Signal line | MACD line < Signal line |

✓ More frequent signals, reflects ongoing trends  
✗ Can produce false signals in sideways markets (whipsaw)

> Source: Murphy, J.J. (1999). _Technical Analysis of the Financial Markets_. New York Institute of Finance. — Kaufman, P.J. (2013). _Trading Systems and Methods_. Wiley, 5th ed.

#### Crossover

Detects the **exact moment** a trend changes direction. A signal fires only on the day the indicator lines cross.

| Indicator | BUY                                        | SELL                                      |
| --------- | ------------------------------------------ | ----------------------------------------- |
| SMA       | Golden Cross (SMA 20 crosses above SMA 50) | Death Cross (SMA 20 crosses below SMA 50) |
| MACD      | MACD crosses above signal line             | MACD crosses below signal line            |

✓ Fewer, deliberate signals — historically validated  
✗ Lagging by nature — trend has already shifted before the signal fires

> Source: Brock, W., Lakonishok, J., & LeBaron, B. (1992). "Simple Technical Trading Rules and the Stochastic Properties of Stock Returns." _Journal of Finance_, 47(5), 1731–1764.

---

### Overall Signal

At least 2 out of 3 indicators must agree to generate a BUY or SELL signal.

---

## 🖥️ Dashboard

Running `python main.py` opens a single `output/dashboard.html` with:

- A color-coded summary table per index (🟢 BUY / 🔴 SELL / neutral)
- Company name and WKN per stock (WKN available for German stocks only)
- RSI value and individual indicator signals per stock
- Click any row → detail chart slides up inline (candlestick, SMA, RSI, MACD)

---

## ⚠️ Disclaimer

This tool is for **educational and informational purposes only**. It does not constitute financial advice. Always do your own research before making investment decisions.

---

## 🗺️ Roadmap

- [ ] Add pytest test suite
- [ ] E-mail summary (daily digest)
- [ ] Streamlit dashboard incl. watchlist management
- [ ] Backtesting module
- [ ] Docker support

---

## 👤 Author

**Edgar** · [github.com/creativeSloth](https://github.com/creativeSloth)

---

## 📄 License

MIT
