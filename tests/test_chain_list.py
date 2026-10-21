import json
from pathlib import Path

from hermes_redteam.store import chain_add, open_engagement, reserve_write


def test_chain_list_returns_paths_and_results(tmp_path: Path):
    from hermes_redteam.store import chain_list

    open_engagement(tmp_path, "lab-01", "Lab 01")
    reserve_write(tmp_path, "lab-01", "rt-exploit")
    chain_add(tmp_path, "lab-01", "range-web", "raw/chain/range-web.txt", "confirmed")

    found = json.loads(chain_list(tmp_path, "lab-01"))

    assert found["ok"] is True
    assert found["count"] == 1
    step = found["steps"][0]
    assert step["asset_key"] == "range-web"
    assert step["command_path"] == "raw/chain/range-web.txt"
    assert step["result"] == "confirmed"
    assert step["stage_code"] == ""
    assert step["tool"] == ""
    assert step["summary"] == ""
    assert step["created_at"]
