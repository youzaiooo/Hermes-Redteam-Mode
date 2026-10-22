import json
from pathlib import Path

from hermes_redteam.store import open_engagement, poc_add, reserve_write


def _root(tmp_path: Path) -> Path:
    return tmp_path / "redteam" / "engagements"


def test_poc_get_returns_source_and_verified(tmp_path: Path):
    from hermes_redteam.store import poc_get

    root = _root(tmp_path)
    open_engagement(root, "lab-01", "Lab 01")
    reserve_write(root, "lab-01", "rt-vuln")
    poc_add(
        root, "lab-01", "web", "range-web", "raw/poc/range-web.txt",
        title="Apache Log4j RCE", source="nuclei:log4j",
    )

    found = json.loads(poc_get(root, "lab-01", "range-web"))

    assert found["ok"] is True
    assert found["poc"]["source"] == "nuclei:log4j"
    assert found["poc"]["verified"] is False
    assert "body" not in found["poc"]
