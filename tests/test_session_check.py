import json
from pathlib import Path

from hermes_redteam.store import (
    open_engagement,
    reserve_write,
    tunnel_add,
    webshell_add,
)


def test_session_check_marks_existing_entries_checked(tmp_path: Path):
    from hermes_redteam.store import session_check

    open_engagement(tmp_path, "lab-01", "Lab 01")
    reserve_write(tmp_path, "lab-01", "rt-exploit")
    webshell_add(tmp_path, "lab-01", "range-web", "behinder", "raw/shell/range-web.txt")
    tunnel_add(tmp_path, "lab-01", "range-web", "http", "raw/tunnel/range-web.txt")

    found = json.loads(session_check(tmp_path, "lab-01"))

    assert found["ok"] is True
    assert found["webshells"] == 1
    assert found["tunnels"] == 1
    assert found["status"] == "checked"
