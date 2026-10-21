import json
from pathlib import Path

from hermes_redteam.store import add_asset, open_engagement, reserve_write


def test_web_list_returns_only_http_assets(tmp_path: Path):
    from hermes_redteam.store import web_list

    open_engagement(tmp_path, "lab-01", "Lab 01")
    reserve_write(tmp_path, "lab-01", "rt-asset")
    add_asset(tmp_path, "lab-01", "range-web", "http://127.0.0.1:8765", "new")
    add_asset(tmp_path, "lab-01", "range-db", "127.0.0.1:5432", "new")

    found = json.loads(web_list(tmp_path, "lab-01"))

    assert found["ok"] is True
    assert found["count"] == 1
    assert found["webs"][0]["stable_key"] == "range-web"
