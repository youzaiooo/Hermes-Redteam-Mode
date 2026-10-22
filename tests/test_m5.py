import json
from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient

from hermes_redteam.dashboard.plugin_api import router
from hermes_redteam.store import open_engagement, reserve_write


def _root(tmp_path: Path) -> Path:
    return tmp_path / "redteam" / "engagements"


def test_poc_add_dedupes_and_search_spans_engagements(tmp_path: Path):
    from hermes_redteam.store import poc_add, poc_search

    root = _root(tmp_path)
    open_engagement(root, "eng-a", "Eng A")
    open_engagement(root, "eng-b", "Eng B")
    reserve_write(root, "eng-a", "rt-vuln")
    reserve_write(root, "eng-b", "rt-vuln")

    first = json.loads(
        poc_add(
            root,
            "eng-a",
            "web",
            "web-a",
            "raw/poc/log4j-a.txt",
            title="Apache Log4j RCE",
            cve="CVE-2021-44228",
            source="nuclei:http/cves/2021/CVE-2021-44228",
            source_url="https://example.com/log4j",
            verified=True,
            verified_note="reproduced",
        )
    )
    second = json.loads(
        poc_add(
            root,
            "eng-b",
            "web",
            "web-b",
            "raw/poc/log4j-b.txt",
            title="Apache Log4j RCE",
            cve="CVE-2021-44228",
            source="nuclei:http/cves/2021/CVE-2021-44228",
        )
    )

    assert first["ok"] is True
    assert first["deduped"] is False
    assert second["ok"] is True
    assert second["deduped"] is True
    assert second["id"] == first["id"]

    found = json.loads(poc_search(root, "eng-b", "log4j"))
    global_rows = [row for row in found["pocs"] if row["id"] is not None]
    assert len(global_rows) == 1
    row = global_rows[0]
    assert row["title"] == "Apache Log4j RCE"
    assert row["cve"] == "CVE-2021-44228"
    assert row["source"] == "nuclei:http/cves/2021/CVE-2021-44228"
    assert row["verified"] is True
    assert row["engagement"] == "eng-a"
    assert "payload" not in json.dumps(found).lower()

    # A distinct POC recorded in eng-b is searchable from eng-a.
    poc_add(
        root,
        "eng-b",
        "web",
        "web-c",
        "raw/poc/spring.txt",
        title="Spring4Shell",
        cve="CVE-2022-22965",
        source="nuclei:http/cves/2022/CVE-2022-22965",
    )
    cross = json.loads(poc_search(root, "eng-a", "spring4shell"))
    assert any(row["title"] == "Spring4Shell" for row in cross["pocs"])


def test_report_export_builds_four_sections(tmp_path: Path):
    from hermes_redteam.store import (
        access_add,
        add_asset,
        chain_add,
        credential_add,
        export_report,
        score_hit,
        vuln_add,
    )

    root = _root(tmp_path)
    open_engagement(root, "lab-01", "Lab 01")
    reserve_write(root, "lab-01", "rt-recon")

    add_asset(
        root,
        "lab-01",
        "web-01",
        "http://127.0.0.1:8765",
        port=80,
        title="Lab Home",
        provenance="nmap",
        scope="10.0.0.0/24",
    )
    score_hit(root, "lab-01", "web-found", "raw/score/web.txt")
    score_hit(root, "lab-01", "web-found", "raw/score/web2.txt")
    credential_add(root, "lab-01", "web-01", "raw/cred/web.txt")
    access_add(root, "lab-01", "web-01", "password", "raw/access/web.txt")
    vuln_add(
        root,
        "lab-01",
        "web-01",
        "confirmed",
        "raw/v/web.txt",
        title="SQL injection",
        severity="high",
        cve="CVE-2021-0001",
        evidence="布尔盲注",
    )
    chain_add(
        root,
        "lab-01",
        "web-01",
        "raw/chain/web.md",
        "got shell",
        stage_code="exploit",
        tool="webshell",
        summary="landed",
    )

    result = json.loads(export_report(root, "lab-01"))
    assert result["ok"] is True
    relative_path = result["relative_path"]
    assert relative_path.startswith("reports/report-")
    assert relative_path.endswith(".md")
    assert result["excerpt"]

    text = (root / "lab-01" / relative_path).read_text(encoding="utf-8")
    for section in ("## 资产证明", "## 得分汇总", "## 凭据与访问", "## 漏洞复现"):
        assert section in text
    assert "http://127.0.0.1:8765" in text
    assert "nmap" in text
    assert "web-found：2 次" in text
    assert "raw/cred/web.txt" in text
    assert "SQL injection" in text
    assert "CVE-2021-0001" in text
    assert "webshell" in text
    assert "payload" not in text.lower()


def test_report_route_returns_latest_markdown(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("HERMES_HOME", str(tmp_path))
    root = _root(tmp_path)
    open_engagement(root, "lab-01", "Lab 01")

    app = FastAPI()
    app.include_router(router)
    client = TestClient(app)

    first = client.get("/report/lab-01")
    assert first.status_code == 200
    payload = first.json()
    assert payload["ok"] is True
    assert payload["generated"] is True
    assert "## 资产证明" in payload["markdown"]
    assert payload["path"]
    assert payload["filename"].startswith("report-")

    second = client.get("/report/lab-01")
    assert second.status_code == 200
    assert second.json()["generated"] is False
    assert second.json()["markdown"] == payload["markdown"]
    assert second.json()["path"] == payload["path"]


def test_report_route_missing_engagement_is_404(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("HERMES_HOME", str(tmp_path))
    app = FastAPI()
    app.include_router(router)
    client = TestClient(app)

    response = client.get("/report/lab-404")

    assert response.status_code == 404


def test_report_export_registered_for_commander_only():
    from hermes_redteam import register

    class _Ctx:
        def __init__(self, profile: str):
            self.profile_name = profile
            self.tools: list[str] = []

        def register_tool(self, name, **kwargs):
            del kwargs
            self.tools.append(name)

        def register_skill(self, name, path, **kwargs):
            del name, path, kwargs

    def _tools(profile: str) -> list[str]:
        ctx = _Ctx(profile)
        register(ctx)
        return ctx.tools

    commander = _tools("default")
    vuln = _tools("rt-vuln")

    assert "redteam_report_export" in commander
    assert "redteam_report_export" not in vuln
    assert "redteam_poc_search" in vuln
