import json
from pathlib import Path

from hermes_redteam.store import add_asset, open_engagement, reserve_write


def test_default_profile_cannot_reserve_or_write(tmp_path: Path):
    open_engagement(tmp_path, "lab-01", "Lab 01")

    reserved = json.loads(reserve_write(tmp_path, "lab-01", "default"))
    written = json.loads(add_asset(tmp_path, "lab-01", "host-a", "10.0.0.8"))

    assert reserved["ok"] is False
    assert reserved["error"] == "invalid_input"
    assert written["error"] == "reservation_required"
