"""CLI entrypoint for MailPilot AI MIME parsing, triage, and IMAP/SMTP config audit."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from mailpilot.classifier import classify_and_draft
from mailpilot.config import parse_raw_email, validate_email_client_profile


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="mailpilot", description="AI Email Triage & SMTP/IMAP Validator")
    sub = parser.add_subparsers(dest="command", required=True)

    triage = sub.add_parser("triage-eml", help="Classify and draft reply for a raw .eml file")
    triage.add_argument("--file", required=True)

    check = sub.add_parser("check-client", help="Validate IMAPS/STARTTLS configuration")
    check.add_argument("--email", required=True)
    check.add_argument("--imap-host", required=True)
    check.add_argument("--smtp-host", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "triage-eml":
        parsed = parse_raw_email(Path(args.file).read_text(encoding="utf-8"))
        res = classify_and_draft(parsed["subject"], parsed["body"], parsed["sender"])
        print(json.dumps({"email": parsed, "triage": res}, indent=2))
        return 0
    if args.command == "check-client":
        res = validate_email_client_profile(args.email, args.imap_host, 993, args.smtp_host, 587, True)
        print(json.dumps(res, indent=2))
        return 0 if res["valid"] else 1
    return 1


if __name__ == "__main__":
    sys.exit(main())
