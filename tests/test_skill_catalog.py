from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_skill_catalog_matches_dsh_names():
    names = sorted(path.parent.name for path in (ROOT / "skills").glob("*/SKILL.md"))
    assert names == [
        "active-scan",
        "asset-correlation",
        "browser-automation",
        "chisel-tunnel",
        "cn-proxy-pool",
        "credential-attack",
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
        "redteam-preflight",
        "redteam-setup",
        "shell-handler",
        "suo5-tunnel",
        "unauth-exploit",
        "vps-reverse-shell",
        "web-fingerprint",
        "webshell-toolkit",
    ]
