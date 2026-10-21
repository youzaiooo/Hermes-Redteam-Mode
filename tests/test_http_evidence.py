import json
import sqlite3
from pathlib import Path

from hermes_redteam.store import open_engagement, reserve_write


def test_http_evidence_add_stores_request_and_response_paths(tmp_path: Path):
    from hermes_redteam.store import http_evidence_add

    open_engagement(tmp_path, "lab-01", "Lab 01")
    reserve_write(tmp_path, "lab-01", "rt-vuln")

    saved = json.loads(
        http_evidence_add(
            tmp_path,
            "lab-01",
            "range-web",
            "raw/http/range-web.request",
            "raw/http/range-web.response",
        )
    )

    assert saved["ok"] is True
    with sqlite3.connect(tmp_path / "lab-01" / "index.db") as db:
        row = db.execute(
            "SELECT asset_key, request_path, response_path FROM http_evidence"
        ).fetchone()
    assert row == (
        "range-web",
        "raw/http/range-web.request",
        "raw/http/range-web.response",
    )
