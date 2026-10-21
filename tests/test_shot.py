import json
from pathlib import Path

from hermes_redteam.store import open_engagement, reserve_write


def test_shot_add_stores_image_path(tmp_path: Path):
    from hermes_redteam.store import shot_add

    open_engagement(tmp_path, "lab-01", "Lab 01")
    reserve_write(tmp_path, "lab-01", "rt-exploit")

    found = json.loads(shot_add(tmp_path, "lab-01", "range-web", "raw/shots/range-web.png"))

    assert found["ok"] is True
    assert found["path"] == "raw/shots/range-web.png"
    assert "data" not in found
