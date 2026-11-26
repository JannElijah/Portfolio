"""PBKDF2 password hashing, HS256 JWT signing/validation, and sliding-window rate limiter."""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import secrets
import time
from collections import defaultdict, deque


def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _b64url_decode(segment: str) -> bytes:
    padding = "=" * (-len(segment) % 4)
    return base64.urlsafe_b64decode(segment + padding)


def hash_password(password: str, iterations: int = 120_000) -> str:
    """Hash a plaintext password using PBKDF2-HMAC-SHA256 with random 16-byte salt."""
    if len(password) < 8:
        raise ValueError("Password must be at least 8 characters.")
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
    return f"pbkdf2_sha256${iterations}${_b64url_encode(salt)}${_b64url_encode(digest)}"


def verify_password(password: str, encoded_hash: str) -> bool:
    """Verify password against stored PBKDF2-HMAC-SHA256 hash in constant time."""
    try:
        scheme, iter_str, salt_b64, digest_b64 = encoded_hash.split("$", 3)
        if scheme != "pbkdf2_sha256":
            return False
        salt = _b64url_decode(salt_b64)
        expected = _b64url_decode(digest_b64)
        candidate = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, int(iter_str))
        return hmac.compare_digest(candidate, expected)
    except (ValueError, TypeError):
        return False


def create_jwt(payload: dict, secret: str, ttl_seconds: int = 900) -> str:
    """Issue a standard HS256 JWT with issued-at, expiration, and unique jti."""
    now = int(time.time())
    full_payload = {
        **payload,
        "iat": now,
        "exp": now + ttl_seconds,
        "jti": secrets.token_hex(12),
    }
    header_b64 = _b64url_encode(json.dumps({"alg": "HS256", "typ": "JWT"}, separators=(",", ":")).encode("utf-8"))
    payload_b64 = _b64url_encode(json.dumps(full_payload, separators=(",", ":")).encode("utf-8"))
    signing_input = f"{header_b64}.{payload_b64}".encode("ascii")
    sig = hmac.new(secret.encode("utf-8"), signing_input, hashlib.sha256).digest()
    return f"{header_b64}.{payload_b64}.{_b64url_encode(sig)}"


def decode_jwt(token: str, secret: str) -> dict:
    """Validate HS256 JWT signature and expiration, returning claims or raising ValueError."""
    parts = token.split(".")
    if len(parts) != 3:
        raise ValueError("Malformed JWT.")

    header_b64, payload_b64, sig_b64 = parts
    signing_input = f"{header_b64}.{payload_b64}".encode("ascii")
    expected_sig = hmac.new(secret.encode("utf-8"), signing_input, hashlib.sha256).digest()
    if not hmac.compare_digest(_b64url_decode(sig_b64), expected_sig):
        raise ValueError("Invalid token signature.")

    claims = json.loads(_b64url_decode(payload_b64).decode("utf-8"))
    if int(claims.get("exp", 0)) < int(time.time()):
        raise ValueError("Token has expired.")
    return claims


class SlidingWindowRateLimiter:
    """Tracks per-key request timestamps within a rolling window."""

    def __init__(self, max_requests: int = 5, window_seconds: int = 60) -> None:
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._buckets: dict[str, deque[float]] = defaultdict(deque)

    def allow(self, key: str) -> bool:
        now = time.monotonic()
        cutoff = now - self.window_seconds
        bucket = self._buckets[key]
        while bucket and bucket[0] < cutoff:
            bucket.popleft()
        if len(bucket) >= self.max_requests:
            return False
        bucket.append(now)
        return True
