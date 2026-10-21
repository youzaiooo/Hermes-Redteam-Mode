import json
from pathlib import Path

from hermes_redteam.store import open_engagement, query_board


def test_board_returns_counts_not_secrets(tmp_path: Path):
    open_engagement(tmp_path, "lab-01", "Lab 01")

    board = json.loads(query_board(tmp_path, "lab-01"))

    assert board["ok"] is True
    assert board["assets"] == 0
    assert board["findings"] == 0
    assert "password" not in json.dumps(board)
