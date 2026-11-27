"""Tests for MCU-Lab UART parsing, electrical/thermal threshold checks, and yield storage."""

from __future__ import annotations

import csv
import json

import pytest

from mcu_lab.cli import main
from mcu_lab.storage import BenchTelemetryStore
from mcu_lab.telemetry import (
    evaluate_frame_against_specs,
    generate_mock_uart_frames,
    parse_uart_frame,
)


def test_parse_valid_and_invalid_uart_frames() -> None:
    parsed = parse_uart_frame(
        "DEV=PIC32-001,FW=2.1.0,VDD_3V3=3.31,VCC_5V=5.01,MCU_TEMP_C=42.0,I_DRAW_MA=35.5"
    )
    assert parsed["device_id"] == "PIC32-001"
    assert parsed["metrics"]["VDD_3V3"] == 3.31

    with pytest.raises(ValueError):
        parse_uart_frame("DEV=PIC32-001,VDD_3V3=3.30")


def test_threshold_validation_flags_out_of_spec_channels() -> None:
    nominal = parse_uart_frame(
        "DEV=MCU-10,VDD_3V3=3.30,VCC_5V=5.00,MCU_TEMP_C=45.0,I_DRAW_MA=40.0"
    )
    assert evaluate_frame_against_specs(nominal)["verdict"] == "PASS"

    faulty = parse_uart_frame(
        "DEV=MCU-11,VDD_3V3=2.92,VCC_5V=5.00,MCU_TEMP_C=91.4,I_DRAW_MA=145.0"
    )
    evaluated = evaluate_frame_against_specs(faulty)
    assert evaluated["verdict"] == "FAIL"
    fault_channels = {f["channel"] for f in evaluated["faults"]}
    assert fault_channels == {"VDD_3V3", "MCU_TEMP_C", "I_DRAW_MA"}


def test_bench_lot_yield_and_csv_export(tmp_path) -> None:
    store = BenchTelemetryStore(tmp_path / "bench.db")
    lot_id = store.create_lot("LOT-TEST-01")
    frames = generate_mock_uart_frames(count=8, fault_probability=0.25, seed=7)
    for raw in frames:
        store.record_evaluated_frame(lot_id, evaluate_frame_against_specs(parse_uart_frame(raw)))

    summary = store.compute_lot_yield(lot_id)
    assert summary["total_units"] == 8
    assert summary["passed_units"] + summary["failed_units"] == 8
    assert 0.0 <= summary["yield_percent"] <= 100.0

    csv_file = store.export_lot_csv(lot_id, tmp_path / "lot.csv")
    with csv_file.open("r", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    assert len(rows) == 8

    pareto = store.compute_fault_pareto(lot_id)
    assert set(["VDD_3V3", "VCC_5V", "MCU_TEMP_C", "I_DRAW_MA"]).issubset(pareto.keys())
    lot_html = store.render_lot_html_report(lot_id)
    assert "MCU-Lab Semiconductor Bench Report — LOT-TEST-01" in lot_html
    assert "<svg" in lot_html and "Channel Fault Pareto" in lot_html


def test_cli_simulate_and_export(tmp_path, capsys) -> None:
    db_file = tmp_path / "cli_mcu.db"
    csv_out = tmp_path / "cli_lot.csv"

    assert main(["--db", str(db_file), "simulate", "--lot", "LOT-A", "--count", "5", "--seed", "1"]) == 0
    summary = json.loads(capsys.readouterr().out)
    assert summary["lot_code"] == "LOT-A"
    assert summary["total_units"] == 5

    assert main(["--db", str(db_file), "export-csv", "--lot-id", str(summary["lot_id"]), "--out", str(csv_out)]) == 0
    assert csv_out.exists()
