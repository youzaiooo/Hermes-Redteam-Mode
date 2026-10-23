"""hermes-redteam plugin registration. Commander plus five role profiles."""

from __future__ import annotations

from pathlib import Path

_COMMANDER_TOOLS = frozenset(
    {
        "redteam_engagement_open",
        "redteam_session_bind",
        "redteam_session_info",
        "redteam_preflight",
        "redteam_asset_query",
        "redteam_asset_get",
        "redteam_asset_stats",
        "redteam_chain",
        "redteam_chain_list",
        "redteam_attack_chain",
        "redteam_attack_path",
        "redteam_score_list",
        "redteam_score_report",
        "redteam_report_index",
        "redteam_report_export",
        "redteam_sessions",
        "redteam_agent_slot",
        "redteam_dispatch",
        "redteam_dispatch_status",
    }
)

_SHARED_READS = frozenset(
    {
        "redteam_engagement_open",
        "redteam_session_bind",
        "redteam_session_info",
        "redteam_preflight",
        "redteam_asset_query",
        "redteam_asset_get",
        "redteam_asset_stats",
    }
)

_ROLE_TOOLS = {
    "rt-recon": frozenset(
        {
            "redteam_asset_add",
            "redteam_asset_test",
            "redteam_asset_link",
            "redteam_asset_graph",
            "redteam_evidence_add",
            "redteam_scan_add",
            "redteam_scan_list",
            "redteam_note_add",
            "redteam_note_list",
            "redteam_domain_index",
        }
    ),
    "rt-asset": frozenset(
        {
            "redteam_asset_assess",
            "redteam_asset_link",
            "redteam_asset_timeline",
            "redteam_web_list",
            "redteam_asset_get",
            "redteam_asset_test",
        }
    ),
    "rt-vuln": frozenset(
        {
            "redteam_finding_add",
            "redteam_vuln_add",
            "redteam_vuln_query",
            "redteam_vuln_update",
            "redteam_http_evidence_add",
            "redteam_poc_add",
            "redteam_poc_search",
            "redteam_poc_use",
            "redteam_knowledge_add",
            "redteam_knowledge_list",
            "redteam_asset_test",
            "redteam_score_hit",
        }
    ),
    "rt-exploit": frozenset(
        {
            "redteam_access_add",
            "redteam_access_list",
            "redteam_credential_add",
            "redteam_credential_list",
            "redteam_sessions",
            "redteam_chain_add",
            "redteam_chain_list",
            "redteam_webshell_add",
            "redteam_webshell_update",
            "redteam_webshell_list",
            "redteam_tunnel_add",
            "redteam_tunnel_list",
            "redteam_shot_add",
            "redteam_shot_list",
            "redteam_shot_delete",
            "redteam_attack_file_add",
            "redteam_attack_file_list",
            "redteam_score_hit",
        }
    ),
    "rt-internal": frozenset(
        {
            "redteam_evidence_add",
            "redteam_asset_add",
            "redteam_tunnel_add",
            "redteam_tunnel_update",
            "redteam_tunnel_list",
            "redteam_chain_add",
            "redteam_chain_list",
            "redteam_score_hit",
        }
    ),
}

_ROLE_SKILLS = {
    "rt-recon": (
        "fofa-recon",
        "passive-recon",
        "deepseek-web-intel",
        "recon-pipeline",
        "active-scan",
        "web-fingerprint",
        "asset-correlation",
        "browser-automation",
        "kimi-webbridge",
        "cn-proxy-pool",
    ),
    "rt-asset": ("asset-correlation", "score-coverage"),
    "rt-vuln": ("nuclei-scan", "dir-bruteforce", "unauth-exploit", "cn-proxy-pool"),
    "rt-exploit": (
        "webshell-toolkit",
        "credential-attack",
        "shell-handler",
        "vps-reverse-shell",
        "score-coverage",
    ),
    "rt-internal": (
        "gogo-intranet",
        "fscan-intranet",
        "suo5-tunnel",
        "chisel-tunnel",
        "frp-tunnel",
        "lateral-movement",
    ),
}


def _profile_name(ctx=None) -> str:
    """Identity of the profile this registration runs for.

    Prefer an explicit ``ctx.profile_name`` when a host/test context provides one.
    ``PluginContext`` has no such attribute on Hermes 0.22.2, so fall back to the
    supported resolver ``hermes_cli.profiles.current_profile_name`` — it reads a
    bound HERMES_HOME override first, then the ``HERMES_PROFILE_NAME`` /
    ``HERMES_PROFILE`` pin a kanban worker inherits, then derives from HERMES_HOME
    (``default``, ``rt-*``, or ``custom`` for ad-hoc homes such as plugin doctor).
    """
    explicit = str(getattr(ctx, "profile_name", "") or "").strip() if ctx is not None else ""
    if explicit:
        return explicit
    try:
        from hermes_cli.profiles import current_profile_name

        name = (current_profile_name(default="default") or "default").strip()
    except Exception:
        name = "default"
    return name or "default"


def _allowed_for(profile: str) -> frozenset[str]:
    if profile == "default":
        return _COMMANDER_TOOLS
    if profile.startswith("rt-"):
        return _ROLE_TOOLS.get(profile, frozenset()) | _SHARED_READS
    # Doctor and ad-hoc homes resolve as "custom". Treat them as commander homes:
    # the surface is inspectable and a dispatch without a bound engagement fails
    # closed in the handler.
    return _COMMANDER_TOOLS


def register(ctx) -> None:
    profile = _profile_name(ctx)
    from .tools import TOOLS

    allowed = _allowed_for(profile)
    if not allowed:
        return

    for name, schema, handler in TOOLS:
        if name not in allowed:
            continue
        ctx.register_tool(
            name=name,
            toolset="hermes-redteam",
            schema=schema,
            handler=handler,
        )

    root = Path(__file__).resolve().parent
    ctx.register_skill("redteam-setup", root / "skills" / "redteam-setup" / "SKILL.md")

    if profile.startswith("rt-"):
        for name in _ROLE_SKILLS.get(profile, ()):
            ctx.register_skill(name, root / "skills" / name / "SKILL.md")
        role = root / "roles" / f"{profile}.md"
        if role.is_file():
            ctx.register_skill(profile, role)
    else:
        ctx.register_skill(
            "redteam-commander", root / "skills" / "redteam-commander" / "SKILL.md"
        )
