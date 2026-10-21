from fastapi import FastAPI
from fastapi.testclient import TestClient

from hermes_redteam.dashboard.plugin_api import router


def test_score_switch_writes_plugin_entry(tmp_path, monkeypatch):
    monkeypatch.setenv("HERMES_HOME", str(tmp_path))
    app = FastAPI()
    app.include_router(router)
    client = TestClient(app)

    saved = client.post("/score-rules", json={"mode": "visible"})
    shown = client.get("/score-rules")

    text = (tmp_path / "config.yaml").read_text(encoding="utf-8")
    assert saved.status_code == 200
    assert shown.json()["mode"] == "visible"
    assert "hermes-redteam" in text
    assert "new_session" in saved.json()["notice"]
