import webbrowser
from datetime import datetime
from pathlib import Path


_SIGNAL_CLS = {"BUY": "signal-buy", "SELL": "signal-sell"}
_OVERALL_CLS = {"BUY": "overall-buy", "SELL": "overall-sell"}
_OVERALL_LABEL = {"BUY": "▲ BUY", "SELL": "▼ SELL"}


def _signal_cls(s: str) -> str:
    return _SIGNAL_CLS.get(s, "signal-neutral")


def _overall_cls(s: str) -> str:
    return _OVERALL_CLS.get(s, "overall-neutral")


def _overall_label(s: str) -> str:
    return _OVERALL_LABEL.get(s, "— NEUTRAL")


_CSS = """
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
  background: #0d0d0d; color: #e0e0e0;
  font-family: 'Segoe UI', system-ui, sans-serif;
  padding: 28px 32px;
}
h1 { font-size: 1.5rem; color: #fff; margin-bottom: 4px; }
.meta { color: #555; font-size: 0.82rem; margin-bottom: 36px; }

.index-section { margin-bottom: 44px; }
.index-title {
  font-size: 1rem; font-weight: 600; color: #999;
  margin-bottom: 10px; padding-bottom: 6px;
  border-bottom: 1px solid #222;
}
.index-counts { color: #444; font-size: 0.8rem; font-weight: 400; margin-left: 8px; }

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

#chart-panel {
  position: fixed; bottom: 0; left: 0; right: 0;
  height: 0; background: #111;
  border-top: 2px solid #222;
  transition: height 0.25s ease;
  z-index: 100;
  overflow: hidden;
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
#chart-frame {
  width: 100%; height: calc(62vh - 36px);
  border: none; background: #111;
}
body.panel-open { padding-bottom: 62vh; }
"""

_JS = """
  let _active = null;
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
"""


def build_dashboard(
    results: list[dict],
    output_path: str = "output/dashboard.html",
) -> None:
    """Generate a single HTML dashboard and open it in the browser.

    Args:
        results: List of dicts with keys: index_name, ticker, signals, rsi_value.
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

    for index_name, rows in by_index.items():
        buy_n = sum(1 for r in rows if r["signals"]["overall"] == "BUY")
        sell_n = sum(1 for r in rows if r["signals"]["overall"] == "SELL")

        parts.append(f'<div class="index-section">')
        parts.append(
            f'<div class="index-title">{index_name}'
            f'<span class="index-counts">'
            f'&nbsp; {len(rows)} stocks &nbsp;'
            f'<span style="color:#00c853">{buy_n} BUY</span> &nbsp;'
            f'<span style="color:#ff1744">{sell_n} SELL</span>'
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
            safe = ticker.replace(".", "_")
            filename = safe + ".html"
            parts.append(
                f'<tr class="stock-row" id="row-{safe}" '
                f'onclick="showChart(\'{safe}\',\'{filename}\')">'
                f'<td class="ticker">{ticker}</td>'
                f'<td class="rsi-val">{r["rsi_value"]:.1f}</td>'
                f'<td class="{_signal_cls(sig["rsi"])}">{sig["rsi"]}</td>'
                f'<td class="{_signal_cls(sig["sma"])}">{sig["sma"]}</td>'
                f'<td class="{_signal_cls(sig["macd"])}">{sig["macd"]}</td>'
                f'<td><span class="{_overall_cls(sig["overall"])}">'
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

    webbrowser.open(f"file://{Path(output_path).resolve()}")
