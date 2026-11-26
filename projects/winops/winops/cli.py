"""CLI entrypoint for WinOps provisioning scripts and workstation asset audits."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from winops.auditor import collect_workstation_audit, export_audit_csv, render_audit_html
from winops.manifest import export_manifest_json, render_provisioning_ps1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="winops",
        description="Windows 11 Baseline Provisioning & Workstation Compliance Auditor",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    audit_cmd = sub.add_parser("audit", help="Run workstation hardware & security audit")
    audit_cmd.add_argument("--no-cim", action="store_true", help="Skip live PowerShell CIM queries")
    audit_cmd.add_argument("--csv", default=None, help="Optional CSV export path")
    audit_cmd.add_argument("--html", default=None, help="Optional HTML export path")

    prov_cmd = sub.add_parser("provision-script", help="Generate PowerShell Winget script")
    prov_cmd.add_argument("--profile", default="developer", choices=["standard", "it_support", "developer"])
    prov_cmd.add_argument("--out", default=None, help="Optional .ps1 output file path")

    man_cmd = sub.add_parser("export-manifest", help="Export Winget package JSON manifest")
    man_cmd.add_argument("--profile", default="developer", choices=["standard", "it_support", "developer"])
    man_cmd.add_argument("--out", default="baseline_manifest.json")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.command == "audit":
        record = collect_workstation_audit(probe_cim=not args.no_cim)
        if args.csv:
            export_audit_csv([record], args.csv)
        if args.html:
            Path(args.html).write_text(render_audit_html(record), encoding="utf-8")
        print(json.dumps(record, indent=2))
        return 0

    if args.command == "provision-script":
        script = render_provisioning_ps1(args.profile)
        if args.out:
            Path(args.out).write_text(script, encoding="utf-8")
            print(f"Wrote PowerShell provisioning script to {args.out}")
        else:
            print(script)
        return 0

    if args.command == "export-manifest":
        export_manifest_json(args.out, profile=args.profile)
        print(f"Exported Winget manifest to {args.out}")
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
