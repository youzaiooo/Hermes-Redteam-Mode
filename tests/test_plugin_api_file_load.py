import importlib.util
import sys
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient


ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def clean_modules():
    """Restore sys.modules afterwards: purging it here would break sibling tests,
    which import `hermes_redteam.*` through the conftest alias package."""
    saved = dict(sys.modules)
    try:
        for name in list(sys.modules):
            if name == "hermes_redteam" or name.startswith(("hermes_redteam.", "hermes_redteam_")):
                sys.modules.pop(name, None)
        yield
    finally:
        sys.modules.clear()
        sys.modules.update(saved)


def test_dashboard_file_loads_without_package_parent(tmp_path, monkeypatch, clean_modules):
    monkeypatch.setenv("HERMES_HOME", str(tmp_path))
    api_path = ROOT / "dashboard" / "plugin_api.py"
    spec = importlib.util.spec_from_file_location("hermes_dashboard_plugin_hermes_redteam", api_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    app = FastAPI()
    app.include_router(module.router)
    listed = TestClient(app).get("/engagements/current")

    assert listed.status_code == 200
    assert listed.json()["engagements"] == []


def test_dashboard_still_imports_as_package(tmp_path, monkeypatch):
    """The alias package conftest installs must expose the same router."""
    monkeypatch.setenv("HERMES_HOME", str(tmp_path))
    import hermes_redteam.dashboard.plugin_api as api

    app = FastAPI()
    app.include_router(api.router)
    listed = TestClient(app).get("/engagements/current")

    assert listed.status_code == 200
