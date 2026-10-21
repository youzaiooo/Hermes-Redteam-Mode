import json
from pathlib import Path

from hermes_redteam.store import open_engagement, reserve_write


def test_score_point_save_stores_point_id(tmp_path: Path):
    from hermes_redteam.store import score_point_save

    open_engagement(tmp_path, "lab-01", "Lab 01")
    reserve_write(tmp_path, "lab-01", "rt-exploit")

    found = json.loads(score_point_save(tmp_path, "lab-01", "web-app", "access"))

    assert found["ok"] is True
    assert found["point_id"] == "web-app"
    assert found["category"] == "access"
