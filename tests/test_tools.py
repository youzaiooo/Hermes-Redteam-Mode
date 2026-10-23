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


def test_engagement_open_binds_session_and_auto_dispatches_recon(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("HERMES_HOME", str(tmp_path))
    import hermes_redteam.tools as tools

    monkeypatch.setattr(
        tools,
        "dispatch",
        lambda args, session_id="": json.dumps({"ok": True, "task_id": "t_auto", "assignee": "rt-recon"}),
    )
    opened = json.loads(
        tools.engagement_open(
            {"id": "auto-01", "display_name": "10.0.0.1"}, session_id="s-auto"
        )
    )
    state = json.loads(
        (tmp_path / "redteam" / "engagements" / "auto-01" / "session.json").read_text()
    )
    assert opened["ok"] is True
    assert opened["session_bound"] is True
    assert opened["auto_task"]["task_id"] == "t_auto"
    assert state["session_id"] == "s-auto"


def test_pre_tool_call_blocks_commander_but_not_worker(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("HERMES_HOME", str(tmp_path))
    from hermes_redteam import _pre_tool_call

    from hermes_redteam.store import bind_session, open_engagement

    root = tmp_path / "redteam" / "engagements"
    open_engagement(root, "hook-01", "10.0.0.2")
    bind_session(root, "hook-01", "s-hook", "default")
    monkeypatch.setattr("hermes_redteam._profile_name", lambda ctx=None: "default")
    blocked = _pre_tool_call("terminal", session_id="s-hook")
    assert blocked and blocked["action"] == "block"
    assert "redteam_dispatch" in blocked["message"]
    monkeypatch.setattr("hermes_redteam._profile_name", lambda ctx=None: "rt-recon")
    assert _pre_tool_call("terminal", session_id="s-hook") is None
    assert _pre_tool_call("read_file", session_id="s-hook") is None
