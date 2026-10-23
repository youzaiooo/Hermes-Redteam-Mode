from hermes_redteam import register


class _Ctx:
    def __init__(self, profile: str):
        self.profile_name = profile
        self.tools = []
        self.skills = []

    def register_tool(self, name, **kwargs):
        del kwargs
        self.tools.append(name)

    def register_skill(self, name, path, **kwargs):
        del path, kwargs
        self.skills.append(name)


def test_default_profile_registers_commander_tools_and_setup_skills():
    ctx = _Ctx("default")

    register(ctx)

    assert "redteam_dispatch" in ctx.tools
    assert "redteam_asset_add" not in ctx.tools
    assert "redteam-setup" in ctx.skills
    assert "redteam-commander" in ctx.skills
    assert "rt-recon" not in ctx.skills
