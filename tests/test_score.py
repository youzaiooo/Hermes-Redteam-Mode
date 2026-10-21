import json
import sqlite3
from pathlib import Path

from hermes_redteam.score import record_score


def test_off_does_not_create_score_row(tmp_path: Path):
    result = json.loads(record_score(tmp_path, "lab-01", "off", "asset-found"))

    assert result["ok"] is True
    assert result["recorded"] is False
    assert not (tmp_path / "lab-01" / "index.db").exists()


def test_visible_records_hit_without_enforcing(tmp_path: Path):
    result = json.loads(record_score(tmp_path, "lab-01", "visible", "asset-found"))

    assert result["ok"] is True
    assert result["recorded"] is True
    with sqlite3.connect(tmp_path / "lab-01" / "index.db") as db:
        row = db.execute("SELECT rule_id, mode FROM score_hit").fetchone()
    assert row == ("asset-found", "visible")
