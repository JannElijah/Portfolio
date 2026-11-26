"""Pytest fixtures launching an isolated live UPHSD-DMS instance + Playwright page."""

from __future__ import annotations

import sys
import threading
import time
from pathlib import Path

import pytest
from playwright.sync_api import sync_playwright

PROJECTS_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECTS_ROOT / "uphsd-dms"))

from dms.server import create_server  # noqa: E402


@pytest.fixture(scope="session")
def live_dms_url(tmp_path_factory: pytest.TempPathFactory) -> str:
    tmp_dir = tmp_path_factory.mktemp("qa_pilot_dms")
    server = create_server(host="127.0.0.1", port=0, db_path=str(tmp_dir / "dms.db"))
    port = server.server_address[1]
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    time.sleep(0.2)
    try:
        yield f"http://127.0.0.1:{port}"
    finally:
        server.shutdown()
        server.server_close()


@pytest.fixture()
def browser_page():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1280, "height": 720})
        page = context.new_page()
        yield page
        browser.close()
