import json
import os
from pathlib import Path

from hermes_redteam.tools import TOOLS, asset_add, engagement_open, session_bind


def test_p1_tools_are_registered():
    names = {item[0] for item in TOOLS}
    assert "redteam_evidence_add" in names
    assert "redteam_reserve" in names
    assert "redteam_release" in names
    assert "redteam_score_record" not in names
    assert "redteam_finding_add" in names
    assert "redteam_report_skeleton" in names


def test_tool_handler_uses_hermes_home_and_rejects_secret(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("HERMES_HOME", str(tmp_path))
    from hermes_redteam.store import reserve_write

    opened = json.loads(engagement_open({"id": "lab-01", "display_name": "Lab 01"}))
    reserve_write(tmp_path / "redteam" / "engagements", "lab-01", "rt-asset")
    session_bind({"id": "lab-01", "session_id": "s-1", "profile": "rt-asset"})
    rejected = json.loads(
        asset_add(
            {
                "id": "lab-01",
                "stable_key": "host-a",
                "address": "10.0.0.8",
                "session_id": "s-1",
                "extra": {"password": "not-stored"},
            }
        )
    )

    assert opened["ok"] is True
    assert rejected["error"] == "secret_field"
    assert (tmp_path / "redteam" / "engagements" / "lab-01" / "index.db").is_file()
    assert "HERMES_HOME" in os.environ
