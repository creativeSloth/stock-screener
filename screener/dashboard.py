import json
from datetime import datetime
from pathlib import Path


def _signal_cls(s: str) -> str:
    return {"BUY": "signal-buy", "SELL": "signal-sell"}.get(s, "signal-neutral")


def _overall_cls(s: str) -> str:
    return {"BUY": "overall-buy", "SELL": "overall-sell"}.get(s, "overall-neutral")


def _overall_label(s: str) -> str:
    return {"BUY": "▲ BUY", "SELL": "▼ SELL"}.get(s, "— NEUTRAL")


_CSS = """
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
  background: #0d0d0d; color: #e0e0e0;
  font-family: 'Segoe UI', system-ui, sans-serif;
  padding: 28px 32px;
}
h1 { font-size: 1.5rem; color: #fff; margin-bottom: 4px; }
.meta { color: #555; font-size: 0.82rem; margin-bottom: 20px; }

/* Controls */
.controls {
  display: flex; align-items: center; gap: 16px;
  margin-bottom: 12px;
}
.controls label { color: #666; font-size: 0.85rem; }
#method-select {
  background: #1a1a1a; color: #e0e0e0;
  border: 1px solid #333; border-radius: 4px;
  padding: 5px 10px; font-size: 0.85rem; cursor: pointer;
}
#method-select:focus { outline: none; border-color: #555; }
.info-btn {
  background: none; border: 1px solid #333; border-radius: 4px;
  color: #666; padding: 5px 12px; font-size: 0.82rem;
  cursor: pointer; transition: all 0.15s;
}
.info-btn:hover { border-color: #555; color: #aaa; }
.info-btn.active { border-color: #555; color: #aaa; background: #1a1a1a; }

/* Info panel */
.info-panel {
  display: none; background: #111; border: 1px solid #222;
  border-radius: 6px; padding: 20px 24px; margin-bottom: 28px;
}
.info-panel.open { display: block; }
.info-grid { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 20px; margin-top: 16px; }
.info-card {
  background: #161616; border-radius: 5px; padding: 16px;
  border: 1px solid #1e1e1e; transition: border-color 0.2s;
}
.info-card.active-method { border-color: #333; }
.info-card h3 { font-size: 0.9rem; color: #fff; margin-bottom: 6px; }
.info-card .badge {
  font-size: 0.7rem; color: #555; background: #222;
  padding: 1px 6px; border-radius: 3px; margin-left: 6px;
  vertical-align: middle;
}
.info-card p { font-size: 0.82rem; color: #777; line-height: 1.6; margin-bottom: 8px; }
.info-card ul { font-size: 0.82rem; color: #777; padding-left: 16px; line-height: 1.7; }
.info-card .pro { color: #00c853; font-size: 0.78rem; margin-top: 6px; }
.info-card .con { color: #ff6b6b; font-size: 0.78rem; }
.info-card .source {
  font-size: 0.73rem; color: #3a3a3a; margin-top: 10px;
  border-top: 1px solid #1e1e1e; padding-top: 8px; line-height: 1.5;
}
.info-card .source em { color: #444; font-style: italic; }

/* Index sections */
.index-section { margin-bottom: 44px; }
.index-title {
  font-size: 1rem; font-weight: 600; color: #999;
  margin-bottom: 10px; padding-bottom: 6px;
  border-bottom: 1px solid #222;
}
.index-counts { color: #444; font-size: 0.8rem; font-weight: 400; margin-left: 8px; }

/* Table */
table { width: 100%; border-collapse: collapse; font-size: 0.88rem; }
th {
  text-align: left; padding: 8px 14px;
  background: #141414; color: #555;
  font-weight: 500; letter-spacing: 0.05em; font-size: 0.78rem;
  text-transform: uppercase; position: sticky; top: 0;
}
tr.stock-row { cursor: pointer; transition: background 0.12s; }
tr.stock-row:hover { background: #181818; }
tr.stock-row.active { background: #0d1f10; }
td { padding: 7px 14px; border-bottom: 1px solid #161616; }

.ticker { font-weight: 600; color: #fff; font-family: monospace; font-size: 0.9rem; }
.rsi-val { color: #666; }

.signal-buy     { color: #00c853; font-weight: 500; }
.signal-sell    { color: #ff1744; font-weight: 500; }
.signal-neutral { color: #3a3a3a; }

.overall-buy  { color: #00c853; font-weight: 700; background: #071a0e;
                padding: 2px 10px; border-radius: 4px; }
.overall-sell { color: #ff1744; font-weight: 700; background: #1a0707;
                padding: 2px 10px; border-radius: 4px; }
.overall-neutral { color: #3a3a3a; }

/* Chart panel */
#chart-panel {
  position: fixed; bottom: 0; left: 0; right: 0;
  height: 0; background: #111;
  border-top: 2px solid #222;
  transition: height 0.25s ease;
  z-index: 100; overflow: hidden;
}
#chart-panel.open { height: 62vh; }
#chart-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 7px 18px; background: #161616; border-bottom: 1px solid #222;
}
#chart-title { font-weight: 600; color: #fff; font-family: monospace; }
#chart-close {
  cursor: pointer; background: none; border: none;
  color: #666; font-size: 1.1rem; line-height: 1;
}
#chart-close:hover { color: #fff; }
#chart-frame { width: 100%; height: calc(62vh - 36px); border: none; background: #111; }
body.panel-open { padding-bottom: 62vh; }
"""

_INFO_PANEL = """
<div class="info-panel" id="info-panel">
  <div class="info-grid">

    <div class="info-card" id="card-rsi">
      <h3>RSI <span class="badge">Both methods</span></h3>
      <p>Relative Strength Index measures momentum — how fast and how much prices are moving recently.</p>
      <ul>
        <li>RSI &lt; 30 → Oversold → potential <strong style="color:#00c853">BUY</strong></li>
        <li>RSI &gt; 70 → Overbought → potential <strong style="color:#ff1744">SELL</strong></li>
        <li>30–70 → Neutral</li>
      </ul>
      <p class="source">
        Wilder, J.W. Jr. (1978). <em>New Concepts in Technical Trading Systems</em>. Trend Research.<br>
        MACD: Appel, G. (2005). <em>Technical Analysis: Power Tools for Active Investors</em>. FT Press.
      </p>
    </div>

    <div class="info-card" id="card-trend">
      <h3>Trend Position</h3>
      <p>Evaluates the <em>current state</em> of each indicator — whether the market is in a bullish or bearish phase right now.</p>
      <ul>
        <li><strong>SMA:</strong> BUY if SMA 20 &gt; SMA 50 (short-term above long-term). SELL if below.</li>
        <li><strong>MACD:</strong> BUY if MACD line &gt; signal line. SELL if below.</li>
      </ul>
      <p class="pro">✓ Reflects ongoing trends. More frequent, actionable signals.</p>
      <p class="con">✗ Can produce false signals in sideways markets (whipsaw).</p>
      <p class="source">
        Murphy, J.J. (1999). <em>Technical Analysis of the Financial Markets</em>. New York Institute of Finance, pp. 195–228.<br>
        Kaufman, P.J. (2013). <em>Trading Systems and Methods</em>. Wiley, 5th ed.
      </p>
    </div>

    <div class="info-card" id="card-cross">
      <h3>Crossover</h3>
      <p>Detects the <em>exact moment</em> a trend changes direction. A signal fires only on the day indicator lines cross.</p>
      <ul>
        <li><strong>SMA:</strong> BUY on Golden Cross (SMA 20 crosses above SMA 50). SELL on Death Cross.</li>
        <li><strong>MACD:</strong> BUY when MACD crosses above signal line. SELL when it crosses below.</li>
      </ul>
      <p class="pro">✓ Fewer, more deliberate signals. Historically validated.</p>
      <p class="con">✗ Lagging — trend has already shifted before the signal fires.</p>
      <p class="source">
        Brock, W., Lakonishok, J., &amp; LeBaron, B. (1992). "Simple Technical Trading Rules and the Stochastic Properties of Stock Returns."
        <em>Journal of Finance</em>, 47(5), 1731–1764.
      </p>
    </div>

  </div>
</div>
"""

_JS = """
  let _active = null;
  let _method = 'trend';

  const SIG_CLS = { BUY: 'signal-buy', SELL: 'signal-sell', NEUTRAL: 'signal-neutral' };
  const OVR_CLS = { BUY: 'overall-buy', SELL: 'overall-sell', NEUTRAL: 'overall-neutral' };
  const OVR_LBL = { BUY: '▲ BUY', SELL: '▼ SELL', NEUTRAL: '— NEUTRAL' };

  function setMethod(method) {
    _method = method;
    const key = method === 'trend' ? 'trend' : 'cross';

    document.querySelectorAll('tr.stock-row').forEach(row => {
      const data = JSON.parse(row.dataset[key]);
      ['rsi','sma','macd'].forEach(ind => {
        const cell = row.querySelector('.cell-' + ind);
        cell.textContent = data[ind];
        cell.className = 'cell-' + ind + ' ' + SIG_CLS[data[ind]];
      });
      const span = row.querySelector('.cell-overall span');
      span.textContent = OVR_LBL[data.overall];
      span.className = OVR_CLS[data.overall];
    });

    document.querySelectorAll('.index-title').forEach(el => {
      el.querySelector('.buy-count').textContent = el.dataset[key + 'Buy'] + ' BUY';
      el.querySelector('.sell-count').textContent = el.dataset[key + 'Sell'] + ' SELL';
    });

    document.getElementById('card-trend').classList.toggle('active-method', method === 'trend');
    document.getElementById('card-cross').classList.toggle('active-method', method === 'cross');
  }

  function toggleInfo() {
    const panel = document.getElementById('info-panel');
    const btn = document.getElementById('info-btn');
    panel.classList.toggle('open');
    btn.classList.toggle('active');
  }

  function showChart(id, file) {
    if (_active) _active.classList.remove('active');
    _active = document.getElementById('row-' + id);
    if (_active) _active.classList.add('active');
    document.getElementById('chart-title').textContent = id.replace(/_/g, '.');
    document.getElementById('chart-frame').src = file;
    document.getElementById('chart-panel').classList.add('open');
    document.body.classList.add('panel-open');
  }

  function closeChart() {
    document.getElementById('chart-panel').classList.remove('open');
    document.body.classList.remove('panel-open');
    document.getElementById('chart-frame').src = 'about:blank';
    if (_active) { _active.classList.remove('active'); _active = null; }
  }

  // Highlight default method card on load
  document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('card-trend').classList.add('active-method');
  });
"""


def build_dashboard(
    results: list[dict],
    output_path: str = "output/dashboard.html",
) -> None:
    """Generate a single HTML dashboard with dual signal method switcher.

    Args:
        results: List of dicts with keys: index_name, ticker, signals,
                 signals_crossover, rsi_value.
        output_path: Path for the generated HTML file.
    """
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    by_index: dict[str, list[dict]] = {}
    for r in results:
        by_index.setdefault(r["index_name"], []).append(r)

    parts: list[str] = []
    parts.append(
        f'<!DOCTYPE html><html lang="de"><head><meta charset="utf-8">'
        f'<title>Stock Screener</title>'
        f'<style>{_CSS}</style></head><body>\n'
        f'<h1>Stock Screener</h1>\n'
        f'<p class="meta">{now} &nbsp;·&nbsp; {len(results)} stocks</p>\n'
    )

    # Controls
    parts.append(
        '<div class="controls">'
        '<label for="method-select">Signal method:</label>'
        '<select id="method-select" onchange="setMethod(this.value)">'
        '<option value="trend" selected>Trend Position</option>'
        '<option value="cross">Crossover</option>'
        '</select>'
        '<button class="info-btn" id="info-btn" onclick="toggleInfo()">ℹ Methodology</button>'
        '</div>'
    )
    parts.append(_INFO_PANEL)

    for index_name, rows in by_index.items():
        trend_buy = sum(1 for r in rows if r["signals"]["overall"] == "BUY")
        trend_sell = sum(1 for r in rows if r["signals"]["overall"] == "SELL")
        cross = [r.get("signals_crossover", r["signals"]) for r in rows]
        cross_buy = sum(1 for s in cross if s["overall"] == "BUY")
        cross_sell = sum(1 for s in cross if s["overall"] == "SELL")

        parts.append('<div class="index-section">')
        parts.append(
            f'<div class="index-title" '
            f'data-trend-buy="{trend_buy}" data-trend-sell="{trend_sell}" '
            f'data-cross-buy="{cross_buy}" data-cross-sell="{cross_sell}">'
            f'{index_name}'
            f'<span class="index-counts">'
            f'&nbsp; {len(rows)} stocks &nbsp;'
            f'<span class="buy-count" style="color:#00c853">{trend_buy} BUY</span> &nbsp;'
            f'<span class="sell-count" style="color:#ff1744">{trend_sell} SELL</span>'
            f'</span></div>'
        )
        parts.append(
            '<table><thead><tr>'
            '<th>Ticker</th><th>RSI</th>'
            '<th>RSI Signal</th><th>SMA Signal</th><th>MACD Signal</th>'
            '<th>Overall</th>'
            '</tr></thead><tbody>'
        )

        for r in rows:
            ticker = r["ticker"]
            sig = r["signals"]
            sig_cross = r.get("signals_crossover", sig)
            safe = ticker.replace(".", "_")
            filename = safe + ".html"

            trend_json = json.dumps({k: sig[k] for k in ("rsi", "sma", "macd", "overall")})
            cross_json = json.dumps({k: sig_cross[k] for k in ("rsi", "sma", "macd", "overall")})

            parts.append(
                f'<tr class="stock-row" id="row-{safe}" '
                f"data-trend='{trend_json}' "
                f"data-cross='{cross_json}' "
                f'onclick="showChart(\'{safe}\',\'{filename}\')">'
                f'<td class="ticker">{ticker}</td>'
                f'<td class="rsi-val">{r["rsi_value"]:.1f}</td>'
                f'<td class="cell-rsi {_signal_cls(sig["rsi"])}">{sig["rsi"]}</td>'
                f'<td class="cell-sma {_signal_cls(sig["sma"])}">{sig["sma"]}</td>'
                f'<td class="cell-macd {_signal_cls(sig["macd"])}">{sig["macd"]}</td>'
                f'<td class="cell-overall"><span class="{_overall_cls(sig["overall"])}">'
                f'{_overall_label(sig["overall"])}</span></td>'
                f'</tr>'
            )

        parts.append('</tbody></table></div>')

    parts.append(
        '<div id="chart-panel">'
        '<div id="chart-header">'
        '<span id="chart-title"></span>'
        '<button id="chart-close" onclick="closeChart()">✕</button>'
        '</div>'
        '<iframe id="chart-frame" src="about:blank"></iframe>'
        '</div>'
        f'<script>{_JS}</script>'
        '</body></html>'
    )

    Path(output_path).parent.mkdir(exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(parts))
