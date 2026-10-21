import json
from pathlib import Path

from hermes_redteam.store import attack_file_add, open_engagement, reserve_write


def test_attack_file_list_returns_paths(tmp_path: Path):
    from hermes_redteam.store import attack_file_list

    open_engagement(tmp_path, "lab-01", "Lab 01")
    reserve_write(tmp_path, "lab-01", "rt-exploit")
    attack_file_add(tmp_path, "lab-01", "range-web", "raw/files/range-web.txt")

    found = json.loads(attack_file_list(tmp_path, "lab-01"))

    assert found["ok"] is True
    assert found["count"] == 1
    assert found["files"][0] == {
        "asset_key": "range-web",
        "relative_path": "raw/files/range-web.txt",
    }
