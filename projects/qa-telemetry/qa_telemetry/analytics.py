"""Analytics, flaky-test detection, regression diffing, and QA release gate checks."""

from __future__ import annotations

import html
import math
from collections import defaultdict

from qa_telemetry.ingestor import TelemetryStore


def percentile(sorted_values: list[float], pct: float) -> float:
    """Compute linear-interpolated percentile from a pre-sorted list of numbers."""
    if not sorted_values:
        return 0.0
    if len(sorted_values) == 1:
        return round(sorted_values[0], 4)
    rank = (pct / 100.0) * (len(sorted_values) - 1)
    low = math.floor(rank)
    high = math.ceil(rank)
    if low == high:
        return round(sorted_values[low], 4)
    weight = rank - low
    return round(sorted_values[low] * (1 - weight) + sorted_values[high] * weight, 4)


def compute_run_summary(store: TelemetryStore, run_id: int) -> dict:
    """Calculate yield/pass rate and latency distribution for a recorded test run."""
    run = store.get_run(run_id)
    if not run:
        raise LookupError(f"Test run #{run_id} not found.")

    executed = run["passed_cases"] + run["failed_cases"]
    pass_rate = round((run["passed_cases"] / executed) * 100, 2) if executed else 0.0
    durations = sorted(float(c["duration_s"]) for c in run["cases"])

    return {
        "run_id": run["id"],
        "suite_name": run["suite_name"],
        "build_ref": run["build_ref"],
        "total_cases": run["total_cases"],
        "passed_cases": run["passed_cases"],
        "failed_cases": run["failed_cases"],
        "skipped_cases": run["skipped_cases"],
        "pass_rate_percent": pass_rate,
        "total_duration_s": run["duration_s"],
        "p50_case_s": percentile(durations, 50),
        "p95_case_s": percentile(durations, 95),
    }


def detect_flaky_tests(store: TelemetryStore, suite_name: str | None = None) -> list[dict]:
    """Identify test cases exhibiting both PASSED and FAILED outcomes across runs."""
    history = store.fetch_all_case_history(suite_name=suite_name)
    outcomes_by_test: dict[str, list[str]] = defaultdict(list)

    for row in history:
        key = f"{row['classname']}::{row['name']}"
        if row["outcome"] in {"PASSED", "FAILED"}:
            outcomes_by_test[key].append(row["outcome"])

    flaky: list[dict] = []
    for key, outcomes in sorted(outcomes_by_test.items()):
        unique = set(outcomes)
        if "PASSED" in unique and "FAILED" in unique:
            fail_count = sum(1 for o in outcomes if o == "FAILED")
            flaky.append(
                {
                    "test_id": key,
                    "runs_observed": len(outcomes),
                    "fail_count": fail_count,
                    "flake_rate_percent": round((fail_count / len(outcomes)) * 100, 2),
                }
            )
    return flaky


def detect_regressions(store: TelemetryStore, baseline_run_id: int, candidate_run_id: int) -> list[str]:
    """Return test identifiers that passed in baseline_run_id and failed in candidate_run_id."""
    baseline = store.get_run(baseline_run_id)
    candidate = store.get_run(candidate_run_id)
    if not baseline or not candidate:
        raise LookupError("Both baseline and candidate run IDs must exist.")

    base_map = {f"{c['classname']}::{c['name']}": c["outcome"] for c in baseline["cases"]}
    regressions = [
        f"{c['classname']}::{c['name']}"
        for c in candidate["cases"]
        if c["outcome"] == "FAILED" and base_map.get(f"{c['classname']}::{c['name']}") == "PASSED"
    ]
    return sorted(regressions)


def evaluate_release_gate(
    store: TelemetryStore,
    run_id: int,
    min_pass_rate: float = 95.0,
    max_failures: int = 0,
) -> dict:
    """Enforce deterministic QA release gate thresholds for CI/CD sign-off."""
    summary = compute_run_summary(store, run_id)
    reasons: list[str] = []

    if summary["pass_rate_percent"] < min_pass_rate:
        reasons.append(
            f"Pass rate {summary['pass_rate_percent']}% is below threshold {min_pass_rate}%."
        )
    if summary["failed_cases"] > max_failures:
        reasons.append(
            f"Failed count {summary['failed_cases']} exceeds max allowed {max_failures}."
        )

    return {
        "run_id": run_id,
        "verdict": "PASS" if not reasons else "BLOCKED",
        "reasons": reasons,
        "summary": summary,
    }


def render_html_signoff_report(store: TelemetryStore, run_id: int) -> str:
    """Render a standalone dark-mode HTML QA sign-off summary report."""
    gate = evaluate_release_gate(store, run_id)
    summary = gate["summary"]
    run = store.get_run(run_id)
    flaky = detect_flaky_tests(store, suite_name=summary["suite_name"])

    rows_html = "\n".join(
        f"<tr><td>{html.escape(c['classname'])}</td>"
        f"<td>{html.escape(c['name'])}</td>"
        f"<td>{html.escape(c['outcome'])}</td>"
        f"<td>{c['duration_s']}s</td></tr>"
        for c in (run["cases"] if run else [])
    )

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <title>QA Sign-Off Report — Run #{run_id}</title>
  <style>
    body {{ font-family: system-ui, sans-serif; background: #0f172a; color: #f8fafc; margin: 2rem; }}
    .card {{ background: #111827; border: 1px solid #1e293b; border-radius: 8px; padding: 1.25rem; margin-bottom: 1rem; }}
    .badge {{ display: inline-block; padding: 0.25rem 0.6rem; border-radius: 4px; font-weight: 700; }}
    .pass {{ background: rgba(16,185,129,0.2); color: #34d399; }}
    .blocked {{ background: rgba(239,68,68,0.2); color: #f87171; }}
    table {{ width: 100%; border-collapse: collapse; margin-top: 0.75rem; font-size: 0.9rem; }}
    th, td {{ border-bottom: 1px solid #1e293b; padding: 0.5rem; text-align: left; }}
  </style>
</head>
<body>
  <div class="card">
    <h1>QA Telemetry Sign-Off — {html.escape(summary['suite_name'])}</h1>
    <p>Build Ref: <code>{html.escape(summary['build_ref'])}</code> · Gate Verdict:
      <span class="badge {'pass' if gate['verdict'] == 'PASS' else 'blocked'}">{gate['verdict']}</span>
    </p>
    <p>Pass Rate: <strong>{summary['pass_rate_percent']}%</strong> ({summary['passed_cases']}/{summary['total_cases']} passed, {summary['failed_cases']} failed) · p95 Duration: {summary['p95_case_s']}s · Flaky Tests Tracked: {len(flaky)}</p>
  </div>
  <div class="card">
    <h2>Executed Test Cases</h2>
    <table>
      <thead><tr><th>Suite</th><th>Test Case</th><th>Outcome</th><th>Duration</th></tr></thead>
      <tbody>{rows_html}</tbody>
    </table>
  </div>
</body>
</html>"""
