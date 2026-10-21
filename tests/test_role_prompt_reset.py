import json
from pathlib import Path

from hermes_redteam.store import role_prompt_reset

ROOT = Path(__file__).resolve().parents[1]


def test_role_prompt_reset_restores_file(tmp_path: Path):
    source = ROOT
    role_dir = tmp_path / "roles"
    role_dir.mkdir()
    (role_dir / "rt-recon.md").write_text("changed\n", encoding="utf-8")

    found = json.loads(role_prompt_reset(tmp_path, "rt-recon", source))

    assert found["ok"] is True
    assert "信息收集执行角色" in (role_dir / "rt-recon.md").read_text(encoding="utf-8")
