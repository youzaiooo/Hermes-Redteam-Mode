import json
import sqlite3
from pathlib import Path

from hermes_redteam.store import open_engagement, reserve_write


def test_vuln_add_stores_conclusion_and_evidence_path(tmp_path: Path):
    from hermes_redteam.store import vuln_add

    open_engagement(tmp_path, "lab-01", "Lab 01")
    reserve_write(tmp_path, "lab-01", "rt-vuln")

    saved = json.loads(
        vuln_add(
            tmp_path,
            "lab-01",
            "range-web",
            "confirmed",
            "raw/http/range-web.txt",
        )
    )

    assert saved["ok"] is True
    with sqlite3.connect(tmp_path / "lab-01" / "index.db") as db:
        row = db.execute("SELECT asset_key, status, evidence_path FROM vuln").fetchone()
    assert row == ("range-web", "confirmed", "raw/http/range-web.txt")
