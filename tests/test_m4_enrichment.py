import json
import sqlite3
from pathlib import Path

from hermes_redteam.store import (
    add_asset,
    asset_test,
    chain_add,
    chain_list,
    migrate_db,
    open_engagement,
    query_assets,
    reserve_write,
    vuln_add,
    vuln_query,
)


OLD_SCHEMA = """
CREATE TABLE engagement (
    id TEXT PRIMARY KEY,
    display_name TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE asset (
    id INTEGER PRIMARY KEY,
    engagement_id TEXT NOT NULL REFERENCES engagement(id),
    stable_key TEXT NOT NULL,
    address TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'new',
    first_seen TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_seen TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (engagement_id, stable_key)
);
CREATE TABLE vuln (
    id INTEGER PRIMARY KEY,
    engagement_id TEXT NOT NULL REFERENCES engagement(id),
    asset_key TEXT NOT NULL,
    status TEXT NOT NULL,
    evidence_path TEXT NOT NULL
);
CREATE TABLE chain_step (
    id INTEGER PRIMARY KEY,
    engagement_id TEXT NOT NULL REFERENCES engagement(id),
    asset_key TEXT NOT NULL,
    command_path TEXT NOT NULL,
    result TEXT NOT NULL
);
"""


def test_migrate_upgrades_old_schema_and_preserves_rows(tmp_path: Path):
    db_path = tmp_path / "index.db"
    with sqlite3.connect(db_path) as db:
        db.executescript(OLD_SCHEMA)
        db.execute("INSERT INTO engagement (id, display_name) VALUES ('lab-01', 'Lab 01')")
        db.execute(
            "INSERT INTO asset (engagement_id, stable_key, address, status) "
            "VALUES ('lab-01', 'web-01', 'http://127.0.0.1:8765', 'new')"
        )
        db.execute(
            "INSERT INTO vuln (engagement_id, asset_key, status, evidence_path) "
            "VALUES ('lab-01', 'web-01', 'confirmed', 'raw/v.txt')"
        )
        db.execute(
            "INSERT INTO chain_step (engagement_id, asset_key, command_path, result) "
            "VALUES ('lab-01', 'web-01', 'raw/c.txt', 'ok')"
        )

    with sqlite3.connect(db_path) as db:
        migrate_db(db)

    with sqlite3.connect(db_path) as db:
        asset_cols = {row[1] for row in db.execute("PRAGMA table_info(asset)")}
        vuln_cols = {row[1] for row in db.execute("PRAGMA table_info(vuln)")}
        chain_cols = {row[1] for row in db.execute("PRAGMA table_info(chain_step)")}

        assert {
            "port", "service", "product", "version", "url", "title", "names",
            "provenance", "tool", "scope", "test_status", "test_notes",
        } <= asset_cols
        assert {
            "title", "severity", "cve", "target", "evidence", "confidence",
            "gained", "agent", "created_at",
        } <= vuln_cols
        assert {"stage_code", "tool", "summary", "created_at"} <= chain_cols

        asset_row = db.execute(
            "SELECT stable_key, port, service, title FROM asset"
        ).fetchone()
        assert asset_row == ("web-01", 0, "", "")
        vuln_row = db.execute(
            "SELECT title, severity, created_at FROM vuln"
        ).fetchone()
        assert vuln_row[0] == ""
        assert vuln_row[1] == ""
        assert vuln_row[2]


def test_asset_add_derives_stable_key_and_returns_new_fields(tmp_path: Path):
    open_engagement(tmp_path, "lab-01", "Lab 01")
    reserve_write(tmp_path, "lab-01", "rt-recon")

    saved = json.loads(
        add_asset(
            tmp_path,
            "lab-01",
            address="10.0.0.8",
            port=443,
            service="https",
            title="Admin console",
            tool="nuclei",
        )
    )
    found = json.loads(query_assets(tmp_path, "lab-01"))

    assert saved["ok"] is True
    assert saved["stable_key"] == "10.0.0.8:443"
    assert found["count"] == 1
    asset = found["assets"][0]
    assert asset["port"] == 443
    assert asset["service"] == "https"
    assert asset["title"] == "Admin console"
    assert asset["tool"] == "nuclei"


def test_asset_query_filters_status_and_assessed(tmp_path: Path):
    open_engagement(tmp_path, "lab-01", "Lab 01")
    reserve_write(tmp_path, "lab-01", "rt-recon")
    add_asset(tmp_path, "lab-01", "a", "10.0.0.1", "new")
    add_asset(tmp_path, "lab-01", "b", "10.0.0.2", "seen")

    seen = json.loads(query_assets(tmp_path, "lab-01", status="seen"))
    asset_test(tmp_path, "lab-01", "b", "checked")
    assessed = json.loads(query_assets(tmp_path, "lab-01", assessed=True))
    unassessed = json.loads(query_assets(tmp_path, "lab-01", assessed=False))

    assert seen["count"] == 1
    assert seen["assets"][0]["stable_key"] == "b"
    assert [asset["stable_key"] for asset in assessed["assets"]] == ["b"]
    assert [asset["stable_key"] for asset in unassessed["assets"]] == ["a"]


def test_asset_test_appends_test_notes_and_sets_test_status(tmp_path: Path):
    open_engagement(tmp_path, "lab-01", "Lab 01")
    reserve_write(tmp_path, "lab-01", "rt-recon")
    add_asset(tmp_path, "lab-01", "a", "10.0.0.1", "new")

    asset_test(tmp_path, "lab-01", "a", "checked")
    saved = json.loads(asset_test(tmp_path, "lab-01", "a", "confirmed"))
    found = json.loads(query_assets(tmp_path, "lab-01", "a"))

    assert saved["ok"] is True
    assert saved["test_status"] == "confirmed"
    assert saved["test_notes"] == "checked\nconfirmed"
    assert found["assets"][0]["test_status"] == "confirmed"
    assert found["assets"][0]["test_notes"] == "checked\nconfirmed"
    assert found["assets"][0]["status"] == "new; checked; confirmed"


def test_vuln_add_and_query_expose_new_fields(tmp_path: Path):
    open_engagement(tmp_path, "lab-01", "Lab 01")
    reserve_write(tmp_path, "lab-01", "rt-vuln")

    vuln_add(
        tmp_path,
        "lab-01",
        "web-01",
        "confirmed",
        "raw/v.txt",
        title="SQL injection",
        severity="high",
        cve="CVE-2026-0001",
        agent="rt-vuln",
    )
    found = json.loads(vuln_query(tmp_path, "lab-01", "web-01"))

    assert found["count"] == 1
    vuln = found["vulns"][0]
    assert vuln["title"] == "SQL injection"
    assert vuln["severity"] == "high"
    assert vuln["cve"] == "CVE-2026-0001"
    assert vuln["agent"] == "rt-vuln"
    assert vuln["created_at"]


def test_chain_add_and_list_expose_new_fields(tmp_path: Path):
    open_engagement(tmp_path, "lab-01", "Lab 01")
    reserve_write(tmp_path, "lab-01", "rt-exploit")

    chain_add(
        tmp_path,
        "lab-01",
        "web-01",
        "raw/chain/web-01.txt",
        "confirmed",
        stage_code="exploit",
        tool="webshell",
        summary="landed shell",
    )
    found = json.loads(chain_list(tmp_path, "lab-01"))

    assert found["count"] == 1
    step = found["steps"][0]
    assert step["stage_code"] == "exploit"
    assert step["tool"] == "webshell"
    assert step["summary"] == "landed shell"
    assert step["created_at"]


def test_dashboard_assets_and_findings_expose_new_columns(tmp_path: Path, monkeypatch):
    from fastapi import FastAPI
    from fastapi.testclient import TestClient

    monkeypatch.setenv("HERMES_HOME", str(tmp_path))

    from hermes_redteam.dashboard.plugin_api import router

    root = tmp_path / "redteam" / "engagements"
    open_engagement(root, "lab-01", "Lab 01")
    reserve_write(root, "lab-01", "rt-recon")
    add_asset(
        root,
        "lab-01",
        "web-01",
        "http://127.0.0.1:8765",
        "new",
        port=8765,
        service="http",
        title="Range Console",
    )
    reserve_write(root, "lab-01", "rt-vuln")
    vuln_add(
        root,
        "lab-01",
        "web-01",
        "confirmed",
        "raw/v.txt",
        title="SQL injection",
        severity="high",
    )

    app = FastAPI()
    app.include_router(router)
    client = TestClient(app)

    assets = client.get("/assets/lab-01").json()
    findings = client.get("/findings/lab-01").json()

    assert assets["assets"][0]["port"] == 8765
    assert assets["assets"][0]["service"] == "http"
    assert assets["assets"][0]["title"] == "Range Console"
    assert findings["vulns"][0]["title"] == "SQL injection"
    assert findings["vulns"][0]["severity"] == "high"
