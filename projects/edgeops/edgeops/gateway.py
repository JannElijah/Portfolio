"""EdgeOps Reverse Proxy Gateway & Service Health HTTP Server."""

from __future__ import annotations

import json
import os
import threading
import time
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

from edgeops.config import load_nginx_audit, parse_nginx_conf
from edgeops.monitor import GatewayMetrics, SlidingWindowRateLimiter, probe_http_target

DEFAULT_CONF = Path(__file__).resolve().parents[1] / "nginx" / "edgeops.conf"
STATIC_HTML = Path(__file__).parent / "static" / "index.html"


def start_demo_upstreams() -> tuple[dict[str, str], list[ThreadingHTTPServer]]:
    """Spin up local upstream microservices (auth-api, dms-core, wafer-telemetry) on free ports."""
    routes: dict[str, str] = {}
    servers: list[ThreadingHTTPServer] = []
    service_payloads = {
        "auth-api": {"service": "auth-api", "role": "RBAC & JWT Authority", "uptime": "99.98%"},
        "dms-core": {"service": "dms-core", "role": "Document Workflow Queue", "uptime": "99.95%"},
        "wafer-api": {"service": "wafer-api", "role": "MCU Bench Telemetry", "uptime": "99.99%"},
    }

    for name, meta in service_payloads.items():
        body_bytes = json.dumps({"ok": True, **meta}).encode("utf-8")

        class UpstreamHandler(BaseHTTPRequestHandler):
            _payload = body_bytes

            def log_message(self, format: str, *args: Any) -> None:
                return

            def do_GET(self) -> None:
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(self._payload)))
                self.end_headers()
                self.wfile.write(self._payload)

        srv = ThreadingHTTPServer(("127.0.0.1", 0), UpstreamHandler)
        port = srv.server_address[1]
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        servers.append(srv)
        routes[name] = f"http://127.0.0.1:{port}"

    return routes, servers


def create_gateway_server(
    host: str = "127.0.0.1",
    port: int = 8000,
    upstream_routes: dict[str, str] | None = None,
    nginx_conf_path: str | Path | None = None,
    rate_limit_max: int = 40,
    rate_limit_window_s: float = 10.0,
) -> ThreadingHTTPServer:
    """Create the EdgeOps reverse proxy & SRE health console server."""
    conf_file = Path(nginx_conf_path) if nginx_conf_path else DEFAULT_CONF
    nginx_audit = load_nginx_audit(conf_file) if conf_file.exists() else parse_nginx_conf("")
    metrics = GatewayMetrics()
    limiter = SlidingWindowRateLimiter(max_requests=rate_limit_max, window_seconds=rate_limit_window_s)
    routes = dict(upstream_routes or {})

    class GatewayHandler(BaseHTTPRequestHandler):
        def log_message(self, format: str, *args: Any) -> None:
            return

        def _write_security_headers(self) -> None:
            self.send_header("X-Frame-Options", "SAMEORIGIN")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Referrer-Policy", "strict-origin-when-cross-origin")
            self.send_header("X-Edge-Proxy", "edgeops-gateway")

        def _send_json(self, status: int, body: dict, upstream_tag: str = "edgeops-self") -> None:
            encoded = json.dumps(body).encode("utf-8")
            self.send_response(status)
            self._write_security_headers()
            self.send_header("X-Proxy-Upstream", upstream_tag)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(encoded)))
            self.end_headers()
            self.wfile.write(encoded)

        def do_GET(self) -> None:
            t0 = time.perf_counter()
            client_ip = self.client_address[0] if self.client_address else "127.0.0.1"

            if self.path == "/healthz":
                elapsed = (time.perf_counter() - t0) * 1000.0
                metrics.record("GET", self.path, "edgeops-self", 200, elapsed)
                self._send_json(200, {"status": "ok", "proxy": "edgeops-gateway"})
                return

            if not limiter.allow(client_ip):
                elapsed = (time.perf_counter() - t0) * 1000.0
                metrics.record("GET", self.path, "rate-limiter", 429, elapsed)
                self._send_json(429, {"error": "Rate limit exceeded (nginx limit_req)"}, "rate-limiter")
                return

            if self.path == "/" or self.path == "/index.html":
                html_bytes = STATIC_HTML.read_bytes()
                self.send_response(200)
                self._write_security_headers()
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(html_bytes)))
                self.end_headers()
                self.wfile.write(html_bytes)
                return

            if self.path == "/api/overview":
                probes = [probe_http_target(name, url) for name, url in routes.items()]
                elapsed = (time.perf_counter() - t0) * 1000.0
                if metrics.total_requests == 0:
                    metrics.record("GET", "/proxy/auth-api", "auth-api", 200, 1.4)
                    metrics.record("GET", "/proxy/dms-core", "dms-core", 200, 1.8)
                    metrics.record("GET", "/proxy/wafer-api", "wafer-api", 200, 1.1)
                self._send_json(
                    200,
                    {
                        "metrics": metrics.summary(),
                        "upstreams": probes,
                        "nginx_audit": nginx_audit,
                    },
                )
                return

            if self.path == "/metrics":
                s = metrics.summary()
                lines = [
                    "# HELP edgeops_requests_total Total HTTP requests routed through EdgeOps",
                    "# TYPE edgeops_requests_total counter",
                    f"edgeops_requests_total {s['total_requests']}",
                    f"edgeops_rate_limited_total {s['rate_limited_429']}",
                    f"edgeops_p95_latency_ms {s['p95_ms']}",
                ]
                raw = ("\n".join(lines) + "\n").encode("utf-8")
                self.send_response(200)
                self._write_security_headers()
                self.send_header("Content-Type", "text/plain; version=0.0.4")
                self.send_header("Content-Length", str(len(raw)))
                self.end_headers()
                self.wfile.write(raw)
                return

            if self.path.startswith("/proxy/"):
                service_name = self.path.removeprefix("/proxy/").split("/", 1)[0]
                target_base = routes.get(service_name)
                if not target_base:
                    elapsed = (time.perf_counter() - t0) * 1000.0
                    metrics.record("GET", self.path, "unknown", 404, elapsed)
                    self._send_json(404, {"error": f"Unknown upstream service '{service_name}'"})
                    return
                try:
                    with urllib.request.urlopen(f"{target_base}/", timeout=2.0) as resp:
                        upstream_body = json.loads(resp.read().decode("utf-8"))
                        elapsed = (time.perf_counter() - t0) * 1000.0
                        metrics.record("GET", self.path, service_name, resp.status, elapsed)
                        self._send_json(
                            resp.status,
                            {"proxied_by": "edgeops-gateway", "upstream": service_name, "data": upstream_body},
                            upstream_tag=service_name,
                        )
                except (urllib.error.URLError, OSError):
                    elapsed = (time.perf_counter() - t0) * 1000.0
                    metrics.record("GET", self.path, service_name, 502, elapsed)
                    self._send_json(502, {"error": f"Bad Gateway: upstream '{service_name}' unavailable"}, service_name)
                return

            self._send_json(404, {"error": "Not found"})

        def do_POST(self) -> None:
            t0 = time.perf_counter()
            if self.path == "/api/simulate-burst":
                burst_limiter = SlidingWindowRateLimiter(max_requests=2, window_seconds=10.0)
                allowed = 0
                throttled = 0
                for _ in range(5):
                    elapsed = (time.perf_counter() - t0) * 1000.0
                    if burst_limiter.allow("burst-client"):
                        allowed += 1
                        metrics.record("GET", "/proxy/auth-api", "auth-api", 200, elapsed + 1.2)
                    else:
                        throttled += 1
                        metrics.record("GET", "/proxy/auth-api", "rate-limiter", 429, 0.2)
                self._send_json(200, {"allowed": allowed, "rate_limited_429": throttled})
                return
            self._send_json(404, {"error": "Not found"})

    return ThreadingHTTPServer((host, port), GatewayHandler)


if __name__ == "__main__":
    host = os.getenv("EDGEOPS_HOST", "127.0.0.1")
    port = int(os.getenv("EDGEOPS_PORT", "8000"))
    demo_routes, demo_upstreams = start_demo_upstreams()
    srv = create_gateway_server(host=host, port=port, upstream_routes=demo_routes)
    print(f"EdgeOps Reverse Proxy & Health Stack listening on http://{host}:{port}")
    try:
        srv.serve_forever()
    finally:
        for u in demo_upstreams:
            u.shutdown()
            u.server_close()
