# QA Telemetry — Automated Test Verification & Defect Analytics Engine

Zero-dependency Python 3.12 + SQLite quality assurance telemetry engine built for software QA and semiconductor/hardware validation pipelines.

## Key Capabilities
- **Multi-Format Ingestion (`qa_telemetry/ingestor.py`):** Parses `pytest --junitxml` XML artifacts and structured JSON test-bench logs into normalized SQLite `test_runs` and `test_cases` tables.
- **Defect & Stability Analytics (`qa_telemetry/analytics.py`):** Computes pass/yield percentages, `p50`/`p95` execution latency percentiles, historical flaky-test detection, baseline-vs-candidate regression diffing, and deterministic CI release gates (`PASS / BLOCKED`).
- **Sign-Off Reporting (`qa_telemetry/cli.py`):** Exports standalone dark-mode HTML QA sign-off reports.

## Usage
```bash
pytest --junitxml=results.xml
python -m qa_telemetry.cli ingest-junit --xml results.xml --suite core-api --build v1.4.0
python -m qa_telemetry.cli gate-check --run-id 1 --min-pass-rate 95 --max-failures 0
python -m qa_telemetry.cli export-html --run-id 1 --out qa_signoff.html
pytest
```
