import json
from pathlib import Path

from hermes_redteam.store import (
    add_asset,
    open_engagement,
    reserve_write,
    vuln_add,
    access_add,
    tunnel_add,
)


def test_attack_chain_returns_five_stage_counts(tmp_path: Path):
    from hermes_redteam.store import attack_chain

    open_engagement(tmp_path, "lab-01", "Lab 01")
    reserve_write(tmp_path, "lab-01", "rt-exploit")
    add_asset(tmp_path, "lab-01", "range-web", "http://127.0.0.1:8765", "new")
    vuln_add(tmp_path, "lab-01", "range-web", "suspected", "raw/vuln/range-web.txt")
    access_add(tmp_path, "lab-01", "range-web", "web-login", "raw/access/range-web.txt")
    tunnel_add(tmp_path, "lab-01", "range-web", "http", "raw/tunnel/range-web.txt")

    found = json.loads(attack_chain(tmp_path, "lab-01"))

    assert found["ok"] is True
    assert [item["stage"] for item in found["stages"]] == [
        "recon",
        "vuln",
        "access",
        "tunnel",
        "report",
    ]
    assert found["stages"][0]["count"] == 1
