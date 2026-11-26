"""Command-line interface for MCU-Lab bench simulation, frame ingestion, and yield reporting."""

from __future__ import annotations

import argparse
import json

from mcu_lab.storage import BenchTelemetryStore
from mcu_lab.telemetry import (
    evaluate_frame_against_specs,
    generate_mock_uart_frames,
    parse_uart_frame,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="mcu-lab",
        description="Microcontroller Hardware Telemetry & Pass/Fail Bench Logger",
    )
    parser.add_argument("--db", default="mcu_lab.db", help="Path to SQLite bench database")
    sub = parser.add_subparsers(dest="command", required=True)

    sim_cmd = sub.add_parser("simulate", help="Run a simulated UART lot and evaluate yield")
    sim_cmd.add_argument("--lot", default="LOT-2026-A")
    sim_cmd.add_argument("--count", type=int, default=12)
    sim_cmd.add_argument("--fault-prob", type=float, default=0.15)
    sim_cmd.add_argument("--seed", type=int, default=42)

    ing_cmd = sub.add_parser("ingest-frame", help="Evaluate and log a single UART frame")
    ing_cmd.add_argument("--lot-id", type=int, required=True)
    ing_cmd.add_argument("--frame", required=True)

    yield_cmd = sub.add_parser("yield-report", help="Print lot yield summary")
    yield_cmd.add_argument("--lot-id", type=int, required=True)

    csv_cmd = sub.add_parser("export-csv", help="Export lot telemetry frames to CSV")
    csv_cmd.add_argument("--lot-id", type=int, required=True)
    csv_cmd.add_argument("--out", default="mcu_lot_telemetry.csv")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    store = BenchTelemetryStore(args.db)

    if args.command == "simulate":
        lot_id = store.create_lot(args.lot)
        frames = generate_mock_uart_frames(
            count=args.count,
            fault_probability=args.fault_prob,
            seed=args.seed,
        )
        for raw in frames:
            evaluated = evaluate_frame_against_specs(parse_uart_frame(raw))
            store.record_evaluated_frame(lot_id, evaluated)
        print(json.dumps(store.compute_lot_yield(lot_id), indent=2))
        return 0

    if args.command == "ingest-frame":
        evaluated = evaluate_frame_against_specs(parse_uart_frame(args.frame))
        frame_id = store.record_evaluated_frame(args.lot_id, evaluated)
        print(json.dumps({"frame_id": frame_id, **evaluated}, indent=2))
        return 0

    if args.command == "yield-report":
        print(json.dumps(store.compute_lot_yield(args.lot_id), indent=2))
        return 0

    if args.command == "export-csv":
        store.export_lot_csv(args.lot_id, args.out)
        print(f"Exported lot #{args.lot_id} telemetry to {args.out}")
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
