"""Tests for WinOps Winget manifest generation, compliance evaluation, and CSV/HTML exports."""

from __future__ import annotations

import csv
import json

import pytest

from winops.auditor import (
    build_remediation_steps,
    collect_workstation_audit,
    compute_compliance_score,
    evaluate_compliance_checks,
    export_audit_csv,
    render_audit_html,
)
from winops.cli import main
from winops.manifest import render_provisioning_ps1, select_packages_for_profile


def test_role_based_winget_manifest_filtering() -> None:
    standard = select_packages_for_profile("standard")
    support = select_packages_for_profile("it_support")
    dev = select_packages_for_profile("developer")

    assert len(standard) < len(support) < len(dev)
    assert any(pkg["id"] == "Python.Python.3.12" for pkg in dev)
    with pytest.raises(ValueError):
        select_packages_for_profile("unknown_role")


def test_powershell_script_generation() -> None:
    script = render_provisioning_ps1("it_support")
    assert "'Notepad++.Notepad++'" in script
    assert "winget install --id $pkgId" in script
    assert "Git.Git" not in script


def test_compliance_evaluation_passes_healthy_workstation() -> None:
    sample = {
        "serial_number": "PF4X9012",
        "storage": {"free_percent": 42.5},
        "firewall_profiles": [
            {"Name": "Domain", "Enabled": True},
            {"Name": "Private", "Enabled": True},
        ],
    }
    checks = evaluate_compliance_checks(sample)
    assert all(item["passed"] for item in checks)


def test_compliance_flags_missing_serial_and_disabled_firewall() -> None:
    sample = {
        "serial_number": "Unknown",
        "storage": {"free_percent": 10.0},
        "firewall_profiles": [{"Name": "Public", "Enabled": False}],
    }
    checks = evaluate_compliance_checks(sample)
    assert not any(item["passed"] for item in checks)
    assert compute_compliance_score(checks) == 0
    steps = build_remediation_steps(checks)
    assert len(steps) == 3 and any("Set-NetFirewallProfile" in s for s in steps)


def test_cli_audit_exports_json_csv_and_html(tmp_path, capsys) -> None:
    csv_path = tmp_path / "fleet.csv"
    html_path = tmp_path / "audit.html"

    assert main(["audit", "--no-cim", "--csv", str(csv_path), "--html", str(html_path)]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["storage"]["total_gb"] > 0
    assert html_path.exists()
    html_out = render_audit_html(payload)
    assert "WinOps Workstation Audit" in html_out
    assert "<svg" in html_out and "Remediation Checklist" in html_out

    with csv_path.open("r", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    assert len(rows) == 1
    assert rows[0]["hostname"] == payload["hostname"]


def test_collect_workstation_audit_offline_mode() -> None:
    record = collect_workstation_audit(probe_cim=False)
    assert len(record["compliance_checks"]) == 3
