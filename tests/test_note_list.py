import json
from pathlib import Path

from hermes_redteam.store import note_add, open_engagement, reserve_write


def test_note_list_returns_saved_path(tmp_path: Path):
    from hermes_redteam.store import note_list

    open_engagement(tmp_path, "lab-01", "Lab 01")
    reserve_write(tmp_path, "lab-01", "rt-recon")
    note_add(tmp_path, "lab-01", "range-web", "wiki/pages/range-web.md")

    found = json.loads(note_list(tmp_path, "lab-01"))

    assert found["count"] == 1
    assert found["notes"][0]["path"] == "wiki/pages/range-web.md"
