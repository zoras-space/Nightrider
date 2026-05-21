"""Small local dashboard for watching the Nightrider run."""

from __future__ import annotations

import argparse
import errno
import html
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
LOG_DIR = ROOT / "agent_logs"
WORKSPACE_SOLUTION = ROOT / "workspace" / "solution.py"
LOG_FILES = (
    "test_runs.log",
    "commands.log",
    "decisions.log",
    "errors.log",
    "human_interventions.log",
    "final_report.md",
)


def read_text(path: Path, max_chars: int = 18000) -> str:
    if not path.exists():
        return "<missing>"
    text = path.read_text(encoding="utf-8", errors="replace")
    if len(text) <= max_chars:
        return text
    return text[-max_chars:]


def split_entries(text: str, limit: int = 6) -> list[str]:
    entries: list[str] = []
    current: list[str] = []
    for line in text.splitlines():
        if line.startswith("[20") and current:
            entries.append("\n".join(current).strip())
            current = [line]
        else:
            current.append(line)
    if current:
        entries.append("\n".join(current).strip())
    return [entry for entry in entries if entry][-limit:]


def parse_latest_test_status(test_log: str) -> dict[str, str]:
    entries = split_entries(test_log, limit=1)
    if not entries:
        return {"status": "Waiting", "detail": "No test run logged yet."}
    latest = entries[-1]
    if "exit_code: 0" in latest:
        return {"status": "Passing", "detail": "Latest test command exited with code 0."}
    if "exit_code:" in latest:
        return {"status": "Failing", "detail": "Latest test command exited nonzero."}
    return {"status": "Unknown", "detail": "Latest test entry could not be classified."}


def dashboard_data() -> dict[str, Any]:
    logs = {name: read_text(LOG_DIR / name) for name in LOG_FILES}
    return {
        "status": parse_latest_test_status(logs["test_runs.log"]),
        "logs": {name: split_entries(content) for name, content in logs.items()},
        "solution": read_text(WORKSPACE_SOLUTION, max_chars=12000),
        "solution_path": str(WORKSPACE_SOLUTION),
    }


def render_page() -> bytes:
    data_json = json.dumps(dashboard_data()).replace("</", "<\\/")
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Nightrider Dashboard</title>
  <style>
    :root {{
      color-scheme: dark;
      --bg: #0d1117;
      --panel: #151b23;
      --panel-2: #0f1620;
      --text: #e6edf3;
      --muted: #8b949e;
      --line: #30363d;
      --green: #3fb950;
      --amber: #d29922;
      --red: #f85149;
      --blue: #58a6ff;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background: var(--bg);
      color: var(--text);
    }}
    header {{
      border-bottom: 1px solid var(--line);
      padding: 18px 22px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
      background: #0b1016;
      position: sticky;
      top: 0;
      z-index: 2;
    }}
    h1 {{ font-size: 20px; margin: 0; letter-spacing: 0; }}
    .sub {{ color: var(--muted); font-size: 13px; margin-top: 3px; }}
    .status {{
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 9px 12px;
      background: var(--panel);
      min-width: 190px;
      text-align: right;
    }}
    .status strong {{ display: block; font-size: 15px; }}
    .status span {{ color: var(--muted); font-size: 12px; }}
    main {{
      display: grid;
      grid-template-columns: minmax(0, 1fr) minmax(360px, 0.85fr);
      gap: 16px;
      padding: 16px;
    }}
    section {{
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--panel);
      min-width: 0;
      overflow: hidden;
    }}
    section h2 {{
      font-size: 14px;
      margin: 0;
      padding: 11px 13px;
      border-bottom: 1px solid var(--line);
      color: #f0f6fc;
      background: var(--panel-2);
    }}
    .grid {{ display: grid; gap: 16px; }}
    .entry {{
      margin: 0;
      padding: 12px 13px;
      border-bottom: 1px solid var(--line);
      white-space: pre-wrap;
      overflow-wrap: anywhere;
      color: #c9d1d9;
      font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
      font-size: 12px;
      line-height: 1.45;
    }}
    .entry:last-child {{ border-bottom: 0; }}
    pre.code {{
      margin: 0;
      padding: 13px;
      white-space: pre-wrap;
      overflow-wrap: anywhere;
      font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
      font-size: 12px;
      line-height: 1.5;
      color: #d2e3f5;
    }}
    .empty {{ color: var(--muted); padding: 13px; font-size: 13px; }}
    @media (max-width: 980px) {{
      main {{ grid-template-columns: 1fr; }}
      header {{ align-items: flex-start; flex-direction: column; }}
      .status {{ text-align: left; width: 100%; }}
    }}
  </style>
</head>
<body>
  <header>
    <div>
      <h1>Nightrider Control</h1>
      <div class="sub">Live view of tests, commands, decisions, errors, and generated code. Refreshes every 2 seconds.</div>
    </div>
    <div class="status" id="status"><strong>Loading</strong><span>Waiting for log data</span></div>
  </header>
  <main>
    <div class="grid">
      <section><h2>Latest Test Runs</h2><div id="test_runs"></div></section>
      <section><h2>Latest Commands</h2><div id="commands"></div></section>
      <section><h2>Agent Decisions</h2><div id="decisions"></div></section>
      <section><h2>Errors</h2><div id="errors"></div></section>
      <section><h2>Human Interventions</h2><div id="human"></div></section>
    </div>
    <div class="grid">
      <section><h2>Current Program</h2><pre class="code" id="solution"></pre></section>
      <section><h2>Final Report</h2><div id="report"></div></section>
    </div>
  </main>
  <script id="initial" type="application/json">{data_json}</script>
  <script>
    function renderEntries(id, entries) {{
      const node = document.getElementById(id);
      node.innerHTML = "";
      if (!entries || entries.length === 0) {{
        node.innerHTML = '<div class="empty">No entries yet.</div>';
        return;
      }}
      for (const entry of entries.slice().reverse()) {{
        const pre = document.createElement("pre");
        pre.className = "entry";
        pre.textContent = entry;
        node.appendChild(pre);
      }}
    }}
    function render(data) {{
      const status = document.getElementById("status");
      const name = data.status.status;
      const color = name === "Passing" ? "var(--green)" : name === "Failing" ? "var(--red)" : "var(--amber)";
      status.innerHTML = `<strong style="color:${{color}}">${{name}}</strong><span>${{data.status.detail}}</span>`;
      renderEntries("test_runs", data.logs["test_runs.log"]);
      renderEntries("commands", data.logs["commands.log"]);
      renderEntries("decisions", data.logs["decisions.log"]);
      renderEntries("errors", data.logs["errors.log"]);
      renderEntries("human", data.logs["human_interventions.log"]);
      renderEntries("report", data.logs["final_report.md"]);
      document.getElementById("solution").textContent = data.solution || "<empty>";
    }}
    async function refresh() {{
      try {{
        const response = await fetch("/api/status", {{ cache: "no-store" }});
        render(await response.json());
      }} catch (error) {{
        console.error(error);
      }}
    }}
    render(JSON.parse(document.getElementById("initial").textContent));
    setInterval(refresh, 2000);
  </script>
</body>
</html>
""".encode("utf-8")


class DashboardHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:  # noqa: N802
        if self.path == "/api/status":
            body = json.dumps(dashboard_data()).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        if self.path not in ("/", "/index.html"):
            self.send_error(404)
            return
        body = render_page()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args: object) -> None:
        return


def main() -> int:
    parser = argparse.ArgumentParser(description="Serve the Nightrider local dashboard.")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind.")
    parser.add_argument("--port", type=int, default=8765, help="Port to bind.")
    args = parser.parse_args()

    try:
        server = ThreadingHTTPServer((args.host, args.port), DashboardHandler)
    except OSError as exc:
        if exc.errno in (errno.EADDRINUSE, 48):
            print(
                f"[Nightrider] Port {args.port} is already in use. "
                f"Open http://{args.host}:{args.port} if the dashboard is already running, "
                "or start another copy with --port 8766."
            )
            return 1
        raise
    print(f"[Nightrider] Dashboard running at http://{args.host}:{args.port}")
    print("[Nightrider] Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[Nightrider] Dashboard stopped.")
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
