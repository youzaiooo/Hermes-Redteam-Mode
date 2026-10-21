from pathlib import Path

from hermes_redteam.store import open_engagement, write_report_index


def test_report_index_lists_existing_sections(tmp_path: Path):
    open_engagement(tmp_path, "lab-01", "Lab 01")

    path = Path(write_report_index(tmp_path, "lab-01"))
    text = path.read_text(encoding="utf-8")

    assert "authorization.md" in text
    assert "index.db" in text
    assert "payload" not in text
