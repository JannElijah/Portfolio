"""Nginx configuration parser and security posture auditor for EdgeOps."""

from __future__ import annotations

import re
from pathlib import Path


def parse_nginx_conf(conf_text: str) -> dict:
    """Parse upstream servers, rate-limit zones, security headers, and location routes."""
    upstreams: list[str] = []
    locations: list[str] = []
    headers: dict[str, str] = {}
    rate_limit_zones: list[str] = []

    for raw in conf_text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("server ") and "listen" not in line and not line.endswith("{"):
            target = line.removeprefix("server ").rstrip(";").strip()
            upstreams.append(target)
        elif line.startswith("location "):
            loc = line.removeprefix("location ").rstrip("{").strip()
            locations.append(loc)
        elif line.startswith("add_header "):
            m = re.match(r'add_header\s+([^\s]+)\s+"?([^";]+)"?', line)
            if m:
                headers[m.group(1)] = m.group(2).strip()
        elif line.startswith("limit_req_zone "):
            rate_limit_zones.append(line.rstrip(";"))

    required_headers = ["X-Frame-Options", "X-Content-Type-Options", "Referrer-Policy"]
    checks = [
        {"check": f"Security Header: {h}", "passed": h in headers, "detail": headers.get(h, "Missing")}
        for h in required_headers
    ]
    checks.append(
        {
            "check": "Nginx Rate-Limit Zone Configured",
            "passed": len(rate_limit_zones) > 0,
            "detail": rate_limit_zones[0] if rate_limit_zones else "None",
        }
    )
    checks.append(
        {
            "check": "Health Check Route (/healthz) Exposed",
            "passed": "/healthz" in locations,
            "detail": "/healthz present" if "/healthz" in locations else "Missing",
        }
    )

    return {
        "upstreams": upstreams,
        "locations": locations,
        "security_headers": headers,
        "rate_limit_zones": rate_limit_zones,
        "audit_checks": checks,
        "compliant": all(c["passed"] for c in checks),
    }


def load_nginx_audit(conf_path: str | Path) -> dict:
    """Read an Nginx config file from disk and run parse_nginx_conf."""
    text = Path(conf_path).read_text(encoding="utf-8")
    return parse_nginx_conf(text)
