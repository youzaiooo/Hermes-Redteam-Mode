from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_desktop_plugin_registers_five_tabs():
    text = (ROOT / "desktop" / "plugin.js").read_text(encoding="utf-8")
    for tab in (
        "situation",
        "assets",
        "results",
        "report",
        "resources",
    ):
        assert f"'{tab}'" in text
