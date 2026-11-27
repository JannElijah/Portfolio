"""Tests for JUnit XML / JSON ingestion, flaky detection, regressions, and release gates."""

from __future__ import annotations

import json

from qa_telemetry.analytics import (
    compute_run_summary,
    compute_suite_trend,
    detect_flaky_tests,
    detect_regressions,
    evaluate_release_gate,
    render_html_signoff_report,
)
from qa_telemetry.cli import main
from qa_telemetry.ingestor import TelemetryStore

SAMPLE_JUNIT_PASS = """<?xml version="1.0" encoding="utf-8"?>
<testsuite name="api-regression" tests="3" failures="0" skipped="0" time="0.45">
  <testcase classname="tests.test_auth" name="test_token_issue" time="0.10" />
  <testcase classname="tests.test_auth" name="test_token_refresh" time="0.15" />
  <testcase classname="tests.test_orders" name="test_create_order" time="0.20" />
</testsuite>
"""

SAMPLE_JUNIT_FAIL = """<?xml version="1.0" encoding="utf-8"?>
<testsuite name="api-regression" tests="3" failures="1" skipped="0" time="0.50">
  <testcase classname="tests.test_auth" name="test_token_issue" time="0.12" />
  <testcase classname="tests.test_auth" name="test_token_refresh" time="0.18">
    <failure message="AssertionError: 401 != 200">Token expired prematurely</failure>
  </testcase>
  <testcase classname="tests.test_orders" name="test_create_order" time="0.20" />
</testsuite>
"""


def test_junit_ingestion_and_summary_metrics(tmp_path) -> None:
    xml_path = tmp_path / "junit_pass.xml"
    xml_path.write_text(SAMPLE_JUNIT_PASS, encoding="utf-8")

    store = TelemetryStore(tmp_path / "qa.db")
    run_id = store.ingest_junit_xml(xml_path, suite_name="api-regression", build_ref="build-101")

    summary = compute_run_summary(store, run_id)
    assert summary["total_cases"] == 3
    assert summary["passed_cases"] == 3
    assert summary["failed_cases"] == 0
    assert summary["pass_rate_percent"] == 100.0
    assert summary["p50_case_s"] == 0.15


def test_flaky_and_regression_detection_across_runs(tmp_path) -> None:
    xml_pass = tmp_path / "pass.xml"
    xml_fail = tmp_path / "fail.xml"
    xml_pass.write_text(SAMPLE_JUNIT_PASS, encoding="utf-8")
    xml_fail.write_text(SAMPLE_JUNIT_FAIL, encoding="utf-8")

    store = TelemetryStore(tmp_path / "qa.db")
    run1 = store.ingest_junit_xml(xml_pass, suite_name="api-regression", build_ref="b1")
    run2 = store.ingest_junit_xml(xml_fail, suite_name="api-regression", build_ref="b2")

    regressions = detect_regressions(store, run1, run2)
    assert regressions == ["tests.test_auth::test_token_refresh"]

    flaky = detect_flaky_tests(store, suite_name="api-regression")
    assert len(flaky) == 1
    assert flaky[0]["test_id"] == "tests.test_auth::test_token_refresh"
    assert flaky[0]["flake_rate_percent"] == 50.0

    trend = compute_suite_trend(store, suite_name="api-regression")
    assert [p["build_ref"] for p in trend] == ["b1", "b2"]
    assert trend[0]["pass_rate_percent"] == 100.0
    assert trend[1]["pass_rate_percent"] == 66.67

    trend_html = render_html_signoff_report(store, run2)
    assert "Suite Pass-Rate Trend" in trend_html and "Flaky Tests Breakdown" in trend_html


def test_release_gate_and_html_signoff_export(tmp_path) -> None:
    json_log = tmp_path / "bench.json"
    json_log.write_text(
        json.dumps(
            {
                "suite_name": "mcu-gpio-bench",
                "build_ref": "fw-2.1.0",
                "cases": [
                    {"classname": "gpio", "name": "pin_voltage_check", "outcome": "PASSED", "duration_s": 0.08},
                    {"classname": "uart", "name": "baud_sync_check", "outcome": "FAILED", "duration_s": 0.22, "failure_message": "CRC mismatch"},
                ],
            }
        ),
        encoding="utf-8",
    )

    store = TelemetryStore(tmp_path / "bench.db")
    run_id = store.ingest_json_log(json_log)
    gate = evaluate_release_gate(store, run_id, min_pass_rate=95.0, max_failures=0)
    assert gate["verdict"] == "BLOCKED"
    assert len(gate["reasons"]) == 2

    html_out = render_html_signoff_report(store, run_id)
    assert "BLOCKED" in html_out
    assert "pin_voltage_check" in html_out


def test_cli_gate_check_exit_codes(tmp_path, capsys) -> None:
    xml_pass = tmp_path / "pass.xml"
    xml_pass.write_text(SAMPLE_JUNIT_PASS, encoding="utf-8")
    db_path = tmp_path / "cli_qa.db"
    html_file = tmp_path / "signoff.html"

    assert main(["--db", str(db_path), "ingest-junit", "--xml", str(xml_pass), "--suite", "ci"]) == 0
    run_id = json.loads(capsys.readouterr().out)["run_id"]

    assert main(["--db", str(db_path), "gate-check", "--run-id", str(run_id)]) == 0
    gate_out = json.loads(capsys.readouterr().out)
    assert gate_out["verdict"] == "PASS"

    assert main(["--db", str(db_path), "export-html", "--run-id", str(run_id), "--out", str(html_file)]) == 0
    assert html_file.exists()
