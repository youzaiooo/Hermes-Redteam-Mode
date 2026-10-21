import json
import sqlite3
from pathlib import Path

from hermes_redteam.store import credential_add, open_engagement, reserve_write


def test_credential_reference_can_be_stored(tmp_path: Path):
    open_engagement(tmp_path, "lab-01", "Lab 01")
    reserve_write(tmp_path, "lab-01", "rt-exploit")

    saved = json.loads(
        credential_add(tmp_path, "lab-01", "range-web", "raw/cred/range-web.txt")
    )

    assert saved["ok"] is True
    with sqlite3.connect(tmp_path / "lab-01" / "index.db") as db:
        row = db.execute(
            "SELECT asset_key, evidence_path FROM credential_ref"
        ).fetchone()
    assert row == ("range-web", "raw/cred/range-web.txt")
