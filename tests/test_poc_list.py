import json
from pathlib import Path

from hermes_redteam.store import open_engagement, poc_add, reserve_write


def test_poc_list_returns_source_paths(tmp_path: Path):
    from hermes_redteam.store import poc_list

    open_engagement(tmp_path, "lab-01", "Lab 01")
    reserve_write(tmp_path, "lab-01", "rt-vuln")
    poc_add(tmp_path, "lab-01", "web", "range-web", "raw/poc/range-web.txt")

    found = json.loads(poc_list(tmp_path, "lab-01"))

    assert found["ok"] is True
    assert found["count"] == 1
    assert found["pocs"][0] == {
        "category": "web",
        "asset_key": "range-web",
        "source_path": "raw/poc/range-web.txt",
        "status": "new",
    }
