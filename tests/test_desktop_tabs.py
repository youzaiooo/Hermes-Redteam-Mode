from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_desktop_plugin_registers_nine_tabs():
    text = (ROOT / "desktop" / "plugin.js").read_text(encoding="utf-8")
    for tab in (
        "board",
        "assets",
        "findings",
        "sessions",
        "tunnels",
        "score",
        "skills",
        "roles",
        "report",
    ):
        assert f"'{tab}'" in text
