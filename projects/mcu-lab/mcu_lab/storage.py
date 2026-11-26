"""SQLite persistence and lot yield analytics for MCU hardware bench telemetry."""

from __future__ import annotations

import csv
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
