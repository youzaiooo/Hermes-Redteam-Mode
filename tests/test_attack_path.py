import json
from pathlib import Path

from hermes_redteam.store import asset_link, open_engagement, reserve_write


def test_attack_path_returns_asset_links(tmp_path: Path):
    from hermes_redteam.store import attack_path

    open_engagement(tmp_path, "lab-01", "Lab 01")
    reserve_write(tmp_path, "lab-01", "rt-asset")
    asset_link(tmp_path, "lab-01", "range-web", "range-app", "leads-to")

    found = json.loads(attack_path(tmp_path, "lab-01"))

    assert found["ok"] is True
    assert found["count"] == 1
    assert found["links"][0]["relation"] == "leads-to"
