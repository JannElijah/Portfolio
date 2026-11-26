"""Cisco IOS running-configuration parser and security/routing hygiene auditor."""

from __future__ import annotations

import html
import ipaddress
import re


def parse_ios_config(config_text: str) -> dict:
    """Extract hostname, interfaces, VLANs, OSPF networks, and VTY/security posture."""
    hostname = "Unknown"
    interfaces: list[dict] = []
    vlans: list[dict] = []
    ospf_areas: list[dict] = []
    vty_transports: list[str] = []
    has_password_encryption = False
    has_enable_secret = False
    ssh_version = None

    current_section: str | None = None
    current_iface: dict | None = None
    current_vlan: dict | None = None

    for raw_line in config_text.splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()
        if not stripped or stripped == "!":
            if not raw_line.startswith(" "):
                current_section = None
            continue

        if stripped.startswith("hostname "):
            hostname = stripped.split(maxsplit=1)[1]
        elif stripped == "service password-encryption":
            has_password_encryption = True
        elif stripped.startswith("enable secret "):
            has_enable_secret = True
        elif stripped.startswith("ip ssh version "):
            ssh_version = stripped.split()[-1]
        elif stripped.startswith("interface "):
            current_section = "interface"
            current_iface = {
                "name": stripped.split(maxsplit=1)[1],
                "ip": None,
                "mask": None,
                "description": None,
                "shutdown": False,
            }
            interfaces.append(current_iface)
        elif stripped.startswith("vlan ") and stripped[5:].strip().isdigit():
            current_section = "vlan"
            current_vlan = {"id": int(stripped[5:].strip()), "name": None}
            vlans.append(current_vlan)
        elif stripped.startswith("router ospf "):
            current_section = "ospf"
        elif stripped.startswith("line vty "):
            current_section = "vty"
        elif current_section == "interface" and current_iface is not None:
            ip_match = re.match(r"ip address (\d+\.\d+\.\d+\.\d+) (\d+\.\d+\.\d+\.\d+)", stripped)
            if ip_match:
                current_iface["ip"] = ip_match.group(1)
                current_iface["mask"] = ip_match.group(2)
            elif stripped.startswith("description "):
                current_iface["description"] = stripped.split(maxsplit=1)[1]
            elif stripped == "shutdown":
                current_iface["shutdown"] = True
        elif current_section == "vlan" and current_vlan is not None:
            if stripped.startswith("name "):
                current_vlan["name"] = stripped.split(maxsplit=1)[1]
        elif current_section == "ospf":
            net_match = re.match(r"network (\d+\.\d+\.\d+\.\d+) (\d+\.\d+\.\d+\.\d+) area (\S+)", stripped)
            if net_match:
                ospf_areas.append(
                    {
                        "network": net_match.group(1),
                        "wildcard": net_match.group(2),
                        "area": net_match.group(3),
                    }
                )
        elif current_section == "vty":
            if stripped.startswith("transport input "):
                vty_transports.extend(stripped.split()[2:])

    return {
        "hostname": hostname,
        "interfaces": interfaces,
        "vlans": vlans,
        "ospf_networks": ospf_areas,
        "security": {
            "service_password_encryption": has_password_encryption,
            "enable_secret": has_enable_secret,
            "ssh_version": ssh_version,
            "vty_transport_input": sorted(set(vty_transports)),
        },
    }


def audit_parsed_config(parsed: dict) -> dict:
    """Evaluate Cisco IOS security and operational hygiene checks."""
    findings: list[dict] = []
    sec = parsed["security"]

    findings.append(
        {
            "rule": "Encrypted Service Passwords",
            "severity": "PASS" if sec["service_password_encryption"] else "WARN",
            "detail": "service password-encryption enabled" if sec["service_password_encryption"] else "Missing service password-encryption",
        }
    )
    findings.append(
        {
            "rule": "Enable Secret Configured",
            "severity": "PASS" if sec["enable_secret"] else "FAIL",
            "detail": "enable secret present" if sec["enable_secret"] else "Missing privileged EXEC enable secret",
        }
    )

    transports = set(sec["vty_transport_input"])
    telnet_exposed = (not transports) or ("telnet" in transports) or ("all" in transports)
    findings.append(
        {
            "rule": "SSH-Only VTY Management",
            "severity": "FAIL" if telnet_exposed else "PASS",
            "detail": "VTY restricted to SSH" if not telnet_exposed else f"Telnet/unrestricted VTY transport ({sorted(transports) or 'default'})",
        }
    )

    valid_ips = 0
    for iface in parsed["interfaces"]:
        if iface["ip"] and iface["mask"]:
            ipaddress.IPv4Interface(f"{iface['ip']}/{iface['mask']}")
            valid_ips += 1

    fail_count = sum(1 for f in findings if f["severity"] == "FAIL")
    warn_count = sum(1 for f in findings if f["severity"] == "WARN")
    return {
        "hostname": parsed["hostname"],
        "interface_count": len(parsed["interfaces"]),
        "configured_l3_interfaces": valid_ips,
        "ospf_network_count": len(parsed["ospf_networks"]),
        "vlan_count": len(parsed["vlans"]),
        "overall_status": "FAIL" if fail_count else "WARN" if warn_count else "PASS",
        "findings": findings,
    }


def render_netaudit_html(parsed: dict, audit: dict) -> str:
    """Render a standalone dark-themed HTML Cisco IOS security audit report."""
    rows = "".join(
        f"<tr><td>{html.escape(f['rule'])}</td><td>{html.escape(f['severity'])}</td><td>{html.escape(f['detail'])}</td></tr>"
        for f in audit["findings"]
    )
    return (
        "<!doctype html><html lang='en'><head><meta charset='utf-8' /><title>NetAudit Report</title></head>"
        "<body style='font-family:system-ui,sans-serif;background:#09090b;color:#f4f4f5;padding:2rem;'>"
        f"<h1>NetAudit IOS Security Report — {html.escape(audit['hostname'])} ({html.escape(audit['overall_status'])})</h1>"
        f"<p>L3 Interfaces: {audit['configured_l3_interfaces']} | VLANs: {audit['vlan_count']} | OSPF Networks: {audit['ospf_network_count']}</p>"
        f"<table border='1' cellpadding='6' cellspacing='0'><thead><tr><th>Check</th><th>Severity</th><th>Detail</th></tr></thead><tbody>{rows}</tbody></table>"
        "</body></html>"
    )
