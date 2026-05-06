import subprocess
from pathlib import Path

_CSS = """
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
  background: #0d0d0d; color: #e0e0e0;
  font-family: 'Segoe UI', system-ui, sans-serif;
  padding: 28px 32px;
}
h1 { font-size: 1.5rem; color: #fff; margin-bottom: 8px; }
.status {
  color: #555; font-size: 0.88rem; margin-bottom: 20px;
  font-family: monospace;
}
.progress-wrap {
  width: 100%; height: 5px; background: #1a1a1a;
  border-radius: 3px; margin-bottom: 8px;
  overflow: hidden;
}
.progress-fill {
  height: 100%; background: #00c853;
  border-radius: 3px;
}
.count { color: #3a3a3a; font-size: 0.8rem; }
"""


def _render(count: int, total: int, current: str, done: bool) -> str:
    pct = int(count / total * 100) if total else 0
    refresh = (
        '<meta http-equiv="refresh" content="0;url=dashboard.html">'
        if done else
        '<meta http-equiv="refresh" content="2">'
    )
    status = "Redirecting to dashboard..." if done else f"Processing: {current}"

    return (
        f'<!DOCTYPE html><html lang="de"><head><meta charset="utf-8">'
        f'{refresh}'
        f'<title>Stock Screener — Running</title>'
        f'<style>{_CSS}</style></head><body>'
        f'<h1>Stock Screener</h1>'
        f'<p class="status">{status}</p>'
        f'<div class="progress-wrap">'
        f'<div class="progress-fill" style="width:{pct}%"></div>'
        f'</div>'
        f'<p class="count">{count} / {total} &nbsp;·&nbsp; {pct}%</p>'
        f'</body></html>'
    )


def _write(html: str, output_path: str) -> None:
    Path(output_path).parent.mkdir(exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)


def init_progress(total: int, output_path: str = "output/progress.html") -> None:
    _write(_render(0, total, "—", done=False), output_path)
    subprocess.Popen(["xdg-open", f"file://{Path(output_path).resolve()}"])


def update_progress(
    count: int,
    total: int,
    current: str,
    output_path: str = "output/progress.html",
) -> None:
    _write(_render(count, total, current, done=False), output_path)


def finish_progress(output_path: str = "output/progress.html") -> None:
    _write(_render(0, 0, "", done=True), output_path)
