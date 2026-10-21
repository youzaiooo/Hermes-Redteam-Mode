import json
from pathlib import Path

from hermes_redteam.store import credential_add, open_engagement, reserve_write


def test_credential_list_returns_paths_not_secrets(tmp_path: Path):
    from hermes_redteam.store import credential_list

    open_engagement(tmp_path, "lab-01", "Lab 01")
    reserve_write(tmp_path, "lab-01", "rt-exploit")
    credential_add(tmp_path, "lab-01", "range-web", "raw/cred/range-web.txt")

    found = json.loads(credential_list(tmp_path, "lab-01"))

    assert found["ok"] is True
    assert found["count"] == 1
    assert found["credentials"][0]["evidence_path"] == "raw/cred/range-web.txt"
    assert "secret" not in json.dumps(found)
