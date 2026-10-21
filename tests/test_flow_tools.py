from hermes_redteam import register


class _Ctx:
    def __init__(self, profile: str):
        self.profile_name = profile
        self.tools = []

    def register_tool(self, name, **kwargs):
        self.tools.append(name)

    def register_skill(self, name, path, **kwargs):
        return None


def test_rt_internal_registers_tunnel_tool_only():
    ctx = _Ctx("rt-internal")

    register(ctx)

    assert "redteam_tunnel_add" in ctx.tools
    assert "redteam_vuln_update" not in ctx.tools
