---
name: active-scan
description: Use when the active-scan step is authorized. Store paths and one-line results only.
---

# active-scan

先占位。用 `nmap`、`masscan` 或 `naabu` 做授权范围内的端口扫描。

结果路径写入 `redteam_scan_add`。不保存命令正文。

结果只写相对路径和一行结论。命令正文、payload、凭据真值不入库。
