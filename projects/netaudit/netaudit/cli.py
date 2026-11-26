"""Command-line interface for NetAudit Cisco IOS audits and VLSM subnet planning."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from netaudit.parser import audit_parsed_config, parse_ios_config, render_netaudit_html
from netaudit.subnetting import allocate_vlsm_subnets, describe_cidr


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="netaudit", description="Cisco IOS Config Auditor & IPv4 Planner")
    sub = parser.add_subparsers(dest="command", required=True)

    audit_cmd = sub.add_parser("audit-config", help="Audit a Cisco IOS running-config file")
    audit_cmd.add_argument("--file", required=True)
    audit_cmd.add_argument("--html", default=None)

    cidr_cmd = sub.add_parser("describe", help="Describe an IPv4 CIDR block with OSPF wildcard mask")
    cidr_cmd.add_argument("--cidr", required=True)

    vlsm_cmd = sub.add_parser("vlsm", help="Allocate VLSM subnets from a parent block")
    vlsm_cmd.add_argument("--parent", required=True)
    vlsm_cmd.add_argument("--req", action="append", required=True, help="Segment:Hosts (e.g. Voice:60)")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.command == "audit-config":
        raw = Path(args.file).read_text(encoding="utf-8")
        parsed = parse_ios_config(raw)
        audit = audit_parsed_config(parsed)
        if getattr(args, "html", None):
            Path(args.html).write_text(render_netaudit_html(parsed, audit), encoding="utf-8")
        print(json.dumps({"parsed": parsed, "audit": audit}, indent=2))
        return 0

    if args.command == "describe":
        print(json.dumps(describe_cidr(args.cidr), indent=2))
        return 0

    if args.command == "vlsm":
        reqs = []
        for item in args.req:
            name, count = item.split(":", 1)
            reqs.append({"name": name, "hosts": int(count)})
        print(json.dumps(allocate_vlsm_subnets(args.parent, reqs), indent=2))
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
