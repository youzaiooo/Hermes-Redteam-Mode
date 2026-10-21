import json
from pathlib import Path

from hermes_redteam.store import open_engagement, poc_add, reserve_write


def test_poc_get_returns_one_source_path(tmp_path: Path):
    from hermes_redteam.store import poc_get

    open_engagement(tmp_path, "lab-01", "Lab 01")
    reserve_write(tmp_path, "lab-01", "rt-vuln")
    poc_add(tmp_path, "lab-01", "web", "range-web", "raw/poc/range-web.txt")

    found = json.loads(poc_get(tmp_path, "lab-01", "range-web"))

    assert found["ok"] is True
    assert found["poc"]["source_path"] == "raw/poc/range-web.txt"
    assert "body" not in found["poc"]
