import json
import sqlite3
from pathlib import Path

from hermes_redteam.store import add_asset, open_engagement, query_assets, reserve_write


def test_asset_add_updates_same_key_and_query_returns_one_line(tmp_path: Path):
    open_engagement(tmp_path, "lab-01", "Lab 01")
    reserve_write(tmp_path, "lab-01", "rt-asset")

    first = json.loads(add_asset(tmp_path, "lab-01", "host-a", "10.0.0.8", "new"))
    second = json.loads(add_asset(tmp_path, "lab-01", "host-a", "10.0.0.8", "seen"))
    found = json.loads(query_assets(tmp_path, "lab-01", "host-a"))

    assert first["ok"] is True
    assert second["ok"] is True
    assert second["updated"] is True
    assert found["count"] == 1
    assert found["assets"][0]["status"] == "seen"
    assert "password" not in found["assets"][0]

    with sqlite3.connect(tmp_path / "lab-01" / "index.db") as db:
        count = db.execute("SELECT COUNT(*) FROM asset").fetchone()[0]
    assert count == 1


def test_asset_add_rejects_secret_fields(tmp_path: Path):
    open_engagement(tmp_path, "lab-01", "Lab 01")
    reserve_write(tmp_path, "lab-01", "rt-asset")

    rejected = json.loads(
        add_asset(
            tmp_path,
            "lab-01",
            "host-a",
            "10.0.0.8",
            "new",
            extra={"password": "not-stored"},
        )
    )

    assert rejected["ok"] is False
    assert rejected["error"] == "secret_field"
    with sqlite3.connect(tmp_path / "lab-01" / "index.db") as db:
        count = db.execute("SELECT COUNT(*) FROM asset").fetchone()[0]
    assert count == 0
