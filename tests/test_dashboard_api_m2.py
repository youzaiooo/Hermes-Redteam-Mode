from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient

from hermes_redteam.dashboard.plugin_api import router
from hermes_redteam.store import (
    add_asset,
    bind_session,
    credential_add,
    open_engagement,
    reserve_write,
    score_hit,
    tunnel_add,
    vuln_add,
)


def _client() -> TestClient:
    app = FastAPI()
    app.include_router(router)
    return TestClient(app)


def _root(tmp_path: Path) -> Path:
    return tmp_path / "redteam" / "engagements"


def test_engagements_empty(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("HERMES_HOME", str(tmp_path))

    response = _client().get("/engagements")

    assert response.status_code == 200
    assert response.json() == {"ok": True, "engagements": []}


def test_engagements_lists_display_name_and_created_at(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("HERMES_HOME", str(tmp_path))
    open_engagement(_root(tmp_path), "lab-01", "Lab 01")

    response = _client().get("/engagements")
    payload = response.json()

    assert payload["ok"] is True
    assert len(payload["engagements"]) == 1
    engagement = payload["engagements"][0]
    assert engagement["id"] == "lab-01"
    assert engagement["display_name"] == "Lab 01"
    assert engagement["created_at"]


def test_engagement_for_session_unbound_is_null(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("HERMES_HOME", str(tmp_path))
    open_engagement(_root(tmp_path), "lab-01", "Lab 01")

    response = _client().get("/engagements/for-session/sess-404")

    assert response.status_code == 200
    assert response.json() == {"ok": True, "engagement": None}


def test_engagement_for_session_resolves_bound_engagement(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("HERMES_HOME", str(tmp_path))
    root = _root(tmp_path)
    open_engagement(root, "lab-01", "Lab 01")
    bind_session(root, "lab-01", "sess-123", "default")

    response = _client().get("/engagements/for-session/sess-123")

    assert response.status_code == 200
    assert response.json() == {
        "ok": True,
        "engagement": {"id": "lab-01", "display_name": "Lab 01"},
    }


def test_summary_missing_engagement_returns_404(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("HERMES_HOME", str(tmp_path))

    response = _client().get("/summary/lab-01")

    assert response.status_code == 404


def test_summary_returns_counts_stage_and_score_hits(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("HERMES_HOME", str(tmp_path))
    root = _root(tmp_path)
    open_engagement(root, "lab-01", "Lab 01")
    reserve_write(root, "lab-01", "rt-recon")
    add_asset(root, "lab-01", "web-01", "http://127.0.0.1:8765")
    add_asset(root, "lab-01", "host-01", "10.0.0.2")
    vuln_add(root, "lab-01", "web-01", "confirmed", "raw/v/web.txt")
    credential_add(root, "lab-01", "web-01", "raw/cred/web.txt")
    tunnel_add(root, "lab-01", "web-01", "frp", "raw/tun/frp.txt")
    score_hit(root, "lab-01", "web-app", "raw/score/web.txt")

    response = _client().get("/summary/lab-01")
    summary = response.json()["summary"]

    assert summary["assets"] == 2
    assert summary["services"] == 1
    assert summary["vulns"] == 1
    assert summary["credentials"] == 1
    assert summary["tunnels"] == 1
    assert summary["score"] == 1
    assert summary["score_hits"] == ["web-app"]
    assert summary["stage"] == "internal"


def test_credentials_route_returns_pointers(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("HERMES_HOME", str(tmp_path))
    root = _root(tmp_path)
    open_engagement(root, "lab-01", "Lab 01")
    reserve_write(root, "lab-01", "rt-exploit")
    credential_add(root, "lab-01", "web-01", "raw/cred/web.txt")

    response = _client().get("/credentials/lab-01")
    payload = response.json()

    assert response.status_code == 200
    assert payload["count"] == 1
    assert payload["credentials"] == [
        {"asset_key": "web-01", "evidence_path": "raw/cred/web.txt"}
    ]
