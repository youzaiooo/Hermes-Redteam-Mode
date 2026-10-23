import json
import sqlite3
from pathlib import Path

from hermes_redteam.store import open_engagement


def test_open_creates_index_wiki_and_implied_authorization(tmp_path: Path):
    result = json.loads(open_engagement(tmp_path, "lab-01", "Lab 01", scope="10.0.0.0/24"))

    root = tmp_path / "lab-01"
    assert result["ok"] is True
    assert result["id"] == "lab-01"
    assert (root / "index.db").is_file()
    assert (root / "wiki" / "SCHEMA.md").is_file()
    assert (root / "wiki" / "index.md").is_file()
    assert (root / "wiki" / "log.md").is_file()
    assert (root / "raw").is_dir()

    auth = (root / "wiki" / "authorization.md").read_text(encoding="utf-8")
    assert "待填写" not in auth
    assert "范围：10.0.0.0/24" in auth
    assert "授权依据" in auth
    assert "无需二次确认" in auth

    with sqlite3.connect(root / "index.db") as db:
        row = db.execute(
            "SELECT id, display_name FROM engagement WHERE id = ?",
            ("lab-01",),
        ).fetchone()
        columns = {item[1] for item in db.execute("PRAGMA table_info(asset)")}
    assert row == ("lab-01", "Lab 01")
    assert "password" not in columns
    assert "secret" not in columns
    assert "cookie" not in columns


def test_open_rejects_bad_id_and_empty_name(tmp_path: Path):
    bad_id = json.loads(open_engagement(tmp_path, "../lab", "Lab"))
    empty_name = json.loads(open_engagement(tmp_path, "lab-01", "  "))

    assert bad_id["ok"] is False
    assert bad_id["error"] == "invalid_id"
    assert empty_name["ok"] is False
    assert empty_name["error"] == "empty_name"
    assert not (tmp_path / "lab-01").exists()
    assert not any(tmp_path.iterdir())
