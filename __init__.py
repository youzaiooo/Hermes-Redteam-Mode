"""hermes-redteam plugin registration. P0 tools only."""

from __future__ import annotations

from pathlib import Path


def register(ctx) -> None:
    profile = str(getattr(ctx, "profile_name", "") or "")
    if not profile.startswith("rt-"):
        return
    from .tools import TOOLS

    allowed = {
        "rt-recon": {
            "redteam_asset_add",
            "redteam_asset_query",
            "redteam_asset_get",
            "redteam_asset_stats",
            "redteam_asset_test",
            "redteam_evidence_add",
            "redteam_domain_index",
            "redteam_scan_add",
            "redteam_scan_list",
            "redteam_note_add",
            "redteam_note_list",
        },
        "rt-asset": {
            "redteam_asset_add",
            "redteam_asset_query",
            "redteam_asset_get",
            "redteam_asset_stats",
            "redteam_asset_test",
            "redteam_asset_link",
            "redteam_asset_graph",
            "redteam_asset_assess",
            "redteam_asset_timeline",
            "redteam_web_list",
        },
        "rt-vuln": {
            "redteam_finding_add",
            "redteam_evidence_add",
            "redteam_vuln_add",
            "redteam_vuln_update",
            "redteam_http_evidence_add",
            "redteam_poc_add",
            "redteam_poc_search",
            "redteam_poc_list",
            "redteam_poc_get",
            "redteam_poc_update",
            "redteam_poc_use",
            "redteam_knowledge_add",
            "redteam_knowledge_list",
        },
        "rt-exploit": {
            "redteam_evidence_add",
            "redteam_access_add",
            "redteam_access_list",
            "redteam_credential_add",
            "redteam_credential_list",
            "redteam_sessions",
            "redteam_chain_add",
            "redteam_chain_list",
            "redteam_chain",
            "redteam_attack_file_add",
            "redteam_attack_file_list",
            "redteam_webshell_add",
            "redteam_webshell_update",
            "redteam_webshell_list",
            "redteam_session_check",
            "redteam_shot_add",
            "redteam_shot_list",
            "redteam_shot_delete",
        },
        "rt-internal": {
            "redteam_evidence_add",
            "redteam_tunnel_add",
            "redteam_tunnel_list",
            "redteam_tunnel_update",
        },
    }[profile] if profile.startswith("rt-") else None
    shared = {
        "redteam_engagement_open",
        "redteam_session_bind",
        "redteam_session_info",
        "redteam_preflight",
        "redteam_reserve",
        "redteam_release",
        "redteam_report_skeleton",
        "redteam_report_index",
        "redteam_score_list",
        "redteam_attack_chain",
        "redteam_attack_path",
        "redteam_roles",
        "redteam_role_prompt",
        "redteam_role_prompt_reset",
        "redteam_score_hit",
        "redteam_score_report",
        "redteam_score_point_save",
        "redteam_score_point_get",
        "redteam_agent_slot",
    }
    for name, schema, handler in TOOLS:
        if allowed is not None and name not in allowed and name not in shared:
            continue
        ctx.register_tool(
            name=name,
            toolset="hermes-redteam",
            schema=schema,
            handler=handler,
        )
    root = Path(__file__).resolve().parent
    role_skills = {
        "rt-recon": (
            "fofa-recon",
            "passive-recon",
            "recon-pipeline",
            "active-scan",
            "web-fingerprint",
            "asset-correlation",
            "browser-automation",
            "kimi-webbridge",
            "cn-proxy-pool",
        ),
        "rt-vuln": ("nuclei-scan", "dir-bruteforce", "unauth-exploit"),
        "rt-exploit": (
            "webshell-toolkit",
            "credential-attack",
            "shell-handler",
            "vps-reverse-shell",
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
    ctx.register_skill("redteam-preflight", root / "skills" / "redteam-preflight" / "SKILL.md")
    ctx.register_skill("redteam-setup", root / "skills" / "redteam-setup" / "SKILL.md")
    for name in role_skills.get(profile, ()):
        ctx.register_skill(name, root / "skills" / name / "SKILL.md")
    role = root / "roles" / f"{profile}.md"
    if role.is_file():
        ctx.register_skill(profile, role)
