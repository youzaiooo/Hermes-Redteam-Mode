from hermes_redteam import register


class _Ctx:
    def __init__(self, profile: str):
        self.profile_name = profile
        self.tools = []

    def register_tool(self, name, **kwargs):
        self.tools.append(name)

    def register_skill(self, name, path, **kwargs):
        return None


def test_rt_exploit_registers_access_and_credential_tools():
    ctx = _Ctx("rt-exploit")

    register(ctx)

    assert "redteam_access_add" in ctx.tools
    assert "redteam_credential_add" in ctx.tools
    assert "redteam_vuln_add" not in ctx.tools
