"""Command-line interface for QA Telemetry ingestion and release gate evaluation."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from qa_telemetry.analytics import (
    compute_run_summary,
    detect_flaky_tests,
    detect_regressions,
    evaluate_release_gate,
    render_html_signoff_report,
)
from qa_telemetry.ingestor import TelemetryStore


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="qa-telemetry",
        description="Automated Test Verification, Flaky Detection & QA Release Gate Engine",
    )
    parser.add_argument("--db", default="qa_telemetry.db", help="Path to SQLite database")
    sub = parser.add_subparsers(dest="command", required=True)

    junit_cmd = sub.add_parser("ingest-junit", help="Ingest a JUnit XML report")
    junit_cmd.add_argument("--xml", required=True)
    junit_cmd.add_argument("--suite", default="pytest-suite")
    junit_cmd.add_argument("--build", default="local")

    json_cmd = sub.add_parser("ingest-json", help="Ingest a structured JSON bench log")
    json_cmd.add_argument("--file", required=True)

    sum_cmd = sub.add_parser("summary", help="Print run summary metrics")
    sum_cmd.add_argument("--run-id", type=int, required=True)

    flaky_cmd = sub.add_parser("flaky", help="Detect flaky tests across recorded runs")
    flaky_cmd.add_argument("--suite", default=None)

    reg_cmd = sub.add_parser("regressions", help="Compare baseline and candidate runs")
    reg_cmd.add_argument("--baseline", type=int, required=True)
    reg_cmd.add_argument("--candidate", type=int, required=True)

    gate_cmd = sub.add_parser("gate-check", help="Evaluate release gate criteria")
    gate_cmd.add_argument("--run-id", type=int, required=True)
    gate_cmd.add_argument("--min-pass-rate", type=float, default=95.0)
    gate_cmd.add_argument("--max-failures", type=int, default=0)

    html_cmd = sub.add_parser("export-html", help="Export standalone HTML QA sign-off report")
    html_cmd.add_argument("--run-id", type=int, required=True)
    html_cmd.add_argument("--out", default="qa_signoff_report.html")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    store = TelemetryStore(args.db)

    if args.command == "ingest-junit":
        run_id = store.ingest_junit_xml(args.xml, suite_name=args.suite, build_ref=args.build)
        print(json.dumps({"run_id": run_id}, indent=2))
        return 0

    if args.command == "ingest-json":
        run_id = store.ingest_json_log(args.file)
        print(json.dumps({"run_id": run_id}, indent=2))
        return 0

    if args.command == "summary":
        print(json.dumps(compute_run_summary(store, args.run_id), indent=2))
        return 0

    if args.command == "flaky":
        print(json.dumps(detect_flaky_tests(store, suite_name=args.suite), indent=2))
        return 0

    if args.command == "regressions":
        print(json.dumps(detect_regressions(store, args.baseline, args.candidate), indent=2))
        return 0

    if args.command == "gate-check":
        result = evaluate_release_gate(
            store,
            args.run_id,
            min_pass_rate=args.min_pass_rate,
            max_failures=args.max_failures,
        )
        print(json.dumps(result, indent=2))
        return 0 if result["verdict"] == "PASS" else 2

    if args.command == "export-html":
        report = render_html_signoff_report(store, args.run_id)
        Path(args.out).write_text(report, encoding="utf-8")
        print(f"Exported QA sign-off report to {args.out}")
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
