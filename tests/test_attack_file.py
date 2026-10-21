import json
import sqlite3
from pathlib import Path

from hermes_redteam.store import open_engagement, reserve_write


def test_attack_file_add_stores_path_not_body(tmp_path: Path):
    from hermes_redteam.store import attack_file_add

    open_engagement(tmp_path, "lab-01", "Lab 01")
    reserve_write(tmp_path, "lab-01", "rt-exploit")

    saved = json.loads(
        attack_file_add(tmp_path, "lab-01", "range-web", "raw/files/range-web.txt")
    )

    assert saved["ok"] is True
    with sqlite3.connect(tmp_path / "lab-01" / "index.db") as db:
        row = db.execute(
            "SELECT asset_key, relative_path FROM attack_file"
        ).fetchone()
    assert row == ("range-web", "raw/files/range-web.txt")
