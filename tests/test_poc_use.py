import json
from pathlib import Path

from hermes_redteam.store import open_engagement, poc_add, reserve_write


def _root(tmp_path: Path) -> Path:
    return tmp_path / "redteam" / "engagements"


def test_poc_use_records_result_not_body(tmp_path: Path):
    from hermes_redteam.store import poc_use

    root = _root(tmp_path)
    open_engagement(root, "lab-01", "Lab 01")
    reserve_write(root, "lab-01", "rt-vuln")
    poc_add(
        root, "lab-01", "web", "range-web", "raw/poc/range-web.txt",
        title="Apache Log4j RCE", source="nuclei:log4j",
    )

    found = json.loads(poc_use(root, "lab-01", "range-web", "checked"))

    assert found["ok"] is True
    assert found["source"] == "nuclei:log4j"
    assert found["result"] == "checked"
    assert "payload" not in found
