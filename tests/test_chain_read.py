import json
from pathlib import Path

from hermes_redteam.store import chain_add, open_engagement, reserve_write


def test_chain_read_returns_steps(tmp_path: Path):
    from hermes_redteam.store import chain_read

    open_engagement(tmp_path, "lab-01", "Lab 01")
    reserve_write(tmp_path, "lab-01", "rt-exploit")
    chain_add(tmp_path, "lab-01", "range-web", "raw/chain/range-web.txt", "confirmed")

    found = json.loads(chain_read(tmp_path, "lab-01"))

    assert found["ok"] is True
    assert found["count"] == 1
    assert found["steps"][0]["result"] == "confirmed"
