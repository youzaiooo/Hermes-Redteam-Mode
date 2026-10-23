from pathlib import Path

from hermes_redteam import register


class _Ctx:
    def __init__(self, profile: str):
        self.profile_name = profile
        self.skills = []
        self.tools = []

    def register_tool(self, name, **kwargs):
        self.tools.append(name)

    def register_skill(self, name, path, **kwargs):
        self.skills.append((name, Path(path).name))


def test_execution_profile_registers_only_its_role(monkeypatch):
    ctx = _Ctx("rt-recon")
    monkeypatch.setattr("hermes_redteam.register_skill_file", ctx.register_skill, raising=False)

    register(ctx)

    assert ("rt-recon", "rt-recon.md") in ctx.skills
    assert all("exploit" not in name for name, _path in ctx.skills)
