"""End-to-end API integration and security tests for AuthGate RBAC service."""

from __future__ import annotations

import json
import threading
import urllib.error
import urllib.request

import pytest

from authgate.app import AuthGateContext, create_server
from authgate.security import create_jwt, decode_jwt, hash_password, verify_password


def _request(url: str, method: str = "GET", payload: dict | None = None, token: str | None = None) -> tuple[int, dict]:
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=3) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as err:
        return err.code, json.loads(err.read().decode("utf-8"))


@pytest.fixture()
def auth_server(tmp_path):
    ctx = AuthGateContext(
        db_path=str(tmp_path / "auth_test.db"),
        secret="unit-test-hmac-secret",
        rate_limit_max=4,
    )
    server = create_server(host="127.0.0.1", port=0, context=ctx)
    port = server.server_address[1]
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{port}", ctx
    finally:
        server.shutdown()
        server.server_close()


def test_pbkdf2_and_jwt_tamper_detection() -> None:
    encoded = hash_password("StrongPass123!")
    assert verify_password("StrongPass123!", encoded) is True
    assert verify_password("WrongPass!", encoded) is False

    token = create_jwt({"sub": "alice", "role": "ADMIN"}, "secret-key", ttl_seconds=60)
    claims = decode_jwt(token, "secret-key")
    assert claims["sub"] == "alice"

    with pytest.raises(ValueError):
        decode_jwt(token + "tamper", "secret-key")


def test_rbac_enforcement_audit_logs_and_token_rotation(auth_server) -> None:
    base_url, _ = auth_server

    # Register STAFF and ADMIN users
    s_code, staff = _request(
        f"{base_url}/api/auth/register",
        "POST",
        {"username": "staff1", "password": "Password!1", "role": "STAFF"},
    )
    assert s_code == 201
    assert staff["user"]["role"] == "STAFF"

    a_code, _ = _request(
        f"{base_url}/api/auth/register",
        "POST",
        {"username": "admin1", "password": "Password!2", "role": "ADMIN"},
    )
    assert a_code == 201

    # Login as STAFF -> /api/me allowed, /api/audit-logs forbidden (403)
    _, staff_login = _request(
        f"{base_url}/api/auth/login",
        "POST",
        {"username": "staff1", "password": "Password!1"},
    )
    me_code, me_data = _request(f"{base_url}/api/me", token=staff_login["access_token"])
    assert me_code == 200
    assert me_data["user"]["username"] == "staff1"

    deny_code, _ = _request(f"{base_url}/api/audit-logs", token=staff_login["access_token"])
    assert deny_code == 403

    # Rotate refresh token once, ensure replay of old refresh token fails
    r_code, rotated = _request(
        f"{base_url}/api/auth/refresh",
        "POST",
        {"refresh_token": staff_login["refresh_token"]},
    )
    assert r_code == 200
    replay_code, _ = _request(
        f"{base_url}/api/auth/refresh",
        "POST",
        {"refresh_token": staff_login["refresh_token"]},
    )
    assert replay_code == 401

    # Logout revokes new refresh token cleanly
    l_code, _ = _request(
        f"{base_url}/api/auth/logout",
        "POST",
        {"refresh_token": rotated["refresh_token"]},
    )
    assert l_code == 200
    after_logout_code, _ = _request(
        f"{base_url}/api/auth/refresh",
        "POST",
        {"refresh_token": rotated["refresh_token"]},
    )
    assert after_logout_code == 401

    # Login as ADMIN -> /api/audit-logs succeeds and captures earlier ACCESS_DENIED event
    _, admin_login = _request(
        f"{base_url}/api/auth/login",
        "POST",
        {"username": "admin1", "password": "Password!2"},
    )
    audit_code, audit_data = _request(f"{base_url}/api/audit-logs", token=admin_login["access_token"])
    assert audit_code == 200
    assert any(log["action"] == "ACCESS_DENIED" for log in audit_data["logs"])


def test_login_rate_limiter_blocks_excess_attempts(auth_server) -> None:
    base_url, _ = auth_server
    _request(
        f"{base_url}/api/auth/register",
        "POST",
        {"username": "target", "password": "Password!9", "role": "TECHNICIAN"},
    )
    for _ in range(4):
        code, _ = _request(
            f"{base_url}/api/auth/login",
            "POST",
            {"username": "target", "password": "WrongPassword!"},
        )
        assert code == 401

    blocked_code, _ = _request(
        f"{base_url}/api/auth/login",
        "POST",
        {"username": "target", "password": "WrongPassword!"},
    )
    assert blocked_code == 429
