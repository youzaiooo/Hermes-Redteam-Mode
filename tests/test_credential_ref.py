import json
import sqlite3
from pathlib import Path

from hermes_redteam.store import open_engagement, reserve_write


def test_credential_add_stores_reference_not_secret(tmp_path: Path):
    from hermes_redteam.store import credential_add

    open_engagement(tmp_path, "lab-01", "Lab 01")
    reserve_write(tmp_path, "lab-01", "rt-exploit")

    saved = json.loads(
        credential_add(
            tmp_path,
            "lab-01",
            "range-web",
            "raw/cred/range-web.txt",
            extra={"secret_value": "not-stored"},
        )
    )

    assert saved["ok"] is False
    assert saved["error"] == "secret_field"
    with sqlite3.connect(tmp_path / "lab-01" / "index.db") as db:
        count = db.execute("SELECT COUNT(*) FROM credential_ref").fetchone()[0]
    assert count == 0
