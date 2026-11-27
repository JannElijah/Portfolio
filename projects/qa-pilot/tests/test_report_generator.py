"""Unit tests for JUnit XML parsing and HTML QA Sign-Off report generation."""

from __future__ import annotations

from pathlib import Path

from qa_pilot.cli import main as cli_main, parse_junit_to_report_rows
from qa_pilot.runner import ingest_cases_to_qa_telemetry, render_qa_report


def test_junit_to_html_signoff_report(tmp_path: Path) -> None:
    junit_file = tmp_path / "sample.xml"
    junit_file.write_text(
        """<testsuite name="pytest" tests="2" failures="0" time="0.54">
          <testcase classname="tests.test_api_contracts" name="test_list_documents" time="0.042" />
          <testcase classname="tests.test_dms_e2e" name="test_e2e_approve" time="0.498" />
        </testsuite>""",
        encoding="utf-8",
    )
    rows = parse_junit_to_report_rows(junit_file)
    assert len(rows) == 2
    assert rows[0]["layer"] == "API Contract"
    assert rows[1]["layer"] == "Playwright E2E"

    html_out = tmp_path / "report.html"
    rc = cli_main(["report", str(junit_file), "--out", str(html_out), "--title", "DMS E2E"])
    assert rc == 0
    content = html_out.read_text(encoding="utf-8")
    assert "GATE: PASS" in content
    assert "test_e2e_approve" in content
    assert "<svg" in content and "250ms" in content and "filterRows" in content

    run_id = ingest_cases_to_qa_telemetry("dms-e2e", "fw-test-1", rows, tmp_path / "tel.db")
    assert run_id >= 1

    blocked = render_qa_report(
        "Blocked Build",
        [
            {
                "layer": "E2E",
                "name": "test_login",
                "status": "FAILED",
                "duration_ms": 120.0,
                "detail": "Timeout",
                "screenshot_data_uri": "data:image/png;base64,AAAA",
            }
        ],
        tmp_path / "blocked.html",
    )
    blocked_html = blocked.read_text(encoding="utf-8")
    assert "GATE: BLOCKED" in blocked_html
    assert "data:image/png;base64,AAAA" in blocked_html
