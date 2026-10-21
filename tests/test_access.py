import json
import sqlite3
from pathlib import Path

from hermes_redteam.store import open_engagement, reserve_write


def test_access_add_stores_method_and_evidence_path(tmp_path: Path):
    from hermes_redteam.store import access_add

    open_engagement(tmp_path, "lab-01", "Lab 01")
    reserve_write(tmp_path, "lab-01", "rt-exploit")

    saved = json.loads(
        access_add(tmp_path, "lab-01", "range-web", "web-login", "raw/access/range-web.txt")
    )

    assert saved["ok"] is True
    with sqlite3.connect(tmp_path / "lab-01" / "index.db") as db:
        row = db.execute(
            "SELECT asset_key, method, evidence_path FROM access_session"
        ).fetchone()
    assert row == ("range-web", "web-login", "raw/access/range-web.txt")
