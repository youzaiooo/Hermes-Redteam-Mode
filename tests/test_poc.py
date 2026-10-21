import json
from pathlib import Path

from hermes_redteam.store import open_engagement, reserve_write


def test_poc_add_stores_category_and_source_path(tmp_path: Path):
    from hermes_redteam.store import poc_add, poc_search

    open_engagement(tmp_path, "lab-01", "Lab 01")
    reserve_write(tmp_path, "lab-01", "rt-vuln")

    saved = json.loads(
        poc_add(tmp_path, "lab-01", "web", "range-web", "raw/poc/range-web.txt")
    )
    found = json.loads(poc_search(tmp_path, "lab-01", "web"))

    assert saved["ok"] is True
    assert found["count"] == 1
    assert found["pocs"][0]["source_path"] == "raw/poc/range-web.txt"
