import json
from pathlib import Path

from hermes_redteam.preflight import preflight
from hermes_redteam.store import open_engagement


def test_preflight_blocks_empty_authorization_and_does_not_install(tmp_path: Path):
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

    assert result["status"] == "blocked"
    assert result["reason"] == "empty_authorization"
    assert "nmap" in result["missing"]
    assert calls == []
    assert "install" not in result
