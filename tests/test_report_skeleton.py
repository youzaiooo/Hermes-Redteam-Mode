from pathlib import Path

from hermes_redteam.store import open_engagement


def test_report_skeleton_has_seven_sections(tmp_path: Path):
    from hermes_redteam.store import write_report_skeleton

    open_engagement(tmp_path, "lab-01", "Lab 01")
    path = Path(write_report_skeleton(tmp_path, "lab-01"))
    text = path.read_text(encoding="utf-8")

    for title in ("结论", "证据与范围", "根因与前提", "验证结果", "影响与检测", "修复与验证建议", "不确定性与后续工作"):
        assert title in text
