"""Thread-safe metrics, sliding-window rate limiter, and HTTP upstream health probing."""

from __future__ import annotations

import threading
import time
import urllib.error
import urllib.request
from collections import deque
from datetime import datetime, timezone


class SlidingWindowRateLimiter:
    """Limits requests per client key inside a configurable time window."""

    def __init__(self, max_requests: int = 30, window_seconds: float = 10.0) -> None:
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._hits: dict[str, deque[float]] = {}
        self._lock = threading.Lock()

    def allow(self, client_key: str) -> bool:
        now = time.monotonic()
        cutoff = now - self.window_seconds
        with self._lock:
            q = self._hits.setdefault(client_key, deque())
            while q and q[0] < cutoff:
                q.popleft()
            if len(q) >= self.max_requests:
                return False
            q.append(now)
            return True


class GatewayMetrics:
    """Tracks request counts, HTTP status breakdowns, latency percentiles, and access log."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self.total_requests = 0
        self.rate_limited_429 = 0
        self.errors_5xx = 0
        self.latencies_ms: deque[float] = deque(maxlen=250)
        self.recent_access: deque[dict] = deque(maxlen=15)

    def record(self, method: str, path: str, upstream: str, status: int, latency_ms: float) -> None:
        with self._lock:
            self.total_requests += 1
            if status == 429:
                self.rate_limited_429 += 1
            if status >= 500:
                self.errors_5xx += 1
            self.latencies_ms.append(round(latency_ms, 2))
            self.recent_access.appendleft(
                {
                    "time_utc": datetime.now(timezone.utc).strftime("%H:%M:%S"),
                    "method": method,
                    "path": path,
                    "upstream": upstream,
                    "status": status,
                    "latency_ms": round(latency_ms, 2),
                }
            )

    def summary(self) -> dict:
        with self._lock:
            lats = sorted(self.latencies_ms)
            if not lats:
                p50 = p95 = 0.0
            else:
                p50 = lats[len(lats) // 2]
                p95 = lats[min(len(lats) - 1, int(round(0.95 * (len(lats) - 1))))]
            return {
                "total_requests": self.total_requests,
                "rate_limited_429": self.rate_limited_429,
                "errors_5xx": self.errors_5xx,
                "p50_ms": round(p50, 2),
                "p95_ms": round(p95, 2),
                "recent_access": list(self.recent_access),
            }

    def reset(self) -> None:
        with self._lock:
            self.total_requests = 0
            self.rate_limited_429 = 0
            self.errors_5xx = 0
            self.latencies_ms.clear()
            self.recent_access.clear()


def probe_http_target(name: str, url: str, timeout: float = 1.5) -> dict:
    """Probe a single HTTP upstream endpoint and return health state and RTT latency."""
    t0 = time.perf_counter()
    try:
        with urllib.request.urlopen(url, timeout=timeout) as resp:
            rtt = (time.perf_counter() - t0) * 1000.0
            healthy = 200 <= resp.status < 400
            return {
                "service": name,
                "url": url,
                "healthy": healthy,
                "status": "UP" if healthy else "DEGRADED",
                "http_code": resp.status,
                "latency_ms": round(rtt, 2),
            }
    except (urllib.error.URLError, OSError):
        rtt = (time.perf_counter() - t0) * 1000.0
        return {
            "service": name,
            "url": url,
            "healthy": False,
            "status": "DOWN",
            "http_code": 503,
            "latency_ms": round(rtt, 2),
        }
