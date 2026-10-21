import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_dashboard_manifest_lists_nine_tabs():
    found = json.loads((ROOT / "dashboard" / "manifest.json").read_text(encoding="utf-8"))

    assert found["tabs"] == [
        "board",
        "assets",
        "findings",
        "sessions",
        "tunnels",
        "score",
        "skills",
        "roles",
        "report",
    ]
