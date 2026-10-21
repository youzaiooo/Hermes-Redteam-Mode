import json
from pathlib import Path

from hermes_redteam.store import (
    add_asset,
    open_engagement,
    reserve_write,
    scan_add,
    vuln_add,
    write_report_index,
)


def test_local_loop_stores_paths_not_commands(tmp_path: Path):
    open_engagement(tmp_path, "lab-local", "Lab Local")
    auth = tmp_path / "lab-local" / "wiki" / "authorization.md"
    auth.write_text(
        "# 授权记录\n\n授权方：local\n范围：127.0.0.1\n时间窗：local\n允许手段：http\n联系人：local\n",
        encoding="utf-8",
    )
    reserve_write(tmp_path, "lab-local", "rt-recon")
    add_asset(tmp_path, "lab-local", "range-web", "http://127.0.0.1:8765", "new")
    raw = tmp_path / "lab-local" / "raw" / "scans" / "range-web.txt"
    raw.parent.mkdir(parents=True, exist_ok=True)
    raw.write_text("http title only\n", encoding="utf-8")
    scan_add(tmp_path, "lab-local", "range-web", "raw/scans/range-web.txt")
    vuln_add(tmp_path, "lab-local", "range-web", "info", "raw/scans/range-web.txt")

    report = Path(write_report_index(tmp_path, "lab-local")).read_text(encoding="utf-8")
    listed = json.loads(
        __import__("hermes_redteam.store", fromlist=["scan_list"]).scan_list(tmp_path, "lab-local")
    )

    assert listed["count"] == 1
    assert "wiki/authorization.md" in report
    assert "nmap" not in report
    assert "payload" not in report
