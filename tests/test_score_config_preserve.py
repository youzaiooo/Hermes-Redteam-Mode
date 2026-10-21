from pathlib import Path

from hermes_redteam.score import read_score_mode, write_score_mode


def test_score_mode_updates_only_its_key(tmp_path: Path):
    config = tmp_path / "config.yaml"
    config.write_text("model: grok\nscore_rules: off\n", encoding="utf-8")

    write_score_mode(tmp_path, "visible")

    text = config.read_text(encoding="utf-8")
    assert "model: grok" in text
    assert read_score_mode(tmp_path) == "visible"
