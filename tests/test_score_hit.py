import json
from pathlib import Path

from hermes_redteam.score import record_score
from hermes_redteam.store import open_engagement, reserve_write


def test_score_hit_stores_rule_and_path(tmp_path: Path):
    from hermes_redteam.store import score_hit

    open_engagement(tmp_path, "lab-01", "Lab 01")
    reserve_write(tmp_path, "lab-01", "rt-exploit")
    record_score(tmp_path, "lab-01", "visible", "web-app")

    found = json.loads(
        score_hit(tmp_path, "lab-01", "web-app", "raw/score/range-web.txt")
    )

    assert found["ok"] is True
    assert found["rule_id"] == "web-app"
    assert found["evidence_path"] == "raw/score/range-web.txt"
