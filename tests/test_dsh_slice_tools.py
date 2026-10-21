from hermes_redteam import register


class _Ctx:
    def __init__(self, profile: str):
        self.profile_name = profile
        self.tools = []

    def register_tool(self, name, **kwargs):
        self.tools.append(name)

    def register_skill(self, name, path, **kwargs):
        return None


def test_rt_vuln_registers_http_evidence_and_vuln_tools():
    ctx = _Ctx("rt-vuln")

    register(ctx)

    assert "redteam_http_evidence_add" in ctx.tools
    assert "redteam_vuln_add" in ctx.tools
    assert "redteam_credential_add" not in ctx.tools
