import json
import subprocess
from pathlib import Path

from hermes_redteam.dispatch import dispatch, dispatch_status
from hermes_redteam.store import bind_session, open_engagement


def _fill_authorization(root: Path) -> None:
    auth = root / "wiki" / "authorization.md"
    auth.write_text(
        "# 授权记录\n"
        "授权方：ACME\n"
        "范围：10.0.0.0/24\n"
        "时间窗：2026-10-01~2026-10-31\n"
        "允许手段：扫描、验证\n"
        "联系人：ops\n",
        encoding="utf-8",
    )


def _completed(cmd: list[str], stdout: str) -> subprocess.CompletedProcess[str]:
    return subprocess.CompletedProcess(cmd, 0, stdout=stdout, stderr="")


def test_dispatch_builds_kanban_card(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("HERMES_HOME", str(tmp_path))
    root = tmp_path / "redteam" / "engagements"
    open_engagement(root, "lab-01", "Lab 01")
    _fill_authorization(root / "lab-01")

    captured: dict[str, list[str]] = {}

    def fake_run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
        captured["cmd"] = cmd
        return _completed(
            cmd,
            json.dumps({"id": "t-1", "assignee": "rt-recon", "status": "ready"}),
        )

    monkeypatch.setattr("hermes_redteam.dispatch._run_kanban", fake_run)

    result = json.loads(
        dispatch(
            {
                "role": "recon",
                "task": "扫描 10.0.0.0/24",
                "priority": 3,
                "engagement_id": "lab-01",
            }
        )
    )

    assert result["ok"] is True
    assert result["task_id"] == "t-1"
    assert result["assignee"] == "rt-recon"
    assert result["status"] == "ready"

    cmd = captured["cmd"]
    idx = cmd.index("create")
    tail = cmd[idx:]
    assert tail[1] == "扫描 10.0.0.0/24"
    assert "--assignee" in tail
    assert tail[tail.index("--assignee") + 1] == "rt-recon"
    assert "--workspace" in tail
    assert tail[tail.index("--workspace") + 1] == f"dir:{root / 'lab-01'}"
    assert "--priority" in tail
    assert tail[tail.index("--priority") + 1] == "3"
    body = tail[tail.index("--body") + 1]
    assert "靶标: lab-01" in body
    assert "范围: 10.0.0.0/24" in body
    assert "角色: rt-recon" in body
    assert f"靶标目录: {root / 'lab-01'}" in body
    assert "redteam_*" in body
    assert "记录要求" in body


def test_dispatch_uses_stable_idempotency_key(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("HERMES_HOME", str(tmp_path))
    root = tmp_path / "redteam" / "engagements"
    open_engagement(root, "lab-01", "Lab 01")
    _fill_authorization(root / "lab-01")

    keys: list[str] = []

    def fake_run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
        keys.append(cmd[cmd.index("--idempotency-key") + 1])
        return _completed(cmd, json.dumps({"id": "t-1", "assignee": "rt-recon", "status": "ready"}))

    monkeypatch.setattr("hermes_redteam.dispatch._run_kanban", fake_run)

    dispatch({"role": "recon", "task": "同一任务", "engagement_id": "lab-01"})
    dispatch({"role": "recon", "task": "同一任务", "engagement_id": "lab-01"})
    dispatch({"role": "recon", "task": "同一任务", "engagement_id": "lab-01", "rerun": True})

    assert keys[0] == keys[1]
    assert keys[2] != keys[1]
    assert keys[0].startswith("rt-lab-01-rt-recon-")


def test_dispatch_resolves_engagement_from_session(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("HERMES_HOME", str(tmp_path))
    root = tmp_path / "redteam" / "engagements"
    open_engagement(root, "lab-01", "Lab 01")
    _fill_authorization(root / "lab-01")
    bind_session(root, "lab-01", "sess-9", "default")

    captured: dict[str, list[str]] = {}

    def fake_run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
        captured["cmd"] = cmd
        return _completed(cmd, json.dumps({"id": "t-2", "assignee": "rt-recon", "status": "ready"}))

    monkeypatch.setattr("hermes_redteam.dispatch._run_kanban", fake_run)

    result = json.loads(dispatch({"role": "recon", "task": "确认入口"}, session_id="sess-9"))

    assert result["ok"] is True
    assert result["task_id"] == "t-2"
    assert f"dir:{root / 'lab-01'}" in captured["cmd"]


def test_dispatch_refuses_empty_authorization(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("HERMES_HOME", str(tmp_path))
    root = tmp_path / "redteam" / "engagements"
    open_engagement(root, "lab-01", "Lab 01")

    called: list[list[str]] = []

    def fake_run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
        called.append(cmd)
        return _completed(cmd, "{}")

    monkeypatch.setattr("hermes_redteam.dispatch._run_kanban", fake_run)

    result = json.loads(dispatch({"role": "recon", "task": "x", "engagement_id": "lab-01"}))

    assert result["ok"] is False
    assert result["error"] == "authorization_required"
    assert called == []


def test_dispatch_refuses_missing_authorization(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("HERMES_HOME", str(tmp_path))
    root = tmp_path / "redteam" / "engagements"
    open_engagement(root, "lab-01", "Lab 01")
    (root / "lab-01" / "wiki" / "authorization.md").unlink()

    monkeypatch.setattr(
        "hermes_redteam.dispatch._run_kanban",
        lambda cmd: _completed(cmd, "{}"),
    )

    result = json.loads(dispatch({"role": "recon", "task": "x", "engagement_id": "lab-01"}))

    assert result["ok"] is False
    assert result["error"] == "authorization_required"


def test_dispatch_status_parses_show_json(monkeypatch):
    captured: dict[str, list[str]] = {}

    def fake_run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
        captured["cmd"] = cmd
        return _completed(
            cmd,
            json.dumps(
                {
                    "task": {"id": "t-1", "status": "done", "result": "wrote index"},
                    "latest_summary": "completed",
                }
            ),
        )

    monkeypatch.setattr("hermes_redteam.dispatch._run_kanban", fake_run)

    result = json.loads(dispatch_status({"task_id": "t-1"}))

    assert result["ok"] is True
    assert result["task_id"] == "t-1"
    assert result["status"] == "done"
    assert result["summary"] == "completed"
    assert result["result"] == "wrote index"
    assert "kanban" in captured["cmd"]
    assert "show" in captured["cmd"]
    assert "t-1" in captured["cmd"]
