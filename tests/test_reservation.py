import json
import sqlite3
from pathlib import Path

from hermes_redteam.store import add_asset, open_engagement, release_write, reserve_write


def test_fourth_open_reservation_is_rejected_until_one_releases(tmp_path: Path):
    open_engagement(tmp_path, "lab-01", "Lab 01")
    held_ids = []
    for role in ("rt-recon", "rt-asset", "rt-vuln"):
        held = json.loads(reserve_write(tmp_path, "lab-01", role))
        assert held["ok"] is True
        held_ids.append(held["id"])

    rejected = json.loads(reserve_write(tmp_path, "lab-01", "rt-exploit"))
    released = json.loads(release_write(tmp_path, "lab-01", held_ids[0]))
    written = json.loads(add_asset(tmp_path, "lab-01", "host-a", "10.0.0.8"))

    assert rejected["ok"] is False
    assert rejected["error"] == "reservation_full"
    assert released["ok"] is True
    assert written["ok"] is True
    with sqlite3.connect(tmp_path / "lab-01" / "index.db") as db:
        open_count = db.execute(
            "SELECT COUNT(*) FROM reservation WHERE released_at IS NULL"
        ).fetchone()[0]
    assert open_count == 2
