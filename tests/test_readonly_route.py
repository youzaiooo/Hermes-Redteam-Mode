from fastapi import FastAPI
from fastapi.testclient import TestClient

from hermes_redteam.dashboard.plugin_api import router


def test_board_route_is_read_only(tmp_path, monkeypatch):
    monkeypatch.setenv("HERMES_HOME", str(tmp_path))
    app = FastAPI()
    app.include_router(router)
    client = TestClient(app)

    opened = client.post("/engagements", json={"id": "lab-01"})
    missing = client.get("/board/lab-01")

    assert opened.status_code in {404, 405}
    assert missing.status_code == 404
