import json
from pathlib import Path

from hermes_redteam.store import access_add, credential_add, open_engagement, reserve_write


def test_sessions_lists_access_and_credential_counts(tmp_path: Path):
    from hermes_redteam.store import sessions

    open_engagement(tmp_path, "lab-01", "Lab 01")
    reserve_write(tmp_path, "lab-01", "rt-exploit")
    access_add(tmp_path, "lab-01", "range-web", "web-login", "raw/access/range-web.txt")
    credential_add(tmp_path, "lab-01", "range-web", "raw/cred/range-web.txt")

    found = json.loads(sessions(tmp_path, "lab-01"))

    assert found["ok"] is True
    assert found["access"] == 1
    assert found["credentials"] == 1
    assert "secret" not in json.dumps(found)
