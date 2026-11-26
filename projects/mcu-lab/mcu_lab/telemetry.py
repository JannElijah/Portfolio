"""UART telemetry frame parsing, spec boundary validation, and mock bench stream generation."""

from __future__ import annotations

import random
from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass(frozen=True)
class SpecLimit:
    """Upper and lower electrical/thermal bounds for an MCU telemetry channel."""

    channel: str
    unit: str
    min_value: float
    max_value: float


DEFAULT_MCU_SPECS: dict[str, SpecLimit] = {
    "VDD_3V3": SpecLimit(channel="VDD_3V3", unit="V", min_value=3.15, max_value=3.45),
    "VCC_5V": SpecLimit(channel="VCC_5V", unit="V", min_value=4.75, max_value=5.25),
    "MCU_TEMP_C": SpecLimit(channel="MCU_TEMP_C", unit="C", min_value=-10.0, max_value=85.0),
    "I_DRAW_MA": SpecLimit(channel="I_DRAW_MA", unit="mA", min_value=5.0, max_value=120.0),
}


def parse_uart_frame(raw_frame: str) -> dict:
    """Parse a comma-delimited key=value UART telemetry packet into structured metrics."""
    cleaned = raw_frame.strip()
    if not cleaned:
        raise ValueError("Empty telemetry frame.")

    pairs: dict[str, str] = {}
    for token in cleaned.split(","):
        if "=" not in token:
            raise ValueError(f"Malformed token in frame: {token!r}")
        key, value = token.split("=", 1)
        pairs[key.strip().upper()] = value.strip()

    if "DEV" not in pairs:
        raise ValueError("Telemetry frame missing DEV identifier.")

    metrics: dict[str, float] = {}
    for channel in DEFAULT_MCU_SPECS:
        if channel not in pairs:
            raise ValueError(f"Telemetry frame missing required channel: {channel}")
        metrics[channel] = float(pairs[channel])

    return {
        "device_id": pairs["DEV"],
        "firmware": pairs.get("FW", "1.0.0"),
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "metrics": metrics,
    }


def evaluate_frame_against_specs(
    parsed_frame: dict,
    specs: dict[str, SpecLimit] | None = None,
) -> dict:
    """Evaluate parsed channel metrics against electrical/thermal pass-fail limits."""
    active_specs = specs or DEFAULT_MCU_SPECS
    faults: list[dict] = []

    for channel, limit in active_specs.items():
        if channel not in parsed_frame["metrics"]:
            continue
        observed = parsed_frame["metrics"][channel]
        if observed < limit.min_value or observed > limit.max_value:
            faults.append(
                {
                    "channel": channel,
                    "observed": observed,
                    "allowed_min": limit.min_value,
                    "allowed_max": limit.max_value,
                    "unit": limit.unit,
                }
            )

    return {
        **parsed_frame,
        "verdict": "PASS" if not faults else "FAIL",
        "faults": faults,
    }


def generate_mock_uart_frames(
    count: int = 10,
    fault_probability: float = 0.15,
    seed: int | None = 42,
    device_prefix: str = "PIC32MX",
) -> list[str]:
    """Generate deterministic simulated UART telemetry packets for bench validation."""
    rng = random.Random(seed)
    frames: list[str] = []

    for idx in range(1, count + 1):
        inject_fault = rng.random() < fault_probability
        vdd = round(rng.uniform(3.24, 3.36), 3)
        vcc = round(rng.uniform(4.92, 5.08), 3)
        temp = round(rng.uniform(32.0, 52.0), 2)
        current = round(rng.uniform(24.0, 58.0), 2)

        if inject_fault:
            fault_type = rng.choice(["over_temp", "brownout", "over_current"])
            if fault_type == "over_temp":
                temp = round(rng.uniform(88.5, 97.0), 2)
            elif fault_type == "brownout":
                vdd = round(rng.uniform(2.75, 3.05), 3)
            else:
                current = round(rng.uniform(132.0, 160.0), 2)

        frames.append(
            f"DEV={device_prefix}-{idx:03d},FW=2.1.0,VDD_3V3={vdd},VCC_5V={vcc},MCU_TEMP_C={temp},I_DRAW_MA={current}"
        )
    return frames
