"""HTTP Web Server integrating projects/mcu-lab and projects/qa-telemetry engines."""

from __future__ import annotations

import csv
import io
import json
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse

PROJECTS_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECTS_ROOT / "mcu-lab"))
sys.path.insert(0, str(PROJECTS_ROOT / "qa-telemetry"))

from mcu_lab.storage import BenchTelemetryStore  # noqa: E402
from mcu_lab.telemetry import (  # noqa: E402
    evaluate_frame_against_specs,
    generate_mock_uart_frames,
    parse_uart_frame,
)
from qa_telemetry.analytics import evaluate_release_gate  # noqa: E402
from qa_telemetry.ingestor import TelemetryStore  # noqa: E402

STATIC_HTML = Path(__file__).parent / "static" / "index.html"


def seed_initial_bench_data(mcu_store: BenchTelemetryStore, qa_store: TelemetryStore) -> None:
    """Ensure initial sample lot and QA run exist on first launch for immediate inspection."""
    with mcu_store._connect() as conn:
        lot_count = conn.execute("SELECT COUNT(*) FROM bench_lots").fetchone()[0]
    if lot_count == 0:
        lot_id = mcu_store.create_lot("LOT-2026-WAFER-A")
        for raw in generate_mock_uart_frames(count=12, fault_probability=0.18, seed=42):
            mcu_store.record_evaluated_frame(lot_id, evaluate_frame_against_specs(parse_uart_frame(raw)))

    if not qa_store.list_runs():
        qa_store.record_run(
            "wafer-validation-ci",
            "fw-2.1.0",
            [
                {"classname": "gpio", "name": "test_vdd_tolerance", "outcome": "PASSED", "duration_s": 0.09},
                {"classname": "uart", "name": "test_baud_sync", "outcome": "PASSED", "duration_s": 0.14},
                {"classname": "thermal", "name": "test_burn_in_ceiling", "outcome": "PASSED", "duration_s": 0.21},
            ],
        )


def create_server(
    host: str = "127.0.0.1",
    port: int = 8620,
    mcu_db: str = "waferbench_mcu.db",
    qa_db: str = "waferbench_qa.db",
) -> ThreadingHTTPServer:
    mcu_store = BenchTelemetryStore(mcu_db)
    qa_store = TelemetryStore(qa_db)
    seed_initial_bench_data(mcu_store, qa_store)

    class WaferHandler(BaseHTTPRequestHandler):
        def log_message(self, format: str, *args: Any) -> None:
            return

        def _send_json(self, status: int, body: dict) -> None:
            encoded = json.dumps(body).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(encoded)))
            self.end_headers()
            self.wfile.write(encoded)

        def do_GET(self) -> None:
            parsed = urlparse(self.path)
            if parsed.path == "/" or parsed.path == "/index.html":
                html_bytes = STATIC_HTML.read_bytes()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(html_bytes)))
                self.end_headers()
                self.wfile.write(html_bytes)
                return

            if parsed.path == "/api/overview":
                qs = parse_qs(parsed.query)
                requested_lot = qs.get("lot_id", [None])[0]
                with mcu_store._connect() as conn:
                    lots = [dict(r) for r in conn.execute("SELECT id, lot_code, created_at FROM bench_lots ORDER BY id DESC").fetchall()]
                    target_id = int(requested_lot) if requested_lot and requested_lot.isdigit() else (lots[0]["id"] if lots else None)
                    frames = (
                        conn.execute(
                            "SELECT device_id, verdict, vdd_3v3, vcc_5v, mcu_temp_c, i_draw_ma FROM telemetry_frames WHERE lot_id = ? ORDER BY id DESC LIMIT 12",
                            (target_id,),
                        ).fetchall()
                        if target_id
                        else []
                    )
                lot_summary = mcu_store.compute_lot_yield(target_id) if target_id else {}
                runs = qa_store.list_runs()
                latest_gate = evaluate_release_gate(qa_store, runs[0]["id"]) if runs else {}
                self._send_json(
                    200,
                    {
                        "lots": lots,
                        "lot_summary": lot_summary,
                        "recent_frames": [dict(f) for f in frames],
                        "qa_gate": latest_gate,
                    },
                )
                return

            if parsed.path == "/api/mcu/export.csv":
                qs = parse_qs(parsed.query)
                requested_lot = qs.get("lot_id", [None])[0]
                with mcu_store._connect() as conn:
                    latest = conn.execute("SELECT id FROM bench_lots ORDER BY id DESC LIMIT 1").fetchone()
                    target_id = int(requested_lot) if requested_lot and requested_lot.isdigit() else (latest["id"] if latest else None)
                    rows = (
                        conn.execute(
                            "SELECT device_id, vdd_3v3, vcc_5v, mcu_temp_c, i_draw_ma, verdict FROM telemetry_frames WHERE lot_id = ? ORDER BY id ASC",
                            (target_id,),
                        ).fetchall()
                        if target_id
                        else []
                    )
                buf = io.StringIO()
                writer = csv.writer(buf)
                writer.writerow(["device_id", "vdd_3v3", "vcc_5v", "mcu_temp_c", "i_draw_ma", "verdict"])
                for r in rows:
                    writer.writerow([r["device_id"], r["vdd_3v3"], r["vcc_5v"], r["mcu_temp_c"], r["i_draw_ma"], r["verdict"]])
                csv_bytes = buf.getvalue().encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "text/csv; charset=utf-8")
                self.send_header("Content-Disposition", "attachment; filename=waferbench_lot.csv")
                self.send_header("Content-Length", str(len(csv_bytes)))
                self.end_headers()
                self.wfile.write(csv_bytes)
                return

            self._send_json(404, {"error": "Not found"})

        def do_POST(self) -> None:
            if self.path == "/api/mcu/simulate":
                length = int(self.headers.get("Content-Length", "0"))
                body = json.loads(self.rfile.read(length).decode("utf-8")) if length > 0 else {}
                lot_code = body.get("lot_code", "LOT-LIVE-SIM")
                fault_prob = max(0.0, min(0.8, float(body.get("fault_probability", 0.2))))
                lot_id = mcu_store.create_lot(lot_code)
                for raw in generate_mock_uart_frames(count=10, fault_probability=fault_prob, seed=None):
                    mcu_store.record_evaluated_frame(lot_id, evaluate_frame_against_specs(parse_uart_frame(raw)))
                self._send_json(201, {"lot_id": lot_id, "lot_summary": mcu_store.compute_lot_yield(lot_id)})
                return

            self._send_json(404, {"error": "Not found"})

    return ThreadingHTTPServer((host, port), WaferHandler)


if __name__ == "__main__":
    srv = create_server()
    print("WaferBench running on http://127.0.0.1:8620")
    srv.serve_forever()
