import json
from pathlib import Path

from hermes_redteam.store import open_engagement, poc_add, reserve_write


def test_poc_use_records_path_not_body(tmp_path: Path):
    from hermes_redteam.store import poc_use

    open_engagement(tmp_path, "lab-01", "Lab 01")
    reserve_write(tmp_path, "lab-01", "rt-vuln")
    poc_add(tmp_path, "lab-01", "web", "range-web", "raw/poc/range-web.txt")

    found = json.loads(poc_use(tmp_path, "lab-01", "range-web", "checked"))

    assert found["ok"] is True
    assert found["source_path"] == "raw/poc/range-web.txt"
    assert found["result"] == "checked"
    assert "payload" not in found
