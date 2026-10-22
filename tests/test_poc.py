import json
from pathlib import Path

from hermes_redteam.store import open_engagement, reserve_write


def _root(tmp_path: Path) -> Path:
    return tmp_path / "redteam" / "engagements"


def test_poc_add_writes_global_row_and_search_finds_it(tmp_path: Path):
    from hermes_redteam.store import poc_add, poc_search

    root = _root(tmp_path)
    open_engagement(root, "lab-01", "Lab 01")
    reserve_write(root, "lab-01", "rt-vuln")

    saved = json.loads(
        poc_add(
            root,
            "lab-01",
            "web",
            "range-web",
            "raw/poc/range-web.txt",
            title="Apache Log4j RCE",
            cve="CVE-2021-44228",
            source="nuclei:http/cves/2021/CVE-2021-44228",
        )
    )
    found = json.loads(poc_search(root, "lab-01", "log4j"))

    assert saved["ok"] is True
    assert saved["deduped"] is False
    assert found["count"] >= 1
    assert found["pocs"][0]["source"] == "nuclei:http/cves/2021/CVE-2021-44228"
    assert found["pocs"][0]["verified"] is False
    assert "body" not in found["pocs"][0]
