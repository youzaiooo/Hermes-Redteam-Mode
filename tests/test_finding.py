import json
import sqlite3
from pathlib import Path

from hermes_redteam.store import add_finding, open_engagement, reserve_write


def test_finding_stores_pointer_not_steps(tmp_path: Path):
    open_engagement(tmp_path, "lab-01", "Lab 01")
    reserve_write(tmp_path, "lab-01", "rt-vuln")

    saved = json.loads(
        add_finding(
            tmp_path,
            "lab-01",
            "host-a",
            "missing header",
            "raw/note.txt",
            extra={"payload": "not-stored"},
        )
    )

    assert saved["ok"] is False
    assert saved["error"] == "secret_field"
    with sqlite3.connect(tmp_path / "lab-01" / "index.db") as db:
        count = db.execute("SELECT COUNT(*) FROM finding").fetchone()[0]
    assert count == 0
