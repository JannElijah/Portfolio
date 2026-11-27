"""SQLite storage and HTML triage report exporter for LogPulse scans."""

from __future__ import annotations

import html
import json
import sqlite3
from pathlib import Path


class PulseStore:
    def __init__(self, db_path: str | Path = "logpulse.db") -> None:
        self.db_path = str(db_path)
        self._init_schema()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_schema(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS pulse_scans (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    status TEXT NOT NULL,
                    critical_events INTEGER NOT NULL,
                    error_events INTEGER NOT NULL,
                    stopped_services_count INTEGER NOT NULL,
                    payload_json TEXT NOT NULL,
                    captured_at TEXT NOT NULL
                )
                """
            )

    def save_scan(self, analysis: dict) -> int:
        with self._connect() as conn:
            cur = conn.execute(
                """
                INSERT INTO pulse_scans (
                    status, critical_events, error_events, stopped_services_count, payload_json, captured_at
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    analysis["status"],
                    analysis["critical_events"],
                    analysis["error_events"],
                    len(analysis["stopped_auto_services"]),
                    json.dumps(analysis),
                    analysis["captured_at_utc"],
                ),
            )
            return int(cur.lastrowid)

    def list_scans(self) -> list[dict]:
        with self._connect() as conn:
            rows = conn.execute("SELECT * FROM pulse_scans ORDER BY id DESC").fetchall()
        return [dict(r) for r in rows]


def render_pulse_html(analysis: dict) -> str:
    """Render a dark Windows Ops triage report with SVG event frequency chart and remediation table."""
    status = str(analysis.get("status", "HEALTHY"))
    st_col = "#10b981" if status == "HEALTHY" else "#f59e0b" if status == "WARN" else "#f43f5e"
    stopped = analysis.get("stopped_auto_services") or []
    top_events = analysis.get("top_event_ids") or []

    svc_items = "".join(
        f"<div class='svc-chip'><strong>{html.escape(str(s.get('Name')))}</strong> <span>({html.escape(str(s.get('State')))})</span></div>"
        for s in stopped
    ) or "<div style='color:#34d399;font-size:0.82rem;'>All monitored Auto-start services running normally.</div>"

    event_items = "".join(
        f"<tr><td class='mono'>ID {html.escape(str(item['event_id']))}</td><td class='mono'>{item['count']}</td>"
        f"<td>{html.escape(str(item.get('remediation', 'Review Windows Event Viewer')))}</td></tr>"
        for item in top_events
    ) or "<tr><td colspan='3' style='color:#94a3b8;'>No error events in window.</td></tr>"

    max_cnt = max([int(item["count"]) for item in top_events], default=1)
    bars_svg = []
    for idx, item in enumerate(top_events[:6]):
        y = 10 + idx * 26
        bar_w = max(14, round((int(item["count"]) / max(1, max_cnt)) * 220))
        bars_svg.append(
            f"<text x='6' y='{y + 13}' fill='#cbd5e1' font-size='11' font-family='monospace'>ID {html.escape(str(item['event_id']))}</text>"
            f"<rect x='82' y='{y + 2}' width='{bar_w}' height='14' rx='3' fill='#f59e0b' />"
            f"<text x='{88 + bar_w}' y='{y + 13}' fill='#fde68a' font-size='11' font-family='monospace'>{int(item['count'])}</text>"
        )
    svg_h = max(48, 16 + len(top_events[:6]) * 26)

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <title>LogPulse Triage Report</title>
  <style>
    body {{ margin:0; font-family:Inter,system-ui,sans-serif; background:#090b0f; color:#f4f4f5; padding:26px 34px; }}
    .hdr {{ display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid #1e2433; padding-bottom:12px; margin-bottom:16px; }}
    .badge {{ padding:5px 12px; border-radius:999px; font-family:monospace; font-weight:700; color:{st_col}; border:1px solid {st_col}; }}
    .kpis {{ display:grid; grid-template-columns:repeat(4,1fr); gap:12px; margin-bottom:16px; }}
    .kpi {{ background:#111520; border:1px solid #1e2433; border-radius:8px; padding:12px 14px; }}
    .lbl {{ font-size:0.68rem; color:#94a3b8; text-transform:uppercase; }}
    .val {{ font-size:1.3rem; font-weight:700; font-family:monospace; margin-top:4px; }}
    .card {{ background:#111520; border:1px solid #1e2433; border-radius:10px; padding:15px; margin-bottom:14px; }}
    .svc-chip {{ display:inline-block; background:#231317; border:1px solid #7f1d1d; color:#fda4af; border-radius:6px; padding:5px 10px; margin:3px 6px 3px 0; font-size:0.8rem; }}
    table {{ width:100%; border-collapse:collapse; font-size:0.82rem; }}
    th, td {{ border-bottom:1px solid #1e2433; padding:8px; text-align:left; }}
    .mono {{ font-family:ui-monospace,monospace; }}
  </style>
</head>
<body>
  <div class="hdr">
    <h1 style="margin:0;font-size:1.3rem;">LogPulse Host Triage ({html.escape(status)})</h1>
    <span class="badge">{html.escape(status)}</span>
  </div>
  <div class="kpis">
    <div class="kpi"><div class="lbl">Triage Status</div><div class="val" style="color:{st_col};">{html.escape(status)}</div></div>
    <div class="kpi"><div class="lbl">Critical Events</div><div class="val" style="color:#fb7185;">{analysis['critical_events']}</div></div>
    <div class="kpi"><div class="lbl">Error Events</div><div class="val" style="color:#fbbf24;">{analysis['error_events']}</div></div>
    <div class="kpi"><div class="lbl">Stopped Services</div><div class="val">{len(stopped)}</div></div>
  </div>
  <div class="card">
    <h2 style="margin:0 0 8px;font-size:0.95rem;">Event ID Frequency Chart</h2>
    <svg viewBox="0 0 360 {svg_h}" style="width:100%;max-width:520px;height:{svg_h}px;background:#090b0f;border:1px solid #1e2433;border-radius:6px;">{"".join(bars_svg)}</svg>
  </div>
  <div class="card"><h2 style="margin:0 0 8px;font-size:0.95rem;">Stopped Auto-Start Services</h2>{svc_items}</div>
  <div class="card">
    <h2 style="margin:0 0 8px;font-size:0.95rem;">Recurring Event IDs &amp; Remediation</h2>
    <table><thead><tr><th>Event ID</th><th>Count</th><th>Recommended Remediation</th></tr></thead><tbody>{event_items}</tbody></table>
  </div>
</body>
</html>"""
