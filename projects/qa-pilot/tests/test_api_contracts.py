"""HTTP API contract and RBAC security tests executed against live UPHSD-DMS."""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.request

from qa_pilot.contracts import validate_contract


def _request_json(url: str, method: str = "GET", body: dict | None = None) -> tuple[int, dict, float]:
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Content-Type", "application/json")
    t0 = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            elapsed = (time.perf_counter() - t0) * 1000.0
            return resp.status, json.loads(resp.read().decode("utf-8")), elapsed
    except urllib.error.HTTPError as err:
        elapsed = (time.perf_counter() - t0) * 1000.0
        return err.code, json.loads(err.read().decode("utf-8")), elapsed


def test_list_documents_contract_and_latency(live_dms_url: str) -> None:
    status, payload, latency = _request_json(f"{live_dms_url}/api/documents")
    result = validate_contract(
        endpoint="GET /api/documents",
        status_code=status,
        expected_status=200,
        payload=payload,
        required_schema={"documents": list},
        latency_ms=latency,
        max_latency_ms=250.0,
    )
    assert result.passed, result.errors
    assert len(payload["documents"]) >= 4


def test_create_document_contract_and_empty_title_rejection(live_dms_url: str) -> None:
    status, payload, latency = _request_json(
        f"{live_dms_url}/api/documents",
        method="POST",
        body={"title": "Contract Test Clearance", "department": "CCS", "submitted_by": "QARunner"},
    )
    created = validate_contract(
        endpoint="POST /api/documents",
        status_code=status,
        expected_status=201,
        payload=payload,
        required_schema={"document": dict},
        latency_ms=latency,
    )
    assert created.passed, created.errors
    assert payload["document"]["status"] == "SUBMITTED"

    bad_status, bad_payload, _ = _request_json(
        f"{live_dms_url}/api/documents",
        method="POST",
        body={"title": "   ", "department": "CCS", "submitted_by": "QARunner"},
    )
    rejected = validate_contract(
        endpoint="POST /api/documents (empty)",
        status_code=bad_status,
        expected_status=400,
        payload=bad_payload,
        required_schema={"error": str},
    )
    assert rejected.passed, rejected.errors
