"""HTML SEO/Asset/Accessibility maintenance scanner, sitemap builder, and Git repository inspector."""

from __future__ import annotations

import html.parser
import subprocess
import urllib.parse
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path


class _HtmlLinkMetaParser(html.parser.HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.title: str = ""
        self._in_title = False
        self.meta: dict[str, str] = {}
        self.icon_href: str | None = None
        self.local_refs: list[str] = []
        self.images_total = 0
        self.images_missing_alt = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr_map = {k.lower(): (v or "") for k, v in attrs}
        if tag.lower() == "title":
            self._in_title = True
        elif tag.lower() == "meta":
            key = attr_map.get("name") or attr_map.get("property")
            if key and attr_map.get("content"):
                self.meta[key.lower()] = attr_map["content"]
        elif tag.lower() == "link":
            rel = attr_map.get("rel", "").lower()
            href = attr_map.get("href", "")
            if "icon" in rel and href:
                self.icon_href = href
            if href and not href.startswith(("http://", "https://", "data:", "#")):
                self.local_refs.append(href)
        elif tag.lower() == "script" and attr_map.get("src"):
            src = attr_map["src"]
            if not src.startswith(("http://", "https://")):
                self.local_refs.append(src)
        elif tag.lower() == "img":
            self.images_total += 1
            if "alt" not in attr_map or not attr_map["alt"].strip():
                self.images_missing_alt += 1
            src = attr_map.get("src", "")
            if src and not src.startswith(("http://", "https://", "data:")):
                self.local_refs.append(src)

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "title":
            self._in_title = False

    def handle_data(self, data: str) -> None:
        if self._in_title:
            self.title += data


def audit_static_site(site_root: str | Path, public_root: str | Path | None = None) -> dict:
    """Audit built index.html + static assets for broken references, SEO/OG metadata, and alt coverage."""
    site_path = Path(site_root)
    public_path = Path(public_root) if public_root else site_path
    index_file = site_path / "index.html"
    if not index_file.exists():
        raise FileNotFoundError(f"index.html not found under {site_path}")

    parser = _HtmlLinkMetaParser()
    parser.feed(index_file.read_text(encoding="utf-8"))

    broken_assets: list[str] = []
    verified_assets: list[str] = []
    for ref in parser.local_refs:
        clean_ref = urllib.parse.urlparse(ref).path.lstrip("/")
        if (site_path / clean_ref).exists() or (public_path / clean_ref).exists():
            verified_assets.append(ref)
        else:
            broken_assets.append(ref)

    checks = [
        {"check": "HTML <title> Tag Present", "passed": bool(parser.title.strip()), "detail": parser.title.strip() or "Missing"},
        {"check": "Meta Description Present", "passed": "description" in parser.meta, "detail": f"{len(parser.meta.get('description', ''))} chars"},
        {"check": "Open Graph (og:title & og:image)", "passed": "og:title" in parser.meta and "og:image" in parser.meta, "detail": parser.meta.get("og:image", "Missing")},
        {"check": "Favicon Link Configured", "passed": bool(parser.icon_href), "detail": parser.icon_href or "Missing"},
        {"check": "Zero Broken Local Asset Refs", "passed": len(broken_assets) == 0, "detail": f"{len(verified_assets)} verified, {len(broken_assets)} broken"},
        {"check": "Image Alt Text Compliance", "passed": parser.images_missing_alt == 0, "detail": f"{parser.images_total} imgs checked"},
    ]
    score = round(sum(1 for c in checks if c["passed"]) / len(checks) * 100)
    return {
        "site_root": str(site_path),
        "health_score": score,
        "broken_assets": broken_assets,
        "verified_assets": verified_assets,
        "checks": checks,
    }


def generate_sitemap_xml(base_url: str, routes: list[str]) -> str:
    """Build valid XML sitemap string for the given base URL and relative routes."""
    urlset = ET.Element("urlset", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    base = base_url.rstrip("/")
    for r in routes:
        url_el = ET.SubElement(urlset, "url")
        loc = ET.SubElement(url_el, "loc")
        loc.text = f"{base}/{r.lstrip('/')}" if r != "/" else f"{base}/"
        lastmod = ET.SubElement(url_el, "lastmod")
        lastmod.text = today
    ET.indent(urlset, space="  ")
    return '<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(urlset, encoding="unicode")


def inspect_github_workflows_and_git(repo_root: str | Path) -> dict:
    """Inspect .github/workflows CI files and Git branch/commit log cleanly."""
    root = Path(repo_root)
    workflows_dir = root / ".github" / "workflows"
    workflow_files = [f.name for f in sorted(workflows_dir.glob("*.yml"))] if workflows_dir.exists() else []

    branch = "main"
    commits: list[str] = []
    try:
        b = subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=root, capture_output=True, text=True, timeout=3)
        if b.returncode == 0 and b.stdout.strip():
            branch = b.stdout.strip()
        lg = subprocess.run(["git", "log", "-n", "5", "--oneline"], cwd=root, capture_output=True, text=True, timeout=3)
        if lg.returncode == 0 and lg.stdout.strip():
            commits = lg.stdout.strip().splitlines()
    except (OSError, subprocess.SubprocessError):
        pass

    return {
        "repo_root": str(root),
        "branch": branch,
        "workflow_files": workflow_files,
        "recent_commits": commits,
        "ci_configured": len(workflow_files) > 0,
    }
