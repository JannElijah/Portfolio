"""SQLite persistence and lot yield analytics for MCU hardware bench telemetry."""

from __future__ import annotations

import csv
import html
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path


class BenchTelemetryStore:
    """Persists hardware test lots, evaluated UART frames, and fault breakdowns."""

    def __init__(self, db_path: str | Path = "mcu_lab.db") -> None:
        self.db_path = str(db_path)
        self._init_schema()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def _init_schema(self) -> None:
        with self._connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS bench_lots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    lot_code TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS telemetry_frames (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    lot_id INTEGER NOT NULL REFERENCES bench_lots(id) ON DELETE CASCADE,
                    device_id TEXT NOT NULL,
                    firmware TEXT NOT NULL,
                    verdict TEXT NOT NULL CHECK(verdict IN ('PASS', 'FAIL')),
                    vdd_3v3 REAL NOT NULL,
                    vcc_5v REAL NOT NULL,
                    mcu_temp_c REAL NOT NULL,
                    i_draw_ma REAL NOT NULL,
                    faults_json TEXT NOT NULL,
                    recorded_at TEXT NOT NULL
                );
                """
            )

    def create_lot(self, lot_code: str) -> int:
        now = datetime.now(timezone.utc).isoformat()
        with self._connect() as conn:
            cur = conn.execute(
                "INSERT INTO bench_lots (lot_code, created_at) VALUES (?, ?)",
                (lot_code, now),
            )
            return int(cur.lastrowid)

    def record_evaluated_frame(self, lot_id: int, evaluated: dict) -> int:
        metrics = evaluated["metrics"]
        with self._connect() as conn:
            cur = conn.execute(
                """
                INSERT INTO telemetry_frames (
                    lot_id, device_id, firmware, verdict,
                    vdd_3v3, vcc_5v, mcu_temp_c, i_draw_ma, faults_json, recorded_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    lot_id,
                    evaluated["device_id"],
                    evaluated["firmware"],
                    evaluated["verdict"],
                    metrics["VDD_3V3"],
                    metrics["VCC_5V"],
                    metrics["MCU_TEMP_C"],
                    metrics["I_DRAW_MA"],
                    json.dumps(evaluated["faults"]),
                    evaluated["timestamp_utc"],
                ),
            )
            return int(cur.lastrowid)

    def compute_lot_yield(self, lot_id: int) -> dict:
        """Compute pass/fail yield percentage and channel extrema for a hardware lot."""
        with self._connect() as conn:
            lot = conn.execute("SELECT * FROM bench_lots WHERE id = ?", (lot_id,)).fetchone()
            if not lot:
                raise LookupError(f"Bench lot #{lot_id} does not exist.")
            rows = conn.execute(
                "SELECT * FROM telemetry_frames WHERE lot_id = ? ORDER BY id ASC",
                (lot_id,),
            ).fetchall()

        total = len(rows)
        passed = sum(1 for r in rows if r["verdict"] == "PASS")
        failed = total - passed
        yield_pct = round((passed / total) * 100, 2) if total else 0.0

        return {
            "lot_id": lot_id,
            "lot_code": lot["lot_code"],
            "total_units": total,
            "passed_units": passed,
            "failed_units": failed,
            "yield_percent": yield_pct,
            "max_temp_c": max((r["mcu_temp_c"] for r in rows), default=None),
            "min_vdd_3v3": min((r["vdd_3v3"] for r in rows), default=None),
            "failed_devices": [r["device_id"] for r in rows if r["verdict"] == "FAIL"],
        }

    def export_lot_csv(self, lot_id: int, out_path: str | Path) -> Path:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM telemetry_frames WHERE lot_id = ? ORDER BY id ASC",
                (lot_id,),
            ).fetchall()
        target = Path(out_path)
        fieldnames = [
            "id",
            "device_id",
            "firmware",
            "verdict",
            "vdd_3v3",
            "vcc_5v",
            "mcu_temp_c",
            "i_draw_ma",
            "faults_json",
            "recorded_at",
        ]
        with target.open("w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=fieldnames)
            writer.writeheader()
            for r in rows:
                writer.writerow({k: r[k] for k in fieldnames})
        return target

    def compute_fault_pareto(self, lot_id: int) -> dict[str, int]:
        """Count fault occurrences per telemetry channel across all frames in lot_id."""
        counts: dict[str, int] = {"VDD_3V3": 0, "VCC_5V": 0, "MCU_TEMP_C": 0, "I_DRAW_MA": 0}
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT faults_json FROM telemetry_frames WHERE lot_id = ?",
                (lot_id,),
            ).fetchall()
        for row in rows:
            try:
                faults = json.loads(row["faults_json"] or "[]")
            except ValueError:
                continue
            for f in faults:
                ch = str(f.get("channel", ""))
                counts[ch] = counts.get(ch, 0) + 1
        return counts

    def render_lot_html_report(self, lot_id: int) -> str:
        """Render a dark semiconductor lot-yield report with SVG channel fault Pareto chart."""
        summary = self.compute_lot_yield(lot_id)
        pareto = self.compute_fault_pareto(lot_id)
        with self._connect() as conn:
            frames = conn.execute(
                "SELECT device_id, firmware, verdict, vdd_3v3, vcc_5v, mcu_temp_c, i_draw_ma "
                "FROM telemetry_frames WHERE lot_id = ? ORDER BY id ASC",
                (lot_id,),
            ).fetchall()

        max_fault = max(pareto.values(), default=1) or 1
        bars_svg = []
        for idx, (ch, cnt) in enumerate(pareto.items()):
            y = 10 + idx * 24
            w = max(6, round((cnt / max_fault) * 200)) if cnt else 2
            col = "#f43f5e" if cnt > 0 else "#1e293b"
            bars_svg.append(
                f"<text x='6' y='{y + 12}' fill='#cbd5e1' font-size='11' font-family='monospace'>{html.escape(ch)}</text>"
                f"<rect x='104' y='{y + 2}' width='{w}' height='13' rx='3' fill='{col}' />"
                f"<text x='{110 + w}' y='{y + 12}' fill='#fda4af' font-size='11' font-family='monospace'>{cnt}</text>"
            )
        rows_html = "".join(
            f"<tr><td class='mono'>{html.escape(r['device_id'])}</td><td class='mono'>{r['vdd_3v3']}V</td>"
            f"<td class='mono'>{r['vcc_5v']}V</td><td class='mono'>{r['mcu_temp_c']}°C</td>"
            f"<td class='mono'>{r['i_draw_ma']}mA</td>"
            f"<td style='color:{'#34d399' if r['verdict']=='PASS' else '#fb7185'};font-weight:700;'>{r['verdict']}</td></tr>"
            for r in frames
        )
        return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <title>MCU-Lab Lot Report — {html.escape(summary['lot_code'])}</title>
  <style>
    body {{ margin:0; font-family:Inter,system-ui,sans-serif; background:#071012; color:#f4f4f5; padding:26px 34px; }}
    .kpis {{ display:grid; grid-template-columns:repeat(4,1fr); gap:12px; margin:14px 0 16px; }}
    .kpi {{ background:#0d1a1d; border:1px solid #1b343a; border-radius:8px; padding:12px; }}
    .lbl {{ font-size:0.68rem; color:#94a3b8; text-transform:uppercase; }}
    .val {{ font-size:1.3rem; font-weight:700; font-family:monospace; margin-top:4px; }}
    .card {{ background:#0d1a1d; border:1px solid #1b343a; border-radius:10px; padding:15px; margin-bottom:14px; }}
    table {{ width:100%; border-collapse:collapse; font-size:0.82rem; }}
    th, td {{ border-bottom:1px solid #1b343a; padding:7px; text-align:left; }}
    .mono {{ font-family:ui-monospace,monospace; }}
  </style>
</head>
<body>
  <h1 style="margin:0;font-size:1.3rem;">MCU-Lab Semiconductor Bench Report — {html.escape(summary['lot_code'])}</h1>
  <div class="kpis">
    <div class="kpi"><div class="lbl">Lot Yield</div><div class="val" style="color:#10b981;">{summary['yield_percent']}%</div></div>
    <div class="kpi"><div class="lbl">Passed / Failed</div><div class="val">{summary['passed_units']} / {summary['failed_units']}</div></div>
    <div class="kpi"><div class="lbl">Peak Temp</div><div class="val">{summary['max_temp_c']}°C</div></div>
    <div class="kpi"><div class="lbl">Min VDD 3.3V</div><div class="val">{summary['min_vdd_3v3']}V</div></div>
  </div>
  <div class="card">
    <h2 style="margin:0 0 8px;font-size:0.95rem;">Channel Fault Pareto</h2>
    <svg viewBox="0 0 360 112" style="width:100%;max-width:480px;height:112px;background:#071012;border:1px solid #1b343a;border-radius:6px;">{"".join(bars_svg)}</svg>
  </div>
  <div class="card">
    <h2 style="margin:0 0 8px;font-size:0.95rem;">Evaluated Bench Frames</h2>
    <table><thead><tr><th>Device</th><th>VDD 3.3V</th><th>VCC 5V</th><th>Temp</th><th>Current</th><th>Verdict</th></tr></thead><tbody>{rows_html}</tbody></table>
  </div>
</body>
</html>"""
