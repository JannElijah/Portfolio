"""Tests for LogPulse event aggregation, stopped-service escalation, and HTML reporting."""

from __future__ import annotations

import json

from logpulse.cli import main
from logpulse.collector import analyze_host_telemetry
from logpulse.storage import PulseStore, render_pulse_html


def test_critical_escalation_on_stopped_auto_service() -> None:
    payload = {
        "events": [{"Id": 7031, "LevelDisplayName": "Error", "ProviderName": "Service Control Manager"}],
        "stopped_auto_services": [{"Name": "Spooler", "State": "Stopped", "StartMode": "Auto"}],
    }
    res = analyze_host_telemetry(payload)
    assert res["status"] == "CRITICAL"
    assert res["top_event_ids"][0]["event_id"] == 7031
    assert "Restart-Service" in res["top_event_ids"][0]["remediation"]


def test_warn_on_recurring_event_id_without_criticals() -> None:
    payload = {
        "events": [
            {"Id": 10016, "LevelDisplayName": "Error"},
            {"Id": 10016, "LevelDisplayName": "Error"},
            {"Id": 10016, "LevelDisplayName": "Error"},
        ],
        "stopped_auto_services": [],
    }
    res = analyze_host_telemetry(payload)
    assert res["status"] == "WARN"
    assert res["top_event_ids"][0]["count"] == 3


def test_storage_and_cli_analyze_json(tmp_path, capsys) -> None:
    sample_json = tmp_path / "events.json"
    sample_json.write_text(
        json.dumps({"events": [{"Id": 41, "LevelDisplayName": "Critical"}], "stopped_auto_services": []}),
        encoding="utf-8",
    )
    db_file = tmp_path / "pulse.db"

    assert main(["--db", str(db_file), "analyze-json", "--file", str(sample_json), "--save"]) == 0
    out = json.loads(capsys.readouterr().out)
    assert out["status"] == "CRITICAL"
    assert out["scan_id"] == 1

    store = PulseStore(db_file)
    assert len(store.list_scans()) == 1
    html_report = render_pulse_html(out)
    assert "LogPulse Host Triage (CRITICAL)" in html_report
    assert "<svg" in html_report and "Event ID Frequency Chart" in html_report
