import json
from pathlib import Path

from hermes_redteam.store import open_engagement, reserve_write, vuln_add


def test_vuln_query_returns_one_asset_row(tmp_path: Path):
    from hermes_redteam.store import vuln_query

    open_engagement(tmp_path, "lab-01", "Lab 01")
    reserve_write(tmp_path, "lab-01", "rt-vuln")
    vuln_add(tmp_path, "lab-01", "range-web", "confirmed", "raw/http/range-web.txt")

    found = json.loads(vuln_query(tmp_path, "lab-01", "range-web"))

    assert found["ok"] is True
    assert found["count"] == 1
    assert found["vulns"][0]["status"] == "confirmed"
    assert found["vulns"][0]["evidence_path"] == "raw/http/range-web.txt"
