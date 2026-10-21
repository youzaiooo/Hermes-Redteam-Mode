"""Read-only dashboard routes. No writes, no tool registration."""

from __future__ import annotations

import importlib.util
import json
import os
import sys
from pathlib import Path

from fastapi import APIRouter, HTTPException


def _load(name: str):
    """Load a sibling module by file path.

    The desktop host imports this file alone, so a relative import has no parent.
    """
    path = Path(__file__).resolve().parents[1] / f"{name}.py"
    module_name = f"hermes_redteam_{name}"
    cached = sys.modules.get(module_name)
    if cached is not None and getattr(cached, "__file__", None) == str(path):
        return cached
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


_score = _load("score")
_store = _load("store")
read_score_mode = _score.read_score_mode
write_score_mode = _score.write_score_mode
query_assets = _store.query_assets
query_board = _store.query_board
role_list = _store.role_list
sessions = _store.sessions
tunnel_list = _store.tunnel_list
vuln_query = _store.vuln_query
write_report_index = _store.write_report_index

router = APIRouter()


def _home() -> Path:
    return Path(os.environ.get("HERMES_HOME", str(Path.home() / ".hermes")))


def _root() -> Path:
    return _home() / "redteam" / "engagements"


def _list_ids() -> list[str]:
    root = _root()
    if not root.is_dir():
        return []
    return sorted(
        path.name
        for path in root.iterdir()
        if (path / "index.db").is_file() and path.name.replace("-", "").replace("_", "").isalnum()
    )


@router.get("/engagements/current")
def current_engagements() -> dict:
    return {"ok": True, "engagements": _list_ids()}


@router.get("/board/{engagement_id}")
def board(engagement_id: str) -> dict:
    payload = json.loads(query_board(_root(), engagement_id))
    if not payload.get("ok"):
        raise HTTPException(status_code=404, detail=payload.get("error", "not_found"))
    return payload


@router.get("/score-rules")
def score_rules() -> dict:
    return {"ok": True, "mode": read_score_mode(_home())}


@router.post("/score-rules")
def set_score_rules(body: dict) -> dict:
    mode = str(body.get("mode", ""))
    try:
        write_score_mode(_home(), mode)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"ok": True, "mode": mode, "notice": "new_session"}


def _rows(payload: str, key: str) -> dict:
    found = json.loads(payload)
    if not found.get("ok"):
        raise HTTPException(status_code=404, detail=found.get("error", "not_found"))
    return found


@router.get("/assets/{engagement_id}")
def assets(engagement_id: str) -> dict:
    return _rows(query_assets(_root(), engagement_id), "assets")


@router.get("/findings/{engagement_id}")
def findings(engagement_id: str) -> dict:
    return _rows(vuln_query(_root(), engagement_id), "vulns")


@router.get("/sessions/{engagement_id}")
def session_rows(engagement_id: str) -> dict:
    return _rows(sessions(_root(), engagement_id), "sessions")


@router.get("/tunnels/{engagement_id}")
def tunnels(engagement_id: str) -> dict:
    return _rows(tunnel_list(_root(), engagement_id), "tunnels")


@router.get("/skills")
def skills() -> dict:
    names = sorted(path.parent.name for path in (Path(__file__).resolve().parents[1] / "skills").glob("*/SKILL.md"))
    return {"ok": True, "count": len(names), "skills": names}


@router.get("/roles")
def roles() -> dict:
    return json.loads(role_list())


@router.get("/report/{engagement_id}")
def report(engagement_id: str) -> dict:
    path = write_report_index(_root(), engagement_id)
    return {"ok": True, "path": path}
