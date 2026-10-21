from hermes_redteam import register


class _Ctx:
    def __init__(self, profile: str):
        self.profile_name = profile
        self.tools = []

    def register_tool(self, name, **kwargs):
        self.tools.append(name)

    def register_skill(self, name, path, **kwargs):
        return None


def test_default_registers_commander_tools():
    ctx = _Ctx("default")

    register(ctx)

    assert "redteam_dispatch" in ctx.tools
    assert "redteam_dispatch_status" in ctx.tools
    assert "redteam_engagement_open" in ctx.tools
    assert "redteam_asset_add" not in ctx.tools


def test_execution_profile_registers_write_tools():
    ctx = _Ctx("rt-asset")

    register(ctx)

    assert "redteam_asset_assess" in ctx.tools
    assert "redteam_asset_link" in ctx.tools
    assert "redteam_asset_get" in ctx.tools
    assert "redteam_asset_add" not in ctx.tools
    assert "redteam_finding_add" not in ctx.tools
    assert "redteam_score_record" not in ctx.tools
