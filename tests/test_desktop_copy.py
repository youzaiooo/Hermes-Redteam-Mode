from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_desktop_panel_uses_chinese_labels():
    text = (ROOT / "desktop" / "plugin.js").read_text(encoding="utf-8")
    for label in ("总览", "资产", "漏洞", "会话", "隧道", "得分", "技能", "角色", "报告"):
        assert label in text
    assert "JSON.stringify(data)" not in text
    assert "no data" not in text
