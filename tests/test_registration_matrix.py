from hermes_redteam import register


class _Ctx:
    def __init__(self, profile: str):
        self.profile_name = profile
        self.tools: list[str] = []

    def register_tool(self, name, **kwargs):
        del kwargs
        self.tools.append(name)

    def register_skill(self, name, path, **kwargs):
        del name, path, kwargs


def _registered(profile: str) -> list[str]:
    ctx = _Ctx(profile)
    register(ctx)
    return ctx.tools


def test_commander_gets_dispatch_only():
    tools = _registered("default")
    assert "redteam_dispatch" in tools
    assert "redteam_dispatch_status" in tools
    assert "redteam_asset_add" not in tools


def test_recon_role_tools():
    tools = _registered("rt-recon")
    assert "redteam_asset_add" in tools
    assert "redteam_scan_add" in tools
    assert "redteam_dispatch" not in tools
    assert "redteam_vuln_add" not in tools


def test_asset_role_tools():
    tools = _registered("rt-asset")
    assert "redteam_asset_assess" in tools
    assert "redteam_web_list" in tools
    assert "redteam_asset_add" not in tools


def test_vuln_role_tools():
    tools = _registered("rt-vuln")
    assert "redteam_vuln_add" in tools
    assert "redteam_vuln_query" in tools
    assert "redteam_poc_use" in tools
    assert "redteam_finding_add" in tools
    assert "redteam_asset_test" in tools
    assert "redteam_score_hit" in tools
    assert "redteam_asset_add" not in tools


def test_exploit_role_tools():
    tools = _registered("rt-exploit")
    assert "redteam_access_add" in tools
    assert "redteam_webshell_add" in tools
    assert "redteam_shot_add" in tools
    assert "redteam_score_hit" in tools
    assert "redteam_vuln_add" not in tools


def test_internal_role_tools():
    tools = _registered("rt-internal")
    assert "redteam_tunnel_add" in tools
    assert "redteam_tunnel_update" in tools
    assert "redteam_asset_add" in tools
    assert "redteam_chain_add" in tools
    assert "redteam_webshell_add" not in tools
