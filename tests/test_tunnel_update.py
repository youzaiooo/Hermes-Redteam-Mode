import json
from pathlib import Path

from hermes_redteam.store import open_engagement, reserve_write, tunnel_add


def test_tunnel_update_changes_status_without_command(tmp_path: Path):
    from hermes_redteam.store import tunnel_update

    open_engagement(tmp_path, "lab-01", "Lab 01")
    reserve_write(tmp_path, "lab-01", "rt-internal")
    tunnel_add(tmp_path, "lab-01", "range-web", "http", "raw/tunnel/range-web.txt")

    found = json.loads(tunnel_update(tmp_path, "lab-01", "range-web", "checked"))

    assert found["ok"] is True
    assert found["status"] == "checked"
    assert "command" not in found
