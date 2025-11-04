import sqlite3

from app import db


def test_initialize_is_idempotent(tmp_path, monkeypatch):
    target = tmp_path / "demo.sqlite3"
    monkeypatch.setenv("FLOWGUARD_DB_PATH", str(target))
    db.initialize()
    db.initialize()
    with sqlite3.connect(target) as connection:
        tables = {row[0] for row in connection.execute("SELECT name FROM sqlite_master WHERE type = 'table'")}
    assert {"runs", "issues", "audit_events"}.issubset(tables)
