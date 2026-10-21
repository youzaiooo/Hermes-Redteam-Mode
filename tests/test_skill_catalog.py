from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_skill_catalog_matches_ported_names():
    names = sorted(path.parent.name for path in (ROOT / "skills").glob("*/SKILL.md"))
    assert names == [
        "active-scan",
        "asset-correlation",
        "browser-automation",
        "chisel-tunnel",
        "cn-proxy-pool",
        "credential-attack",
        "deepseek-web-intel",
        "dir-bruteforce",
        "fofa-recon",
        "frp-tunnel",
        "fscan-intranet",
        "gogo-intranet",
        "kimi-webbridge",
        "lateral-movement",
        "nuclei-scan",
        "passive-recon",
        "recon-pipeline",
        "redteam-commander",
        "redteam-preflight",
        "redteam-setup",
        "score-coverage",
        "shell-handler",
        "suo5-tunnel",
        "unauth-exploit",
        "vps-reverse-shell",
        "web-fingerprint",
        "webshell-toolkit",
    ]
