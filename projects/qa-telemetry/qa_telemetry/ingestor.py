"""Ingestion and SQLite storage for JUnit XML and structured JSON test-bench runs."""

from __future__ import annotations

import json
import sqlite3
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path


class TelemetryStore:
    """Persists automated QA test runs and individual test-case outcomes."""

    def __init__(self, db_path: str | Path = "qa_telemetry.db") -> None:
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
                CREATE TABLE IF NOT EXISTS test_runs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    suite_name TEXT NOT NULL,
                    build_ref TEXT NOT NULL,
                    total_cases INTEGER NOT NULL,
                    passed_cases INTEGER NOT NULL,
                    failed_cases INTEGER NOT NULL,
                    skipped_cases INTEGER NOT NULL,
                    duration_s REAL NOT NULL,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS test_cases (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_id INTEGER NOT NULL REFERENCES test_runs(id) ON DELETE CASCADE,
                    classname TEXT NOT NULL,
                    name TEXT NOT NULL,
                    outcome TEXT NOT NULL CHECK(outcome IN ('PASSED', 'FAILED', 'SKIPPED')),
                    duration_s REAL NOT NULL,
                    failure_message TEXT
                );
                """
            )

    def record_run(self, suite_name: str, build_ref: str, cases: list[dict]) -> int:
        """Persist a normalized test run and its cases, returning the run ID."""
        total = len(cases)
        passed = sum(1 for c in cases if c["outcome"] == "PASSED")
        failed = sum(1 for c in cases if c["outcome"] == "FAILED")
        skipped = sum(1 for c in cases if c["outcome"] == "SKIPPED")
        duration_s = round(sum(float(c.get("duration_s", 0.0)) for c in cases), 4)
        now = datetime.now(timezone.utc).isoformat()

        with self._connect() as conn:
            cur = conn.execute(
                """
                INSERT INTO test_runs (
                    suite_name, build_ref, total_cases, passed_cases, failed_cases, skipped_cases, duration_s, created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (suite_name, build_ref, total, passed, failed, skipped, duration_s, now),
            )
            run_id = int(cur.lastrowid)
            conn.executemany(
                """
                INSERT INTO test_cases (run_id, classname, name, outcome, duration_s, failure_message)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        run_id,
                        c.get("classname", "default"),
                        c["name"],
                        c["outcome"],
                        float(c.get("duration_s", 0.0)),
                        c.get("failure_message"),
                    )
                    for c in cases
                ],
            )
        return run_id

    def ingest_junit_xml(self, xml_path: str | Path, suite_name: str = "pytest-suite", build_ref: str = "local") -> int:
        """Parse a JUnit XML file (e.g. from pytest --junitxml) into SQLite."""
        tree = ET.parse(xml_path)
        root = tree.getroot()
        suites = [root] if root.tag == "testsuite" else list(root.findall("testsuite"))

        cases: list[dict] = []
        for suite in suites:
            for elem in suite.findall("testcase"):
                classname = elem.attrib.get("classname", "suite")
                name = elem.attrib.get("name", "unnamed_test")
                duration_s = float(elem.attrib.get("time", "0") or 0)

                failure = elem.find("failure")
                error = elem.find("error")
                skipped = elem.find("skipped")

                if failure is not None or error is not None:
                    node = failure if failure is not None else error
                    outcome = "FAILED"
                    msg = (node.attrib.get("message") or node.text or "Test failed").strip()
                elif skipped is not None:
                    outcome = "SKIPPED"
                    msg = (skipped.attrib.get("message") or "Skipped").strip()
                else:
                    outcome = "PASSED"
                    msg = None

                cases.append(
                    {
                        "classname": classname,
                        "name": name,
                        "outcome": outcome,
                        "duration_s": duration_s,
                        "failure_message": msg,
                    }
                )
        return self.record_run(suite_name=suite_name, build_ref=build_ref, cases=cases)

    def ingest_json_log(self, json_path: str | Path) -> int:
        """Parse a structured hardware/API JSON test-bench log into SQLite."""
        payload = json.loads(Path(json_path).read_text(encoding="utf-8"))
        suite_name = payload.get("suite_name", "hardware-bench")
        build_ref = payload.get("build_ref", "v0")
        raw_cases = payload.get("cases", [])

        normalized: list[dict] = []
        for item in raw_cases:
            raw_outcome = str(item.get("outcome", "PASSED")).upper()
            if raw_outcome not in {"PASSED", "FAILED", "SKIPPED"}:
                raise ValueError(f"Unsupported test outcome: {raw_outcome}")
            normalized.append(
                {
                    "classname": item.get("classname", "bench"),
                    "name": item["name"],
                    "outcome": raw_outcome,
                    "duration_s": float(item.get("duration_s", 0.0)),
                    "failure_message": item.get("failure_message"),
                }
            )
        return self.record_run(suite_name=suite_name, build_ref=build_ref, cases=normalized)

    def get_run(self, run_id: int) -> dict | None:
        with self._connect() as conn:
            row = conn.execute("SELECT * FROM test_runs WHERE id = ?", (run_id,)).fetchone()
            if not row:
                return None
            cases = conn.execute(
                "SELECT * FROM test_cases WHERE run_id = ? ORDER BY id ASC",
                (run_id,),
            ).fetchall()
        data = dict(row)
        data["cases"] = [dict(c) for c in cases]
        return data

    def list_runs(self, suite_name: str | None = None) -> list[dict]:
        query = "SELECT * FROM test_runs"
        params: tuple = ()
        if suite_name:
            query += " WHERE suite_name = ?"
            params = (suite_name,)
        query += " ORDER BY id DESC"
        with self._connect() as conn:
            rows = conn.execute(query, params).fetchall()
        return [dict(r) for r in rows]

    def fetch_all_case_history(self, suite_name: str | None = None) -> list[dict]:
        query = """
            SELECT tc.classname, tc.name, tc.outcome, tc.duration_s, tr.id AS run_id, tr.build_ref
            FROM test_cases tc
            JOIN test_runs tr ON tc.run_id = tr.id
        """
        params: tuple = ()
        if suite_name:
            query += " WHERE tr.suite_name = ?"
            params = (suite_name,)
        query += " ORDER BY tr.id ASC, tc.id ASC"
        with self._connect() as conn:
            rows = conn.execute(query, params).fetchall()
        return [dict(r) for r in rows]
