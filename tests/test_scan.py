import json
from pathlib import Path

from hermes_redteam.store import open_engagement, reserve_write


def test_scan_add_stores_pointer_not_command(tmp_path: Path):
    from hermes_redteam.store import scan_add

    open_engagement(tmp_path, "lab-01", "Lab 01")
    reserve_write(tmp_path, "lab-01", "rt-recon")

    found = json.loads(
        scan_add(tmp_path, "lab-01", "range-web", "raw/scans/range-web.txt")
    )

    assert found["ok"] is True
    assert found["path"] == "raw/scans/range-web.txt"
    assert "command" not in found
