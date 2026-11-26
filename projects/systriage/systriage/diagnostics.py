"""Cross-platform workstation health and network reachability diagnostics."""

from __future__ import annotations

import os
import platform
import shutil
import socket
import subprocess
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Iterable


@dataclass(frozen=True)
class ProbeTarget:
    """Network target for DNS and TCP connectivity checks."""

    name: str
    host: str
    port: int


DEFAULT_TARGETS: tuple[ProbeTarget, ...] = (
    ProbeTarget(name="Local Loopback", host="127.0.0.1", port=80),
    ProbeTarget(name="Cloudflare DNS", host="1.1.1.1", port=53),
)


def classify_usage_severity(percent_used: float, warn_threshold: float = 80.0, critical_threshold: float = 92.0) -> str:
    """Map percentage utilization to HEALTHY, WARN, or CRITICAL."""
    if percent_used >= critical_threshold:
        return "CRITICAL"
    if percent_used >= warn_threshold:
        return "WARN"
    return "HEALTHY"


def collect_disk_metrics(path: str | None = None) -> dict:
    """Measure filesystem capacity and usage severity for the target drive."""
    target_path = path or os.path.abspath(os.sep)
    usage = shutil.disk_usage(target_path)
    used_pct = round((usage.used / usage.total) * 100, 2) if usage.total else 0.0
    gb = 1024 ** 3
    return {
        "path": target_path,
        "total_gb": round(usage.total / gb, 2),
        "free_gb": round(usage.free / gb, 2),
        "used_percent": used_pct,
        "severity": classify_usage_severity(used_pct),
    }


def collect_memory_metrics() -> dict:
    """Collect RAM utilization using Windows CIM/WMIC fallback or /proc/meminfo."""
    system_name = platform.system().lower()
    if system_name == "windows":
        try:
            proc = subprocess.run(
                [
                    "powershell",
                    "-NoProfile",
                    "-Command",
                    "$os = Get-CimInstance Win32_OperatingSystem; "
                    "$tot = [math]::Round($os.TotalVisibleMemorySize / 1MB, 2); "
                    "$free = [math]::Round($os.FreePhysicalMemory / 1MB, 2); "
                    "Write-Output \"$tot,$free\"",
                ],
                capture_output=True,
                text=True,
                timeout=4,
                check=True,
            )
            parts = proc.stdout.strip().split(",")
            if len(parts) == 2:
                total_gb = float(parts[0])
                free_gb = float(parts[1])
                used_pct = round(((total_gb - free_gb) / total_gb) * 100, 2) if total_gb else 0.0
                return {
                    "total_gb": total_gb,
                    "free_gb": free_gb,
                    "used_percent": used_pct,
                    "severity": classify_usage_severity(used_pct, 85.0, 95.0),
                    "source": "cim_win32_os",
                }
        except (OSError, ValueError, subprocess.SubprocessError):
            pass
    elif os.path.exists("/proc/meminfo"):
        try:
            values: dict[str, int] = {}
            with open("/proc/meminfo", "r", encoding="utf-8") as fh:
                for line in fh:
                    key, rest = line.split(":", 1)
                    values[key] = int(rest.strip().split()[0])
            total_kb = values.get("MemTotal", 0)
            avail_kb = values.get("MemAvailable", values.get("MemFree", 0))
            if total_kb:
                kb_to_gb = 1024 ** 2
                total_gb = round(total_kb / kb_to_gb, 2)
                free_gb = round(avail_kb / kb_to_gb, 2)
                used_pct = round(((total_kb - avail_kb) / total_kb) * 100, 2)
                return {
                    "total_gb": total_gb,
                    "free_gb": free_gb,
                    "used_percent": used_pct,
                    "severity": classify_usage_severity(used_pct, 85.0, 95.0),
                    "source": "proc_meminfo",
                }
        except (OSError, ValueError):
            pass

    return {
        "total_gb": None,
        "free_gb": None,
        "used_percent": None,
        "severity": "UNKNOWN",
        "source": "unavailable",
    }


def probe_tcp_endpoint(target: ProbeTarget, timeout_seconds: float = 1.5) -> dict:
    """Test DNS resolution and TCP socket reachability with round-trip latency."""
    start = time.perf_counter()
    try:
        resolved_ip = socket.gethostbyname(target.host)
        with socket.create_connection((resolved_ip, target.port), timeout=timeout_seconds):
            latency_ms = round((time.perf_counter() - start) * 1000, 2)
            return {
                "name": target.name,
                "host": target.host,
                "port": target.port,
                "resolved_ip": resolved_ip,
                "reachable": True,
                "latency_ms": latency_ms,
                "error": None,
            }
    except OSError as exc:
        latency_ms = round((time.perf_counter() - start) * 1000, 2)
        return {
            "name": target.name,
            "host": target.host,
            "port": target.port,
            "resolved_ip": None,
            "reachable": False,
            "latency_ms": latency_ms,
            "error": str(exc),
        }


def run_endpoint_diagnostic(
    targets: Iterable[ProbeTarget] | None = None,
    disk_path: str | None = None,
    include_network: bool = True,
) -> dict:
    """Execute full endpoint diagnostic snapshot and derive overall triage status."""
    probe_list = list(targets) if targets is not None else list(DEFAULT_TARGETS)
    disk = collect_disk_metrics(disk_path)
    memory = collect_memory_metrics()
    network = [probe_tcp_endpoint(target) for target in probe_list] if include_network else []

    severities = [disk["severity"], memory["severity"]]
    unreachable_count = sum(1 for item in network if not item["reachable"])

    if "CRITICAL" in severities:
        overall = "CRITICAL"
    elif "WARN" in severities or (include_network and network and unreachable_count == len(network)):
        overall = "WARN"
    else:
        overall = "HEALTHY"

    return {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "host": {
            "hostname": socket.gethostname(),
            "os": f"{platform.system()} {platform.release()}",
            "architecture": platform.machine(),
            "cpu_cores": os.cpu_count() or 1,
            "python_version": platform.python_version(),
        },
        "disk": disk,
        "memory": memory,
        "network": network,
        "overall_status": overall,
    }


def suggest_ticket_priority(diagnostic: dict) -> str:
    """Derive P1-P3 IT helpdesk SLA priority from diagnostic severity."""
    status = diagnostic.get("overall_status", "HEALTHY")
    if status == "CRITICAL":
        return "P1"
    if status == "WARN":
        return "P2"
    return "P3"


def probe_target_to_dict(target: ProbeTarget) -> dict:
    """Serialize ProbeTarget dataclass for reporting."""
    return asdict(target)
