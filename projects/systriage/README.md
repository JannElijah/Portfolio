# SysTriage — Endpoint Health & IT Helpdesk Triage Utility

Zero-dependency Python 3.12 + SQLite diagnostic and incident triage tool built for Tier-1/Tier-2 IT Technical Support and Systems Operations workflows.

## Key Capabilities
- **Endpoint Diagnostics (`systriage/diagnostics.py`):** Measures filesystem capacity, OS/host hardware profile, Windows CIM / Linux `/proc/meminfo` memory pressure, and TCP/DNS reachability latency with `HEALTHY / WARN / CRITICAL` severity rules.
- **Relational Ticket Store (`systriage/storage.py`):** SQLite schema (`tickets` + `diagnostic_snapshots`) with foreign-key snapshot linkage, P1–P3 SLA priority validation, and `OPEN -> IN_PROGRESS -> RESOLVED` lifecycle updates.
- **CLI & JSON Export (`systriage/cli.py`):** Supports `scan`, `ticket create|list|resolve`, and `export` commands.

## Usage
```bash
python -m systriage.cli scan --save --auto-ticket
python -m systriage.cli ticket list --status OPEN
python -m systriage.cli export --out systriage_report.json
pytest
```
