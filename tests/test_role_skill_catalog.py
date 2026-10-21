from pathlib import Path

from hermes_redteam import register


class _Ctx:
    def __init__(self, profile: str):
        self.profile_name = profile
        self.skills = []

    def register_tool(self, name, **kwargs):
        del name, kwargs

    def register_skill(self, name, path, **kwargs):
        del kwargs
        self.skills.append((name, Path(path).name))


def test_recon_registers_recon_skills_not_exploit_skills():
    ctx = _Ctx("rt-recon")

    register(ctx)

    names = {name for name, _path in ctx.skills}
    assert "fofa-recon" in names
    assert "active-scan" in names
    assert "webshell-toolkit" not in names
    assert "lateral-movement" not in names
