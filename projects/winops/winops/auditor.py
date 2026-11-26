"""Workstation hardware serial inventory, OS compliance, and HTML/CSV audit reporting."""

from __future__ import annotations

import csv
import html
import json
import os
import platform
import shutil
import socket
import subprocess
from datetime import datetime, timezone
from pathlib import Path


def _query_windows_cim_inventory() -> dict | None:
    """Retrieve hardware serial number, BIOS model, OS build, and Defender status via CIM."""
    if platform.system().lower() != "windows":
        return None
    ps_script = (
        "$cs = Get-CimInstance Win32_ComputerSystem; "
        "$bios = Get-CimInstance Win32_BIOS; "
        "$os = Get-CimInstance Win32_OperatingSystem; "
        "$fw = @(Get-NetFirewallProfile | Select-Object Name, Enabled); "
        "$obj = [ordered]@{"
        "manufacturer=$cs.Manufacturer; model=$cs.Model; "
        "serial_number=$bios.SerialNumber; os_caption=$os.Caption; "
        "os_build=$os.BuildNumber; total_ram_gb=[math]::Round($cs.TotalPhysicalMemory / 1GB, 2); "
        "firewall_profiles=$fw"
        "}; "
        "$obj | ConvertTo-Json -Compress"
    )
    try:
        proc = subprocess.run(
            ["powershell", "-NoProfile", "-Command", ps_script],
            capture_output=True,
            text=True,
            timeout=6,
            check=True,
        )
        return json.loads(proc.stdout.strip())
    except (OSError, ValueError, subprocess.SubprocessError):
        return None


def evaluate_compliance_checks(audit_record: dict) -> list[dict]:
    """Evaluate baseline IT workstation security and capacity checks."""
    checks: list[dict] = []

    free_pct = audit_record["storage"]["free_percent"]
    checks.append(
        {
            "check": "Minimum 15% Free Disk Capacity",
            "passed": free_pct >= 15.0,
            "observed": f"{free_pct}% free",
        }
    )

    fw_profiles = audit_record.get("firewall_profiles") or []
    if fw_profiles:
        all_enabled = all(bool(p.get("Enabled")) for p in fw_profiles)
        checks.append(
            {
                "check": "Windows Firewall Profiles Enabled",
                "passed": all_enabled,
                "observed": ", ".join(
                    f"{p.get('Name')}:{'ON' if p.get('Enabled') else 'OFF'}" for p in fw_profiles
                ),
            }
        )
    else:
        checks.append(
            {
                "check": "Windows Firewall Profiles Enabled",
                "passed": False,
                "observed": "Unavailable / non-Windows host",
            }
        )

    serial = str(audit_record.get("serial_number") or "").strip()
    checks.append(
        {
            "check": "Hardware Asset Serial Recorded",
            "passed": bool(serial and serial.lower() != "unknown"),
            "observed": serial or "Unknown",
        }
    )
    return checks


def collect_workstation_audit(disk_path: str | None = None, probe_cim: bool = True) -> dict:
    """Collect normalized hardware, OS, storage, and compliance audit data."""
    root = disk_path or os.path.abspath(os.sep)
    disk = shutil.disk_usage(root)
    gb = 1024 ** 3
    free_pct = round((disk.free / disk.total) * 100, 2) if disk.total else 0.0

    cim = _query_windows_cim_inventory() if probe_cim else None
    cim = cim or {}

    record = {
        "audited_at_utc": datetime.now(timezone.utc).isoformat(),
        "hostname": socket.gethostname(),
        "os": cim.get("os_caption") or f"{platform.system()} {platform.release()}",
        "os_build": cim.get("os_build") or platform.version(),
        "architecture": platform.machine(),
        "manufacturer": cim.get("manufacturer") or "Generic",
        "model": cim.get("model") or platform.machine(),
        "serial_number": cim.get("serial_number") or "Unknown",
        "total_ram_gb": cim.get("total_ram_gb"),
        "firewall_profiles": cim.get("firewall_profiles") or [],
        "storage": {
            "mount": root,
            "total_gb": round(disk.total / gb, 2),
            "free_gb": round(disk.free / gb, 2),
            "free_percent": free_pct,
        },
    }
    record["compliance_checks"] = evaluate_compliance_checks(record)
    record["compliant"] = all(c["passed"] for c in record["compliance_checks"])
    return record


def export_audit_csv(records: list[dict], out_path: str | Path) -> Path:
    """Write workstation fleet audit records to an IT asset CSV file."""
    target = Path(out_path)
    fieldnames = [
        "audited_at_utc",
        "hostname",
        "manufacturer",
        "model",
        "serial_number",
        "os",
        "os_build",
        "total_ram_gb",
        "free_gb",
        "free_percent",
        "compliant",
    ]
    with target.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        for rec in records:
            writer.writerow(
                {
                    "audited_at_utc": rec["audited_at_utc"],
                    "hostname": rec["hostname"],
                    "manufacturer": rec["manufacturer"],
                    "model": rec["model"],
                    "serial_number": rec["serial_number"],
                    "os": rec["os"],
                    "os_build": rec["os_build"],
                    "total_ram_gb": rec.get("total_ram_gb") or "",
                    "free_gb": rec["storage"]["free_gb"],
                    "free_percent": rec["storage"]["free_percent"],
                    "compliant": rec["compliant"],
                }
            )
    return target


def render_audit_html(record: dict) -> str:
    """Render an executive HTML compliance & hardware asset sheet."""
    rows = "\n".join(
        f"<tr><td>{html.escape(c['check'])}</td>"
        f"<td>{'PASS' if c['passed'] else 'FAIL'}</td>"
        f"<td>{html.escape(c['observed'])}</td></tr>"
        for c in record["compliance_checks"]
    )
    return f"""<!doctype html>
<html lang="en">
<head><meta charset="utf-8" /><title>WinOps Asset Audit — {html.escape(record['hostname'])}</title></head>
<body style="font-family:system-ui,sans-serif;background:#0f172a;color:#f8fafc;padding:2rem;">
  <h1>WinOps Workstation Audit: {html.escape(record['hostname'])}</h1>
  <p>Model: {html.escape(str(record['manufacturer']))} {html.escape(str(record['model']))} | Serial: <code>{html.escape(str(record['serial_number']))}</code></p>
  <p>OS: {html.escape(str(record['os']))} (Build {html.escape(str(record['os_build']))}) | Free Disk: {record['storage']['free_gb']} GB ({record['storage']['free_percent']}%)</p>
  <table border="1" cellpadding="8" cellspacing="0" style="border-collapse:collapse;border-color:#334155;">
    <thead><tr><th>Compliance Check</th><th>Status</th><th>Observed</th></tr></thead>
    <tbody>{rows}</tbody>
  </table>
</body>
</html>"""
