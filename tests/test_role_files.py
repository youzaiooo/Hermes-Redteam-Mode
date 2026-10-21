from pathlib import Path


def test_every_execution_role_file_exists():
    root = Path("roles")
    names = ["rt-recon", "rt-asset", "rt-vuln", "rt-exploit", "rt-internal"]

    for name in names:
        text = (root / f"{name}.md").read_text(encoding="utf-8")
        assert name in text
        assert "payload" not in text.lower() or name == "rt-exploit"
