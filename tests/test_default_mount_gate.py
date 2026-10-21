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


def test_default_profile_registers_no_execution_tools_or_skills():
    ctx = _Ctx("default")

    register(ctx)

    assert ctx.tools == []
    assert ctx.skills == []
