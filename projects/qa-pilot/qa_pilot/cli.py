"""CLI entrypoint for QA-Pilot to execute E2E + Contract checks and build HTML/JUnit reports."""

from __future__ import annotations

import argparse
import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

from qa_pilot.runner import render_qa_report


def parse_junit_to_report_rows(junit_xml_path: str | Path) -> list[dict]:
    """Convert pytest JUnit XML results into rows suitable for render_qa_report."""
    tree = ET.parse(junit_xml_path)
    root = tree.getroot()
    rows: list[dict] = []
    for tc in root.iter("testcase"):
        classname = tc.attrib.get("classname", "qa_pilot")
        name = tc.attrib.get("name", "unnamed")
        duration_ms = float(tc.attrib.get("time", "0")) * 1000.0
        failure = tc.find("failure")
        layer = "API Contract" if "contract" in classname.lower() else "Playwright E2E"
        rows.append(
            {
                "layer": layer,
                "name": name,
                "status": "FAILED" if failure is not None else "PASSED",
                "duration_ms": round(duration_ms, 1),
                "detail": failure.attrib.get("message", "Failure") if failure is not None else "All assertions passed",
            }
        )
    return rows


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="qa-pilot", description="QA-Pilot Report & JUnit Converter")
    sub = parser.add_subparsers(dest="command", required=True)

    rep = sub.add_parser("report", help="Render an HTML sign-off report from a JUnit XML file")
    rep.add_argument("junit_xml", help="Path to pytest --junitxml output")
    rep.add_argument("--title", default="UPHSD-DMS Release Verification", help="Report header title")
    rep.add_argument("--out", default="qa_report.html", help="Destination HTML path")

    args = parser.parse_args(argv)
    if args.command == "report":
        rows = parse_junit_to_report_rows(args.junit_xml)
        out_file = render_qa_report(args.title, rows, args.out)
        print(json.dumps({"report": str(out_file), "cases": len(rows)}))
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
