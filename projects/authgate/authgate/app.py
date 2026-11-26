"""HTTP REST server implementing RBAC authentication, token refresh, and audit logging."""

from __future__ import annotations

import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

from authgate.security import (
    SlidingWindowRateLimiter,
    create_jwt,
    decode_jwt,
    hash_password,
    verify_password,
)
from authgate.store import AuthStore


class AuthGateContext:
    """Shared dependencies injected into HTTP request handlers."""

    def __init__(
        self,
        db_path: str = "authgate.db",
        secret: str | None = None,
        rate_limit_max: int = 5,
    ) -> None:
        self.store = AuthStore(db_path)
        self.secret = secret or os.environ.get("AUTHGATE_SECRET", "dev-only-change-in-prod-secret")
        self.limiter = SlidingWindowRateLimiter(max_requests=rate_limit_max, window_seconds=60)


def create_server(host: str = "127.0.0.1", port: int = 8080, context: AuthGateContext | None = None) -> ThreadingHTTPServer:
    """Create a configured ThreadingHTTPServer bound to the supplied AuthGateContext."""
    ctx = context or AuthGateContext()

    class AuthHandler(BaseHTTPRequestHandler):
        def log_message(self, format: str, *args: Any) -> None:
            # Silence default stderr access logs during tests
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

        def _authenticate(self, allowed_roles: set[str] | None = None) -> dict | None:
            auth_header = self.headers.get("Authorization", "")
            if not auth_header.startswith("Bearer "):
                self._send_json(401, {"error": "Missing Bearer token"})
                return None
            token = auth_header.removeprefix("Bearer ").strip()
            try:
                claims = decode_jwt(token, ctx.secret)
            except ValueError as exc:
                self._send_json(401, {"error": str(exc)})
                return None
            if claims.get("type") != "access":
                self._send_json(401, {"error": "Invalid token type"})
                return None
            if allowed_roles and claims.get("role") not in allowed_roles:
                ctx.store.append_audit(
                    actor=claims.get("sub", "unknown"),
                    action="ACCESS_DENIED",
                    resource=self.path,
                    outcome="403_FORBIDDEN",
                )
                self._send_json(403, {"error": "Insufficient role permissions"})
                return None
            return claims

        def do_GET(self) -> None:
            if self.path == "/api/me":
                claims = self._authenticate()
                if not claims:
                    return
                user = ctx.store.get_user_by_id(int(claims["uid"]))
                self._send_json(200, {"user": user})
                return

            if self.path == "/api/audit-logs":
                claims = self._authenticate(allowed_roles={"ADMIN"})
                if not claims:
                    return
                logs = ctx.store.list_audit_logs()
                self._send_json(200, {"logs": logs})
                return

            self._send_json(404, {"error": "Endpoint not found"})

        def do_POST(self) -> None:
            try:
                data = self._read_json()
            except ValueError:
                self._send_json(400, {"error": "Malformed JSON payload"})
                return

            if self.path == "/api/auth/register":
                try:
                    pw_hash = hash_password(data.get("password", ""))
                    user = ctx.store.create_user(
                        username=data.get("username", ""),
                        password_hash=pw_hash,
                        role=data.get("role", "STAFF"),
                    )
                    ctx.store.append_audit(user["username"], "REGISTER", "/api/auth/register", "SUCCESS")
                    self._send_json(201, {"user": user})
                except ValueError as exc:
                    self._send_json(400, {"error": str(exc)})
                return

            if self.path == "/api/auth/login":
                client_ip = self.client_address[0]
                if not ctx.limiter.allow(client_ip):
                    ctx.store.append_audit(data.get("username", "unknown"), "LOGIN", "/api/auth/login", "RATE_LIMITED")
                    self._send_json(429, {"error": "Too many login attempts"})
                    return

                user = ctx.store.get_user_by_username(data.get("username", ""))
                if not user or not verify_password(data.get("password", ""), user["password_hash"]):
                    ctx.store.append_audit(data.get("username", "unknown"), "LOGIN", "/api/auth/login", "INVALID_CREDS")
                    self._send_json(401, {"error": "Invalid credentials"})
                    return

                access = create_jwt({"uid": user["id"], "sub": user["username"], "role": user["role"], "type": "access"}, ctx.secret, 900)
                refresh = create_jwt({"uid": user["id"], "sub": user["username"], "role": user["role"], "type": "refresh"}, ctx.secret, 86400)
                ctx.store.append_audit(user["username"], "LOGIN", "/api/auth/login", "SUCCESS")
                self._send_json(200, {"access_token": access, "refresh_token": refresh, "role": user["role"]})
                return

            if self.path == "/api/auth/refresh":
                raw_refresh = data.get("refresh_token", "")
                try:
                    claims = decode_jwt(raw_refresh, ctx.secret)
                except ValueError as exc:
                    self._send_json(401, {"error": str(exc)})
                    return
                if claims.get("type") != "refresh" or ctx.store.is_jti_revoked(claims["jti"]):
                    self._send_json(401, {"error": "Refresh token revoked or invalid"})
                    return

                ctx.store.revoke_jti(claims["jti"])
                new_access = create_jwt({"uid": claims["uid"], "sub": claims["sub"], "role": claims["role"], "type": "access"}, ctx.secret, 900)
                new_refresh = create_jwt({"uid": claims["uid"], "sub": claims["sub"], "role": claims["role"], "type": "refresh"}, ctx.secret, 86400)
                ctx.store.append_audit(claims["sub"], "TOKEN_REFRESH", "/api/auth/refresh", "SUCCESS")
                self._send_json(200, {"access_token": new_access, "refresh_token": new_refresh})
                return

            if self.path == "/api/auth/logout":
                raw_refresh = data.get("refresh_token", "")
                try:
                    claims = decode_jwt(raw_refresh, ctx.secret)
                    ctx.store.revoke_jti(claims["jti"])
                    ctx.store.append_audit(claims["sub"], "LOGOUT", "/api/auth/logout", "SUCCESS")
                except ValueError:
                    pass
                self._send_json(200, {"status": "logged_out"})
                return

            self._send_json(404, {"error": "Endpoint not found"})

        def do_PATCH(self) -> None:
            if self.path.startswith("/api/users/") and self.path.endswith("/role"):
                claims = self._authenticate(allowed_roles={"ADMIN"})
                if not claims:
                    return
                try:
                    uid = int(self.path.split("/")[3])
                    body = self._read_json()
                    updated = ctx.store.update_user_role(uid, body.get("role", ""))
                    ctx.store.append_audit(claims["sub"], "ROLE_UPDATE", self.path, f"TO_{updated['role']}")
                    self._send_json(200, {"user": updated})
                except (ValueError, LookupError) as exc:
                    self._send_json(400, {"error": str(exc)})
                return

            self._send_json(404, {"error": "Endpoint not found"})

    return ThreadingHTTPServer((host, port), AuthHandler)


if __name__ == "__main__":
    srv = create_server()
    print("AuthGate REST API listening on http://127.0.0.1:8080")
    srv.serve_forever()
