import json
from pathlib import Path

from hermes_redteam.store import open_engagement, reserve_write, webshell_add


def test_webshell_list_and_update_keep_path_only(tmp_path: Path):
    from hermes_redteam.store import webshell_list, webshell_update

    open_engagement(tmp_path, "lab-01", "Lab 01")
    reserve_write(tmp_path, "lab-01", "rt-exploit")
    webshell_add(tmp_path, "lab-01", "range-web", "godzilla", "raw/shell/range-web.txt")

    updated = json.loads(webshell_update(tmp_path, "lab-01", "range-web", "checked"))
    found = json.loads(webshell_list(tmp_path, "lab-01"))

    assert updated["ok"] is True
    assert found["count"] == 1
    assert found["shells"][0]["status"] == "checked"
    assert "password" not in json.dumps(found)
