"""Integration tests for WaferBench unified HTTP API bridging MCU-Lab & QA Telemetry."""

from __future__ import annotations

import json
import threading
import urllib.error
import urllib.request

import pytest

from waferbench.server import create_server


@pytest.fixture()
def bench_url(tmp_path):
    srv = create_server(
        host="127.0.0.1",
        port=0,
        mcu_db=str(tmp_path / "wb_mcu.db"),
        qa_db=str(tmp_path / "wb_qa.db"),
    )
    port = srv.server_address[1]
    t = threading.Thread(target=srv.serve_forever, daemon=True)
    t.start()
    try:
        yield f"http://127.0.0.1:{port}"
    finally:
        srv.shutdown()
        srv.server_close()


def test_overview_and_simulation_endpoints(bench_url: str) -> None:
    with urllib.request.urlopen(f"{bench_url}/api/overview", timeout=3) as resp:
        assert resp.status == 200
        overview = json.loads(resp.read().decode("utf-8"))

    assert overview["lot_summary"]["total_units"] == 12
    assert overview["qa_gate"]["verdict"] == "PASS"

    req = urllib.request.Request(
        f"{bench_url}/api/mcu/simulate",
        data=json.dumps({"lot_code": "LOT-API-TEST", "fault_probability": 0.4}).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=3) as sim_resp:
        assert sim_resp.status == 201
        sim_data = json.loads(sim_resp.read().decode("utf-8"))
    assert sim_data["lot_summary"]["lot_code"] == "LOT-API-TEST"
    assert sim_data["lot_summary"]["total_units"] == 10

    # Check historical lot query and CSV export
    with urllib.request.urlopen(f"{bench_url}/api/overview?lot_id={sim_data['lot_id']}", timeout=3) as ov2:
        ov2_data = json.loads(ov2.read().decode("utf-8"))
        assert len(ov2_data["lots"]) >= 2
        assert ov2_data["lot_summary"]["lot_code"] == "LOT-API-TEST"

    with urllib.request.urlopen(f"{bench_url}/api/mcu/export.csv?lot_id={sim_data['lot_id']}", timeout=3) as csv_resp:
        csv_text = csv_resp.read().decode("utf-8")
        assert "device_id,vdd_3v3,vcc_5v,mcu_temp_c,i_draw_ma,verdict" in csv_text
        assert len(csv_text.strip().splitlines()) == 11

    # Inject live raw UART frame and verify invalid frame rejection
    ing_req = urllib.request.Request(
        f"{bench_url}/api/mcu/ingest-frame",
        data=json.dumps(
            {
                "lot_id": sim_data["lot_id"],
                "raw_frame": "DEV=PIC32MX-99,VDD_3V3=3.29,VCC_5V=5.01,MCU_TEMP_C=46.2,I_DRAW_MA=118.4",
            }
        ).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(ing_req, timeout=3) as ing_resp:
        assert ing_resp.status == 201
        ing_data = json.loads(ing_resp.read().decode("utf-8"))
    assert ing_data["frame"]["verdict"] == "PASS"

    bad_req = urllib.request.Request(
        f"{bench_url}/api/mcu/ingest-frame",
        data=json.dumps({"raw_frame": "BAD_FRAME"}).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with pytest.raises(urllib.error.HTTPError) as exc_info:
        urllib.request.urlopen(bad_req, timeout=3)
    assert exc_info.value.code == 400
