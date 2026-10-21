from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_desktop_panel_uses_chinese_labels():
    text = (ROOT / "desktop" / "plugin.js").read_text(encoding="utf-8")
    for label in ("态势", "资产", "成果", "报告", "资源"):
        assert label in text
    assert "JSON.stringify(data)" not in text
    assert "no data" not in text
