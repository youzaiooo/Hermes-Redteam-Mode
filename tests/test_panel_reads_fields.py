from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_panel_reads_current_engagement_and_counts():
    text = (ROOT / "desktop" / "plugin.js").read_text(encoding="utf-8")

    assert "host.state.activeSessionId" in text
    assert "'/engagements'" in text
    assert "`/engagements/for-session/${activeSessionId}`" in text
    assert "`/summary/${engagementId}`" in text
    assert "assets" in text
    assert "services" in text
    assert "vulns" in text
    assert "credentials" in text
    assert "tunnels" in text
    assert "score_hits" in text
    assert "stage" in text
    assert "还没有资产" in text
    assert "还没有成果" in text
    assert "加载失败" in text
