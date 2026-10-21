import json
import sqlite3
from pathlib import Path

from hermes_redteam.store import add_chain, open_engagement, reserve_write


def test_chain_stores_ids_not_steps(tmp_path: Path):
    open_engagement(tmp_path, "lab-01", "Lab 01")
    reserve_write(tmp_path, "lab-01", "rt-exploit")

    saved = json.loads(add_chain(tmp_path, "lab-01", "edge-1", [1, 2], extra={"steps": "not-stored"}))

    assert saved["error"] == "secret_field"
    with sqlite3.connect(tmp_path / "lab-01" / "index.db") as db:
        count = db.execute("SELECT COUNT(*) FROM attack_chain").fetchone()[0]
    assert count == 0
