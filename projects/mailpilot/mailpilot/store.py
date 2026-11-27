"""SQLite persistence for triaged inbox messages and approved outbox logs."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from mailpilot.classifier import classify_and_draft


class MailStore:
    def __init__(self, db_path: str | Path = "mailpilot.db") -> None:
        self.db_path = str(db_path)
        self._init_schema()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_schema(self) -> None:
        with self._connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS inbox_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sender TEXT NOT NULL,
                    subject TEXT NOT NULL,
                    body TEXT NOT NULL,
                    category TEXT NOT NULL,
                    priority TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    engine TEXT NOT NULL,
                    action_items_json TEXT NOT NULL,
                    draft_reply TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'PENDING_REVIEW',
                    received_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS outbox_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    inbox_id INTEGER NOT NULL,
                    recipient TEXT NOT NULL,
                    subject TEXT NOT NULL,
                    sent_body TEXT NOT NULL,
                    approved_by TEXT NOT NULL,
                    sent_at TEXT NOT NULL
                );
                """
            )
            count = conn.execute("SELECT COUNT(*) FROM inbox_messages").fetchone()[0]
            if count == 0:
                seeds = [
                    (
                        "ops@clientportal.ph",
                        "Urgent: 502 Bad Gateway on staging checkout page",
                        "Hi team, our staging Nginx route started returning 502 timeouts after this morning's push. Please inspect immediately.",
                    ),
                    (
                        "marketing@partner.ph",
                        "Website maintenance: update hero banner & broken footer link",
                        "Could we schedule an update to refresh our product landing page SSL check and broken FAQ route?",
                    ),
                    (
                        "accounting@vendor.ph",
                        "Invoice #INV-2026-884 for Q4 cloud server renewal",
                        "Attached is the billing quote and payment reference for server hosting renewal due Friday.",
                    ),
                    (
                        "talent@techcorp-makati.ph",
                        "Engineering Internship Screening – Python & Web Automation Track",
                        "Following up on Python automation, website maintenance, and AI email workflow demos prior to screening.",
                    ),
                ]
                for sender, subject, body in seeds:
                    self.ingest_email(sender=sender, subject=subject, body=body)

    def ingest_email(self, sender: str, subject: str, body: str, gemini_api_key: str | None = None) -> dict:
        if not subject.strip():
            raise ValueError("Subject cannot be empty.")
        triage = classify_and_draft(subject=subject.strip(), body=body.strip(), sender=sender.strip(), gemini_api_key=gemini_api_key)
        now = datetime.now(timezone.utc).isoformat()
        with self._connect() as conn:
            cur = conn.execute(
                """
                INSERT INTO inbox_messages (
                    sender, subject, body, category, priority, confidence, engine, action_items_json, draft_reply, status, received_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'PENDING_REVIEW', ?)
                """,
                (
                    sender.strip(),
                    subject.strip(),
                    body.strip(),
                    triage["category"],
                    triage["priority"],
                    float(triage["confidence"]),
                    triage["engine"],
                    json.dumps(triage["action_items"]),
                    triage["draft_reply"],
                    now,
                ),
            )
            msg_id = int(cur.lastrowid)
        return self.get_email(msg_id)

    def get_email(self, msg_id: int) -> dict | None:
        with self._connect() as conn:
            row = conn.execute("SELECT * FROM inbox_messages WHERE id = ?", (msg_id,)).fetchone()
        if not row:
            return None
        d = dict(row)
        d["action_items"] = json.loads(d.pop("action_items_json"))
        return d

    def list_emails(self, category: str | None = None) -> list[dict]:
        query = "SELECT * FROM inbox_messages"
        params: list[str] = []
        if category:
            query += " WHERE category = ?"
            params.append(category)
        query += " ORDER BY id DESC"
        with self._connect() as conn:
            rows = conn.execute(query, params).fetchall()
        results = []
        for r in rows:
            d = dict(r)
            d["action_items"] = json.loads(d.pop("action_items_json"))
            results.append(d)
        return results

    def approve_and_send(self, msg_id: int, final_body: str, approved_by: str = "Jann Limpiado") -> dict:
        msg = self.get_email(msg_id)
        if not msg:
            raise LookupError(f"Message #{msg_id} not found.")
        clean_reply = final_body.strip()
        if not clean_reply:
            raise ValueError("Reply body cannot be empty.")
        now = datetime.now(timezone.utc).isoformat()
        with self._connect() as conn:
            conn.execute(
                "UPDATE inbox_messages SET draft_reply = ?, status = 'SENT' WHERE id = ?",
                (clean_reply, msg_id),
            )
            conn.execute(
                "INSERT INTO outbox_log (inbox_id, recipient, subject, sent_body, approved_by, sent_at) VALUES (?, ?, ?, ?, ?, ?)",
                (msg_id, msg["sender"], f"Re: {msg['subject']}", clean_reply, approved_by, now),
            )
        return self.get_email(msg_id)

    def outbox_count(self) -> int:
        with self._connect() as conn:
            return int(conn.execute("SELECT COUNT(*) FROM outbox_log").fetchone()[0])

    def list_outbox(self) -> list[dict]:
        with self._connect() as conn:
            rows = conn.execute("SELECT * FROM outbox_log ORDER BY id DESC").fetchall()
        return [dict(r) for r in rows]
