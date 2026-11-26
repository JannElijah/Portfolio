# LogPulse — Windows Event Log & Service Health Monitor

PowerShell + Python 3.12 utility for Windows System/Application Critical/Error event aggregation, Auto-start service failure detection, and SQLite/HTML triage reporting.

## Usage
```bash
python -m logpulse.cli scan --save --html host_triage.html
python -m logpulse.cli analyze-json --file sample.json --save
pytest
```
