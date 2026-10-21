import json
from pathlib import Path

from hermes_redteam.store import open_engagement, reserve_write, score_point_save


def test_score_point_get_returns_saved_category(tmp_path: Path):
    from hermes_redteam.store import score_point_get

    open_engagement(tmp_path, "lab-01", "Lab 01")
    reserve_write(tmp_path, "lab-01", "rt-exploit")
    score_point_save(tmp_path, "lab-01", "web-app", "access")

    found = json.loads(score_point_get(tmp_path, "lab-01", "web-app"))

    assert found["ok"] is True
    assert found["category"] == "access"
