import json
from pathlib import Path

from hermes_redteam.preflight import preflight
from hermes_redteam.store import open_engagement


def test_preflight_ready_when_target_implies_authorization_and_does_not_install(tmp_path: Path):
    open_engagement(tmp_path, "lab-01", "Lab 01")
    calls: list[str] = []

    result = json.loads(
        preflight(
            tmp_path,
            "lab-01",
            which=lambda _name: None,
            install=lambda cmd: calls.append(cmd),
        )
    )

    assert result["status"] == "ready"
    assert result["authorization"] == "implied_by_target"
    assert result["engagement_exists"] is True
    assert "nmap" in result["missing"]
    assert calls == []
    assert "install" not in result


def test_preflight_before_engagement_exists_is_ready(tmp_path: Path):
    result = json.loads(preflight(tmp_path, "new-lab", which=lambda _name: None))

    assert result["ok"] is True
    assert result["status"] == "ready"
    assert result["engagement_exists"] is False
