"""Automated tests for EdgeOps Nginx parser, reverse-proxy forwarding, headers, and rate limits."""

from __future__ import annotations

import json
import threading
import urllib.error
import urllib.request
from pathlib import Path

from edgeops.config import load_nginx_audit
from edgeops.gateway import create_gateway_server, start_demo_upstreams


def _get(url: str) -> tuple[int, dict[str, str], str]:
    try:
        with urllib.request.urlopen(url, timeout=4) as resp:
            return resp.status, dict(resp.headers), resp.read().decode("utf-8")
    except urllib.error.HTTPError as err:
        return err.code, dict(err.headers), err.read().decode("utf-8")


def test_nginx_conf_security_and_rate_limit_audit() -> None:
    conf_path = Path(__file__).resolve().parents[1] / "nginx" / "edgeops.conf"
    audit = load_nginx_audit(conf_path)
    assert audit["compliant"] is True
    assert "edgeops-gateway:8000" in audit["upstreams"]
    assert "/healthz" in audit["locations"]
    assert audit["security_headers"]["X-Frame-Options"] == "SAMEORIGIN"


def test_reverse_proxy_headers_health_and_down_upstream() -> None:
    routes, upstream_servers = start_demo_upstreams()
    routes["offline-svc"] = "http://127.0.0.1:59999"
    srv = create_gateway_server(host="127.0.0.1", port=0, upstream_routes=routes, rate_limit_max=25)
    port = srv.server_address[1]
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    try:
        st, hdrs, body = _get(f"http://127.0.0.1:{port}/proxy/auth-api")
        assert st == 200
        assert hdrs["X-Frame-Options"] == "SAMEORIGIN"
        assert hdrs["X-Proxy-Upstream"] == "auth-api"
        parsed = json.loads(body)
        assert parsed["proxied_by"] == "edgeops-gateway"
        assert parsed["data"]["service"] == "auth-api"

        st_ov, _, ov_body = _get(f"http://127.0.0.1:{port}/api/overview")
        assert st_ov == 200
        overview = json.loads(ov_body)
        by_name = {u["service"]: u for u in overview["upstreams"]}
        assert by_name["auth-api"]["status"] == "UP"
        assert by_name["offline-svc"]["status"] == "DOWN"

        st_metrics, _, metrics_txt = _get(f"http://127.0.0.1:{port}/metrics")
        assert st_metrics == 200
        assert "edgeops_requests_total" in metrics_txt

        # Verify burst simulator triggers 429 metrics cleanly
        req_burst = urllib.request.Request(f"http://127.0.0.1:{port}/api/simulate-burst", data=b"{}", method="POST")
        with urllib.request.urlopen(req_burst, timeout=3) as b_resp:
            burst = json.loads(b_resp.read().decode("utf-8"))
        assert burst["allowed"] == 2 and burst["rate_limited_429"] == 3
    finally:
        srv.shutdown()
        srv.server_close()
        for u in upstream_servers:
            u.shutdown()
            u.server_close()


def test_rate_limiter_returns_429_after_burst() -> None:
    routes, upstream_servers = start_demo_upstreams()
    srv = create_gateway_server(
        host="127.0.0.1",
        port=0,
        upstream_routes=routes,
        rate_limit_max=2,
        rate_limit_window_s=60.0,
    )
    port = srv.server_address[1]
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    try:
        assert _get(f"http://127.0.0.1:{port}/proxy/auth-api")[0] == 200
        assert _get(f"http://127.0.0.1:{port}/proxy/dms-core")[0] == 200
        st3, _, body3 = _get(f"http://127.0.0.1:{port}/proxy/wafer-api")
        assert st3 == 429
        assert "Rate limit" in body3
    finally:
        srv.shutdown()
        srv.server_close()
        for u in upstream_servers:
            u.shutdown()
            u.server_close()
