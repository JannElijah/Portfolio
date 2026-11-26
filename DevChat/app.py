"""DevChat v2.1 — Tactical Zero-Trust Encrypted Channel Relay."""

from __future__ import annotations

import base64
import hashlib
import html
import sqlite3
import time
from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

# --- CONFIGURATION ---
DB_PATH = str(Path(__file__).parent / "devchat.db")
DEFAULT_CHANNELS = ["Demo-Relay", "General", "Ops", "SecAudit", "Top Secret"]


# --- TACTICAL CIPHER THEME ---
def load_css() -> None:
    st.set_page_config(page_title="DevChat // Encrypted Relay", page_icon="🛡️", layout="wide")
    st.markdown(
        """
    <style>
        .stApp {
            background-color: #0a0c0f;
            color: #e4e4e7;
        }
        section[data-testid="stSidebar"] {
            background-color: #0f1216;
            border-right: 1px solid #22262e;
        }
        .chat-row {
            display: flex;
            flex-direction: column;
            margin-bottom: 10px;
        }
        .bubble-self {
            background-color: #064e3b;
            border: 1px solid #10b981;
            color: #ecfdf5;
            padding: 10px 14px;
            border-radius: 10px 10px 2px 10px;
            max-width: 72%;
            margin-left: auto;
        }
        .bubble-peer {
            background-color: #14181f;
            border: 1px solid #272d38;
            color: #e4e4e7;
            padding: 10px 14px;
            border-radius: 10px 10px 10px 2px;
            max-width: 72%;
            margin-right: auto;
        }
        .bubble-locked {
            background-color: #1c1215;
            border: 1px solid #7f1d1d;
            color: #fca5a5;
            padding: 10px 14px;
            border-radius: 8px;
            max-width: 72%;
        }
        .meta {
            font-family: monospace;
            font-size: 0.72rem;
            color: #9ca3af;
            margin-top: 4px;
        }
    </style>
    """,
        unsafe_allow_html=True,
    )


# --- CRYPTO HANDLER ---
class CryptoHandler:
    BASE_SALT = b"devchat_zero_trust_2026"

    @staticmethod
    def generate_key() -> str:
        return Fernet.generate_key().decode()

    @staticmethod
    def derive_key_from_password(password: str, channel: str) -> str:
        """Derive a channel-isolated Fernet key via 480k-iteration PBKDF2-SHA256."""
        channel_salt = hashlib.sha256(CryptoHandler.BASE_SALT + channel.encode("utf-8")).digest()[:16]
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=channel_salt,
            iterations=480_000,
        )
        return base64.urlsafe_b64encode(kdf.derive(password.encode("utf-8"))).decode()

    @staticmethod
    def key_fingerprint(key: str) -> str:
        digest = hashlib.sha256(key.encode("utf-8")).hexdigest().upper()
        return f"{digest[:4]}·{digest[4:8]}"

    @staticmethod
    def validate_key(key: str) -> bool:
        try:
            Fernet(key.encode())
            return True
        except Exception:
            return False

    @staticmethod
    def message_sha256(ciphertext: str) -> str:
        return hashlib.sha256(ciphertext.encode("utf-8")).hexdigest()[:12]

    @staticmethod
    def encrypt(message: str, key: str) -> str:
        return Fernet(key.encode()).encrypt(message.encode("utf-8")).decode()

    @staticmethod
    def decrypt(ciphertext: str, key: str) -> str | None:
        try:
            return Fernet(key.encode()).decrypt(ciphertext.encode("utf-8")).decode("utf-8")
        except Exception:
            return None


# --- STORAGE MANAGER ---
class StorageManager:
    def __init__(self, db_path: str = DB_PATH) -> None:
        self.db_path = db_path
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS channels (
                    name TEXT PRIMARY KEY
                );
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    channel TEXT,
                    username TEXT,
                    ciphertext TEXT,
                    created_epoch REAL
                );
                """
            )
            try:
                conn.execute("ALTER TABLE messages ADD COLUMN created_epoch REAL")
            except sqlite3.OperationalError:
                pass
            for ch in DEFAULT_CHANNELS:
                conn.execute("INSERT OR IGNORE INTO channels (name) VALUES (?)", (ch,))

            # Seed sample encrypted handshake messages in Demo-Relay if empty
            demo_count = conn.execute("SELECT COUNT(*) FROM messages WHERE channel = 'Demo-Relay'").fetchone()[0]
            if demo_count == 0:
                demo_key = CryptoHandler.derive_key_from_password("demo-devchat", "Demo-Relay")
                now = datetime.now().strftime("%H:%M")
                samples = [
                    ("Demo-Relay", "System", CryptoHandler.encrypt("Zero-trust channel initialized (Fernet AES-128-CBC + HMAC-SHA256).", demo_key)),
                    ("Demo-Relay", "Jann", CryptoHandler.encrypt("Key fingerprint verified. Ready for encrypted telemetry relay.", demo_key)),
                ]
                conn.executemany(
                    "INSERT INTO messages (timestamp, channel, username, ciphertext) VALUES (?, ?, ?, ?)",
                    [(now, ch, user, ct) for ch, user, ct in samples],
                )

    def list_channels(self) -> list[str]:
        with self._connect() as conn:
            rows = conn.execute("SELECT name FROM channels ORDER BY rowid ASC").fetchall()
        return [r[0] for r in rows]

    def create_channel(self, name: str) -> None:
        clean = name.strip().replace("#", "")
        if clean:
            with self._connect() as conn:
                conn.execute("INSERT OR IGNORE INTO channels (name) VALUES (?)", (clean,))

    def load_messages(self, channel: str) -> pd.DataFrame:
        with self._connect() as conn:
            return pd.read_sql_query(
                "SELECT id, timestamp, username, ciphertext FROM messages WHERE channel = ? ORDER BY id ASC",
                conn,
                params=(channel,),
            )

    def add_message(self, channel: str, username: str, ciphertext: str, created_epoch: float | None = None) -> None:
        ts = datetime.now().strftime("%H:%M")
        epoch = created_epoch if created_epoch is not None else time.time()
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO messages (timestamp, channel, username, ciphertext, created_epoch) VALUES (?, ?, ?, ?, ?)",
                (ts, channel, username, ciphertext, epoch),
            )

    def prune_expired(self, channel: str, ttl_minutes: int) -> int:
        """Delete messages older than ttl_minutes inside a channel and return removed count."""
        cutoff = time.time() - (max(1, int(ttl_minutes)) * 60)
        with self._connect() as conn:
            cur = conn.execute(
                "DELETE FROM messages WHERE channel = ? AND created_epoch IS NOT NULL AND created_epoch < ?",
                (channel, cutoff),
            )
            return int(cur.rowcount)

    def clear_channel(self, channel: str) -> None:
        with self._connect() as conn:
            conn.execute("DELETE FROM messages WHERE channel = ?", (channel,))


@st.fragment(run_every=2)
def render_messages(storage: StorageManager, channel: str, room_key: str, username: str, debug_mode: bool) -> None:
    df = storage.load_messages(channel)
    with st.container(height=460, border=True):
        if df.empty:
            st.caption("Channel clear. Encrypted messages sent here are stored only as Fernet ciphertext.")
            return

        for _, row in df.iterrows():
            safe_user = html.escape(str(row["username"]))
            safe_ts = html.escape(str(row["timestamp"]))
            decrypted = CryptoHandler.decrypt(row["ciphertext"], room_key)

            if decrypted is not None:
                safe_body = html.escape(decrypted)
                css_cls = "bubble-self" if row["username"] == username else "bubble-peer"
                st.markdown(
                    f"""
                    <div class="chat-row">
                        <div class="{css_cls}">
                            <strong>{safe_user}</strong>: {safe_body}
                            <div class="meta">{safe_ts} · VERIFIED HMAC</div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                if debug_mode:
                    st.code(f"CIPHERTEXT: {row['ciphertext']}", language="text")
            else:
                st.markdown(
                    f"""
                    <div class="chat-row">
                        <div class="bubble-locked">
                            🔒 <strong>Encrypted Payload</strong> (Key mismatch for this room)
                            <div class="meta">{safe_ts} · {safe_user}</div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )


def main() -> None:
    load_css()
    storage = StorageManager()

    if "demo_pass" not in st.session_state:
        st.session_state.demo_pass = "demo-devchat"

    with st.sidebar:
        st.title("🛡️ DevChat Relay")
        st.caption("Fernet AES-128-CBC + PBKDF2-SHA256")
        st.divider()

        username = st.text_input("Operator Handle", value="Jann").strip() or "Anon"
        channels = storage.list_channels()
        default_idx = channels.index("Demo-Relay") if "Demo-Relay" in channels else 0
        channel = st.selectbox("Encrypted Channel", channels, index=default_idx)

        with st.expander("Create Custom Channel"):
            new_ch = st.text_input("Channel Name", placeholder="e.g. Incident-Response")
            if st.button("Add Channel", use_container_width=True) and new_ch.strip():
                storage.create_channel(new_ch)
                st.rerun()

        st.divider()
        auth_method = st.radio("Key Mode", ["Passphrase (PBKDF2)", "Raw Fernet Key"], horizontal=True)
        room_key = None

        if auth_method == "Passphrase (PBKDF2)":
            pwd = st.text_input("Room Passphrase", value=st.session_state.demo_pass, type="password")
            if pwd:
                room_key = CryptoHandler.derive_key_from_password(pwd, channel)
        else:
            if "gen_key" not in st.session_state:
                st.session_state.gen_key = CryptoHandler.generate_key()
            if st.button("Generate New Key", use_container_width=True):
                st.session_state.gen_key = CryptoHandler.generate_key()
            room_key = st.text_input("Fernet Key", value=st.session_state.gen_key, type="password")

        valid_key = bool(room_key and CryptoHandler.validate_key(room_key))
        if valid_key:
            st.success(f"Cipher Active · KEY {CryptoHandler.key_fingerprint(room_key)}")
        else:
            st.error("Provide a valid passphrase or 32-byte Fernet key.")

        st.divider()
        c_dbg, c_clr = st.columns(2)
        debug_mode = c_dbg.toggle("Audit Cipher", value=False)
        if c_clr.button("Clear Room", use_container_width=True):
            storage.clear_channel(channel)
            st.rerun()

        ttl_mins = st.number_input("Ephemeral TTL (mins)", min_value=1, max_value=1440, value=60)
        if st.button("Purge Expired Messages", use_container_width=True):
            removed = storage.prune_expired(channel, int(ttl_mins))
            st.toast(f"Purged {removed} expired messages.")
            st.rerun()

    st.header(f"Channel // #{channel}")
    if not valid_key:
        st.info("Set a room passphrase or Fernet key in the sidebar to decrypt and transmit messages.")
        st.stop()

    render_messages(storage, channel, room_key, username, debug_mode)

    with st.form("send_msg_form", clear_on_submit=True):
        c_msg, c_btn = st.columns([6, 1])
        text = c_msg.text_input("Message", placeholder="Transmit encrypted payload...", label_visibility="collapsed")
        if c_btn.form_submit_button("Send", type="primary", use_container_width=True) and text.strip():
            storage.add_message(channel, username, CryptoHandler.encrypt(text.strip(), room_key))
            st.rerun()

    if debug_mode:
        df = storage.load_messages(channel)
        if not df.empty:
            lines = []
            for _, row in df.iterrows():
                dec = CryptoHandler.decrypt(row["ciphertext"], room_key)
                if dec is not None:
                    lines.append(f"[{row['timestamp']}] {row['username']}: {dec}")
            if lines:
                st.download_button(
                    "Export Decrypted Audit Log (.txt)",
                    data="\n".join(lines).encode("utf-8"),
                    file_name=f"devchat_{channel.lower()}_audit.txt",
                    mime="text/plain",
                )


if __name__ == "__main__":
    main()
