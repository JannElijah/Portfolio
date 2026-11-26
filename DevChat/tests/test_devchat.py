"""Unit tests for DevChat channel-isolated PBKDF2, Fernet encryption, and SQLite storage."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app import CryptoHandler, StorageManager


def test_channel_isolated_pbkdf2_and_fernet_roundtrip() -> None:
    key_gen = CryptoHandler.derive_key_from_password("shared-pass", "General")
    key_ops = CryptoHandler.derive_key_from_password("shared-pass", "Ops")
    assert key_gen != key_ops
    assert CryptoHandler.validate_key(key_gen) is True

    cipher = CryptoHandler.encrypt("Status nominal", key_gen)
    assert CryptoHandler.decrypt(cipher, key_gen) == "Status nominal"
    assert CryptoHandler.decrypt(cipher, key_ops) is None


def test_storage_per_channel_isolation_and_clear(tmp_path) -> None:
    store = StorageManager(str(tmp_path / "devchat.db"))
    store.create_channel("SecAudit")
    assert "SecAudit" in store.list_channels()

    k = CryptoHandler.derive_key_from_password("p1", "SecAudit")
    cipher_txt = CryptoHandler.encrypt("Audit ready", k)
    assert len(CryptoHandler.message_sha256(cipher_txt)) == 12
    store.add_message("SecAudit", "alice", cipher_txt, created_epoch=1.0)
    assert len(store.load_messages("SecAudit")) == 1

    # Message from epoch 1.0 expires cleanly under 5-minute TTL
    assert store.prune_expired("SecAudit", ttl_minutes=5) == 1
    assert len(store.load_messages("SecAudit")) == 0

    store.add_message("SecAudit", "alice", cipher_txt)
    assert len(store.load_messages("SecAudit")) == 1
    store.clear_channel("SecAudit")
    assert len(store.load_messages("SecAudit")) == 0
    assert len(store.load_messages("Demo-Relay")) == 2
