# NetAudit — Cisco IOS Config Auditor & IPv4 VLSM Planner

Python 3.12 network engineering utility for auditing Cisco IOS `running-config` files and computing OSPF-ready IPv4 VLSM subnet allocations.

## Capabilities
- **IOS Config Auditor (`netaudit/parser.py`):** Extracts hostnames, L3 interfaces, VLANs, OSPF networks, and flags missing `enable secret`, unencrypted passwords, or exposed VTY Telnet.
- **VLSM & OSPF Wildcard Planner (`netaudit/subnetting.py`):** Calculates optimal non-overlapping VLSM allocations and Cisco wildcard masks.

## Usage
```bash
python -m netaudit.cli audit-config --file router.cfg
python -m netaudit.cli vlsm --parent 10.20.0.0/24 --req Data:100 --req Voice:50 --req P2P:2
pytest
```
