"""CLI for LogPulse Windows Event Log & Service Monitor."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from logpulse.collector import analyze_host_telemetry, run_logpulse_scan
from logpulse.storage import PulseStore, render_pulse_html


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="logpulse", description="Windows Event Log & Service Health Monitor")
    parser.add_argument("--db", default="logpulse.db")
    sub = parser.add_subparsers(dest="command", required=True)

    scan = sub.add_parser("scan", help="Inspect live Windows events & services")
    scan.add_argument("--offline", action="store_true")
    scan.add_argument("--save", action="store_true")
    scan.add_argument("--html", default=None)

    ingest = sub.add_parser("analyze-json", help="Analyze an exported Windows telemetry JSON payload")
    ingest.add_argument("--file", required=True)
    ingest.add_argument("--save", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    store = PulseStore(args.db)

    if args.command == "scan":
        res = run_logpulse_scan(live_windows=not args.offline)
        if args.save:
            res["scan_id"] = store.save_scan(res)
        if args.html:
            Path(args.html).write_text(render_pulse_html(res), encoding="utf-8")
        print(json.dumps(res, indent=2))
        return 0

    if args.command == "analyze-json":
        raw = json.loads(Path(args.file).read_text(encoding="utf-8"))
        res = analyze_host_telemetry(raw)
        if args.save:
            res["scan_id"] = store.save_scan(res)
        print(json.dumps(res, indent=2))
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
