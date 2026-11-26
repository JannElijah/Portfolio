"""HTTP REST API and web UI server for UPHSD Document Management System."""

from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse

from dms.store import DocumentStore

STATIC_HTML = Path(__file__).parent / "static" / "index.html"


def create_server(host: str = "127.0.0.1", port: int = 8610, db_path: str = "uphsd_dms.db") -> ThreadingHTTPServer:
    store = DocumentStore(db_path)

    class DmsHandler(BaseHTTPRequestHandler):
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
            if parsed.path == "/" or parsed.path == "/index.html":
                html_bytes = STATIC_HTML.read_bytes()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(html_bytes)))
                self.end_headers()
                self.wfile.write(html_bytes)
                return

            if parsed.path == "/api/documents":
                qs = parse_qs(parsed.query)
                status = qs.get("status", [None])[0]
                dept = qs.get("department", [None])[0]
                docs = store.list_documents(status=status, department=dept)
                self._send_json(200, {"documents": docs})
                return

            if parsed.path.startswith("/api/documents/"):
                try:
                    doc_id = int(parsed.path.split("/")[3])
                    doc = store.get_document(doc_id)
                    if not doc:
                        self._send_json(404, {"error": "Document not found"})
                    else:
                        self._send_json(200, {"document": doc})
                except (ValueError, IndexError):
                    self._send_json(400, {"error": "Invalid document ID"})
                return

            self._send_json(404, {"error": "Not found"})

        def do_POST(self) -> None:
            if self.path == "/api/documents":
                try:
                    data = self._read_json()
                    doc = store.create_document(
                        title=data.get("title", ""),
                        department=data.get("department", "CCS"),
                        submitted_by=data.get("submitted_by", "Student"),
                        remarks=data.get("remarks", ""),
                    )
                    self._send_json(201, {"document": doc})
                except ValueError as exc:
                    self._send_json(400, {"error": str(exc)})
                return
            self._send_json(404, {"error": "Not found"})

        def do_PATCH(self) -> None:
            if self.path.startswith("/api/documents/") and self.path.endswith("/transition"):
                try:
                    doc_id = int(self.path.split("/")[3])
                    data = self._read_json()
                    updated = store.transition_document(
                        doc_id=doc_id,
                        to_status=data.get("to_status", ""),
                        actor=data.get("actor", "Reviewer"),
                        role=data.get("role", "STAFF"),
                        note=data.get("note", ""),
                    )
                    self._send_json(200, {"document": updated})
                except PermissionError as exc:
                    self._send_json(403, {"error": str(exc)})
                except (ValueError, LookupError, IndexError) as exc:
                    self._send_json(400, {"error": str(exc)})
                return
            self._send_json(404, {"error": "Not found"})

    return ThreadingHTTPServer((host, port), DmsHandler)


if __name__ == "__main__":
    srv = create_server()
    print("UPHSD DMS running on http://127.0.0.1:8610")
    srv.serve_forever()
