import json
from pathlib import Path

from hermes_redteam.store import open_engagement, poc_add, reserve_write


def _root(tmp_path: Path) -> Path:
    return tmp_path / "redteam" / "engagements"


def test_poc_update_marks_verified_without_body(tmp_path: Path):
    from hermes_redteam.store import poc_get, poc_update

    root = _root(tmp_path)
    open_engagement(root, "lab-01", "Lab 01")
    reserve_write(root, "lab-01", "rt-vuln")
    poc_add(
        root, "lab-01", "web", "range-web", "raw/poc/range-web.txt",
        title="Apache Log4j RCE", source="nuclei:log4j",
    )

    updated = json.loads(poc_update(root, "lab-01", "range-web", "verified"))
    found = json.loads(poc_get(root, "lab-01", "range-web"))

    assert updated["ok"] is True
    assert updated["verified"] is True
    assert found["poc"]["verified"] is True
    assert found["poc"]["verified_note"] == "verified"
    assert "payload" not in found["poc"]
