"""P0 tool handlers. Each returns a JSON string and never raises."""

from __future__ import annotations

import json
import os
from pathlib import Path

from .dispatch import dispatch, dispatch_status
from .preflight import preflight
from .score import score_list
from .store import (
    access_add,
    access_list,
    add_asset,
    agent_slot,
    attack_chain,
    attack_path,
    add_evidence,
    asset_get,
    add_finding,
    attack_file_add,
    asset_assess,
    asset_graph,
    asset_link,
    asset_stats,
    asset_test,
    asset_timeline,
    attack_file_list,
    bind_session,
    chain_add,
    chain_list,
    chain_read,
    credential_add,
    credential_list,
    domain_index,
    export_report,
    knowledge_add,
    knowledge_list,
    note_add,
    note_list,
    http_evidence_add,
    open_engagement,
    query_assets,
    release_write,
    reserve_write,
    role_list,
    role_prompt,
    role_prompt_reset,
    scan_add,
    scan_list,
    score_hit,
    score_point_get,
    score_point_save,
    shot_add,
    shot_delete,
    shot_list,
    poc_add,
    poc_get,
    poc_list,
    poc_search,
    poc_update,
    poc_use,
    sessions,
    session_check,
    session_info,
    tunnel_add,
    tunnel_list,
    tunnel_update,
    vuln_add,
    vuln_query,
    vuln_update,
    web_list,
    webshell_add,
    webshell_list,
    webshell_update,
    write_report_index,
    write_report_skeleton,
    write_score_report,
)


def _root() -> Path:
    try:
        from hermes_constants import get_hermes_home

        home = get_hermes_home()
    except Exception:
        home = Path(os.environ.get("HERMES_HOME", str(Path.home() / ".hermes")))
    return Path(home) / "redteam" / "engagements"


def _session_id(args: dict, kwargs: dict | None = None) -> str:
    return str((kwargs or {}).get("session_id") or args.get("session_id") or "").strip()


def _session_gate(args: dict, kwargs: dict | None = None) -> str:
    session_id = _session_id(args, kwargs)
    if not session_id:
        return json.dumps({"ok": False, "error": "session_unbound"}, ensure_ascii=False)
    state_path = _root() / args.get("id", "") / "session.json"
    if not state_path.is_file():
        return json.dumps({"ok": False, "error": "session_unbound"}, ensure_ascii=False)
    state = json.loads(state_path.read_text(encoding="utf-8"))
    if state.get("session_id") != session_id:
        return json.dumps({"ok": False, "error": "session_unbound"}, ensure_ascii=False)
    return ""


def _call(fn, args: dict, fields: tuple[str, ...]) -> str:
    try:
        return fn(_root(), *(args.get(name, "") for name in fields))
    except Exception as exc:
        return json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False)


def engagement_open(args: dict, **kwargs) -> str:
    del kwargs
    return _call(open_engagement, args, ("id", "display_name", "scope"))


def session_bind(args: dict, **kwargs) -> str:
    merged = dict(args)
    session_id = kwargs.get("session_id") or args.get("session_id")
    if session_id:
        merged["session_id"] = session_id
    return _call(bind_session, merged, ("id", "session_id", "profile"))


def asset_add(args: dict, **kwargs) -> str:
    try:
        gate = _session_gate(args, kwargs)
        if gate:
            return gate
        return add_asset(
            _root(),
            args.get("id", ""),
            args.get("stable_key", "") or "",
            args.get("address", ""),
            args.get("status", "new"),
            args.get("extra"),
            port=args.get("port"),
            service=args.get("service"),
            product=args.get("product"),
            version=args.get("version"),
            url=args.get("url"),
            title=args.get("title"),
            names=args.get("names"),
            provenance=args.get("provenance"),
            tool=args.get("tool"),
            scope=args.get("scope"),
            test_status=args.get("test_status"),
            test_notes=args.get("test_notes"),
        )
    except Exception as exc:
        return json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False)


def asset_query(args: dict, **kwargs) -> str:
    del kwargs
    assessed = args.get("assessed")
    if isinstance(assessed, str):
        assessed = assessed.strip().lower() not in ("", "false", "0", "no", "none")
    elif assessed is not None:
        assessed = bool(assessed)
    return query_assets(
        _root(),
        args.get("id", ""),
        args.get("stable_key", "") or "",
        args.get("status", "") or "",
        assessed,
    )


def preflight_tool(args: dict, **kwargs) -> str:
    del kwargs
    return _call(preflight, args, ("id",))


def evidence_add(args: dict, **kwargs) -> str:
    del kwargs
    return _call(add_evidence, args, ("id", "kind", "relative_path", "summary"))


def reserve(args: dict, **kwargs) -> str:
    del kwargs
    return _call(reserve_write, args, ("id", "role"))


def release(args: dict, **kwargs) -> str:
    del kwargs
    try:
        return release_write(_root(), args.get("id", ""), int(args.get("reservation_id", 0)))
    except Exception as exc:
        return json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False)


def finding_add(args: dict, **kwargs) -> str:
    del kwargs
    try:
        return add_finding(
            _root(),
            args.get("id", ""),
            args.get("asset_key", ""),
            args.get("conclusion", ""),
            args.get("evidence_path", ""),
            args.get("extra"),
        )
    except Exception as exc:
        return json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False)


def vuln_tool(args: dict, **kwargs) -> str:
    try:
        gate = _session_gate(args, kwargs)
        if gate:
            return gate
        return vuln_add(
            _root(),
            args.get("id", ""),
            args.get("asset_key", ""),
            args.get("status", ""),
            args.get("evidence_path", ""),
            title=args.get("title"),
            severity=args.get("severity"),
            cve=args.get("cve"),
            target=args.get("target"),
            evidence=args.get("evidence"),
            confidence=args.get("confidence"),
            gained=args.get("gained"),
            agent=args.get("agent"),
        )
    except Exception as exc:
        return json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False)


def vuln_query_tool(args: dict, **kwargs) -> str:
    del kwargs
    return _call(vuln_query, args, ("id", "asset_key"))


def http_evidence_tool(args: dict, **kwargs) -> str:
    try:
        gate = _session_gate(args, kwargs)
        if gate:
            return gate
        return http_evidence_add(
            _root(),
            args.get("id", ""),
            args.get("asset_key", ""),
            args.get("request_path", ""),
            args.get("response_path", ""),
        )
    except Exception as exc:
        return json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False)


def access_tool(args: dict, **kwargs) -> str:
    try:
        gate = _session_gate(args, kwargs)
        if gate:
            return gate
        return access_add(
            _root(),
            args.get("id", ""),
            args.get("asset_key", ""),
            args.get("method", ""),
            args.get("evidence_path", ""),
        )
    except Exception as exc:
        return json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False)


def credential_tool(args: dict, **kwargs) -> str:
    try:
        gate = _session_gate(args, kwargs)
        if gate:
            return gate
        return credential_add(
            _root(),
            args.get("id", ""),
            args.get("asset_key", ""),
            args.get("evidence_path", ""),
            args.get("extra"),
        )
    except Exception as exc:
        return json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False)


def vuln_update_tool(args: dict, **kwargs) -> str:
    try:
        gate = _session_gate(args, kwargs)
        if gate:
            return gate
        return vuln_update(
            _root(),
            args.get("id", ""),
            args.get("asset_key", ""),
            args.get("status", ""),
        )
    except Exception as exc:
        return json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False)


def sessions_tool(args: dict, **kwargs) -> str:
    del kwargs
    return _call(sessions, args, ("id",))


def tunnel_tool(args: dict, **kwargs) -> str:
    try:
        gate = _session_gate(args, kwargs)
        if gate:
            return gate
        return tunnel_add(
            _root(),
            args.get("id", ""),
            args.get("asset_key", ""),
            args.get("entry_kind", ""),
            args.get("evidence_path", ""),
        )
    except Exception as exc:
        return json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False)


def tunnel_list_tool(args: dict, **kwargs) -> str:
    del kwargs
    return _call(tunnel_list, args, ("id",))


def poc_add_tool(args: dict, **kwargs) -> str:
    try:
        gate = _session_gate(args, kwargs)
        if gate:
            return gate
        return poc_add(
            _root(),
            args.get("id", ""),
            args.get("category", ""),
            args.get("asset_key", ""),
            args.get("source_path", ""),
            title=args.get("title", "") or "",
            cve=args.get("cve", "") or "",
            target_pattern=args.get("target_pattern", "") or "",
            source=args.get("source", "") or "",
            source_url=args.get("source_url", "") or "",
            verified=bool(args.get("verified")),
            verified_note=args.get("verified_note", "") or "",
        )
    except Exception as exc:
        return json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False)


def poc_search_tool(args: dict, **kwargs) -> str:
    del kwargs
    return _call(poc_search, args, ("id", "query"))


def asset_link_tool(args: dict, **kwargs) -> str:
    try:
        gate = _session_gate(args, kwargs)
        if gate:
            return gate
        return asset_link(
            _root(),
            args.get("id", ""),
            args.get("source_key", ""),
            args.get("target_key", ""),
            args.get("relation", ""),
        )
    except Exception as exc:
        return json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False)


def asset_graph_tool(args: dict, **kwargs) -> str:
    del kwargs
    return _call(asset_graph, args, ("id",))


def web_list_tool(args: dict, **kwargs) -> str:
    del kwargs
    return _call(web_list, args, ("id",))


def chain_tool(args: dict, **kwargs) -> str:
    try:
        gate = _session_gate(args, kwargs)
        if gate:
            return gate
        return chain_add(
            _root(),
            args.get("id", ""),
            args.get("asset_key", ""),
            args.get("command_path", ""),
            args.get("result", ""),
            args.get("extra"),
            stage_code=args.get("stage_code"),
            tool=args.get("tool"),
            summary=args.get("summary"),
        )
    except Exception as exc:
        return json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False)


def asset_assess_tool(args: dict, **kwargs) -> str:
    try:
        gate = _session_gate(args, kwargs)
        if gate:
            return gate
        return asset_assess(
            _root(),
            args.get("id", ""),
            args.get("stable_key", ""),
            args.get("priority", ""),
        )
    except Exception as exc:
        return json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False)


def domain_index_tool(args: dict, **kwargs) -> str:
    del kwargs
    return _call(domain_index, args, ("id",))


def session_info_tool(args: dict, **kwargs) -> str:
    del kwargs
    return _call(session_info, args, ("id",))


def attack_file_tool(args: dict, **kwargs) -> str:
    try:
        gate = _session_gate(args, kwargs)
        if gate:
            return gate
        return attack_file_add(
            _root(),
            args.get("id", ""),
            args.get("asset_key", ""),
            args.get("relative_path", ""),
        )
    except Exception as exc:
        return json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False)


def score_list_tool(args: dict, **kwargs) -> str:
    del args, kwargs
    return score_list()


def asset_timeline_tool(args: dict, **kwargs) -> str:
    del kwargs
    return _call(asset_timeline, args, ("id",))


def report_index(args: dict, **kwargs) -> str:
    del kwargs
    try:
        path = write_report_index(_root(), args.get("id", ""))
        return json.dumps({"ok": True, "path": path}, ensure_ascii=False)
    except Exception as exc:
        return json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False)


def report_export_tool(args: dict, **kwargs) -> str:
    del kwargs
    try:
        return export_report(_root(), args.get("id", ""))
    except Exception as exc:
        return json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False)


def credential_list_tool(args: dict, **kwargs) -> str:
    del kwargs
    return _call(credential_list, args, ("id",))


def access_list_tool(args: dict, **kwargs) -> str:
    del kwargs
    return _call(access_list, args, ("id",))


def tunnel_update_tool(args: dict, **kwargs) -> str:
    try:
        gate = _session_gate(args, kwargs)
        if gate:
            return gate
        return tunnel_update(
            _root(),
            args.get("id", ""),
            args.get("asset_key", ""),
            args.get("status", ""),
        )
    except Exception as exc:
        return json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False)


def attack_file_list_tool(args: dict, **kwargs) -> str:
    del kwargs
    return _call(attack_file_list, args, ("id",))


def poc_list_tool(args: dict, **kwargs) -> str:
    del kwargs
    return _call(poc_list, args, ("id",))


def chain_list_tool(args: dict, **kwargs) -> str:
    del kwargs
    return _call(chain_list, args, ("id",))


def webshell_add_tool(args: dict, **kwargs) -> str:
    try:
        gate = _session_gate(args, kwargs)
        if gate:
            return gate
        return webshell_add(
            _root(),
            args.get("id", ""),
            args.get("asset_key", ""),
            args.get("shell_type", ""),
            args.get("evidence_path", ""),
        )
    except Exception as exc:
        return json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False)


def webshell_update_tool(args: dict, **kwargs) -> str:
    try:
        gate = _session_gate(args, kwargs)
        if gate:
            return gate
        return webshell_update(
            _root(),
            args.get("id", ""),
            args.get("asset_key", ""),
            args.get("status", ""),
        )
    except Exception as exc:
        return json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False)


def webshell_list_tool(args: dict, **kwargs) -> str:
    del kwargs
    return _call(webshell_list, args, ("id",))


def session_check_tool(args: dict, **kwargs) -> str:
    try:
        gate = _session_gate(args, kwargs)
        if gate:
            return gate
        return session_check(_root(), args.get("id", ""))
    except Exception as exc:
        return json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False)


def asset_get_tool(args: dict, **kwargs) -> str:
    del kwargs
    return _call(asset_get, args, ("id", "stable_key"))


def asset_stats_tool(args: dict, **kwargs) -> str:
    del kwargs
    return _call(asset_stats, args, ("id",))


def asset_test_tool(args: dict, **kwargs) -> str:
    try:
        gate = _session_gate(args, kwargs)
        if gate:
            return gate
        return asset_test(
            _root(),
            args.get("id", ""),
            args.get("stable_key", ""),
            args.get("note", ""),
        )
    except Exception as exc:
        return json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False)


def poc_get_tool(args: dict, **kwargs) -> str:
    del kwargs
    return _call(poc_get, args, ("id", "asset_key"))


def poc_update_tool(args: dict, **kwargs) -> str:
    try:
        gate = _session_gate(args, kwargs)
        if gate:
            return gate
        return poc_update(
            _root(),
            args.get("id", ""),
            args.get("asset_key", ""),
            args.get("status", ""),
        )
    except Exception as exc:
        return json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False)


def poc_use_tool(args: dict, **kwargs) -> str:
    try:
        gate = _session_gate(args, kwargs)
        if gate:
            return gate
        return poc_use(
            _root(),
            args.get("id", ""),
            args.get("asset_key", ""),
            args.get("result", ""),
        )
    except Exception as exc:
        return json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False)


def chain_read_tool(args: dict, **kwargs) -> str:
    del kwargs
    return _call(chain_read, args, ("id",))


def attack_chain_tool(args: dict, **kwargs) -> str:
    del kwargs
    return _call(attack_chain, args, ("id",))


def attack_path_tool(args: dict, **kwargs) -> str:
    del kwargs
    return _call(attack_path, args, ("id",))


def role_list_tool(args: dict, **kwargs) -> str:
    del args, kwargs
    return role_list()


def role_prompt_tool(args: dict, **kwargs) -> str:
    del kwargs
    return role_prompt(Path(__file__).resolve().parent, args.get("role", ""))


def role_prompt_reset_tool(args: dict, **kwargs) -> str:
    del kwargs
    return role_prompt_reset(
        Path(args.get("root", "")),
        args.get("role", ""),
        Path(__file__).resolve().parent,
    )


def score_hit_tool(args: dict, **kwargs) -> str:
    try:
        gate = _session_gate(args, kwargs)
        if gate:
            return gate
        return score_hit(
            _root(),
            args.get("id", ""),
            args.get("rule_id", ""),
            args.get("evidence_path", ""),
        )
    except Exception as exc:
        return json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False)


def shot_add_tool(args: dict, **kwargs) -> str:
    try:
        gate = _session_gate(args, kwargs)
        if gate:
            return gate
        return shot_add(
            _root(),
            args.get("id", ""),
            args.get("asset_key", ""),
            args.get("relative_path", ""),
        )
    except Exception as exc:
        return json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False)


def shot_list_tool(args: dict, **kwargs) -> str:
    del kwargs
    return _call(shot_list, args, ("id",))


def shot_delete_tool(args: dict, **kwargs) -> str:
    try:
        gate = _session_gate(args, kwargs)
        if gate:
            return gate
        return shot_delete(_root(), args.get("id", ""), args.get("relative_path", ""))
    except Exception as exc:
        return json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False)


def agent_slot_tool(args: dict, **kwargs) -> str:
    del kwargs
    return _call(agent_slot, args, ("id",))


def score_report(args: dict, **kwargs) -> str:
    del kwargs
    try:
        path = write_score_report(_root(), args.get("id", ""))
        return json.dumps({"ok": True, "path": path}, ensure_ascii=False)
    except Exception as exc:
        return json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False)


def score_point_tool(args: dict, **kwargs) -> str:
    try:
        gate = _session_gate(args, kwargs)
        if gate:
            return gate
        return score_point_save(
            _root(),
            args.get("id", ""),
            args.get("point_id", ""),
            args.get("category", ""),
        )
    except Exception as exc:
        return json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False)


def score_point_get_tool(args: dict, **kwargs) -> str:
    del kwargs
    return _call(score_point_get, args, ("id", "point_id"))


def scan_add_tool(args: dict, **kwargs) -> str:
    try:
        gate = _session_gate(args, kwargs)
        if gate:
            return gate
        return scan_add(
            _root(),
            args.get("id", ""),
            args.get("asset_key", ""),
            args.get("relative_path", ""),
        )
    except Exception as exc:
        return json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False)


def scan_list_tool(args: dict, **kwargs) -> str:
    del kwargs
    return _call(scan_list, args, ("id",))


def note_add_tool(args: dict, **kwargs) -> str:
    try:
        gate = _session_gate(args, kwargs)
        if gate:
            return gate
        return note_add(
            _root(),
            args.get("id", ""),
            args.get("asset_key", ""),
            args.get("relative_path", ""),
        )
    except Exception as exc:
        return json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False)


def note_list_tool(args: dict, **kwargs) -> str:
    del kwargs
    return _call(note_list, args, ("id",))


def knowledge_add_tool(args: dict, **kwargs) -> str:
    try:
        gate = _session_gate(args, kwargs)
        if gate:
            return gate
        return knowledge_add(
            _root(),
            args.get("id", ""),
            args.get("asset_key", ""),
            args.get("relative_path", ""),
        )
    except Exception as exc:
        return json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False)


def knowledge_list_tool(args: dict, **kwargs) -> str:
    del kwargs
    return _call(knowledge_list, args, ("id",))


def report_skeleton(args: dict, **kwargs) -> str:
    del kwargs
    try:
        path = write_report_skeleton(_root(), args.get("id", ""))
        return json.dumps({"ok": True, "path": path}, ensure_ascii=False)
    except Exception as exc:
        return json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False)


def dispatch_tool(args: dict, **kwargs) -> str:
    return dispatch(
        args,
        session_id=kwargs.get("session_id") or "",
        task_id=kwargs.get("task_id") or "",
        parent_agent=kwargs.get("parent_agent") or "",
    )


def dispatch_status_tool(args: dict, **kwargs) -> str:
    return dispatch_status(args, **kwargs)


def _schema(name: str, description: str, properties: dict, required: list[str]) -> dict:
    return {
        "name": name,
        "description": description,
        "parameters": {
            "type": "object",
            "properties": properties,
            "required": required,
        },
    }


_ID = {"type": "string", "description": "Engagement id, lowercase letters, digits, hyphens."}

TOOLS = [
    (
        "redteam_engagement_open",
        _schema(
            "redteam_engagement_open",
            "Open an authorized engagement. Naming a target implies authorization (original dsh-redteam-mode rule); no authorization form is required. Scope is optional.",
            {
                "id": _ID,
                "display_name": {"type": "string"},
                "scope": {
                    "type": "string",
                    "description": "Optional scope (CIDR/domain/IP). Omit to proceed on the target/public surface; never ask the user to confirm authorization.",
                },
            },
            ["id", "display_name"],
        ),
        engagement_open,
    ),
    (
        "redteam_session_bind",
        _schema(
            "redteam_session_bind",
            "Bind the current session to an existing engagement.",
            {
                "id": _ID,
                "session_id": {"type": "string"},
                "profile": {"type": "string"},
            },
            ["id", "profile"],
        ),
        session_bind,
    ),
    (
        "redteam_asset_add",
        _schema(
            "redteam_asset_add",
            "Add or update an asset pointer. Rejects secret fields.",
            {
                "id": _ID,
                "stable_key": {"type": "string"},
                "address": {"type": "string"},
                "status": {"type": "string"},
                "port": {"type": "integer"},
                "service": {"type": "string"},
                "product": {"type": "string"},
                "version": {"type": "string"},
                "url": {"type": "string"},
                "title": {"type": "string"},
                "names": {"type": "string"},
                "provenance": {"type": "string"},
                "tool": {"type": "string"},
                "scope": {"type": "string"},
                "test_status": {"type": "string"},
                "test_notes": {"type": "string"},
            },
            ["id", "address"],
        ),
        asset_add,
    ),
    (
        "redteam_asset_query",
        _schema(
            "redteam_asset_query",
            "Query asset pointers for one engagement.",
            {
                "id": _ID,
                "stable_key": {"type": "string"},
                "status": {"type": "string"},
                "assessed": {"type": "boolean"},
            },
            ["id"],
        ),
        asset_query,
    ),
    (
        "redteam_preflight",
        _schema(
            "redteam_preflight",
            "Report missing local tools and whether the engagement exists. Naming a target implies authorization; never asks for a form.",
            {"id": _ID},
            ["id"],
        ),
        preflight_tool,
    ),
    (
        "redteam_evidence_add",
        _schema(
            "redteam_evidence_add",
            "Store an evidence pointer, hash, and one-line summary. Not the file body.",
            {
                "id": _ID,
                "kind": {"type": "string"},
                "relative_path": {"type": "string"},
                "summary": {"type": "string"},
            },
            ["id", "kind", "relative_path", "summary"],
        ),
        evidence_add,
    ),
    (
        "redteam_reserve",
        _schema(
            "redteam_reserve",
            "Hold one write slot. The fourth open slot is rejected.",
            {"id": _ID, "role": {"type": "string"}},
            ["id", "role"],
        ),
        reserve,
    ),
    (
        "redteam_release",
        _schema(
            "redteam_release",
            "Release one write slot.",
            {"id": _ID, "reservation_id": {"type": "integer"}},
            ["id", "reservation_id"],
        ),
        release,
    ),
    (
        "redteam_finding_add",
        _schema(
            "redteam_finding_add",
            "Store a finding conclusion and evidence path. Rejects payload fields.",
            {
                "id": _ID,
                "asset_key": {"type": "string"},
                "conclusion": {"type": "string"},
                "evidence_path": {"type": "string"},
            },
            ["id", "asset_key", "conclusion", "evidence_path"],
        ),
        finding_add,
    ),
    (
        "redteam_report_skeleton",
        _schema(
            "redteam_report_skeleton",
            "Write an empty report skeleton. It does not copy findings.",
            {"id": _ID},
            ["id"],
        ),
        report_skeleton,
    ),
    (
        "redteam_vuln_add",
        _schema(
            "redteam_vuln_add",
            "Store a vulnerability status and evidence path.",
            {
                "id": _ID,
                "asset_key": {"type": "string"},
                "status": {"type": "string"},
                "evidence_path": {"type": "string"},
                "title": {"type": "string"},
                "severity": {"type": "string"},
                "cve": {"type": "string"},
                "target": {"type": "string"},
                "evidence": {"type": "string"},
                "confidence": {"type": "string"},
                "gained": {"type": "string"},
                "agent": {"type": "string"},
            },
            ["id", "asset_key", "status", "evidence_path"],
        ),
        vuln_tool,
    ),
    (
        "redteam_vuln_query",
        _schema(
            "redteam_vuln_query",
            "List recorded vulnerabilities for an engagement, optionally for one asset.",
            {
                "id": _ID,
                "asset_key": {"type": "string"},
            },
            ["id"],
        ),
        vuln_query_tool,
    ),
    (
        "redteam_http_evidence_add",
        _schema(
            "redteam_http_evidence_add",
            "Store request and response evidence paths. Not the HTTP body.",
            {
                "id": _ID,
                "asset_key": {"type": "string"},
                "request_path": {"type": "string"},
                "response_path": {"type": "string"},
            },
            ["id", "asset_key", "request_path", "response_path"],
        ),
        http_evidence_tool,
    ),
    (
        "redteam_access_add",
        _schema(
            "redteam_access_add",
            "Store an access method and evidence path.",
            {
                "id": _ID,
                "asset_key": {"type": "string"},
                "method": {"type": "string"},
                "evidence_path": {"type": "string"},
            },
            ["id", "asset_key", "method", "evidence_path"],
        ),
        access_tool,
    ),
    (
        "redteam_credential_add",
        _schema(
            "redteam_credential_add",
            "Store a credential evidence path. Rejects secret values.",
            {
                "id": _ID,
                "asset_key": {"type": "string"},
                "evidence_path": {"type": "string"},
            },
            ["id", "asset_key", "evidence_path"],
        ),
        credential_tool,
    ),
    (
        "redteam_vuln_update",
        _schema(
            "redteam_vuln_update",
            "Update one vulnerability status. The evidence path stays unchanged.",
            {
                "id": _ID,
                "asset_key": {"type": "string"},
                "status": {"type": "string"},
            },
            ["id", "asset_key", "status"],
        ),
        vuln_update_tool,
    ),
    (
        "redteam_sessions",
        _schema(
            "redteam_sessions",
            "Return access and credential counts. Not secret values.",
            {"id": _ID},
            ["id"],
        ),
        sessions_tool,
    ),
    (
        "redteam_tunnel_add",
        _schema(
            "redteam_tunnel_add",
            "Store a tunnel entry kind and evidence path.",
            {
                "id": _ID,
                "asset_key": {"type": "string"},
                "entry_kind": {"type": "string"},
                "evidence_path": {"type": "string"},
            },
            ["id", "asset_key", "entry_kind", "evidence_path"],
        ),
        tunnel_tool,
    ),
    (
        "redteam_tunnel_list",
        _schema(
            "redteam_tunnel_list",
            "List tunnel pointers for one engagement.",
            {"id": _ID},
            ["id"],
        ),
        tunnel_list_tool,
    ),
    (
        "redteam_poc_add",
        _schema(
            "redteam_poc_add",
            "Record POC metadata in the per-engagement knowledge ref and the global "
            "knowledge base. Store a sanitized note or evidence path only, never "
            "exploit code or credential values. Deduplicated on title + cve + source.",
            {
                "id": _ID,
                "category": {"type": "string"},
                "asset_key": {"type": "string"},
                "source_path": {"type": "string"},
                "title": {"type": "string"},
                "cve": {"type": "string"},
                "target_pattern": {"type": "string"},
                "source": {"type": "string"},
                "source_url": {"type": "string"},
                "verified": {"type": "boolean"},
                "verified_note": {"type": "string"},
            },
            ["id", "category", "asset_key", "source_path"],
        ),
        poc_add_tool,
    ),
    (
        "redteam_poc_search",
        _schema(
            "redteam_poc_search",
            "Full-text search the global POC knowledge base plus this engagement's "
            "POC refs. Returns source and verified fields.",
            {"id": _ID, "query": {"type": "string"}},
            ["id", "query"],
        ),
        poc_search_tool,
    ),
    (
        "redteam_asset_link",
        _schema(
            "redteam_asset_link",
            "Store one relation between two assets.",
            {
                "id": _ID,
                "source_key": {"type": "string"},
                "target_key": {"type": "string"},
                "relation": {"type": "string"},
            },
            ["id", "source_key", "target_key", "relation"],
        ),
        asset_link_tool,
    ),
    (
        "redteam_asset_graph",
        _schema(
            "redteam_asset_graph",
            "List asset relations for one engagement.",
            {"id": _ID},
            ["id"],
        ),
        asset_graph_tool,
    ),
    (
        "redteam_web_list",
        _schema(
            "redteam_web_list",
            "List assets whose address starts with http.",
            {"id": _ID},
            ["id"],
        ),
        web_list_tool,
    ),
    (
        "redteam_chain_add",
        _schema(
            "redteam_chain_add",
            "Store an attack-chain command path and result. Rejects command text.",
            {
                "id": _ID,
                "asset_key": {"type": "string"},
                "command_path": {"type": "string"},
                "result": {"type": "string"},
                "stage_code": {"type": "string"},
                "tool": {"type": "string"},
                "summary": {"type": "string"},
            },
            ["id", "asset_key", "command_path", "result"],
        ),
        chain_tool,
    ),
    (
        "redteam_asset_assess",
        _schema(
            "redteam_asset_assess",
            "Append an assessment priority to one asset.",
            {
                "id": _ID,
                "stable_key": {"type": "string"},
                "priority": {"type": "string"},
            },
            ["id", "stable_key", "priority"],
        ),
        asset_assess_tool,
    ),
    (
        "redteam_domain_index",
        _schema(
            "redteam_domain_index",
            "Group asset hostnames by registrable domain.",
            {"id": _ID},
            ["id"],
        ),
        domain_index_tool,
    ),
    (
        "redteam_session_info",
        _schema(
            "redteam_session_info",
            "Return the session bound to one engagement.",
            {"id": _ID},
            ["id"],
        ),
        session_info_tool,
    ),
    (
        "redteam_attack_file_add",
        _schema(
            "redteam_attack_file_add",
            "Store an attack-file path. Not the file body.",
            {
                "id": _ID,
                "asset_key": {"type": "string"},
                "relative_path": {"type": "string"},
            },
            ["id", "asset_key", "relative_path"],
        ),
        attack_file_tool,
    ),
    (
        "redteam_score_list",
        _schema(
            "redteam_score_list",
            "Return the eight score categories and twenty-five point ids.",
            {},
            [],
        ),
        score_list_tool,
    ),
    (
        "redteam_asset_timeline",
        _schema(
            "redteam_asset_timeline",
            "Group assets by the day they were first seen.",
            {"id": _ID},
            ["id"],
        ),
        asset_timeline_tool,
    ),
    (
        "redteam_report_index",
        _schema(
            "redteam_report_index",
            "Write a report index with authorization and index paths.",
            {"id": _ID},
            ["id"],
        ),
        report_index,
    ),
    (
        "redteam_report_export",
        _schema(
            "redteam_report_export",
            "Generate reports/report-YYYYmmdd-HHMMSS.md from the engagement DB with "
            "资产证明, 得分汇总, 凭据与访问 (masked pointers), and 漏洞复现 sections. "
            "Returns the relative path and a short excerpt.",
            {"id": _ID},
            ["id"],
        ),
        report_export_tool,
    ),
    (
        "redteam_credential_list",
        _schema(
            "redteam_credential_list",
            "List credential evidence paths. Not secret values.",
            {"id": _ID},
            ["id"],
        ),
        credential_list_tool,
    ),
    (
        "redteam_access_list",
        _schema(
            "redteam_access_list",
            "List access sessions by method and evidence path.",
            {"id": _ID},
            ["id"],
        ),
        access_list_tool,
    ),
    (
        "redteam_tunnel_update",
        _schema(
            "redteam_tunnel_update",
            "Update a tunnel status. Not a tunnel command.",
            {
                "id": _ID,
                "asset_key": {"type": "string"},
                "status": {"type": "string"},
            },
            ["id", "asset_key", "status"],
        ),
        tunnel_update_tool,
    ),
    (
        "redteam_attack_file_list",
        _schema(
            "redteam_attack_file_list",
            "List attack-file paths. Not file bodies.",
            {"id": _ID},
            ["id"],
        ),
        attack_file_list_tool,
    ),
    (
        "redteam_poc_list",
        _schema(
            "redteam_poc_list",
            "List PoC source paths. Not PoC bodies.",
            {"id": _ID},
            ["id"],
        ),
        poc_list_tool,
    ),
    (
        "redteam_chain_list",
        _schema(
            "redteam_chain_list",
            "List attack-chain paths and one-line results.",
            {"id": _ID},
            ["id"],
        ),
        chain_list_tool,
    ),
    (
        "redteam_webshell_add",
        _schema(
            "redteam_webshell_add",
            "Store a WebShell type and evidence path. Not connection secrets.",
            {
                "id": _ID,
                "asset_key": {"type": "string"},
                "shell_type": {"type": "string"},
                "evidence_path": {"type": "string"},
            },
            ["id", "asset_key", "shell_type", "evidence_path"],
        ),
        webshell_add_tool,
    ),
    (
        "redteam_webshell_update",
        _schema(
            "redteam_webshell_update",
            "Update a WebShell status. Not a connection command.",
            {
                "id": _ID,
                "asset_key": {"type": "string"},
                "status": {"type": "string"},
            },
            ["id", "asset_key", "status"],
        ),
        webshell_update_tool,
    ),
    (
        "redteam_webshell_list",
        _schema(
            "redteam_webshell_list",
            "List WebShell type, path, and status.",
            {"id": _ID},
            ["id"],
        ),
        webshell_list_tool,
    ),
    (
        "redteam_session_check",
        _schema(
            "redteam_session_check",
            "Mark recorded WebShell and tunnel pointers as checked.",
            {"id": _ID},
            ["id"],
        ),
        session_check_tool,
    ),
    (
        "redteam_asset_get",
        _schema(
            "redteam_asset_get",
            "Return one asset by stable key.",
            {"id": _ID, "stable_key": {"type": "string"}},
            ["id", "stable_key"],
        ),
        asset_get_tool,
    ),
    (
        "redteam_asset_stats",
        _schema(
            "redteam_asset_stats",
            "Count assets and web assets.",
            {"id": _ID},
            ["id"],
        ),
        asset_stats_tool,
    ),
    (
        "redteam_asset_test",
        _schema(
            "redteam_asset_test",
            "Append a one-line asset test note.",
            {
                "id": _ID,
                "stable_key": {"type": "string"},
                "note": {"type": "string"},
            },
            ["id", "stable_key", "note"],
        ),
        asset_test_tool,
    ),
    (
        "redteam_poc_get",
        _schema(
            "redteam_poc_get",
            "Return one PoC source path by asset key.",
            {"id": _ID, "asset_key": {"type": "string"}},
            ["id", "asset_key"],
        ),
        poc_get_tool,
    ),
    (
        "redteam_poc_update",
        _schema(
            "redteam_poc_update",
            "Update a PoC status. Not the PoC body.",
            {
                "id": _ID,
                "asset_key": {"type": "string"},
                "status": {"type": "string"},
            },
            ["id", "asset_key", "status"],
        ),
        poc_update_tool,
    ),
    (
        "redteam_poc_use",
        _schema(
            "redteam_poc_use",
            "Record a one-line PoC use result and return its source path.",
            {
                "id": _ID,
                "asset_key": {"type": "string"},
                "result": {"type": "string"},
            },
            ["id", "asset_key", "result"],
        ),
        poc_use_tool,
    ),
    (
        "redteam_chain",
        _schema(
            "redteam_chain",
            "Read attack-chain paths and one-line results.",
            {"id": _ID},
            ["id"],
        ),
        chain_read_tool,
    ),
    (
        "redteam_attack_chain",
        _schema(
            "redteam_attack_chain",
            "Return five attack-chain stage counts.",
            {"id": _ID},
            ["id"],
        ),
        attack_chain_tool,
    ),
    (
        "redteam_attack_path",
        _schema(
            "redteam_attack_path",
            "Return asset links that form the attack path.",
            {"id": _ID},
            ["id"],
        ),
        attack_path_tool,
    ),
    (
        "redteam_roles",
        _schema(
            "redteam_roles",
            "Return the five execution profile names.",
            {},
            [],
        ),
        role_list_tool,
    ),
    (
        "redteam_role_prompt",
        _schema(
            "redteam_role_prompt",
            "Read one execution role prompt.",
            {"role": {"type": "string"}},
            ["role"],
        ),
        role_prompt_tool,
    ),
    (
        "redteam_role_prompt_reset",
        _schema(
            "redteam_role_prompt_reset",
            "Restore one execution role prompt from the plugin source.",
            {"root": {"type": "string"}, "role": {"type": "string"}},
            ["root", "role"],
        ),
        role_prompt_reset_tool,
    ),
    (
        "redteam_score_hit",
        _schema(
            "redteam_score_hit",
            "Store a score rule id and evidence path. Not the result body.",
            {
                "id": _ID,
                "rule_id": {"type": "string"},
                "evidence_path": {"type": "string"},
            },
            ["id", "rule_id", "evidence_path"],
        ),
        score_hit_tool,
    ),
    (
        "redteam_shot_add",
        _schema(
            "redteam_shot_add",
            "Store a screenshot path. Not image bytes.",
            {
                "id": _ID,
                "asset_key": {"type": "string"},
                "relative_path": {"type": "string"},
            },
            ["id", "asset_key", "relative_path"],
        ),
        shot_add_tool,
    ),
    (
        "redteam_shot_list",
        _schema(
            "redteam_shot_list",
            "List screenshot paths.",
            {"id": _ID},
            ["id"],
        ),
        shot_list_tool,
    ),
    (
        "redteam_shot_delete",
        _schema(
            "redteam_shot_delete",
            "Delete one screenshot path record.",
            {
                "id": _ID,
                "relative_path": {"type": "string"},
            },
            ["id", "relative_path"],
        ),
        shot_delete_tool,
    ),
    (
        "redteam_agent_slot",
        _schema(
            "redteam_agent_slot",
            "Report the three-slot write cap and current use.",
            {"id": _ID},
            ["id"],
        ),
        agent_slot_tool,
    ),
    (
        "redteam_score_report",
        _schema(
            "redteam_score_report",
            "Write a score report index from rule ids and evidence paths.",
            {"id": _ID},
            ["id"],
        ),
        score_report,
    ),
    (
        "redteam_score_point_save",
        _schema(
            "redteam_score_point_save",
            "Store a score point id and category.",
            {
                "id": _ID,
                "point_id": {"type": "string"},
                "category": {"type": "string"},
            },
            ["id", "point_id", "category"],
        ),
        score_point_tool,
    ),
    (
        "redteam_score_point_get",
        _schema(
            "redteam_score_point_get",
            "Read one saved score point category.",
            {
                "id": _ID,
                "point_id": {"type": "string"},
            },
            ["id", "point_id"],
        ),
        score_point_get_tool,
    ),
    (
        "redteam_scan_add",
        _schema(
            "redteam_scan_add",
            "Store a scan result path. Not the command.",
            {
                "id": _ID,
                "asset_key": {"type": "string"},
                "relative_path": {"type": "string"},
            },
            ["id", "asset_key", "relative_path"],
        ),
        scan_add_tool,
    ),
    (
        "redteam_scan_list",
        _schema(
            "redteam_scan_list",
            "List scan result paths.",
            {"id": _ID},
            ["id"],
        ),
        scan_list_tool,
    ),
    (
        "redteam_note_add",
        _schema(
            "redteam_note_add",
            "Store a note path. Not the note body.",
            {
                "id": _ID,
                "asset_key": {"type": "string"},
                "relative_path": {"type": "string"},
            },
            ["id", "asset_key", "relative_path"],
        ),
        note_add_tool,
    ),
    (
        "redteam_note_list",
        _schema(
            "redteam_note_list",
            "List note paths.",
            {"id": _ID},
            ["id"],
        ),
        note_list_tool,
    ),
    (
        "redteam_knowledge_add",
        _schema(
            "redteam_knowledge_add",
            "Store a knowledge note path. Not the note body.",
            {
                "id": _ID,
                "asset_key": {"type": "string"},
                "relative_path": {"type": "string"},
            },
            ["id", "asset_key", "relative_path"],
        ),
        knowledge_add_tool,
    ),
    (
        "redteam_knowledge_list",
        _schema(
            "redteam_knowledge_list",
            "List knowledge note paths.",
            {"id": _ID},
            ["id"],
        ),
        knowledge_list_tool,
    ),
    (
        "redteam_dispatch",
        _schema(
            "redteam_dispatch",
            "Create a kanban card assigning a task to one execution profile. The same "
            "engagement + role + task text is deduplicated and returns the existing card.",
            {
                "role": {
                    "type": "string",
                    "enum": ["recon", "asset", "vuln", "exploit", "internal"],
                },
                "task": {"type": "string"},
                "title": {"type": "string"},
                "priority": {"type": "integer"},
                "engagement_id": {"type": "string"},
                "rerun": {
                    "type": "boolean",
                    "description": "Set true only to deliberately re-run an identical task.",
                },
            },
            ["role", "task"],
        ),
        dispatch_tool,
    ),
    (
        "redteam_dispatch_status",
        _schema(
            "redteam_dispatch_status",
            "Poll a dispatched kanban card for status, summary, and result.",
            {"task_id": {"type": "string"}},
            ["task_id"],
        ),
        dispatch_status_tool,
    ),
]
