import json
from pathlib import Path

from hermes_redteam.store import role_prompt

ROOT = Path(__file__).resolve().parents[1]


def test_role_prompt_reads_existing_role_file():
    found = json.loads(role_prompt(ROOT, "rt-recon"))

    assert found["ok"] is True
    assert found["role"] == "rt-recon"
    assert "只写资产指针" in found["text"]
