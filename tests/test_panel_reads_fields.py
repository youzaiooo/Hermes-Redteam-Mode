from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_panel_reads_current_engagement_and_counts():
    text = (ROOT / "desktop" / "plugin.js").read_text(encoding="utf-8")

    assert "rest('/engagements/current')" in text
    assert "rest('/board/current')" not in text
    assert "asset_count" in text
    assert "finding_count" in text
    assert "vulns" in text
    assert ".catch(() => {})" not in text
    assert "加载失败" in text
