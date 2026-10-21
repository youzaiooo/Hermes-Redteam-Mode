import json
from pathlib import Path

from hermes_redteam.store import open_engagement, reserve_write


def test_webshell_add_stores_type_and_path(tmp_path: Path):
    from hermes_redteam.store import webshell_add

    open_engagement(tmp_path, "lab-01", "Lab 01")
    reserve_write(tmp_path, "lab-01", "rt-exploit")

    saved = json.loads(
        webshell_add(tmp_path, "lab-01", "range-web", "behinder", "raw/shell/range-web.txt")
    )

    assert saved["ok"] is True
    assert saved["shell_type"] == "behinder"
    assert "password" not in saved
