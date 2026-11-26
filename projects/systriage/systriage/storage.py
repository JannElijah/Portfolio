"""SQLite relational persistence layer for IT helpdesk tickets and snapshots."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

VALID_PRIORITIES = {"P1", "P2", "P3"}
VALID_STATUSES = {"OPEN", "IN_PROGRESS", "RESOLVED"}


class TriageStore:
    """Manages helpdesk incident tickets linked to diagnostic snapshots."""

    def __init__(self, db_path: str | Path = "systriage.db") -> None:
        self.db_path = str(db_path)
        self._init_schema()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def _init_schema(self) -> None:
        with self._connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS diagnostic_snapshots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    hostname TEXT NOT NULL,
                    overall_status TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS tickets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    category TEXT NOT NULL,
                    priority TEXT NOT NULL CHECK(priority IN ('P1', 'P2', 'P3')),
                    status TEXT NOT NULL CHECK(status IN ('OPEN', 'IN_PROGRESS', 'RESOLVED')),
                    assignee TEXT NOT NULL,
                    resolution_notes TEXT,
                    snapshot_id INTEGER REFERENCES diagnostic_snapshots(id) ON DELETE SET NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                """
            )

    def save_snapshot(self, diagnostic: dict) -> int:
        """Persist a diagnostic telemetry payload and return its snapshot ID."""
        now = datetime.now(timezone.utc).isoformat()
        hostname = diagnostic.get("host", {}).get("hostname", "unknown")
        status = diagnostic.get("overall_status", "UNKNOWN")
        with self._connect() as conn:
            cur = conn.execute(
                """
                INSERT INTO diagnostic_snapshots (hostname, overall_status, payload_json, created_at)
                VALUES (?, ?, ?, ?)
                """,
                (hostname, status, json.dumps(diagnostic), now),
            )
            return int(cur.lastrowid)

    def create_ticket(
        self,
        title: str,
        category: str = "Endpoint",
        priority: str = "P3",
        assignee: str = "Unassigned",
        snapshot_id: int | None = None,
    ) -> dict:
        """Create a validated helpdesk triage ticket."""
        clean_title = title.strip()
        if not clean_title:
            raise ValueError("Ticket title cannot be empty.")
        if priority not in VALID_PRIORITIES:
            raise ValueError(f"Priority must be one of {sorted(VALID_PRIORITIES)}.")

        now = datetime.now(timezone.utc).isoformat()
        with self._connect() as conn:
            cur = conn.execute(
                """
                INSERT INTO tickets (
                    title, category, priority, status, assignee, snapshot_id, created_at, updated_at
                )
                VALUES (?, ?, ?, 'OPEN', ?, ?, ?, ?)
                """,
                (clean_title, category.strip() or "Endpoint", priority, assignee.strip() or "Unassigned", snapshot_id, now, now),
            )
            ticket_id = int(cur.lastrowid)
        return self.get_ticket(ticket_id)

    def get_ticket(self, ticket_id: int) -> dict | None:
        """Retrieve a single ticket by ID with optional snapshot summary."""
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT t.*, s.hostname AS snapshot_hostname, s.overall_status AS snapshot_status
                FROM tickets t
                LEFT JOIN diagnostic_snapshots s ON t.snapshot_id = s.id
                WHERE t.id = ?
                """,
                (ticket_id,),
            ).fetchone()
        return dict(row) if row else None

    def list_tickets(self, status: str | None = None) -> list[dict]:
        """List tickets ordered newest-first, optionally filtered by status."""
        if status and status not in VALID_STATUSES:
            raise ValueError(f"Status must be one of {sorted(VALID_STATUSES)}.")

        query = """
            SELECT t.*, s.hostname AS snapshot_hostname, s.overall_status AS snapshot_status
            FROM tickets t
            LEFT JOIN diagnostic_snapshots s ON t.snapshot_id = s.id
        """
        params: tuple = ()
        if status:
            query += " WHERE t.status = ?"
            params = (status,)
        query += " ORDER BY t.id DESC"

        with self._connect() as conn:
            rows = conn.execute(query, params).fetchall()
        return [dict(r) for r in rows]

    def update_ticket_status(self, ticket_id: int, status: str, resolution_notes: str | None = None) -> dict:
        """Transition ticket status and record optional resolution notes."""
        if status not in VALID_STATUSES:
            raise ValueError(f"Status must be one of {sorted(VALID_STATUSES)}.")

        now = datetime.now(timezone.utc).isoformat()
        with self._connect() as conn:
            cur = conn.execute(
                """
                UPDATE tickets
                SET status = ?,
                    resolution_notes = COALESCE(?, resolution_notes),
                    updated_at = ?
                WHERE id = ?
                """,
                (status, resolution_notes, now, ticket_id),
            )
            if cur.rowcount == 0:
                raise LookupError(f"Ticket #{ticket_id} does not exist.")
        return self.get_ticket(ticket_id)
