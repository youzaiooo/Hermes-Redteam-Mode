from pathlib import Path

from hermes_redteam.score import read_score_mode, write_score_mode


def test_score_mode_round_trip_defaults_off(tmp_path: Path):
    assert read_score_mode(tmp_path) == "off"

    write_score_mode(tmp_path, "visible")

    assert read_score_mode(tmp_path) == "visible"
    text = (tmp_path / "config.yaml").read_text(encoding="utf-8")
    assert "plugins.entries.hermes-redteam.score_rules: visible" in text
    assert "password" not in text
