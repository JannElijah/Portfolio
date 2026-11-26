"""Unit tests for StormWatchPH meteorological classification and wind vectors."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd

from app import build_hazard_snapshot_html, classify_heat_index, filter_weather_by_risk, get_wind_direction


def test_wind_direction_compass_bins() -> None:
    assert get_wind_direction(0) == "N"
    assert get_wind_direction(90) == "E"
    assert get_wind_direction(225) == "SW"
    assert get_wind_direction(359) == "N"


def test_pagasa_heat_index_risk_tiers() -> None:
    assert classify_heat_index(22.0) == "Normal"
    assert classify_heat_index(29.5) == "Caution"
    assert classify_heat_index(36.0) == "Extreme Caution"
    assert classify_heat_index(45.0) == "Danger"
    assert classify_heat_index(53.0) == "Extreme Danger"


def test_weather_risk_filtering_and_html_advisory() -> None:
    w_df = pd.DataFrame(
        [
            {"city": "Manila", "temp": 33.0, "feels_like": 43.0, "heat_risk": "Danger"},
            {"city": "Baguio", "temp": 20.0, "feels_like": 20.0, "heat_risk": "Normal"},
        ]
    )
    q_df = pd.DataFrame([{"magnitude": 4.8, "place": "Luzon", "depth_km": 12.0}])
    filtered = filter_weather_by_risk(w_df, ["Danger"])
    assert len(filtered) == 1 and filtered.iloc[0]["city"] == "Manila"

    html_doc = build_hazard_snapshot_html(q_df, filtered)
    assert "StormWatch PH — Regional Hazard Advisory Snapshot" in html_doc
    assert "M 4.8" in html_doc
    assert "Manila" in html_doc
