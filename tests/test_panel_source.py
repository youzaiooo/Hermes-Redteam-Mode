from pathlib import Path


def test_panel_polls_readonly_route_and_stays_opt_in():
    text = Path("desktop/plugin.js").read_text(encoding="utf-8")

    assert "defaultEnabled: false" in text
    assert "rest('/engagements/current')" in text
    assert "ctx.rest" in text
    assert "setInterval" in text
    assert "register_tool" not in text
    assert "register_skill" not in text
