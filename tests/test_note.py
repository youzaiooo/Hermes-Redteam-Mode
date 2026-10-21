import json
from pathlib import Path

from hermes_redteam.store import open_engagement, reserve_write


def test_note_add_stores_pointer_not_body(tmp_path: Path):
    from hermes_redteam.store import note_add

    open_engagement(tmp_path, "lab-01", "Lab 01")
    reserve_write(tmp_path, "lab-01", "rt-recon")

    found = json.loads(note_add(tmp_path, "lab-01", "range-web", "wiki/pages/range-web.md"))

    assert found["ok"] is True
    assert found["path"] == "wiki/pages/range-web.md"
    assert "body" not in found
