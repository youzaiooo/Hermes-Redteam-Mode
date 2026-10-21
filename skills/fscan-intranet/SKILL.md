---
name: fscan-intranet
description: Use when the fscan-intranet step is authorized. Store paths and one-line results only.
---

# fscan-intranet

再打点。普查结果写入 `redteam_scan_add`。

确认的漏洞写入 `redteam_vuln_add`。口令真值不入库。

结果只写相对路径和一行结论。命令正文、payload、凭据真值不入库。
