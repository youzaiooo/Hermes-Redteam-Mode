import json
from pathlib import Path

from hermes_redteam.store import bind_session, open_engagement


def test_bind_records_session_and_rejects_unknown(tmp_path: Path):
    open_engagement(tmp_path, "lab-01", "Lab 01")

    bound = json.loads(bind_session(tmp_path, "lab-01", "sess-1", "default"))
    missing = json.loads(bind_session(tmp_path, "no-such", "sess-1", "default"))

    assert bound["ok"] is True
    assert bound["engagement_id"] == "lab-01"
    assert bound["session_id"] == "sess-1"
    assert missing["ok"] is False
    assert missing["error"] == "not_found"

    state = json.loads((tmp_path / "lab-01" / "session.json").read_text(encoding="utf-8"))
    assert state["session_id"] == "sess-1"
    assert state["profile"] == "default"
