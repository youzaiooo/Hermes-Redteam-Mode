import json
import sqlite3
from pathlib import Path

from hermes_redteam.store import open_engagement, reserve_write


def test_tunnel_add_requires_entry_kind_and_stores_pointer(tmp_path: Path):
    from hermes_redteam.store import tunnel_add

    open_engagement(tmp_path, "lab-01", "Lab 01")
    reserve_write(tmp_path, "lab-01", "rt-internal")

    saved = json.loads(
        tunnel_add(tmp_path, "lab-01", "range-web", "socks5", "raw/tunnel/range-web.txt")
    )

    assert saved["ok"] is True
    with sqlite3.connect(tmp_path / "lab-01" / "index.db") as db:
        row = db.execute(
            "SELECT asset_key, entry_kind, evidence_path FROM tunnel"
        ).fetchone()
    assert row == ("range-web", "socks5", "raw/tunnel/range-web.txt")
