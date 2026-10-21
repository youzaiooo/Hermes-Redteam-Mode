import json
from pathlib import Path

from hermes_redteam.store import add_asset, open_engagement, query_assets, reserve_write


def test_asset_test_appends_status_without_replacing_history(tmp_path: Path):
    from hermes_redteam.store import asset_test

    open_engagement(tmp_path, "lab-01", "Lab 01")
    reserve_write(tmp_path, "lab-01", "rt-asset")
    add_asset(tmp_path, "lab-01", "range-web", "127.0.0.1:8765", "new")

    saved = json.loads(asset_test(tmp_path, "lab-01", "range-web", "checked"))
    found = json.loads(query_assets(tmp_path, "lab-01", "range-web"))

    assert saved["ok"] is True
    assert found["assets"][0]["status"] == "new; checked"
