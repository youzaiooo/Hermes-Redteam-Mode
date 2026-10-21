import json
from pathlib import Path

from hermes_redteam.store import open_engagement, reserve_write, tunnel_add


def test_tunnel_list_returns_entry_kind(tmp_path: Path):
    from hermes_redteam.store import tunnel_list

    open_engagement(tmp_path, "lab-01", "Lab 01")
    reserve_write(tmp_path, "lab-01", "rt-internal")
    tunnel_add(tmp_path, "lab-01", "range-web", "socks5", "raw/tunnel/range-web.txt")

    found = json.loads(tunnel_list(tmp_path, "lab-01"))

    assert found["ok"] is True
    assert found["count"] == 1
    assert found["tunnels"][0]["entry_kind"] == "socks5"
