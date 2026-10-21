from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_remaining_skills_name_store_and_limits():
    expected = {
        "nuclei-scan": ("nuclei", "redteam_vuln_add"),
        "dir-bruteforce": ("ffuf", "redteam_scan_add"),
        "unauth-exploit": ("一行结论", "不写利用步骤"),
        "webshell-toolkit": ("behinder", "godzilla"),
        "credential-attack": ("口令真值不入库", "redteam_credential_add"),
        "shell-handler": ("不记监听命令", "redteam_access_add"),
        "vps-reverse-shell": ("REDTEAM_VPS_HOST", "不入库"),
        "gogo-intranet": ("先铺面", "redteam_scan_add"),
        "fscan-intranet": ("再打点", "redteam_vuln_add"),
        "suo5-tunnel": ("entry_kind", "redteam_tunnel_add"),
        "chisel-tunnel": ("redteam_tunnel_update", "不记命令"),
        "frp-tunnel": ("redteam_tunnel_list", "入口类型"),
        "lateral-movement": ("证据路径", "不写命令正文"),
        "redteam-setup": ("FOFA_KEY", "不自动安装"),
    }
    for name, needles in expected.items():
        text = (ROOT / "skills" / name / "SKILL.md").read_text(encoding="utf-8")
        for needle in needles:
            assert needle in text
