"""End-to-end API tests for UPHSD-DMS document submission, RBAC transition, and audit logs."""

from __future__ import annotations

import json
import threading
import urllib.error
import urllib.request

import pytest

from dms.server import create_server


def _req(url: str, method: str = "GET", payload: dict | None = None) -> tuple[int, dict]:
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}, method=method)
    try:
        with urllib.request.urlopen(req, timeout=3) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as err:
        return err.code, json.loads(err.read().decode("utf-8"))


@pytest.fixture()
def dms_url(tmp_path):
    srv = create_server(host="127.0.0.1", port=0, db_path=str(tmp_path / "dms.db"))
    port = srv.server_address[1]
    t = threading.Thread(target=srv.serve_forever, daemon=True)
    t.start()
    try:
        yield f"http://127.0.0.1:{port}"
    finally:
        srv.shutdown()
        srv.server_close()


def test_document_submission_rbac_approval_and_audit(dms_url: str) -> None:
    c_code, created = _req(
        f"{dms_url}/api/documents",
        "POST",
        {"title": "Internship Evaluation Form", "department": "CCS", "submitted_by": "Jann"},
    )
    assert c_code == 201
    doc_id = created["document"]["id"]
    assert created["document"]["status"] == "SUBMITTED"

    # STAFF role cannot approve
    deny_code, _ = _req(
        f"{dms_url}/api/documents/{doc_id}/transition",
        "PATCH",
        {"to_status": "APPROVED", "role": "STAFF", "actor": "Jann"},
    )
    assert deny_code == 403

    # DEAN role returns then STAFF resubmits before DEAN approves cleanly
    ret_code, returned = _req(
        f"{dms_url}/api/documents/{doc_id}/transition",
        "PATCH",
        {"to_status": "RETURNED", "role": "DEAN", "actor": "Dean Office", "note": "Attach signature"},
    )
    assert ret_code == 200
    assert returned["document"]["status"] == "RETURNED"

    resub_code, resubmitted = _req(
        f"{dms_url}/api/documents/{doc_id}/transition",
        "PATCH",
        {"to_status": "SUBMITTED", "role": "STAFF", "actor": "Jann", "note": "Resubmitted with signature"},
    )
    assert resub_code == 200
    assert resubmitted["document"]["status"] == "SUBMITTED"

    # DEAN role approves cleanly
    ok_code, approved = _req(
        f"{dms_url}/api/documents/{doc_id}/transition",
        "PATCH",
        {"to_status": "APPROVED", "role": "DEAN", "actor": "Dean Office", "note": "Signed"},
    )
    assert ok_code == 200
    assert approved["document"]["status"] == "APPROVED"
    assert len(approved["document"]["audit_trail"]) == 4

    # Department query filter returns scoped rows
    f_code, filtered = _req(f"{dms_url}/api/documents?department=CCS")
    assert f_code == 200
    assert all(d["department"] == "CCS" for d in filtered["documents"])
