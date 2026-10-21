"""Score hits and the three-way switch. off records nothing."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

_MODES = {"off", "visible", "enforced"}


def read_score_mode(config_dir: Path) -> str:
    path = Path(config_dir) / "config.yaml"
    if not path.is_file():
        return "off"
    for line in path.read_text(encoding="utf-8").splitlines():
        if "hermes-redteam.score_rules:" in line:
            mode = line.split(":", 1)[1].strip()
            return mode if mode in _MODES else "off"
    return "off"


def write_score_mode(config_dir: Path, mode: str) -> None:
    if mode not in _MODES:
        raise ValueError("invalid score mode")
    path = Path(config_dir) / "config.yaml"
    lines = path.read_text(encoding="utf-8").splitlines() if path.is_file() else []
    kept = [line for line in lines if not line.startswith("score_rules:")]
    kept.append(f"plugins.entries.hermes-redteam.score_rules: {mode}")
    path.write_text("\n".join(kept) + "\n", encoding="utf-8")


def record_score(root: Path, engagement_id: str, mode: str, rule_id: str) -> str:
    if mode not in _MODES or not rule_id.strip():
        return json.dumps({"ok": False, "error": "invalid_input"}, ensure_ascii=False)
    if mode == "off":
        return json.dumps({"ok": True, "recorded": False}, ensure_ascii=False)

    base = Path(root) / engagement_id
    base.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(base / "index.db") as db:
        db.execute(
            "CREATE TABLE IF NOT EXISTS score_hit ("
            "id INTEGER PRIMARY KEY, rule_id TEXT NOT NULL, mode TEXT NOT NULL)"
        )
        db.execute(
            "INSERT INTO score_hit (rule_id, mode) VALUES (?, ?)",
            (rule_id, mode),
        )
    return json.dumps({"ok": True, "recorded": True, "mode": mode}, ensure_ascii=False)


def score_list() -> str:
    categories = [
        {"id": "recon", "points": ["asset-found", "service-found", "web-found"]},
        {"id": "vuln", "points": ["suspected", "confirmed", "reproduced"]},
        {"id": "access", "points": ["credential-ref", "web-login", "shell-pointer"]},
        {"id": "tunnel", "points": ["tunnel-pointer", "tunnel-checked"]},
        {"id": "internal", "points": ["internal-asset", "internal-access", "pivot-pointer"]},
        {"id": "data", "points": ["data-pointer", "config-pointer", "secret-ref"]},
        {"id": "chain", "points": ["chain-pointer", "evidence-linked", "report-ready"]},
        {"id": "report", "points": ["authorization", "asset-index", "evidence-index", "finding-index", "residual-risk"]},
    ]
    return json.dumps({"ok": True, "categories": categories}, ensure_ascii=False)
