"""Collects and classifies Windows Event Log errors and stopped Auto-start services."""

from __future__ import annotations

import json
import platform
import subprocess
from collections import Counter
from datetime import datetime, timezone


def _query_windows_events_and_services(max_events: int = 25) -> dict | None:
    """Query Windows System/Application Error/Critical events and stopped Auto services via PowerShell."""
    if platform.system().lower() != "windows":
        return None
    ps_script = (
        f"$ev = @(Get-WinEvent -FilterHashtable @{{LogName='System','Application'; Level=1,2}} -MaxEvents {max_events} -ErrorAction SilentlyContinue "
        "| Select-Object Id, LevelDisplayName, LogName, ProviderName, @{N='Time';E={$_.TimeCreated.ToString('o')}}, Message); "
        "$svc = @(Get-CimInstance Win32_Service -Filter \"StartMode='Auto' AND State!='Running'\" "
        "| Select-Object Name, DisplayName, State, StartMode); "
        "@{events=$ev; stopped_auto_services=$svc} | ConvertTo-Json -Depth 4 -Compress"
    )
    try:
        proc = subprocess.run(
            ["powershell", "-NoProfile", "-Command", ps_script],
            capture_output=True,
            text=True,
            timeout=8,
            check=True,
        )
        raw = proc.stdout.strip()
        return json.loads(raw) if raw else None
    except (OSError, ValueError, subprocess.SubprocessError):
        return None


def analyze_host_telemetry(payload: dict) -> dict:
    """Aggregate Event ID frequencies, stopped services, and derive overall host triage status."""
    events = payload.get("events") or []
    if isinstance(events, dict):
        events = [events]
    stopped = payload.get("stopped_auto_services") or []
    if isinstance(stopped, dict):
        stopped = [stopped]

    critical_count = sum(1 for e in events if str(e.get("LevelDisplayName", "")).lower() == "critical")
    error_count = len(events) - critical_count
    id_counts = Counter(int(e["Id"]) for e in events if e.get("Id") is not None)
    remediation_map = {
        7031: "Restart stopped Windows service: Restart-Service -Name <ServiceName> -Force",
        7000: "Inspect service binary path & LogOn credentials in services.msc",
        41: "Verify power stability & sleep state logs: powercfg /sleepstudy",
        1000: "Inspect faulting module in Event Viewer or run sfc /scannow",
        10016: "Review DCOM AppID permissions in Component Services (dcomcnfg)",
    }
    top_event_ids = [
        {
            "event_id": eid,
            "count": cnt,
            "remediation": remediation_map.get(eid, "Review provider logs with Get-WinEvent -FilterHashtable"),
        }
        for eid, cnt in id_counts.most_common(5)
    ]

    if critical_count > 0 or len(stopped) > 0:
        status = "CRITICAL"
    elif error_count >= 5 or any(cnt >= 3 for _, cnt in id_counts.items()):
        status = "WARN"
    else:
        status = "HEALTHY"

    return {
        "captured_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "critical_events": critical_count,
        "error_events": error_count,
        "stopped_auto_services": stopped,
        "top_event_ids": top_event_ids,
        "events": events,
    }


def run_logpulse_scan(max_events: int = 25, live_windows: bool = True) -> dict:
    """Run live Windows Event/Service inspection or return an empty baseline payload."""
    payload = _query_windows_events_and_services(max_events=max_events) if live_windows else None
    if payload is None:
        payload = {"events": [], "stopped_auto_services": []}
    return analyze_host_telemetry(payload)
