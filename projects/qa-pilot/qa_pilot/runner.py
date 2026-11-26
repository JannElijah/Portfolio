"""HTML QA Sign-Off Report Renderer & QA-Telemetry Integration for QA-Pilot."""

from __future__ import annotations

import html
import sys
from datetime import datetime, timezone
from pathlib import Path


def render_qa_report(suite_title: str, results: list[dict], out_path: str | Path) -> Path:
    """Render a clean dark-mode HTML QA verification report with optional failure screenshot thumbnails."""
    total = len(results)
    passed = sum(1 for r in results if r.get("status") == "PASSED")
    failed = sum(1 for r in results if r.get("status") == "FAILED")
    pass_rate = round((passed / total) * 100, 1) if total else 0.0
    avg_ms = round(sum(float(r.get("duration_ms", 0.0)) for r in results) / total, 1) if total else 0.0
    verdict = "PASS" if failed == 0 and total > 0 else "BLOCKED"
    verdict_cls = "ok" if verdict == "PASS" else "bad"

    rows_html = []
    for r in results:
        st = html.escape(str(r.get("status", "UNKNOWN")))
        badge = "ok" if st == "PASSED" else "bad"
        thumb_html = ""
        shot = r.get("screenshot_data_uri")
        if isinstance(shot, str) and shot.startswith("data:image/"):
            thumb_html = (
                f"<div style='margin-top:6px;'>"
                f"<img src='{html.escape(shot)}' alt='Failure evidence' style='max-height:70px;border-radius:4px;border:1px solid #334155;' />"
                f"</div>"
            )
        rows_html.append(
            f"<tr>"
            f"<td class='mono'>{html.escape(str(r.get('layer', 'E2E')))}</td>"
            f"<td>{html.escape(str(r.get('name', '')))}</td>"
            f"<td><span class='badge {badge}'>{st}</span></td>"
            f"<td class='mono'>{float(r.get('duration_ms', 0.0)):.1f} ms</td>"
            f"<td class='muted'>{html.escape(str(r.get('detail', 'Contract & DOM assertions satisfied')))}{thumb_html}</td>"
            f"</tr>"
        )

    generated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    doc = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>QA-Pilot Sign-Off Report — {html.escape(suite_title)}</title>
  <style>
    :root {{ --bg:#0b0c10; --panel:#13161f; --border:#242938; --ok:#10b981; --bad:#f43f5e; --amber:#f59e0b; --text:#f4f4f5; --muted:#9ca3af; }}
    * {{ box-sizing:border-box; font-family:Inter,system-ui,sans-serif; }}
    body {{ margin:0; background:var(--bg); color:var(--text); padding:28px 36px; }}
    .hdr {{ display:flex; justify-content:space-between; align-items:flex-end; border-bottom:1px solid var(--border); padding-bottom:14px; margin-bottom:20px; }}
    h1 {{ margin:0; font-size:1.35rem; }}
    .sub {{ color:var(--muted); font-size:0.82rem; margin-top:4px; }}
    .verdict {{ padding:6px 14px; border-radius:6px; font-family:monospace; font-weight:700; font-size:0.9rem; }}
    .verdict.ok {{ background:rgba(16,185,129,0.14); color:#34d399; border:1px solid rgba(16,185,129,0.45); }}
    .verdict.bad {{ background:rgba(244,63,94,0.14); color:#fb7185; border:1px solid rgba(244,63,94,0.45); }}
    .kpis {{ display:grid; grid-template-columns:repeat(4,1fr); gap:14px; margin-bottom:20px; }}
    .kpi {{ background:var(--panel); border:1px solid var(--border); border-radius:10px; padding:14px 16px; }}
    .kpi .lbl {{ font-size:0.7rem; text-transform:uppercase; letter-spacing:0.06em; color:var(--muted); }}
    .kpi .val {{ font-size:1.5rem; font-weight:700; margin-top:4px; font-family:monospace; }}
    .card {{ background:var(--panel); border:1px solid var(--border); border-radius:10px; padding:16px; }}
    table {{ width:100%; border-collapse:collapse; font-size:0.84rem; }}
    th {{ text-align:left; font-size:0.72rem; text-transform:uppercase; letter-spacing:0.05em; color:var(--muted); border-bottom:1px solid var(--border); padding:8px 10px; }}
    td {{ border-bottom:1px solid #1b1f2d; padding:10px; vertical-align:middle; }}
    .mono {{ font-family:ui-monospace,monospace; font-size:0.78rem; color:#fde68a; }}
    .muted {{ color:var(--muted); font-size:0.8rem; }}
    .badge {{ display:inline-block; padding:2px 8px; border-radius:999px; font-family:monospace; font-size:0.72rem; font-weight:700; }}
    .badge.ok {{ background:rgba(16,185,129,0.16); color:#34d399; }}
    .badge.bad {{ background:rgba(244,63,94,0.16); color:#fb7185; }}
  </style>
</head>
<body>
  <div class="hdr">
    <div>
      <h1>QA-Pilot — Automated E2E &amp; Contract Verification</h1>
      <div class="sub">{html.escape(suite_title)} · Generated {generated}</div>
    </div>
    <div class="verdict {verdict_cls}">GATE: {verdict}</div>
  </div>
  <div class="kpis">
    <div class="kpi"><div class="lbl">Total Assertions</div><div class="val">{total}</div></div>
    <div class="kpi"><div class="lbl">Pass Rate</div><div class="val" style="color:#34d399;">{pass_rate}%</div></div>
    <div class="kpi"><div class="lbl">Failures</div><div class="val" style="color:{'#fb7185' if failed else '#34d399'};">{failed}</div></div>
    <div class="kpi"><div class="lbl">Avg Case Latency</div><div class="val" style="color:#fde68a;">{avg_ms}ms</div></div>
  </div>
  <div class="card">
    <table>
      <thead><tr><th>Layer</th><th>Test Case</th><th>Status</th><th>Latency</th><th>Verification Summary</th></tr></thead>
      <tbody>{"".join(rows_html)}</tbody>
    </table>
  </div>
</body>
</html>"""
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(doc, encoding="utf-8")
    return out


def ingest_cases_to_qa_telemetry(suite_name: str, build_ref: str, rows: list[dict], db_path: str | Path) -> int:
    """Persist QA-Pilot run outcomes directly into projects/qa-telemetry TelemetryStore."""
    qa_tel_dir = Path(__file__).resolve().parents[2] / "qa-telemetry"
    if str(qa_tel_dir) not in sys.path:
        sys.path.insert(0, str(qa_tel_dir))
    from qa_telemetry.ingestor import TelemetryStore

    store = TelemetryStore(db_path)
    cases = [
        {
            "classname": r.get("layer", "e2e"),
            "name": r.get("name", "test_case"),
            "outcome": "FAILED" if r.get("status") == "FAILED" else "PASSED",
            "duration_s": round(float(r.get("duration_ms", 0.0)) / 1000.0, 4),
            "failure_message": r.get("detail") if r.get("status") == "FAILED" else None,
        }
        for r in rows
    ]
    return store.record_run(suite_name, build_ref, cases)
