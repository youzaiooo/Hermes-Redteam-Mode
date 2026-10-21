from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_recon_skills_name_tools_and_store_paths():
    expected = {
        "fofa-recon": ("FOFA_KEY", "redteam_scan_add"),
        "passive-recon": ("crt.sh", "redteam_domain_index"),
        "recon-pipeline": ("subfinder", "redteam_asset_add"),
        "active-scan": ("nmap", "redteam_scan_add"),
        "web-fingerprint": ("httpx", "redteam_asset_test"),
        "asset-correlation": ("redteam_asset_link", "redteam_asset_graph"),
        "browser-automation": ("redteam_shot_add", "Cookie"),
        "kimi-webbridge": ("redteam_access_add", "Token"),
        "cn-proxy-pool": ("单条命令", "系统代理"),
    }
    for name, needles in expected.items():
        text = (ROOT / "skills" / name / "SKILL.md").read_text(encoding="utf-8")
        for needle in needles:
            assert needle in text
