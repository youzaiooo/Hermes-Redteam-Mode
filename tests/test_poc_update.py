import json
from pathlib import Path

from hermes_redteam.store import open_engagement, poc_add, reserve_write


def test_poc_update_changes_status_without_body(tmp_path: Path):
    from hermes_redteam.store import poc_get, poc_update

    open_engagement(tmp_path, "lab-01", "Lab 01")
    reserve_write(tmp_path, "lab-01", "rt-vuln")
    poc_add(tmp_path, "lab-01", "web", "range-web", "raw/poc/range-web.txt")

    updated = json.loads(poc_update(tmp_path, "lab-01", "range-web", "verified"))
    found = json.loads(poc_get(tmp_path, "lab-01", "range-web"))

    assert updated["ok"] is True
    assert found["poc"]["status"] == "verified"
    assert "payload" not in found["poc"]
