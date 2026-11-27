"""Unit tests for StockPilot local SQLite inventory CRUD and QR generation."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core import LocalInventoryStore, build_qr_label_sheet_html, compute_reorder_plan, generate_qr


def test_local_inventory_crud_and_seed(tmp_path) -> None:
    store = LocalInventoryStore(tmp_path / "inv.db")
    seeded = store.fetch()
    assert len(seeded) == 6

    ok, err = store.add("CAT6 Tester", "Electronics", 49.5, 12)
    assert ok is True
    assert err is None

    df = store.fetch()
    new_row = df[df["name"] == "CAT6 Tester"].iloc[0]
    row_id = int(new_row["id"])
    ok_u, _ = store.update(row_id, "CAT6 Pro Tester", "Electronics", 55.0, 9)
    assert ok_u is True

    # Test stock adjustment, clamp at 0, and reorder plan
    ok_r, _ = store.adjust_stock(row_id, 10, "Inbound shipment")
    assert ok_r is True
    assert int(store.fetch().set_index("id").loc[row_id, "quantity"]) == 19

    ok_d_clamp, _ = store.adjust_stock(row_id, -999, "Full dispatch")
    assert ok_d_clamp is True
    assert int(store.fetch().set_index("id").loc[row_id, "quantity"]) == 0

    plan = compute_reorder_plan(store.fetch(), threshold=10, target_buffer=15)
    assert "CAT6 Pro Tester" in plan["name"].tolist()
    assert int(plan.set_index("name").loc["CAT6 Pro Tester", "suggested_order"]) == 15

    ok_d, _ = store.delete(row_id)
    assert ok_d is True
    assert len(store.fetch()) == 6

    movements = store.fetch_movements()
    assert list(movements["action"])[:4] == ["DELETE", "DISPATCH", "RESTOCK", "UPDATE"]


def test_bulk_csv_import_and_batch_qr_sheet(tmp_path) -> None:
    store = LocalInventoryStore(tmp_path / "batch.db")
    csv_data = "name,category,price,quantity\nFiber SFP Module,Electronics,45.0,15\nBadRow,Electronics,-5,1\n"
    imported, errors = store.import_csv(csv_data)
    assert imported == 1
    assert len(errors) == 1

    sheet = build_qr_label_sheet_html(store.fetch())
    assert "data:image/png;base64," in sheet
    assert "Fiber SFP Module" in sheet


def test_qr_tag_generates_png_bytes() -> None:
    png = generate_qr("STOCKPILOT|ID:1|NAME:Router|CAT:Electronics")
    assert png.startswith(b"\x89PNG")
