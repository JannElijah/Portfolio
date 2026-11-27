"""Tests for NetAudit Cisco IOS parsing, security auditing, and VLSM subnet planning."""

from __future__ import annotations

import json

import pytest

from netaudit.cli import main
from netaudit.parser import audit_parsed_config, generate_ios_remediation_cli, parse_ios_config
from netaudit.subnetting import allocate_vlsm_subnets, describe_cidr

SECURE_IOS = """
hostname HQ-CORE-R1
service password-encryption
enable secret 5 $1$xyz$hash
ip ssh version 2
!
vlan 10
 name CORP_DATA
vlan 20
 name CME_VOICE
!
interface GigabitEthernet0/0
 description Uplink to Branch A
 ip address 10.10.0.1 255.255.255.252
!
router ospf 1
 network 10.10.0.0 0.0.0.3 area 0
 network 192.168.10.0 0.0.0.255 area 0
!
line vty 0 4
 transport input ssh
!
"""

INSECURE_IOS = """
hostname BRANCH-R2
interface FastEthernet0/0
 ip address 192.168.20.1 255.255.255.0
line vty 0 4
 transport input telnet
"""


def test_parse_and_audit_secure_cisco_config() -> None:
    parsed = parse_ios_config(SECURE_IOS)
    assert parsed["hostname"] == "HQ-CORE-R1"
    assert len(parsed["vlans"]) == 2
    assert len(parsed["ospf_networks"]) == 2

    audit = audit_parsed_config(parsed)
    assert audit["overall_status"] == "PASS"
    assert audit["configured_l3_interfaces"] == 1


def test_audit_flags_telnet_and_missing_secrets() -> None:
    audit = audit_parsed_config(parse_ios_config(INSECURE_IOS))
    assert audit["overall_status"] == "FAIL"
    severities = {f["rule"]: f["severity"] for f in audit["findings"]}
    assert severities["Enable Secret Configured"] == "FAIL"
    assert severities["SSH-Only VTY Management"] == "FAIL"
    assert severities["SSHv2 Enforced"] == "WARN"
    rems = generate_ios_remediation_cli(audit)
    assert "ip ssh version 2" in rems and "enable secret <strong-secret>" in rems


def test_cidr_and_vlsm_allocation() -> None:
    info = describe_cidr("192.168.10.0/24")
    assert info["wildcard_mask"] == "0.0.0.255"
    assert info["usable_hosts"] == 254

    plan = allocate_vlsm_subnets(
        "10.20.0.0/24",
        [{"name": "Staff-LAN", "hosts": 100}, {"name": "VoIP-VLAN", "hosts": 50}, {"name": "P2P-Link", "hosts": 2}],
    )
    assert [row["cidr"] for row in plan] == ["10.20.0.0/25", "10.20.0.128/26", "10.20.0.192/30"]

    with pytest.raises(ValueError):
        allocate_vlsm_subnets("10.20.0.0/28", [{"name": "TooBig", "hosts": 30}])


def test_cli_audit_and_vlsm(tmp_path, capsys) -> None:
    cfg = tmp_path / "r1.cfg"
    html_out = tmp_path / "audit.html"
    cfg.write_text(SECURE_IOS, encoding="utf-8")
    assert main(["audit-config", "--file", str(cfg), "--html", str(html_out)]) == 0
    out = json.loads(capsys.readouterr().out)
    assert out["audit"]["overall_status"] == "PASS"
    html_text = html_out.read_text(encoding="utf-8")
    assert "NetAudit IOS Security Report — HQ-CORE-R1 (PASS)" in html_text
    assert "Cisco IOS Hardening Remediation CLI" in html_text

    assert main(["vlsm", "--parent", "172.16.0.0/24", "--req", "Voice:25", "--req", "Data:60"]) == 0
    vlsm_out = json.loads(capsys.readouterr().out)
    assert len(vlsm_out) == 2
