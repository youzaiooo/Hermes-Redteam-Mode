import json
from pathlib import Path

from hermes_redteam.store import add_asset, open_engagement, reserve_write


def test_asset_get_returns_one_asset(tmp_path: Path):
    from hermes_redteam.store import asset_get

    open_engagement(tmp_path, "lab-01", "Lab 01")
    reserve_write(tmp_path, "lab-01", "rt-asset")
    add_asset(tmp_path, "lab-01", "range-web", "http://127.0.0.1:8765", "new")

    found = json.loads(asset_get(tmp_path, "lab-01", "range-web"))

    assert found["ok"] is True
    assert found["asset"]["stable_key"] == "range-web"
    assert found["asset"]["address"] == "http://127.0.0.1:8765"
