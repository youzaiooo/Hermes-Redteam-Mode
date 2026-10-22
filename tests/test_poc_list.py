import json
from pathlib import Path

from hermes_redteam.store import open_engagement, poc_add, reserve_write


def _root(tmp_path: Path) -> Path:
    return tmp_path / "redteam" / "engagements"


def test_poc_list_reads_global_db(tmp_path: Path):
    from hermes_redteam.store import poc_list

    root = _root(tmp_path)
    open_engagement(root, "lab-01", "Lab 01")
    reserve_write(root, "lab-01", "rt-vuln")
    poc_add(
        root, "lab-01", "web", "range-web", "raw/poc/range-web.txt",
        title="Apache Log4j RCE", source="nuclei:log4j",
    )

    found = json.loads(poc_list(root, "lab-01"))

    assert found["ok"] is True
    assert found["count"] == 1
    poc = found["pocs"][0]
    assert poc["category"] == "web"
    assert poc["asset_target"] == "range-web"
    assert poc["source"] == "nuclei:log4j"
    assert poc["verified"] is False
    assert "body" not in poc
