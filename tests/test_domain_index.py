import json
from pathlib import Path

from hermes_redteam.store import add_asset, open_engagement, reserve_write


def test_domain_index_groups_hosts_by_domain(tmp_path: Path):
    from hermes_redteam.store import domain_index

    open_engagement(tmp_path, "lab-01", "Lab 01")
    reserve_write(tmp_path, "lab-01", "rt-recon")
    add_asset(tmp_path, "lab-01", "a", "a.example.test", "new")
    add_asset(tmp_path, "lab-01", "b", "b.example.test", "new")

    found = json.loads(domain_index(tmp_path, "lab-01"))

    assert found["ok"] is True
    assert found["domains"]["example.test"] == ["a.example.test", "b.example.test"]
