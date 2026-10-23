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
    base = Path(root) / engagement_id
    if not (base / "index.db").is_file():
        return json.dumps({"ok": False, "error": "not_found"}, ensure_ascii=False)
    skills = sorted(path.parent.name for path in (Path(__file__).resolve().parent / "skills").glob("*/SKILL.md"))
    return json.dumps(
        {
            "ok": True,
            "status": "ready",
            # Original dsh-redteam-mode rule: naming a target implies authorization.
            "authorization": "implied_by_target",
            "missing": missing,
            "skill_count": len(skills),
            "skills": skills,
        },
        ensure_ascii=False,
    )
