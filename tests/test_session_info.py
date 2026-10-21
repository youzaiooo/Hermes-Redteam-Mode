import json
from pathlib import Path

from hermes_redteam.store import bind_session, open_engagement


def test_session_info_returns_bound_profile(tmp_path: Path):
    from hermes_redteam.store import session_info

    open_engagement(tmp_path, "lab-01", "Lab 01")
    bind_session(tmp_path, "lab-01", "s-1", "rt-recon")

    found = json.loads(session_info(tmp_path, "lab-01"))

    assert found["ok"] is True
    assert found["session_id"] == "s-1"
    assert found["profile"] == "rt-recon"
