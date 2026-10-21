import json
from pathlib import Path

from hermes_redteam.store import open_engagement, reserve_write, vuln_add, vuln_query


def test_vuln_update_changes_status_and_keeps_evidence_path(tmp_path: Path):
    from hermes_redteam.store import vuln_update

    open_engagement(tmp_path, "lab-01", "Lab 01")
    reserve_write(tmp_path, "lab-01", "rt-vuln")
    vuln_add(tmp_path, "lab-01", "range-web", "suspected", "raw/http/range-web.txt")

    saved = json.loads(vuln_update(tmp_path, "lab-01", "range-web", "confirmed"))
    found = json.loads(vuln_query(tmp_path, "lab-01", "range-web"))

    assert saved["ok"] is True
    assert found["vulns"][0]["status"] == "confirmed"
    assert found["vulns"][0]["evidence_path"] == "raw/http/range-web.txt"
