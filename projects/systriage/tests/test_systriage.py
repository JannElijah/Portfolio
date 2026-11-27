"""Unit and integration tests for SysTriage diagnostics and ticket persistence."""

from __future__ import annotations

import json
import socket
import threading

import pytest

from systriage.cli import main
from systriage.diagnostics import (
    ProbeTarget,
    classify_usage_severity,
    probe_tcp_endpoint,
    run_endpoint_diagnostic,
    suggest_ticket_priority,
)
from systriage.storage import TriageStore


def test_severity_classification_thresholds() -> None:
    assert classify_usage_severity(45.0) == "HEALTHY"
    assert classify_usage_severity(80.0) == "WARN"
    assert classify_usage_severity(92.0) == "CRITICAL"


def test_tcp_probe_against_ephemeral_local_server() -> None:
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("127.0.0.1", 0))
    server.listen(1)
    port = server.getsockname()[1]

    def accept_once() -> None:
        conn, _ = server.accept()
        conn.close()

    thread = threading.Thread(target=accept_once, daemon=True)
    thread.start()
    try:
        result = probe_tcp_endpoint(ProbeTarget(name="Local Echo", host="127.0.0.1", port=port))
        assert result["reachable"] is True
        assert result["resolved_ip"] == "127.0.0.1"
        assert isinstance(result["latency_ms"], float)
    finally:
        server.close()


def test_ticket_lifecycle_and_snapshot_foreign_key(tmp_path) -> None:
    db_file = tmp_path / "triage.db"
    store = TriageStore(db_file)
    diag = run_endpoint_diagnostic(include_network=False)
    snap_id = store.save_snapshot(diag)

    ticket = store.create_ticket(
        title="High disk warning on workstation",
        category="Storage",
        priority=suggest_ticket_priority({"overall_status": "WARN"}),
        assignee="Jann Limpiado",
        snapshot_id=snap_id,
    )
    assert ticket["priority"] == "P2"
    assert ticket["status"] == "OPEN"
    assert ticket["snapshot_id"] == snap_id

    resolved = store.update_ticket_status(ticket["id"], "RESOLVED", "Cleared temp build artifacts")
    assert resolved["status"] == "RESOLVED"
    assert resolved["resolution_notes"] == "Cleared temp build artifacts"
    assert len(store.list_tickets(status="RESOLVED")) == 1


def test_invalid_ticket_inputs_raise_errors(tmp_path) -> None:
    store = TriageStore(tmp_path / "invalid.db")
    with pytest.raises(ValueError):
        store.create_ticket(title="   ")
    with pytest.raises(ValueError):
        store.create_ticket(title="Bad priority", priority="P9")
    with pytest.raises(LookupError):
        store.update_ticket_status(999, "RESOLVED")


def test_cli_scan_and_export(tmp_path, capsys) -> None:
    db_file = tmp_path / "cli.db"
    out_file = tmp_path / "report.json"

    exit_code = main(["--db", str(db_file), "scan", "--skip-network", "--save"])
    assert exit_code == 0
    captured = json.loads(capsys.readouterr().out)
    assert "snapshot_id" in captured
    assert captured["diagnostic"]["disk"]["total_gb"] > 0

    html_file = tmp_path / "report.html"
    assert main(["--db", str(db_file), "export", "--out", str(out_file), "--html", str(html_file)]) == 0
    exported = json.loads(out_file.read_text(encoding="utf-8"))
    assert "latest_diagnostic" in exported
    assert "tickets" in exported
    html_text = html_file.read_text(encoding="utf-8")
    assert "SysTriage Diagnostics" in html_text and "P1–P3 Helpdesk Triage Ledger" in html_text
