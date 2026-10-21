import json
from pathlib import Path

from hermes_redteam.store import add_asset, open_engagement, reserve_write


def test_asset_timeline_groups_by_first_seen_day(tmp_path: Path):
    from hermes_redteam.store import asset_timeline

    open_engagement(tmp_path, "lab-01", "Lab 01")
    reserve_write(tmp_path, "lab-01", "rt-asset")
    add_asset(tmp_path, "lab-01", "range-web", "http://127.0.0.1:8765", "new")

    found = json.loads(asset_timeline(tmp_path, "lab-01"))

    assert found["ok"] is True
    assert found["count"] == 1
    assert found["days"][0]["assets"] == ["range-web"]
