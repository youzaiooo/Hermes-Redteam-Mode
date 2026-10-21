"""Read-only preflight. It reports gaps and never installs."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

_REQUIRED = ("nmap", "nuclei", "sqlmap", "ffuf")
_AUTH_EMPTY = "待填写"


def preflight(root: Path, engagement_id: str, which=None, install=None) -> str:
    del install  # accepted so tests can prove it is never called
    locator = which or shutil.which
    missing = [name for name in _REQUIRED if locator(name) is None]
    auth = Path(root) / engagement_id / "wiki" / "authorization.md"
    text = auth.read_text(encoding="utf-8") if auth.is_file() else ""
    blocked = (not text) or any(f"{field}：{_AUTH_EMPTY}" in text for field in (
        "授权方", "范围", "时间窗", "允许手段", "联系人"
    ))
    skills = sorted(path.parent.name for path in (Path(__file__).resolve().parent / "skills").glob("*/SKILL.md"))
    status = "blocked" if blocked else "ready"
    return json.dumps(
        {
            "ok": True,
            "status": status,
            "reason": "empty_authorization" if blocked else "",
            "missing": missing,
            "skill_count": len(skills),
            "skills": skills,
        },
        ensure_ascii=False,
    )
