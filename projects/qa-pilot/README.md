# QA-Pilot — Browser E2E & API Contract Test Framework

Automated end-to-end **Playwright Page Object Model** + **HTTP API Contract Validation** framework written in Python (`pytest`), executing live Chromium workflows and SLA latency checks against `projects/uphsd-dms` and exporting dark-themed HTML QA Sign-Off reports + JUnit XML for `projects/qa-telemetry`.

## Features
- **Playwright Page Object Model** (`qa_pilot/pages/dms_page.py`): Encapsulates selectors and Kanban workflow actions cleanly.
- **API Contract & Latency Validator** (`qa_pilot/contracts.py`): Enforces HTTP status codes, JSON response field types, and response latency budgets.
- **HTML QA Sign-Off Report Generator** (`qa_pilot/runner.py` & `qa_pilot/cli.py`): Converts `--junitxml` results into executive dark-mode HTML reports.

## Quick Start
```bash
cd projects/qa-pilot
python -m pytest -v --junitxml=junit.xml
python -m qa_pilot.cli report junit.xml --out qa_report.html
```
