import json
from pathlib import Path

from hermes_redteam.store import open_engagement, reserve_write, shot_add


def test_shot_list_and_delete_keep_paths_only(tmp_path: Path):
    from hermes_redteam.store import shot_delete, shot_list

    open_engagement(tmp_path, "lab-01", "Lab 01")
    reserve_write(tmp_path, "lab-01", "rt-exploit")
    shot_add(tmp_path, "lab-01", "range-web", "raw/shots/range-web.png")

    listed = json.loads(shot_list(tmp_path, "lab-01"))
    deleted = json.loads(shot_delete(tmp_path, "lab-01", "raw/shots/range-web.png"))
    after = json.loads(shot_list(tmp_path, "lab-01"))

    assert listed["count"] == 1
    assert deleted["ok"] is True
    assert after["count"] == 0
