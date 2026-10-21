import json
from pathlib import Path

from hermes_redteam.tools import asset_add, session_bind


def test_write_handler_reads_session_id_from_kwargs(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("HERMES_HOME", str(tmp_path))
    from hermes_redteam.store import open_engagement, reserve_write

    root = tmp_path / "redteam" / "engagements"
    open_engagement(root, "lab-01", "Lab 01")
    reserve_write(root, "lab-01", "rt-recon")
    session_bind({"id": "lab-01", "profile": "rt-recon"}, session_id="s-1")

    accepted = json.loads(
        asset_add(
            {"id": "lab-01", "stable_key": "host-a", "address": "127.0.0.1"},
            session_id="s-1",
        )
    )

    assert accepted["ok"] is True
    assert accepted["stable_key"] == "host-a"


def test_kwargs_session_wins_over_args_session(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("HERMES_HOME", str(tmp_path))
    from hermes_redteam.store import open_engagement, reserve_write

    root = tmp_path / "redteam" / "engagements"
    open_engagement(root, "lab-01", "Lab 01")
    reserve_write(root, "lab-01", "rt-recon")
    session_bind({"id": "lab-01", "session_id": "good", "profile": "rt-recon"})

    rejected = json.loads(
        asset_add(
            {
                "id": "lab-01",
                "stable_key": "host-a",
                "address": "127.0.0.1",
                "session_id": "stale",
            },
            session_id="good",
        )
    )

    assert rejected["ok"] is True
