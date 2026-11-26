"""Pure data & QR helpers for StockPilot (decoupled from Streamlit UI)."""

from __future__ import annotations

import base64
import csv
import html
import io
from datetime import datetime
from io import BytesIO
from pathlib import Path
import sqlite3

import pandas as pd
import qrcode
from supabase import create_client

CATEGORIES = ["Electronics", "Clothing", "Home", "Food", "Other"]
DEMO_DB_PATH = Path(__file__).parent / "stockpilot_demo.db"


class LocalInventoryStore:
    """SQLite fallback store so StockPilot works seamlessly in offline/demo mode."""

    def __init__(self, db_path: Path = DEMO_DB_PATH) -> None:
        self.db_path = str(db_path)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS inventory (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    category TEXT NOT NULL,
                    price REAL NOT NULL,
                    quantity INTEGER NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS inventory_movements (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    item_name TEXT NOT NULL,
                    action TEXT NOT NULL,
                    delta_qty INTEGER NOT NULL,
                    note TEXT,
                    created_at TEXT NOT NULL
                )
                """
            )
            count = conn.execute("SELECT COUNT(*) FROM inventory").fetchone()[0]
            if count == 0:
                now = datetime.now().isoformat(timespec="seconds")
                seed_rows = [
                    ("Dell Latitude 5440 Laptop", "Electronics", 940.00, 14, now),
                    ("Cisco Catalyst 2960 Switch", "Electronics", 620.00, 6, now),
                    ("USB-C Docking Station", "Electronics", 145.00, 22, now),
                    ("Cat6 Patch Cable Pack (20x)", "Home", 34.50, 48, now),
                    ("Thermal Barcode Label Roll", "Other", 18.00, 8, now),
                    ("Ergonomic Wireless Mouse", "Electronics", 39.99, 19, now),
                ]
                conn.executemany(
                    "INSERT INTO inventory (name, category, price, quantity, created_at) VALUES (?, ?, ?, ?, ?)",
                    seed_rows,
                )

    def fetch(self) -> pd.DataFrame:
        with self._connect() as conn:
            return pd.read_sql_query("SELECT * FROM inventory ORDER BY id ASC", conn)

    def _record_movement(self, conn: sqlite3.Connection, item_name: str, action: str, delta_qty: int, note: str = "") -> None:
        conn.execute(
            "INSERT INTO inventory_movements (item_name, action, delta_qty, note, created_at) VALUES (?, ?, ?, ?, ?)",
            (item_name, action, int(delta_qty), note, datetime.now().isoformat(timespec="seconds")),
        )

    def fetch_movements(self, limit: int = 30) -> pd.DataFrame:
        with self._connect() as conn:
            return pd.read_sql_query(
                "SELECT item_name, action, delta_qty, note, created_at FROM inventory_movements ORDER BY id DESC LIMIT ?",
                conn,
                params=(limit,),
            )

    def add(self, name: str, category: str, price: float, quantity: int) -> tuple[bool, str | None]:
        try:
            with self._connect() as conn:
                conn.execute(
                    "INSERT INTO inventory (name, category, price, quantity, created_at) VALUES (?, ?, ?, ?, ?)",
                    (name, category, price, quantity, datetime.now().isoformat(timespec="seconds")),
                )
                self._record_movement(conn, name, "ADD", quantity, f"{category} @ ${price:.2f}")
            return True, None
        except Exception as exc:
            return False, str(exc)

    def update(self, item_id: int, name: str, category: str, price: float, quantity: int) -> tuple[bool, str | None]:
        try:
            with self._connect() as conn:
                prev = conn.execute("SELECT quantity FROM inventory WHERE id = ?", (item_id,)).fetchone()
                old_qty = int(prev[0]) if prev else 0
                conn.execute(
                    "UPDATE inventory SET name = ?, category = ?, price = ?, quantity = ? WHERE id = ?",
                    (name, category, price, quantity, item_id),
                )
                self._record_movement(conn, name, "UPDATE", quantity - old_qty, f"Qty {old_qty}->{quantity}")
            return True, None
        except Exception as exc:
            return False, str(exc)

    def delete(self, item_id: int) -> tuple[bool, str | None]:
        try:
            with self._connect() as conn:
                prev = conn.execute("SELECT name, quantity FROM inventory WHERE id = ?", (item_id,)).fetchone()
                conn.execute("DELETE FROM inventory WHERE id = ?", (item_id,))
                if prev:
                    self._record_movement(conn, str(prev[0]), "DELETE", -int(prev[1]), "Removed SKU")
            return True, None
        except Exception as exc:
            return False, str(exc)

    def import_csv(self, csv_text: str) -> tuple[int, list[str]]:
        """Bulk import inventory rows from CSV text (name,category,price,quantity)."""
        reader = csv.DictReader(io.StringIO(csv_text.strip()))
        inserted = 0
        errors: list[str] = []
        for idx, row in enumerate(reader, start=2):
            name = (row.get("name") or "").strip()
            cat = (row.get("category") or "Other").strip()
            if cat not in CATEGORIES:
                cat = "Other"
            try:
                price = float(row.get("price", 0))
                qty = int(float(row.get("quantity", 0)))
                if not name or price <= 0 or qty < 0:
                    raise ValueError("invalid fields")
                ok, err = self.add(name, cat, price, qty)
                if ok:
                    inserted += 1
                else:
                    errors.append(f"Row {idx}: {err}")
            except (TypeError, ValueError):
                errors.append(f"Row {idx}: Invalid name/price/quantity")
        return inserted, errors


class SupabaseInventoryStore:
    """Supabase PostgreSQL backed inventory store."""

    def __init__(self, url: str, key: str) -> None:
        self.client = create_client(url, key)

    def fetch(self) -> pd.DataFrame:
        response = self.client.table("inventory").select("*").execute()
        df = pd.DataFrame(response.data)
        if not df.empty and "id" in df.columns:
            df = df.sort_values(by="id")
        return df

    def add(self, name: str, category: str, price: float, quantity: int) -> tuple[bool, str | None]:
        try:
            self.client.table("inventory").insert(
                {"name": name, "category": category, "price": price, "quantity": quantity}
            ).execute()
            return True, None
        except Exception as exc:
            return False, str(exc)

    def update(self, item_id: int, name: str, category: str, price: float, quantity: int) -> tuple[bool, str | None]:
        try:
            self.client.table("inventory").update(
                {"name": name, "category": category, "price": price, "quantity": quantity}
            ).eq("id", item_id).execute()
            return True, None
        except Exception as exc:
            return False, str(exc)

    def delete(self, item_id: int) -> tuple[bool, str | None]:
        try:
            self.client.table("inventory").delete().eq("id", item_id).execute()
            return True, None
        except Exception as exc:
            return False, str(exc)


def generate_qr(data: str) -> bytes:
    qr = qrcode.QRCode(version=1, box_size=10, border=2)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#111215", back_color="#ffffff")
    buf = BytesIO()
    img.save(buf)
    return buf.getvalue()


def build_qr_label_sheet_html(df: pd.DataFrame) -> str:
    """Build a printable HTML label sheet containing QR tags for all SKUs in df."""
    cards = []
    for _, row in df.iterrows():
        payload = f"STOCKPILOT|ID:{int(row['id'])}|NAME:{row['name']}|CAT:{row['category']}"
        b64 = base64.b64encode(generate_qr(payload)).decode("ascii")
        cards.append(
            f"<div style='border:1px solid #d4d4d8;border-radius:8px;padding:12px;text-align:center;break-inside:avoid;'>"
            f"<img src='data:image/png;base64,{b64}' style='width:120px;height:120px;' />"
            f"<div style='font-weight:700;font-size:13px;margin-top:6px;'>#{int(row['id'])} {html.escape(str(row['name']))}</div>"
            f"<div style='font-size:11px;color:#52525b;'>{html.escape(str(row['category']))} · ${float(row['price']):.2f}</div>"
            f"</div>"
        )
    return (
        "<!doctype html><html><head><meta charset='utf-8' /><title>StockPilot QR Labels</title></head>"
        "<body style='font-family:Inter,system-ui,sans-serif;padding:20px;'>"
        "<h2>StockPilot — Batch QR Asset Labels</h2>"
        "<div style='display:grid;grid-template-columns:repeat(3,1fr);gap:14px;'>"
        + "".join(cards)
        + "</div></body></html>"
    )
