"""HTML QA Sign-Off Report Renderer & QA-Telemetry Integration for QA-Pilot."""

from __future__ import annotations

import html
import math
import sys
from datetime import datetime, timezone
from pathlib import Path


def _p95(values: list[float]) -> float:
    if not values:
        return 0.0
    s = sorted(values)
    idx = min(len(s) - 1, math.ceil(0.95 * len(s)) - 1)
    return round(s[idx], 1)


def render_qa_report(suite_title: str, results: list[dict], out_path: str | Path) -> Path:
    """Render a dark-mode HTML QA report with SVG latency bar chart, SLO line, and layer filter pills."""
    total = len(results)
    passed = sum(1 for r in results if r.get("status") == "PASSED")
    failed = sum(1 for r in results if r.get("status") == "FAILED")
    pass_rate = round((passed / total) * 100, 1) if total else 0.0
    durations = [float(r.get("duration_ms", 0.0)) for r in results]
    avg_ms = round(sum(durations) / total, 1) if total else 0.0
    p95_ms = _p95(durations)
    verdict = "PASS" if failed == 0 and total > 0 else "BLOCKED"
    verdict_cls = "ok" if verdict == "PASS" else "bad"

    max_ms = max([260.0] + durations)
    svg_w, svg_h, pad = 640, 118, 12
    slo_y = svg_h - pad - (250.0 / max_ms) * (svg_h - pad * 2)
    bar_slot = (svg_w - pad * 2) / max(1, total)
    bars_svg = []
    for i, r in enumerate(results):
        d_ms = float(r.get("duration_ms", 0.0))
        bh = max(4.0, (d_ms / max_ms) * (svg_h - pad * 2))
        bw = max(12.0, min(42.0, bar_slot * 0.6))
        bx = pad + i * bar_slot + (bar_slot - bw) / 2.0
        by = svg_h - pad - bh
        col = "#f43f5e" if r.get("status") == "FAILED" else "#f59e0b" if d_ms > 250 else "#10b981"
        bars_svg.append(
            f"<rect x='{bx:.1f}' y='{by:.1f}' width='{bw:.1f}' height='{bh:.1f}' rx='3' fill='{col}' />"
        )

    rows_html = []
    for r in results:
        layer = str(r.get("layer", "E2E"))
        st = str(r.get("status", "UNKNOWN"))
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
            f"<tr data-layer='{html.escape(layer)}' data-status='{html.escape(st)}'>"
            f"<td class='mono'>{html.escape(layer)}</td>"
            f"<td>{html.escape(str(r.get('name', '')))}</td>"
            f"<td><span class='badge {badge}'>{html.escape(st)}</span></td>"
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
    :root {{ --bg:#090b10; --panel:#12151f; --border:#232838; --ok:#10b981; --bad:#f43f5e; --amber:#f59e0b; --text:#f4f4f5; --muted:#9ca3af; }}
    * {{ box-sizing:border-box; font-family:Inter,system-ui,sans-serif; }}
    body {{ margin:0; background:radial-gradient(960px 420px at 85% -10%, rgba(245,158,11,0.08), transparent), var(--bg); color:var(--text); padding:24px 30px; }}
    .hdr {{ display:flex; justify-content:space-between; align-items:flex-end; border-bottom:1px solid var(--border); padding-bottom:12px; margin-bottom:16px; }}
    h1 {{ margin:0; font-size:1.3rem; }}
    .sub {{ color:var(--muted); font-size:0.8rem; margin-top:4px; }}
    .verdict {{ padding:6px 13px; border-radius:6px; font-family:monospace; font-weight:700; font-size:0.86rem; }}
    .verdict.ok {{ background:rgba(16,185,129,0.14); color:#34d399; border:1px solid rgba(16,185,129,0.45); }}
    .verdict.bad {{ background:rgba(244,63,94,0.14); color:#fb7185; border:1px solid rgba(244,63,94,0.45); }}
    .kpis {{ display:grid; grid-template-columns:repeat(4,1fr); gap:12px; margin-bottom:16px; }}
    .kpi {{ background:var(--panel); border:1px solid var(--border); border-radius:9px; padding:12px 14px; }}
    .kpi .lbl {{ font-size:0.68rem; text-transform:uppercase; letter-spacing:0.06em; color:var(--muted); }}
    .kpi .val {{ font-size:1.35rem; font-weight:700; margin-top:4px; font-family:ui-monospace,monospace; }}
    .card {{ background:var(--panel); border:1px solid var(--border); border-radius:10px; padding:15px; margin-bottom:14px; }}
    .card-hdr {{ display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px; margin-bottom:10px; }}
    .pills {{ display:flex; gap:6px; flex-wrap:wrap; }}
    .fpill {{ background:#0b0e16; border:1px solid var(--border); color:var(--muted); padding:4px 10px; border-radius:999px; font-size:0.72rem; cursor:pointer; font-weight:600; }}
    .fpill.active {{ background:var(--amber); border-color:var(--amber); color:#18181b; }}
    table {{ width:100%; border-collapse:collapse; font-size:0.82rem; }}
    th {{ text-align:left; font-size:0.7rem; text-transform:uppercase; letter-spacing:0.05em; color:var(--muted); border-bottom:1px solid var(--border); padding:7px 9px; }}
    td {{ border-bottom:1px solid #1b1f2d; padding:8px 9px; vertical-align:middle; }}
    .mono {{ font-family:ui-monospace,monospace; font-size:0.77rem; color:#fde68a; }}
    .muted {{ color:var(--muted); font-size:0.79rem; }}
    .badge {{ display:inline-block; padding:2px 8px; border-radius:999px; font-family:monospace; font-size:0.71rem; font-weight:700; }}
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
    <div class="kpi"><div class="lbl">Avg Latency</div><div class="val" style="color:#fde68a;">{avg_ms}ms</div></div>
    <div class="kpi"><div class="lbl">p95 Latency</div><div class="val" style="color:#38bdf8;">{p95_ms}ms</div></div>
  </div>
  <div class="card">
    <div class="card-hdr">
      <strong style="font-size:0.9rem;">Per-Case Execution Latency vs. 250ms SLO</strong>
      <span class="mono" style="color:#fb7185;">--- 250ms API Contract Threshold</span>
    </div>
    <svg viewBox="0 0 {svg_w} {svg_h}" style="width:100%;height:{svg_h}px;background:#090b10;border:1px solid var(--border);border-radius:7px;">
      <line x1="{pad}" y1="{slo_y:.1f}" x2="{svg_w - pad}" y2="{slo_y:.1f}" stroke="#f43f5e" stroke-dasharray="5 3" stroke-width="1.2" />
      {"".join(bars_svg)}
    </svg>
  </div>
  <div class="card">
    <div class="card-hdr">
      <strong style="font-size:0.9rem;">Verification Matrix</strong>
      <div class="pills">
        <button class="fpill active" onclick="filterRows('ALL', this)">All ({total})</button>
        <button class="fpill" onclick="filterRows('E2E', this)">Playwright E2E</button>
        <button class="fpill" onclick="filterRows('API', this)">API Contracts</button>
        <button class="fpill" onclick="filterRows('FAILED', this)">Failures ({failed})</button>
      </div>
    </div>
    <table>
      <thead><tr><th>Layer</th><th>Test Case</th><th>Status</th><th>Latency</th><th>Verification Summary</th></tr></thead>
      <tbody>{"".join(rows_html)}</tbody>
    </table>
  </div>
<script>
function filterRows(mode, btn) {{
  document.querySelectorAll('.fpill').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  document.querySelectorAll('tbody tr').forEach(tr => {{
    const layer = (tr.dataset.layer || '').toLowerCase();
    const st = tr.dataset.status || '';
    const show = mode === 'ALL'
      || (mode === 'E2E' && layer.includes('e2e'))
      || (mode === 'API' && layer.includes('api'))
      || (mode === 'FAILED' && st === 'FAILED');
    tr.style.display = show ? '' : 'none';
  }});
}}
</script>
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
