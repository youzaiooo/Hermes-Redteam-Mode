import json
from pathlib import Path

from hermes_redteam.store import add_asset, open_engagement, reserve_write


def test_asset_link_connects_two_assets(tmp_path: Path):
    from hermes_redteam.store import asset_link, asset_graph

    open_engagement(tmp_path, "lab-01", "Lab 01")
    reserve_write(tmp_path, "lab-01", "rt-asset")
    add_asset(tmp_path, "lab-01", "range-web", "127.0.0.1:8765", "new")
    add_asset(tmp_path, "lab-01", "range-db", "127.0.0.1:5432", "new")

    saved = json.loads(asset_link(tmp_path, "lab-01", "range-web", "range-db", "depends"))
    found = json.loads(asset_graph(tmp_path, "lab-01"))

    assert saved["ok"] is True
    assert found["count"] == 1
    assert found["links"][0]["relation"] == "depends"
