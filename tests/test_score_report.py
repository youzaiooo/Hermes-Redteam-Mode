from pathlib import Path

from hermes_redteam.store import open_engagement, reserve_write, score_hit


def test_score_report_lists_score_paths(tmp_path: Path):
    from hermes_redteam.store import write_score_report

    open_engagement(tmp_path, "lab-01", "Lab 01")
    reserve_write(tmp_path, "lab-01", "rt-exploit")
    score_hit(tmp_path, "lab-01", "web-app", "raw/score/range-web.txt")

    path = Path(write_score_report(tmp_path, "lab-01"))
    text = path.read_text(encoding="utf-8")

    assert "web-app" in text
    assert "raw/score/range-web.txt" in text
    assert "payload" not in text
