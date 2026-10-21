"""Read-only dashboard routes. No writes, no tool registration."""

from __future__ import annotations

import importlib.util
import json
import os
import sqlite3
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
credential_list = _store.credential_list
write_report_index = _store.write_report_index

router = APIRouter()


def _home() -> Path:
    try:
        from hermes_constants import get_hermes_home

        return Path(get_hermes_home())
    except Exception:
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


def _engagement_meta(root: Path, engagement_id: str) -> dict | None:
    """Read {id, display_name, created_at} from an engagement's index.db."""
    db_path = root / engagement_id / "index.db"
    if not db_path.is_file():
        return None
    with sqlite3.connect(db_path) as db:
        row = db.execute(
            "SELECT display_name, created_at FROM engagement WHERE id = ?",
            (engagement_id,),
        ).fetchone()
    if row is None:
        return None
    return {"id": engagement_id, "display_name": row[0], "created_at": row[1]}


@router.get("/engagements/current")
def current_engagements() -> dict:
    return {"ok": True, "engagements": _list_ids()}


@router.get("/engagements")
def list_engagements() -> dict:
    root = _root()
    rows = [
        meta
        for engagement_id in _list_ids()
        if (meta := _engagement_meta(root, engagement_id)) is not None
    ]
    rows.sort(key=lambda row: (row.get("created_at") or "", row.get("id") or ""), reverse=True)
    return {"ok": True, "engagements": rows}


@router.get("/engagements/for-session/{session_id}")
def engagement_for_session(session_id: str) -> dict:
    root = _root()
    for engagement_id in _list_ids():
        state_path = root / engagement_id / "session.json"
        if not state_path.is_file():
            continue
        try:
            state = json.loads(state_path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if state.get("session_id") == session_id:
            meta = _engagement_meta(root, engagement_id)
            if meta is not None:
                return {
                    "ok": True,
                    "engagement": {"id": meta["id"], "display_name": meta["display_name"]},
                }
    return {"ok": True, "engagement": None}


@router.get("/summary/{engagement_id}")
def summary(engagement_id: str) -> dict:
    root = _root()
    db_path = root / engagement_id / "index.db"
    if not db_path.is_file():
        raise HTTPException(status_code=404, detail="not_found")
    with sqlite3.connect(db_path) as db:
        assets = db.execute(
            "SELECT COUNT(*) FROM asset WHERE engagement_id = ?", (engagement_id,)
        ).fetchone()[0]
        services = db.execute(
            "SELECT COUNT(*) FROM asset WHERE engagement_id = ? AND address LIKE 'http%'",
            (engagement_id,),
        ).fetchone()[0]
        vulns = db.execute(
            "SELECT COUNT(*) FROM vuln WHERE engagement_id = ?", (engagement_id,)
        ).fetchone()[0]
        credentials = db.execute(
            "SELECT COUNT(*) FROM credential_ref WHERE engagement_id = ?", (engagement_id,)
        ).fetchone()[0]
        tunnels = db.execute(
            "SELECT COUNT(*) FROM tunnel WHERE engagement_id = ?", (engagement_id,)
        ).fetchone()[0]
        access = db.execute(
            "SELECT COUNT(*) FROM access_session WHERE engagement_id = ?", (engagement_id,)
        ).fetchone()[0]
        hit_rows = db.execute(
            "SELECT rule_id FROM score_event WHERE engagement_id = ?", (engagement_id,)
        ).fetchall()
    score_hits = sorted({rule for (rule,) in hit_rows if rule})
    if tunnels:
        stage = "internal"
    elif credentials or access:
        stage = "exploit"
    elif vulns:
        stage = "vuln"
    elif assets:
        stage = "asset"
    else:
        stage = "recon"
    return {
        "ok": True,
        "summary": {
            "assets": assets,
            "services": services,
            "vulns": vulns,
            "credentials": credentials,
            "tunnels": tunnels,
            "score": len(score_hits),
            "stage": stage,
            "score_hits": score_hits,
        },
    }


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


@router.get("/credentials/{engagement_id}")
def credentials(engagement_id: str) -> dict:
    return _rows(credential_list(_root(), engagement_id), "credentials")


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
