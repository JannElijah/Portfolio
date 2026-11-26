"""API Contract & Schema Validator for HTTP JSON endpoints."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class ContractResult:
    endpoint: str
    passed: bool
    status_code: int
    latency_ms: float
    errors: list[str]


def validate_contract(
    endpoint: str,
    status_code: int,
    expected_status: int,
    payload: Any,
    required_schema: dict[str, type | tuple[type, ...]],
    latency_ms: float = 0.0,
    max_latency_ms: float = 500.0,
) -> ContractResult:
    """Validate response HTTP status, JSON top-level types, and latency budget."""
    errors: list[str] = []

    if status_code != expected_status:
        errors.append(f"Expected status {expected_status}, got {status_code}")

    if latency_ms > max_latency_ms:
        errors.append(f"Latency {latency_ms:.1f}ms exceeded SLA budget {max_latency_ms:.1f}ms")

    if not isinstance(payload, dict):
        errors.append(f"Expected JSON object payload, got {type(payload).__name__}")
    else:
        for field, expected_type in required_schema.items():
            if field not in payload:
                errors.append(f"Missing required field '{field}'")
            elif not isinstance(payload[field], expected_type):
                errors.append(
                    f"Field '{field}' expected {expected_type}, got {type(payload[field]).__name__}"
                )

    return ContractResult(
        endpoint=endpoint,
        passed=len(errors) == 0,
        status_code=status_code,
        latency_ms=round(latency_ms, 2),
        errors=errors,
    )
