# WinOps — Windows 11 Provisioning & Asset Audit Toolkit

PowerShell + Python 3.12 workstation onboarding and compliance auditing utility for IT Technical Support and Systems Administration workflows.

## Key Capabilities
- **Role-Based Winget Manifest (`winops/manifest.py`):** Generates idempotent PowerShell provisioning scripts tailored for `standard`, `it_support`, or `developer` endpoints.
- **Hardware & Security Audit (`winops/auditor.py`, `scripts/audit_workstation.ps1`):** Captures host model, BIOS serial number, OS build, RAM/disk capacity, and Windows Firewall profile states via Windows CIM, exporting structured JSON, CSV, and HTML compliance reports.

## Usage
```powershell
powershell -ExecutionPolicy Bypass -File scripts/audit_workstation.ps1
python -m winops.cli audit --csv fleet.csv --html audit.html
python -m winops.cli provision-script --profile it_support --out provision.ps1
pytest
```
