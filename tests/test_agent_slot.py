import json
from pathlib import Path

from hermes_redteam.store import open_engagement, reserve_write


def test_agent_slot_reports_three_cap(tmp_path: Path):
    from hermes_redteam.store import agent_slot

    open_engagement(tmp_path, "lab-01", "Lab 01")
    reserve_write(tmp_path, "lab-01", "rt-recon")

    found = json.loads(agent_slot(tmp_path, "lab-01"))

    assert found["ok"] is True
    assert found["cap"] == 3
    assert found["used"] == 1
    assert found["free"] == 2
