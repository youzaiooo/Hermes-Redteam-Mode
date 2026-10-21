from hermes_redteam import register


class _Ctx:
    def __init__(self, profile: str):
        self.profile_name = profile
        self.tools = []

    def register_tool(self, name, **kwargs):
        self.tools.append(name)

    def register_skill(self, name, path, **kwargs):
        return None


def test_rt_recon_does_not_register_finding_writer():
    ctx = _Ctx("rt-recon")

    register(ctx)

    assert "redteam_asset_add" in ctx.tools
    assert "redteam_finding_add" not in ctx.tools
