from pathlib import Path

from hermes_redteam.store import open_engagement, write_report_skeleton


def test_report_skeleton_has_sections_not_findings(tmp_path: Path):
    open_engagement(tmp_path, "lab-01", "Lab 01")

    path = write_report_skeleton(tmp_path, "lab-01")
    text = Path(path).read_text(encoding="utf-8")

    assert "授权" in text
    assert "资产" in text
    assert "证据路径" in text
    assert "payload" not in text.lower()
