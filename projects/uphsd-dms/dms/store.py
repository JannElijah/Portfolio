"""SQLite workflow state machine and audit trail for UPHSD Document Management System."""

from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path

VALID_STATUSES = {"SUBMITTED", "IN_REVIEW", "APPROVED", "RETURNED"}
REVIEWER_ROLES = {"DEAN", "ADMIN", "REGISTRAR"}


class DocumentStore:
    def __init__(self, db_path: str | Path = "uphsd_dms.db") -> None:
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
                CREATE TABLE IF NOT EXISTS documents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ref_code TEXT NOT NULL UNIQUE,
                    title TEXT NOT NULL,
                    department TEXT NOT NULL,
                    submitted_by TEXT NOT NULL,
                    status TEXT NOT NULL CHECK(status IN ('SUBMITTED', 'IN_REVIEW', 'APPROVED', 'RETURNED')),
                    remarks TEXT,
                    updated_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS document_audit (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    document_id INTEGER NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
                    actor TEXT NOT NULL,
                    role TEXT NOT NULL,
                    from_status TEXT,
                    to_status TEXT NOT NULL,
                    note TEXT,
                    created_at TEXT NOT NULL
                );
                """
            )
            count = conn.execute("SELECT COUNT(*) FROM documents").fetchone()[0]
            if count == 0:
                now = datetime.now(timezone.utc).isoformat()
                seeds = [
                    ("DOC-2026-042", "OJT Industry Endorsement Letter", "CCS", "Jann Limpiado", "IN_REVIEW", "Pending Dean endorsement", now),
                    ("CAP-2026-019", "Capstone Defense Clearance Form", "CCS", "Team Torvalds", "APPROVED", "Signed by Capstone Chair", now),
                    ("LAB-2026-008", "Cisco Lab Switch Request", "IT Lab", "Lab Tech", "SUBMITTED", "Awaiting queue triage", now),
                    ("MOU-2026-014", "Enterprise OJT Partner MOU", "Registrar", "External Linkages", "APPROVED", "Archived in vault", now),
                ]
                conn.executemany(
                    "INSERT INTO documents (ref_code, title, department, submitted_by, status, remarks, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    seeds,
                )

    def list_documents(self, status: str | None = None, department: str | None = None) -> list[dict]:
        query = "SELECT * FROM documents WHERE 1=1"
        params: list[str] = []
        if status:
            query += " AND status = ?"
            params.append(status)
        if department:
            query += " AND department = ?"
            params.append(department)
        query += " ORDER BY id DESC"
        with self._connect() as conn:
            rows = conn.execute(query, params).fetchall()
        return [dict(r) for r in rows]

    def create_document(self, title: str, department: str, submitted_by: str, remarks: str = "") -> dict:
        clean_title = title.strip()
        if not clean_title:
            raise ValueError("Document title is required.")
        now = datetime.now(timezone.utc).isoformat()
        with self._connect() as conn:
            next_num = (conn.execute("SELECT COALESCE(MAX(id), 0) + 1 FROM documents").fetchone()[0]) + 40
            ref_code = f"DOC-2026-{next_num:03d}"
            cur = conn.execute(
                "INSERT INTO documents (ref_code, title, department, submitted_by, status, remarks, updated_at) VALUES (?, ?, ?, ?, 'SUBMITTED', ?, ?)",
                (ref_code, clean_title, department.strip() or "CCS", submitted_by.strip() or "Student", remarks.strip(), now),
            )
            doc_id = int(cur.lastrowid)
            conn.execute(
                "INSERT INTO document_audit (document_id, actor, role, from_status, to_status, note, created_at) VALUES (?, ?, 'STAFF', NULL, 'SUBMITTED', ?, ?)",
                (doc_id, submitted_by.strip() or "Student", "Initial intake submission", now),
            )
        return self.get_document(doc_id)

    def get_document(self, doc_id: int) -> dict | None:
        with self._connect() as conn:
            row = conn.execute("SELECT * FROM documents WHERE id = ?", (doc_id,)).fetchone()
            if not row:
                return None
            audit = conn.execute(
                "SELECT * FROM document_audit WHERE document_id = ? ORDER BY id DESC",
                (doc_id,),
            ).fetchall()
        doc = dict(row)
        doc["audit_trail"] = [dict(a) for a in audit]
        return doc

    def transition_document(self, doc_id: int, to_status: str, actor: str, role: str, note: str = "") -> dict:
        if to_status not in VALID_STATUSES:
            raise ValueError(f"Invalid target status: {to_status}")
        if to_status in {"APPROVED", "RETURNED", "IN_REVIEW"} and role.upper() not in REVIEWER_ROLES:
            raise PermissionError("Reviewer or Dean role required to approve, return, or escalate documents.")

        doc = self.get_document(doc_id)
        if not doc:
            raise LookupError(f"Document #{doc_id} not found.")

        now = datetime.now(timezone.utc).isoformat()
        with self._connect() as conn:
            conn.execute(
                "UPDATE documents SET status = ?, remarks = ?, updated_at = ? WHERE id = ?",
                (to_status, note or doc["remarks"], now, doc_id),
            )
            conn.execute(
                "INSERT INTO document_audit (document_id, actor, role, from_status, to_status, note, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (doc_id, actor, role.upper(), doc["status"], to_status, note or f"Transitioned to {to_status}", now),
            )
        return self.get_document(doc_id)
