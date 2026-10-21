import json
import sqlite3
from pathlib import Path

from hermes_redteam.store import add_evidence, open_engagement


def test_evidence_stores_pointer_not_body(tmp_path: Path):
    open_engagement(tmp_path, "lab-01", "Lab 01")
    raw = tmp_path / "lab-01" / "raw" / "note.txt"
    raw.write_text("body stays on disk", encoding="utf-8")

    saved = json.loads(
        add_evidence(tmp_path, "lab-01", "note", "raw/note.txt", "one line")
    )

    assert saved["ok"] is True
    assert saved["sha256"]
    assert "body stays on disk" not in json.dumps(saved)
    with sqlite3.connect(tmp_path / "lab-01" / "index.db") as db:
        row = db.execute(
            "SELECT kind, relative_path, sha256, summary FROM evidence_ref"
        ).fetchone()
    assert row[0] == "note"
    assert row[1] == "raw/note.txt"
    assert row[2] == saved["sha256"]
    assert row[3] == "one line"
