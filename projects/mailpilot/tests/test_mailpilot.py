"""Automated tests for MailPilot AI triage, MIME parser, IMAP/SMTP audit, and HTTP console."""

from __future__ import annotations

import json
import threading
import urllib.request

from mailpilot.cli import main as cli_main
from mailpilot.config import parse_raw_email, validate_email_client_profile
from mailpilot.server import create_server


def test_imap_smtp_profile_validation_and_mime_parser(tmp_path) -> None:
    ok = validate_email_client_profile("ops@company.ph", "imap.gmail.com", 993, "smtp.gmail.com", 587, True)
    assert ok["valid"] is True and ok["tls_enforced"] is True

    bad = validate_email_client_profile("invalid", "", 143, "smtp.bad.local", 25, False)
    assert bad["valid"] is False and len(bad["issues"]) >= 3

    eml = tmp_path / "alert.eml"
    eml.write_text("From: client@acme.ph\nSubject: Urgent 502 error on website\n\nCheckout returns 502 timeout.", encoding="utf-8")
    parsed = parse_raw_email(eml.read_text(encoding="utf-8"))
    assert parsed["sender"] == "client@acme.ph"
    assert cli_main(["triage-eml", "--file", str(eml)]) == 0


def test_mailpilot_server_ingest_and_outbox_approval(tmp_path) -> None:
    srv = create_server(host="127.0.0.1", port=0, db_path=str(tmp_path / "mp.db"))
    port = srv.server_address[1]
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    try:
        req = urllib.request.Request(
            f"http://127.0.0.1:{port}/api/emails/ingest",
            data=json.dumps(
                {
                    "sender": "pm@makati-client.ph",
                    "subject": "Website maintenance update request",
                    "body": "Please fix broken footer link and landing page bug.",
                }
            ).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=3) as r1:
            created = json.loads(r1.read().decode("utf-8"))
        assert created["email"]["category"] == "Website Maintenance"
        msg_id = created["email"]["id"]

        app_req = urllib.request.Request(
            f"http://127.0.0.1:{port}/api/emails/{msg_id}/approve",
            data=json.dumps({"draft_reply": "Scheduled in GitHub staging branch now."}).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(app_req, timeout=3) as r2:
            approved = json.loads(r2.read().decode("utf-8"))
        assert approved["email"]["status"] == "SENT"
        assert approved["outbox_sent"] >= 1
    finally:
        srv.shutdown()
        srv.server_close()
