"""CLI entrypoint for SiteCare website maintenance auditing and sitemap export."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from sitecare.auditor import audit_static_site, generate_sitemap_xml, inspect_github_workflows_and_git


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="sitecare", description="Website Maintenance & GitHub CI Auditor")
    sub = parser.add_subparsers(dest="command", required=True)

    scan = sub.add_parser("audit", help="Audit static site folder and GitHub workflows")
    scan.add_argument("--site-dir", required=True)
    scan.add_argument("--public-dir", default=None)
    scan.add_argument("--repo-dir", default=".")

    sm = sub.add_parser("sitemap", help="Generate XML sitemap")
    sm.add_argument("--base-url", required=True)
    sm.add_argument("--routes", nargs="+", default=["/"])
    sm.add_argument("--out", default=None)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "audit":
        audit = audit_static_site(args.site_dir, args.public_dir)
        git_ci = inspect_github_workflows_and_git(args.repo_dir)
        print(json.dumps({"audit": audit, "git_ci": git_ci}, indent=2))
        return 0 if audit["broken_assets"] == [] else 1
    if args.command == "sitemap":
        xml_txt = generate_sitemap_xml(args.base_url, args.routes)
        if args.out:
            Path(args.out).write_text(xml_txt, encoding="utf-8")
        else:
            print(xml_txt)
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
