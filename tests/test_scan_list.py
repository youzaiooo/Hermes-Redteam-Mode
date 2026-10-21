import json
from pathlib import Path

from hermes_redteam.store import open_engagement, reserve_write, scan_add


def test_scan_list_returns_saved_path(tmp_path: Path):
    from hermes_redteam.store import scan_list

    open_engagement(tmp_path, "lab-01", "Lab 01")
    reserve_write(tmp_path, "lab-01", "rt-recon")
    scan_add(tmp_path, "lab-01", "range-web", "raw/scans/range-web.txt")

    found = json.loads(scan_list(tmp_path, "lab-01"))

    assert found["count"] == 1
    assert found["scans"][0]["path"] == "raw/scans/range-web.txt"
