"""Engagement directory, SQLite index, and local wiki skeleton."""

from __future__ import annotations

import hashlib
import json
import re
import sqlite3
from pathlib import Path

_ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,63}$")

_SCHEMA = """
CREATE TABLE IF NOT EXISTS engagement (
    id TEXT PRIMARY KEY,
    display_name TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS asset (
    id INTEGER PRIMARY KEY,
    engagement_id TEXT NOT NULL REFERENCES engagement(id),
    stable_key TEXT,
    address TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'new',
    port INTEGER DEFAULT 0,
    service TEXT DEFAULT '',
    product TEXT DEFAULT '',
    version TEXT DEFAULT '',
    url TEXT DEFAULT '',
    title TEXT DEFAULT '',
    names TEXT DEFAULT '',
    provenance TEXT DEFAULT '',
    tool TEXT DEFAULT '',
    scope TEXT DEFAULT '',
    test_status TEXT DEFAULT '',
    test_notes TEXT DEFAULT '',
    first_seen TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_seen TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (engagement_id, stable_key)
);

CREATE TABLE IF NOT EXISTS evidence_ref (
    id INTEGER PRIMARY KEY,
    engagement_id TEXT NOT NULL REFERENCES engagement(id),
    kind TEXT NOT NULL,
    relative_path TEXT NOT NULL,
    sha256 TEXT NOT NULL,
    summary TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS vuln (
    id INTEGER PRIMARY KEY,
    engagement_id TEXT NOT NULL REFERENCES engagement(id),
    asset_key TEXT NOT NULL,
    status TEXT NOT NULL,
    evidence_path TEXT NOT NULL,
    title TEXT DEFAULT '',
    severity TEXT DEFAULT '',
    cve TEXT DEFAULT '',
    target TEXT DEFAULT '',
    evidence TEXT DEFAULT '',
    confidence TEXT DEFAULT '',
    gained TEXT DEFAULT '',
    agent TEXT DEFAULT '',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS http_evidence (
    id INTEGER PRIMARY KEY,
    engagement_id TEXT NOT NULL REFERENCES engagement(id),
    asset_key TEXT NOT NULL,
    request_path TEXT NOT NULL,
    response_path TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS credential_ref (
    id INTEGER PRIMARY KEY,
    engagement_id TEXT NOT NULL REFERENCES engagement(id),
    asset_key TEXT NOT NULL,
    evidence_path TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS access_session (
    id INTEGER PRIMARY KEY,
    engagement_id TEXT NOT NULL REFERENCES engagement(id),
    asset_key TEXT NOT NULL,
    method TEXT NOT NULL,
    evidence_path TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS tunnel (
    id INTEGER PRIMARY KEY,
    engagement_id TEXT NOT NULL REFERENCES engagement(id),
    asset_key TEXT NOT NULL,
    entry_kind TEXT NOT NULL,
    evidence_path TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'new'
);

CREATE TABLE IF NOT EXISTS poc_ref (
    id INTEGER PRIMARY KEY,
    engagement_id TEXT NOT NULL REFERENCES engagement(id),
    category TEXT NOT NULL,
    asset_key TEXT NOT NULL,
    source_path TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'new'
);

CREATE TABLE IF NOT EXISTS asset_link (
    id INTEGER PRIMARY KEY,
    engagement_id TEXT NOT NULL REFERENCES engagement(id),
    source_key TEXT NOT NULL,
    target_key TEXT NOT NULL,
    relation TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS chain_step (
    id INTEGER PRIMARY KEY,
    engagement_id TEXT NOT NULL REFERENCES engagement(id),
    asset_key TEXT NOT NULL,
    command_path TEXT NOT NULL,
    result TEXT NOT NULL,
    stage_code TEXT DEFAULT '',
    tool TEXT DEFAULT '',
    summary TEXT DEFAULT '',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS attack_file (
    id INTEGER PRIMARY KEY,
    engagement_id TEXT NOT NULL REFERENCES engagement(id),
    asset_key TEXT NOT NULL,
    relative_path TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS webshell (
    id INTEGER PRIMARY KEY,
    engagement_id TEXT NOT NULL REFERENCES engagement(id),
    asset_key TEXT NOT NULL,
    shell_type TEXT NOT NULL,
    evidence_path TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'new'
);

CREATE TABLE IF NOT EXISTS score_event (
    id INTEGER PRIMARY KEY,
    engagement_id TEXT NOT NULL REFERENCES engagement(id),
    rule_id TEXT NOT NULL,
    evidence_path TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS shot (
    id INTEGER PRIMARY KEY,
    engagement_id TEXT NOT NULL REFERENCES engagement(id),
    asset_key TEXT NOT NULL,
    relative_path TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS score_point (
    id INTEGER PRIMARY KEY,
    engagement_id TEXT NOT NULL REFERENCES engagement(id),
    point_id TEXT NOT NULL,
    category TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS scan_ref (
    id INTEGER PRIMARY KEY,
    engagement_id TEXT NOT NULL REFERENCES engagement(id),
    asset_key TEXT NOT NULL,
    relative_path TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS note_ref (
    id INTEGER PRIMARY KEY,
    engagement_id TEXT NOT NULL REFERENCES engagement(id),
    asset_key TEXT NOT NULL,
    relative_path TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS knowledge_ref (
    id INTEGER PRIMARY KEY,
    engagement_id TEXT NOT NULL REFERENCES engagement(id),
    asset_key TEXT NOT NULL,
    relative_path TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS finding (
    id INTEGER PRIMARY KEY,
    engagement_id TEXT NOT NULL REFERENCES engagement(id),
    asset_key TEXT NOT NULL,
    conclusion TEXT NOT NULL,
    evidence_path TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS attack_chain (
    id INTEGER PRIMARY KEY,
    engagement_id TEXT NOT NULL REFERENCES engagement(id),
    conclusion TEXT NOT NULL,
    evidence_ids TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS reservation (
    id INTEGER PRIMARY KEY,
    engagement_id TEXT NOT NULL REFERENCES engagement(id),
    role TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    released_at TEXT
);
"""

_AUTH_FIELDS = ("授权方", "范围", "时间窗", "允许手段", "联系人")

_MIGRATION_COLUMNS: dict[str, dict[str, str]] = {
    "asset": {
        "port": "INTEGER DEFAULT 0",
        "service": "TEXT DEFAULT ''",
        "product": "TEXT DEFAULT ''",
        "version": "TEXT DEFAULT ''",
        "url": "TEXT DEFAULT ''",
        "title": "TEXT DEFAULT ''",
        "names": "TEXT DEFAULT ''",
        "provenance": "TEXT DEFAULT ''",
        "tool": "TEXT DEFAULT ''",
        "scope": "TEXT DEFAULT ''",
        "test_status": "TEXT DEFAULT ''",
        "test_notes": "TEXT DEFAULT ''",
    },
    "vuln": {
        "title": "TEXT DEFAULT ''",
        "severity": "TEXT DEFAULT ''",
        "cve": "TEXT DEFAULT ''",
        "target": "TEXT DEFAULT ''",
        "evidence": "TEXT DEFAULT ''",
        "confidence": "TEXT DEFAULT ''",
        "gained": "TEXT DEFAULT ''",
        "agent": "TEXT DEFAULT ''",
        "created_at": "TEXT DEFAULT ''",
    },
    "chain_step": {
        "stage_code": "TEXT DEFAULT ''",
        "tool": "TEXT DEFAULT ''",
        "summary": "TEXT DEFAULT ''",
        "created_at": "TEXT DEFAULT ''",
    },
}


def migrate_db(db: sqlite3.Connection) -> None:
    """Upgrade an older index.db in place using PRAGMA table_info + ALTER TABLE."""
    present = {
        row[0]
        for row in db.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table'"
        )
    }
    for table, columns in _MIGRATION_COLUMNS.items():
        if table not in present:
            continue
        existing = {
            row[1] for row in db.execute(f"PRAGMA table_info({table})")
        }
        for name, ddl in columns.items():
            if name not in existing:
                db.execute(f"ALTER TABLE {table} ADD COLUMN {name} {ddl}")
    for table in ("vuln", "chain_step"):
        if table not in present:
            continue
        db.execute(
            f"UPDATE {table} SET created_at = CURRENT_TIMESTAMP "
            "WHERE created_at IS NULL OR created_at = ''"
        )
    db.commit()


def _connect(path: Path | str) -> sqlite3.Connection:
    db = sqlite3.connect(path)
    migrate_db(db)
    return db


def _clean(value: object) -> str:
    return str(value or "").strip()


def _parse_port(value: object) -> int:
    try:
        port = int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError("invalid_port") from exc
    if port < 0:
        raise ValueError("invalid_port")
    return port


def _derive_stable_key(address: str, port: int = 0) -> str:
    address = _clean(address)
    if port:
        return f"{address}:{port}"
    return address


def open_engagement(root: Path, engagement_id: str, display_name: str) -> str:
    if not _ID_RE.match(engagement_id):
        return json.dumps({"ok": False, "error": "invalid_id"}, ensure_ascii=False)
    if not display_name.strip():
        return json.dumps({"ok": False, "error": "empty_name"}, ensure_ascii=False)

    base = Path(root) / engagement_id
    wiki = base / "wiki"
    pages = wiki / "pages"
    raw = base / "raw"
    pages.mkdir(parents=True, exist_ok=True)
    raw.mkdir(parents=True, exist_ok=True)

    auth = wiki / "authorization.md"
    if not auth.exists():
        lines = ["# 授权记录", ""]
        lines.extend(f"{field}：待填写" for field in _AUTH_FIELDS)
        lines.append("")
        auth.write_text("\n".join(lines), encoding="utf-8")

    _write_once(wiki / "SCHEMA.md", "# 本靶标 Wiki\n\n事实只写在这个目录。凭据真值不进页面。\n")
    _write_once(wiki / "index.md", f"# {display_name}\n\n开工先读本页。\n")
    _write_once(wiki / "log.md", "# 动作记录\n\n")

    db_path = base / "index.db"
    with _connect(db_path) as db:
        db.executescript(_SCHEMA)
        db.execute(
            "INSERT OR IGNORE INTO engagement (id, display_name) VALUES (?, ?)",
            (engagement_id, display_name),
        )

    return json.dumps(
        {"ok": True, "id": engagement_id, "path": str(base)},
        ensure_ascii=False,
    )


def bind_session(root: Path, engagement_id: str, session_id: str, profile: str) -> str:
    if not _ID_RE.match(engagement_id) or not session_id.strip() or not profile.strip():
        return json.dumps({"ok": False, "error": "invalid_input"}, ensure_ascii=False)
    base = Path(root) / engagement_id
    if not (base / "index.db").is_file():
        return json.dumps({"ok": False, "error": "not_found"}, ensure_ascii=False)
    state = {
        "engagement_id": engagement_id,
        "session_id": session_id,
        "profile": profile,
    }
    (base / "session.json").write_text(
        json.dumps(state, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return json.dumps({"ok": True, **state}, ensure_ascii=False)


def session_info(root: Path, engagement_id: str) -> str:
    state_path = Path(root) / engagement_id / "session.json"
    if not state_path.is_file():
        return json.dumps({"ok": False, "error": "session_unbound"}, ensure_ascii=False)
    state = json.loads(state_path.read_text(encoding="utf-8"))
    return json.dumps({"ok": True, **state}, ensure_ascii=False)


_SECRET_FIELDS = {"password", "secret", "cookie", "token", "credential", "payload", "steps", "tool"}


def query_board(root: Path, engagement_id: str) -> str:
    db_path = Path(root) / engagement_id / "index.db"
    if not db_path.is_file():
        return json.dumps({"ok": False, "error": "not_found"}, ensure_ascii=False)
    with _connect(db_path) as db:
        assets = db.execute("SELECT COUNT(*) FROM asset").fetchone()[0]
        findings = db.execute("SELECT COUNT(*) FROM finding").fetchone()[0]
    return json.dumps(
        {
            "ok": True,
            "id": engagement_id,
            "assets": assets,
            "findings": findings,
            "asset_count": assets,
            "finding_count": findings,
        },
        ensure_ascii=False,
    )


def add_asset(
    root: Path,
    engagement_id: str,
    stable_key: str = "",
    address: str = "",
    status: str = "new",
    extra: dict | None = None,
    port: int | None = None,
    service: str | None = None,
    product: str | None = None,
    version: str | None = None,
    url: str | None = None,
    title: str | None = None,
    names: str | None = None,
    provenance: str | None = None,
    tool: str | None = None,
    scope: str | None = None,
    test_status: str | None = None,
    test_notes: str | None = None,
) -> str:
    if extra and _SECRET_FIELDS.intersection(extra):
        return json.dumps({"ok": False, "error": "secret_field"}, ensure_ascii=False)
    address = _clean(address)
    if not _ID_RE.match(engagement_id) or not address:
        return json.dumps({"ok": False, "error": "invalid_input"}, ensure_ascii=False)
    if port is not None:
        try:
            port = _parse_port(port)
        except ValueError:
            return json.dumps({"ok": False, "error": "invalid_port"}, ensure_ascii=False)
    key = _clean(stable_key) or _derive_stable_key(address, port or 0)
    if not key:
        return json.dumps({"ok": False, "error": "invalid_input"}, ensure_ascii=False)
    db_path = Path(root) / engagement_id / "index.db"
    if not db_path.is_file():
        return json.dumps({"ok": False, "error": "not_found"}, ensure_ascii=False)
    if not _has_reservation(db_path, engagement_id):
        return json.dumps({"ok": False, "error": "reservation_required"}, ensure_ascii=False)

    with _connect(db_path) as db:
        existing = db.execute(
            "SELECT id FROM asset WHERE engagement_id = ? AND stable_key = ?",
            (engagement_id, key),
        ).fetchone()
        if existing:
            sets = ["address = ?", "status = ?", "last_seen = CURRENT_TIMESTAMP"]
            values: list[object] = [address, _clean(status)]
            for column, value in (
                ("port", port),
                ("service", service),
                ("product", product),
                ("version", version),
                ("url", url),
                ("title", title),
                ("names", names),
                ("provenance", provenance),
                ("tool", tool),
                ("scope", scope),
                ("test_status", test_status),
                ("test_notes", test_notes),
            ):
                if value is not None:
                    sets.append(f"{column} = ?")
                    values.append(_clean(value))
            values.extend((engagement_id, key))
            db.execute(
                "UPDATE asset SET " + ", ".join(sets)
                + " WHERE engagement_id = ? AND stable_key = ?",
                values,
            )
            updated = True
        else:
            db.execute(
                "INSERT INTO asset (engagement_id, stable_key, address, status, port, "
                "service, product, version, url, title, names, provenance, tool, scope, "
                "test_status, test_notes) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    engagement_id,
                    key,
                    address,
                    _clean(status),
                    port or 0,
                    _clean(service),
                    _clean(product),
                    _clean(version),
                    _clean(url),
                    _clean(title),
                    _clean(names),
                    _clean(provenance),
                    _clean(tool),
                    _clean(scope),
                    _clean(test_status),
                    _clean(test_notes),
                ),
            )
            updated = False
    return json.dumps(
        {"ok": True, "stable_key": key, "updated": updated},
        ensure_ascii=False,
    )


def query_assets(
    root: Path,
    engagement_id: str,
    stable_key: str = "",
    status: str = "",
    assessed: bool | None = None,
) -> str:
    db_path = Path(root) / engagement_id / "index.db"
    if not db_path.is_file():
        return json.dumps({"ok": False, "error": "not_found"}, ensure_ascii=False)
    sql = (
        "SELECT stable_key, address, port, status, service, product, version, url, "
        "title, names, provenance, tool, scope, test_status, test_notes, "
        "first_seen, last_seen "
        "FROM asset WHERE engagement_id = ?"
    )
    params: list[object] = [engagement_id]
    if stable_key:
        sql += " AND stable_key = ?"
        params.append(stable_key)
    if status:
        sql += " AND status = ?"
        params.append(status)
    if assessed is True:
        sql += " AND test_status <> ''"
    elif assessed is False:
        sql += " AND test_status = ''"
    with _connect(db_path) as db:
        rows = db.execute(sql, params).fetchall()
    assets = [
        {
            "stable_key": row[0],
            "address": row[1],
            "port": row[2],
            "status": row[3],
            "service": row[4],
            "product": row[5],
            "version": row[6],
            "url": row[7],
            "title": row[8],
            "names": row[9],
            "provenance": row[10],
            "tool": row[11],
            "scope": row[12],
            "test_status": row[13],
            "test_notes": row[14],
            "first_seen": row[15],
            "last_seen": row[16],
        }
        for row in rows
    ]
    return json.dumps(
        {"ok": True, "count": len(assets), "assets": assets},
        ensure_ascii=False,
    )


def asset_get(root: Path, engagement_id: str, stable_key: str) -> str:
    found = json.loads(query_assets(root, engagement_id, stable_key))
    if not found["ok"]:
        return json.dumps(found, ensure_ascii=False)
    if found["count"] != 1:
        return json.dumps({"ok": False, "error": "not_found"}, ensure_ascii=False)
    return json.dumps({"ok": True, "asset": found["assets"][0]}, ensure_ascii=False)


def asset_stats(root: Path, engagement_id: str) -> str:
    db_path = Path(root) / engagement_id / "index.db"
    if not db_path.is_file():
        return json.dumps({"ok": False, "error": "not_found"}, ensure_ascii=False)
    with _connect(db_path) as db:
        assets = db.execute(
            "SELECT COUNT(*) FROM asset WHERE engagement_id = ?",
            (engagement_id,),
        ).fetchone()[0]
        web = db.execute(
            "SELECT COUNT(*) FROM asset WHERE engagement_id = ? AND address LIKE 'http%'",
            (engagement_id,),
        ).fetchone()[0]
    return json.dumps({"ok": True, "assets": assets, "web": web}, ensure_ascii=False)


def asset_test(root: Path, engagement_id: str, stable_key: str, note: str) -> str:
    db_path = Path(root) / engagement_id / "index.db"
    if not db_path.is_file():
        return json.dumps({"ok": False, "error": "not_found"}, ensure_ascii=False)
    if not _has_reservation(db_path, engagement_id):
        return json.dumps({"ok": False, "error": "reservation_required"}, ensure_ascii=False)
    line = " ".join(note.split())
    if not line or len(line) > 80:
        return json.dumps({"ok": False, "error": "invalid_input"}, ensure_ascii=False)
    with _connect(db_path) as db:
        row = db.execute(
            "SELECT status, test_notes FROM asset "
            "WHERE engagement_id = ? AND stable_key = ?",
            (engagement_id, stable_key),
        ).fetchone()
        if not row:
            return json.dumps({"ok": False, "error": "not_found"}, ensure_ascii=False)
        status = f"{row[0]}; {line}"
        test_notes = f"{row[1]}\n{line}".strip() if row[1] else line
        db.execute(
            "UPDATE asset SET status = ?, test_status = ?, test_notes = ?, "
            "last_seen = CURRENT_TIMESTAMP "
            "WHERE engagement_id = ? AND stable_key = ?",
            (status, line, test_notes, engagement_id, stable_key),
        )
    return json.dumps(
        {
            "ok": True,
            "stable_key": stable_key,
            "status": status,
            "test_status": line,
            "test_notes": test_notes,
        },
        ensure_ascii=False,
    )


def asset_assess(root: Path, engagement_id: str, stable_key: str, priority: str) -> str:
    return asset_test(root, engagement_id, stable_key, f"assess {priority}")


def reserve_write(root: Path, engagement_id: str, role: str) -> str:
    if not _ID_RE.match(engagement_id) or not role.startswith("rt-"):
        return json.dumps({"ok": False, "error": "invalid_input"}, ensure_ascii=False)
    db_path = Path(root) / engagement_id / "index.db"
    if not db_path.is_file():
        return json.dumps({"ok": False, "error": "not_found"}, ensure_ascii=False)
    with _connect(db_path) as db:
        db.execute("BEGIN IMMEDIATE")
        count = db.execute(
            "SELECT COUNT(*) FROM reservation WHERE engagement_id = ? AND released_at IS NULL",
            (engagement_id,),
        ).fetchone()[0]
        if count >= 3:
            db.rollback()
            return json.dumps({"ok": False, "error": "reservation_full"}, ensure_ascii=False)
        cursor = db.execute(
            "INSERT INTO reservation (engagement_id, role) VALUES (?, ?)",
            (engagement_id, role),
        )
    return json.dumps(
        {"ok": True, "id": cursor.lastrowid, "role": role, "open": count + 1},
        ensure_ascii=False,
    )


def release_write(root: Path, engagement_id: str, reservation_id: int) -> str:
    db_path = Path(root) / engagement_id / "index.db"
    if not db_path.is_file():
        return json.dumps({"ok": False, "error": "not_found"}, ensure_ascii=False)
    with _connect(db_path) as db:
        updated = db.execute(
            "UPDATE reservation SET released_at = CURRENT_TIMESTAMP "
            "WHERE id = ? AND engagement_id = ? AND released_at IS NULL",
            (reservation_id, engagement_id),
        ).rowcount
    if updated != 1:
        return json.dumps({"ok": False, "error": "not_held"}, ensure_ascii=False)
    return json.dumps({"ok": True, "id": reservation_id}, ensure_ascii=False)


def agent_slot(root: Path, engagement_id: str) -> str:
    db_path = Path(root) / engagement_id / "index.db"
    if not db_path.is_file():
        return json.dumps({"ok": False, "error": "not_found"}, ensure_ascii=False)
    with _connect(db_path) as db:
        used = db.execute(
            "SELECT COUNT(*) FROM reservation WHERE engagement_id = ? AND released_at IS NULL",
            (engagement_id,),
        ).fetchone()[0]
    return json.dumps(
        {"ok": True, "cap": 3, "used": used, "free": 3 - used},
        ensure_ascii=False,
    )


def _has_reservation(db_path: Path, engagement_id: str) -> bool:
    with _connect(db_path) as db:
        count = db.execute(
            "SELECT COUNT(*) FROM reservation WHERE engagement_id = ? AND released_at IS NULL",
            (engagement_id,),
        ).fetchone()[0]
    return count > 0


def add_evidence(
    root: Path,
    engagement_id: str,
    kind: str,
    relative_path: str,
    summary: str,
) -> str:
    if not _ID_RE.match(engagement_id) or not kind.strip() or not summary.strip():
        return json.dumps({"ok": False, "error": "invalid_input"}, ensure_ascii=False)
    if relative_path.startswith("/") or ".." in Path(relative_path).parts:
        return json.dumps({"ok": False, "error": "invalid_path"}, ensure_ascii=False)
    base = Path(root) / engagement_id
    target = (base / relative_path).resolve()
    if not target.is_relative_to(base.resolve()) or not target.is_file():
        return json.dumps({"ok": False, "error": "missing_file"}, ensure_ascii=False)
    digest = hashlib.sha256(target.read_bytes()).hexdigest()
    line = " ".join(summary.split())
    if len(line) > 120:
        return json.dumps({"ok": False, "error": "summary_too_long"}, ensure_ascii=False)
    db_path = base / "index.db"
    if not db_path.is_file():
        return json.dumps({"ok": False, "error": "not_found"}, ensure_ascii=False)
    with _connect(db_path) as db:
        db.execute(
            "INSERT INTO evidence_ref (engagement_id, kind, relative_path, sha256, summary) "
            "VALUES (?, ?, ?, ?, ?)",
            (engagement_id, kind, relative_path, digest, line),
        )
    return json.dumps(
        {"ok": True, "relative_path": relative_path, "sha256": digest},
        ensure_ascii=False,
    )


def vuln_add(
    root: Path,
    engagement_id: str,
    asset_key: str,
    status: str,
    evidence_path: str,
    title: str | None = None,
    severity: str | None = None,
    cve: str | None = None,
    target: str | None = None,
    evidence: str | None = None,
    confidence: str | None = None,
    gained: str | None = None,
    agent: str | None = None,
) -> str:
    if not _has_reservation(Path(root) / engagement_id / "index.db", engagement_id):
        return json.dumps({"ok": False, "error": "reservation_required"}, ensure_ascii=False)
    if evidence_path.startswith("/") or ".." in Path(evidence_path).parts:
        return json.dumps({"ok": False, "error": "invalid_input"}, ensure_ascii=False)
    with _connect(Path(root) / engagement_id / "index.db") as db:
        db.execute(
            "INSERT INTO vuln (engagement_id, asset_key, status, evidence_path, "
            "title, severity, cve, target, evidence, confidence, gained, agent) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                engagement_id,
                _clean(asset_key),
                _clean(status),
                _clean(evidence_path),
                _clean(title),
                _clean(severity),
                _clean(cve),
                _clean(target),
                _clean(evidence),
                _clean(confidence),
                _clean(gained),
                _clean(agent),
            ),
        )
    return json.dumps({"ok": True, "asset_key": asset_key}, ensure_ascii=False)


def vuln_query(root: Path, engagement_id: str, asset_key: str = "") -> str:
    db_path = Path(root) / engagement_id / "index.db"
    if not db_path.is_file():
        return json.dumps({"ok": False, "error": "not_found"}, ensure_ascii=False)
    sql = (
        "SELECT asset_key, status, evidence_path, title, severity, cve, target, "
        "evidence, confidence, gained, agent, created_at "
        "FROM vuln WHERE engagement_id = ?"
    )
    params: list[object] = [engagement_id]
    if asset_key:
        sql += " AND asset_key = ?"
        params.append(asset_key)
    with _connect(db_path) as db:
        rows = db.execute(sql, params).fetchall()
    vulns = [
        {
            "asset_key": row[0],
            "status": row[1],
            "evidence_path": row[2],
            "title": row[3],
            "severity": row[4],
            "cve": row[5],
            "target": row[6],
            "evidence": row[7],
            "confidence": row[8],
            "gained": row[9],
            "agent": row[10],
            "created_at": row[11],
        }
        for row in rows
    ]
    return json.dumps({"ok": True, "count": len(vulns), "vulns": vulns}, ensure_ascii=False)


def vuln_update(root: Path, engagement_id: str, asset_key: str, status: str) -> str:
    if not _has_reservation(Path(root) / engagement_id / "index.db", engagement_id):
        return json.dumps({"ok": False, "error": "reservation_required"}, ensure_ascii=False)
    if not status.strip():
        return json.dumps({"ok": False, "error": "invalid_input"}, ensure_ascii=False)
    with _connect(Path(root) / engagement_id / "index.db") as db:
        updated = db.execute(
            "UPDATE vuln SET status = ? WHERE engagement_id = ? AND asset_key = ?",
            (status, engagement_id, asset_key),
        ).rowcount
    if updated != 1:
        return json.dumps({"ok": False, "error": "not_found"}, ensure_ascii=False)
    return json.dumps({"ok": True, "asset_key": asset_key, "status": status}, ensure_ascii=False)


def http_evidence_add(
    root: Path,
    engagement_id: str,
    asset_key: str,
    request_path: str,
    response_path: str,
) -> str:
    if not _has_reservation(Path(root) / engagement_id / "index.db", engagement_id):
        return json.dumps({"ok": False, "error": "reservation_required"}, ensure_ascii=False)
    for path in (request_path, response_path):
        if path.startswith("/") or ".." in Path(path).parts:
            return json.dumps({"ok": False, "error": "invalid_input"}, ensure_ascii=False)
    with _connect(Path(root) / engagement_id / "index.db") as db:
        db.execute(
            "INSERT INTO http_evidence "
            "(engagement_id, asset_key, request_path, response_path) VALUES (?, ?, ?, ?)",
            (engagement_id, asset_key, request_path, response_path),
        )
    return json.dumps({"ok": True, "asset_key": asset_key}, ensure_ascii=False)


def credential_add(
    root: Path,
    engagement_id: str,
    asset_key: str,
    evidence_path: str,
    extra: dict | None = None,
) -> str:
    if extra and _SECRET_FIELDS.intersection(extra):
        return json.dumps({"ok": False, "error": "secret_field"}, ensure_ascii=False)
    if "secret_value" in (extra or {}):
        return json.dumps({"ok": False, "error": "secret_field"}, ensure_ascii=False)
    if not _has_reservation(Path(root) / engagement_id / "index.db", engagement_id):
        return json.dumps({"ok": False, "error": "reservation_required"}, ensure_ascii=False)
    if evidence_path.startswith("/") or ".." in Path(evidence_path).parts:
        return json.dumps({"ok": False, "error": "invalid_input"}, ensure_ascii=False)
    with _connect(Path(root) / engagement_id / "index.db") as db:
        db.execute(
            "INSERT INTO credential_ref (engagement_id, asset_key, evidence_path) VALUES (?, ?, ?)",
            (engagement_id, asset_key, evidence_path),
        )
    return json.dumps({"ok": True, "asset_key": asset_key}, ensure_ascii=False)


def credential_list(root: Path, engagement_id: str) -> str:
    db_path = Path(root) / engagement_id / "index.db"
    if not db_path.is_file():
        return json.dumps({"ok": False, "error": "not_found"}, ensure_ascii=False)
    with _connect(db_path) as db:
        rows = db.execute(
            "SELECT asset_key, evidence_path FROM credential_ref WHERE engagement_id = ?",
            (engagement_id,),
        ).fetchall()
    credentials = [
        {"asset_key": row[0], "evidence_path": row[1]}
        for row in rows
    ]
    return json.dumps(
        {"ok": True, "count": len(credentials), "credentials": credentials},
        ensure_ascii=False,
    )


def access_add(
    root: Path,
    engagement_id: str,
    asset_key: str,
    method: str,
    evidence_path: str,
) -> str:
    if not _has_reservation(Path(root) / engagement_id / "index.db", engagement_id):
        return json.dumps({"ok": False, "error": "reservation_required"}, ensure_ascii=False)
    if evidence_path.startswith("/") or ".." in Path(evidence_path).parts or not method.strip():
        return json.dumps({"ok": False, "error": "invalid_input"}, ensure_ascii=False)
    with _connect(Path(root) / engagement_id / "index.db") as db:
        db.execute(
            "INSERT INTO access_session (engagement_id, asset_key, method, evidence_path) "
            "VALUES (?, ?, ?, ?)",
            (engagement_id, asset_key, method, evidence_path),
        )
    return json.dumps({"ok": True, "asset_key": asset_key}, ensure_ascii=False)


def access_list(root: Path, engagement_id: str) -> str:
    db_path = Path(root) / engagement_id / "index.db"
    if not db_path.is_file():
        return json.dumps({"ok": False, "error": "not_found"}, ensure_ascii=False)
    with _connect(db_path) as db:
        rows = db.execute(
            "SELECT asset_key, method, evidence_path FROM access_session WHERE engagement_id = ?",
            (engagement_id,),
        ).fetchall()
    sessions_found = [
        {"asset_key": row[0], "method": row[1], "evidence_path": row[2]}
        for row in rows
    ]
    return json.dumps(
        {"ok": True, "count": len(sessions_found), "sessions": sessions_found},
        ensure_ascii=False,
    )


def sessions(root: Path, engagement_id: str) -> str:
    db_path = Path(root) / engagement_id / "index.db"
    if not db_path.is_file():
        return json.dumps({"ok": False, "error": "not_found"}, ensure_ascii=False)
    with _connect(db_path) as db:
        access = db.execute("SELECT COUNT(*) FROM access_session").fetchone()[0]
        credentials = db.execute("SELECT COUNT(*) FROM credential_ref").fetchone()[0]
    return json.dumps(
        {"ok": True, "access": access, "credentials": credentials},
        ensure_ascii=False,
    )


def session_check(root: Path, engagement_id: str) -> str:
    db_path = Path(root) / engagement_id / "index.db"
    if not db_path.is_file():
        return json.dumps({"ok": False, "error": "not_found"}, ensure_ascii=False)
    if not _has_reservation(db_path, engagement_id):
        return json.dumps({"ok": False, "error": "reservation_required"}, ensure_ascii=False)
    with _connect(db_path) as db:
        webshells = db.execute(
            "UPDATE webshell SET status = 'checked' WHERE engagement_id = ?",
            (engagement_id,),
        ).rowcount
        tunnels = db.execute(
            "UPDATE tunnel SET status = 'checked' WHERE engagement_id = ?",
            (engagement_id,),
        ).rowcount
    return json.dumps(
        {"ok": True, "webshells": webshells, "tunnels": tunnels, "status": "checked"},
        ensure_ascii=False,
    )


def tunnel_add(
    root: Path,
    engagement_id: str,
    asset_key: str,
    entry_kind: str,
    evidence_path: str,
) -> str:
    if not _has_reservation(Path(root) / engagement_id / "index.db", engagement_id):
        return json.dumps({"ok": False, "error": "reservation_required"}, ensure_ascii=False)
    if not entry_kind.strip() or evidence_path.startswith("/") or ".." in Path(evidence_path).parts:
        return json.dumps({"ok": False, "error": "invalid_input"}, ensure_ascii=False)
    with _connect(Path(root) / engagement_id / "index.db") as db:
        db.execute(
            "INSERT INTO tunnel (engagement_id, asset_key, entry_kind, evidence_path) "
            "VALUES (?, ?, ?, ?)",
            (engagement_id, asset_key, entry_kind, evidence_path),
        )
    return json.dumps({"ok": True, "asset_key": asset_key}, ensure_ascii=False)


def tunnel_update(root: Path, engagement_id: str, asset_key: str, status: str) -> str:
    if not _has_reservation(Path(root) / engagement_id / "index.db", engagement_id):
        return json.dumps({"ok": False, "error": "reservation_required"}, ensure_ascii=False)
    if not status.strip():
        return json.dumps({"ok": False, "error": "invalid_input"}, ensure_ascii=False)
    with _connect(Path(root) / engagement_id / "index.db") as db:
        changed = db.execute(
            "UPDATE tunnel SET status = ? WHERE engagement_id = ? AND asset_key = ?",
            (status, engagement_id, asset_key),
        ).rowcount
    if changed != 1:
        return json.dumps({"ok": False, "error": "not_found"}, ensure_ascii=False)
    return json.dumps({"ok": True, "status": status}, ensure_ascii=False)


def tunnel_list(root: Path, engagement_id: str) -> str:
    db_path = Path(root) / engagement_id / "index.db"
    if not db_path.is_file():
        return json.dumps({"ok": False, "error": "not_found"}, ensure_ascii=False)
    with _connect(db_path) as db:
        rows = db.execute(
            "SELECT asset_key, entry_kind, evidence_path FROM tunnel WHERE engagement_id = ?",
            (engagement_id,),
        ).fetchall()
    tunnels = [
        {"asset_key": row[0], "entry_kind": row[1], "evidence_path": row[2]}
        for row in rows
    ]
    return json.dumps({"ok": True, "count": len(tunnels), "tunnels": tunnels}, ensure_ascii=False)


def poc_add(
    root: Path,
    engagement_id: str,
    category: str,
    asset_key: str,
    source_path: str,
) -> str:
    if not _has_reservation(Path(root) / engagement_id / "index.db", engagement_id):
        return json.dumps({"ok": False, "error": "reservation_required"}, ensure_ascii=False)
    if not category.strip() or source_path.startswith("/") or ".." in Path(source_path).parts:
        return json.dumps({"ok": False, "error": "invalid_input"}, ensure_ascii=False)
    with _connect(Path(root) / engagement_id / "index.db") as db:
        db.execute(
            "INSERT INTO poc_ref (engagement_id, category, asset_key, source_path) "
            "VALUES (?, ?, ?, ?)",
            (engagement_id, category, asset_key, source_path),
        )
    return json.dumps({"ok": True, "asset_key": asset_key}, ensure_ascii=False)


def poc_search(root: Path, engagement_id: str, category: str) -> str:
    db_path = Path(root) / engagement_id / "index.db"
    if not db_path.is_file():
        return json.dumps({"ok": False, "error": "not_found"}, ensure_ascii=False)
    with _connect(db_path) as db:
        rows = db.execute(
            "SELECT category, asset_key, source_path FROM poc_ref "
            "WHERE engagement_id = ? AND category = ?",
            (engagement_id, category),
        ).fetchall()
    pocs = [
        {"category": row[0], "asset_key": row[1], "source_path": row[2]}
        for row in rows
    ]
    return json.dumps({"ok": True, "count": len(pocs), "pocs": pocs}, ensure_ascii=False)


def poc_list(root: Path, engagement_id: str) -> str:
    db_path = Path(root) / engagement_id / "index.db"
    if not db_path.is_file():
        return json.dumps({"ok": False, "error": "not_found"}, ensure_ascii=False)
    with _connect(db_path) as db:
        rows = db.execute(
            "SELECT category, asset_key, source_path, status FROM poc_ref WHERE engagement_id = ?",
            (engagement_id,),
        ).fetchall()
    pocs = [
        {"category": row[0], "asset_key": row[1], "source_path": row[2], "status": row[3]}
        for row in rows
    ]
    return json.dumps({"ok": True, "count": len(pocs), "pocs": pocs}, ensure_ascii=False)


def poc_get(root: Path, engagement_id: str, asset_key: str) -> str:
    found = json.loads(poc_list(root, engagement_id))
    if not found["ok"]:
        return json.dumps(found, ensure_ascii=False)
    matches = [item for item in found["pocs"] if item["asset_key"] == asset_key]
    if len(matches) != 1:
        return json.dumps({"ok": False, "error": "not_found"}, ensure_ascii=False)
    return json.dumps({"ok": True, "poc": matches[0]}, ensure_ascii=False)


def poc_update(root: Path, engagement_id: str, asset_key: str, status: str) -> str:
    if not _has_reservation(Path(root) / engagement_id / "index.db", engagement_id):
        return json.dumps({"ok": False, "error": "reservation_required"}, ensure_ascii=False)
    if not status.strip():
        return json.dumps({"ok": False, "error": "invalid_input"}, ensure_ascii=False)
    with _connect(Path(root) / engagement_id / "index.db") as db:
        changed = db.execute(
            "UPDATE poc_ref SET status = ? WHERE engagement_id = ? AND asset_key = ?",
            (status, engagement_id, asset_key),
        ).rowcount
    if changed != 1:
        return json.dumps({"ok": False, "error": "not_found"}, ensure_ascii=False)
    return json.dumps({"ok": True, "status": status}, ensure_ascii=False)


def poc_use(root: Path, engagement_id: str, asset_key: str, result: str) -> str:
    if not _has_reservation(Path(root) / engagement_id / "index.db", engagement_id):
        return json.dumps({"ok": False, "error": "reservation_required"}, ensure_ascii=False)
    line = " ".join(result.split())
    if not line or len(line) > 80:
        return json.dumps({"ok": False, "error": "invalid_input"}, ensure_ascii=False)
    found = json.loads(poc_get(root, engagement_id, asset_key))
    if not found["ok"]:
        return json.dumps(found, ensure_ascii=False)
    updated = json.loads(poc_update(root, engagement_id, asset_key, line))
    if not updated["ok"]:
        return json.dumps(updated, ensure_ascii=False)
    return json.dumps(
        {"ok": True, "source_path": found["poc"]["source_path"], "result": line},
        ensure_ascii=False,
    )


def asset_link(
    root: Path,
    engagement_id: str,
    source_key: str,
    target_key: str,
    relation: str,
) -> str:
    if not _has_reservation(Path(root) / engagement_id / "index.db", engagement_id):
        return json.dumps({"ok": False, "error": "reservation_required"}, ensure_ascii=False)
    if not source_key.strip() or not target_key.strip() or not relation.strip():
        return json.dumps({"ok": False, "error": "invalid_input"}, ensure_ascii=False)
    with _connect(Path(root) / engagement_id / "index.db") as db:
        db.execute(
            "INSERT INTO asset_link (engagement_id, source_key, target_key, relation) "
            "VALUES (?, ?, ?, ?)",
            (engagement_id, source_key, target_key, relation),
        )
    return json.dumps({"ok": True, "source_key": source_key, "target_key": target_key}, ensure_ascii=False)


def asset_graph(root: Path, engagement_id: str) -> str:
    db_path = Path(root) / engagement_id / "index.db"
    if not db_path.is_file():
        return json.dumps({"ok": False, "error": "not_found"}, ensure_ascii=False)
    with _connect(db_path) as db:
        rows = db.execute(
            "SELECT source_key, target_key, relation FROM asset_link WHERE engagement_id = ?",
            (engagement_id,),
        ).fetchall()
    links = [
        {"source_key": row[0], "target_key": row[1], "relation": row[2]}
        for row in rows
    ]
    return json.dumps({"ok": True, "count": len(links), "links": links}, ensure_ascii=False)


def attack_path(root: Path, engagement_id: str) -> str:
    return asset_graph(root, engagement_id)


def web_list(root: Path, engagement_id: str) -> str:
    db_path = Path(root) / engagement_id / "index.db"
    if not db_path.is_file():
        return json.dumps({"ok": False, "error": "not_found"}, ensure_ascii=False)
    with _connect(db_path) as db:
        rows = db.execute(
            "SELECT stable_key, address, status FROM asset "
            "WHERE engagement_id = ? AND address LIKE 'http%'",
            (engagement_id,),
        ).fetchall()
    webs = [
        {"stable_key": row[0], "address": row[1], "status": row[2]}
        for row in rows
    ]
    return json.dumps({"ok": True, "count": len(webs), "webs": webs}, ensure_ascii=False)


def domain_index(root: Path, engagement_id: str) -> str:
    db_path = Path(root) / engagement_id / "index.db"
    if not db_path.is_file():
        return json.dumps({"ok": False, "error": "not_found"}, ensure_ascii=False)
    with _connect(db_path) as db:
        rows = db.execute(
            "SELECT address FROM asset WHERE engagement_id = ?",
            (engagement_id,),
        ).fetchall()
    domains: dict[str, list[str]] = {}
    for (address,) in rows:
        host = address.split("://", 1)[-1].split("/", 1)[0].split(":", 1)[0]
        parts = host.split(".")
        if len(parts) < 2 or not all(part.isalpha() for part in parts):
            continue
        domains.setdefault(".".join(parts[-2:]), []).append(host)
    return json.dumps({"ok": True, "domains": domains}, ensure_ascii=False)


def asset_timeline(root: Path, engagement_id: str) -> str:
    db_path = Path(root) / engagement_id / "index.db"
    if not db_path.is_file():
        return json.dumps({"ok": False, "error": "not_found"}, ensure_ascii=False)
    with _connect(db_path) as db:
        rows = db.execute(
            "SELECT substr(first_seen, 1, 10), stable_key FROM asset "
            "WHERE engagement_id = ? ORDER BY first_seen",
            (engagement_id,),
        ).fetchall()
    grouped: dict[str, list[str]] = {}
    for day, stable_key in rows:
        grouped.setdefault(day, []).append(stable_key)
    days = [{"day": day, "assets": assets} for day, assets in grouped.items()]
    return json.dumps({"ok": True, "count": len(rows), "days": days}, ensure_ascii=False)


def chain_add(
    root: Path,
    engagement_id: str,
    asset_key: str,
    command_path: str,
    result: str,
    extra: dict | None = None,
    stage_code: str | None = None,
    tool: str | None = None,
    summary: str | None = None,
) -> str:
    if extra and _SECRET_FIELDS.intersection(extra):
        return json.dumps({"ok": False, "error": "secret_field"}, ensure_ascii=False)
    if not _has_reservation(Path(root) / engagement_id / "index.db", engagement_id):
        return json.dumps({"ok": False, "error": "reservation_required"}, ensure_ascii=False)
    if command_path.startswith("/") or ".." in Path(command_path).parts or not result.strip():
        return json.dumps({"ok": False, "error": "invalid_input"}, ensure_ascii=False)
    with _connect(Path(root) / engagement_id / "index.db") as db:
        db.execute(
            "INSERT INTO chain_step (engagement_id, asset_key, command_path, result, "
            "stage_code, tool, summary) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                engagement_id,
                asset_key,
                command_path,
                " ".join(result.split()),
                _clean(stage_code),
                _clean(tool),
                _clean(summary),
            ),
        )
    return json.dumps({"ok": True, "asset_key": asset_key}, ensure_ascii=False)


def chain_list(root: Path, engagement_id: str) -> str:
    db_path = Path(root) / engagement_id / "index.db"
    if not db_path.is_file():
        return json.dumps({"ok": False, "error": "not_found"}, ensure_ascii=False)
    with _connect(db_path) as db:
        rows = db.execute(
            "SELECT asset_key, command_path, result, stage_code, tool, summary, created_at "
            "FROM chain_step WHERE engagement_id = ?",
            (engagement_id,),
        ).fetchall()
    steps = [
        {
            "asset_key": row[0],
            "command_path": row[1],
            "result": row[2],
            "stage_code": row[3],
            "tool": row[4],
            "summary": row[5],
            "created_at": row[6],
        }
        for row in rows
    ]
    return json.dumps({"ok": True, "count": len(steps), "steps": steps}, ensure_ascii=False)


def chain_read(root: Path, engagement_id: str) -> str:
    return chain_list(root, engagement_id)


def attack_chain(root: Path, engagement_id: str) -> str:
    db_path = Path(root) / engagement_id / "index.db"
    if not db_path.is_file():
        return json.dumps({"ok": False, "error": "not_found"}, ensure_ascii=False)
    with _connect(db_path) as db:
        counts = {
            "recon": db.execute("SELECT COUNT(*) FROM asset").fetchone()[0],
            "vuln": db.execute("SELECT COUNT(*) FROM vuln").fetchone()[0],
            "access": db.execute("SELECT COUNT(*) FROM access_session").fetchone()[0],
            "tunnel": db.execute("SELECT COUNT(*) FROM tunnel").fetchone()[0],
            "report": 1 if (Path(root) / engagement_id / "wiki" / "authorization.md").is_file() else 0,
        }
    stages = [{"stage": name, "count": count} for name, count in counts.items()]
    return json.dumps({"ok": True, "stages": stages}, ensure_ascii=False)


def attack_file_add(
    root: Path,
    engagement_id: str,
    asset_key: str,
    relative_path: str,
) -> str:
    if not _has_reservation(Path(root) / engagement_id / "index.db", engagement_id):
        return json.dumps({"ok": False, "error": "reservation_required"}, ensure_ascii=False)
    if relative_path.startswith("/") or ".." in Path(relative_path).parts:
        return json.dumps({"ok": False, "error": "invalid_input"}, ensure_ascii=False)
    with _connect(Path(root) / engagement_id / "index.db") as db:
        db.execute(
            "INSERT INTO attack_file (engagement_id, asset_key, relative_path) VALUES (?, ?, ?)",
            (engagement_id, asset_key, relative_path),
        )
    return json.dumps({"ok": True, "asset_key": asset_key}, ensure_ascii=False)


def attack_file_list(root: Path, engagement_id: str) -> str:
    db_path = Path(root) / engagement_id / "index.db"
    if not db_path.is_file():
        return json.dumps({"ok": False, "error": "not_found"}, ensure_ascii=False)
    with _connect(db_path) as db:
        rows = db.execute(
            "SELECT asset_key, relative_path FROM attack_file WHERE engagement_id = ?",
            (engagement_id,),
        ).fetchall()
    files = [{"asset_key": row[0], "relative_path": row[1]} for row in rows]
    return json.dumps({"ok": True, "count": len(files), "files": files}, ensure_ascii=False)


def webshell_add(
    root: Path,
    engagement_id: str,
    asset_key: str,
    shell_type: str,
    evidence_path: str,
) -> str:
    if not _has_reservation(Path(root) / engagement_id / "index.db", engagement_id):
        return json.dumps({"ok": False, "error": "reservation_required"}, ensure_ascii=False)
    if shell_type not in {"behinder", "godzilla"}:
        return json.dumps({"ok": False, "error": "invalid_input"}, ensure_ascii=False)
    if evidence_path.startswith("/") or ".." in Path(evidence_path).parts:
        return json.dumps({"ok": False, "error": "invalid_input"}, ensure_ascii=False)
    with _connect(Path(root) / engagement_id / "index.db") as db:
        db.execute(
            "INSERT INTO webshell (engagement_id, asset_key, shell_type, evidence_path) "
            "VALUES (?, ?, ?, ?)",
            (engagement_id, asset_key, shell_type, evidence_path),
        )
    return json.dumps({"ok": True, "shell_type": shell_type}, ensure_ascii=False)


def webshell_update(root: Path, engagement_id: str, asset_key: str, status: str) -> str:
    if not _has_reservation(Path(root) / engagement_id / "index.db", engagement_id):
        return json.dumps({"ok": False, "error": "reservation_required"}, ensure_ascii=False)
    if not status.strip():
        return json.dumps({"ok": False, "error": "invalid_input"}, ensure_ascii=False)
    with _connect(Path(root) / engagement_id / "index.db") as db:
        changed = db.execute(
            "UPDATE webshell SET status = ? WHERE engagement_id = ? AND asset_key = ?",
            (status, engagement_id, asset_key),
        ).rowcount
    if changed != 1:
        return json.dumps({"ok": False, "error": "not_found"}, ensure_ascii=False)
    return json.dumps({"ok": True, "status": status}, ensure_ascii=False)


def webshell_list(root: Path, engagement_id: str) -> str:
    db_path = Path(root) / engagement_id / "index.db"
    if not db_path.is_file():
        return json.dumps({"ok": False, "error": "not_found"}, ensure_ascii=False)
    with _connect(db_path) as db:
        rows = db.execute(
            "SELECT asset_key, shell_type, evidence_path, status FROM webshell "
            "WHERE engagement_id = ?",
            (engagement_id,),
        ).fetchall()
    shells = [
        {
            "asset_key": row[0],
            "shell_type": row[1],
            "evidence_path": row[2],
            "status": row[3],
        }
        for row in rows
    ]
    return json.dumps({"ok": True, "count": len(shells), "shells": shells}, ensure_ascii=False)


def add_finding(
    root: Path,
    engagement_id: str,
    asset_key: str,
    conclusion: str,
    evidence_path: str,
    extra: dict | None = None,
) -> str:
    if extra and _SECRET_FIELDS.intersection(extra):
        return json.dumps({"ok": False, "error": "secret_field"}, ensure_ascii=False)
    if not _has_reservation(Path(root) / engagement_id / "index.db", engagement_id):
        return json.dumps({"ok": False, "error": "reservation_required"}, ensure_ascii=False)
    line = " ".join(conclusion.split())
    if len(line) > 120 or evidence_path.startswith("/") or ".." in Path(evidence_path).parts:
        return json.dumps({"ok": False, "error": "invalid_input"}, ensure_ascii=False)
    db_path = Path(root) / engagement_id / "index.db"
    with _connect(db_path) as db:
        db.execute(
            "INSERT INTO finding (engagement_id, asset_key, conclusion, evidence_path) "
            "VALUES (?, ?, ?, ?)",
            (engagement_id, asset_key, line, evidence_path),
        )
    return json.dumps({"ok": True, "asset_key": asset_key}, ensure_ascii=False)


def add_chain(
    root: Path,
    engagement_id: str,
    conclusion: str,
    evidence_ids: list[int],
    extra: dict | None = None,
) -> str:
    if extra and _SECRET_FIELDS.intersection(extra):
        return json.dumps({"ok": False, "error": "secret_field"}, ensure_ascii=False)
    if not _has_reservation(Path(root) / engagement_id / "index.db", engagement_id):
        return json.dumps({"ok": False, "error": "reservation_required"}, ensure_ascii=False)
    line = " ".join(conclusion.split())
    if len(line) > 120 or not evidence_ids:
        return json.dumps({"ok": False, "error": "invalid_input"}, ensure_ascii=False)
    with _connect(Path(root) / engagement_id / "index.db") as db:
        db.execute(
            "INSERT INTO attack_chain (engagement_id, conclusion, evidence_ids) VALUES (?, ?, ?)",
            (engagement_id, line, json.dumps(evidence_ids)),
        )
    return json.dumps({"ok": True}, ensure_ascii=False)


def write_report_skeleton(root: Path, engagement_id: str) -> str:
    path = Path(root) / engagement_id / "wiki" / "pages" / "report.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text(
            "# 报告骨架\n\n## 授权\n\n## 资产\n\n## 证据路径\n\n## 结论\n\n## 证据与范围\n\n## 根因与前提\n\n## 验证结果\n\n## 影响与检测\n\n## 修复与验证建议\n\n## 不确定性与后续工作\n",
            encoding="utf-8",
        )
    return str(path)


def score_hit(root: Path, engagement_id: str, rule_id: str, evidence_path: str) -> str:
    if not _has_reservation(Path(root) / engagement_id / "index.db", engagement_id):
        return json.dumps({"ok": False, "error": "reservation_required"}, ensure_ascii=False)
    if not rule_id.strip() or evidence_path.startswith("/") or ".." in Path(evidence_path).parts:
        return json.dumps({"ok": False, "error": "invalid_input"}, ensure_ascii=False)
    with _connect(Path(root) / engagement_id / "index.db") as db:
        db.execute(
            "INSERT INTO score_event (engagement_id, rule_id, evidence_path) VALUES (?, ?, ?)",
            (engagement_id, rule_id, evidence_path),
        )
    return json.dumps(
        {"ok": True, "rule_id": rule_id, "evidence_path": evidence_path},
        ensure_ascii=False,
    )


def shot_add(root: Path, engagement_id: str, asset_key: str, relative_path: str) -> str:
    if not _has_reservation(Path(root) / engagement_id / "index.db", engagement_id):
        return json.dumps({"ok": False, "error": "reservation_required"}, ensure_ascii=False)
    if relative_path.startswith("/") or ".." in Path(relative_path).parts:
        return json.dumps({"ok": False, "error": "invalid_input"}, ensure_ascii=False)
    with _connect(Path(root) / engagement_id / "index.db") as db:
        db.execute(
            "INSERT INTO shot (engagement_id, asset_key, relative_path) VALUES (?, ?, ?)",
            (engagement_id, asset_key, relative_path),
        )
    return json.dumps({"ok": True, "path": relative_path}, ensure_ascii=False)


def shot_list(root: Path, engagement_id: str) -> str:
    db_path = Path(root) / engagement_id / "index.db"
    if not db_path.is_file():
        return json.dumps({"ok": False, "error": "not_found"}, ensure_ascii=False)
    with _connect(db_path) as db:
        rows = db.execute(
            "SELECT asset_key, relative_path FROM shot WHERE engagement_id = ?",
            (engagement_id,),
        ).fetchall()
    shots = [{"asset_key": row[0], "path": row[1]} for row in rows]
    return json.dumps({"ok": True, "count": len(shots), "shots": shots}, ensure_ascii=False)


def shot_delete(root: Path, engagement_id: str, relative_path: str) -> str:
    if not _has_reservation(Path(root) / engagement_id / "index.db", engagement_id):
        return json.dumps({"ok": False, "error": "reservation_required"}, ensure_ascii=False)
    with _connect(Path(root) / engagement_id / "index.db") as db:
        changed = db.execute(
            "DELETE FROM shot WHERE engagement_id = ? AND relative_path = ?",
            (engagement_id, relative_path),
        ).rowcount
    if changed != 1:
        return json.dumps({"ok": False, "error": "not_found"}, ensure_ascii=False)
    return json.dumps({"ok": True, "path": relative_path}, ensure_ascii=False)


def score_point_save(root: Path, engagement_id: str, point_id: str, category: str) -> str:
    if not _has_reservation(Path(root) / engagement_id / "index.db", engagement_id):
        return json.dumps({"ok": False, "error": "reservation_required"}, ensure_ascii=False)
    if not point_id.strip() or not category.strip():
        return json.dumps({"ok": False, "error": "invalid_input"}, ensure_ascii=False)
    with _connect(Path(root) / engagement_id / "index.db") as db:
        db.execute(
            "INSERT INTO score_point (engagement_id, point_id, category) VALUES (?, ?, ?)",
            (engagement_id, point_id, category),
        )
    return json.dumps(
        {"ok": True, "point_id": point_id, "category": category},
        ensure_ascii=False,
    )


def score_point_get(root: Path, engagement_id: str, point_id: str) -> str:
    db_path = Path(root) / engagement_id / "index.db"
    if not db_path.is_file():
        return json.dumps({"ok": False, "error": "not_found"}, ensure_ascii=False)
    with _connect(db_path) as db:
        row = db.execute(
            "SELECT category FROM score_point WHERE engagement_id = ? AND point_id = ?",
            (engagement_id, point_id),
        ).fetchone()
    if row is None:
        return json.dumps({"ok": False, "error": "not_found"}, ensure_ascii=False)
    return json.dumps({"ok": True, "category": row[0]}, ensure_ascii=False)


def scan_add(root: Path, engagement_id: str, asset_key: str, relative_path: str) -> str:
    if not _has_reservation(Path(root) / engagement_id / "index.db", engagement_id):
        return json.dumps({"ok": False, "error": "reservation_required"}, ensure_ascii=False)
    if relative_path.startswith("/") or ".." in Path(relative_path).parts:
        return json.dumps({"ok": False, "error": "invalid_input"}, ensure_ascii=False)
    with _connect(Path(root) / engagement_id / "index.db") as db:
        db.execute(
            "INSERT INTO scan_ref (engagement_id, asset_key, relative_path) VALUES (?, ?, ?)",
            (engagement_id, asset_key, relative_path),
        )
    return json.dumps({"ok": True, "path": relative_path}, ensure_ascii=False)


def scan_list(root: Path, engagement_id: str) -> str:
    db_path = Path(root) / engagement_id / "index.db"
    if not db_path.is_file():
        return json.dumps({"ok": False, "error": "not_found"}, ensure_ascii=False)
    with _connect(db_path) as db:
        rows = db.execute(
            "SELECT asset_key, relative_path FROM scan_ref WHERE engagement_id = ?",
            (engagement_id,),
        ).fetchall()
    scans = [{"asset_key": row[0], "path": row[1]} for row in rows]
    return json.dumps({"ok": True, "count": len(scans), "scans": scans}, ensure_ascii=False)


def note_add(root: Path, engagement_id: str, asset_key: str, relative_path: str) -> str:
    if not _has_reservation(Path(root) / engagement_id / "index.db", engagement_id):
        return json.dumps({"ok": False, "error": "reservation_required"}, ensure_ascii=False)
    if relative_path.startswith("/") or ".." in Path(relative_path).parts:
        return json.dumps({"ok": False, "error": "invalid_input"}, ensure_ascii=False)
    with _connect(Path(root) / engagement_id / "index.db") as db:
        db.execute(
            "INSERT INTO note_ref (engagement_id, asset_key, relative_path) VALUES (?, ?, ?)",
            (engagement_id, asset_key, relative_path),
        )
    return json.dumps({"ok": True, "path": relative_path}, ensure_ascii=False)


def note_list(root: Path, engagement_id: str) -> str:
    db_path = Path(root) / engagement_id / "index.db"
    if not db_path.is_file():
        return json.dumps({"ok": False, "error": "not_found"}, ensure_ascii=False)
    with _connect(db_path) as db:
        rows = db.execute(
            "SELECT asset_key, relative_path FROM note_ref WHERE engagement_id = ?",
            (engagement_id,),
        ).fetchall()
    notes = [{"asset_key": row[0], "path": row[1]} for row in rows]
    return json.dumps({"ok": True, "count": len(notes), "notes": notes}, ensure_ascii=False)


def knowledge_add(root: Path, engagement_id: str, asset_key: str, relative_path: str) -> str:
    if not _has_reservation(Path(root) / engagement_id / "index.db", engagement_id):
        return json.dumps({"ok": False, "error": "reservation_required"}, ensure_ascii=False)
    if relative_path.startswith("/") or ".." in Path(relative_path).parts:
        return json.dumps({"ok": False, "error": "invalid_input"}, ensure_ascii=False)
    with _connect(Path(root) / engagement_id / "index.db") as db:
        db.execute(
            "INSERT INTO knowledge_ref (engagement_id, asset_key, relative_path) VALUES (?, ?, ?)",
            (engagement_id, asset_key, relative_path),
        )
    return json.dumps({"ok": True, "path": relative_path}, ensure_ascii=False)


def knowledge_list(root: Path, engagement_id: str) -> str:
    db_path = Path(root) / engagement_id / "index.db"
    if not db_path.is_file():
        return json.dumps({"ok": False, "error": "not_found"}, ensure_ascii=False)
    with _connect(db_path) as db:
        rows = db.execute(
            "SELECT asset_key, relative_path FROM knowledge_ref WHERE engagement_id = ?",
            (engagement_id,),
        ).fetchall()
    notes = [{"asset_key": row[0], "path": row[1]} for row in rows]
    return json.dumps({"ok": True, "count": len(notes), "notes": notes}, ensure_ascii=False)


def role_list() -> str:
    return json.dumps(
        {
            "ok": True,
            "roles": [
                "rt-recon",
                "rt-asset",
                "rt-vuln",
                "rt-exploit",
                "rt-internal",
            ],
        },
        ensure_ascii=False,
    )


def role_prompt(root: Path, role: str) -> str:
    if role not in {"rt-recon", "rt-asset", "rt-vuln", "rt-exploit", "rt-internal"}:
        return json.dumps({"ok": False, "error": "invalid_input"}, ensure_ascii=False)
    path = Path(root) / "roles" / f"{role}.md"
    if not path.is_file():
        return json.dumps({"ok": False, "error": "not_found"}, ensure_ascii=False)
    return json.dumps(
        {"ok": True, "role": role, "text": path.read_text(encoding="utf-8")},
        ensure_ascii=False,
    )


def role_prompt_reset(root: Path, role: str, source: Path) -> str:
    if role not in {"rt-recon", "rt-asset", "rt-vuln", "rt-exploit", "rt-internal"}:
        return json.dumps({"ok": False, "error": "invalid_input"}, ensure_ascii=False)
    source_path = Path(source) / "roles" / f"{role}.md"
    target = Path(root) / "roles" / f"{role}.md"
    if not source_path.is_file() or not target.parent.is_dir():
        return json.dumps({"ok": False, "error": "not_found"}, ensure_ascii=False)
    target.write_text(source_path.read_text(encoding="utf-8"), encoding="utf-8")
    return json.dumps({"ok": True, "role": role}, ensure_ascii=False)


def write_report_index(root: Path, engagement_id: str) -> str:
    path = Path(root) / engagement_id / "wiki" / "pages" / "report-index.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "# 报告索引\n\n- wiki/authorization.md\n- index.db\n",
        encoding="utf-8",
    )
    return str(path)


def write_score_report(root: Path, engagement_id: str) -> str:
    db_path = Path(root) / engagement_id / "index.db"
    with _connect(db_path) as db:
        rows = db.execute(
            "SELECT rule_id, evidence_path FROM score_event WHERE engagement_id = ?",
            (engagement_id,),
        ).fetchall()
    lines = ["# 得分报告", ""]
    lines.extend(f"- {rule_id}: {path}" for rule_id, path in rows)
    path = Path(root) / engagement_id / "wiki" / "pages" / "score-report.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return str(path)


def _write_once(path: Path, content: str) -> None:
    if not path.exists():
        path.write_text(content, encoding="utf-8")
