import json
from pathlib import Path

from hermes_redteam.store import access_add, open_engagement, reserve_write


def test_access_list_returns_method_and_path(tmp_path: Path):
    from hermes_redteam.store import access_list

    open_engagement(tmp_path, "lab-01", "Lab 01")
    reserve_write(tmp_path, "lab-01", "rt-exploit")
    access_add(tmp_path, "lab-01", "range-web", "web-login", "raw/access/range-web.txt")

    found = json.loads(access_list(tmp_path, "lab-01"))

    assert found["ok"] is True
    assert found["count"] == 1
    assert found["sessions"][0] == {
        "asset_key": "range-web",
        "method": "web-login",
        "evidence_path": "raw/access/range-web.txt",
    }
