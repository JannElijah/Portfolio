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
    svc_items = "".join(
        f"<li>{html.escape(str(s.get('Name')))} ({html.escape(str(s.get('State')))})</li>"
        for s in analysis["stopped_auto_services"]
    ) or "<li>All Auto-start services running.</li>"
    event_items = "".join(
        f"<tr><td>{html.escape(str(item['event_id']))}</td><td>{item['count']}</td>"
        f"<td>{html.escape(str(item.get('remediation', 'Review Windows Event Viewer')))}</td></tr>"
        for item in analysis["top_event_ids"]
    )
    return f"""<!doctype html>
<html lang="en">
<head><meta charset="utf-8" /><title>LogPulse Triage Report</title></head>
<body style="font-family:system-ui,sans-serif;background:#09090b;color:#f4f4f5;padding:2rem;">
  <h1>LogPulse Host Triage ({html.escape(analysis['status'])})</h1>
  <p>Critical Events: {analysis['critical_events']} | Error Events: {analysis['error_events']}</p>
  <h2>Stopped Auto-Start Services</h2><ul>{svc_items}</ul>
  <h2>Recurring Event IDs &amp; Remediation</h2>
  <table border="1" cellpadding="6" cellspacing="0"><thead><tr><th>Event ID</th><th>Count</th><th>Recommended Remediation</th></tr></thead><tbody>{event_items}</tbody></table>
</body>
</html>"""
