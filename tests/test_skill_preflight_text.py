from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_preflight_skill_lists_required_tools():
    text = (ROOT / "skills" / "redteam-preflight" / "SKILL.md").read_text(encoding="utf-8")
    for name in ("nmap", "nuclei", "sqlmap", "ffuf"):
        assert name in text
    assert "不自动安装" in text
