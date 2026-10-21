import pytest
from types import SimpleNamespace

from hermes_redteam import register

pytest.importorskip("hermes_cli")


def test_execution_profile_registers_declared_tools(monkeypatch):
    monkeypatch.setattr(
        "hermes_cli.profiles.get_active_profile_name",
        lambda: "rt-vuln",
    )
    from hermes_cli.plugins import PluginContext

    seen = []
    ctx = PluginContext.__new__(PluginContext)
    ctx._manager = SimpleNamespace(scope_key="rt-vuln")
    ctx.register_tool = lambda name, **kwargs: seen.append(name)

    register(ctx)

    assert "redteam_finding_add" in seen
    assert "redteam_score_record" not in seen
