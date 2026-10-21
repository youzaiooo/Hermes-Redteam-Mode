import json
from pathlib import Path

from hermes_redteam.store import open_engagement, reserve_write


def test_knowledge_add_stores_pointer_not_body(tmp_path: Path):
    from hermes_redteam.store import knowledge_add

    open_engagement(tmp_path, "lab-01", "Lab 01")
    reserve_write(tmp_path, "lab-01", "rt-vuln")

    found = json.loads(
        knowledge_add(tmp_path, "lab-01", "range-web", "wiki/knowledge/range-web.md")
    )

    assert found["ok"] is True
    assert found["path"] == "wiki/knowledge/range-web.md"
    assert "body" not in found
