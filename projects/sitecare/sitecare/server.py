"""HTTP Web Dashboard & API server for SiteCare Website Maintenance & GitHub CI."""

from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse

from sitecare.auditor import audit_static_site, generate_sitemap_xml, inspect_github_workflows_and_git

STATIC_HTML = Path(__file__).parent / "static" / "index.html"
DEFAULT_WORKSPACE = Path(__file__).resolve().parents[3]
DEFAULT_BASE_URL = "https://jann-limpiado-portfolio.vercel.app"
SITEMAP_ROUTES = ["/", "/#projects", "/#additional-work", "/#skills", "/#credentials"]


def create_server(
    host: str = "127.0.0.1",
    port: int = 8650,
    site_root: str | Path | None = None,
    repo_root: str | Path | None = None,
) -> ThreadingHTTPServer:
    target_repo = Path(repo_root) if repo_root else DEFAULT_WORKSPACE
    dist_dir = Path(site_root) if site_root else (target_repo / "dist")
    if not (dist_dir / "index.html").exists():
        dist_dir = target_repo

    class SiteCareHandler(BaseHTTPRequestHandler):
        def log_message(self, format: str, *args: Any) -> None:
            return

        def _send_json(self, status: int, body: dict) -> None:
            encoded = json.dumps(body).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(encoded)))
            self.end_headers()
            self.wfile.write(encoded)

        def _resolve_base_url(self, query: str) -> str:
            qs = parse_qs(query)
            candidate = (qs.get("base_url", [DEFAULT_BASE_URL])[0] or "").strip()
            return candidate if candidate.startswith(("http://", "https://")) else DEFAULT_BASE_URL

        def do_GET(self) -> None:
            parsed = urlparse(self.path)
            if parsed.path in {"/", "/index.html"}:
                html_bytes = STATIC_HTML.read_bytes()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(html_bytes)))
                self.end_headers()
                self.wfile.write(html_bytes)
                return

            if parsed.path == "/api/audit":
                base_url = self._resolve_base_url(parsed.query)
                audit = audit_static_site(dist_dir, target_repo / "public")
                git_info = inspect_github_workflows_and_git(target_repo)
                sitemap = generate_sitemap_xml(base_url, SITEMAP_ROUTES)
                self._send_json(200, {"audit": audit, "git_ci": git_info, "sitemap_xml": sitemap, "base_url": base_url})
                return

            if parsed.path == "/api/sitemap.xml":
                base_url = self._resolve_base_url(parsed.query)
                xml_bytes = generate_sitemap_xml(base_url, SITEMAP_ROUTES).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/xml; charset=utf-8")
                self.send_header("Content-Disposition", "attachment; filename=sitemap.xml")
                self.send_header("Content-Length", str(len(xml_bytes)))
                self.end_headers()
                self.wfile.write(xml_bytes)
                return

            self._send_json(404, {"error": "Not found"})

    return ThreadingHTTPServer((host, port), SiteCareHandler)


if __name__ == "__main__":
    srv = create_server()
    print("SiteCare Maintenance Console running on http://127.0.0.1:8650")
    srv.serve_forever()
