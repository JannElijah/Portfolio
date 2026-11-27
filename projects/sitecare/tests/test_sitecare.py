"""Automated tests for SiteCare HTML audit, asset checking, sitemap generation, and web server."""

from __future__ import annotations

import json
import threading
import urllib.request

from sitecare.auditor import audit_static_site, generate_sitemap_xml, inspect_github_workflows_and_git
from sitecare.cli import main as cli_main
from sitecare.server import create_server


def test_audit_static_site_and_sitemap(tmp_path) -> None:
    site = tmp_path / "dist"
    site.mkdir()
    (site / "favicon.svg").write_text("<svg></svg>", encoding="utf-8")
    (site / "banner.png").write_bytes(b"PNG")
    (site / "index.html").write_text(
        """<!doctype html><html><head>
        <title>Test Portal</title>
        <link rel="icon" href="/favicon.svg" />
        <meta name="description" content="Sample site" />
        <meta property="og:title" content="Test Portal" />
        <meta property="og:image" content="/banner.png" />
        </head><body><img src="/banner.png" alt="Banner preview" /></body></html>""",
        encoding="utf-8",
    )

    res = audit_static_site(site)
    assert res["health_score"] == 100
    assert res["broken_assets"] == []

    xml_out = generate_sitemap_xml("https://example.com", ["/", "/#projects"])
    assert "<loc>https://example.com/</loc>" in xml_out
    assert "<loc>https://example.com/#projects</loc>" in xml_out
    assert cli_main(["audit", "--site-dir", str(site)]) == 0


def test_sitecare_server_and_git_ci_endpoint(tmp_path) -> None:
    site = tmp_path / "dist"
    site.mkdir()
    (site / "index.html").write_text("<title>Demo</title>", encoding="utf-8")
    wf = tmp_path / ".github" / "workflows"
    wf.mkdir(parents=True)
    (wf / "ci.yml").write_text("name: CI\n", encoding="utf-8")

    git_info = inspect_github_workflows_and_git(tmp_path)
    assert git_info["ci_configured"] is True and "ci.yml" in git_info["workflow_files"]

    srv = create_server(host="127.0.0.1", port=0, site_root=site, repo_root=tmp_path)
    port = srv.server_address[1]
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/api/audit", timeout=3) as r:
            payload = json.loads(r.read().decode("utf-8"))
        assert payload["git_ci"]["ci_configured"] is True
        assert "<urlset" in payload["sitemap_xml"]

        with urllib.request.urlopen(f"http://127.0.0.1:{port}/api/sitemap.xml?base_url=https://example.org", timeout=3) as r_xml:
            assert r_xml.status == 200
            assert "application/xml" in r_xml.headers.get("Content-Type", "")
            xml_body = r_xml.read().decode("utf-8")
        assert "<loc>https://example.org/</loc>" in xml_body
    finally:
        srv.shutdown()
        srv.server_close()
