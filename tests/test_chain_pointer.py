import json
from pathlib import Path

from hermes_redteam.store import open_engagement, reserve_write


def test_chain_add_stores_command_pointer_not_command(tmp_path: Path):
    from hermes_redteam.store import chain_add

    open_engagement(tmp_path, "lab-01", "Lab 01")
    reserve_write(tmp_path, "lab-01", "rt-exploit")

    saved = json.loads(
        chain_add(
            tmp_path,
            "lab-01",
            "range-web",
            "raw/chain/range-web.txt",
            "confirmed",
            extra={"tool": "not-stored"},
        )
    )

    assert saved["ok"] is False
    assert saved["error"] == "secret_field"
