import json
import sqlite3
from pathlib import Path

from hermes_redteam.store import chain_add, open_engagement, reserve_write


def test_chain_add_stores_command_path(tmp_path: Path):
    open_engagement(tmp_path, "lab-01", "Lab 01")
    reserve_write(tmp_path, "lab-01", "rt-exploit")

    saved = json.loads(
        chain_add(tmp_path, "lab-01", "range-web", "raw/chain/range-web.txt", "confirmed")
    )

    assert saved["ok"] is True
    with sqlite3.connect(tmp_path / "lab-01" / "index.db") as db:
        row = db.execute(
            "SELECT asset_key, command_path, result FROM chain_step"
        ).fetchone()
    assert row == ("range-web", "raw/chain/range-web.txt", "confirmed")
