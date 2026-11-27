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


def compute_suite_trend(store: TelemetryStore, suite_name: str, limit: int = 10) -> list[dict]:
    """Return chronological run trend metrics (pass rate & p95 duration) for suite_name."""
    runs = list(reversed(store.list_runs(suite_name=suite_name)[:limit]))
    trend: list[dict] = []
    for run in runs:
        s = compute_run_summary(store, int(run["id"]))
        trend.append(
            {
                "run_id": s["run_id"],
                "build_ref": s["build_ref"],
                "pass_rate_percent": s["pass_rate_percent"],
                "p95_case_s": s["p95_case_s"],
            }
        )
    return trend


def render_html_signoff_report(store: TelemetryStore, run_id: int) -> str:
    """Render a standalone dark-mode HTML QA sign-off summary report with trend & flaky panels."""
    gate = evaluate_release_gate(store, run_id)
    summary = gate["summary"]
    run = store.get_run(run_id)
    flaky = detect_flaky_tests(store, suite_name=summary["suite_name"])
    trend = compute_suite_trend(store, suite_name=summary["suite_name"])

    rows_html = "\n".join(
        f"<tr><td class='mono'>{html.escape(c['classname'])}</td>"
        f"<td>{html.escape(c['name'])}</td>"
        f"<td><span class='badge {'pass' if c['outcome']=='PASSED' else 'blocked'}'>{html.escape(c['outcome'])}</span></td>"
        f"<td class='mono'>{c['duration_s']}s</td></tr>"
        for c in (run["cases"] if run else [])
    )

    trend_section = ""
    if len(trend) >= 2:
        w, h, pad = 340, 74, 10
        pts = " ".join(
            f"{(pad + (i / (len(trend) - 1)) * (w - pad * 2)):.1f},{(h - pad - (p['pass_rate_percent'] / 100.0) * (h - pad * 2)):.1f}"
            for i, p in enumerate(trend)
        )
        trend_section = (
            "<div class='card'><h2 style='margin:0 0 8px;font-size:0.95rem;'>Suite Pass-Rate Trend</h2>"
            f"<svg viewBox='0 0 {w} {h}' style='width:100%;max-width:460px;height:{h}px;background:#090d16;border:1px solid #1e293b;border-radius:6px;'>"
            f"<polyline fill='none' stroke='#38bdf8' stroke-width='2.2' points='{pts}' /></svg></div>"
        )

    flaky_rows = "".join(
        f"<tr><td class='mono'>{html.escape(f['test_id'])}</td><td class='mono'>{f['runs_observed']}</td>"
        f"<td class='mono' style='color:#fbbf24;'>{f['flake_rate_percent']}%</td></tr>"
        for f in flaky
    ) or "<tr><td colspan='3' style='color:#94a3b8;'>Zero flaky tests observed across historical runs.</td></tr>"

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <title>QA Sign-Off Report — Run #{run_id}</title>
  <style>
    body {{ font-family: Inter, system-ui, sans-serif; background: #0b0f19; color: #f8fafc; margin: 2rem; }}
    .kpis {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin: 14px 0; }}
    .kpi {{ background: #111827; border: 1px solid #1e293b; border-radius: 8px; padding: 12px; }}
    .lbl {{ font-size: 0.68rem; color: #94a3b8; text-transform: uppercase; }}
    .val {{ font-size: 1.3rem; font-weight: 700; font-family: monospace; margin-top: 4px; }}
    .card {{ background: #111827; border: 1px solid #1e293b; border-radius: 8px; padding: 1.2rem; margin-bottom: 1rem; }}
    .badge {{ display: inline-block; padding: 0.2rem 0.55rem; border-radius: 999px; font-weight: 700; font-size: 0.72rem; font-family: monospace; }}
    .pass {{ background: rgba(16,185,129,0.2); color: #34d399; }}
    .blocked {{ background: rgba(239,68,68,0.2); color: #f87171; }}
    .mono {{ font-family: ui-monospace, monospace; }}
    table {{ width: 100%; border-collapse: collapse; margin-top: 0.5rem; font-size: 0.85rem; }}
    th, td {{ border-bottom: 1px solid #1e293b; padding: 0.5rem; text-align: left; }}
  </style>
</head>
<body>
  <div class="card">
    <h1 style="margin:0 0 6px;">QA Telemetry Sign-Off — {html.escape(summary['suite_name'])}</h1>
    <p style="margin:0;">Build Ref: <code>{html.escape(summary['build_ref'])}</code> · Gate Verdict:
      <span class="badge {'pass' if gate['verdict'] == 'PASS' else 'blocked'}">{gate['verdict']}</span>
    </p>
  </div>
  <div class="kpis">
    <div class="kpi"><div class="lbl">Pass Rate</div><div class="val" style="color:#34d399;">{summary['pass_rate_percent']}%</div></div>
    <div class="kpi"><div class="lbl">Cases Passed / Total</div><div class="val">{summary['passed_cases']} / {summary['total_cases']}</div></div>
    <div class="kpi"><div class="lbl">p95 Case Duration</div><div class="val">{summary['p95_case_s']}s</div></div>
    <div class="kpi"><div class="lbl">Flaky Tests</div><div class="val" style="color:#fbbf24;">{len(flaky)}</div></div>
  </div>
  {trend_section}
  <div class="card">
    <h2 style="margin:0 0 6px;font-size:0.95rem;">Flaky Tests Breakdown</h2>
    <table><thead><tr><th>Test Identifier</th><th>Runs</th><th>Flake Rate</th></tr></thead><tbody>{flaky_rows}</tbody></table>
  </div>
  <div class="card">
    <h2 style="margin:0 0 6px;font-size:0.95rem;">Executed Test Cases</h2>
    <table>
      <thead><tr><th>Suite</th><th>Test Case</th><th>Outcome</th><th>Duration</th></tr></thead>
      <tbody>{rows_html}</tbody>
    </table>
  </div>
</body>
</html>"""
