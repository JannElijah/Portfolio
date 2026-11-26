"""SQLite user, RBAC role, revoked-token, and immutable audit log store."""

from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path

VALID_ROLES = {"ADMIN", "TECHNICIAN", "STAFF"}


class AuthStore:
    """Manages RBAC identities, token revocation, and security audit trail."""

    def __init__(self, db_path: str | Path = "authgate.db") -> None:
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
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL UNIQUE,
                    password_hash TEXT NOT NULL,
                    role TEXT NOT NULL CHECK(role IN ('ADMIN', 'TECHNICIAN', 'STAFF')),
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS revoked_tokens (
                    jti TEXT PRIMARY KEY,
                    revoked_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS audit_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    actor TEXT NOT NULL,
                    action TEXT NOT NULL,
                    resource TEXT NOT NULL,
                    outcome TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                """
            )

    def create_user(self, username: str, password_hash: str, role: str = "STAFF") -> dict:
        clean_name = username.strip().lower()
        if not clean_name:
            raise ValueError("Username cannot be empty.")
        if role not in VALID_ROLES:
            raise ValueError(f"Role must be one of {sorted(VALID_ROLES)}.")

        now = datetime.now(timezone.utc).isoformat()
        with self._connect() as conn:
            try:
                cur = conn.execute(
                    "INSERT INTO users (username, password_hash, role, created_at) VALUES (?, ?, ?, ?)",
                    (clean_name, password_hash, role, now),
                )
            except sqlite3.IntegrityError as exc:
                raise ValueError("Username already exists.") from exc
            user_id = int(cur.lastrowid)
        return self.get_user_by_id(user_id)

    def get_user_by_username(self, username: str) -> dict | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM users WHERE username = ?",
                (username.strip().lower(),),
            ).fetchone()
        return dict(row) if row else None

    def get_user_by_id(self, user_id: int) -> dict | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT id, username, role, created_at FROM users WHERE id = ?",
                (user_id,),
            ).fetchone()
        return dict(row) if row else None

    def update_user_role(self, user_id: int, new_role: str) -> dict:
        if new_role not in VALID_ROLES:
            raise ValueError(f"Role must be one of {sorted(VALID_ROLES)}.")
        with self._connect() as conn:
            cur = conn.execute("UPDATE users SET role = ? WHERE id = ?", (new_role, user_id))
            if cur.rowcount == 0:
                raise LookupError(f"User #{user_id} not found.")
        return self.get_user_by_id(user_id)

    def revoke_jti(self, jti: str) -> None:
        now = datetime.now(timezone.utc).isoformat()
        with self._connect() as conn:
            conn.execute(
                "INSERT OR IGNORE INTO revoked_tokens (jti, revoked_at) VALUES (?, ?)",
                (jti, now),
            )

    def is_jti_revoked(self, jti: str) -> bool:
        with self._connect() as conn:
            row = conn.execute("SELECT 1 FROM revoked_tokens WHERE jti = ?", (jti,)).fetchone()
        return row is not None

    def append_audit(self, actor: str, action: str, resource: str, outcome: str) -> None:
        now = datetime.now(timezone.utc).isoformat()
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO audit_logs (actor, action, resource, outcome, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (actor, action, resource, outcome, now),
            )

    def list_audit_logs(self, limit: int = 50) -> list[dict]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM audit_logs ORDER BY id DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return [dict(r) for r in rows]
