"""HTTP Web Console & API Server for MailPilot AI."""

from __future__ import annotations

import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse

from mailpilot.config import validate_email_client_profile
from mailpilot.store import MailStore

STATIC_HTML = Path(__file__).parent / "static" / "index.html"


def create_server(
    host: str = "127.0.0.1",
    port: int = 8640,
    db_path: str = "mailpilot.db",
) -> ThreadingHTTPServer:
    store = MailStore(db_path)

    class MailHandler(BaseHTTPRequestHandler):
        def log_message(self, format: str, *args: Any) -> None:
            return

        def _send_json(self, status: int, body: dict) -> None:
            encoded = json.dumps(body).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(encoded)))
            self.end_headers()
            self.wfile.write(encoded)

        def _read_json(self) -> dict:
            length = int(self.headers.get("Content-Length", "0"))
            raw = self.rfile.read(length) if length > 0 else b"{}"
            return json.loads(raw.decode("utf-8"))

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

            if parsed.path == "/api/emails":
                qs = parse_qs(parsed.query)
                category = qs.get("category", [None])[0]
                emails = store.list_emails(category=category)
                self._send_json(200, {"emails": emails, "outbox_sent": store.outbox_count()})
                return

            if parsed.path == "/api/outbox":
                self._send_json(200, {"outbox": store.list_outbox()})
                return

            self._send_json(404, {"error": "Not found"})

        def do_POST(self) -> None:
            if self.path == "/api/emails/ingest":
                try:
                    data = self._read_json()
                    msg = store.ingest_email(
                        sender=data.get("sender", "client@example.com"),
                        subject=data.get("subject", ""),
                        body=data.get("body", ""),
                        gemini_api_key=os.getenv("GEMINI_API_KEY"),
                    )
                    self._send_json(201, {"email": msg})
                except ValueError as exc:
                    self._send_json(400, {"error": str(exc)})
                return

            if self.path.startswith("/api/emails/") and self.path.endswith("/approve"):
                try:
                    msg_id = int(self.path.split("/")[3])
                    data = self._read_json()
                    updated = store.approve_and_send(
                        msg_id=msg_id,
                        final_body=data.get("draft_reply", ""),
                        approved_by=data.get("approved_by", "Jann Limpiado"),
                    )
                    self._send_json(200, {"email": updated, "outbox_sent": store.outbox_count()})
                except (ValueError, LookupError, IndexError) as exc:
                    self._send_json(400, {"error": str(exc)})
                return

            if self.path == "/api/config/validate":
                data = self._read_json()
                res = validate_email_client_profile(
                    email_address=data.get("email", ""),
                    imap_host=data.get("imap_host", ""),
                    imap_port=int(data.get("imap_port", 993)),
                    smtp_host=data.get("smtp_host", ""),
                    smtp_port=int(data.get("smtp_port", 587)),
                    use_tls=bool(data.get("use_tls", True)),
                )
                self._send_json(200, res)
                return

            self._send_json(404, {"error": "Not found"})

    return ThreadingHTTPServer((host, port), MailHandler)


if __name__ == "__main__":
    srv = create_server()
    print("MailPilot AI Console running on http://127.0.0.1:8640")
    srv.serve_forever()
