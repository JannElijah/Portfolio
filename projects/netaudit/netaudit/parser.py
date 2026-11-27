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
    ssh_v2 = str(sec.get("ssh_version") or "") == "2"
    findings.append(
        {
            "rule": "SSHv2 Enforced",
            "severity": "PASS" if ssh_v2 else "WARN",
            "detail": "ip ssh version 2 configured" if ssh_v2 else f"SSH version is {sec.get('ssh_version') or 'unset'}; recommend SSHv2",
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


def generate_ios_remediation_cli(audit: dict) -> list[str]:
    """Generate Cisco IOS hardening commands for non-passing findings in audit."""
    cmds: list[str] = []
    for f in audit.get("findings", []):
        if f.get("severity") == "PASS":
            continue
        rule = f.get("rule", "")
        if rule == "Encrypted Service Passwords":
            cmds.append("service password-encryption")
        elif rule == "Enable Secret Configured":
            cmds.append("enable secret <strong-secret>")
        elif rule == "SSH-Only VTY Management":
            cmds.extend(["line vty 0 4", " transport input ssh"])
        elif rule == "SSHv2 Enforced":
            cmds.append("ip ssh version 2")
    return cmds


def render_netaudit_html(parsed: dict, audit: dict) -> str:
    """Render a standalone dark-themed HTML Cisco IOS security & topology audit report."""
    status = str(audit["overall_status"])
    st_col = "#10b981" if status == "PASS" else "#f59e0b" if status == "WARN" else "#f43f5e"
    rows = "".join(
        f"<tr><td>{html.escape(f['rule'])}</td>"
        f"<td><span class='pill {html.escape(f['severity'].lower())}'>{html.escape(f['severity'])}</span></td>"
        f"<td>{html.escape(f['detail'])}</td></tr>"
        for f in audit["findings"]
    )
    iface_rows = "".join(
        f"<tr><td class='mono'>{html.escape(i['name'])}</td><td class='mono'>{html.escape(str(i.get('ip') or '-'))}</td>"
        f"<td class='mono'>{html.escape(str(i.get('mask') or '-'))}</td><td>{html.escape(str(i.get('description') or ''))}</td></tr>"
        for i in parsed.get("interfaces", [])
    ) or "<tr><td colspan='4'>None</td></tr>"
    rem_cli = "\n".join(generate_ios_remediation_cli(audit)) or "! No hardening remediation commands required."

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <title>NetAudit Report — {html.escape(audit['hostname'])}</title>
  <style>
    body {{ margin:0; font-family:Inter,system-ui,sans-serif; background:#080c14; color:#f4f4f5; padding:26px 34px; }}
    .hdr {{ display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid #1e293b; padding-bottom:12px; margin-bottom:16px; }}
    .kpis {{ display:grid; grid-template-columns:repeat(4,1fr); gap:12px; margin-bottom:16px; }}
    .kpi {{ background:#0f1624; border:1px solid #1e293b; border-radius:8px; padding:12px 14px; }}
    .lbl {{ font-size:0.68rem; color:#94a3b8; text-transform:uppercase; }}
    .val {{ font-size:1.3rem; font-weight:700; font-family:monospace; margin-top:4px; }}
    .card {{ background:#0f1624; border:1px solid #1e293b; border-radius:10px; padding:15px; margin-bottom:14px; }}
    table {{ width:100%; border-collapse:collapse; font-size:0.82rem; }}
    th, td {{ border-bottom:1px solid #1e293b; padding:8px; text-align:left; }}
    .mono {{ font-family:ui-monospace,monospace; }}
    .pill {{ padding:2px 8px; border-radius:999px; font-family:monospace; font-size:0.72rem; font-weight:700; }}
    .pass {{ background:rgba(16,185,129,0.16); color:#34d399; }}
    .warn {{ background:rgba(245,158,11,0.16); color:#fbbf24; }}
    .fail {{ background:rgba(244,63,94,0.16); color:#fb7185; }}
    pre {{ margin:0; padding:10px; background:#06090f; border:1px solid #1e293b; border-radius:6px; font-size:0.78rem; color:#7dd3fc; }}
  </style>
</head>
<body>
  <div class="hdr">
    <h1 style="margin:0;font-size:1.3rem;">NetAudit IOS Security Report — {html.escape(audit['hostname'])} ({html.escape(status)})</h1>
    <span class="pill" style="color:{st_col};border:1px solid {st_col};">{html.escape(status)}</span>
  </div>
  <div class="kpis">
    <div class="kpi"><div class="lbl">Audit Status</div><div class="val" style="color:{st_col};">{html.escape(status)}</div></div>
    <div class="kpi"><div class="lbl">L3 Interfaces</div><div class="val">{audit['configured_l3_interfaces']}</div></div>
    <div class="kpi"><div class="lbl">VLANs</div><div class="val">{audit['vlan_count']}</div></div>
    <div class="kpi"><div class="lbl">OSPF Networks</div><div class="val">{audit['ospf_network_count']}</div></div>
  </div>
  <div class="card"><h2 style="margin:0 0 8px;font-size:0.95rem;">Security Hygiene Findings</h2><table><thead><tr><th>Check</th><th>Severity</th><th>Detail</th></tr></thead><tbody>{rows}</tbody></table></div>
  <div class="card"><h2 style="margin:0 0 8px;font-size:0.95rem;">Parsed Interfaces</h2><table><thead><tr><th>Interface</th><th>IP Address</th><th>Subnet Mask</th><th>Description</th></tr></thead><tbody>{iface_rows}</tbody></table></div>
  <div class="card"><h2 style="margin:0 0 8px;font-size:0.95rem;">Cisco IOS Hardening Remediation CLI</h2><pre>{html.escape(rem_cli)}</pre></div>
</body>
</html>"""
