"""Kanban dispatch layer for the commander profile.

The commander (the Hermes ``default`` profile) creates kanban cards that the
gateway dispatcher hands to the long-lived ``rt-*`` worker profiles. This
module is intentionally small and never raises: every public function returns
a JSON string.
"""

from __future__ import annotations

import json
import hashlib
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROLE_SUFFIXES = ("recon", "asset", "vuln", "exploit", "internal")
_ENGAGEMENT_ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,63}$")


def engagement_root() -> Path:
    """Engagement store root, using Hermes' own home resolver when available."""

    try:
        from hermes_constants import get_hermes_home

        return Path(get_hermes_home()) / "redteam" / "engagements"
    except Exception:
        home = Path(os.environ.get("HERMES_HOME", str(Path.home() / ".hermes")))
        return home / "redteam" / "engagements"


def _authorization_ok(engagement_dir: Path) -> bool:
    # Original dsh-redteam-mode rule: naming a target implies authorization.
    # The engagement's existence (index.db) is the audit record; never gate on a form.
    return (engagement_dir / "index.db").is_file()


def _resolve_engagement(root: Path, explicit: str, session_id: str) -> tuple[Path | None, str]:
    if explicit:
        if not _ENGAGEMENT_ID_RE.match(explicit):
            return None, "invalid_id"
        engagement_dir = root / explicit
        if not (engagement_dir / "index.db").is_file():
            return None, "not_found"
        return engagement_dir, ""

    if not session_id:
        return None, "session_unbound"

    for session_file in sorted(root.glob("*/session.json")):
        try:
            state = json.loads(session_file.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if state.get("session_id") == session_id:
            return session_file.parent, ""
    return None, "session_unbound"


def _auth_fields(engagement_dir: Path) -> dict[str, str]:
    auth = engagement_dir / "wiki" / "authorization.md"
    fields: dict[str, str] = {}
    try:
        for line in auth.read_text(encoding="utf-8").splitlines():
            if "：" in line:
                key, _, value = line.partition("：")
                fields[key.strip()] = value.strip()
    except OSError:
        pass
    return fields


def _brief(engagement_dir: Path, engagement_id: str, assignee: str, task: str) -> str:
    fields = _auth_fields(engagement_dir)
    scope = fields.get("范围") or "按公开可见资产面自主推进（用户未指定范围）"
    boundary = fields.get("允许手段") or "授权范围内常规渗透测试"
    return (
        f"靶标: {engagement_id}\n"
        f"范围: {scope}\n"
        f"边界: {boundary}\n"
        f"角色: {assignee}\n"
        f"靶标目录: {engagement_dir}\n"
        f"任务: {task}\n"
        "记录要求: 用 redteam_* 工具把每一条发现写入 Wiki 与 index.db。"
    )


def _hermes_argv() -> list[str]:
    hermes = shutil.which("hermes")
    if hermes:
        return [hermes]
    for candidate in (
        Path.home() / ".local/bin/hermes",
        Path.home() / ".hermes/hermes-agent/.hermes/bin/hermes",
    ):
        if candidate.is_file() and os.access(candidate, os.X_OK):
            return [str(candidate)]
    return [sys.executable, "-m", "hermes_cli.main"]


def _run_kanban(cmd: list[str], timeout: int = 30) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        env=os.environ.copy(),
        timeout=timeout,
    )


def dispatch(args: dict, session_id: str = "", task_id: str = "", parent_agent: str = "") -> str:
    del task_id, parent_agent

    role = str(args.get("role", "")).strip()
    task = str(args.get("task", "")).strip()
    if role not in ROLE_SUFFIXES:
        return json.dumps({"ok": False, "error": "invalid_role"}, ensure_ascii=False)
    if not task:
        return json.dumps({"ok": False, "error": "empty_task"}, ensure_ascii=False)

    root = engagement_root()
    engagement_dir, error = _resolve_engagement(
        root,
        str(args.get("engagement_id", "")).strip(),
        session_id,
    )
    if error:
        return json.dumps({"ok": False, "error": error}, ensure_ascii=False)
    assert engagement_dir is not None

    if not _authorization_ok(engagement_dir):
        return json.dumps({"ok": False, "error": "authorization_required"}, ensure_ascii=False)

    assignee = f"rt-{role}"
    title = str(args.get("title", "")).strip() or task
    brief = _brief(engagement_dir, engagement_dir.name, assignee, task)
    # Idempotency: the same engagement + role + task text returns the existing card
    # instead of stacking duplicates (observed when the commander re-planned the same
    # step). ``rerun: true`` deliberately bypasses it.
    dedupe_key = (
        f"rt-{engagement_dir.name}-{assignee}-"
        f"{hashlib.sha1(task.strip().encode('utf-8')).hexdigest()[:12]}"
    )
    if args.get("rerun"):
        dedupe_key = f"{dedupe_key}-{int(time.time())}"

    cmd = _hermes_argv() + [
        "kanban",
        "create",
        title,
        "--assignee",
        assignee,
        "--workspace",
        f"dir:{engagement_dir}",
        "--body",
        brief,
        "--idempotency-key",
        dedupe_key,
        "--json",
    ]
    priority = args.get("priority")
    if priority is not None:
        try:
            cmd += ["--priority", str(int(priority))]
        except (TypeError, ValueError):
            return json.dumps({"ok": False, "error": "invalid_priority"}, ensure_ascii=False)

    try:
        result = _run_kanban(cmd)
    except subprocess.TimeoutExpired:
        return json.dumps({"ok": False, "error": "kanban_timeout"}, ensure_ascii=False)
    except OSError as exc:
        return json.dumps(
            {"ok": False, "error": f"kanban_spawn_failed: {exc}"},
            ensure_ascii=False,
        )

    if result.returncode != 0:
        detail = (result.stderr or result.stdout).strip()[:500]
        return json.dumps(
            {"ok": False, "error": "kanban_failed", "detail": detail},
            ensure_ascii=False,
        )

    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError:
        data = {}

    return json.dumps(
        {
            "ok": True,
            "task_id": data.get("id") or data.get("task_id") or "",
            "assignee": data.get("assignee", assignee),
            "status": data.get("status", ""),
        },
        ensure_ascii=False,
    )


def dispatch_status(args: dict, **kwargs) -> str:
    del kwargs

    task_id = str(args.get("task_id", "")).strip()
    if not task_id:
        return json.dumps({"ok": False, "error": "missing_task_id"}, ensure_ascii=False)

    cmd = _hermes_argv() + ["kanban", "show", task_id, "--json"]
    try:
        result = _run_kanban(cmd)
    except subprocess.TimeoutExpired:
        return json.dumps({"ok": False, "error": "kanban_timeout"}, ensure_ascii=False)
    except OSError as exc:
        return json.dumps(
            {"ok": False, "error": f"kanban_spawn_failed: {exc}"},
            ensure_ascii=False,
        )

    if result.returncode != 0:
        detail = (result.stderr or result.stdout).strip()[:500]
        return json.dumps(
            {"ok": False, "error": "kanban_failed", "detail": detail},
            ensure_ascii=False,
        )

    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError:
        data = {}

    task = data.get("task") or data
    return json.dumps(
        {
            "ok": True,
            "task_id": task.get("id") or task_id,
            "status": task.get("status", ""),
            "summary": data.get("latest_summary") or task.get("summary") or "",
            "result": task.get("result") or "",
        },
        ensure_ascii=False,
    )
