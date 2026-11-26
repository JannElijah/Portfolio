"""Command-line interface and JSON report exporter for SysTriage."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from systriage.diagnostics import ProbeTarget, run_endpoint_diagnostic, suggest_ticket_priority
from systriage.storage import TriageStore


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="systriage",
        description="Endpoint Health Diagnostics & IT Helpdesk Triage Utility",
    )
    parser.add_argument("--db", default="systriage.db", help="Path to SQLite database file")
    sub = parser.add_subparsers(dest="command", required=True)

    scan_cmd = sub.add_parser("scan", help="Run workstation & network probe")
    scan_cmd.add_argument("--skip-network", action="store_true", help="Skip outbound TCP probes")
    scan_cmd.add_argument("--save", action="store_true", help="Persist snapshot to SQLite")
    scan_cmd.add_argument("--auto-ticket", action="store_true", help="Open triage ticket if WARN/CRITICAL")
    scan_cmd.add_argument("--target", action="append", default=[], help="Extra host:port probe target")

    ticket_cmd = sub.add_parser("ticket", help="Manage IT helpdesk triage tickets")
    ticket_sub = ticket_cmd.add_subparsers(dest="ticket_action", required=True)

    create_t = ticket_sub.add_parser("create", help="Create a new support ticket")
    create_t.add_argument("--title", required=True)
    create_t.add_argument("--category", default="Endpoint")
    create_t.add_argument("--priority", default="P3", choices=["P1", "P2", "P3"])
    create_t.add_argument("--assignee", default="IT Support Tier 1")

    list_t = ticket_sub.add_parser("list", help="List support tickets")
    list_t.add_argument("--status", choices=["OPEN", "IN_PROGRESS", "RESOLVED"])

    resolve_t = ticket_sub.add_parser("resolve", help="Resolve a support ticket")
    resolve_t.add_argument("--id", type=int, required=True)
    resolve_t.add_argument("--notes", required=True)

    export_cmd = sub.add_parser("export", help="Export diagnostic + ticket bundle to JSON")
    export_cmd.add_argument("--out", default="systriage_report.json")
    return parser


def _parse_targets(raw_targets: list[str]) -> list[ProbeTarget] | None:
    if not raw_targets:
        return None
    parsed: list[ProbeTarget] = []
    for raw in raw_targets:
        host, port_str = raw.rsplit(":", 1)
        parsed.append(ProbeTarget(name=host, host=host, port=int(port_str)))
    return parsed


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    store = TriageStore(args.db)

    if args.command == "scan":
        targets = _parse_targets(args.target)
        diag = run_endpoint_diagnostic(targets=targets, include_network=not args.skip_network)
        result: dict = {"diagnostic": diag}

        if args.save or args.auto_ticket:
            snap_id = store.save_snapshot(diag)
            result["snapshot_id"] = snap_id
            if args.auto_ticket and diag["overall_status"] in {"WARN", "CRITICAL"}:
                ticket = store.create_ticket(
                    title=f"Automated alert: {diag['host']['hostname']} status {diag['overall_status']}",
                    category="Diagnostics",
                    priority=suggest_ticket_priority(diag),
                    assignee="IT Operations",
                    snapshot_id=snap_id,
                )
                result["created_ticket"] = ticket

        print(json.dumps(result, indent=2))
        return 0

    if args.command == "ticket":
        if args.ticket_action == "create":
            ticket = store.create_ticket(
                title=args.title,
                category=args.category,
                priority=args.priority,
                assignee=args.assignee,
            )
            print(json.dumps(ticket, indent=2))
        elif args.ticket_action == "list":
            print(json.dumps(store.list_tickets(status=args.status), indent=2))
        elif args.ticket_action == "resolve":
            ticket = store.update_ticket_status(args.id, "RESOLVED", args.notes)
            print(json.dumps(ticket, indent=2))
        return 0

    if args.command == "export":
        payload = {
            "latest_diagnostic": run_endpoint_diagnostic(include_network=False),
            "tickets": store.list_tickets(),
        }
        Path(args.out).write_text(json.dumps(payload, indent=2), encoding="utf-8")
        print(f"Exported SysTriage report to {args.out}")
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
