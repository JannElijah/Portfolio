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


def compute_compliance_score(checks: list[dict]) -> int:
    """Return integer 0-100 percentage of compliance checks passing."""
    if not checks:
        return 0
    return round(sum(1 for c in checks if c.get("passed")) / len(checks) * 100)


def build_remediation_steps(checks: list[dict]) -> list[str]:
    """Map failing compliance checks to concrete PowerShell/IT remediation commands."""
    steps: list[str] = []
    for chk in checks:
        if chk.get("passed"):
            continue
        name = chk.get("check", "")
        if "Disk" in name:
            steps.append("Run Storage Sense / clean Windows Update cache: cleanmgr /sagerun:1")
        elif "Firewall" in name:
            steps.append("Enable all firewall profiles: Set-NetFirewallProfile -Profile Domain,Public,Private -Enabled True")
        elif "Serial" in name:
            steps.append("Record BIOS asset tag via CIM: (Get-CimInstance Win32_BIOS).SerialNumber")
        else:
            steps.append(f"Inspect and resolve failing check: {name}")
    return steps


def render_audit_html(record: dict) -> str:
    """Render an executive dark-mode HTML compliance & hardware asset sheet with SVG gauge."""
    checks = record["compliance_checks"]
    score = compute_compliance_score(checks)
    remediations = build_remediation_steps(checks)
    free_pct = float(record["storage"]["free_percent"])
    used_pct = max(0.0, min(100.0, round(100.0 - free_pct, 1)))
    ring_r = 26
    ring_c = round(2 * 3.14159 * ring_r, 1)
    ring_dash = round((score / 100.0) * ring_c, 1)
    ring_col = "#10b981" if score == 100 else "#f59e0b" if score >= 60 else "#f43f5e"

    rows = "\n".join(
        f"<tr><td>{html.escape(c['check'])}</td>"
        f"<td><span class='pill {'ok' if c['passed'] else 'bad'}'>{'PASS' if c['passed'] else 'FAIL'}</span></td>"
        f"<td class='mono'>{html.escape(c['observed'])}</td></tr>"
        for c in checks
    )
    rem_html = (
        "".join(f"<li><code>{html.escape(s)}</code></li>" for s in remediations)
        or "<li class='muted'>All compliance baselines satisfied — no remediation required.</li>"
    )
    ram_val = f"{record.get('total_ram_gb')} GB" if record.get("total_ram_gb") else "Offline"

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <title>WinOps Asset Audit — {html.escape(record['hostname'])}</title>
  <style>
    body {{ margin:0; font-family:Inter,system-ui,sans-serif; background:#090d16; color:#f4f4f5; padding:26px 34px; }}
    .hdr {{ display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid #1e293b; padding-bottom:14px; margin-bottom:18px; }}
    h1 {{ margin:0; font-size:1.3rem; }}
    .sub {{ color:#94a3b8; font-size:0.82rem; margin-top:4px; }}
    .kpis {{ display:grid; grid-template-columns:repeat(4,1fr); gap:12px; margin-bottom:18px; }}
    .kpi {{ background:#111827; border:1px solid #1e293b; border-radius:10px; padding:12px 14px; }}
    .lbl {{ font-size:0.68rem; color:#94a3b8; text-transform:uppercase; letter-spacing:0.06em; }}
    .val {{ font-size:1.25rem; font-weight:700; margin-top:4px; font-family:ui-monospace,monospace; }}
    .card {{ background:#111827; border:1px solid #1e293b; border-radius:10px; padding:16px; margin-bottom:14px; }}
    .bar-bg {{ height:8px; background:#1e293b; border-radius:999px; overflow:hidden; margin-top:8px; }}
    .bar-fill {{ height:100%; background:#38bdf8; width:{used_pct}%; }}
    table {{ width:100%; border-collapse:collapse; font-size:0.84rem; }}
    th, td {{ border-bottom:1px solid #1e293b; padding:9px 8px; text-align:left; }}
    th {{ font-size:0.72rem; color:#94a3b8; text-transform:uppercase; }}
    .mono {{ font-family:ui-monospace,monospace; font-size:0.8rem; color:#cbd5e1; }}
    .pill {{ padding:2px 8px; border-radius:999px; font-family:monospace; font-size:0.72rem; font-weight:700; }}
    .ok {{ background:rgba(16,185,129,0.16); color:#34d399; }}
    .bad {{ background:rgba(244,63,94,0.16); color:#fb7185; }}
    .muted {{ color:#94a3b8; }}
  </style>
</head>
<body>
  <div class="hdr">
    <div>
      <h1>WinOps Workstation Audit: {html.escape(record['hostname'])}</h1>
      <div class="sub">Model: {html.escape(str(record['manufacturer']))} {html.escape(str(record['model']))} · Serial: <code>{html.escape(str(record['serial_number']))}</code></div>
    </div>
    <svg width="68" height="68" viewBox="0 0 68 68" aria-label="Compliance score">
      <circle cx="34" cy="34" r="{ring_r}" fill="none" stroke="#1e293b" stroke-width="6" />
      <circle cx="34" cy="34" r="{ring_r}" fill="none" stroke="{ring_col}" stroke-width="6" stroke-dasharray="{ring_dash} {ring_c}" stroke-linecap="round" transform="rotate(-90 34 34)" />
      <text x="34" y="38" text-anchor="middle" fill="#f8fafc" font-size="13" font-family="monospace" font-weight="700">{score}%</text>
    </svg>
  </div>
  <div class="kpis">
    <div class="kpi"><div class="lbl">Compliance Score</div><div class="val" style="color:{ring_col};">{score}%</div></div>
    <div class="kpi"><div class="lbl">Operating System</div><div class="val" style="font-size:0.95rem;">{html.escape(str(record['os']))}</div></div>
    <div class="kpi"><div class="lbl">Memory</div><div class="val">{html.escape(ram_val)}</div></div>
    <div class="kpi"><div class="lbl">Free Storage</div><div class="val">{record['storage']['free_gb']} GB ({free_pct}%)</div><div class="bar-bg"><div class="bar-fill"></div></div></div>
  </div>
  <div class="card">
    <h2 style="margin:0 0 10px;font-size:0.95rem;">Workstation Compliance Matrix</h2>
    <table>
      <thead><tr><th>Compliance Check</th><th>Status</th><th>Observed</th></tr></thead>
      <tbody>{rows}</tbody>
    </table>
  </div>
  <div class="card">
    <h2 style="margin:0 0 8px;font-size:0.95rem;">Remediation Checklist</h2>
    <ul style="margin:0 0 0 18px;line-height:1.6;">{rem_html}</ul>
  </div>
</body>
</html>"""
