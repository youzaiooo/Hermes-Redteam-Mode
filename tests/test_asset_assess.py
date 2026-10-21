import json
from pathlib import Path

from hermes_redteam.store import add_asset, open_engagement, reserve_write


def test_asset_assess_appends_priority_note(tmp_path: Path):
    from hermes_redteam.store import asset_assess

    open_engagement(tmp_path, "lab-01", "Lab 01")
    reserve_write(tmp_path, "lab-01", "rt-asset")
    add_asset(tmp_path, "lab-01", "range-web", "http://127.0.0.1:8765", "new")

    saved = json.loads(asset_assess(tmp_path, "lab-01", "range-web", "high"))

    assert saved["ok"] is True
    assert saved["status"] == "new; assess high"
